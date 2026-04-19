"""
Start all FairGig auth-service development processes.

Usage (from auth-service/ directory, with venv active):
    python start.py

Starts:
  • Mail server on localhost:1025  (mail_server.py)
  • Auth service on localhost:8001 (main.py, auto-reload enabled)
"""
import os
import signal
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable


def main():
    print("Starting FairGig Auth Service...\n")

    mail = subprocess.Popen(
        [PYTHON, os.path.join(ROOT, "mail_server.py")],
        cwd=ROOT,
    )
    time.sleep(1)

    auth = subprocess.Popen(
        [PYTHON, os.path.join(ROOT, "main.py")],
        cwd=ROOT,
    )

    def _shutdown(sig, frame):
        print("\nShutting down...")
        mail.terminate()
        auth.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print("\nServices running:")
    print("  Auth API  →  http://localhost:8001")
    print("  Swagger   →  http://localhost:8001/docs")
    print("  Mail log  →  auth-service/emails.json")
    print("\nPress Ctrl+C to stop all services.\n")

    auth.wait()


if __name__ == "__main__":
    main()
