"""
New Simplified TopKit Server - 2-Type System
1. Master Kit = Official jersey reference
2. My Collection = Master Kits with personal details

Phase 1: Core structure with basic endpoints
"""
import os
import logging
import mimetypes
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid
import asyncio

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path

# Force load .env file from the backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ValidationError
import aiohttp
import json
import aiofiles
import shutil
from PIL import Image

# Import new simplified models
from collaborative_models import (
    # New Simplified Kit System (2-Type System)
    MasterKit, MyCollection, KitType, KitModel, Gender, KitCondition, PhysicalState,
    CollectionType,
    MasterKitCreate, MyCollectionCreate, MyCollectionUpdate,
    MasterKitResponse, MyCollectionResponse,
    # Existing entities (unchanged)
    Team, Brand, Player, Competition, ContributionStatus, VerificationLevel, EntityType,
    ContributionSummary, ContributionStatusV2,
    User, UserResponse, UserLevel, UserGamificationResponse, ContributionEntry, XPTransaction
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="TopKit API - Simplified 2-Type System", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Database
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
# Use DB_NAME from environment variable
DB_NAME = os.environ.get('DB_NAME', 'topkit')
db = client[DB_NAME]

# Add startup verification
async def verify_database_connection():
    """Verify database connection and log details"""
    try:
        # Test database connection
        result = await db.command("ping")
        logger.info(f"✅ Database ping successful: {result}")
        
        # Log database name being used
        logger.info(f"🔍 DATABASE CONFIGURATION:")
        logger.info(f"  MONGO_URL: {MONGO_URL}")
        logger.info(f"  DB_NAME: {os.environ.get('DB_NAME', 'NOT_SET')}")
        logger.info(f"  Database connection: {db.name}")
        
        # List collections to verify we're connected to the right database
        collections = await db.list_collection_names()
        logger.info(f"📋 Collections in '{db.name}' database: {collections}")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")

# Call verification on startup
import asyncio
asyncio.create_task(verify_database_connection())

# ================================
# GAMIFICATION SYSTEM UTILITIES
# ================================

# XP Rules Configuration
XP_RULES = {
    'team': 10,
    'brand': 10,
    'player': 10,
    'competition': 10,
    'jersey': 20  # Master kit creation
}

# Level thresholds and emojis
LEVEL_THRESHOLDS = {
    UserLevel.REMPLACANT: {'min_xp': 0, 'max_xp': 99, 'emoji': '👕'},
    UserLevel.TITULAIRE: {'min_xp': 100, 'max_xp': 499, 'emoji': '⚽'},
    UserLevel.LEGENDE: {'min_xp': 500, 'max_xp': 1999, 'emoji': '🏆'},
    UserLevel.BALLON_DOR: {'min_xp': 2000, 'max_xp': float('inf'), 'emoji': '🔥'}
}

# Daily XP limit for anti-farming
DAILY_XP_LIMIT = 100

async def calculate_user_level(xp: int) -> UserLevel:
    """Calculate user level based on XP"""
    for level, thresholds in LEVEL_THRESHOLDS.items():
        if thresholds['min_xp'] <= xp <= thresholds['max_xp']:
            return level
    return UserLevel.BALLON_DOR  # Default to highest level if XP exceeds all thresholds

def get_level_emoji(level: UserLevel) -> str:
    """Get emoji for level"""
    return LEVEL_THRESHOLDS[level]['emoji']

def get_xp_to_next_level(current_xp: int, current_level: UserLevel) -> tuple[int, Optional[UserLevel]]:
    """Calculate XP needed for next level and what that level would be"""
    levels_list = list(LEVEL_THRESHOLDS.keys())
    current_index = levels_list.index(current_level)
    
    # If already at max level
    if current_index == len(levels_list) - 1:
        return 0, None
    
    next_level = levels_list[current_index + 1]
    next_level_min_xp = LEVEL_THRESHOLDS[next_level]['min_xp']
    xp_needed = next_level_min_xp - current_xp
    
    return max(0, xp_needed), next_level

def calculate_progress_percentage(current_xp: int, current_level: UserLevel) -> int:
    """Calculate progress percentage within current level"""
    level_min_xp = LEVEL_THRESHOLDS[current_level]['min_xp']
    level_max_xp = LEVEL_THRESHOLDS[current_level]['max_xp']
    
    # Handle infinite max (Ballon d'Or level)
    if level_max_xp == float('inf'):
        return 100
    
    level_range = level_max_xp - level_min_xp + 1  # +1 because ranges are inclusive
    progress_in_level = current_xp - level_min_xp
    
    return min(100, int((progress_in_level / level_range) * 100))

async def check_daily_xp_limit(user_id: str, xp_to_add: int) -> bool:
    """Check if user can receive XP without exceeding daily limit"""
    today = datetime.now(timezone.utc).date()
    
    # Get user's current daily XP
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    user_daily_date = user.get('xp_daily_date')
    user_daily_total = user.get('xp_daily_total', 0)
    
    # Reset daily total if it's a new day
    if not user_daily_date or user_daily_date.date() != today:
        user_daily_total = 0
    
    # Check if adding XP would exceed daily limit
    return (user_daily_total + xp_to_add) <= DAILY_XP_LIMIT

async def award_xp(user_id: str, contribution_id: str, item_type: str, item_id: str, approved_by: str) -> dict:
    """Award XP to user for approved contribution"""
    try:
        # Check if contribution exists and hasn't been rewarded
        contribution = await db.contributions_gamification.find_one({
            "id": contribution_id,
            "user_id": user_id,
            "is_approved": False
        })
        
        if not contribution:
            return {"success": False, "message": "Contribution not found or already rewarded"}
        
        # Get XP amount for item type
        xp_amount = XP_RULES.get(item_type, 0)
        if xp_amount == 0:
            return {"success": False, "message": f"No XP rule for item type: {item_type}"}
        
        # Check daily XP limit
        if not await check_daily_xp_limit(user_id, xp_amount):
            return {"success": False, "message": "Daily XP limit would be exceeded"}
        
        # Get user current data
        user = await db.users.find_one({"id": user_id})
        if not user:
            return {"success": False, "message": "User not found"}
        
        current_xp = user.get('xp', 0)
        current_level = UserLevel(user.get('level', UserLevel.REMPLACANT))
        daily_total = user.get('xp_daily_total', 0)
        daily_date = user.get('xp_daily_date')
        
        # Reset daily total if new day
        today = datetime.now(timezone.utc)
        if not daily_date or daily_date.date() != today.date():
            daily_total = 0
        
        # Calculate new totals
        new_xp = current_xp + xp_amount
        new_daily_total = daily_total + xp_amount
        new_level = await calculate_user_level(new_xp)
        level_changed = new_level != current_level
        
        # Update user XP and level
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "xp": new_xp,
                "level": new_level,
                "xp_daily_total": new_daily_total,
                "xp_daily_date": today
            }}
        )
        
        # Mark contribution as approved and rewarded
        await db.contributions_gamification.update_one(
            {"id": contribution_id},
            {"$set": {
                "is_approved": True,
                "xp_awarded": xp_amount,
                "approved_at": today,
                "approved_by": approved_by
            }}
        )
        
        # Create XP transaction record for audit
        xp_transaction = XPTransaction(
            user_id=user_id,
            contribution_id=contribution_id,
            xp_amount=xp_amount,
            item_type=item_type,
            item_id=item_id,
            created_by=approved_by
        )
        await db.xp_transactions.insert_one(xp_transaction.dict())
        
        return {
            "success": True,
            "xp_awarded": xp_amount,
            "new_xp": new_xp,
            "new_level": new_level,
            "level_changed": level_changed,
            "level_emoji": get_level_emoji(new_level)
        }
        
    except Exception as e:
        logger.error(f"Error awarding XP: {str(e)}")
        return {"success": False, "message": f"Error awarding XP: {str(e)}"}

async def create_contribution_entry(user_id: str, item_type: str, item_id: str) -> str:
    """Create a contribution entry for potential XP award"""
    try:
        # Check for duplicate contributions
        existing = await db.contributions_gamification.find_one({
            "user_id": user_id,
            "item_type": item_type,
            "item_id": item_id
        })
        
        if existing:
            return existing["id"]  # Return existing ID
        
        contribution = ContributionEntry(
            user_id=user_id,
            item_type=item_type,
            item_id=item_id
        )
        
        await db.contributions_gamification.insert_one(contribution.dict())
        logger.info(f"Created contribution entry for user {user_id}, {item_type} {item_id}")
        return contribution.id
        
    except Exception as e:
        logger.error(f"Error creating contribution entry: {str(e)}")
        return ""

# Security
SECRET_KEY = os.environ.get('SECRET_KEY', "topkit_secret_key_2024")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)  # Make it optional
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# File upload settings
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ================================
# AUTHENTICATION
# ================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    try:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin privileges"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

async def get_current_user_flexible(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """Get current authenticated user - supports both JWT tokens and session tokens"""
    try:
        # First try JWT token from Authorization header
        if credentials:
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                user = await db.users.find_one({"id": user_id})
                if user:
                    return user
        
        # If JWT fails, try session token from cookie
        session_token = request.cookies.get("session_token")
        if session_token:
            # Find session in database
            session = await db.sessions.find_one({"session_token": session_token})
            if session:
                # Check if session is still valid
                if session.get("expires_at") and session["expires_at"] > datetime.now(timezone.utc):
                    # Get user from session
                    user = await db.users.find_one({"id": session["user_id"]})
                    if user:
                        return user
                else:
                    # Session expired, clean it up
                    await db.sessions.delete_one({"session_token": session_token})
        
        # If both methods fail, raise authentication error
        raise HTTPException(status_code=401, detail="Invalid authentication")
        
    except jwt.PyJWTError:
        # JWT failed, try session token as fallback
        session_token = request.cookies.get("session_token")
        if session_token:
            session = await db.sessions.find_one({"session_token": session_token})
            if session and session.get("expires_at") and session["expires_at"] > datetime.now(timezone.utc):
                user = await db.users.find_one({"id": session["user_id"]})
                if user:
                    return user
        
        raise HTTPException(status_code=401, detail="Invalid authentication")

# ================================
# GAMIFICATION API ENDPOINTS
# ================================

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = Query(50, le=100)):
    """Get user leaderboard ranked by XP"""
    try:
        cursor = db.users.find({}, {"_id": 0}).sort("xp", -1).limit(limit)
        users = await cursor.to_list(length=None)
        
        leaderboard = []
        for i, user in enumerate(users, 1):
            user_data = {
                "rank": i,
                "username": user.get("name", "Unknown"),
                "xp": user.get("xp", 0),
                "level": user.get("level", UserLevel.REMPLACANT),
                "level_emoji": get_level_emoji(UserLevel(user.get("level", UserLevel.REMPLACANT)))
            }
            leaderboard.append(user_data)
        
        return leaderboard
    except Exception as e:
        logger.error(f"Error fetching leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/gamification", response_model=UserGamificationResponse)
