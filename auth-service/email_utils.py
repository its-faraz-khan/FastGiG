import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()

MAILHOG_HOST = os.getenv("MAILHOG_SMTP_HOST", "localhost")
MAILHOG_PORT = int(os.getenv("MAILHOG_SMTP_PORT", "1025"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@fairgig.app")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


async def send_otp_email(to_email: str, otp: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "FairGig - Email Verification OTP"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
        <h2 style="color: #1e3a5f;">FairGig Email Verification</h2>
        <p>Your one-time password (OTP) for email verification is:</p>
        <div style="
            background: #f0f4ff;
            border: 2px solid #2563eb;
            border-radius: 8px;
            padding: 24px;
            text-align: center;
            margin: 24px 0;
        ">
            <span style="
                color: #2563eb;
                font-size: 48px;
                font-weight: bold;
                letter-spacing: 12px;
                font-family: monospace;
            ">{otp}</span>
        </div>
        <p>This OTP expires in <strong>5 minutes</strong>.</p>
        <p style="color: #6b7280; font-size: 13px;">
            If you did not create a FairGig account, you can safely ignore this email.
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=MAILHOG_HOST,
        port=MAILHOG_PORT,
    )


async def send_password_reset_email(to_email: str, reset_token: str) -> None:
    reset_link = f"{FRONTEND_URL}/reset-password/{reset_token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "FairGig - Password Reset Request"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px;">
        <h2 style="color: #1e3a5f;">FairGig Password Reset</h2>
        <p>We received a request to reset your password. Click the button below to proceed:</p>
        <div style="text-align: center; margin: 32px 0;">
            <a href="{reset_link}" style="
                display: inline-block;
                background-color: #2563eb;
                color: white;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            ">Reset Password</a>
        </div>
        <p style="font-size: 13px; color: #6b7280;">
            Or copy this link into your browser:<br>
            <a href="{reset_link}" style="color: #2563eb;">{reset_link}</a>
        </p>
        <p>This link expires in <strong>24 hours</strong>.</p>
        <p style="color: #6b7280; font-size: 13px;">
            If you did not request a password reset, please ignore this email.
            Your password will not change.
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=MAILHOG_HOST,
        port=MAILHOG_PORT,
    )
