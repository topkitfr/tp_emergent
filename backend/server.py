from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, UploadFile, File, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import httpx
import uuid
import aiofiles
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Static files directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Pydantic Models ───

class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: Optional[str] = None

class MasterKitCreate(BaseModel):
    club: str
    season: str
    kit_type: str  # Home/Away/Third/Fourth/GK/Special
    brand: str
    front_photo: str
    year: int

class MasterKitOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    kit_id: str
    club: str
    season: str
    kit_type: str
    brand: str
    front_photo: str
    year: int
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    version_count: Optional[int] = 0
    avg_rating: Optional[float] = 0.0

class VersionCreate(BaseModel):
    kit_id: str
    competition: str
    model: str  # Authentic/Replica/Player Issue
    gender: str  # Men/Women/Kids
    sku_code: Optional[str] = ""
    front_photo: Optional[str] = ""
    back_photo: Optional[str] = ""

class VersionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    version_id: str
    kit_id: str
    competition: str
    model: str
    gender: str
    sku_code: Optional[str] = ""
    front_photo: Optional[str] = ""
    back_photo: Optional[str] = ""
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    avg_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0

class CollectionAdd(BaseModel):
    version_id: str
    category: Optional[str] = "General"
    notes: Optional[str] = ""

class CollectionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    collection_id: str
    user_id: str
    version_id: str
    category: str
    notes: Optional[str] = ""
    added_at: Optional[str] = None

class ReviewCreate(BaseModel):
    version_id: str
    rating: int  # 1-5
    comment: Optional[str] = ""

class ReviewOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str
    version_id: str
    user_id: str
    user_name: Optional[str] = ""
    user_picture: Optional[str] = ""
    rating: int
    comment: Optional[str] = ""
    created_at: Optional[str] = None


# ─── Auth Helpers ───

EMERGENT_AUTH_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"

async def get_current_user(request: Request) -> dict:
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
    return user_doc


# ─── Auth Routes ───