async def get_user_gamification_data(user_id: str):
    """Get detailed gamification data for a user"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_xp = user.get("xp", 0)
        current_level = UserLevel(user.get("level", UserLevel.REMPLACANT))
        
        xp_to_next, next_level = get_xp_to_next_level(current_xp, current_level)
        progress_percentage = calculate_progress_percentage(current_xp, current_level)
        
        return UserGamificationResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user["role"],
            created_at=user["created_at"],
            xp=current_xp,
            level=current_level,
            level_emoji=get_level_emoji(current_level),
            xp_to_next_level=xp_to_next,
            next_level=next_level,
            progress_percentage=progress_percentage
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user gamification data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/approve-contribution")
async def approve_contribution(
    contribution_id: str = Form(...),
    admin_user: dict = Depends(get_admin_user)
):
    """Admin endpoint to approve contribution and award XP"""
    try:
        # Get contribution details
        contribution = await db.contributions_gamification.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        if contribution.get("is_approved"):
            raise HTTPException(status_code=400, detail="Contribution already approved")
        
        # Award XP
        result = await award_xp(
            user_id=contribution["user_id"],
            contribution_id=contribution_id,
            item_type=contribution["item_type"],
            item_id=contribution["item_id"],
            approved_by=admin_user["id"]
        )
        
        if result["success"]:
            return {
                "message": "Contribution approved and XP awarded",
                "xp_awarded": result["xp_awarded"],
                "new_level": result["new_level"],
                "level_changed": result["level_changed"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving contribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/pending-contributions")
async def get_pending_contributions(
    admin_user: dict = Depends(get_admin_user),
    limit: int = Query(50, le=100)
):
    """Admin endpoint to get pending contributions for approval"""
    try:
        cursor = db.contributions_gamification.find(
            {"is_approved": False}
        ).sort("created_at", -1).limit(limit)
        
        contributions = await cursor.to_list(length=None)
        
        # Enhance with user and item details
        enhanced_contributions = []
        for contrib in contributions:
            user = await db.users.find_one({"id": contrib["user_id"]})
            
            # Get item details based on type
            item_details = {}
            if contrib["item_type"] == "team":
                item = await db.teams.find_one({"id": contrib["item_id"]})
                item_details = {"name": item.get("name") if item else "Unknown Team"}
            elif contrib["item_type"] == "brand":
                item = await db.brands.find_one({"id": contrib["item_id"]})
                item_details = {"name": item.get("name") if item else "Unknown Brand"}
            elif contrib["item_type"] == "player":
                item = await db.players.find_one({"id": contrib["item_id"]})
                item_details = {"name": item.get("display_name") if item else "Unknown Player"}
            elif contrib["item_type"] == "competition":
                item = await db.competitions.find_one({"id": contrib["item_id"]})
                item_details = {"name": item.get("competition_name") if item else "Unknown Competition"}
            elif contrib["item_type"] == "jersey":
                item = await db.master_kits.find_one({"id": contrib["item_id"]})
                item_details = {"name": f"{item.get('club')} {item.get('season')}" if item else "Unknown Jersey"}
            
            enhanced_contrib = {
                **contrib,
                "_id": None,  # Remove MongoDB ObjectId
                "user_name": user.get("name") if user else "Unknown User",
                "item_details": item_details,
                "xp_to_award": XP_RULES.get(contrib["item_type"], 0)
            }
            enhanced_contributions.append(enhanced_contrib)
        
        return enhanced_contributions
        
    except Exception as e:
        logger.error(f"Error fetching pending contributions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# UTILITY FUNCTIONS
# ================================

def generate_topkit_reference(entity_type: str, db_collection) -> str:
    """Generate TopKit reference (TK-MASTER-000001, etc.)"""
    # This is a simplified version - would need proper counter logic in production
    import random
    number = random.randint(100000, 999999)
    return f"TK-{entity_type.upper()}-{number:06d}"

async def save_uploaded_file(file: UploadFile, subfolder: str = "general") -> str:
    """Save uploaded file and return the file path"""
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Create subfolder if it doesn't exist
    upload_path = UPLOAD_DIR / subfolder
    upload_path.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_path / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Return relative path for storage in database
    return f"uploads/{subfolder}/{unique_filename}"

async def trigger_cascading_updates(entity_type: str, entity_id: str, update_fields: dict):
    """Trigger cascading updates for related entities when an entity is updated"""
    try:
        logger.info(f"Triggering cascading updates for {entity_type} entity {entity_id}")
        
        if entity_type == "team":
            # Update master kits that reference this team
            if "name" in update_fields:
                result = await db.master_kits.update_many(
                    {"club_id": entity_id},
                    {"$set": {"club": update_fields["name"]}}
                )
                logger.info(f"Updated {result.modified_count} master kits referencing team {entity_id}")
                
        elif entity_type == "brand":
            # Update master kits that reference this brand
            if "name" in update_fields:
                result1 = await db.master_kits.update_many(
                    {"brand_id": entity_id},
                    {"$set": {"brand": update_fields["name"]}}
                )
                result2 = await db.master_kits.update_many(
                    {"main_sponsor_id": entity_id},
                    {"$set": {"main_sponsor": update_fields["name"]}}
                )
                logger.info(f"Updated {result1.modified_count + result2.modified_count} master kits referencing brand {entity_id}")
                
        elif entity_type == "competition":
            # Update master kits that reference this competition
            if "competition_name" in update_fields:
                result = await db.master_kits.update_many(
                    {"competition_id": entity_id},
                    {"$set": {"competition": update_fields["competition_name"]}}
                )
                logger.info(f"Updated {result.modified_count} master kits referencing competition {entity_id}")
                
        elif entity_type == "master_kit":
            # For master_kit updates, we should refresh collection items that reference this kit
            # Find all collection items that reference this master kit
            collection_items = await db.my_collection.find({"master_kit_id": entity_id}).to_list(length=None)
            
            if collection_items:
                logger.info(f"Found {len(collection_items)} collection items referencing updated master kit {entity_id}")
                
                # If front_photo_url was updated, we might want to invalidate caches or trigger notifications
                if "front_photo_url" in update_fields:
                    logger.info(f"Master kit {entity_id} photo was updated - collection items may need refreshing")
        
        logger.info(f"Completed cascading updates for {entity_type} entity {entity_id}")
        
    except Exception as e:
        logger.error(f"Error in cascading updates for {entity_type} entity {entity_id}: {str(e)}")
        # Don't raise the exception to avoid breaking the main update operation

# Duplicate function removed - using the first implementation above

# ================================
# BASIC ENDPOINTS FOR FRONTEND COMPATIBILITY
# ================================

@app.get("/api/teams")
async def get_teams():
    """Get teams - basic endpoint to avoid 404s (latest first for homepage)"""
    try:
        cursor = db.teams.find({}, {"_id": 0}).sort("created_at", -1)  # Sort by created_at descending (latest first)
        teams = await cursor.to_list(length=None)
        return teams
    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        return []

@app.get("/api/brands")
async def get_brands():
    """Get brands - basic endpoint to avoid 404s"""
    try:
        cursor = db.brands.find({}, {"_id": 0})  # Exclude MongoDB _id field
        brands = await cursor.to_list(length=None)
        return brands
    except Exception as e:
        logger.error(f"Error fetching brands: {str(e)}")
        return []

@app.get("/api/competitions")
async def get_competitions():
    """Get competitions - basic endpoint to avoid 404s"""
    try:
        cursor = db.competitions.find({}, {"_id": 0})  # Exclude MongoDB _id field
        competitions = await cursor.to_list(length=None)
        return competitions
    except Exception as e:
        logger.error(f"Error fetching competitions: {str(e)}")
        return []

@app.get("/api/players")
async def get_players():
    """Get players - basic endpoint to avoid 404s"""
    try:
        cursor = db.players.find({}, {"_id": 0})  # Exclude MongoDB _id field
        players = await cursor.to_list(length=None)
        return players
    except Exception as e:
        logger.error(f"Error fetching players: {str(e)}")
        return []

@app.get("/api/master-jerseys")
async def get_master_jerseys():
    """Get master jerseys - basic endpoint to avoid 404s (redirects to master-kits)"""
    try:
        # Redirect to master-kits endpoint for backward compatibility
        cursor = db.master_kits.find({})
        master_kits = await cursor.to_list(length=None)
        return master_kits
    except Exception as e:
        logger.error(f"Error fetching master jerseys: {str(e)}")
        return []

# ================================
# BACKWARD COMPATIBILITY ENDPOINTS
# ================================

@app.get("/api/master-jerseys")
async def get_master_jerseys_list():
    """Backward compatibility - redirect master-jerseys list to master-kits"""
    try:
        master_kits = await db.master_kits.find({}).to_list(length=None)
        # Remove MongoDB ObjectId from all items
        for kit in master_kits:
            if "_id" in kit:
                del kit["_id"]
        return master_kits
    except Exception as e:
        logger.error(f"Error fetching master jerseys: {str(e)}")
        return []

@app.get("/api/reference-kits")
async def get_reference_kits_list():
    """Backward compatibility - return empty array for reference kits"""
    return []

@app.get("/api/master-jerseys/{jersey_id}")  
async def get_single_master_jersey(jersey_id: str):
    """Backward compatibility - redirect single master-jersey to master-kit"""
    try:
        master_kit = await db.master_kits.find_one({"id": jersey_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        # Remove MongoDB ObjectId
        if "_id" in master_kit:
            del master_kit["_id"]
            
        return master_kit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching master jersey {jersey_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# FORM DATA ENDPOINTS
# ================================

@app.get("/api/form-data/clubs")
async def get_clubs_for_form():
    """Get clubs for Master Kit form dropdown"""
    try:
        cursor = db.teams.find({}, {"id": 1, "name": 1, "country": 1})
        clubs = await cursor.to_list(length=None)
        return [{"id": club["id"], "name": club["name"], "country": club.get("country", "Unknown")} for club in clubs]
    except Exception as e:
        logger.error(f"Error fetching clubs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/form-data/competitions")
async def get_competitions_for_form():
    """Get competitions for Master Kit form dropdown"""
    try:
        cursor = db.competitions.find({}, {"id": 1, "competition_name": 1, "country": 1})
        competitions = await cursor.to_list(length=None)
        return [{"id": comp["id"], "name": comp["competition_name"], "country": comp.get("country", "Unknown")} for comp in competitions]
    except Exception as e:
        logger.error(f"Error fetching competitions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/form-data/brands")
async def get_brands_for_form():
    """Get brands for Master Kit form dropdown"""
    try:
        cursor = db.brands.find({}, {"id": 1, "name": 1, "country": 1})
        brands = await cursor.to_list(length=None)
        return [{"id": brand["id"], "name": brand["name"], "country": brand.get("country", "Unknown")} for brand in brands]
    except Exception as e:
        logger.error(f"Error fetching brands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# MASTER KIT ENDPOINTS
# ================================

@app.post("/api/master-kits", response_model=MasterKitResponse)
async def create_master_kit(
    master_kit_data: MasterKitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new Master Kit (official jersey reference)"""
    try:
        # Validate referenced entities exist
        club = await db.teams.find_one({"id": master_kit_data.club_id})
        if not club:
            raise HTTPException(status_code=400, detail="Club not found")
        
        competition = await db.competitions.find_one({"id": master_kit_data.competition_id})
        if not competition:
            raise HTTPException(status_code=400, detail="Competition not found")
            
        brand = await db.brands.find_one({"id": master_kit_data.brand_id})
        if not brand:
            raise HTTPException(status_code=400, detail="Brand not found")
        
        # Validate sponsor if provided
        main_sponsor = None
        if master_kit_data.main_sponsor_id:
            main_sponsor = await db.brands.find_one({"id": master_kit_data.main_sponsor_id})
            if not main_sponsor:
                raise HTTPException(status_code=400, detail="Main sponsor not found")
        
        # Generate new Master Kit
        master_kit = MasterKit(
            **master_kit_data.dict(),
            created_by=current_user["id"],
            topkit_reference=generate_topkit_reference("MASTER", db.master_kits)
        )
        
        # Insert into database
        result = await db.master_kits.insert_one(master_kit.dict())
        
        if result.inserted_id:
            # Create a gamification contribution entry for approval
            try:
                contribution_id = await create_contribution_entry(
                    user_id=current_user["id"],
                    item_type="jersey",
                    item_id=master_kit.id
                )
                logger.info(f"Created gamification contribution entry: {contribution_id} for Master Kit: {master_kit.id}")
            except Exception as contrib_error:
                logger.warning(f"Failed to create gamification contribution entry: {str(contrib_error)}")
            
            # Create a contribution entry for the Master Kit creation (existing system)
            try:
                contribution_data = {
                    "id": str(uuid.uuid4()),
                    "title": f"New Master Kit: {master_kit.club} {master_kit.season} {master_kit.kit_type}",
                    "entity_type": "master_kit",
                    "entity_id": master_kit.id,
                    "status": "approved",  # Auto-approve Master Kit creations
                    "created_at": datetime.utcnow(),
                    "created_by": current_user["id"],
                    "upvotes": 0,
                    "downvotes": 0,
                    "images_count": 1 if master_kit.front_photo_url else 0,
                    "topkit_reference": master_kit.topkit_reference,
                    "change_summary": {
                        "club": master_kit.club,
                        "season": master_kit.season,
                        "kit_type": master_kit.kit_type,
                        "brand": master_kit.brand,
                        "competition": master_kit.competition
                    }
                }
                
                await db.contributions.insert_one(contribution_data)
                logger.info(f"Created contribution entry for Master Kit: {master_kit.topkit_reference}")
                
            except Exception as contrib_error:
                logger.warning(f"Failed to create contribution entry for Master Kit: {str(contrib_error)}")
                # Don't fail the Master Kit creation if contribution creation fails
            
            # Get updated item with populated data
            created_kit = await db.master_kits.find_one({"id": master_kit.id})
            
            # Populate related data for response
            response_data = MasterKitResponse(
                **created_kit,
                club_name=club.get("name"),
                competition_name=competition.get("competition_name"),
                brand_name=brand.get("name"),
                main_sponsor_name=main_sponsor.get("name") if main_sponsor else None
            )
            
            return response_data
        else:
            raise HTTPException(status_code=500, detail="Error creating Master Kit")
            
    except Exception as e:
        logger.error(f"Error creating Master Kit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/master-kits", response_model=List[MasterKitResponse])
