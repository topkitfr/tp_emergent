"""
Modèles collaboratifs pour TopKit - Base de données type Discogs
Nouvelles entités pour la vision collaborative
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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
    """Entité Team/Club avec informations détaillées"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # "Paris Saint-Germain"
    short_name: Optional[str] = None  # "PSG"
    common_names: List[str] = []  # ["PSG", "Paris SG", "Paris Saint-Germain"]
    
    # Informations club
    founded_year: Optional[int] = None
    country: str  # France
    city: Optional[str] = None  # Paris
    league_id: Optional[str] = None  # Référence vers Competition
    
    # Média
    logo_url: Optional[str] = None
    colors: List[str] = []  # ["navy", "red", "white"]
    
    # Métadonnées collaboratives
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User ID
    verified_level: VerificationLevel = VerificationLevel.UNVERIFIED
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # Historique modifications
    modification_count: int = 0
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    
    # Références et identifiants externes
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
    """Entité Competition/Event (Championnats, coupes, événements)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # "Ligue 1"
    official_name: Optional[str] = None  # "Ligue 1 Uber Eats"
    common_names: List[str] = []
    
    # Type et informations
    competition_type: str  # "domestic_league", "cup", "international", "friendly"
    country: Optional[str] = None
    level: Optional[int] = None  # 1 pour première division
    
    # Dates et récurrence
    start_year: Optional[int] = None
    is_recurring: bool = True  # False pour événements uniques
    current_season: Optional[str] = None
    
    # Logo et couleurs
    logo_url: Optional[str] = None
    secondary_images: List[str] = []
    primary_color: Optional[str] = None
    
    # Métadonnées collaboratives
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
    """Personal Kit - User's specific kit in their collection with personalization"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Owner & Reference
    user_id: str
    reference_kit_id: str
    
    # Physical Details
    size: str
    condition: KitCondition
    
    # Purchase Information
    purchase_price: Optional[float] = None
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
    
    # Collection Status
    collection_type: str = "owned"  # "owned", "wanted"
    is_for_sale: bool = False
    asking_price: Optional[float] = None
    
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
    league_id: Optional[str] = None
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
    name: str
    official_name: Optional[str] = None
    common_names: List[str] = []
    competition_type: str
    country: Optional[str] = None
    level: Optional[int] = None
    logo_url: Optional[str] = None
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
    reference_kit_id: str
    size: str
    condition: KitCondition = KitCondition.GOOD
    purchase_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    purchase_location: Optional[str] = None
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
    collection_type: str = "owned"

class PersonalKitUpdate(BaseModel):
    size: Optional[str] = None
    condition: Optional[KitCondition] = None
    purchase_price: Optional[float] = None
    purchase_date: Optional[datetime] = None
    purchase_location: Optional[str] = None
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
    acquisition_story: Optional[str] = None
    is_for_sale: Optional[bool] = None
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

class MasterJerseyResponse(BaseModel):
    """Réponse API enrichie pour MasterJersey"""
    # Données MasterJersey
    id: str
    season: str
    jersey_type: str
    design_name: Optional[str]
    primary_color: str
    secondary_colors: List[str]
    main_sponsor: Optional[str]
    reference_images: List[str]
    topkit_reference: str
    verified_level: VerificationLevel
    
    # Données enrichies
    team_info: Dict[str, Any]  # Données Team
    brand_info: Dict[str, Any]  # Données Brand
    competition_info: Optional[Dict[str, Any]] = None
    
    # Statistiques
    releases_count: int = 0  # Renamed from total_releases to avoid conflict
    collectors_count: int = 0  # Renamed from total_collectors to avoid conflict
    estimated_value_range: Optional[Dict[str, float]] = None
    
    # Métadonnées
    created_at: datetime
    modification_count: int

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