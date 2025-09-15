"""
New Simplified TopKit Models - 2-Type System
1. Master Kit = Official jersey reference (like a product listing)
2. My Collection = Master Kits that I own with personal details

NO Reference Kit or separate Personal Kit entities.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid
from enum import Enum

class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"

class VerificationLevel(str, Enum):
    UNVERIFIED = "unverified"
    COMMUNITY_VERIFIED = "community_verified"
    EXPERT_VERIFIED = "expert_verified"
    OFFICIAL = "official"

class EntityType(str, Enum):
    TEAM = "team"
    BRAND = "brand" 
    PLAYER = "player"
    COMPETITION = "competition"
    MASTER_KIT = "master_kit"  # Only Master Kit now, no reference/personal separation

# ================================
# NEW SIMPLIFIED KIT SYSTEM
# ================================

class KitType(str, Enum):
    HOME = "home"
    AWAY = "away"
    THIRD = "third"
    FOURTH = "fourth"
    GK = "gk"
    SPECIAL = "special"

class KitModel(str, Enum):
    AUTHENTIC = "authentic"
    REPLICA = "replica"

class Gender(str, Enum):
    MAN = "man"
    WOMAN = "woman"
    CHILD = "child"

class KitCondition(str, Enum):
    CLUB_STOCK = "club_stock"
    MATCH_PREPARED = "match_prepared"
    MATCH_WORN = "match_worn"
    TRAINING = "training"
    OTHER = "other"

class PhysicalState(str, Enum):
    NEW_WITH_TAGS = "new_with_tags"
    VERY_GOOD_CONDITION = "very_good_condition"
    USED = "used"
    DAMAGED = "damaged"
    NEEDS_RESTORATION = "needs_restoration"

# ================================
# MASTER KIT - OFFICIAL REFERENCE
# ================================

class MasterKit(BaseModel):
    """Master Kit = Official jersey reference (like a product listing)
    Created once per jersey design, contains standard info, shared by all users"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # ALL FIELDS REQUIRED - as specified
    club_id: str  # Reference to club in database *
    season: str  # e.g., "2024-2025" (YEAR-YEAR format) *
    kit_type: KitType  # Home/Away/Third/Fourth/GK/Special *
    competition_id: str  # Reference to competition in database *
    model: KitModel  # Authentic/Replica *
    brand_id: str  # Reference to brand in database *
    sku_code: Optional[str] = None  # Product SKU or catalog code
    main_sponsor_id: Optional[str] = None  # Reference to sponsor/brand in database
    gender: Gender  # Man/Woman/Child *
    primary_color: str  # Primary color *
    secondary_colors: List[str] = []  # Secondary colors with add/remove functionality
    front_photo_url: Optional[str] = None  # Upload required (minimum 800x600px) *
    
    # Optional additional info
    pattern_description: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User ID
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    topkit_reference: str  # TK-MASTER-000001
    
    # Statistics - how many users have this in their collection
    total_collectors: int = 0

class MasterKitCreate(BaseModel):
    """Creation model for Master Kit - ALL FIELDS REQUIRED"""
    club_id: str = Field(..., min_length=1, description="Club ID is required")
    season: str = Field(..., min_length=1, description="Season is required (YEAR-YEAR format)")
    kit_type: KitType = Field(..., description="Kit type is required")
    competition_id: str = Field(..., min_length=1, description="Competition ID is required")
    model: KitModel = Field(..., description="Model is required")
    brand_id: str = Field(..., min_length=1, description="Brand ID is required")
    sku_code: Optional[str] = None  # Optional product SKU or catalog code
    main_sponsor_id: Optional[str] = None  # Optional sponsor
    gender: Gender = Field(..., description="Gender is required")
    primary_color: str = Field(..., min_length=1, description="Primary color is required")
    secondary_colors: List[str] = []
    
    # Optional fields
    pattern_description: Optional[str] = None

    @validator('season')
    def validate_season_format(cls, v):
        """Validate season format is YEAR-YEAR"""
        import re
        if not re.match(r'^\d{4}-\d{4}$', v):
            raise ValueError('Season must be in YEAR-YEAR format (e.g., 2024-2025)')
        return v

