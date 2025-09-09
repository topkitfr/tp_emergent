"""
Modèles collaboratifs pour TopKit - Base de données type Discogs
Nouvelles entités pour la vision collaborative
"""
from pydantic import BaseModel, Field
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
    MASTER_JERSEY = "master_jersey"
    JERSEY_RELEASE = "jersey_release"

# ================================
# ENTITÉS PRINCIPALES COLLABORATIVES
# ================================

class Team(BaseModel):
    """Entité Team/Club avec informations détaillées - Updated for interconnected forms"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # "Paris Saint-Germain"
    short_name: Optional[str] = None  # "PSG"
    common_names: List[str] = []  # ["PSG", "Paris SG", "Paris Saint-Germain"]
    
    # Club information with competition references
    founded_year: Optional[int] = None
    country: str  # France
    city: Optional[str] = None  # Paris
    
    # Competition relationships - can reference multiple competitions
    current_competitions: List[str] = []  # List of competition IDs team currently participates in
    primary_competition_id: Optional[str] = None  # Main competition (e.g., domestic league)
    competition_history: List[Dict[str, Any]] = []  # Historical participation
    
    # Media
    logo_url: Optional[str] = None
    colors: List[str] = []  # ["navy", "red", "white"]
    
    # Collaborative metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User ID
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # History tracking
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    # External references
    external_ids: Dict[str, str] = {}  # {"fifa": "123", "transfermarkt": "456"}
    topkit_reference: str  # TK-TEAM-000001

class Brand(BaseModel):
    """Entité Brand/Manufacturer (Nike, Adidas, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # "Nike"
    official_name: Optional[str] = None  # "Nike Inc."
    common_names: List[str] = []  # ["Nike", "Nike Football"]
    
    # Informations marque
    country: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None
    
    # Logo et identité visuelle
    logo_url: Optional[str] = None
    brand_colors: List[str] = []
    
    # Métadonnées collaboratives
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    topkit_reference: str  # TK-BRAND-000001

class Player(BaseModel):
    """Entité Player avec historique des maillots portés"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # "Kylian Mbappé"
    full_name: Optional[str] = None
    common_names: List[str] = []  # ["Mbappé", "Kylian Mbappé", "K. Mbappé"]
    
    # Informations joueur
    birth_date: Optional[datetime] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    jersey_number_history: List[Dict[str, Any]] = []  # [{"team_id": "...", "number": 7, "season": "2023-24"}]
    
    # Photo
    photo_url: Optional[str] = None
    
    # Métadonnées collaboratives
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    # Références externes
    external_ids: Dict[str, str] = {}
    topkit_reference: str  # TK-PLAYER-000001

class Competition(BaseModel):
    """Entité Competition/Event (Championnats, coupes, événements) - Updated to match CSV structure"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competition_name: str  # "Ligue 1" - main display name
    official_name: Optional[str] = None  # "Ligue 1 Uber Eats"
    alternative_names: List[str] = []  # ["L1", "French Championship"]
    
    # Competition classification matching CSV structure
    type: str  # "National league", "Continental competition", "International competition", "Intercontinental competition", "National cup", "Continental super cup"
    confederations_federations: List[str] = []  # ["UEFA"], ["FIFA"], ["CONMEBOL"], ["UEFA", "CONMEBOL"]
    country: Optional[str] = None  # France, Spain, etc. (None for international)
    level: Optional[Union[str, int]] = None  # 1 pour première division, 2 pour deuxième, etc.
    
    # Historical information
    year_created: Optional[int] = None  # Year when competition was created
    is_recurring: bool = True  # False for one-off events
    current_season: Optional[str] = None
    
    # Media and branding
    logo: Optional[str] = None  # Logo file path/URL
    trophy_photo: Optional[str] = None  # Trophy image file path/URL
    secondary_images: List[str] = []
    primary_color: Optional[str] = None
    
    # Metadata for collaborative system
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    topkit_reference: str  # TK-COMP-000001

# ================================
# NEW KIT HIERARCHY SYSTEM
# ================================

class KitType(str, Enum):
    HOME = "home"
    AWAY = "away"
    THIRD = "third"
    FOURTH = "fourth"
    GOALKEEPER = "goalkeeper"
    SPECIAL = "special"

class KitModel(str, Enum):
    REPLICA = "replica"
    AUTHENTIC = "authentic"

class KitCondition(str, Enum):
    MINT = "mint"
    NEAR_MINT = "near_mint"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class MasterKit(BaseModel):
    """Master Kit - Template level with design information"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Basic Kit Info
    team_id: str  # Reference to Team
    brand_id: str  # Reference to Brand
    season: str  # "2022-23"
    kit_type: KitType  # home/away/third/fourth/goalkeeper/special
    model: KitModel  # replica/authentic
    
    # Competition Details
    competition_id: Optional[str] = None  # Reference to Competition
    competition_badges: List[str] = []  # Competition-specific badges/patches
    competition_details: Optional[Dict[str, Any]] = None  # Special competition info
    
    # Design Information
    design_name: Optional[str] = None  # "Jordan Collection", "Centenario"
    primary_color: str
    secondary_colors: List[str] = []
    pattern_description: Optional[str] = None
    
    # Sponsor & Branding
    main_sponsor: Optional[str] = None
    sponsor_placement: Optional[str] = None
    
    # Media
    main_image_url: Optional[str] = None
    reference_images: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    topkit_reference: str  # TK-MASTER-000001
    
    # Statistics
    total_reference_kits: int = 0
    total_collectors: int = 0

class ReferenceKit(BaseModel):
    """Reference Kit - Generic version users can add to their collections"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Master Kit Reference
    master_kit_id: str
    
    # Available Variations
    available_sizes: List[str] = []  # ["XS", "S", "M", "L", "XL", "XXL"]
    available_prints: List[Dict[str, Any]] = []  # [{"player_name": "Messi", "number": 10, "player_id": "123"}]
    
    # Pricing Information
    original_retail_price: Optional[float] = None
    current_market_estimate: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    
    # Availability
    release_date: Optional[datetime] = None
    discontinued_date: Optional[datetime] = None
    is_limited_edition: bool = False
    production_run: Optional[int] = None  # Total pieces produced
    
    # Reference Information
    official_product_code: Optional[str] = None  # Brand's SKU
    retailer_links: List[Dict[str, str]] = []  # [{"retailer": "Nike", "url": "..."}]
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    
    topkit_reference: str  # TK-REF-000001
    
    # Statistics
    total_in_collections: int = 0  # How many users have this in their collection
    total_for_sale: int = 0

class PersonalKit(BaseModel):
    """Personal Kit - User's specific kit in their OWNED collection with personalization"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Owner & Reference
    user_id: str
    reference_kit_id: str
    
    # Physical Details
    size: str
    condition: KitCondition
    
    # Purchase Information
    purchase_price: Optional[float] = None
    price_value: Optional[float] = None  # Current value estimate
    purchase_date: Optional[datetime] = None
    purchase_location: Optional[str] = None  # Store, online, etc.
    
    # Personalization
    is_worn: bool = False
    is_signed: bool = False
    signed_by: Optional[str] = None  # Player name or person who signed
    
    # Printing Details
    has_printing: bool = False
    printed_name: Optional[str] = None
    printed_number: Optional[int] = None
    printing_type: Optional[str] = None  # "official", "custom", "heat_press", etc.
    
    # Special Attributes
    is_match_worn: bool = False
    match_details: Optional[str] = None  # Which match, date, etc.
    is_authenticated: bool = False
    authentication_details: Optional[str] = None
    
    # Custom Notes
    personal_notes: Optional[str] = None
    acquisition_story: Optional[str] = None
    
    # Collection Status - REMOVED collection_type, PersonalKit is ONLY for owned items
    for_sale: bool = False
    asking_price: Optional[float] = None
    
    # Metadata
    added_to_collection_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: Optional[datetime] = None
    
    # Statistics
    estimated_current_value: Optional[float] = None
    times_worn: int = 0

class WantedKit(BaseModel):
    """Wanted Kit - Simple reference to a kit the user wants (remains as Reference Kit)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Owner & Reference - MINIMAL DATA ONLY
    user_id: str
    reference_kit_id: str
    
    # Optional preference (but kit remains a Reference Kit)
    preferred_size: Optional[str] = None  # User's preferred size, but not required
    max_price_willing_to_pay: Optional[float] = None  # Optional price limit
    notes: Optional[str] = None  # Optional notes like "looking for authentic version"
    
    # Metadata
    added_to_wanted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Priority
    priority: str = "medium"  # "low", "medium", "high"
    
    # Photos (user's own photos)
    personal_photos: List[str] = []
    
    # Metadata
    added_to_collection_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: Optional[datetime] = None
    
    # Valuation
    estimated_current_value: Optional[float] = None
    last_valuation_date: Optional[datetime] = None

# ================================
# SYSTÈME COLLABORATIF
# ================================

class Contribution(BaseModel):
    """Contribution/modification proposée par un utilisateur"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Informations contribution
    contributor_id: str
    entity_type: EntityType
    entity_id: str
    
    # Type de contribution
    contribution_type: str  # "create", "update", "merge", "delete"
    
    # Données proposées
    proposed_changes: Dict[str, Any] = {}
    previous_data: Dict[str, Any] = {}
    
    # Justification et preuves
    description: str
    evidence_urls: List[str] = []  # Photos, sources, liens
    source_links: List[str] = []
    
    # Statut et modération
    status: ContributionStatus = ContributionStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    # Votes communautaires
    upvotes: int = 0
    downvotes: int = 0
    total_votes: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Vote(BaseModel):
    """Vote d'un utilisateur sur une contribution"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contribution_id: str
    user_id: str
    vote_type: str  # "upvote", "downvote"
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DuplicateDetection(BaseModel):
    """Détection automatique de doublons"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType
    primary_entity_id: str
    potential_duplicate_id: str
    
    # Score de similarité (0-100)
    similarity_score: int
    
    # Champs similaires détectés
    matching_fields: List[str] = []
    similar_data: Dict[str, Any] = {}
    
    # Statut
    status: str = "detected"  # "detected", "confirmed", "rejected", "merged"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EntityHistory(BaseModel):
    """Historique des modifications d'une entité"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType
    entity_id: str
    
    # Modification
    action: str  # "create", "update", "merge", "delete"
    changed_fields: List[str] = []
    old_values: Dict[str, Any] = {}
    new_values: Dict[str, Any] = {}
    
    # Qui et quand
    modified_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Lien vers contribution si applicable
    contribution_id: Optional[str] = None

# ================================
# MODÈLES DE REQUÊTES API
# ================================

class TeamCreate(BaseModel):
    name: str
    short_name: Optional[str] = None
    common_names: List[str] = []
    country: str
    city: Optional[str] = None
    founded_year: Optional[int] = None
    current_competitions: List[str] = []  # List of competition IDs
    primary_competition_id: Optional[str] = None  # Main competition
    colors: List[str] = []
    
class BrandCreate(BaseModel):
    name: str
    official_name: Optional[str] = None
    common_names: List[str] = []
    country: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None

class PlayerCreate(BaseModel):
    name: str
    full_name: Optional[str] = None
    common_names: List[str] = []
    birth_date: Optional[datetime] = None
    nationality: Optional[str] = None
    position: Optional[str] = None

class CompetitionCreate(BaseModel):
    competition_name: str  # Main display name
    official_name: Optional[str] = None
    alternative_names: List[str] = []
    type: str  # Competition type from CSV structure
    confederations_federations: List[str] = []  # ["UEFA"], ["FIFA"], etc.
    country: Optional[str] = None
    level: Optional[Union[str, int]] = None
    year_created: Optional[int] = None
    logo: Optional[str] = None  # Logo file path/URL
    trophy_photo: Optional[str] = None  # Trophy image file path/URL
    secondary_images: List[str] = []

# ================================
# CREATE CLASSES FOR NEW HIERARCHY
# ================================

class MasterKitCreate(BaseModel):
    team_id: str
    brand_id: str
    season: str
    kit_type: KitType
    model: KitModel
    competition_id: Optional[str] = None
    competition_badges: List[str] = []
    design_name: Optional[str] = None
    primary_color: str
    secondary_colors: List[str] = []
    pattern_description: Optional[str] = None
    main_sponsor: Optional[str] = None
    sponsor_placement: Optional[str] = None
    main_image_url: Optional[str] = None
    reference_images: List[str] = []

class ReferenceKitCreate(BaseModel):
    master_kit_id: str
    available_sizes: List[str] = []
    available_prints: List[Dict[str, Any]] = []
    original_retail_price: Optional[float] = None
    current_market_estimate: Optional[float] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    release_date: Optional[datetime] = None
    is_limited_edition: bool = False
    production_run: Optional[int] = None
    official_product_code: Optional[str] = None

class PersonalKitCreate(BaseModel):
    """Create Personal Kit - ONLY for OWNED items with detailed information"""
    reference_kit_id: str
    size: str
    condition: KitCondition = KitCondition.GOOD
    purchase_price: Optional[float] = None
    price_value: Optional[float] = None  # Current value estimate
    purchase_date: Optional[datetime] = None
    purchase_location: Optional[str] = None
    acquisition_story: Optional[str] = None  # Story of how it was acquired
    times_worn: Optional[int] = 0  # How many times worn
    is_worn: bool = False
    is_signed: bool = False
    signed_by: Optional[str] = None
    has_printing: bool = False
    printed_name: Optional[str] = None
    printed_number: Optional[int] = None
    printing_type: Optional[str] = None
    is_match_worn: bool = False
    match_details: Optional[str] = None
    is_authenticated: bool = False
    authentication_details: Optional[str] = None
    personal_notes: Optional[str] = None
    for_sale: bool = False  # Marketplace option
    # Removed collection_type - PersonalKit is ONLY for owned items

class WantedKitCreate(BaseModel):
    """Create Wanted Kit - Simple reference to a Reference Kit the user wants"""
    reference_kit_id: str
    preferred_size: Optional[str] = None  # Optional preferred size
    max_price_willing_to_pay: Optional[float] = None  # Optional price limit
    notes: Optional[str] = None  # Optional notes
    priority: str = "medium"  # "low", "medium", "high"

class PersonalKitUpdate(BaseModel):
    size: Optional[str] = None
    condition: Optional[KitCondition] = None
    purchase_price: Optional[float] = None
    price_value: Optional[float] = None
    purchase_date: Optional[datetime] = None
    purchase_location: Optional[str] = None
    acquisition_story: Optional[str] = None
    times_worn: Optional[int] = None
    is_worn: Optional[bool] = None
    is_signed: Optional[bool] = None
    signed_by: Optional[str] = None
    has_printing: Optional[bool] = None
    printed_name: Optional[str] = None
    printed_number: Optional[int] = None
    printing_type: Optional[str] = None
    is_match_worn: Optional[bool] = None
    match_details: Optional[str] = None
    is_authenticated: Optional[bool] = None
    authentication_details: Optional[str] = None
    personal_notes: Optional[str] = None
    for_sale: Optional[bool] = None  # Fixed to match PersonalKit model
    asking_price: Optional[float] = None

# ================================
# MODÈLES DE RÉPONSE
# ================================

class TeamResponse(BaseModel):
    """Réponse API enrichie pour Team"""
    # Données Team
    id: str
    name: str
    short_name: Optional[str]
    common_names: List[str]
    country: str
    city: Optional[str]
    founded_year: Optional[int]
    colors: List[str]
    logo_url: Optional[str]
    topkit_reference: str
    verified_level: VerificationLevel
    
    # Données enrichies
    league_info: Optional[Dict[str, Any]] = None  # Info Competition
    master_jerseys_count: int = 0
    total_collectors: int = 0
    
    # Métadonnées
    created_at: datetime
    modification_count: int

# ================================
# RESPONSE MODELS FOR NEW HIERARCHY  
# ================================

class MasterKitResponse(BaseModel):
    """API Response for Master Kit with enriched data"""
    # Master Kit Data
    id: str
    team_id: str  # Foreign key to Team
    brand_id: str  # Foreign key to Brand
    season: str
    kit_type: KitType
    model: KitModel
    competition_id: Optional[str] = None  # Foreign key to Competition
    design_name: Optional[str]
    primary_color: str
    secondary_colors: List[str]
    main_sponsor: Optional[str]
    reference_images: List[str]
    topkit_reference: str
    verified_level: VerificationLevel
    
    # Enriched Data
    team_info: Dict[str, Any]  # Team data
    brand_info: Dict[str, Any]  # Brand data
    competition_info: Optional[Dict[str, Any]] = None  # Competition data
    
    # Statistics
    total_reference_kits: int
    total_collectors: int
    
    # Metadata
    created_at: datetime
    modification_count: int

class ReferenceKitResponse(BaseModel):
    """API Response for Reference Kit with enriched data"""
    # Reference Kit Data
    id: str
    master_kit_id: str  # Foreign key to Master Kit
    available_sizes: List[str]
    available_prints: List[Dict[str, Any]]
    original_retail_price: Optional[float]
    current_market_estimate: Optional[float]
    price_range_min: Optional[float]
    price_range_max: Optional[float]
    is_limited_edition: bool
    topkit_reference: str
    verified_level: VerificationLevel
    
    # Image fields
    main_photo: Optional[str] = None
    product_images: List[str] = []
    secondary_photos: List[str] = []
    
    # Model and competition fields
    model_name: Optional[str] = None
    league_competition: Optional[str] = None
    
    # Additional fields
    description: Optional[str] = None
    sku_code: Optional[str] = None
    barcode: Optional[str] = None
    release_date: Optional[str] = None
    production_run: Optional[int] = None
    material_composition: Optional[str] = None
    care_instructions: Optional[str] = None
    authenticity_features: List[str] = []
    
    # Enriched Data
    master_kit_info: Dict[str, Any]  # Master Kit data
    team_info: Dict[str, Any]  # Team data
    brand_info: Dict[str, Any]  # Brand data
    competition_info: Dict[str, Any] = {}  # Competition data
    
    # Statistics  
    total_in_collections: int
    total_for_sale: int
    
    # Metadata
    created_at: datetime

class PersonalKitResponse(BaseModel):
    """API Response for Personal Kit with enriched data"""
    # Personal Kit Data
    id: str
    size: str
    condition: KitCondition
    purchase_price: Optional[float]
    price_value: Optional[float]  # Current value estimate
    purchase_date: Optional[datetime]
    purchase_location: Optional[str]
    acquisition_story: Optional[str]
    times_worn: int
    is_worn: bool
    is_signed: bool
    signed_by: Optional[str]
    has_printing: bool
    printed_name: Optional[str]
    printed_number: Optional[int]
    printing_type: Optional[str]
    is_match_worn: bool
    match_details: Optional[str]
    is_authenticated: bool
    authentication_details: Optional[str]
    personal_notes: Optional[str]
    for_sale: bool  # Fixed to match PersonalKit model
    asking_price: Optional[float]
    estimated_current_value: Optional[float]
    
    # Enriched Data
    reference_kit_info: Dict[str, Any]  # Reference Kit data
    master_kit_info: Dict[str, Any]  # Master Kit data
    team_info: Dict[str, Any]  # Team data
    brand_info: Dict[str, Any]  # Brand data
    
    # Metadata
    added_to_collection_at: datetime
    last_updated_at: Optional[datetime]

# ================================
# SYSTÈME DE CONTRIBUTION COLLABORATIF
# ================================

class ContributionAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    MERGE = "merge"
    DELETE = "delete"

class ContributionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    AUTO_APPROVED = "auto_approved"

class VoteType(str, Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"

class ContributionVote(BaseModel):
    """Vote sur une contribution"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contribution_id: str
    voter_id: str
    vote_type: VoteType  # upvote, downvote
    comment: Optional[str] = None
    field_votes: Optional[Dict[str, str]] = {}  # Field-level votes: {"field_name": "approve"|"reject"}
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Contribution(BaseModel):
    """Contribution/Suggestion de modification collaborative"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Référence de l'entité modifiée
    entity_type: EntityType  # team, brand, player, competition, master_jersey
    entity_id: str  # ID de l'entité concernée
    entity_reference: str  # TK-TEAM-000001 pour affichage
    
    # Type d'action
    action_type: ContributionAction
    
    # Données proposées (diff avec existantes)
    current_data: Dict[str, Any] = {}  # Données actuelles
    proposed_data: Dict[str, Any] = {} # Données proposées
    changed_fields: List[str] = []     # Champs modifiés
    
    # Métadonnées contribution
    title: str  # "Ajout du logo officiel FC Barcelona"
    description: Optional[str] = None  # Justification détaillée
    source_urls: List[str] = []  # URLs de sources pour validation
    images: Optional[Dict[str, Any]] = None  # Images proposées (logo, primary_photo, secondary_photos)
    
    # Contributeur
    contributor_id: str
    contributor_level: Optional[str] = None  # Rookie, Expert, etc.
    
    # Statut et validation
    status: ContributionStatus = ContributionStatus.PENDING
    
    # Système de votes
    upvotes: int = 0
    downvotes: int = 0
    vote_score: int = 0  # upvotes - downvotes
    voters: List[str] = []  # Liste des user IDs qui ont voté
    
    # Modération
    moderator_id: Optional[str] = None
    moderator_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Automatisation
    auto_approved: bool = False
    requires_expert_review: bool = False
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # 7 jours par défaut
    
    # Référence unique
    topkit_reference: str  # TK-CONTRIB-000001

class ContributorStats(BaseModel):
    """Statistiques d'un contributeur"""
    user_id: str
    username: str
    
    # Statistiques contributions
    total_contributions: int = 0
    accepted_contributions: int = 0
    rejected_contributions: int = 0
    pending_contributions: int = 0
    
    # Statistiques votes
    total_votes: int = 0
    quality_votes: int = 0  # Votes alignés avec décision finale
    vote_accuracy: float = 0.0  # % de votes "justes"
    
    # Points et niveau
    reputation_points: int = 0
    contributor_level: str = "Rookie"  # Rookie, Contributor, Expert, Legend
    
    # Spécialisations (badges)
    badges: List[str] = []  # ["logo_hunter", "french_expert", etc.]
    specializations: List[str] = []  # ["teams", "competitions", "brands"]
    
    # Activité
    first_contribution: Optional[datetime] = None
    last_contribution: Optional[datetime] = None
    contributions_this_month: int = 0
    
    # Classement
    global_rank: Optional[int] = None
    monthly_rank: Optional[int] = None

# ================================
# MODÈLES DE RÉPONSE POUR CONTRIBUTIONS
# ================================

class ContributionResponse(BaseModel):
    """Réponse API pour une contribution"""
    id: str
    entity_type: str
    entity_reference: str
    action_type: str
    title: str
    description: Optional[str]
    
    # Contributeur
    contributor: Dict[str, str]  # {id, username, level}
    
    # Changements proposés (simplifié pour affichage)
    changes_summary: List[Dict[str, Any]]  # [{"field": "logo_url", "from": null, "to": "url"}]
    
    # Votes
    vote_score: int
    upvotes: int
    downvotes: int
    user_vote: Optional[str] = None  # upvote/downvote si user a voté
    
    # Statut
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    
    # Référence
    topkit_reference: str

class ContributionCreateRequest(BaseModel):
    """Requête pour créer une contribution"""
    entity_type: EntityType
    entity_id: str
    action_type: ContributionAction = ContributionAction.UPDATE
    
    # Données proposées
    proposed_data: Dict[str, Any]
    
    # Métadonnées
    title: str
    description: Optional[str] = None
    source_urls: List[str] = []
    images: Optional[Dict[str, Any]] = None  # Nouvelles images proposées

class VoteRequest(BaseModel):
    """Requête pour voter sur une contribution"""
    vote_type: VoteType
    comment: Optional[str] = None
    field_votes: Optional[Dict[str, str]] = {}  # Field-level votes: {"field_name": "approve"|"reject"}
    granular_votes: Optional[Dict[str, str]] = {}  # Alias for field_votes for compatibility

# ================================
# LEGACY JERSEY SYSTEM (for compatibility)
# ================================

class MasterJersey(BaseModel):
    """Legacy Master Jersey model for compatibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    brand_id: str
    season: str
    jersey_type: str
    model: str
    primary_color: str
    secondary_colors: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    topkit_reference: str

class JerseyRelease(BaseModel):
    """Legacy Jersey Release model for compatibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    master_jersey_id: str
    player_name: Optional[str] = None
    player_number: Optional[int] = None
    retail_price: Optional[float] = None
    release_type: str = "standard"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    topkit_reference: str

class UserJerseyCollection(BaseModel):
    """Legacy User Jersey Collection model for compatibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    jersey_release_id: str
    collection_type: str  # "owned", "wanted"
    size: Optional[str] = None
    condition: Optional[str] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)

class JerseyReleaseValuation(BaseModel):
    """Legacy Jersey Release Valuation model for compatibility"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_release_id: str
    estimated_value: float
    market_trend: str = "stable"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# ================================
# LEGACY CREATE MODELS
# ================================

class MasterJerseyCreate(BaseModel):
    """Legacy Master Jersey creation model"""
    team_id: str
    brand_id: str
    season: str
    jersey_type: str
    model: str
    primary_color: str
    secondary_colors: List[str] = []

class JerseyReleaseCreate(BaseModel):
    """Legacy Jersey Release creation model"""
    master_jersey_id: str
    player_name: Optional[str] = None
    player_number: Optional[int] = None
    retail_price: Optional[float] = None
    release_type: str = "standard"

# ================================
# LEGACY RESPONSE MODELS
# ================================

class MasterJerseyResponse(BaseModel):
    """Legacy Master Jersey response model"""
    id: str
    team_id: str
    brand_id: str
    season: str
    jersey_type: str
    model: str
    primary_color: str
    secondary_colors: List[str] = []
    created_at: datetime
    created_by: str
    verified_level: VerificationLevel
    topkit_reference: str
    # Image fields
    main_image_url: Optional[str] = None
    additional_images: List[str] = []
    # Enriched data
    team_info: Optional[Dict[str, Any]] = {}
    brand_info: Optional[Dict[str, Any]] = {}
    competition_info: Optional[Dict[str, Any]] = {}
    # Statistics for versions and collectors
    releases_count: int = 0
    collectors_count: int = 0

# ================================
# ENHANCED CONTRIBUTIONS SYSTEM - DISCOGS STYLE
# ================================

class ContributionType(str, Enum):
    """Types of entities that can be contributed to"""
    TEAM = "team"
    BRAND = "brand"
    PLAYER = "player"
    COMPETITION = "competition"
    MASTER_KIT = "master_kit"
    REFERENCE_KIT = "reference_kit"

class ContributionStatusV2(str, Enum):
    """Enhanced contribution status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class VoteTypeV2(str, Enum):
    """Vote types for contributions"""
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"

class ContributionImage(BaseModel):
    """Image associated with a contribution"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    is_primary: bool = False
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str

class ContributionVoteV2(BaseModel):
    """Individual vote on a contribution"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    vote_type: VoteTypeV2
    comment: Optional[str] = None
    voted_at: datetime = Field(default_factory=datetime.utcnow)
    # Field-specific votes for granular approval
    field_votes: Dict[str, VoteTypeV2] = {}

class ContributionHistoryEntry(BaseModel):
    """History entry for contribution changes"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str  # created, updated, approved, rejected, voted, etc.
    user_id: str
    user_name: Optional[str] = None
    details: Dict[str, Any] = {}
    changes: Optional[Dict[str, Any]] = None

class EnhancedContribution(BaseModel):
    """Enhanced Discogs-style contribution model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Entity information
    entity_type: ContributionType
    entity_id: Optional[str] = None  # None for new entities
    
    # Dynamic data based on entity type
    data: Dict[str, Any] = {}  # Flexible JSON data for any entity type
    
    # Images (required for kits, optional for others)
    images: List[ContributionImage] = []
    
    # Status and workflow
    status: ContributionStatusV2 = ContributionStatusV2.DRAFT
    
    # Voting
    upvotes: int = 0
    downvotes: int = 0
    votes: List[ContributionVoteV2] = []
    
    # Review and moderation
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_comment: Optional[str] = None
    
    # History and audit trail
    history: List[ContributionHistoryEntry] = []
    
    # Metadata
    title: str
    description: Optional[str] = None
    source_urls: List[str] = []
    
    # Creator information
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Auto-approval tracking
    auto_approved: bool = False
    auto_rejected: bool = False
    
    # Reference
    topkit_reference: str = Field(default="")

class ContributionCreateV2(BaseModel):
    """Request model for creating new contributions"""
    entity_type: ContributionType
    entity_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    data: Dict[str, Any] = {}
    source_urls: List[str] = []

class ContributionUpdateV2(BaseModel):
    """Request model for updating contributions"""
    title: Optional[str] = None
    description: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    source_urls: Optional[List[str]] = None
    status: Optional[ContributionStatusV2] = None

class ContributionVoteRequest(BaseModel):
    """Request model for voting on contributions"""
    vote_type: VoteTypeV2
    comment: Optional[str] = None
    field_votes: Dict[str, VoteTypeV2] = {}

class ContributionImageUpload(BaseModel):
    """Request model for uploading contribution images"""
    is_primary: bool = False
    caption: Optional[str] = None

# Response models
class ContributionSummary(BaseModel):
    """Summary response for contribution listings"""
    id: str
    entity_type: ContributionType
    title: str
    status: ContributionStatusV2
    upvotes: int
    downvotes: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    images_count: int
    topkit_reference: str

class ContributionDetail(BaseModel):
    """Detailed response for individual contributions"""
    id: str
    entity_type: ContributionType
    entity_id: Optional[str]
    title: str
    description: Optional[str]
    data: Dict[str, Any]
    images: List[ContributionImage]
    status: ContributionStatusV2
    upvotes: int
    downvotes: int
    votes: List[ContributionVoteV2]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_comment: Optional[str]
    history: List[ContributionHistoryEntry]
    source_urls: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    auto_approved: bool
    auto_rejected: bool
    topkit_reference: str
    # Additional computed fields
    user_can_vote: bool = True
    user_vote: Optional[VoteTypeV2] = None
    requires_images: bool = False

# Moderation models
class ModerationAction(str, Enum):
    """Available moderation actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_REVISION = "request_revision"
    DELETE = "delete"
    FEATURE = "feature"
    UNFAIR_VOTE = "unfair_vote"

class ModerationRequest(BaseModel):
    """Request for moderation actions"""
    action: ModerationAction
    reason: Optional[str] = None
    internal_notes: Optional[str] = None
    notify_contributor: bool = True

class ModerationStats(BaseModel):
    """Statistics for moderation dashboard"""
    pending_contributions: int
    approved_today: int
    rejected_today: int
    total_votes_today: int
    auto_approved_today: int
    auto_rejected_today: int
    contributions_by_type: Dict[str, int]
    top_contributors: List[Dict[str, Any]]