# backend/routers/users.py
"""
Routes utilisateur :
- PUT  /api/users/profile            — mise à jour profil (username, bio, photo)
- PUT  /api/users/credentials        — changement email + mot de passe
- GET  /api/users/profile/badges     — badges ClubID calculés depuis la collection
- POST /api/users/follow             — follow team ou player
- DELETE /api/users/follow           — unfollow
- GET  /api/users/follows            — liste des entités suivies
- POST /api/players/{player_id}/aura — voter l'aura d'un joueur (1-5)
- GET  /api/players/{player_id}/aura — récupère le score aura communautaire
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database import db
from auth import get_current_user
from routers.notifications import create_notification
import uuid

router = APIRouter(prefix="/api", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Pydantic models ──────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    username:           Optional[str] = None
    description:        Optional[str] = None
    collection_privacy: Optional[str] = None
    profile_picture:    Optional[str] = None


class CredentialsUpdate(BaseModel):
    current_password: str
    new_email:        Optional[EmailStr] = None
    new_password:     Optional[str]      = None


class FollowRequest(BaseModel):
    target_type: Literal["team", "player"]
    target_id:   str


class AuraVote(BaseModel):
    score: int  # 1-5


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.put("/users/profile")
async def update_profile(update: ProfileUpdate, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "username" in data:
        taken = await db.users.find_one({"username": data["username"], "user_id": {"$ne": uid}})
        if taken:
            raise HTTPException(status_code=400, detail="Username already taken")
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"user_id": uid}, {"$set": data})
    return await db.users.find_one({"user_id": uid}, {"_id": 0, "password_hash": 0})


@router.put("/users/credentials")
async def update_credentials(update: CredentialsUpdate, request: Request):
    user     = await get_current_user(request)
    uid      = user["user_id"]
    user_doc = await db.users.find_one({"user_id": uid})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    # Vérification du mot de passe actuel obligatoire
    if not pwd_context.verify(update.current_password, user_doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")

    patch = {}

    if update.new_email:
        if update.new_email != user_doc["email"]:
            existing = await db.users.find_one({"email": update.new_email})
            if existing:
                raise HTTPException(status_code=400, detail="Email déjà utilisé")
        patch["email"] = update.new_email

    if update.new_password:
        if len(update.new_password) < 8:
            raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 8 caractères")
        patch["password_hash"] = pwd_context.hash(update.new_password)

    if not patch:
        raise HTTPException(status_code=400, detail="Aucun changement à effectuer")

    patch["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"user_id": uid}, {"$set": patch})
    return {"message": "Credentials updated"}


# ─── Badges ───────────────────────────────────────────────────────────────────

@router.get("/users/profile/badges")
async def get_user_badges(request: Request):
    """
    Retourne les badges ClubID de l'utilisateur connecté.
    Un badge est décerné pour chaque club dont l'user possède >= 10 maillots.
    Inclut primary_color/secondary_color de l'équipe pour coloriser le badge.
    """
    user = await get_current_user(request)
    uid  = user["user_id"]

    # Agrégation : compte les kits par club depuis la collection de l'user
    pipeline = [
        {"$match": {"user_id": uid}},
        {"$lookup": {
            "from":         "master_kits",
            "localField":   "kit_id",
            "foreignField": "kit_id",
            "as":           "master_kit",
        }},
        {"$unwind": {"path": "$master_kit", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id":     "$master_kit.team_id",
            "club":    {"$first": "$master_kit.club"},
            "count":   {"$sum": 1},
        }},
        {"$match": {"count": {"$gte": 10}, "_id": {"$ne": None}}},
    ]
    results = await db.collections.aggregate(pipeline).to_list(100)

    badges = []
    for r in results:
        team_id = r["_id"]
        team    = await db.teams.find_one({"team_id": team_id}, {"_id": 0, "primary_color": 1, "secondary_color": 1, "name": 1}) or {}
        badges.append({
            "type":            "clubid_fan",
            "club":            r["club"] or team.get("name", ""),
            "team_id":         team_id,
            "kit_count":       r["count"],
            "primary_color":   team.get("primary_color", "#6366f1"),
            "secondary_color": team.get("secondary_color", "#ffffff"),
        })

    return {"badges": badges}


# ─── Follow ───────────────────────────────────────────────────────────────────

@router.post("/users/follow")
async def follow_entity(body: FollowRequest, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    existing = await db.follows.find_one({
        "user_id":     uid,
        "target_type": body.target_type,
        "target_id":   body.target_id,
    })
    if existing:
        return {"message": "Already following"}
    await db.follows.insert_one({
        "follow_id":   f"follow_{uuid.uuid4().hex[:12]}",
        "user_id":     uid,
        "target_type": body.target_type,
        "target_id":   body.target_id,
        "created_at":  datetime.now(timezone.utc).isoformat(),
    })
    return {"message": f"Now following {body.target_type} {body.target_id}"}


@router.delete("/users/follow")
async def unfollow_entity(body: FollowRequest, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    result = await db.follows.delete_one({
        "user_id":     uid,
        "target_type": body.target_type,
        "target_id":   body.target_id,
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Follow not found")
    return {"message": "Unfollowed"}


@router.get("/users/follows")
async def get_follows(request: Request):
    user    = await get_current_user(request)
    uid     = user["user_id"]
    follows = await db.follows.find({"user_id": uid}, {"_id": 0}).to_list(500)

    # Enrichit chaque follow avec target_name
    for f in follows:
        try:
            if f["target_type"] == "team":
                doc = await db.teams.find_one({"team_id": f["target_id"]}, {"name": 1})
                f["target_name"] = doc["name"] if doc else f["target_id"]
            elif f["target_type"] == "player":
                doc = await db.players.find_one({"player_id": f["target_id"]}, {"full_name": 1})
                f["target_name"] = doc["full_name"] if doc else f["target_id"]
        except Exception:
            f["target_name"] = f["target_id"]

    return {"follows": follows}


@router.get("/users/follows/{target_type}/{target_id}")
async def is_following(target_type: str, target_id: str, request: Request):
    user = await get_current_user(request)
    uid  = user["user_id"]
    doc  = await db.follows.find_one({
        "user_id":     uid,
        "target_type": target_type,
        "target_id":   target_id,
    })
    return {"following": doc is not None}


# ─── Aura communautaire ───────────────────────────────────────────────────────

@router.post("/players/{player_id}/aura")
async def vote_player_aura(player_id: str, body: AuraVote, request: Request):
    """Vote 1-5 étoiles sur l'aura d'un joueur. Un user = un vote (modifiable)."""
    if body.score < 1 or body.score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 5")
    user = await get_current_user(request)
    uid  = user["user_id"]

    player = await db.players.find_one({"player_id": player_id}, {"_id": 0, "player_id": 1})
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Upsert le vote
    await db.player_aura_votes.update_one(
        {"player_id": player_id, "user_id": uid},
        {"$set": {
            "score":      body.score,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )

    # Recalcule le score moyen et met à jour le joueur
    pipeline = [
        {"$match": {"player_id": player_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$score"}, "count": {"$sum": 1}}},
    ]
    agg = await db.player_aura_votes.aggregate(pipeline).to_list(1)
    avg_score   = agg[0]["avg"]   if agg else body.score
    vote_count  = agg[0]["count"] if agg else 1

    # Arrondi au niveau 1-5 le plus proche
    aura_level = max(1, min(5, round(avg_score)))

    await db.players.update_one(
        {"player_id": player_id},
        {"$set": {"aura_level": aura_level, "aura_avg": round(avg_score, 2), "aura_vote_count": vote_count}},
    )

    return {
        "aura_level":    aura_level,
        "aura_avg":      round(avg_score, 2),
        "aura_votes":    vote_count,
        "your_vote":     body.score,
    }


@router.get("/players/{player_id}/aura")
async def get_player_aura(player_id: str, request: Request):
    """Retourne le score aura communautaire + le vote de l'user connecté si disponible."""
    player = await db.players.find_one(
        {"player_id": player_id},
        {"_id": 0, "aura_level": 1, "aura_avg": 1, "aura_vote_count": 1}
    )
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    your_vote = None
    try:
        user = await get_current_user(request)
        vote = await db.player_aura_votes.find_one(
            {"player_id": player_id, "user_id": user["user_id"]},
            {"_id": 0, "score": 1}
        )
        if vote:
            your_vote = vote["score"]
    except Exception:
        pass  # utilisateur non connecté → pas de vote personnel

    return {
        "aura_level":  player.get("aura_level", 1),
        "aura_avg":    player.get("aura_avg", 0.0),
        "aura_votes":  player.get("aura_vote_count", 0),
        "your_vote":   your_vote,
    }
