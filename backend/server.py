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

class JerseyStatus(str, Enum):
    PENDING = "pending"      # En attente de validation
    APPROVED = "approved"    # Validé et visible
    REJECTED = "rejected"    # Rejeté

class UserRole(str, Enum):
    USER = "user"           # Utilisateur normal
    MODERATOR = "moderator" # Modérateur (peut valider les références)
    ADMIN = "admin"         # Admin principal (peut tout faire)

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
    profile_privacy: str = "public"  # "public" or "private"
    show_collection_value: bool = False  # Only owner can see collection values
    role: str = "user"  # Default role is user
    assigned_by: Optional[str] = None  # ID of admin who assigned the role
    role_assigned_at: Optional[datetime] = None

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
    reference_code: Optional[str] = None
    status: JerseyStatus = JerseyStatus.PENDING  # Default to pending for moderation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    submitted_by: str  # User who submitted this jersey
    approved_by: Optional[str] = None  # Admin who approved/rejected
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_id: str
    seller_id: str
    price: Optional[float] = None  # Price is optional - market determined like Discogs
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
    size: str  # Allow string input, validate in endpoint
    condition: str  # Allow string input, validate in endpoint  
    manufacturer: Optional[str] = ""
    home_away: Optional[str] = ""
    league: Optional[str] = ""
    description: Optional[str] = ""
    images: List[str] = []
    reference_code: Optional[str] = None

class ListingCreate(BaseModel):
    jersey_id: str
    price: Optional[float] = None  # Price is optional - market determined like Discogs
    description: str
    images: List[str] = []

class CollectionAdd(BaseModel):
    jersey_id: str
    collection_type: str

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    listing_id: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False

class MessageCreate(BaseModel):
    recipient_id: str
    listing_id: Optional[str] = None
    message: str

class UserActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action: str  # "jersey_submission", "jersey_approved", "jersey_rejected", "role_assigned", etc.
    target_id: Optional[str] = None  # ID of jersey/listing/etc involved
    details: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RoleAssignment(BaseModel):
    user_id: str
    role: str
    reason: Optional[str] = None

class UserStats(BaseModel):
    jerseys_submitted: int = 0
    jerseys_approved: int = 0
    jerseys_rejected: int = 0
    collections_added: int = 0
    listings_created: int = 0

class ProfileSettings(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None
    profile_privacy: Optional[str] = None
    show_collection_value: Optional[bool] = None

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
        
        # Remove MongoDB ObjectId from price data
        for item in price_data:
            item.pop('_id', None)
        
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
        import traceback
        logger.error(traceback.format_exc())

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
        
        # Remove MongoDB ObjectId fields
        for collection in collections:
            collection.pop('_id', None)
            if 'jersey' in collection:
                collection['jersey'].pop('_id', None)
        
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
        import traceback
        logger.error(traceback.format_exc())
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
    
    # Determine role - admin for main account
    user_role = "admin" if user_data.email == ADMIN_EMAIL else "user"
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        provider="custom",
        password_hash=hashed_password,
        role=user_role
    )
    
    await db.users.insert_one(user.dict())
    token = create_jwt_token(user.id)
    
    # Log registration activity
    await log_user_activity(user.id, "user_registered", None, {
        "provider": "custom",
        "role": user_role
    })
    
    return {"token": token, "user": {"id": user.id, "email": user.email, "name": user.name, "role": user_role}}

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email, "provider": "custom"})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Ensure admin account has admin role
    if user["email"] == ADMIN_EMAIL and user.get("role") != "admin":
        await db.users.update_one({"id": user["id"]}, {"$set": {"role": "admin"}})
        user["role"] = "admin"
    
    token = create_jwt_token(user["id"])
    return {"token": token, "user": {
        "id": user["id"], 
        "email": user["email"], 
        "name": user["name"],
        "role": user.get("role", "user")
    }}

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
        # Ensure admin account has admin role
        if existing_user["email"] == ADMIN_EMAIL and existing_user.get("role") != "admin":
            await db.users.update_one({"id": user_id}, {"$set": {"role": "admin"}})
    else:
        # Determine role - admin for main account
        user_role = "admin" if user_info["email"] == ADMIN_EMAIL else "user"
        
        # Create new user
        user = User(
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture"),
            provider="google",
            role=user_role
        )
        await db.users.insert_one(user.dict())
        user_id = user.id
        
        # Log registration activity
        await log_user_activity(user_id, "user_registered", None, {
            "provider": "google",
            "role": user_role
        })
    
    token = create_jwt_token(user_id)
    # Redirect to frontend with token
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    return f"<script>window.location.href = '{frontend_url}/auth/success?token={token}';</script>"