class CollectionType(str, Enum):
    OWNED = "owned"
    WANTED = "wanted"

# ================================
# MY COLLECTION - MASTER KIT + PERSONAL DETAILS
# ================================

class MyCollection(BaseModel):
    """My Collection = Master Kits that I own/want with personal details
    When I add a Master Kit to my collection, it keeps all Master Kit info + my personal details"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Link to Master Kit (REQUIRED)
    master_kit_id: str = Field(..., description="Master Kit ID is required")
    user_id: str = Field(..., description="User ID is required")
    
    # Collection Type (REQUIRED)
    collection_type: CollectionType = Field(..., description="Collection type (owned/wanted)")
    
    # Personal Kit Form Fields (as specified) - mostly for owned items
    name_printing: Optional[str] = None  # e.g., "Mbappé"
    number_printing: Optional[str] = None  # e.g., "7"
    patches: Optional[str] = None  # dropdown: Ligue 1/Champions League/etc.
    
    # Signed section
    is_signed: bool = False
    signed_by: Optional[str] = None  # Player name(s)
    certificate_url: Optional[str] = None  # Certificate upload
    
    # Condition
    condition: Optional[KitCondition] = None
    condition_other: Optional[str] = None  # Free text if "Other" selected
    
    # Physical State
    physical_state: Optional[PhysicalState] = None  
    
    # Size and Purchase Info
    size: Optional[str] = None  # S/M/L/XL/etc.
    purchase_price: Optional[float] = None  # €
    purchase_date: Optional[datetime] = None  # DD/MM/YYYY
    proof_of_purchase_url: Optional[str] = None  # File upload
    personal_notes: Optional[str] = None  # Free text
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class MyCollectionCreate(BaseModel):
    """Creation model for adding Master Kit to My Collection"""
    master_kit_id: str = Field(..., description="Master Kit ID is required")
    collection_type: CollectionType = Field(..., description="Collection type (owned/wanted)")
    
    # All personal fields are optional when adding to collection
    name_printing: Optional[str] = None
    number_printing: Optional[str] = None
    patches: Optional[str] = None
    is_signed: bool = False
    signed_by: Optional[str] = None
    condition: Optional[KitCondition] = None
    condition_other: Optional[str] = None
    physical_state: Optional[PhysicalState] = None
    size: Optional[str] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    personal_notes: Optional[str] = None

class MyCollectionUpdate(BaseModel):
    """Update model for personal details in My Collection"""
    name_printing: Optional[str] = None
    number_printing: Optional[str] = None
    patches: Optional[str] = None
    is_signed: Optional[bool] = None
    signed_by: Optional[str] = None
    condition: Optional[KitCondition] = None
    condition_other: Optional[str] = None
    physical_state: Optional[PhysicalState] = None
    size: Optional[str] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    personal_notes: Optional[str] = None

# ================================
# RESPONSE MODELS
# ================================

class MasterKitResponse(BaseModel):
    """Response model for Master Kit with all info and populated references"""
    id: str
    
    # Backward compatibility: Support both old (club/competition/brand as strings) and new (IDs) formats
    club_id: Optional[str] = None  # New format
    club: Optional[str] = None  # Old format - for backward compatibility
    club_name: Optional[str] = None  # Populated from club
    
    season: str
    kit_type: Optional[KitType] = None  # Made optional for backward compatibility
    
    competition_id: Optional[str] = None  # New format
    competition: Optional[str] = None  # Old format - for backward compatibility
    competition_name: Optional[str] = None  # Populated from competition
    
    model: KitModel
    
    brand_id: Optional[str] = None  # New format
    brand: Optional[str] = None  # Old format - for backward compatibility
    brand_name: Optional[str] = None  # Populated from brand
    
    sku_code: Optional[str] = None  # Product SKU or catalog code
    
    main_sponsor_id: Optional[str] = None
    main_sponsor: Optional[str] = None  # Old format - for backward compatibility
    main_sponsor_name: Optional[str] = None  # Populated from sponsor
    
    gender: Union[Gender, str]  # Allow old enum values for backward compatibility
    primary_color: Optional[str] = None  # Made optional for backward compatibility
    secondary_colors: List[str] = []
    front_photo_url: Optional[str] = None
    pattern_description: Optional[str] = None
    created_at: datetime
    verified_level: Union[VerificationLevel, str] = "unverified"  # Allow both enum and string for backward compatibility
    topkit_reference: str
    total_collectors: int
    
    class Config:
        # Allow population by field name or alias (Pydantic v2)
        populate_by_name = True

class MyCollectionResponse(BaseModel):
    """Response model for My Collection item (Master Kit + Personal Details)"""
    id: str
    master_kit_id: str
    user_id: str
    collection_type: Optional[str] = "owned"  # Default to "owned" for backward compatibility
    
    # Master Kit info (embedded)
    master_kit: MasterKitResponse
    
    # Personal details
    name_printing: Optional[str]
    number_printing: Optional[str]
    patches: Optional[str]
    is_signed: bool
    signed_by: Optional[str]
    certificate_url: Optional[str]
    condition: Optional[KitCondition]
    condition_other: Optional[str]
    physical_state: Optional[PhysicalState]
    size: Optional[str]
    purchase_price: Optional[float]
    purchase_date: Optional[datetime]
    proof_of_purchase_url: Optional[str]
    personal_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

# ================================
# EXISTING ENTITIES (UNCHANGED)
# ================================

class Team(BaseModel):
    """Team/Club entity - keeping existing structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    short_name: Optional[str] = None
    common_names: List[str] = []
    founded_year: Optional[int] = None
    country: str
    city: Optional[str] = None
    current_competitions: List[str] = []
    primary_competition_id: Optional[str] = None
    competition_history: List[Dict[str, Any]] = []
    logo_url: Optional[str] = None
    colors: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    external_ids: Dict[str, str] = {}
    topkit_reference: str

