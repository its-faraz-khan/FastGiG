import os
import secrets
import string
from datetime import datetime, timedelta

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
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from database import get_db
from email_utils import send_otp_email, send_password_reset_email
from schemas import PLATFORM_TO_CATEGORY

load_dotenv()

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FairGig Auth Service",
    description="Authentication microservice for the FairGig platform",
    version="1.0.0",
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


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=schemas.RegisterResponse, status_code=201)
async def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(db_models.User).filter(db_models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(payload.password)
    user = db_models.User(
        email=payload.email,
        password_hash=hashed_pw,
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

        worker = db_models.Worker(
            user_id=user.id,
            full_name=payload.full_name,
            city_zone=payload.city_zone,
            primary_platform=payload.platform,
            category=PLATFORM_TO_CATEGORY.get(payload.platform, "other"),
        )
        db.add(worker)

    otp = _generate_otp()
    db.add(db_models.OtpToken(
        email=payload.email,
        token=otp,
        purpose="email_verification",
        expiry=datetime.utcnow() + timedelta(minutes=5),
    ))
    db.commit()

    try:
        await send_otp_email(payload.email, otp)
    except Exception:
        pass  # MailHog may not be running; don't fail registration

    return schemas.RegisterResponse(
        requires_otp=True,
        otp_sent_to=payload.email,
        message="Account created. Please verify your email with the OTP sent.",
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@app.post("/auth/login", response_model=schemas.LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox for an OTP.",
        )

    user.last_login = datetime.utcnow()
    db.commit()

    return schemas.LoginResponse(
        token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        role=user.role,
        user_id=str(user.id),
    )


# ---------------------------------------------------------------------------
# POST /auth/otp/send
# ---------------------------------------------------------------------------

@app.post("/auth/otp/send", response_model=schemas.MessageResponse)
@limiter.limit("3/minute")
async def send_otp(
    request: Request,
    payload: schemas.OtpSendRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if user:
        # Invalidate existing unused OTPs for this email
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
            expiry=datetime.utcnow() + timedelta(minutes=5),
        ))
        db.commit()

        try:
            await send_otp_email(payload.email, otp)
        except Exception:
            pass

    # Always return the same message to avoid email enumeration
    return schemas.MessageResponse(
        message="If an account exists with that email, an OTP has been sent."
    )


# ---------------------------------------------------------------------------
# POST /auth/otp/verify
# ---------------------------------------------------------------------------

@app.post("/auth/otp/verify", response_model=schemas.LoginResponse)
async def verify_otp(payload: schemas.OtpVerifyRequest, db: Session = Depends(get_db)):
    otp_record = (
        db.query(db_models.OtpToken)
        .filter(
            db_models.OtpToken.email == payload.email,
            db_models.OtpToken.token == payload.otp,
            db_models.OtpToken.purpose == "email_verification",
            db_models.OtpToken.is_used == False,
            db_models.OtpToken.expiry > datetime.utcnow(),
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
    user.last_login = datetime.utcnow()
    db.commit()

    return schemas.LoginResponse(
        token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        role=user.role,
        user_id=str(user.id),
    )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@app.post("/auth/refresh", response_model=schemas.RefreshResponse)
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

    return schemas.RefreshResponse(token=create_access_token(user))


# ---------------------------------------------------------------------------
# GET /auth/verify  (used by other microservices to validate a token)
# ---------------------------------------------------------------------------

@app.get("/auth/verify", response_model=schemas.VerifyResponse)
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
# POST /auth/forgot-password
# ---------------------------------------------------------------------------

@app.post("/auth/forgot-password", response_model=schemas.MessageResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    payload: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(db_models.User).filter(db_models.User.email == payload.email).first()

    if user:
        # Invalidate previous unused reset tokens
        db.query(db_models.PasswordResetToken).filter(
            db_models.PasswordResetToken.user_id == user.id,
            db_models.PasswordResetToken.is_used == False,
        ).update({"is_used": True})

        reset_token = secrets.token_urlsafe(48)
        db.add(db_models.PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expiry=datetime.utcnow() + timedelta(hours=24),
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
# POST /auth/reset-password
# ---------------------------------------------------------------------------

@app.post("/auth/reset-password", response_model=schemas.MessageResponse)
async def reset_password(
    payload: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    token_record = (
        db.query(db_models.PasswordResetToken)
        .filter(
            db_models.PasswordResetToken.token == payload.token,
            db_models.PasswordResetToken.is_used == False,
            db_models.PasswordResetToken.expiry > datetime.utcnow(),
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
