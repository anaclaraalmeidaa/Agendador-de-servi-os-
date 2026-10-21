import hashlib, hmac, secrets
from fastapi import Request
from app.config import SESSION_SECRET

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, salt_hex, digest_hex = encoded.split("$")
        return scheme == "scrypt" and hmac.compare_digest(hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1).hex(), digest_hex)
    except (ValueError, TypeError): return False

def require_professional(request: Request):
    identity = request.session.get("professional_id")
    if not identity: return None
    return identity

def new_csrf_token() -> str: return secrets.token_urlsafe(32)
