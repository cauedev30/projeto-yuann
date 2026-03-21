from __future__ import annotations

from datetime import datetime, timedelta, timezone

import hashlib
import hmac
import base64
import json


def hash_password(password: str) -> str:
    salt = hashlib.sha256(password.encode() + b"legalboard-salt").hexdigest()[:16]
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${hashed.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    parts = hashed_password.split("$")
    if len(parts) != 2:
        return False
    salt, stored_hash = parts
    computed = hashlib.pbkdf2_hmac("sha256", plain_password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(computed.hex(), stored_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_access_token(
    *,
    user_id: str,
    secret: str,
    expires_minutes: int = 480,
) -> str:
    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    now = datetime.now(timezone.utc)
    payload_data = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    payload = _b64url_encode(json.dumps(payload_data).encode())
    signature_input = f"{header}.{payload}".encode()
    signature = _b64url_encode(
        hmac.new(secret.encode(), signature_input, hashlib.sha256).digest()
    )
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str, *, secret: str) -> dict | None:
    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, signature_b64 = parts
    signature_input = f"{header_b64}.{payload_b64}".encode()
    expected_sig = hmac.new(secret.encode(), signature_input, hashlib.sha256).digest()
    actual_sig = _b64url_decode(signature_b64)

    if not hmac.compare_digest(expected_sig, actual_sig):
        return None

    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (json.JSONDecodeError, Exception):
        return None

    exp = payload.get("exp")
    if exp is not None and datetime.now(timezone.utc).timestamp() > exp:
        return None

    return payload
