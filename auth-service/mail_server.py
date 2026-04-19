"""
FairGig debug SMTP server (MailHog substitute).
Accepts all emails on localhost:1025, prints OTPs/tokens to the terminal,
and saves every email to emails.json for inspection.

Run standalone: python mail_server.py
Or use: python start.py  (starts both this and the auth service)
"""
import asyncio
import json
import os
import re
from datetime import datetime
from email import message_from_bytes

from aiosmtpd.controller import Controller

EMAILS_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emails.json")


class _Handler:
    """Custom aiosmtpd handler: logs emails and highlights OTPs / reset tokens."""

    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        msg = message_from_bytes(envelope.content)
        subject = msg.get("Subject", "")
        to_addr = ", ".join(envelope.rcpt_tos)

        body_html = ""
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                decoded = payload.decode("utf-8", errors="replace")
                if ct == "text/html":
                    body_html = decoded
                elif ct == "text/plain":
                    body_text = decoded
        else:
            payload = msg.get_payload(decode=True) or b""
            body_text = payload.decode("utf-8", errors="replace")

        content = body_html or body_text

        # ── Console output ──────────────────────────────────────────────────
        sep = "=" * 62
        print(f"\n{sep}")
        print(f"  MAIL  To: {to_addr}")
        print(f"        Subject: {subject}")

        otp_match = re.search(r"\b(\d{6})\b", content)
        if otp_match:
            print(f"  OTP  >>>  {otp_match.group(1)}  <<<")

        link_match = re.search(r"reset-password/([A-Za-z0-9_\-]+)", content)
        if link_match:
            token = link_match.group(1)
            print(f"  RESET TOKEN  >>>  {token[:40]}{'...' if len(token) > 40 else ''}  <<<")

        print(f"{sep}\n")

        # ── Save to emails.json ─────────────────────────────────────────────
        entry = {
            "received_at": datetime.utcnow().isoformat(),
            "from": envelope.mail_from,
            "to": to_addr,
            "subject": subject,
            "otp": otp_match.group(1) if otp_match else None,
            "reset_token": link_match.group(1) if link_match else None,
            "body_html": body_html[:8000] or None,
            "body_text": body_text[:4000] or None,
        }

        try:
            with open(EMAILS_LOG) as f:
                emails = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            emails = []

        emails.insert(0, entry)

        with open(EMAILS_LOG, "w") as f:
            json.dump(emails[:100], f, indent=2)

        return "250 Message accepted for delivery"


def run():
    controller = Controller(_Handler(), hostname="127.0.0.1", port=2525)
    controller.start()
    print(f"[MAIL SERVER] Listening on 127.0.0.1:2525")
    print(f"[MAIL SERVER] Emails saved to: {EMAILS_LOG}")
    print(f"[MAIL SERVER] Press Ctrl+C to stop\n")
    async def _run_forever():
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass

    try:
        asyncio.run(_run_forever())
    except KeyboardInterrupt:
        controller.stop()
        print("\n[MAIL SERVER] Stopped.")


if __name__ == "__main__":
    run()
