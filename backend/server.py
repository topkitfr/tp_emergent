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
from datetime import datetime, timezone
from pathlib import Path
import uuid
import asyncio

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ValidationError
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
    User, UserResponse
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
db = client.topkit_db

# Security
SECRET_KEY = "topkit_secret_key_2024"
ALGORITHM = "HS256"
security = HTTPBearer()
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
            # Create a contribution entry for the Master Kit creation
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
                    
                # Set club_name from club field if using old format
                if "club" in kit and not kit.get("club_name"):
                    kit["club_name"] = kit["club"]
                    
                # Set competition_name from competition field if using old format
                if "competition" in kit and not kit.get("competition_name"):
                    kit["competition_name"] = kit["competition"]
                    
                # Set brand_name from brand field if using old format
                if "brand" in kit and not kit.get("brand_name"):
                    kit["brand_name"] = kit["brand"]
                    
                # Set main_sponsor_name from main_sponsor field if using old format
                if "main_sponsor" in kit and not kit.get("main_sponsor_name"):
                    kit["main_sponsor_name"] = kit["main_sponsor"]
                    
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
    """Get specific Master Kit by ID"""
    try:
        master_kit = await db.master_kits.find_one({"id": master_kit_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master Kit not found")
        
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
    """Search Master Kits by club, season, brand, etc."""
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
        
        return [MasterKitResponse(**kit) for kit in master_kits]
        
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
        existing = await db.my_collection.find_one({
            "user_id": current_user["id"],
            "master_kit_id": collection_data.master_kit_id,
            "collection_type": collection_data.collection_type
        })
        if existing:
            collection_type_name = "owned collection" if collection_data.collection_type == "owned" else "want list"
            raise HTTPException(status_code=400, detail=f"Master Kit already in your {collection_type_name}")
        
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

# ================================
# BASIC AUTH ENDPOINTS (placeholder)
# ================================

class LoginRequest(BaseModel):
    email: str
    password: str

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
        
        # Verify password (simplified - would use proper hashing in production)
        if user.get("password") != login_data.password:  # TODO: Use proper password hashing
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
# STATS ENDPOINT
# ================================

@app.get("/api/stats")
async def get_stats():
    """Get basic stats for the new system"""
    try:
        total_master_kits = await db.master_kits.count_documents({})
        total_collections = await db.my_collection.count_documents({})
        total_users = await db.users.count_documents({})
        
        return {
            "master_kits": total_master_kits,
            "collections": total_collections,
            "users": total_users,
            "system": "simplified_2_type"
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)