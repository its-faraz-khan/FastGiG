import re
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

VALID_ROLES = {"worker", "verifier", "advocate"}
VALID_PLATFORMS = {"Careem", "Uber", "Shopee", "InDrive", "Freelance", "Domestic Work", "Other"}
VALID_CITY_ZONES = {"Karachi", "Lahore", "Islamabad", "Peshawar", "Quetta", "Multan", "Faisalabad", "Other"}

PLATFORM_TO_CATEGORY = {
    "Careem": "ride-hailing",
    "Uber": "ride-hailing",
    "InDrive": "ride-hailing",
    "Shopee": "delivery",
    "Freelance": "freelance",
    "Domestic Work": "domestic-work",
    "Other": "other",
}

# Triple-quoted raw string avoids single-quote escaping issues
_SPECIAL_CHAR_RE = re.compile(r"""[!@#$%^&*()\-_=+\[\]{};:'",.<>?/\\|`~]""")


def _validate_password_strength(v: str) -> str:
    errors = []
    if len(v) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", v):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", v):
        errors.append("one lowercase letter")
    if not re.search(r"\d", v):
        errors.append("one digit")
    if not _SPECIAL_CHAR_RE.search(v):
        errors.append("one special character (!@#$%^&* etc.)")
    if errors:
        raise ValueError("Password must contain: " + ", ".join(errors))
    return v


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str
    full_name: Optional[str] = None
    platform: Optional[str] = None
    city_zone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @field_validator("role")
    @classmethod
    def check_role(cls, v: str) -> str:
        if v not in VALID_ROLES:
            raise ValueError(f"role must be one of: {', '.join(sorted(VALID_ROLES))}")
        return v

    @field_validator("platform")
    @classmethod
    def check_platform(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_PLATFORMS:
            raise ValueError(f"platform must be one of: {', '.join(sorted(VALID_PLATFORMS))}")
        return v

    @field_validator("city_zone")
    @classmethod
    def check_city_zone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_CITY_ZONES:
            raise ValueError(f"city_zone must be one of: {', '.join(sorted(VALID_CITY_ZONES))}")
        return v


class RegisterResponse(BaseModel):
    requires_otp: bool
    otp_sent_to: str
    message: str


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    refresh_token: str
    role: str
    user_id: str
    expires_in: int  # access token lifetime in seconds


# ---------------------------------------------------------------------------
# OTP
# ---------------------------------------------------------------------------

class OtpSendRequest(BaseModel):
    email: EmailStr


class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


# ---------------------------------------------------------------------------
# Token refresh / verify
# ---------------------------------------------------------------------------

class RefreshRequest(BaseModel):
    refresh_token: str


class RefreshResponse(BaseModel):
    token: str
    expires_in: int


class VerifyResponse(BaseModel):
    valid: bool
    user_id: str
    email: str
    role: str


# ---------------------------------------------------------------------------
# Current user (GET /auth/me)
# ---------------------------------------------------------------------------

class WorkerProfile(BaseModel):
    full_name: str
    city_zone: str
    primary_platform: str
    category: str
    verified_entries_count: int

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    user_id: str
    email: str
    role: str
    email_verified: bool
    created_at: str
    worker_profile: Optional[WorkerProfile] = None


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password_strength(v)


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