class Brand(BaseModel):
    """Brand/Manufacturer entity - keeping existing structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    official_name: Optional[str] = None
    common_names: List[str] = []
    country: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    topkit_reference: str

class Player(BaseModel):
    """Player entity - keeping existing structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    full_name: Optional[str] = None
    common_names: List[str] = []
    birth_date: Optional[datetime] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    current_team_id: Optional[str] = None
    team_history: List[Dict[str, Any]] = []
    profile_picture_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    topkit_reference: str

class Competition(BaseModel):
    """Competition entity - keeping existing structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competition_name: str
    short_name: Optional[str] = None
    common_names: List[str] = []
    type: str
    country: Optional[str] = None
    confederations_federations: List[str] = []
    level: Union[str, int]
    current_season: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    topkit_reference: str

# ================================
# CONTRIBUTION SYSTEM (SIMPLIFIED)
# ================================

class ContributionStatusV2(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ContributionSummary(BaseModel):
    """Simplified contribution model"""
    id: str
    title: str
    entity_type: str
    status: ContributionStatusV2
    upvotes: int = 0
    downvotes: int = 0
    images_count: int = 0
    created_at: datetime
    topkit_reference: Optional[str] = None

# ================================
# USER SYSTEM (SIMPLIFIED)
# ================================

class User(BaseModel):
    """User model"""
    id: str
    name: str
    email: str
    role: str = "user"  # "user" or "admin"
    created_at: datetime

class UserResponse(BaseModel):
    """User response model"""
    id: str
    name: str
    email: str
    role: str
    created_at: datetime