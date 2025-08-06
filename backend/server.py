from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from authlib.integrations.starlette_client import OAuth
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import requests
import bcrypt
import jwt
from enum import Enum
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="TopKit - Soccer Jersey Marketplace")

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=os.environ.get('SECRET_KEY', 'topkit-secret-key-2024'))

# OAuth setup for Google
oauth = OAuth()
oauth.register(
    name='google',
    client_id="920523740769-d74f1dsdajtilkqasrhtrei4blmf8ujj.apps.googleusercontent.com",
    client_secret="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",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'topkit-secret-key-2024')

# Enums
class JerseyCondition(str, Enum):
    MINT = "mint"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"

class JerseySize(str, Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    INACTIVE = "inactive"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    picture: Optional[str] = None
    provider: str  # 'custom', 'google', 'emergent'
    password_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_token: Optional[str] = None
    session_expires: Optional[datetime] = None

class Jersey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team: str
    season: str
    player: Optional[str] = None
    size: JerseySize
    condition: JerseyCondition
    manufacturer: str
    home_away: str  # "home", "away", "third"
    league: str
    description: str
    images: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_id: str
    seller_id: str
    price: float
    status: ListingStatus = ListingStatus.ACTIVE
    description: str
    images: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Collection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    jersey_id: str
    collection_type: str  # "owned", "wanted"
    added_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    payment_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    amount: float
    currency: str = "usd"
    listing_id: str
    payment_status: str = "pending"
    status: str = "initiated"
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class JerseyCreate(BaseModel):
    team: str
    season: str
    player: Optional[str] = None
    size: JerseySize
    condition: JerseyCondition
    manufacturer: str
    home_away: str
    league: str
    description: str
    images: List[str] = []

class ListingCreate(BaseModel):
    jersey_id: str
    price: float
    description: str
    images: List[str] = []

class CollectionAdd(BaseModel):
    jersey_id: str
    collection_type: str

class CheckoutRequest(BaseModel):
    listing_id: str
    origin_url: str

# Authentication helpers
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    token = credentials.credentials
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user_id

# Authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        provider="custom",
        password_hash=hashed_password
    )
    
    await db.users.insert_one(user.dict())
    token = create_jwt_token(user.id)
    
    return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.name}}

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email, "provider": "custom"})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_jwt_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "name": user["name"]}}

@api_router.get("/auth/google")
async def google_auth(request: Request):
    redirect_uri = f"{request.base_url}api/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@api_router.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_info["email"]})
    
    if existing_user:
        user_id = existing_user["id"]
    else:
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture"),
            provider="google"
        )
        await db.users.insert_one(user.dict())
        user_id = user.id
    
    token = create_jwt_token(user_id)
    # Redirect to frontend with token
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    return f"<script>window.location.href = '{frontend_url}/auth/success?token={token}';</script>"

@api_router.get("/auth/emergent/redirect")
async def emergent_auth_redirect():
    preview_url = "https://ce446aa3-3dc9-46b4-8a26-16c4f295a473.preview.emergentagent.com"
    auth_url = f"https://auth.emergentagent.com/?redirect={preview_url}/profile"
    return {"auth_url": auth_url}

@api_router.post("/auth/emergent/session")
async def emergent_session(request: Request):
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Call Emergent auth API
    headers = {"X-Session-ID": session_id}
    response = requests.get(
        "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
        headers=headers
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    user_data = response.json()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data["email"]})
    
    if existing_user:
        user_id = existing_user["id"]
        # Update session token
        session_token = user_data["session_token"]
        session_expires = datetime.utcnow() + timedelta(days=7)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"session_token": session_token, "session_expires": session_expires}}
        )
    else:
        # Create new user
        user = User(
            email=user_data["email"],
            name=user_data.get("name", ""),
            picture=user_data.get("picture"),
            provider="emergent",
            session_token=user_data["session_token"],
            session_expires=datetime.utcnow() + timedelta(days=7)
        )
        await db.users.insert_one(user.dict())
        user_id = user.id
    
    token = create_jwt_token(user_id)
    return {"token": token, "user": {"id": user_id, "email": user_data["email"], "name": user_data.get("name", "")}}

# Jersey endpoints
@api_router.post("/jerseys", response_model=Jersey)
async def create_jersey(jersey_data: JerseyCreate, user_id: str = Depends(get_current_user)):
    jersey = Jersey(**jersey_data.dict(), created_by=user_id)
    await db.jerseys.insert_one(jersey.dict())
    return jersey

