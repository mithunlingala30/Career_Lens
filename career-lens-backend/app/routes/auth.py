import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from ..config import DEBUG
from ..database import get_store
from ..schemas import ForgotIn, LoginIn, RegisterIn, ResetIn
from ..utils.helpers import user_out
from ..utils.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(body: RegisterIn, store=Depends(get_store)):
    email = body.email.lower()
    if store.one("users", email=email):
        raise HTTPException(409, "An account with this email already exists")
    user = store.create("users", {"full_name": body.full_name.strip(), "email": email, "password_hash": hash_password(body.password),
                                  "role": "candidate", "is_active": True, "reset_token": None, "reset_token_expires": None})
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_out(user)}


@router.post("/login")
def login(body: LoginIn, store=Depends(get_store)):
    user = store.one("users", email=body.email.lower())
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Incorrect email or password")
    if not user.get("is_active", True):
        raise HTTPException(403, "This account is disabled")
    if body.role and body.role != user["role"]:
        raise HTTPException(403, "This account is not an administrator account" if body.role == "admin" else "Use the admin login for this account")
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": user_out(user)}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user_out(user)


@router.post("/forgot-password")
def forgot(body: ForgotIn, store=Depends(get_store)):
    """No e-mail server is bundled: in DEBUG mode the reset token is returned so the flow can be tested."""
    user = store.one("users", email=body.email.lower())
    out = {"message": "If the email exists, a reset token has been generated."}
    if user:
        token = secrets.token_urlsafe(24)
        store.update("users", user["id"], {"reset_token": token, "reset_token_expires": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()})
        if DEBUG:
            out["dev_reset_token"] = token
    return out


@router.post("/reset-password")
def reset(body: ResetIn, store=Depends(get_store)):
    user = store.one("users", reset_token=body.token)
    if not user or not user.get("reset_token_expires") or datetime.fromisoformat(user["reset_token_expires"]) < datetime.now(timezone.utc):
        raise HTTPException(400, "Reset token is invalid or expired")
    store.update("users", user["id"], {"password_hash": hash_password(body.new_password), "reset_token": None, "reset_token_expires": None})
    return {"message": "Password updated. You can now sign in."}
