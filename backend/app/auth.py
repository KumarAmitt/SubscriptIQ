import time
import hmac
import hashlib
import json
import base64
from fastapi import Header, HTTPException, Depends
from typing import Annotated
from app.config import settings

SECRET_KEY = settings.JWT_SECRET

# Default demo users
USERS_DB = {
    "admin@subscriptiq.ai": {
        "id": 1,
        "name": "Alex Rivera",
        "email": "admin@subscriptiq.ai",
        "password": "admin123",
        "role": "admin"
    },
    "user@subscriptiq.ai": {
        "id": 2,
        "name": "Sarah Chen",
        "email": "user@subscriptiq.ai",
        "password": "user123",
        "role": "user"
    }
}

def create_access_token(user_data: dict, expires_in_seconds: int = 86400 * 7) -> str:
    """Creates a signed HMAC token encoding user identity and role."""
    payload = {
        "sub": user_data["email"],
        "name": user_data["name"],
        "role": user_data["role"],
        "exp": int(time.time()) + expires_in_seconds
    }
    header_b64 = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_token(token: str) -> dict:
    """Verifies HMAC signature and expiration."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token")
        
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256
        ).digest()
        
        padding = "=" * (-len(sig_b64) % 4)
        actual_sig = base64.urlsafe_b64decode(sig_b64 + padding)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Invalid signature")
            
        payload_padding = "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + payload_padding).decode())
        
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
            
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired credentials: {str(e)}")

def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    x_user_role: Annotated[str | None, Header()] = None
) -> dict:
    """
    Extracts the current user from Bearer token or development headers.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        return verify_token(token)
    
    # Development role bypass if header explicitly provided
    if x_user_role:
        role = x_user_role.lower()
        if role == "admin":
            return {"sub": "admin@subscriptiq.ai", "name": "Alex Rivera", "role": "admin"}
        return {"sub": "user@subscriptiq.ai", "name": "Standard User", "role": "user"}

    # Default to unprivileged user
    return {"sub": "guest@subscriptiq.ai", "name": "Guest User", "role": "user"}

def require_admin(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """
    Enforces that the authenticated user possesses the 'admin' role.
    Rejects unauthorized access with HTTP 403 Forbidden.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access Denied: Administrator role required to access this feature."
        )
    return current_user
