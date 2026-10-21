from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Annotated
from app.auth import USERS_DB, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & Access Control"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(payload: LoginRequest):
    """
    Authenticates user credentials and issues an access token with role claims.
    Admin account: admin@subscriptiq.ai / admin123
    User account: user@subscriptiq.ai / user123
    """
    email_clean = payload.email.strip().lower()
    user = USERS_DB.get(email_clean)

    if not user or user["password"] != payload.password.strip():
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }

@router.get("/me")
async def get_my_profile(current_user: Annotated[dict, Depends(get_current_user)]):
    """
    Returns current authenticated profile and verified permissions.
    """
    return {
        "authenticated": True,
        "email": current_user.get("sub"),
        "name": current_user.get("name"),
        "role": current_user.get("role"),
        "is_admin": current_user.get("role") == "admin"
    }
