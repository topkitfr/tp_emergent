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

class JerseyValuation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_signature: str  # Unique identifier based on team+season+player+size+condition
    low_estimate: float
    median_estimate: float
    high_estimate: float
    total_listings: int
    total_sales: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    market_data: Dict[str, Any] = {}

class PriceHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_signature: str
    price: float
    transaction_type: str  # "listing", "sale", "collector_estimate"
    listing_id: Optional[str] = None
    transaction_date: datetime = Field(default_factory=datetime.utcnow)
    source: str = "marketplace"  # "marketplace", "collector_input", "external"

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

# Jersey valuation helpers
def generate_jersey_signature(team: str, season: str, player: Optional[str], size: str, condition: str) -> str:
    """Generate a unique signature for jersey valuation grouping"""
    player_part = f"_{player}" if player else ""
    return f"{team.lower().replace(' ', '_')}_{season}_{size.lower()}_{condition.lower()}{player_part}"

async def update_jersey_valuation(jersey: Jersey, price: float, transaction_type: str, listing_id: Optional[str] = None):
    """Update jersey valuation based on new price data"""
    try:
        signature = generate_jersey_signature(
            jersey.team, jersey.season, jersey.player, jersey.size, jersey.condition
        )
        
        # Add price to history
        price_history = PriceHistory(
            jersey_signature=signature,
            price=price,
            transaction_type=transaction_type,
            listing_id=listing_id
        )
        await db.price_history.insert_one(price_history.dict())
        
        # Recalculate valuation
        await recalculate_jersey_valuation(signature)
        
    except Exception as e:
        logger.error(f"Error updating jersey valuation: {e}")

async def recalculate_jersey_valuation(jersey_signature: str):
    """Recalculate valuation estimates for a jersey type"""
    try:
        # Get all price data for this jersey type
        price_data = await db.price_history.find({"jersey_signature": jersey_signature}).to_list(1000)
        
        if not price_data:
            return
        
        # Extract prices and categorize
        all_prices = [item["price"] for item in price_data]
        sales_prices = [item["price"] for item in price_data if item["transaction_type"] == "sale"]
        listing_prices = [item["price"] for item in price_data if item["transaction_type"] == "listing"]
        
        # Calculate estimates with weighted approach
        # Sales carry more weight than listings for accuracy
        if len(sales_prices) >= 3:
            # Use sales data if sufficient
            prices = sales_prices
            weight_factor = 1.0
        else:
            # Use combined data with weighting
            weighted_prices = []
            for item in price_data:
                if item["transaction_type"] == "sale":
                    # Sales count triple
                    weighted_prices.extend([item["price"]] * 3)
                elif item["transaction_type"] == "collector_estimate":
                    # Collector estimates count double
                    weighted_prices.extend([item["price"]] * 2)
                else:
                    # Listings count once
                    weighted_prices.append(item["price"])
            
            prices = weighted_prices
        
        if len(prices) < 2:
            return
        
        # Sort prices
        prices.sort()
        
        # Calculate percentiles
        def percentile(data, p):
            n = len(data)
            if n == 0:
                return 0
            if n == 1:
                return data[0]
            
            k = (n - 1) * p / 100
            f = int(k)
            c = k - f
            
            if f + 1 < n:
                return data[f] * (1 - c) + data[f + 1] * c
            else:
                return data[f]
        
        low_estimate = percentile(prices, 25)  # 25th percentile
        median_estimate = percentile(prices, 50)  # 50th percentile  
        high_estimate = percentile(prices, 75)  # 75th percentile
        
        # Market data analysis
        market_data = {
            "total_data_points": len(all_prices),
            "sales_count": len(sales_prices),
            "listings_count": len(listing_prices),
            "price_range": {
                "min": min(all_prices) if all_prices else 0,
                "max": max(all_prices) if all_prices else 0
            },
            "last_sale_price": sales_prices[-1] if sales_prices else None,
            "confidence_score": min(100, (len(sales_prices) * 30 + len(all_prices) * 10))
        }
        
        # Update or create valuation
        valuation = JerseyValuation(
            jersey_signature=jersey_signature,
            low_estimate=round(low_estimate, 2),
            median_estimate=round(median_estimate, 2),
            high_estimate=round(high_estimate, 2),
            total_listings=len(listing_prices),
            total_sales=len(sales_prices),
            market_data=market_data
        )
        
        # Upsert valuation
        await db.jersey_valuations.update_one(
            {"jersey_signature": jersey_signature},
            {"$set": valuation.dict()},
            upsert=True
        )
        
    except Exception as e:
        logger.error(f"Error recalculating jersey valuation: {e}")

async def get_jersey_valuation(jersey: Jersey) -> Optional[JerseyValuation]:
    """Get valuation for a specific jersey"""
    signature = generate_jersey_signature(
        jersey.team, jersey.season, jersey.player, jersey.size, jersey.condition
    )
    
    valuation_data = await db.jersey_valuations.find_one({"jersey_signature": signature})
    if valuation_data:
        # Remove MongoDB ObjectId to avoid serialization issues
        valuation_data.pop('_id', None)
        return JerseyValuation(**valuation_data)
    return None

