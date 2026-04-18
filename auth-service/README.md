# FairGig Auth Service

FastAPI authentication microservice for the FairGig platform.  
Runs on `http://localhost:8001` — Swagger docs at `http://localhost:8001/docs`.

---

## Prerequisites

- Python 3.9+
- PostgreSQL running with `fairgig_db` created and schema applied
- MailHog running on `localhost:1025` (for OTP and reset emails in development)

### Install MailHog (Development Email Server)

**Windows (via Go or pre-built binary):**
Download from https://github.com/mailhog/MailHog/releases and run `MailHog.exe`.

**macOS:**
```bash
brew install mailhog
mailhog
```

**Docker (any platform):**
```bash
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

MailHog web UI: `http://localhost:8025` — all sent emails appear here.

---

## Setup

### 1. Create and activate a virtual environment

```bash
cd auth-service

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
```

Minimum required settings in `.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/fairgig_db
JWT_SECRET=replace-with-a-long-random-string
```

Generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Run the service

```bash
python main.py
```

Or via uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

---

## Endpoints

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| POST | `/auth/register` | Create account + send OTP | — |
| POST | `/auth/login` | Email/password login → JWT | 5/min per IP |
| POST | `/auth/otp/send` | Resend OTP to email | 3/min per IP |
| POST | `/auth/otp/verify` | Verify OTP → JWT | — |
| POST | `/auth/refresh` | Exchange refresh token → new access token | — |
| GET | `/auth/verify` | Validate token (used by other services) | — |
| POST | `/auth/forgot-password` | Send password reset email | 3/min per IP |
| POST | `/auth/reset-password` | Reset password with token | — |

---

## Token Design

**Access token** — short-lived (default 15 min):
```json
{
  "sub": "<user-uuid>",
  "email": "user@example.com",
  "role": "worker",
  "type": "access",
  "iat": 1713400000,
  "exp": 1713400900
}
```

**Refresh token** — long-lived (default 7 days), same payload with `"type": "refresh"`.

---

## Manual API Testing

### Register a worker
```bash
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@1234",
    "role": "worker",
    "full_name": "Ali Raza",
    "platform": "Careem",
    "city_zone": "Karachi"
  }'
```

### Verify OTP (check MailHog at http://localhost:8025 for the code)
```bash
curl -X POST http://localhost:8001/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'
```

### Login
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test@1234"}'
```

### Validate a token (from another service)
```bash
curl http://localhost:8001/auth/verify \
  -H "Authorization: Bearer <access_token>"
```

---

## Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (`!@#$%^&*` etc.)

---

## Project Structure

```
auth-service/
├── main.py          # FastAPI app — all routes
├── database.py      # SQLAlchemy engine and session factory
├── db_models.py     # ORM models (maps to existing schema.sql tables)
├── schemas.py       # Pydantic request/response models
├── auth_utils.py    # JWT encode/decode, bcrypt hashing
├── email_utils.py   # Async email sending via MailHog SMTP
├── requirements.txt
├── .env.example
└── README.md
```

---

## Next Step

Once this service is running and you can register/login successfully, proceed to:

**Phase 1.1** — Frontend Project Setup (React + TypeScript + Tailwind CSS)
