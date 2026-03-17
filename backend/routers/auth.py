from fastapi import APIRouter, HTTPException, Request, Response
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import uuid
from database import db
from auth import get_current_user
from utils import MODERATOR_EMAILS

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        secure=False,       # True en production HTTPS
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60
    )


@router.post("/register")
async def register(body: RegisterBody, response: Response):
    existing = await db.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    role = "moderator" if body.email in MODERATOR_EMAILS else "user"

    await db.users.insert_one({
        "user_id": user_id,
        "email": body.email,
        "name": body.name,
        "picture": "",
        "role": role,
        "username": body.name.replace(" ", "").lower() if body.name else "",
        "description": "",
        "collection_privacy": "public",
        "password_hash": pwd_context.hash(body.password),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    session_token = uuid.uuid4().hex
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    set_session_cookie(response, session_token)
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0, "password_hash": 0})
    return user_doc


@router.post("/login")
async def login(body: LoginBody, response: Response):
    user = await db.users.find_one({"email": body.email})
    if not user or not pwd_context.verify(body.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    session_token = uuid.uuid4().hex
    await db.user_sessions.insert_one({
        "user_id": user["user_id"],
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    set_session_cookie(response, session_token)
    user_doc = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0, "password_hash": 0})
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
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out"}