# Admin functions
ADMIN_EMAIL = "topkitfr@gmail.com"

async def get_current_admin(user_id: str = Depends(get_current_user)):
    """Check if the current user is an admin"""
    user = await db.users.find_one({"id": user_id})
    if not user or user["email"] != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id

async def get_current_moderator_or_admin(user_id: str = Depends(get_current_user)):
    """Check if the current user is a moderator or admin"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=403, detail="Authentication required")
    
    # Admin can always access
    if user["email"] == ADMIN_EMAIL:
        return user_id
    
    # Check if user has moderator role
    user_role = user.get("role", "user")
    if user_role not in ["moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Moderator or admin access required")
    
    return user_id

async def log_user_activity(user_id: str, action: str, target_id: str = None, details: Dict[str, Any] = None):
    """Log user activity for admin tracking"""
    if details is None:
        details = {}
    
    activity = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "target_id": target_id,
        "details": details,
        "created_at": datetime.utcnow()
    }
    
    await db.user_activities.insert_one(activity)

# Admin endpoints
@api_router.get("/admin/jerseys/pending")
async def get_pending_jerseys(moderator_id: str = Depends(get_current_moderator_or_admin)):
    """Get all jerseys pending approval"""
    jerseys = await db.jerseys.find({"status": "pending"}).to_list(100)
    
    # Remove MongoDB ObjectId for JSON serialization
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

@api_router.post("/admin/jerseys/{jersey_id}/approve")
async def approve_jersey(jersey_id: str, moderator_id: str = Depends(get_current_moderator_or_admin)):
    """Approve a pending jersey"""
    result = await db.jerseys.update_one(
        {"id": jersey_id, "status": "pending"},
        {
            "$set": {
                "status": "approved",
                "approved_by": moderator_id,
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Jersey not found or already processed")
    
    # Log activity
    await log_user_activity(moderator_id, "jersey_approved", jersey_id)
    
    # Get jersey info for activity logging
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if jersey:
        await log_user_activity(jersey["created_by"], "jersey_approved", jersey_id, {
            "approved_by": moderator_id,
            "jersey_name": f"{jersey.get('team', '')} {jersey.get('season', '')}"
        })
    
    return {"message": "Jersey approved successfully"}

@api_router.post("/admin/jerseys/{jersey_id}/reject")
async def reject_jersey(
    jersey_id: str, 
    rejection_data: dict,
    moderator_id: str = Depends(get_current_moderator_or_admin)
):
    """Reject a pending jersey"""
    reason = rejection_data.get("reason", "No reason provided")
    
    result = await db.jerseys.update_one(
        {"id": jersey_id, "status": "pending"},
        {
            "$set": {
                "status": "rejected",
                "approved_by": moderator_id,
                "approved_at": datetime.utcnow(),
                "rejection_reason": reason
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Jersey not found or already processed")
    
    # Log activity
    await log_user_activity(moderator_id, "jersey_rejected", jersey_id, {"reason": reason})
    
    # Get jersey info for activity logging
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if jersey:
        await log_user_activity(jersey["created_by"], "jersey_rejected", jersey_id, {
            "rejected_by": moderator_id,
            "jersey_name": f"{jersey.get('team', '')} {jersey.get('season', '')}",
            "reason": reason
        })
    
    return {"message": "Jersey rejected successfully"}

# User management endpoints (Admin only)
@api_router.get("/admin/users")
async def get_all_users(admin_id: str = Depends(get_current_admin)):
    """Get all users with their stats and activities"""
    users = await db.users.find({}).to_list(1000)
    
    user_list = []
    for user in users:
        user.pop('_id', None)
        user.pop('password_hash', None)  # Don't expose password hash
        
        # Get user statistics
        user_stats = {
            "jerseys_submitted": await db.jerseys.count_documents({"created_by": user["id"]}),
            "jerseys_approved": await db.jerseys.count_documents({"created_by": user["id"], "status": "approved"}),
            "jerseys_rejected": await db.jerseys.count_documents({"created_by": user["id"], "status": "rejected"}),
            "collections_added": await db.collections.count_documents({"user_id": user["id"]}),
            "listings_created": await db.listings.count_documents({"seller_id": user["id"]})
        }
        
        # Get recent activities
        recent_activities = await db.user_activities.find(
            {"user_id": user["id"]}
        ).sort("created_at", -1).limit(5).to_list(5)
        
        for activity in recent_activities:
            activity.pop('_id', None)
        
        user_data = {
            **user,
            "stats": user_stats,
            "recent_activities": recent_activities
        }
        
        user_list.append(user_data)
    
    return {"users": user_list, "total": len(user_list)}

@api_router.post("/admin/users/{user_id}/assign-role")
async def assign_user_role(
    user_id: str, 
    role_data: RoleAssignment,
    admin_id: str = Depends(get_current_admin)
):
    """Assign a role to a user (Admin only)"""
    
    # Validate role
    if role_data.role not in ["user", "moderator"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'moderator'")
    
    # Cannot change admin role
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["email"] == ADMIN_EMAIL:
        raise HTTPException(status_code=400, detail="Cannot modify admin user role")
    
    # Update user role
    result = await db.users.update_one(
        {"id": user_id},
        {
            "$set": {
                "role": role_data.role,
                "assigned_by": admin_id,
                "role_assigned_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log activity
    await log_user_activity(admin_id, "role_assigned", user_id, {
        "new_role": role_data.role,
        "reason": role_data.reason,
        "user_email": user["email"]
    })
    
    await log_user_activity(user_id, "role_received", None, {
        "new_role": role_data.role,
        "assigned_by": admin_id,
        "reason": role_data.reason
    })
    
    return {"message": f"Role '{role_data.role}' assigned to user successfully"}

@api_router.get("/admin/activities")
async def get_all_activities(admin_id: str = Depends(get_current_admin), limit: int = 50):
    """Get recent system activities"""
    activities = await db.user_activities.find({}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Enrich activities with user info
    for activity in activities:
        activity.pop('_id', None)
        
        # Get user info
        user = await db.users.find_one({"id": activity["user_id"]}, {"name": 1, "email": 1})
        if user:
            activity["user_name"] = user.get("name", "Unknown")
            activity["user_email"] = user.get("email", "Unknown")
    
    return {"activities": activities, "total": len(activities)}


# Jersey endpoints
@api_router.post("/jerseys", response_model=Jersey)
async def create_jersey(jersey_data: JerseyCreate, user_id: str = Depends(get_current_user)):
    """Create a new jersey submission (pending approval)"""
    try:
        print(f"🟡 Jersey submission received from user {user_id}")
        print(f"🟡 Jersey data: {jersey_data.dict()}")
        
        # Validate required fields
        if not jersey_data.team or not jersey_data.season:
            raise HTTPException(status_code=422, detail="Team and season are required")
        
        if not jersey_data.size or not jersey_data.condition:
            raise HTTPException(status_code=422, detail="Size and condition are required")
        
        # Validate enums
        try:
            size_enum = JerseySize(jersey_data.size.upper() if jersey_data.size else "")
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid size: {jersey_data.size}. Must be one of: XS, S, M, L, XL, XXL")
        
        try:
            condition_enum = JerseyCondition(jersey_data.condition.lower() if jersey_data.condition else "")
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid condition: {jersey_data.condition}. Must be one of: new, near_mint, very_good, good, poor")
        
        # Create jersey with validated data
        jersey = Jersey(
            team=jersey_data.team.strip(),
            season=jersey_data.season.strip(),
            player=jersey_data.player.strip() if jersey_data.player else None,
            size=size_enum,
            condition=condition_enum,
            manufacturer=jersey_data.manufacturer.strip() if jersey_data.manufacturer else "",
            home_away=jersey_data.home_away.strip() if jersey_data.home_away else "",
            league=jersey_data.league.strip() if jersey_data.league else "",
            description=jersey_data.description.strip() if jersey_data.description else "",
            images=jersey_data.images or [],
            reference_code=jersey_data.reference_code.strip() if jersey_data.reference_code else None,
            created_by=user_id,
            submitted_by=user_id
        )
        
        # Insert into database
        await db.jerseys.insert_one(jersey.dict())
        print(f"✅ Jersey created successfully with ID: {jersey.id}")
        
        # Log user activity
        await log_user_activity(user_id, "jersey_submission", jersey.id, {
            "jersey_name": f"{jersey.team} {jersey.season}",
            "player": jersey.player,
            "status": jersey.status
        })
        
        return jersey
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Jersey creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create jersey: {str(e)}")

@api_router.get("/jerseys")
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
    # Only show approved jerseys (Discogs-like system)
    query["$and"] = [{"status": "approved"}]
    
    filter_conditions = []
    if team:
        filter_conditions.append({"team": {"$regex": team, "$options": "i"}})
    if season:
        filter_conditions.append({"season": season})
    if player:
        filter_conditions.append({"player": {"$regex": player, "$options": "i"}})
    if size:
        filter_conditions.append({"size": size})
    if condition:
        filter_conditions.append({"condition": condition})
    if league:
        filter_conditions.append({"league": {"$regex": league, "$options": "i"}})
    
    if filter_conditions:
        query["$and"].extend(filter_conditions)
    
    # Use aggregation to include creator information
    pipeline = [
        {"$match": query},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "created_by",
                "foreignField": "id", 
                "as": "creator"
            }
        },
        {
            "$addFields": {
                "creator_info": {
                    "$cond": {
                        "if": {"$eq": [{"$size": "$creator"}, 0]},
                        "then": {"name": "Unknown User", "id": None},
                        "else": {
                            "name": {"$arrayElemAt": ["$creator.name", 0]},
                            "id": {"$arrayElemAt": ["$creator.id", 0]},
                            "picture": {"$arrayElemAt": ["$creator.picture", 0]}
                        }
                    }
                }
            }
        },
        {"$unset": "creator"}
    ]
    
    jerseys = await db.jerseys.aggregate(pipeline).to_list(limit)
    
    # Remove MongoDB ObjectId fields to avoid serialization issues
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

@api_router.get("/jerseys/{jersey_id}", response_model=Jersey)
async def get_jersey(jersey_id: str):
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    return Jersey(**jersey)

@api_router.put("/jerseys/{jersey_id}", response_model=Jersey)
async def update_jersey(jersey_id: str, jersey_data: JerseyCreate, user_id: str = Depends(get_current_user)):
    # Check if jersey exists and user owns it
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    # Check if the user created this jersey
    if jersey.get("created_by") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this jersey")
    
    # Update the jersey
    update_data = jersey_data.dict(exclude_unset=True)
    await db.jerseys.update_one(
        {"id": jersey_id}, 
        {"$set": update_data}
    )
    
    # Return the updated jersey
    updated_jersey = await db.jerseys.find_one({"id": jersey_id})
    return Jersey(**updated_jersey)

# Marketplace endpoints
@api_router.post("/listings", response_model=Listing)
async def create_listing(listing_data: ListingCreate, user_id: str = Depends(get_current_user)):
    # Verify jersey exists
    jersey = await db.jerseys.find_one({"id": listing_data.jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    listing = Listing(**listing_data.dict(), seller_id=user_id)
    await db.listings.insert_one(listing.dict())
    
    # Update jersey valuation with new listing price (if price is provided)
    if listing_data.price:
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

@api_router.delete("/collections/{jersey_id}")
async def remove_from_collection(jersey_id: str, user_id: str = Depends(get_current_user)):
    result = await db.collections.delete_one({
        "user_id": user_id,
        "jersey_id": jersey_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Jersey not found in collection")
    
    return {"message": "Removed from collection"}

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
    
    # Get collection valuations (always show to owner)
    collection_valuations = await get_user_collection_valuations(user_id)
    
    return {
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "picture": user.get("picture"),
            "provider": user["provider"],
            "created_at": user["created_at"],
            "profile_privacy": user.get("profile_privacy", "public"),
            "show_collection_value": user.get("show_collection_value", False)
        },
        "stats": {
            "owned_jerseys": owned_count,
            "wanted_jerseys": wanted_count,
            "active_listings": listings_count
        },
        "valuations": collection_valuations
    }

@api_router.put("/profile/settings")
async def update_profile_settings(settings: ProfileSettings, user_id: str = Depends(get_current_user)):
    # Build update dictionary only with provided fields
    update_data = {}
    
    if settings.name is not None:
        update_data["name"] = settings.name
    
    if settings.picture is not None:
        update_data["picture"] = settings.picture
    
    if settings.profile_privacy is not None:
        update_data["profile_privacy"] = settings.profile_privacy
    
    if settings.show_collection_value is not None:
        update_data["show_collection_value"] = settings.show_collection_value
    
    if update_data:
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Profile settings updated successfully"}

# Jersey valuation endpoints
@api_router.get("/jerseys/{jersey_id}/valuation")
async def get_jersey_valuation_endpoint(jersey_id: str):
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    # Remove MongoDB ObjectId
    jersey.pop('_id', None)
    
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

@api_router.get("/collections/pending")
async def get_user_pending_submissions(user_id: str = Depends(get_current_user)):
    """Get user's pending jersey submissions"""
    submissions = await db.jerseys.find({
        "submitted_by": user_id,
        "status": {"$in": ["pending", "rejected"]}
    }).to_list(100)
    
    # Remove MongoDB ObjectId for JSON serialization
    for submission in submissions:
        submission.pop('_id', None)
    
    return submissions

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
    
    return {"message": f"Price estimate of ${estimated_price} added for jersey {jersey_id}"}