@api_router.get("/jerseys", response_model=List[Jersey])
async def get_jerseys(
    team: Optional[str] = None,
    season: Optional[str] = None,
    player: Optional[str] = None,
    size: Optional[JerseySize] = None,
    condition: Optional[JerseyCondition] = None,
    league: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    query = {}
    if team:
        query["team"] = {"$regex": team, "$options": "i"}
    if season:
        query["season"] = season
    if player:
        query["player"] = {"$regex": player, "$options": "i"}
    if size:
        query["size"] = size
    if condition:
        query["condition"] = condition
    if league:
        query["league"] = {"$regex": league, "$options": "i"}
    
    jerseys = await db.jerseys.find(query).skip(skip).limit(limit).to_list(limit)
    return [Jersey(**jersey) for jersey in jerseys]

@api_router.get("/jerseys/{jersey_id}", response_model=Jersey)
async def get_jersey(jersey_id: str):
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    return Jersey(**jersey)

# Marketplace endpoints
@api_router.post("/listings", response_model=Listing)
async def create_listing(listing_data: ListingCreate, user_id: str = Depends(get_current_user)):
    # Verify jersey exists
    jersey = await db.jerseys.find_one({"id": listing_data.jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    listing = Listing(**listing_data.dict(), seller_id=user_id)
    await db.listings.insert_one(listing.dict())
    return listing

@api_router.get("/listings", response_model=List[Dict])
async def get_listings(
    team: Optional[str] = None,
    season: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    condition: Optional[JerseyCondition] = None,
    size: Optional[JerseySize] = None,
    skip: int = 0,
    limit: int = 20
):
    # Build aggregation pipeline
    pipeline = [
        {"$match": {"status": "active"}},
        {
            "$lookup": {
                "from": "jerseys",
                "localField": "jersey_id",
                "foreignField": "id",
                "as": "jersey"
            }
        },
        {"$unwind": "$jersey"}
    ]
    
    # Add filters
    match_conditions = []
    if team:
        match_conditions.append({"jersey.team": {"$regex": team, "$options": "i"}})
    if season:
        match_conditions.append({"jersey.season": season})
    if condition:
        match_conditions.append({"jersey.condition": condition})
    if size:
        match_conditions.append({"jersey.size": size})
    if min_price is not None:
        match_conditions.append({"price": {"$gte": min_price}})
    if max_price is not None:
        match_conditions.append({"price": {"$lte": max_price}})
    
    if match_conditions:
        pipeline.append({"$match": {"$and": match_conditions}})
    
    pipeline.extend([
        {"$skip": skip},
        {"$limit": limit}
    ])
    
    listings = await db.listings.aggregate(pipeline).to_list(limit)
    # Remove MongoDB ObjectId fields to avoid serialization issues
    for listing in listings:
        listing.pop('_id', None)
        if 'jersey' in listing:
            listing['jersey'].pop('_id', None)
    return listings

@api_router.get("/listings/{listing_id}")
async def get_listing(listing_id: str):
    pipeline = [
        {"$match": {"id": listing_id}},
        {
            "$lookup": {
                "from": "jerseys",
                "localField": "jersey_id",
                "foreignField": "id",
                "as": "jersey"
            }
        },
        {"$unwind": "$jersey"},
        {
            "$lookup": {
                "from": "users",
                "localField": "seller_id",
                "foreignField": "id",
                "as": "seller"
            }
        },
        {"$unwind": "$seller"}
    ]
    
    result = await db.listings.aggregate(pipeline).to_list(1)
    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # Remove MongoDB ObjectId fields to avoid serialization issues
    listing = result[0]
    listing.pop('_id', None)
    if 'jersey' in listing:
        listing['jersey'].pop('_id', None)
    if 'seller' in listing:
        listing['seller'].pop('_id', None)
    
    return listing

# Collection endpoints
@api_router.post("/collections")
async def add_to_collection(collection_data: CollectionAdd, user_id: str = Depends(get_current_user)):
    # Check if already in collection
    existing = await db.collections.find_one({
        "user_id": user_id,
        "jersey_id": collection_data.jersey_id,
        "collection_type": collection_data.collection_type
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already in collection")
    
    collection = Collection(**collection_data.dict(), user_id=user_id)
    await db.collections.insert_one(collection.dict())
    return {"message": "Added to collection"}

@api_router.get("/collections/{collection_type}")
async def get_user_collection(collection_type: str, user_id: str = Depends(get_current_user)):
    pipeline = [
        {"$match": {"user_id": user_id, "collection_type": collection_type}},
        {
            "$lookup": {
                "from": "jerseys",
                "localField": "jersey_id",
                "foreignField": "id",
                "as": "jersey"
            }
        },
        {"$unwind": "$jersey"}
    ]
    
    collections = await db.collections.aggregate(pipeline).to_list(1000)
    # Remove MongoDB ObjectId fields to avoid serialization issues
    for collection in collections:
        collection.pop('_id', None)
        if 'jersey' in collection:
            collection['jersey'].pop('_id', None)
    return collections

# Payment endpoints (Stripe integration will be added)
@api_router.post("/payments/checkout")
async def create_checkout(request_data: CheckoutRequest, user_id: str = Depends(get_current_user)):
    # Get listing
    listing = await db.listings.find_one({"id": request_data.listing_id, "status": "active"})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # For now, return a mock checkout session
    # TODO: Integrate with Stripe
    session_id = str(uuid.uuid4())
    
    # Create payment transaction record
    transaction = PaymentTransaction(
        session_id=session_id,
        user_id=user_id,
        amount=listing["price"],
        listing_id=request_data.listing_id,
        metadata={"listing_id": request_data.listing_id, "seller_id": listing["seller_id"]}
    )
    
    await db.payment_transactions.insert_one(transaction.dict())
    
    return {
        "checkout_url": f"{request_data.origin_url}/checkout/{session_id}",
        "session_id": session_id
    }

# User profile endpoint
@api_router.get("/profile")
async def get_profile(user_id: str = Depends(get_current_user)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user stats
    owned_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "owned"})
    wanted_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "wanted"})
    listings_count = await db.listings.count_documents({"seller_id": user_id})
    
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture"),
            "provider": user["provider"],
            "created_at": user["created_at"]
        },
        "stats": {
            "owned_jerseys": owned_count,
            "wanted_jerseys": wanted_count,
            "active_listings": listings_count
        }
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()