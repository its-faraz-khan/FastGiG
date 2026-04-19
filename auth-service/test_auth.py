"""
End-to-end tests for every Phase 0.2 auth endpoint.
Run: python test_auth.py
"""
import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"

import psycopg
import requests

BASE = "http://localhost:8001"
DB   = "postgresql://postgres:%40Uckhan%406435@localhost:5432/fairgig_db"

results = []


def check(label, resp, expected_status, check_keys=()):
    body = {}
    try:
        body = resp.json()
    except Exception:
        pass
    ok = resp.status_code == expected_status and all(k in body for k in check_keys)
    results.append(ok)
    mark = "PASS" if ok else "FAIL"
    detail = str(body) if not ok else ""
    print(f"  [{mark}] {label} ({resp.status_code}) {detail}")
    return ok


def run():
    # ------------------------------------------------------------------
    # 1. Health
    # ------------------------------------------------------------------
    r = requests.get(f"{BASE}/health")
    check("GET /health", r, 200, ["status", "service", "version"])

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/register", json={
        "email": "verif3@test.com", "password": "Verify@1234", "role": "verifier"
    })
    check("POST /register (verifier)", r, 201, ["requires_otp", "otp_sent_to"])

    r = requests.post(f"{BASE}/auth/register", json={
        "email": "work3@test.com", "password": "Worker@1234", "role": "worker",
        "full_name": "Sara Ahmed", "platform": "Shopee", "city_zone": "Lahore",
    })
    check("POST /register (worker)", r, 201, ["requires_otp"])

    r = requests.post(f"{BASE}/auth/register", json={
        "email": "work3@test.com", "password": "Worker@1234", "role": "worker",
        "full_name": "Dup", "platform": "Shopee", "city_zone": "Lahore",
    })
    check("POST /register (duplicate email -> 400)", r, 400)

    r = requests.post(f"{BASE}/auth/register", json={
        "email": "x@x.com", "password": "Abc@1234", "role": "admin",
    })
    check("POST /register (bad role -> 422)", r, 422)

    r = requests.post(f"{BASE}/auth/register", json={
        "email": "y@y.com", "password": "weak", "role": "advocate",
    })
    check("POST /register (weak password -> 422)", r, 422)

    r = requests.post(f"{BASE}/auth/register", json={
        "email": "z@z.com", "password": "Strong@1234", "role": "worker",
    })
    check("POST /register (worker missing fields -> 400)", r, 400)

    # Fetch OTPs from DB
    conn = psycopg.connect(DB)
    otp_w = conn.execute(
        "SELECT token FROM otp_tokens WHERE email='work3@test.com' "
        "AND is_used=false ORDER BY created_at DESC LIMIT 1"
    ).fetchone()[0]
    otp_v = conn.execute(
        "SELECT token FROM otp_tokens WHERE email='verif3@test.com' "
        "AND is_used=false ORDER BY created_at DESC LIMIT 1"
    ).fetchone()[0]
    print(f"  [INFO] Worker OTP={otp_w}   Verifier OTP={otp_v}")

    # ------------------------------------------------------------------
    # OTP verify
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/otp/verify",
                      json={"email": "work3@test.com", "otp": otp_w})
    check("POST /otp/verify (worker)", r, 200,
          ["token", "refresh_token", "role", "user_id", "expires_in"])
    assert r.json()["role"] == "worker"
    assert r.json()["expires_in"] == 900, f"expires_in={r.json()['expires_in']}"
    worker_token   = r.json()["token"]
    worker_refresh = r.json()["refresh_token"]

    r = requests.post(f"{BASE}/auth/otp/verify",
                      json={"email": "verif3@test.com", "otp": otp_v})
    check("POST /otp/verify (verifier)", r, 200)
    assert r.json()["role"] == "verifier"

    r = requests.post(f"{BASE}/auth/otp/verify",
                      json={"email": "work3@test.com", "otp": otp_w})
    check("POST /otp/verify (used OTP -> 400)", r, 400)

    r = requests.post(f"{BASE}/auth/otp/verify",
                      json={"email": "work3@test.com", "otp": "abcdef"})
    check("POST /otp/verify (non-digit OTP -> 422)", r, 422)

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "work3@test.com", "password": "Worker@1234"})
    check("POST /login (correct)", r, 200,
          ["token", "refresh_token", "role", "expires_in"])

    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "work3@test.com", "password": "wrongpass"})
    check("POST /login (wrong password -> 401)", r, 401)

    # Unverified user
    requests.post(f"{BASE}/auth/register", json={
        "email": "unverif3@test.com", "password": "Test@1234", "role": "advocate"
    })
    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "unverif3@test.com", "password": "Test@1234"})
    check("POST /login (unverified -> 403)", r, 403)

    # ------------------------------------------------------------------
    # Token verify
    # ------------------------------------------------------------------
    r = requests.get(f"{BASE}/auth/verify",
                     headers={"Authorization": f"Bearer {worker_token}"})
    check("GET /auth/verify (valid)", r, 200, ["valid", "user_id", "email", "role"])
    assert r.json()["role"] == "worker"

    r = requests.get(f"{BASE}/auth/verify",
                     headers={"Authorization": "Bearer badtoken"})
    check("GET /auth/verify (bad token -> 401)", r, 401)

    r = requests.get(f"{BASE}/auth/verify")
    check("GET /auth/verify (no header -> 401)", r, 401)

    # Refresh token must not work as access token
    r = requests.get(f"{BASE}/auth/verify",
                     headers={"Authorization": f"Bearer {worker_refresh}"})
    check("GET /auth/verify (refresh token as access -> 401)", r, 401)

    # ------------------------------------------------------------------
    # GET /auth/me
    # ------------------------------------------------------------------
    r = requests.get(f"{BASE}/auth/me",
                     headers={"Authorization": f"Bearer {worker_token}"})
    check("GET /auth/me (worker)", r, 200,
          ["user_id", "email", "role", "email_verified", "worker_profile"])
    wp = r.json().get("worker_profile", {})
    assert wp.get("full_name") == "Sara Ahmed",      f"Wrong name: {wp}"
    assert wp.get("primary_platform") == "Shopee",   f"Wrong platform: {wp}"
    assert wp.get("city_zone") == "Lahore",           f"Wrong zone: {wp}"
    assert wp.get("category") == "delivery",          f"Wrong category: {wp}"

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/refresh",
                      json={"refresh_token": worker_refresh})
    check("POST /auth/refresh", r, 200, ["token", "expires_in"])
    new_token = r.json()["token"]

    r = requests.get(f"{BASE}/auth/verify",
                     headers={"Authorization": f"Bearer {new_token}"})
    check("GET /auth/verify (with refreshed token)", r, 200)

    # ------------------------------------------------------------------
    # OTP resend
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/otp/send",
                      json={"email": "work3@test.com"})
    check("POST /otp/send (known email)", r, 200, ["message"])

    r = requests.post(f"{BASE}/auth/otp/send",
                      json={"email": "nobody@fake.com"})
    check("POST /otp/send (unknown email, same response)", r, 200)

    # ------------------------------------------------------------------
    # Forgot password + reset
    # ------------------------------------------------------------------
    r = requests.post(f"{BASE}/auth/forgot-password",
                      json={"email": "work3@test.com"})
    check("POST /forgot-password", r, 200, ["message"])

    reset_tok = conn.execute(
        "SELECT token FROM password_reset_tokens "
        "WHERE is_used=false ORDER BY created_at DESC LIMIT 1"
    ).fetchone()[0]
    print(f"  [INFO] Reset token (first 30): {reset_tok[:30]}...")

    r = requests.post(f"{BASE}/auth/reset-password",
                      json={"token": reset_tok, "new_password": "NewPass@9876"})
    check("POST /reset-password (valid)", r, 200, ["message"])

    r = requests.post(f"{BASE}/auth/reset-password",
                      json={"token": reset_tok, "new_password": "NewPass@9876"})
    check("POST /reset-password (used token -> 400)", r, 400)

    r = requests.post(f"{BASE}/auth/login",
                      json={"email": "work3@test.com", "password": "NewPass@9876"})
    check("POST /login (after password reset)", r, 200, ["token"])

    r = requests.post(f"{BASE}/auth/reset-password",
                      json={"token": "faketoken", "new_password": "weak"})
    check("POST /reset-password (weak password -> 422)", r, 422)

    conn.close()

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------
    total  = len(results)
    passed = sum(results)
    failed = total - passed
    print()
    print("=" * 54)
    print(f"  {passed}/{total} PASSED" + (f"   ({failed} FAILED)" if failed else ""))
    print("=" * 54)
    return all(results)


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
