import os
import secrets
import string
from contextlib import asynccontextmanager
from datetime import timedelta

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import db_models
import schemas
from auth_utils import (
    JWT_EXPIRY_MINUTES,
    REFRESH_TOKEN_EXPIRY_DAYS,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    utcnow,
    verify_password,
)
from database import get_db
from email_utils import send_otp_email, send_password_reset_email
from schemas import PLATFORM_TO_CATEGORY

load_dotenv()

# ---------------------------------------------------------------------------
# Startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Clean up expired tokens once on startup so they don't pile up
    db = next(get_db())
    try:
        now = utcnow()
        deleted_otp = db.query(db_models.OtpToken).filter(
            db_models.OtpToken.expiry < now
        ).delete()
        deleted_pw = db.query(db_models.PasswordResetToken).filter(
            db_models.PasswordResetToken.expiry < now
        ).delete()
        db.commit()
        if deleted_otp or deleted_pw:
            print(f"[startup] Cleaned {deleted_otp} expired OTPs, {deleted_pw} expired reset tokens.")
    except Exception as exc:
        print(f"[startup] Cleanup skipped: {exc}")
    finally:
        db.close()
    yield


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FairGig Auth Service",
    description="Authentication microservice for the FairGig platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_otp(length: int = 6) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _login_response(user) -> schemas.LoginResponse:
    return schemas.LoginResponse(
        token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        role=user.role,
        user_id=str(user.id),
        expires_in=JWT_EXPIRY_MINUTES * 60,
    )