@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    body = await request.json()
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    async with httpx.AsyncClient() as hc:
        resp = await hc.get(EMERGENT_AUTH_URL, headers={"X-Session-ID": session_id})
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session_id")
        data = resp.json()
    email = data["email"]
    name = data.get("name", "")
    picture = data.get("picture", "")
    session_token = data["session_token"]
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one({"email": email}, {"$set": {"name": name, "picture": picture}})
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        await db.users.insert_one({
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    await db.user_sessions.insert_one({
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    response.set_cookie(
        key="session_token", value=session_token,
        httponly=True, secure=True, samesite="none",
        path="/", max_age=7*24*60*60
    )
    user_doc = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    return user_doc

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        await db.user_sessions.delete_one({"session_token": session_token})
    response.delete_cookie(key="session_token", path="/", secure=True, samesite="none")
    return {"message": "Logged out"}


# ─── Master Kit Routes ───

@api_router.get("/master-kits", response_model=List[MasterKitOut])
async def list_master_kits(
    club: Optional[str] = None,
    season: Optional[str] = None,
    brand: Optional[str] = None,
    kit_type: Optional[str] = None,
    year: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    query = {}
    if club:
        query["club"] = {"$regex": club, "$options": "i"}
    if season:
        query["season"] = {"$regex": season, "$options": "i"}
    if brand:
        query["brand"] = {"$regex": brand, "$options": "i"}
    if kit_type:
        query["kit_type"] = kit_type
    if year:
        query["year"] = year
    if search:
        query["$or"] = [
            {"club": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"season": {"$regex": search, "$options": "i"}}
        ]
    kits = await db.master_kits.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for kit in kits:
        version_count = await db.versions.count_documents({"kit_id": kit["kit_id"]})
        kit["version_count"] = version_count
        reviews = await db.reviews.find({"kit_id": kit["kit_id"]}, {"_id": 0, "rating": 1}).to_list(1000)
        if reviews:
            kit["avg_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1)
        else:
            kit["avg_rating"] = 0.0
    return kits

@api_router.get("/master-kits/count")
async def count_master_kits():
    count = await db.master_kits.count_documents({})
    return {"count": count}

@api_router.get("/master-kits/filters")
async def get_filters():
    clubs = await db.master_kits.distinct("club")
    brands = await db.master_kits.distinct("brand")
    seasons = await db.master_kits.distinct("season")
    years = await db.master_kits.distinct("year")
    kit_types = await db.master_kits.distinct("kit_type")
    return {
        "clubs": sorted(clubs),
        "brands": sorted(brands),
        "seasons": sorted(seasons),
        "years": sorted(years, reverse=True),
        "kit_types": sorted(kit_types)
    }

@api_router.get("/master-kits/{kit_id}")
async def get_master_kit(kit_id: str):
    kit = await db.master_kits.find_one({"kit_id": kit_id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Kit not found")
    versions = await db.versions.find({"kit_id": kit_id}, {"_id": 0}).to_list(100)
    for v in versions:
        reviews = await db.reviews.find({"version_id": v["version_id"]}, {"_id": 0, "rating": 1}).to_list(1000)
        v["avg_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
        v["review_count"] = len(reviews)
    kit["versions"] = versions
    kit["version_count"] = len(versions)
    all_reviews = await db.reviews.find({"kit_id": kit_id}, {"_id": 0, "rating": 1}).to_list(1000)
    kit["avg_rating"] = round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1) if all_reviews else 0.0
    return kit

@api_router.post("/master-kits", response_model=MasterKitOut)
async def create_master_kit(kit: MasterKitCreate, request: Request):
    user = await get_current_user(request)
    doc = kit.model_dump()
    doc["kit_id"] = f"kit_{uuid.uuid4().hex[:12]}"
    doc["created_by"] = user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    await db.master_kits.insert_one(doc)
    result = await db.master_kits.find_one({"kit_id": doc["kit_id"]}, {"_id": 0})
    result["version_count"] = 0
    result["avg_rating"] = 0.0
    return result


# ─── Version Routes ───

@api_router.get("/versions/{version_id}")
async def get_version(version_id: str):
    version = await db.versions.find_one({"version_id": version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    kit = await db.master_kits.find_one({"kit_id": version["kit_id"]}, {"_id": 0})
    version["master_kit"] = kit
    reviews = await db.reviews.find({"version_id": version_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one({"user_id": r["user_id"]}, {"_id": 0, "name": 1, "picture": 1})
        if u:
            r["user_name"] = u.get("name", "")
            r["user_picture"] = u.get("picture", "")
    version["reviews"] = reviews
    version["avg_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
    version["review_count"] = len(reviews)
    collection_count = await db.collections.count_documents({"version_id": version_id})
    version["collection_count"] = collection_count
    return version

@api_router.post("/versions", response_model=VersionOut)
async def create_version(version: VersionCreate, request: Request):
    user = await get_current_user(request)
    kit = await db.master_kits.find_one({"kit_id": version.kit_id}, {"_id": 0})
    if not kit:
        raise HTTPException(status_code=404, detail="Master Kit not found")
    doc = version.model_dump()
    doc["version_id"] = f"ver_{uuid.uuid4().hex[:12]}"
    doc["created_by"] = user["user_id"]
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    if not doc["front_photo"]:
        doc["front_photo"] = kit.get("front_photo", "")
    await db.versions.insert_one(doc)
    result = await db.versions.find_one({"version_id": doc["version_id"]}, {"_id": 0})
    result["avg_rating"] = 0.0
    result["review_count"] = 0
    return result

@api_router.get("/versions", response_model=List[VersionOut])
async def list_versions(kit_id: Optional[str] = None, skip: int = 0, limit: int = 50):
    query = {}
    if kit_id:
        query["kit_id"] = kit_id
    versions = await db.versions.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for v in versions:
        reviews = await db.reviews.find({"version_id": v["version_id"]}, {"_id": 0, "rating": 1}).to_list(1000)
        v["avg_rating"] = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0.0
        v["review_count"] = len(reviews)
    return versions


# ─── Collection Routes ───

@api_router.get("/collections")
async def get_my_collection(request: Request, category: Optional[str] = None):
    user = await get_current_user(request)
    query = {"user_id": user["user_id"]}
    if category:
        query["category"] = category
    items = await db.collections.find(query, {"_id": 0}).sort("added_at", -1).to_list(500)
    enriched = []
    for item in items:
        version = await db.versions.find_one({"version_id": item["version_id"]}, {"_id": 0})
        if version:
            kit = await db.master_kits.find_one({"kit_id": version["kit_id"]}, {"_id": 0})
            item["version"] = version
            item["master_kit"] = kit
        enriched.append(item)
    return enriched

@api_router.get("/collections/categories")
async def get_collection_categories(request: Request):
    user = await get_current_user(request)
    cats = await db.collections.distinct("category", {"user_id": user["user_id"]})
    return sorted(cats)

@api_router.post("/collections")
async def add_to_collection(item: CollectionAdd, request: Request):
    user = await get_current_user(request)
    version = await db.versions.find_one({"version_id": item.version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    existing = await db.collections.find_one(
        {"user_id": user["user_id"], "version_id": item.version_id}, {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already in collection")
    doc = {
        "collection_id": f"col_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "version_id": item.version_id,
        "category": item.category or "General",
        "notes": item.notes or "",
        "added_at": datetime.now(timezone.utc).isoformat()
    }
    await db.collections.insert_one(doc)
    result = await db.collections.find_one({"collection_id": doc["collection_id"]}, {"_id": 0})
    return result

@api_router.delete("/collections/{collection_id}")
async def remove_from_collection(collection_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.collections.delete_one({"collection_id": collection_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Removed from collection"}


# ─── Review Routes ───

@api_router.post("/reviews")
async def create_review(review: ReviewCreate, request: Request):
    user = await get_current_user(request)
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    version = await db.versions.find_one({"version_id": review.version_id}, {"_id": 0})
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    existing = await db.reviews.find_one(
        {"user_id": user["user_id"], "version_id": review.version_id}, {"_id": 0}
    )
    if existing:
        await db.reviews.update_one(
            {"review_id": existing["review_id"]},
            {"$set": {"rating": review.rating, "comment": review.comment, "created_at": datetime.now(timezone.utc).isoformat()}}
        )
        updated = await db.reviews.find_one({"review_id": existing["review_id"]}, {"_id": 0})
        return updated
    doc = {
        "review_id": f"rev_{uuid.uuid4().hex[:12]}",
        "version_id": review.version_id,
        "kit_id": version["kit_id"],
        "user_id": user["user_id"],
        "user_name": user.get("name", ""),
        "user_picture": user.get("picture", ""),
        "rating": review.rating,
        "comment": review.comment or "",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.reviews.insert_one(doc)
    result = await db.reviews.find_one({"review_id": doc["review_id"]}, {"_id": 0})
    return result

@api_router.get("/reviews")
async def get_reviews(version_id: str):
    reviews = await db.reviews.find({"version_id": version_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for r in reviews:
        u = await db.users.find_one({"user_id": r["user_id"]}, {"_id": 0, "name": 1, "picture": 1})
        if u:
            r["user_name"] = u.get("name", "")
            r["user_picture"] = u.get("picture", "")
    return reviews


# ─── Stats Routes ───

@api_router.get("/stats")
async def get_stats():
    kits = await db.master_kits.count_documents({})
    versions = await db.versions.count_documents({})
    users = await db.users.count_documents({})
    reviews = await db.reviews.count_documents({})
    return {"master_kits": kits, "versions": versions, "users": users, "reviews": reviews}


# ─── User Profile ───

@api_router.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    collection_count = await db.collections.count_documents({"user_id": user_id})
    review_count = await db.reviews.count_documents({"user_id": user_id})
    user["collection_count"] = collection_count
    user["review_count"] = review_count
    return user


# ─── Seed Data ───

@api_router.post("/seed")
async def seed_data():
    existing = await db.master_kits.count_documents({})
    if existing > 0:
        return {"message": "Data already seeded", "count": existing}

    JERSEY_PHOTOS = [
        "https://images.unsplash.com/photo-1763656812756-3539efd3e301?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
        "https://images.unsplash.com/photo-1693683224122-0a8e206f248d?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
        "https://images.unsplash.com/photo-1764116679127-dc9d2c1138a7?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
        "https://images.unsplash.com/photo-1768146106244-e1ac5490504f?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
        "https://images.unsplash.com/photo-1671810458671-759db56dc405?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
        "https://images.unsplash.com/photo-1616479719489-a68220dc9d6e?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
    ]

    seed_kits = [
        {"club": "FC Barcelona", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "FC Barcelona", "season": "2024/2025", "kit_type": "Away", "brand": "Nike", "year": 2024},
        {"club": "Real Madrid", "season": "2024/2025", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "Real Madrid", "season": "2023/2024", "kit_type": "Away", "brand": "Adidas", "year": 2023},
        {"club": "Manchester United", "season": "2024/2025", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "Manchester United", "season": "2024/2025", "kit_type": "Third", "brand": "Adidas", "year": 2024},
        {"club": "Liverpool FC", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Liverpool FC", "season": "2023/2024", "kit_type": "Away", "brand": "Nike", "year": 2023},
        {"club": "AC Milan", "season": "2024/2025", "kit_type": "Home", "brand": "Puma", "year": 2024},
        {"club": "Inter Milan", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Juventus", "season": "2024/2025", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "Bayern Munich", "season": "2024/2025", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "Paris Saint-Germain", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Paris Saint-Germain", "season": "2024/2025", "kit_type": "Away", "brand": "Nike", "year": 2024},
        {"club": "Borussia Dortmund", "season": "2024/2025", "kit_type": "Home", "brand": "Puma", "year": 2024},
        {"club": "Chelsea FC", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Arsenal", "season": "2024/2025", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "Arsenal", "season": "2024/2025", "kit_type": "Away", "brand": "Adidas", "year": 2024},
        {"club": "Atletico Madrid", "season": "2024/2025", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Napoli", "season": "2024/2025", "kit_type": "Home", "brand": "EA7", "year": 2024},
        {"club": "Brazil National Team", "season": "2024", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Argentina National Team", "season": "2024", "kit_type": "Home", "brand": "Adidas", "year": 2024},
        {"club": "France National Team", "season": "2024", "kit_type": "Home", "brand": "Nike", "year": 2024},
        {"club": "Germany National Team", "season": "2024", "kit_type": "Home", "brand": "Adidas", "year": 2024},
    ]

    for i, kit_data in enumerate(seed_kits):
        kit_id = f"kit_{uuid.uuid4().hex[:12]}"
        doc = {
            **kit_data,
            "kit_id": kit_id,
            "front_photo": JERSEY_PHOTOS[i % len(JERSEY_PHOTOS)],
            "created_by": "system",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.master_kits.insert_one(doc)

        # Create 1-2 versions per kit
        models = ["Replica", "Authentic"]
        competitions = ["Domestic League", "Champions League 2024/2025", "Europa League 2024/2025", "Copa America 2024", "Euro 2024"]
        for j, m in enumerate(models[:((i % 2) + 1)]):
            ver_doc = {
                "version_id": f"ver_{uuid.uuid4().hex[:12]}",
                "kit_id": kit_id,
                "competition": competitions[i % len(competitions)],
                "model": m,
                "gender": "Men",
                "sku_code": f"SKU-{kit_data['brand'][:3].upper()}-{kit_data['year']}-{i:03d}{j}",
                "front_photo": JERSEY_PHOTOS[i % len(JERSEY_PHOTOS)],
                "back_photo": JERSEY_PHOTOS[(i + 1) % len(JERSEY_PHOTOS)],
                "created_by": "system",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.versions.insert_one(ver_doc)

    return {"message": "Seed data created", "count": len(seed_kits)}


# ─── Static File Serving ───

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Include the router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