async def get_master_kits(
    club: Optional[str] = None,
    season: Optional[str] = None,
    kit_type: Optional[KitType] = None,
    brand: Optional[str] = None,
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get Master Kits with optional filtering - backward compatible"""
    try:
        # Build filter query
        filter_query = {}
        if club:
            filter_query["club"] = {"$regex": club, "$options": "i"}
        if season:
            filter_query["season"] = season
        if kit_type:
            filter_query["kit_type"] = kit_type
        if brand:
            filter_query["brand"] = {"$regex": brand, "$options": "i"}
        
        # Query database
        cursor = db.master_kits.find(filter_query).skip(skip).limit(limit)
        master_kits = await cursor.to_list(length=None)
        
        # Convert data to be compatible with both old and new formats
        response_kits = []
        for kit in master_kits:
            try:
                # Handle gender enum conversion for backward compatibility
                if kit.get("gender") == "men":
                    kit["gender"] = "man"
                elif kit.get("gender") == "women":
                    kit["gender"] = "woman"
                    
                # Handle backward compatibility for club names
                if "club" in kit and not kit.get("club_name"):
                    kit["club_name"] = kit["club"]
                elif kit.get("club_id") and not kit.get("club_name"):
                    # Look up club name from club_id
                    club = await db.teams.find_one({"id": kit["club_id"]})
                    if club:
                        kit["club_name"] = club.get("name", "Unknown Club")
                        kit["club"] = club.get("name", "Unknown Club")  # For backward compatibility
                    
                # Handle backward compatibility for competition names
                if "competition" in kit and not kit.get("competition_name"):
                    kit["competition_name"] = kit["competition"]
                elif kit.get("competition_id") and not kit.get("competition_name"):
                    # Look up competition name from competition_id
                    competition = await db.competitions.find_one({"id": kit["competition_id"]})
                    if competition:
                        kit["competition_name"] = competition.get("competition_name", "Unknown Competition")
                        kit["competition"] = competition.get("competition_name", "Unknown Competition")  # For backward compatibility
                    
                # Handle backward compatibility for brand names
                if "brand" in kit and not kit.get("brand_name"):
                    kit["brand_name"] = kit["brand"]
                elif kit.get("brand_id") and not kit.get("brand_name"):
                    # Look up brand name from brand_id
                    brand = await db.brands.find_one({"id": kit["brand_id"]})
                    if brand:
                        kit["brand_name"] = brand.get("name", "Unknown Brand")
                        kit["brand"] = brand.get("name", "Unknown Brand")  # For backward compatibility
                        
                # Handle backward compatibility for main sponsor names
                if "main_sponsor" in kit and not kit.get("main_sponsor_name"):
                    kit["main_sponsor_name"] = kit["main_sponsor"]
                elif kit.get("main_sponsor_id") and not kit.get("main_sponsor_name"):
                    # Look up main sponsor name from main_sponsor_id
                    sponsor = await db.brands.find_one({"id": kit["main_sponsor_id"]})
                    if sponsor:
                        kit["main_sponsor_name"] = sponsor.get("name", "Unknown Sponsor")
                        kit["main_sponsor"] = sponsor.get("name", "Unknown Sponsor")  # For backward compatibility
                    
                # Ensure primary_color has a default value if None
                if kit.get("primary_color") is None:
                    kit["primary_color"] = "Unknown"
                
                response_kits.append(MasterKitResponse(**kit))
                
            except Exception as kit_error:
                logger.warning(f"Skipping Master Kit {kit.get('id', 'unknown')} due to validation error: {str(kit_error)}")
                continue
        
        return response_kits
        
    except Exception as e:
        logger.error(f"Error fetching Master Kits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/master-kits/{master_kit_id}", response_model=MasterKitResponse)
async def get_master_kit(master_kit_id: str):
    """Get specific Master Kit by ID - backward compatible"""
    try:
        master_kit = await db.master_kits.find_one({"id": master_kit_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        # Apply backward compatibility transformations
        if master_kit.get("gender") == "men":
            master_kit["gender"] = "man"
        elif master_kit.get("gender") == "women":
            master_kit["gender"] = "woman"
            
        # Apply backward compatibility transformations for names
        # Handle club names
        if "club" in master_kit and not master_kit.get("club_name"):
            master_kit["club_name"] = master_kit["club"]
        elif master_kit.get("club_id") and not master_kit.get("club_name"):
            # Look up club name from club_id
            club = await db.teams.find_one({"id": master_kit["club_id"]})
            if club:
                master_kit["club_name"] = club.get("name", "Unknown Club")
                master_kit["club"] = club.get("name", "Unknown Club")  # For backward compatibility
                
        # Handle competition names
        if "competition" in master_kit and not master_kit.get("competition_name"):
            master_kit["competition_name"] = master_kit["competition"]
        elif master_kit.get("competition_id") and not master_kit.get("competition_name"):
            # Look up competition name from competition_id
            competition = await db.competitions.find_one({"id": master_kit["competition_id"]})
            if competition:
                master_kit["competition_name"] = competition.get("competition_name", "Unknown Competition")
                master_kit["competition"] = competition.get("competition_name", "Unknown Competition")  # For backward compatibility
                
        # Handle brand names
        if "brand" in master_kit and not master_kit.get("brand_name"):
            master_kit["brand_name"] = master_kit["brand"]
        elif master_kit.get("brand_id") and not master_kit.get("brand_name"):
            # Look up brand name from brand_id
            brand = await db.brands.find_one({"id": master_kit["brand_id"]})
            if brand:
                master_kit["brand_name"] = brand.get("name", "Unknown Brand")
                master_kit["brand"] = brand.get("name", "Unknown Brand")  # For backward compatibility
                
        # Handle main sponsor names
        if "main_sponsor" in master_kit and not master_kit.get("main_sponsor_name"):
            master_kit["main_sponsor_name"] = master_kit["main_sponsor"]
        elif master_kit.get("main_sponsor_id") and not master_kit.get("main_sponsor_name"):
            # Look up main sponsor name from main_sponsor_id
            sponsor = await db.brands.find_one({"id": master_kit["main_sponsor_id"]})
            if sponsor:
                master_kit["main_sponsor_name"] = sponsor.get("name", "Unknown Sponsor")
                master_kit["main_sponsor"] = sponsor.get("name", "Unknown Sponsor")  # For backward compatibility
            
        # Ensure primary_color has a default value if None
        if master_kit.get("primary_color") is None:
            master_kit["primary_color"] = "Unknown"
        
        return MasterKitResponse(**master_kit)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Master Kit {master_kit_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/master-kits/search")
async def search_master_kits(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=50)
):
    """Search Master Kits by club, season, brand, etc. - backward compatible"""
    try:
        # Build search query
        search_query = {
            "$or": [
                {"club": {"$regex": q, "$options": "i"}},
                {"season": {"$regex": q, "$options": "i"}},
                {"brand": {"$regex": q, "$options": "i"}},
                {"competition": {"$regex": q, "$options": "i"}},
                {"topkit_reference": {"$regex": q, "$options": "i"}}
            ]
        }
        
        cursor = db.master_kits.find(search_query).limit(limit)
        master_kits = await cursor.to_list(length=None)
        
        # Apply backward compatibility transformations
        response_kits = []
        for kit in master_kits:
            try:
                # Handle gender enum conversion
                if kit.get("gender") == "men":
                    kit["gender"] = "man"
                elif kit.get("gender") == "women":
                    kit["gender"] = "woman"
                    
                # Set names from old format fields
                if "club" in kit and not kit.get("club_name"):
                    kit["club_name"] = kit["club"]
                if "competition" in kit and not kit.get("competition_name"):
                    kit["competition_name"] = kit["competition"]
                if "brand" in kit and not kit.get("brand_name"):
                    kit["brand_name"] = kit["brand"]
                if "main_sponsor" in kit and not kit.get("main_sponsor_name"):
                    kit["main_sponsor_name"] = kit["main_sponsor"]
                    
                # Ensure primary_color has a default value if None
                if kit.get("primary_color") is None:
                    kit["primary_color"] = "Unknown"
                
                response_kits.append(MasterKitResponse(**kit))
                
            except Exception as kit_error:
                logger.warning(f"Skipping Master Kit {kit.get('id', 'unknown')} in search due to validation error: {str(kit_error)}")
                continue
        
        return response_kits
        
    except Exception as e:
        logger.error(f"Error searching Master Kits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# MY COLLECTION ENDPOINTS
# ================================

@app.post("/api/my-collection", response_model=MyCollectionResponse)
async def add_to_my_collection(
    collection_data: MyCollectionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a Master Kit to My Collection with personal details"""
    try:
        # Verify Master Kit exists
        master_kit = await db.master_kits.find_one({"id": collection_data.master_kit_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        # Check if already in collection (same type)
        existing_same_type = await db.my_collection.find_one({
            "user_id": current_user["id"],
            "master_kit_id": collection_data.master_kit_id,
            "collection_type": collection_data.collection_type
        })
        if existing_same_type:
            collection_type_name = "owned collection" if collection_data.collection_type == "owned" else "want list"
            raise HTTPException(status_code=400, detail=f"Master Kit already in your {collection_type_name}")
        
        # BILATERAL LOGIC: Check if already in opposite collection type
        opposite_type = "wanted" if collection_data.collection_type == "owned" else "owned"
        existing_opposite_type = await db.my_collection.find_one({
            "user_id": current_user["id"],
            "master_kit_id": collection_data.master_kit_id,
            "collection_type": opposite_type
        })
        if existing_opposite_type:
            opposite_type_name = "owned collection" if opposite_type == "owned" else "want list"
            current_type_name = "owned collection" if collection_data.collection_type == "owned" else "want list"
            raise HTTPException(
                status_code=400, 
                detail=f"Master Kit is already in your {opposite_type_name}. Please remove it first before adding to {current_type_name}."
            )
        
        # Create collection entry
        collection_item = MyCollection(
            **collection_data.dict(),
            user_id=current_user["id"]
        )
        
        # Insert into database
        result = await db.my_collection.insert_one(collection_item.dict())
        
        if result.inserted_id:
            # Update Master Kit collector count
            await db.master_kits.update_one(
                {"id": collection_data.master_kit_id},
                {"$inc": {"total_collectors": 1}}
            )
            
            # Return response with embedded Master Kit info
            collection_item_dict = collection_item.dict()
            collection_item_dict["master_kit"] = MasterKitResponse(**master_kit)
            
            return MyCollectionResponse(**collection_item_dict)
        else:
            raise HTTPException(status_code=500, detail="Error adding to collection")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/my-collection", response_model=List[MyCollectionResponse])
async def get_my_collection(
    current_user: dict = Depends(get_current_user),
    collection_type: Optional[str] = Query(None, description="Filter by collection type (owned/wanted)"),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get user's collection (Master Kits with personal details)"""
    try:
        # Build query
        query = {"user_id": current_user["id"]}
        if collection_type:
            query["collection_type"] = collection_type
            
        # Get collection items
        cursor = db.my_collection.find(query).skip(skip).limit(limit)
        collection_items = await cursor.to_list(length=None)
        
        # Embed Master Kit info for each item
        response_items = []
        for item in collection_items:
            master_kit = await db.master_kits.find_one({"id": item["master_kit_id"]})
            if master_kit:
                # Add default collection_type for backward compatibility
                if "collection_type" not in item:
                    item["collection_type"] = "owned"
                    
                item["master_kit"] = MasterKitResponse(**master_kit)
                response_items.append(MyCollectionResponse(**item))
        
        return response_items
        
    except Exception as e:
        logger.error(f"Error fetching collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/my-collection/{collection_id}", response_model=MyCollectionResponse)
async def update_collection_item(
    collection_id: str,
    update_data: MyCollectionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update personal details for a collection item"""
    try:
        # Find collection item
        collection_item = await db.my_collection.find_one({
            "id": collection_id,
            "user_id": current_user["id"]
        })
        if not collection_item:
            raise HTTPException(status_code=404, detail="Collection item not found")
        
        # Update with provided fields only
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updated_at"] = datetime.utcnow()
        
        result = await db.my_collection.update_one(
            {"id": collection_id, "user_id": current_user["id"]},
            {"$set": update_dict}
        )
        
        if result.modified_count > 0:
            # Get updated item with Master Kit info
            updated_item = await db.my_collection.find_one({"id": collection_id})
            master_kit = await db.master_kits.find_one({"id": updated_item["master_kit_id"]})
            
            updated_item["master_kit"] = MasterKitResponse(**master_kit)
            return MyCollectionResponse(**updated_item)
        else:
            raise HTTPException(status_code=500, detail="Error updating collection item")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating collection item: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/my-collection/{collection_id}")
async def remove_from_collection(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove item from My Collection"""
    try:
        # Find and delete collection item
        collection_item = await db.my_collection.find_one_and_delete({
            "id": collection_id,
            "user_id": current_user["id"]
        })
        
        if not collection_item:
            raise HTTPException(status_code=404, detail="Collection item not found")
        
        # Update Master Kit collector count
        await db.master_kits.update_one(
            {"id": collection_item["master_kit_id"]},
            {"$inc": {"total_collectors": -1}}
        )
        
        return {"message": "Item removed from collection successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from collection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# FILE UPLOAD ENDPOINTS
# ================================

@app.post("/api/upload/master-kit-photo")
async def upload_master_kit_photo(
    file: UploadFile = File(..., description="Master Kit front photo (minimum 800x600px)"),
    current_user: dict = Depends(get_current_user)
):
    """Upload front photo for Master Kit"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save file
        file_path = await save_uploaded_file(file, "master_kits")
        
        # Validate image dimensions (minimum 800x600px)
        full_path = Path(file_path)
        with Image.open(full_path) as img:
            width, height = img.size
            if width < 800 or height < 600:
                # Delete the uploaded file if it doesn't meet requirements
                full_path.unlink()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Image must be at least 800x600px. Uploaded image is {width}x{height}px"
                )
        
        return {"file_url": file_path, "message": "Photo uploaded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading Master Kit photo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/certificate")
async def upload_certificate(
    file: UploadFile = File(..., description="Certificate of authenticity"),
    current_user: dict = Depends(get_current_user)
):
    """Upload certificate for signed kit"""
    try:
        # Save file
        file_path = await save_uploaded_file(file, "certificates")
        
        return {"file_url": file_path, "message": "Certificate uploaded successfully"}
        
    except Exception as e:
        logger.error(f"Error uploading certificate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/proof-of-purchase")
async def upload_proof_of_purchase(
    file: UploadFile = File(..., description="Proof of purchase document"),
    current_user: dict = Depends(get_current_user)
):
    """Upload proof of purchase"""
    try:
        # Save file
        file_path = await save_uploaded_file(file, "receipts")
        
        return {"file_url": file_path, "message": "Proof of purchase uploaded successfully"}
        
    except Exception as e:
        logger.error(f"Error uploading proof of purchase: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# FILE SERVING
# ================================

@app.get("/api/uploads/{file_path:path}")
async def serve_file(file_path: str):
    """Serve uploaded files"""
    try:
        full_path = UPLOAD_DIR / file_path
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(full_path))
        if not content_type:
            content_type = "application/octet-stream"
        
        return FileResponse(
            path=str(full_path),
            media_type=content_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/legacy-image/{image_id}")
async def serve_legacy_image(image_id: str):
    """Serve legacy format images (image_uploaded_TIMESTAMP)"""
    try:
        # Legacy images might be stored in various directories
        possible_paths = [
            UPLOAD_DIR / "teams" / f"{image_id}.jpg",
            UPLOAD_DIR / "teams" / f"{image_id}.jpeg", 
            UPLOAD_DIR / "teams" / f"{image_id}.png",
            UPLOAD_DIR / "brands" / f"{image_id}.jpg",
            UPLOAD_DIR / "brands" / f"{image_id}.jpeg",
            UPLOAD_DIR / "brands" / f"{image_id}.png",
            UPLOAD_DIR / "players" / f"{image_id}.jpg",
            UPLOAD_DIR / "players" / f"{image_id}.jpeg",
            UPLOAD_DIR / "players" / f"{image_id}.png",
            UPLOAD_DIR / "competitions" / f"{image_id}.jpg",
            UPLOAD_DIR / "competitions" / f"{image_id}.jpeg",
            UPLOAD_DIR / "competitions" / f"{image_id}.png",
            # Also check root uploads directory
            UPLOAD_DIR / f"{image_id}.jpg",
            UPLOAD_DIR / f"{image_id}.jpeg",
            UPLOAD_DIR / f"{image_id}.png"
        ]
        
        for path in possible_paths:
            if path.exists():
                # Determine content type
                content_type, _ = mimetypes.guess_type(str(path))
                if not content_type:
                    content_type = "application/octet-stream"
                
                return FileResponse(
                    path=str(path),
                    media_type=content_type
                )
        
        # If no file found, return a 404
        raise HTTPException(status_code=404, detail=f"Legacy image {image_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving legacy image {image_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# BASIC AUTH ENDPOINTS (placeholder)
# ================================

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class GoogleSessionRequest(BaseModel):
    session_id: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login user (simplified for now)"""
    try:
        # Find user by email
        user = await db.users.find_one({"email": login_data.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Verify password using bcrypt
        if not pwd_context.verify(login_data.password, user.get("password_hash")):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate JWT token
        token_data = {"sub": user["id"]}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Return response
        user_response = UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user.get("role", "user"),
            created_at=user.get("created_at", datetime.utcnow())
        )
        
        return LoginResponse(token=token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/google/session", response_model=LoginResponse)
async def google_session_auth(request: GoogleSessionRequest, response: Response):
    """Handle Google OAuth session authentication via Emergent Auth"""
    try:
        # Call Emergent Auth API to get session data
        session_url = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
        headers = {"X-Session-ID": request.session_id}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(session_url, headers=headers) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=401, detail="Invalid session ID")
                
                session_data = await resp.json()
        
        # Extract user data from session
        google_user_id = session_data.get("id")
        email = session_data.get("email")
        name = session_data.get("name")
        picture = session_data.get("picture")
        session_token = session_data.get("session_token")
        
        if not all([google_user_id, email, name, session_token]):
            raise HTTPException(status_code=400, detail="Invalid session data")
        
        # Check if user exists, if not create new user
        user = await db.users.find_one({"email": email})
        
        if not user:
            # Create new user for Google OAuth
            user_id = str(uuid.uuid4())
            new_user = {
                "id": user_id,
                "name": name,
                "email": email,
                "google_id": google_user_id,
                "picture": picture,
                "role": "user",
                "created_at": datetime.now(timezone.utc),
                "auth_type": "google"
            }
            await db.users.insert_one(new_user)
            user = new_user
        
        # Store session in database with timezone-aware expiry
        session_expiry = datetime.now(timezone.utc) + timedelta(days=7)
        session_record = {
            "session_token": session_token,
            "user_id": user["id"],
            "expires_at": session_expiry,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Remove any existing sessions for this user
        await db.sessions.delete_many({"user_id": user["id"]})
        
        # Insert new session
        await db.sessions.insert_one(session_record)
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days in seconds
            httponly=True,
            secure=True,
            samesite="none",
            path="/"
        )
        
        # Generate JWT token for compatibility
        token_data = {"sub": user["id"]}
        jwt_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Return response
        user_response = UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            role=user.get("role", "user"),
            created_at=user.get("created_at", datetime.now(timezone.utc))
        )
        
        return LoginResponse(token=jwt_token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during Google OAuth: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user and clear session"""
    try:
        # Get session token from cookie
        session_token = request.cookies.get("session_token")
        
        if session_token:
            # Delete session from database
            await db.sessions.delete_one({"session_token": session_token})
        
        # Clear cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            samesite="none"
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user_flexible)):
    """Get current user profile (works with both JWT and session token)"""
    try:
        user_response = UserResponse(
            id=current_user["id"],
            name=current_user["name"],
            email=current_user["email"],
            role=current_user.get("role", "user"),
            created_at=current_user.get("created_at", datetime.now(timezone.utc))
        )
        return user_response
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(register_data: RegisterRequest):
    """Register new user"""
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": register_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = pwd_context.hash(register_data.password)
        
        # Create new user
        user_id = str(uuid.uuid4())
        new_user = {
            "id": user_id,
            "name": register_data.name,
            "email": register_data.email,
            "password_hash": password_hash,
            "role": "user",
            "created_at": datetime.now(timezone.utc)
        }
        
        # Save to database
        await db.users.insert_one(new_user)
        
        # Generate JWT token
        token_data = {"sub": user_id}
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        
        # Return response
        user_response = UserResponse(
            id=user_id,
            name=register_data.name,
            email=register_data.email,
            role="user",
            created_at=new_user["created_at"]
        )
        
        return LoginResponse(token=token, user=user_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# DATABASE CLEANUP ENDPOINT
# ================================

@app.post("/api/admin/cleanup-database")
async def cleanup_database(admin_user: dict = Depends(get_admin_user)):
    """Clean up old data and start fresh (as requested)"""
    try:
        # Delete all old kit-related collections
        collections_to_clean = [
            "reference_kits",
            "personal_kits", 
            "wanted_kits",
            "master_jerseys",  # Old master jerseys
            "jersey_releases",
            "user_collections",
            "reference_kit_collections"
        ]
        
        cleanup_results = {}
        for collection_name in collections_to_clean:
            result = await db[collection_name].delete_many({})
            cleanup_results[collection_name] = result.deleted_count
        
        # Keep master_kits collection but clean it if needed
        # (Since we're using the same name but with simplified structure)
        
        return {
            "message": "Database cleanup completed - starting fresh as requested",
            "deleted": cleanup_results
        }
        
    except Exception as e:
        logger.error(f"Error during database cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# CONTRIBUTION SYSTEM ENDPOINTS
# ================================

class ContributionCreate(BaseModel):
    entity_type: str
    title: str
    description: str = ""
    data: dict
    source_urls: List[str] = []
    entity_id: Optional[str] = None  # For updating existing entities

class ContributionResponse(BaseModel):
    id: str
    entity_type: str
    title: str
    
    # Support both old and new formats
    description: Optional[str] = ""
    data: Optional[dict] = {}
    
    # Old format fields (for backward compatibility)
    entity_id: Optional[str] = None
    change_summary: Optional[dict] = {}
    
    status: str = "pending_review"
    upvotes: int = 0
    downvotes: int = 0
    images_count: int = 0
    created_at: datetime
    topkit_reference: Optional[str] = None
    source_urls: List[str] = []
    uploaded_images: Optional[List[dict]] = []  # New field for tracking uploaded images

@app.post("/api/contributions-v2/", response_model=ContributionResponse)
async def create_contribution(
    contribution_data: ContributionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new contribution"""
    try:
        # Generate contribution
        contribution = {
            "id": str(uuid.uuid4()),
            "entity_type": contribution_data.entity_type,
            "entity_id": contribution_data.entity_id,  # Store entity_id for updates
            "title": contribution_data.title,
            "description": contribution_data.description,
            "data": contribution_data.data,
            "status": "pending_review",
            "created_at": datetime.utcnow(),
            "created_by": current_user["id"],
            "upvotes": 0,
            "downvotes": 0,
            "images_count": 0,
            "source_urls": contribution_data.source_urls,
            "topkit_reference": f"TK-CONTRIB-{uuid.uuid4().hex[:6].upper()}"
        }
        
        # Insert into database
        result = await db.contributions.insert_one(contribution)
        
        if result.inserted_id:
            return ContributionResponse(**contribution)
        else:
            raise HTTPException(status_code=500, detail="Error creating contribution")
            
    except Exception as e:
        logger.error(f"Error creating contribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contributions-v2/", response_model=List[ContributionResponse])
async def get_contributions(
    status: Optional[str] = None,
    entity_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get contributions with filtering"""
    try:
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status
        if entity_type:
            filter_query["entity_type"] = entity_type
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Query database
        cursor = db.contributions.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        contributions = await cursor.to_list(length=None)
        
        # Convert contributions to handle both old and new formats
        response_contributions = []
        for contrib in contributions:
            # Handle backward compatibility
            if "description" not in contrib:
                contrib["description"] = ""
            if "data" not in contrib:
                contrib["data"] = contrib.get("change_summary", {})
            if "source_urls" not in contrib:
                contrib["source_urls"] = []
                
            response_contributions.append(ContributionResponse(**contrib))
        
        return response_contributions
        
    except Exception as e:
        logger.error(f"Error fetching contributions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contributions-v2/{contribution_id}", response_model=ContributionResponse)
async def get_contribution(
    contribution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific contribution by ID"""
    try:
        contribution = await db.contributions.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        # Handle backward compatibility
        if "description" not in contribution:
            contribution["description"] = ""
        if "data" not in contribution:
            contribution["data"] = contribution.get("change_summary", {})
        if "source_urls" not in contribution:
            contribution["source_urls"] = []
        
        return ContributionResponse(**contribution)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contribution {contribution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class VoteRequest(BaseModel):
    vote_type: str  # "upvote" or "downvote"
    comment: str = ""
    field_votes: dict = {}

@app.post("/api/contributions-v2/{contribution_id}/vote")
async def vote_on_contribution(
    contribution_id: str,
    vote_data: VoteRequest,
    current_user: dict = Depends(get_current_user)
):
    """Vote on a contribution"""
    try:
        contribution = await db.contributions.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        # Update vote counts
        if vote_data.vote_type == "upvote":
            new_upvotes = contribution.get("upvotes", 0) + 1
            await db.contributions.update_one(
                {"id": contribution_id},
                {"$set": {"upvotes": new_upvotes}}
            )
            
            # Auto-approve if 3 upvotes
            if new_upvotes >= 3:
                await db.contributions.update_one(
                    {"id": contribution_id},
                    {"$set": {"status": "approved"}}
                )
                return {
                    "message": "Vote recorded",
                    "upvotes": new_upvotes,
                    "downvotes": contribution.get("downvotes", 0),
                    "status": "approved",
                    "auto_approved": True
                }
        
        elif vote_data.vote_type == "downvote":
            new_downvotes = contribution.get("downvotes", 0) + 1
            await db.contributions.update_one(
                {"id": contribution_id},
                {"$set": {"downvotes": new_downvotes}}
            )
            
            # Auto-reject if 2 downvotes
            if new_downvotes >= 2:
                await db.contributions.update_one(
                    {"id": contribution_id},
                    {"$set": {"status": "rejected"}}
                )
                return {
                    "message": "Vote recorded",
                    "upvotes": contribution.get("upvotes", 0),
                    "downvotes": new_downvotes,
                    "status": "rejected",
                    "auto_rejected": True
                }
        
        # Get updated contribution
        updated_contribution = await db.contributions.find_one({"id": contribution_id})
        
        return {
            "message": "Vote recorded",
            "upvotes": updated_contribution.get("upvotes", 0),
            "downvotes": updated_contribution.get("downvotes", 0),
            "status": updated_contribution.get("status", "pending_review")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting on contribution {contribution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contributions-v2/{contribution_id}/images")
async def upload_contribution_image(
    contribution_id: str,
    file: UploadFile = File(...),
    is_primary: str = Form("false"),
    caption: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Upload image for contribution"""
    try:
        # Verify contribution exists
        contribution = await db.contributions.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        # Save image
        file_path = await save_uploaded_file(file, "contributions")
        
        # Update contribution with image info and file path
        # First ensure uploaded_images array exists
        await db.contributions.update_one(
            {"id": contribution_id, "uploaded_images": {"$exists": False}},
            {"$set": {"uploaded_images": []}}
        )
        
        # Then push the new image info and increment count
        update_data = {
            "$inc": {"images_count": 1},
            "$push": {"uploaded_images": {
                "field_name": caption or "logo",
                "file_path": file_path,
                "is_primary": is_primary.lower() == "true",
                "uploaded_at": datetime.utcnow()
            }}
        }
        
        result = await db.contributions.update_one(
            {"id": contribution_id},
            update_data
        )
        
        logger.info(f"Updated contribution {contribution_id} with image. Modified count: {result.modified_count}")
        
        return {"file_url": file_path, "message": "Image uploaded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image for contribution {contribution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contributions-v2/admin/moderation-stats")
async def get_moderation_stats(admin_user: dict = Depends(get_admin_user)):
    """Get moderation statistics for admin"""
    try:
        total_pending = await db.contributions.count_documents({"status": "pending_review"})
        total_approved = await db.contributions.count_documents({"status": "approved"})
        total_rejected = await db.contributions.count_documents({"status": "rejected"})
        
        return {
            "pending": total_pending,
            "approved": total_approved,
            "rejected": total_rejected,
            "total": total_pending + total_approved + total_rejected
        }
        
    except Exception as e:
        logger.error(f"Error fetching moderation stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ModerationAction(BaseModel):
    action: str  # "approve" or "reject"
    reason: str = ""

@app.post("/api/contributions-v2/{contribution_id}/moderate")
async def moderate_contribution(
    contribution_id: str,
    moderation_data: ModerationAction,
    admin_user: dict = Depends(get_admin_user)
):
    """Moderate a contribution (admin only)"""
    try:
        contribution = await db.contributions.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution not found")
        
        new_status = "approved" if moderation_data.action == "approve" else "rejected"
        entity_id = None
        
        # If approving, create or update the actual entity in the database
        if moderation_data.action == "approve":
            entity_id = await create_or_update_entity_from_contribution(contribution)
            
            # Transfer contribution images to entity if any exist
            if entity_id:
                await transfer_contribution_images_to_entity(contribution, entity_id)
        
        await db.contributions.update_one(
            {"id": contribution_id},
            {
                "$set": {
                    "status": new_status,
                    "moderated_at": datetime.utcnow(),
                    "moderated_by": admin_user["id"],
                    "moderation_reason": moderation_data.reason,
                    "entity_id": entity_id
                }
            }
        )
        
        return {
            "message": f"Contribution {moderation_data.action}d successfully",
            "entity_id": entity_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating contribution {contribution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def create_entity_from_contribution(contribution: dict) -> str:
    """Create an entity in the appropriate collection from an approved contribution"""
    try:
        entity_type = contribution["entity_type"]
        entity_data = contribution["data"]
        entity_id = str(uuid.uuid4())
        
        # Prepare common fields
        entity = {
            "id": entity_id,
            "created_at": datetime.utcnow(),
            "created_from_contribution": contribution["id"],
            "topkit_reference": f"TK-{entity_type.upper()}-{uuid.uuid4().hex[:6].upper()}"
        }
        
        # Add entity-specific data
        if entity_type == "team":
            # Process logo_url - copy from contributions to teams directory if needed
            logo_url = entity_data.get("logo_url", "")
            if logo_url and logo_url.startswith("image_uploaded_"):
                # Find the actual uploaded file in contributions directory
                contribution_files = list(Path(UPLOAD_DIR / "contributions").glob("*.jpg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.jpeg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.png"))
                
                # Find the most recent file (likely the uploaded logo)
                if contribution_files:
                    latest_file = max(contribution_files, key=lambda p: p.stat().st_mtime)
                    
                    # Copy to teams directory with the expected legacy name
                    teams_dir = UPLOAD_DIR / "teams"
                    teams_dir.mkdir(exist_ok=True)
                    
                    # Determine file extension from the source file
                    file_ext = latest_file.suffix
                    destination = teams_dir / f"{logo_url}{file_ext}"
                    
                    try:
                        shutil.copy2(latest_file, destination)
                        logger.info(f"Copied team logo from {latest_file} to {destination}")
                    except Exception as e:
                        logger.error(f"Failed to copy team logo: {str(e)}")
            
            entity.update({
                "name": entity_data.get("name", ""),
                "short_name": entity_data.get("short_name", ""),
                "country": entity_data.get("country", ""),
                "city": entity_data.get("city", ""),
                "founded_year": entity_data.get("founded_year", 0),
                "colors": entity_data.get("colors", []),
                "logo_url": logo_url,
                "secondary_photos": entity_data.get("secondary_photos", "")
            })
            await db.teams.insert_one(entity)
            
        elif entity_type == "brand":
            # Process logo_url - copy from contributions to brands directory if needed
            logo_url = entity_data.get("logo_url", "")
            if logo_url and logo_url.startswith("image_uploaded_"):
                # Find the actual uploaded file in contributions directory
                contribution_files = list(Path(UPLOAD_DIR / "contributions").glob("*.jpg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.jpeg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.png"))
                
                # Find the most recent file (likely the uploaded logo)
                if contribution_files:
                    latest_file = max(contribution_files, key=lambda p: p.stat().st_mtime)
                    
                    # Copy to brands directory with the expected legacy name
                    brands_dir = UPLOAD_DIR / "brands"
                    brands_dir.mkdir(exist_ok=True)
                    
                    # Determine file extension from the source file
                    file_ext = latest_file.suffix
                    destination = brands_dir / f"{logo_url}{file_ext}"
                    
                    try:
                        shutil.copy2(latest_file, destination)
                        logger.info(f"Copied brand logo from {latest_file} to {destination}")
                    except Exception as e:
                        logger.error(f"Failed to copy brand logo: {str(e)}")
            
            entity.update({
                "name": entity_data.get("name", ""),
                "country": entity_data.get("country", ""),
                "founded_year": entity_data.get("founded_year", 0),
                "logo_url": logo_url,
                "description": entity_data.get("description", "")
            })
            await db.brands.insert_one(entity)
            
        elif entity_type == "player":
            # Process photo_url - copy from contributions to players directory if needed
            photo_url = entity_data.get("photo_url", "")
            if photo_url and photo_url.startswith("image_uploaded_"):
                # Find the actual uploaded file in contributions directory
                contribution_files = list(Path(UPLOAD_DIR / "contributions").glob("*.jpg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.jpeg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.png"))
                
                # Find the most recent file (likely the uploaded photo)
                if contribution_files:
                    latest_file = max(contribution_files, key=lambda p: p.stat().st_mtime)
                    
                    # Copy to players directory with the expected legacy name
                    players_dir = UPLOAD_DIR / "players"
                    players_dir.mkdir(exist_ok=True)
                    
                    # Determine file extension from the source file
                    file_ext = latest_file.suffix
                    destination = players_dir / f"{photo_url}{file_ext}"
                    
                    try:
                        shutil.copy2(latest_file, destination)
                        logger.info(f"Copied player photo from {latest_file} to {destination}")
                    except Exception as e:
                        logger.error(f"Failed to copy player photo: {str(e)}")
            
            entity.update({
                "name": entity_data.get("name", ""),
                "nationality": entity_data.get("nationality", ""),
                "position": entity_data.get("position", ""),
                "birth_date": entity_data.get("birth_date", ""),
                "photo_url": photo_url
            })
            await db.players.insert_one(entity)
            
        elif entity_type == "competition":
            # Process logo_url - copy from contributions to competitions directory if needed
            logo_url = entity_data.get("logo_url", "")
            if logo_url and logo_url.startswith("image_uploaded_"):
                # Find the actual uploaded file in contributions directory
                contribution_files = list(Path(UPLOAD_DIR / "contributions").glob("*.jpg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.jpeg")) + \
                                   list(Path(UPLOAD_DIR / "contributions").glob("*.png"))
                
                # Find the most recent file (likely the uploaded logo)
                if contribution_files:
                    latest_file = max(contribution_files, key=lambda p: p.stat().st_mtime)
                    
                    # Copy to competitions directory with the expected legacy name
                    competitions_dir = UPLOAD_DIR / "competitions"
                    competitions_dir.mkdir(exist_ok=True)
                    
                    # Determine file extension from the source file
                    file_ext = latest_file.suffix
                    destination = competitions_dir / f"{logo_url}{file_ext}"
                    
                    try:
                        shutil.copy2(latest_file, destination)
                        logger.info(f"Copied competition logo from {latest_file} to {destination}")
                    except Exception as e:
                        logger.error(f"Failed to copy competition logo: {str(e)}")
            
            entity.update({
                "name": entity_data.get("name", ""),
                "competition_name": entity_data.get("competition_name", entity_data.get("name", "")),
                "country": entity_data.get("country", ""),
                "level": entity_data.get("level", ""),
                "format": entity_data.get("format", ""),
                "logo_url": logo_url
            })
            await db.competitions.insert_one(entity)
        
        elif entity_type == "master_kit":
            entity.update({
                "club_id": entity_data.get("club_id", ""),
                "season": entity_data.get("season", ""),
                "kit_type": entity_data.get("kit_type", ""),
                "competition_id": entity_data.get("competition_id", ""),
                "model": entity_data.get("model", ""),
                "brand_id": entity_data.get("brand_id", ""),
                "sku_code": entity_data.get("sku_code", ""),
                "main_sponsor_id": entity_data.get("main_sponsor_id", ""),
                "gender": entity_data.get("gender", ""),
                "primary_color": entity_data.get("primary_color", ""),
                "secondary_colors": entity_data.get("secondary_colors", []),
                "pattern_description": entity_data.get("pattern_description", ""),
                "front_photo_url": entity_data.get("front_photo_url", ""),
                "total_collectors": 0,
                "created_by": contribution.get("created_by", ""),
                "verified_level": "unverified",
                "verified_at": None,
                "verified_by": None,
                "modification_count": 0,
                "last_modified_at": None,
                "last_modified_by": None
            })
            # Generate proper master kit topkit reference
            entity["topkit_reference"] = f"TK-MASTER-{uuid.uuid4().hex[:6].upper()}"
            await db.master_kits.insert_one(entity)
        
        # Create gamification contribution entry for XP awarding (CRITICAL FIX)
        try:
            contribution_id = await create_contribution_entry(
                user_id=contribution.get("created_by"),
                item_type=entity_type,  # team, brand, player, competition, or master_kit
                item_id=entity_id
            )
            logger.info(f"Created gamification contribution entry: {contribution_id} for {entity_type}: {entity_id}")
        except Exception as contrib_error:
            logger.warning(f"Failed to create gamification contribution entry: {str(contrib_error)}")
        
        logger.info(f"Created {entity_type} entity {entity_id} from contribution {contribution['id']}")
        return entity_id
        
    except Exception as e:
        logger.error(f"Error creating entity from contribution: {str(e)}")
        return None

async def create_or_update_entity_from_contribution(contribution: dict) -> str:
    """Create or update an entity in the appropriate collection from an approved contribution"""
    try:
        entity_type = contribution["entity_type"]
        entity_data = contribution["data"]
        
        # Check if this is an update (entity_id provided) or a new creation
        existing_entity_id = contribution.get("entity_id")
        
        if existing_entity_id:
            # Update existing entity
            logger.info(f"Updating existing {entity_type} entity {existing_entity_id} from contribution {contribution['id']}")
            
            # Prepare update fields
            update_fields = {
                "last_modified_at": datetime.utcnow(),
                "last_modified_by": contribution.get("created_by", "")
                # modification_count will be handled with $inc separately
            }
            
            # Add only provided/changed entity-specific data to update fields
            if entity_type == "team":
                # Only update fields that are explicitly provided in the contribution
                team_fields = ["name", "short_name", "country", "city", "founded_year", "colors", "logo_url", "secondary_photos"]
                for field in team_fields:
                    if field in entity_data:
                        update_fields[field] = entity_data[field]
                
                logger.info(f"Updating team {existing_entity_id} with fields: {list(update_fields.keys())}")
                
                # Update the entity
                result = await db.teams.update_one(
                    {"id": existing_entity_id},
                    {"$set": update_fields, "$inc": {"modification_count": 1}}
                )
                
            elif entity_type == "brand":
                # Only update fields that are explicitly provided in the contribution
                brand_fields = ["name", "country", "founded_year", "logo_url", "description"]
                for field in brand_fields:
                    if field in entity_data:
                        update_fields[field] = entity_data[field]
                
                logger.info(f"Updating brand {existing_entity_id} with fields: {list(update_fields.keys())}")
                
                result = await db.brands.update_one(
                    {"id": existing_entity_id},
                    {"$set": update_fields, "$inc": {"modification_count": 1}}
                )
                
            elif entity_type == "player":
                # Only update fields that are explicitly provided in the contribution
                player_fields = ["name", "nationality", "position", "birth_date", "photo_url"]
                for field in player_fields:
                    if field in entity_data:
                        update_fields[field] = entity_data[field]
                
                logger.info(f"Updating player {existing_entity_id} with fields: {list(update_fields.keys())}")
                
                result = await db.players.update_one(
                    {"id": existing_entity_id},
                    {"$set": update_fields, "$inc": {"modification_count": 1}}
                )
                
            elif entity_type == "competition":
                # Only update fields that are explicitly provided in the contribution
                competition_fields = ["name", "competition_name", "country", "level", "format", "logo_url"]
                for field in competition_fields:
                    if field in entity_data:
                        update_fields[field] = entity_data[field]
                    # Special handling for competition_name fallback
                    elif field == "competition_name" and "name" in entity_data:
                        update_fields["competition_name"] = entity_data["name"]
                
                logger.info(f"Updating competition {existing_entity_id} with fields: {list(update_fields.keys())}")
                
                result = await db.competitions.update_one(
                    {"id": existing_entity_id},
                    {"$set": update_fields, "$inc": {"modification_count": 1}}
                )
                
            elif entity_type == "master_kit":
                # Only update fields that are explicitly provided in the contribution
                master_kit_fields = [
                    "club_id", "season", "kit_type", "competition_id", "model", "brand_id", 
                    "sku_code", "main_sponsor_id", "gender", "primary_color", "secondary_colors", 
                    "pattern_description", "front_photo_url"
                ]
                for field in master_kit_fields:
                    if field in entity_data:
                        update_fields[field] = entity_data[field]
                
                logger.info(f"Updating master_kit {existing_entity_id} with fields: {list(update_fields.keys())}")
                
                result = await db.master_kits.update_one(
                    {"id": existing_entity_id},
                    {"$set": update_fields, "$inc": {"modification_count": 1}}
                )
            
            if result.modified_count > 0:
                logger.info(f"Successfully updated {entity_type} entity {existing_entity_id}")
                
                # Trigger cascading updates for related entities
                await trigger_cascading_updates(entity_type, existing_entity_id, update_fields)
                
                return existing_entity_id
            else:
                logger.warning(f"No changes made to {entity_type} entity {existing_entity_id}")
                return existing_entity_id
                
        else:
            # Create new entity - delegate to existing function
            logger.info(f"Creating new {entity_type} entity from contribution {contribution['id']}")
            return await create_entity_from_contribution(contribution)
            
    except Exception as e:
        logger.error(f"Error creating or updating entity from contribution: {str(e)}")
        return None

async def transfer_contribution_images_to_entity(contribution: dict, entity_id: str) -> bool:
    """Transfer images from contribution to the actual entity when approved"""
    try:
        entity_type = contribution["entity_type"]
        contribution_id = contribution["id"]
        
        # Find all images associated with this contribution
        contribution_images = []
        
        # Check for uploaded images stored in contribution document
        if "uploaded_images" in contribution:
            for img_info in contribution["uploaded_images"]:
                field_name = img_info.get("field_name", "logo")
                file_path = img_info.get("file_path", "")
                if file_path:
                    contribution_images.append((field_name, file_path))
        
        # Also check if contribution has images in data (legacy format)
        if "images" in contribution.get("data", {}):
            images_data = contribution["data"]["images"]
            if isinstance(images_data, dict):
                for field_name, image_path in images_data.items():
                    if image_path and isinstance(image_path, str):
                        contribution_images.append((field_name, image_path))
        
        # CRITICAL FIX: Check for image fields directly in contribution data
        # This handles the case where front_photo_url, logo_url, etc. are set in the contribution data
        data = contribution.get("data", {})
        image_fields = ["front_photo_url", "logo_url", "photo_url"]
        
        for field in image_fields:
            if field in data and data[field] and isinstance(data[field], str):
                if data[field].startswith("image_uploaded_"):
                    contribution_images.append((field, data[field]))
                    logger.info(f"Found image field {field} in contribution data: {data[field]}")
        
        if not contribution_images:
            logger.info(f"No images found for contribution {contribution_id}")
            return True
        
        # Determine target folder based on entity type
        target_folder_map = {
            "team": "teams",
            "brand": "brands", 
            "player": "players",
            "competition": "competitions",
            "master_kit": "master_kits"
        }
        
        target_folder = target_folder_map.get(entity_type)
        if not target_folder:
            logger.warning(f"Unknown entity type for image transfer: {entity_type}")
            return False
        
        # Create target directory if it doesn't exist
        target_dir = f"/app/backend/uploads/{target_folder}"
        os.makedirs(target_dir, exist_ok=True)
        
        # Transfer images and update entity
        transferred_files = []
        
        # Get current entity to check existing logo_url
        collection_map = {
            "team": db.teams,
            "brand": db.brands,
            "player": db.players, 
            "competition": db.competitions,
            "master_kit": db.master_kits
        }
        
        collection = collection_map.get(entity_type)
        if collection is None:
            logger.warning(f"Unknown entity type for image transfer: {entity_type}")
            return False
            
        current_entity = await collection.find_one({"id": entity_id})
        if not current_entity:
            logger.warning(f"Entity {entity_id} not found for image transfer")
            return False
        
        for field_name, source_path in contribution_images:
            try:
                # Construct full source path - try multiple locations
                possible_paths = []
                
                if source_path.startswith("/"):
                    possible_paths.append(source_path)
                elif source_path.startswith("uploads/"):
                    possible_paths.append(f"/app/backend/{source_path}")
                elif source_path.startswith("contributions/"):
                    possible_paths.append(f"/app/backend/uploads/{source_path}")
                else:
                    # Try multiple possible locations for the image file
                    possible_paths.extend([
                        f"/app/backend/uploads/contributions/{source_path}",
                        f"/app/backend/uploads/contributions/{source_path}.png",
                        f"/app/backend/uploads/contributions/{source_path}.jpg",
                        f"/app/backend/uploads/contributions/{source_path}.jpeg"
                    ])
                
                # Find the first existing file
                full_source_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        full_source_path = path
                        break
                
                if not full_source_path:
                    logger.warning(f"Source image file not found in any of these locations: {possible_paths}")
                    continue
                
                # Get the legacy filename from the entity's current field or use the field name directly
                legacy_filename = None
                
                # First, try to get the existing filename from the entity
                if field_name in ["logo", "logo_url", "uploaded_file"] or field_name.endswith("_logo"):
                    legacy_filename = current_entity.get("logo_url", "")
                elif field_name in ["photo", "photo_url", "primary_photo", "front_photo", "front_photo_url"]:
                    if entity_type == "player":
                        legacy_filename = current_entity.get("photo_url", "")
                    elif entity_type == "master_kit":
                        legacy_filename = current_entity.get("front_photo_url", "")
                
                # If no existing filename or it doesn't start with image_uploaded_, use the source_path as filename
                if not legacy_filename or not legacy_filename.startswith("image_uploaded_"):
                    # Use the source filename (which should be the image_uploaded_ value)
                    if source_path.startswith("image_uploaded_"):
                        legacy_filename = source_path
                    else:
                        # Extract filename from path
                        legacy_filename = os.path.basename(source_path)
                        if not legacy_filename.startswith("image_uploaded_"):
                            logger.warning(f"Could not determine legacy filename for {field_name} in entity {entity_id}, using {legacy_filename}")
                
                logger.info(f"Using legacy filename: {legacy_filename} for field {field_name}")
                
                # Determine file extension from source file
                file_extension = os.path.splitext(source_path)[1] or '.png'
                target_filename = f"{legacy_filename}{file_extension}"
                target_path = f"{target_dir}/{target_filename}"
                
                # Copy file to entity folder with legacy filename
                import shutil
                shutil.copy2(full_source_path, target_path)
                transferred_files.append(target_path)
                
                logger.info(f"Transferred image {source_path} -> {target_folder}/{target_filename} for entity {entity_id}")
                
            except Exception as e:
                logger.error(f"Error transferring image {source_path}: {str(e)}")
                continue
        
        # No need to update entity URLs since they're already set correctly
        return len(transferred_files) > 0
        
    except Exception as e:
        logger.error(f"Error transferring contribution images to entity: {str(e)}")
        return False

# ================================
# PRICE ESTIMATION SYSTEM
# ================================

def calculate_estimated_price(master_kit: dict, collection_item: dict = None) -> float:
    """
    Calculate estimated price for a Master Kit with optional personal details
    
    TOPKIT Jersey Price Estimation Coefficients (Updated):
    Base Price: Authentic (€140), Replica (€90)
    
    Coefficients:
    - Condition:
      * Club Stock: +1.2
      * Match Prepared: +0.8
      * Match Worn: +1.5
      * Training: +0.2
    - Physical State:
      * New with tags: +0.3
      * Very good: +0.15
      * Used: 0
      * Damaged: -0.25
      * Needs restoration: -0.4
    - Flocking:
      * Official name flocking: +0.15
      * Official number flocking: +0.1
      * Full flocking (name + number): +0.2
    - Additional Features:
      * Competition patches: +0.15
      * Signed by a famous player: +1.0
      * Age: +0.03 per year (max +0.6)
    
    Formula: Estimated Price = Base Price × (1 + sum of coefficients)
    """
    try:
        # Base price from kit model
        base_price = 140.0 if master_kit.get('model') == 'authentic' else 90.0
        
        # Initialize coefficients
        coefficients = 0.0
        
        # Personal details from collection item (if provided)
        if collection_item:
            # Flocking coefficients (more granular)
            has_name = bool(collection_item.get('name_printing'))
            has_number = bool(collection_item.get('number_printing'))
            
            if has_name and has_number:
                coefficients += 0.2  # Full flocking (name + number)
            elif has_name:
                coefficients += 0.15  # Official name flocking only
            elif has_number:
                coefficients += 0.1   # Official number flocking only
                
            # Competition patches (reduced coefficient)
            if collection_item.get('patches'):
                coefficients += 0.15
                
            # Condition multipliers (new values)
            condition = collection_item.get('condition')
            if condition == 'club_stock':
                coefficients += 1.2
            elif condition == 'match_prepared':
                coefficients += 0.8
            elif condition == 'match_worn':
                coefficients += 1.5
            elif condition == 'training':
                coefficients += 0.2
                
            # Physical State multipliers (new category)
            physical_state = collection_item.get('physical_state')
            if physical_state == 'new_with_tags':
                coefficients += 0.3
            elif physical_state == 'very_good_condition':
                coefficients += 0.15
            elif physical_state == 'used':
                coefficients += 0.0  # No change
            elif physical_state == 'damaged':
                coefficients -= 0.25  # Negative impact
            elif physical_state == 'needs_restoration':
                coefficients -= 0.4   # Significant negative impact
                
            # Signed by a famous player (reduced coefficient)
            if collection_item.get('is_signed') and collection_item.get('signed_by'):
                coefficients += 1.0
        
        # Age calculation from season (reduced coefficient and max)
        season = master_kit.get('season', '')
        if season and '-' in season:
            try:
                # Extract start year from season (e.g., "2015-2016" -> 2015)
                start_year = int(season.split('-')[0])
                current_year = 2025  # Current year
                age_years = current_year - start_year
                age_coefficient = min(age_years * 0.03, 0.6)  # Max +0.6
                coefficients += age_coefficient
            except (ValueError, IndexError):
                pass  # Skip age calculation if season format is invalid
        
        # Calculate final price (ensure minimum doesn't go below 50% of base price for damaged items)
        estimated_price = base_price * (1 + coefficients)
        min_price = base_price * 0.5  # Minimum 50% of base price
        estimated_price = max(estimated_price, min_price)
        
        return round(estimated_price, 2)
        
    except Exception as e:
        logger.error(f"Error calculating estimated price: {str(e)}")
        return 0.0

@app.get("/api/price-estimation/{master_kit_id}")
async def get_price_estimation(master_kit_id: str):
    """Get price estimation for a Master Kit (basic estimation without personal details)"""
    try:
        master_kit = await db.master_kits.find_one({"id": master_kit_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        estimated_price = calculate_estimated_price(master_kit)
        
        return {
            "master_kit_id": master_kit_id,
            "estimated_price": estimated_price,
            "base_price": 140.0 if master_kit.get('model') == 'authentic' else 90.0,
            "model": master_kit.get('model'),
            "calculation_details": {
                "base_price": 140.0 if master_kit.get('model') == 'authentic' else 90.0,
                "coefficients_applied": "Basic estimation without personal details",
                "formula": "Base Price × (1 + age coefficient)"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in price estimation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/my-collection/{collection_id}/price-estimation")
async def get_collection_item_price_estimation(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed price estimation for a specific collection item with personal details"""
    try:
        # Find collection item
        collection_item = await db.my_collection.find_one({
            "id": collection_id,
            "user_id": current_user["id"]
        })
        if not collection_item:
            raise HTTPException(status_code=404, detail="Collection item not found")
        
        # Get master kit
        master_kit = await db.master_kits.find_one({"id": collection_item["master_kit_id"]})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        # Calculate detailed price with personal details
        estimated_price = calculate_estimated_price(master_kit, collection_item)
        
        # Build detailed breakdown
        base_price = 140.0 if master_kit.get('model') == 'authentic' else 90.0
        coefficients = []
        
        # Flocking breakdown (more granular)
        has_name = bool(collection_item.get('name_printing'))
        has_number = bool(collection_item.get('number_printing'))
        
        if has_name and has_number:
            coefficients.append({"factor": "Full flocking (name + number)", "value": "+0.2"})
        elif has_name:
            coefficients.append({"factor": "Official name flocking", "value": "+0.15"})
        elif has_number:
            coefficients.append({"factor": "Official number flocking", "value": "+0.1"})
        
        if collection_item.get('patches'):
            coefficients.append({"factor": "Competition patches", "value": "+0.15"})
        
        # Condition coefficients (updated)
        condition = collection_item.get('condition')
        if condition == 'club_stock':
            coefficients.append({"factor": "Club Stock condition", "value": "+1.2"})
        elif condition == 'match_prepared':
            coefficients.append({"factor": "Match Prepared condition", "value": "+0.8"})
        elif condition == 'match_worn':
            coefficients.append({"factor": "Match Worn condition", "value": "+1.5"})
        elif condition == 'training':
            coefficients.append({"factor": "Training condition", "value": "+0.2"})
        
        # Physical State coefficients (new)
        physical_state = collection_item.get('physical_state')
        if physical_state == 'new_with_tags':
            coefficients.append({"factor": "New with tags", "value": "+0.3"})
        elif physical_state == 'very_good_condition':
            coefficients.append({"factor": "Very good condition", "value": "+0.15"})
        elif physical_state == 'used':
            coefficients.append({"factor": "Used condition", "value": "0"})
        elif physical_state == 'damaged':
            coefficients.append({"factor": "Damaged condition", "value": "-0.25"})
        elif physical_state == 'needs_restoration':
            coefficients.append({"factor": "Needs restoration", "value": "-0.4"})
        
        if collection_item.get('is_signed') and collection_item.get('signed_by'):
            coefficients.append({"factor": f"Signed by {collection_item['signed_by']}", "value": "+1.0"})
        
        # Age coefficient (updated)
        season = master_kit.get('season', '')
        if season and '-' in season:
            try:
                start_year = int(season.split('-')[0])
                age_years = 2025 - start_year
                age_coefficient = min(age_years * 0.03, 0.6)
                coefficients.append({"factor": f"Age ({age_years} years)", "value": f"+{age_coefficient:.2f}"})
            except:
                pass
        
        return {
            "collection_id": collection_id,
            "master_kit_id": collection_item["master_kit_id"],
            "estimated_price": estimated_price,
            "base_price": base_price,
            "model": master_kit.get('model'),
            "calculation_details": {
                "base_price": base_price,
                "coefficients_applied": coefficients,
                "formula": f"€{base_price} × (1 + coefficients) = €{estimated_price}",
                "master_kit_details": {
                    "club": master_kit.get('club'),
                    "season": master_kit.get('season'),
                    "kit_type": master_kit.get('kit_type'),
                    "model": master_kit.get('model')
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in collection item price estimation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# HOMEPAGE & PUBLIC PROFILES ENDPOINTS
# ================================

@app.get("/api/homepage/expensive-kits")
async def get_expensive_kits(limit: int = Query(5, le=10)):
    """Get the most expensive kits from public collections for homepage"""
    try:
        # First, we need to add a way to determine if a collection is public
        # For now, let's get all collections and sort by estimated price
        
        # Get all collection items with their master kit info
        cursor = db.my_collection.find({})
        collection_items = await cursor.to_list(length=None)
        
        expensive_items = []
        
        for item in collection_items:
            # Get master kit info
            master_kit = await db.master_kits.find_one({"id": item["master_kit_id"]})
            if not master_kit:
                continue
                
            # Remove MongoDB ObjectId to prevent serialization issues
            if "_id" in master_kit:
                del master_kit["_id"]
                
            # Get user info
            user = await db.users.find_one({"id": item["user_id"]})
            if not user:
                continue
                
            # For now, consider all collections as public
            # In the future, add a "is_public_collection" field to users
            
            # Calculate estimated price
            estimated_price = calculate_estimated_price(master_kit, item)
            
            expensive_items.append({
                "collection_id": item["id"],
                "master_kit_id": item["master_kit_id"],
                "estimated_price": estimated_price,
                "master_kit": master_kit,
                "user": {
                    "id": user["id"],
                    "name": user["name"]
                }
            })
        
        # Sort by estimated price (descending) and take top items
        expensive_items.sort(key=lambda x: x["estimated_price"], reverse=True)
        return expensive_items[:limit]
        
    except Exception as e:
        logger.error(f"Error fetching expensive kits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/homepage/recent-master-kits")
async def get_recent_master_kits(limit: int = Query(6, le=20)):
    """Get recently uploaded master kits for homepage 'Latest database contributions' section"""
    try:
        cursor = db.master_kits.find({}).sort("created_at", -1).limit(limit)
        master_kits = await cursor.to_list(length=None)
        
        # Remove MongoDB _id field
        for kit in master_kits:
            if "_id" in kit:
                del kit["_id"]
                
        return master_kits
        
    except Exception as e:
        logger.error(f"Error fetching recent master kits: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/homepage/recent-contributions")
async def get_recent_contributions(limit: int = Query(10, le=20)):
    """Get recently approved contributions (teams, brands, players, competitions) for homepage 'Latest documentation' section"""
    try:
        # Get recent contributions from the gamification contributions table
        cursor = db.contributions_gamification.find({
            "is_approved": True,
            "item_type": {"$in": ["team", "brand", "player", "competition"]}
        }).sort("approved_at", -1).limit(limit)
        
        contributions = await cursor.to_list(length=None)
        
        result = []
        for contrib in contributions:
            # Get the actual entity data
            collection_name = f"{contrib['item_type']}s"  # teams, brands, players, competitions
            entity = await db[collection_name].find_one({"id": contrib["item_id"]})
            
            if entity:
                # Remove MongoDB ObjectId to prevent serialization issues
                if "_id" in entity:
                    del entity["_id"]
                    
                # Get user info
                user = await db.users.find_one({"id": contrib["user_id"]})
                
                result.append({
                    "contribution_id": contrib["id"],
                    "item_type": contrib["item_type"], 
                    "item_id": contrib["item_id"],
                    "entity": entity,
                    "user": {"id": user["id"], "name": user["name"]} if user else None,
                    "approved_at": contrib.get("approved_at"),
                    "xp_awarded": contrib.get("xp_awarded", 0)
                })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching recent contributions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/public-profile")
async def get_user_public_profile(
    user_id: str, 
    current_user: dict = Depends(get_current_user)  # Require login
):
    """Get public profile of another user (only for logged-in users)"""
    try:
        # Check if requesting user is logged in
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Find the target user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check privacy settings
        if user.get("profile_private", False) and user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="This profile is private")
        
        # Get user statistics
        collections_count = await db.my_collection.count_documents({"user_id": user_id})
        contributions_count = await db.contributions_gamification.count_documents({"user_id": user_id})
        
        return {
            "id": user["id"],
            "name": user["name"],
            "created_at": user.get("created_at"),
            "role": user.get("role", "user"),
            "xp": user.get("xp", 0),
            "level": user.get("level", "Remplaçant"),
            "collections_count": collections_count,
            "contributions_count": contributions_count,
            "profile_picture_url": user.get("profile_picture_url"),
            "bio": user.get("bio"),
            "favorite_club": user.get("favorite_club"),
            "instagram_username": user.get("instagram_username"),
            "twitter_username": user.get("twitter_username"),
            "website": user.get("website")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user public profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ================================
# STATS ENDPOINT
# ================================

@app.get("/api/stats")
async def get_stats():
    """Get statistics for the application - WITH COMPATIBILITY TEST"""
    return {
        "master_kits": 999,  # TEST VALUE TO VERIFY BACKEND UPDATE
        "collections": 888,  # TEST VALUE
        "users": 777,        # TEST VALUE
        "system": "BACKEND_UPDATE_TEST_SUCCESS",
        "backwards_compatibility": "TESTING"
    }

# ================================
# HEALTH CHECK
# ================================

@app.get("/")
async def root():
    return {
        "message": "TopKit API - Simplified 2-Type System",
        "version": "2.0.0",
        "system": "Master Kit + My Collection",
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "timestamp": "2025-09-13",
        "backend_update_test": "SUCCESS - CODE IS LOADING"
    }

@app.get("/api/master-jerseys/{jersey_id}")
async def master_jersey_compat(jersey_id: str):
    """Backward compatibility for master-jerseys"""
    try:
        master_kit = await db.master_kits.find_one({"id": jersey_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
        if "_id" in master_kit:
            del master_kit["_id"]
            
        return master_kit
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reference-kits")
async def reference_kits_compat():
    """Backward compatibility for reference-kits"""
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)