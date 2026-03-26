from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import uuid
import os
from ..database import db, client
from ..auth import get_current_user
from ..utils import MODERATOR_EMAILS
from ..email_service import send_welcome, send_password_reset

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


class ForgotPasswordBody(BaseModel):
    email: EmailStr


class ResetPasswordBody(BaseModel):
    token: str
    new_password: str


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
            "last_active": datetime.now(timezone.utc).isoformat(),
        }
    )

    set_session_cookie(response, session_token)
    user_doc = await db.users.find_one(
        {"user_id": user_id}, {"_id": 0, "password_hash": 0}
    )

    # Email de bienvenue (non-bloquant)
    await send_welcome(body.email, body.name.strip())

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
            "last_active": datetime.now(timezone.utc).isoformat(),
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


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordBody):
    """
    Demande de reset de mot de passe.
    Retourne toujours 200 même si l'email est inconnu (anti-enumeration).
    """
    user = await db.users.find_one({"email": body.email})
    if user:
        # Invalider les anciens tokens non utilisés pour cet email
        await db.password_resets.delete_many({"email": body.email, "used": False})

        reset_token = uuid.uuid4().hex
        expires     = datetime.now(timezone.utc) + timedelta(hours=1)

        await db.password_resets.insert_one({
            "token":      reset_token,
            "user_id":    user["user_id"],
            "email":      body.email,
            "expires_at": expires.isoformat(),
            "used":       False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

        await send_password_reset(body.email, reset_token)

    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé."}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordBody):
    """Réinitialise le mot de passe via un token reçu par email."""
    doc = await db.password_resets.find_one({"token": body.token, "used": False})
    if not doc:
        raise HTTPException(status_code=400, detail="Token invalide ou déjà utilisé")

    expires = datetime.fromisoformat(doc["expires_at"])
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expiré (1h max)")

    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Le mot de passe doit contenir au moins 8 caractères",
        )

    new_hash = pwd_context.hash(normalize_password(body.new_password))

    await db.users.update_one(
        {"user_id": doc["user_id"]},
        {"$set": {
            "password_hash": new_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    # Invalide le token
    await db.password_resets.update_one(
        {"token": body.token},
        {"$set": {"used": True}}
    )
    # Invalide toutes les sessions actives par sécurité
    await db.user_sessions.delete_many({"user_id": doc["user_id"]})

    return {"message": "Mot de passe réinitialisé. Reconnecte-toi."}
