from fastapi import HTTPException, Request
from datetime import datetime, timezone
from .database import db, client
from utils import MODERATOR_EMAILS
import os

IS_DEV_LOGIN = os.getenv("DEV_LOGIN", "false").lower() == "true"


async def get_current_user(request: Request) -> dict:
    if IS_DEV_LOGIN:
        return {
            "user_id": "dev-user-1",
            "email": "dev@topkit.local",
            "name": "Dev User",
            "picture": "",
            "role": "moderator",
        }

    session_token = request.cookies.get("session_token")
    if not session_token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            session_token = auth_header[7:]
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_doc = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")

    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    user_doc = await db.users.find_one({"user_id": session_doc["user_id"]}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")

    if "role" not in user_doc:
        user_doc["role"] = "moderator" if user_doc.get("email") in MODERATOR_EMAILS else "user"

    user_doc.pop("password_hash", None)
    return user_doc