async def get_user_collection_valuations(user_id: str):
    """Get valuations for all jerseys in user's collection"""
    try:
        # Get user's collections with jersey data
        pipeline = [
            {"$match": {"user_id": user_id}},
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
        
        valuations = []
        total_low = 0
        total_median = 0
        total_high = 0
        valued_items = 0
        
        for collection in collections:
            jersey_data = collection["jersey"]
            jersey = Jersey(**jersey_data)
            valuation = await get_jersey_valuation(jersey)
            
            collection_item = {
                "collection_id": collection["id"],
                "collection_type": collection["collection_type"],
                "jersey": jersey_data,
                "valuation": valuation.dict() if valuation else None,
                "added_at": collection["added_at"]
            }
            
            if valuation:
                total_low += valuation.low_estimate
                total_median += valuation.median_estimate
                total_high += valuation.high_estimate
                valued_items += 1
            
            valuations.append(collection_item)
        
        return {
            "collections": valuations,
            "portfolio_summary": {
                "total_items": len(valuations),
                "valued_items": valued_items,
                "total_low_estimate": round(total_low, 2),
                "total_median_estimate": round(total_median, 2),
                "total_high_estimate": round(total_high, 2),
                "average_value": round(total_median / valued_items, 2) if valued_items > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user collection valuations: {e}")
        return {
            "collections": [],
            "portfolio_summary": {
                "total_items": 0,
                "valued_items": 0, 
                "total_low_estimate": 0,
                "total_median_estimate": 0,
                "total_high_estimate": 0,
                "average_value": 0
            }
        }

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
    
    # Update jersey valuation with new listing price
    jersey_obj = Jersey(**jersey)
    await update_jersey_valuation(jersey_obj, listing_data.price, "listing", listing.id)
    
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
    
    # Get collection valuations
    collection_valuations = await get_user_collection_valuations(user_id)
    
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
        },
        "valuations": collection_valuations
    }

# Jersey valuation endpoints
@api_router.get("/jerseys/{jersey_id}/valuation")
async def get_jersey_valuation_endpoint(jersey_id: str):
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    jersey_obj = Jersey(**jersey)
    valuation = await get_jersey_valuation(jersey_obj)
    
    if not valuation:
        return {"message": "No valuation data available", "jersey_id": jersey_id}
    
    return {
        "jersey_id": jersey_id,
        "jersey": jersey,
        "valuation": valuation.dict()
    }

@api_router.get("/collections/valuations")
async def get_collection_valuations_endpoint(user_id: str = Depends(get_current_user)):
    return await get_user_collection_valuations(user_id)

@api_router.post("/jerseys/{jersey_id}/price-estimate")
async def add_collector_price_estimate(
    jersey_id: str, 
    price_estimate: Dict[str, float],
    user_id: str = Depends(get_current_user)
):
    """Allow collectors to contribute price estimates"""
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    estimated_price = price_estimate.get("price")
    if not estimated_price or estimated_price <= 0:
        raise HTTPException(status_code=400, detail="Valid price required")
    
    jersey_obj = Jersey(**jersey)
    await update_jersey_valuation(jersey_obj, estimated_price, "collector_estimate")
    
    return {"message": "Price estimate added successfully", "estimated_price": estimated_price}

@api_router.get("/market/trending")
async def get_trending_jerseys():
    """Get trending jerseys based on recent activity"""
    try:
        # Get recent price activity
        recent_activity = await db.price_history.find().sort("transaction_date", -1).limit(50).to_list(50)
        
        # Group by jersey signature
        signature_activity = {}
        for activity in recent_activity:
            signature = activity["jersey_signature"]
            if signature not in signature_activity:
                signature_activity[signature] = {
                    "recent_prices": [],
                    "activity_count": 0,
                    "last_activity": activity["transaction_date"]
                }
            signature_activity[signature]["recent_prices"].append(activity["price"])
            signature_activity[signature]["activity_count"] += 1
        
        # Get top trending
        trending = []
        for signature, data in signature_activity.items():
            if data["activity_count"] >= 2:  # Minimum activity threshold
                valuation = await db.jersey_valuations.find_one({"jersey_signature": signature})
                if valuation:
                    trending.append({
                        "jersey_signature": signature,
                        "valuation": valuation,
                        "activity_count": data["activity_count"],
                        "price_trend": "up" if len(data["recent_prices"]) >= 2 and data["recent_prices"][-1] > data["recent_prices"][0] else "stable"
                    })
        
        # Sort by activity
        trending.sort(key=lambda x: x["activity_count"], reverse=True)
        
        return {"trending_jerseys": trending[:10]}
        
    except Exception as e:
        logger.error(f"Error getting trending jerseys: {e}")
        return {"trending_jerseys": []}

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