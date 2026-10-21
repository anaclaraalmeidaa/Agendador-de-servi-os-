import hmac
from fastapi import Request
from app.security import new_csrf_token

def csrf_for(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not token:
        token = new_csrf_token(); request.session["csrf_token"] = token
    return token

def csrf_valid(request: Request, submitted: str) -> bool:
    expected = request.session.get("csrf_token", "")
    return bool(expected and submitted and hmac.compare_digest(expected, submitted))