@api_router.get("/users/{user_id}/profile")
async def get_user_public_profile(user_id: str):
    """Get public profile information for a user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile is private
    if user.get("profile_privacy") == "private":
        return {
            "id": user["id"],
            "name": user["name"],
            "picture": user.get("picture"),
            "profile_privacy": "private",
            "message": "This user's profile is private"
        }
    
    # Get user's collection stats
    owned_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "owned"})
    wanted_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "wanted"})
    listings_count = await db.listings.count_documents({"seller_id": user_id, "status": "active"})
    jerseys_created_count = await db.jerseys.count_documents({"created_by": user_id})
    
    return {
        "id": user["id"],
        "name": user["name"],
        "picture": user.get("picture"),
        "provider": user.get("provider", "custom"),
        "created_at": user.get("created_at"),
        "profile_privacy": user.get("profile_privacy", "public"),
        "stats": {
            "owned_jerseys": owned_count,
            "wanted_jerseys": wanted_count,
            "active_listings": listings_count,
            "jerseys_created": jerseys_created_count
        }
    }


@api_router.get("/users/{user_id}/jerseys")
async def get_user_created_jerseys(user_id: str, skip: int = 0, limit: int = 20):
    """Get jerseys created by a specific user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile is private
    if user.get("profile_privacy") == "private":
        raise HTTPException(status_code=403, detail="This user's jerseys are private")
    
    pipeline = [
        {"$match": {"created_by": user_id}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$addFields": {
                "creator_info": {
                    "name": user["name"],
                    "id": user["id"],
                    "picture": user.get("picture")
                }
            }
        }
    ]
    
    jerseys = await db.jerseys.aggregate(pipeline).to_list(limit)
    
    # Remove MongoDB ObjectId fields to avoid serialization issues
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys


@api_router.get("/market/trending")
async def get_trending_jerseys():
    """Get trending jerseys based on recent activity"""
    try:
        # Get recent price activity
        recent_activity = await db.price_history.find().sort("transaction_date", -1).limit(50).to_list(50)
        
        # Remove MongoDB ObjectId from activity data
        for activity in recent_activity:
            activity.pop('_id', None)
        
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
                    # Remove MongoDB ObjectId
                    valuation.pop('_id', None)
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
        import traceback
        logger.error(traceback.format_exc())
        return {"trending_jerseys": []}

# Database management endpoints
@api_router.delete("/admin/database/erase")
async def erase_database(current_user: dict = Depends(get_current_user)):
    """
    Erase the entire database - USE WITH CAUTION!
    This will delete all users, jerseys, listings, and collections.
    """
    try:
        # Delete all collections
        await db.users.delete_many({})
        await db.jerseys.delete_many({})
        await db.listings.delete_many({})
        await db.collections.delete_many({})
        await db.price_history.delete_many({})
        await db.jersey_valuations.delete_many({})
        await db.messages.delete_many({})
        
        return {"message": "Database successfully erased", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to erase database: {str(e)}")

@api_router.delete("/admin/database/clear-listings")
async def clear_deleted_listings():
    """
    Remove all listings marked as deleted from Browse and Marketplace
    """
    try:
        # Delete all listings that are marked as deleted or inactive
        result = await db.listings.delete_many({"deleted": True})
        result2 = await db.listings.delete_many({"status": "deleted"})
        
        deleted_count = result.deleted_count + result2.deleted_count
        return {"message": f"Removed {deleted_count} deleted listings", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear deleted listings: {str(e)}")

# Messaging endpoints
@api_router.post("/messages")
async def send_message(message_data: MessageCreate, user_id: str = Depends(get_current_user)):
    message = Message(**message_data.dict(), sender_id=user_id)
    await db.messages.insert_one(message.dict())
    return {"message": "Message sent successfully"}

@api_router.get("/messages")
async def get_messages(user_id: str = Depends(get_current_user)):
    messages = await db.messages.find({
        "$or": [
            {"sender_id": user_id},
            {"recipient_id": user_id}
        ]
    }).sort("created_at", -1).to_list(100)
    return messages

# Public user endpoints
@api_router.get("/users/{user_id}/public")
async def get_public_user_info(user_id: str, current_user_id: Optional[str] = None):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile is private
    if user.get("profile_privacy", "public") == "private" and current_user_id != user_id:
        return {
            "id": user["id"],
            "name": user["name"],
            "picture": user.get("picture"),
            "created_at": user["created_at"],
            "profile_private": True
        }
    
    # Get public stats if profile is public
    owned_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "owned"})
    wanted_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "wanted"})
    listings_count = await db.listings.count_documents({"seller_id": user_id})
    
    response = {
        "id": user["id"],
        "name": user["name"],
        "picture": user.get("picture"),
        "created_at": user["created_at"],
        "profile_private": False,
        "stats": {
            "owned_jerseys": owned_count,
            "wanted_jerseys": wanted_count,
            "active_listings": listings_count
        }
    }
    
    # Only show collection if profile privacy allows and user opted to show collections
    if user.get("profile_privacy", "public") == "public":
        # Get collection without valuations (valuations are private)
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
        
        collections = await db.collections.aggregate(pipeline).to_list(100)
        response["public_collection"] = collections
    
    return response

@api_router.get("/users/{user_id}/collections")
async def get_user_public_collections(user_id: str, current_user_id: str = Depends(get_current_user)):
    """Get user's public collections (no valuations shown to others)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile is private
    if user.get("profile_privacy", "public") == "private" and current_user_id != user_id:
        raise HTTPException(status_code=403, detail="This user's profile is private")
    
    # Get collection without valuations
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
    
    # Remove valuation data for privacy
    for collection in collections:
        collection.pop('valuation', None)
    
    return {
        "user_id": user_id,
        "profile_owner": current_user_id == user_id,
        "collections": collections
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