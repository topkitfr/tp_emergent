from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import uuid
import os
from ..database import db, client
from ..auth import get_current_user
from ..utils import MODERATOR_EMAILS

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

IS_PRODUCTION = os.getenv("ENVIRONMENT", "production").lower() == "production"

MAX_BCRYPT_BYTES = 72


def normalize_password(pwd: str) -> str:
    """Tronque le mot de passe à 72 bytes max (limite bcrypt)."""
    b = pwd.encode("utf-8")
    if len(b) > MAX_BCRYPT_BYTES:
        b = b[:MAX_BCRYPT_BYTES]
    return b.decode("utf-8", errors="ignore")


class RegisterBody(BaseModel):
    email: EmailStr
    password: str
    name: str = ""


class LoginBody(BaseModel):
    email: EmailStr
    password: str


def set_session_cookie(response: Response, session_token: str):
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,         # obligatoire avec SameSite=none
        samesite="none",     # autorise le cross-site (frontend != backend domaine)
        path="/",
        max_age=7 * 24 * 60 * 60,
    )


@router.post("/register")
async def register(body: RegisterBody, response: Response):
    if len(body.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Le mot de passe doit contenir au moins 8 caractères",
        )
    if len(body.name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Le nom doit contenir au moins 2 caractères",
        )
    if len(body.name) > 50:
        raise HTTPException(
            status_code=400,
            detail="Le nom ne peut pas dépasser 50 caractères",
        )

    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    role = "moderator" if body.email in MODERATOR_EMAILS else "user"

    password = normalize_password(body.password)

    await db.users.insert_one(
        {
            "user_id": user_id,
            "email": body.email,
            "name": body.name.strip(),
            "picture": "",
            "role": role,
            "username": body.name.replace(" ", "").lower() if body.name else "",
            "description": "",
            "collection_privacy": "public",
            "password_hash": pwd_context.hash(password),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    session_token = uuid.uuid4().hex
    await db.user_sessions.insert_one(
        {
            "user_id": user_id,
            "session_token": session_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    set_session_cookie(response, session_token)
    user_doc = await db.users.find_one(
        {"user_id": user_id}, {"_id": 0, "password_hash": 0}
    )
    return user_doc


@router.post("/login")
async def login(body: LoginBody, response: Response):
    user = await db.users.find_one({"email": body.email})
    password = normalize_password(body.password)
    if not user or not pwd_context.verify(
        password, user.get("password_hash", "")
    ):
        raise HTTPException(
            status_code=401, detail="Email ou mot de passe incorrect"
        )

    session_token = uuid.uuid4().hex
    await db.user_sessions.insert_one(
        {
            "user_id": user["user_id"],
            "session_token": session_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    set_session_cookie(response, session_token)
    user_doc = await db.users.find_one(
        {"user_id": user["user_id"]}, {"_id": 0, "password_hash": 0}
    )
    return user_doc


@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user


@router.post("/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(
        key="session_token",
        path="/",
        httponly=True,
        secure=True,
        samesite="none",
    )
    return {"message": "Logged out"}