def _get_current_user(request: Request, db: Session) -> db_models.User:
    """Decode Bearer token and return the User ORM object."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = auth_header.split(" ", 1)[1]
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Not an access token")

    user = db.query(db_models.User).filter(db_models.User.id == data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=schemas.HealthResponse, tags=["System"])
async def health():
    return schemas.HealthResponse(
        status="ok",
        service="fairgig-auth",
        version="1.0.0",
    )


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=schemas.RegisterResponse, status_code=201, tags=["Auth"])
async def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(db_models.User).filter(db_models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = db_models.User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        email_verified=False,
    )
    db.add(user)
    db.flush()

    if payload.role == "worker":
        if not payload.full_name or not payload.city_zone or not payload.platform:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="full_name, city_zone, and platform are required for workers",
            )
        db.add(db_models.Worker(
            user_id=user.id,
            full_name=payload.full_name,
            city_zone=payload.city_zone,
            primary_platform=payload.platform,
            category=PLATFORM_TO_CATEGORY.get(payload.platform, "other"),
        ))

    otp = _generate_otp()
    db.add(db_models.OtpToken(
        email=payload.email,
        token=otp,
        purpose="email_verification",
        expiry=utcnow() + timedelta(minutes=5),
    ))
    db.commit()

    try:
        await send_otp_email(payload.email, otp)
    except Exception:
        pass  # Mail server may not be running — OTP is always in the DB

    return schemas.RegisterResponse(
        requires_otp=True,
        otp_sent_to=payload.email,
        message="Account created. Please verify your email with the OTP sent.",
    )


# ---------------------------------------------------------------------------
# POST /auth/login   (rate-limited: 5 attempts / minute / IP)
# ---------------------------------------------------------------------------

@app.post("/auth/login", response_model=schemas.LoginResponse, tags=["Auth"])
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password")

    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Email not verified. Check your inbox for an OTP.")

    user.last_login = utcnow()
    db.commit()

    return _login_response(user)


# ---------------------------------------------------------------------------
# POST /auth/otp/send   (rate-limited: 3 / minute / IP)
# ---------------------------------------------------------------------------

@app.post("/auth/otp/send", response_model=schemas.MessageResponse, tags=["Auth"])
@limiter.limit("3/minute")
async def send_otp(
    request: Request,
    payload: schemas.OtpSendRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if user:
        db.query(db_models.OtpToken).filter(
            db_models.OtpToken.email == payload.email,
            db_models.OtpToken.purpose == "email_verification",
            db_models.OtpToken.is_used == False,
        ).update({"is_used": True})

        otp = _generate_otp()
        db.add(db_models.OtpToken(
            email=payload.email,
            token=otp,
            purpose="email_verification",
            expiry=utcnow() + timedelta(minutes=5),
        ))
        db.commit()

        try:
            await send_otp_email(payload.email, otp)
        except Exception:
            pass

    return schemas.MessageResponse(
        message="If an account exists with that email, an OTP has been sent."
    )


# ---------------------------------------------------------------------------
# POST /auth/otp/verify   (rate-limited: 10 / minute / IP)
# ---------------------------------------------------------------------------

@app.post("/auth/otp/verify", response_model=schemas.LoginResponse, tags=["Auth"])
@limiter.limit("10/minute")
async def verify_otp(
    request: Request,
    payload: schemas.OtpVerifyRequest,
    db: Session = Depends(get_db),
):
    otp_record = (
        db.query(db_models.OtpToken)
        .filter(
            db_models.OtpToken.email == payload.email,
            db_models.OtpToken.token == payload.otp,
            db_models.OtpToken.purpose == "email_verification",
            db_models.OtpToken.is_used == False,
            db_models.OtpToken.expiry > utcnow(),
        )
        .first()
    )

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    otp_record.is_used = True

    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email_verified = True
    user.last_login = utcnow()
    db.commit()

    return _login_response(user)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@app.post("/auth/refresh", response_model=schemas.RefreshResponse, tags=["Auth"])
async def refresh_token(payload: schemas.RefreshRequest, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user = db.query(db_models.User).filter(db_models.User.id == data["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.RefreshResponse(
        token=create_access_token(user),
        expires_in=JWT_EXPIRY_MINUTES * 60,
    )


# ---------------------------------------------------------------------------
# GET /auth/verify   (inter-service token validation)
# ---------------------------------------------------------------------------

@app.get("/auth/verify", response_model=schemas.VerifyResponse, tags=["Auth"])
async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")

    token = auth_header.split(" ", 1)[1]
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if data.get("type") != "access":
        raise HTTPException(status_code=401, detail="Not an access token")

    return schemas.VerifyResponse(
        valid=True,
        user_id=data["sub"],
        email=data["email"],
        role=data["role"],
    )


# ---------------------------------------------------------------------------
# GET /auth/me   (get current user profile from token)
# ---------------------------------------------------------------------------

@app.get("/auth/me", response_model=schemas.MeResponse, tags=["Auth"])
async def get_me(request: Request, db: Session = Depends(get_db)):
    user = _get_current_user(request, db)

    worker_profile = None
    if user.role == "worker" and user.worker:
        worker_profile = schemas.WorkerProfile.model_validate(user.worker)

    return schemas.MeResponse(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
        email_verified=user.email_verified,
        created_at=user.created_at.isoformat(),
        worker_profile=worker_profile,
    )


# ---------------------------------------------------------------------------
# POST /auth/forgot-password   (rate-limited: 3 / minute / IP)
# ---------------------------------------------------------------------------

@app.post("/auth/forgot-password", response_model=schemas.MessageResponse, tags=["Auth"])
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    payload: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if user:
        db.query(db_models.PasswordResetToken).filter(
            db_models.PasswordResetToken.user_id == user.id,
            db_models.PasswordResetToken.is_used == False,
        ).update({"is_used": True})

        reset_token = secrets.token_urlsafe(48)
        db.add(db_models.PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expiry=utcnow() + timedelta(hours=24),
        ))
        db.commit()

        try:
            await send_password_reset_email(payload.email, reset_token)
        except Exception:
            pass

    return schemas.MessageResponse(
        message="If an account exists with that email, a password reset link has been sent."
    )


# ---------------------------------------------------------------------------
# POST /auth/reset-password   (rate-limited: 5 / minute / IP)
# ---------------------------------------------------------------------------

@app.post("/auth/reset-password", response_model=schemas.MessageResponse, tags=["Auth"])
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    payload: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    token_record = (
        db.query(db_models.PasswordResetToken)
        .filter(
            db_models.PasswordResetToken.token == payload.token,
            db_models.PasswordResetToken.is_used == False,
            db_models.PasswordResetToken.expiry > utcnow(),
        )
        .first()
    )

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(db_models.User).filter(db_models.User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = get_password_hash(payload.new_password)
    token_record.is_used = True
    db.commit()

    return schemas.MessageResponse(message="Password reset successfully")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
