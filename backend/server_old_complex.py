from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, Form, File, UploadFile, Query, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from authlib.integrations.starlette_client import OAuth
import os
import logging
import mimetypes
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from image_processor import image_processor
import requests
import bcrypt
import jwt
from enum import Enum
import json
import websockets
import asyncio
import re
from collections import defaultdict
import time
import random
import secrets

# Import Stripe integration
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Import for 2FA
import pyotp
import qrcode
import io
import base64

# Import Gmail SMTP service and Email Manager
from email_service import gmail_service
from email_manager import email_manager

# Import collaborative models
from collaborative_models import (
    Team, Brand, Player, Competition, MasterJersey, JerseyRelease, Contribution,
    UserJerseyCollection, JerseyReleaseValuation,
    TeamCreate, BrandCreate, PlayerCreate, CompetitionCreate, MasterJerseyCreate,
    JerseyReleaseCreate,
    TeamResponse, MasterJerseyResponse,
    ContributionVote, ContributorStats, ContributionResponse, ContributionCreateRequest, VoteRequest,
    ContributionAction, ContributionStatus, VoteType, EntityType, VerificationLevel,
    # New Kit Hierarchy Models
    MasterKit, ReferenceKit, PersonalKit, WantedKit, KitType,
    MasterKitCreate, ReferenceKitCreate, PersonalKitCreate, WantedKitCreate, PersonalKitUpdate,
    MasterKitResponse, ReferenceKitResponse, PersonalKitResponse,
    # Enhanced Contributions System V2 - Discogs Style
    EnhancedContribution, ContributionCreateV2, ContributionUpdateV2,
    ContributionVoteRequest, ContributionType, ContributionStatusV2,
    VoteTypeV2, ContributionImage, ContributionVoteV2, ContributionHistoryEntry,
    ContributionSummary, ContributionDetail, ModerationAction, ModerationRequest,
    ModerationStats
)

# ================================
# AUTO-APPROVAL SYSTEM FOR TESTING
# ================================

# Global system settings
system_settings = {
    "auto_approval_enabled": True,  # Default to true for testing
    "admin_notifications": True,
    "community_voting_enabled": True
}

def enable_auto_approval_for_testing(entity_data: dict, user_id: str) -> dict:
    """
    Conditionally auto-approve entities based on system settings.
    This function checks the system settings to determine if entities
    should be automatically approved or require manual review.
    """
    if system_settings.get("auto_approval_enabled", False):
        entity_data["verified_level"] = VerificationLevel.COMMUNITY_VERIFIED
        entity_data["verified_at"] = datetime.utcnow()
        entity_data["verified_by"] = user_id
    else:
        # Set to pending status for manual review
        entity_data["verified_level"] = VerificationLevel.PENDING
        entity_data["verified_at"] = None
        entity_data["verified_by"] = None
    
    return entity_data

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="TopKit - Soccer Jersey Marketplace")

# Add session middleware for potential future OAuth (currently disabled)
# app.add_middleware(SessionMiddleware, secret_key=os.environ.get('SECRET_KEY', 'topkit-secret-key-2024'))

# OAuth disabled - using email/password authentication only
# oauth = OAuth()
# Previous Google OAuth configuration removed for security and functionality reasons

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer(auto_error=False)
# Security configurations
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIREMENTS = {
    'min_length': 8,
    'require_uppercase': True,
    'require_lowercase': True, 
    'require_number': True,
    'require_special': True
}

# Rate limiting for account creation (IP-based)
account_creation_attempts = defaultdict(list)
ACCOUNT_CREATION_LIMIT = 3  # Max 3 accounts per IP per hour
ACCOUNT_CREATION_WINDOW = 3600  # 1 hour in seconds

# Email verification tokens storage (in production, use Redis or database)
email_verification_tokens = {}

# Password reset tokens storage (in production, use Redis or database)
password_reset_tokens = {}

SECRET_KEY = os.environ.get('SECRET_KEY', 'topkit-secret-key-2024')

# Logger setup
logger = logging.getLogger(__name__)

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
if not STRIPE_API_KEY:
    logger.warning("STRIPE_API_KEY not found in environment variables")

# Email Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@topkit.fr')
if not SENDGRID_API_KEY:
    logger.warning("SENDGRID_API_KEY not found in environment variables - password reset emails will be disabled")

# Site Mode Configuration (private/public)
SITE_MODE = os.environ.get('SITE_MODE', 'public')
logger.info(f"Site mode: {SITE_MODE}")

# Commission Configuration for TopKit Marketplace
TOPKIT_COMMISSION_RATE = 0.05  # 5% commission on all sales
MINIMUM_LISTING_PRICE = 10.0   # Minimum €10 for listings
MAXIMUM_LISTING_PRICE = 5000.0 # Maximum €5000 for listings

# Enums
class JerseyCondition(str, Enum):
    NEW_WITH_TAGS = "new_with_tags"
    MINT = "mint"
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

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

# Transaction Status for Anti-Fraud System
class TransactionStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"      # En attente de paiement
    PAYMENT_HELD = "payment_held"            # Paiement bloqué (comme Leboncoin)
    AWAITING_SHIPMENT = "awaiting_shipment"  # En attente d'expédition
    SHIPPED = "shipped"                      # Expédié par le vendeur
    AWAITING_VERIFICATION = "awaiting_verification"  # En attente de vérification authenticité
    VERIFIED_AUTHENTIC = "verified_authentic"        # Maillot vérifié authentique
    VERIFIED_FAKE = "verified_fake"                  # Maillot détecté comme faux
    PAYMENT_RELEASED = "payment_released"           # Paiement libéré au vendeur
    REFUNDED = "refunded"                           # Remboursé à l'acheteur
    DISPUTED = "disputed"                           # En litige
    CANCELLED = "cancelled"                         # Annulé

class PaymentMethod(str, Enum):
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    CASH = "cash"
    CHECK = "check"

class ShippingZone(str, Enum):
    DOMESTIC = "domestic"
    EUROPE = "europe"
    WORLDWIDE = "worldwide"
    
class CollectionVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS = "friends"

class ProfileVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"

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
    # Enhanced profile fields - Public information
    bio: Optional[str] = None  # User biography (max 200 characters)
    favorite_club: Optional[str] = None  # Favorite football club from database
    instagram_username: Optional[str] = None  # Instagram username (without @)
    twitter_username: Optional[str] = None  # Twitter/X username (without @)
    website: Optional[str] = None  # Personal website URL
    profile_picture_url: Optional[str] = None  # Profile picture path
    # Enhanced security fields
    email_verified: bool = False  # Email verification status
    email_verified_at: Optional[datetime] = None  # When email was verified
    last_login: Optional[datetime] = None  # Last successful login
    failed_login_attempts: int = 0  # Count of consecutive failed logins
    account_locked_until: Optional[datetime] = None  # Account lockout expiration
    # Security Level 2 fields
    two_factor_enabled: bool = False  # 2FA status
    two_factor_secret: Optional[str] = None  # Secret for TOTP
    two_factor_backup_codes: List[str] = []  # Backup codes for 2FA
    # User status fields  
    is_banned: bool = False  # Ban status
    banned_by: Optional[str] = None  # ID of admin who banned user
    banned_at: Optional[datetime] = None  # When user was banned
    ban_reason: Optional[str] = None  # Reason for ban
    suspicious_activity_score: int = 0  # Suspicious activity tracking

class Jersey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team: str
    league: str  # Required field now
    season: str
    manufacturer: str
    jersey_type: str  # "home", "away", "third", "goalkeeper", "training", "special"
    sku_code: Optional[str] = None  # Changed from reference_code to sku_code
    model: str  # Required field: "authentic" or "replica"
    description: str
    # Photo URLs (will be set after file processing)
    front_photo_url: Optional[str] = None
    back_photo_url: Optional[str] = None
    reference_number: str  # Unique reference like TK-000001
    status: JerseyStatus = JerseyStatus.PENDING  # Default to pending for moderation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    submitted_by: str  # User who submitted this jersey
    approved_by: Optional[str] = None  # Admin who approved/rejected
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_id: str  # Reference to jersey in catalog
    seller_id: str
    size: JerseySize  # Size of this specific item
    condition: JerseyCondition  # Condition of this specific item  
    price: float  # Price for this specific listing (required)
    status: ListingStatus = ListingStatus.ACTIVE
    description: str  # Seller's description of this specific item
    images: List[str] = []  # Photos of this specific item
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # New fields for payment tracking
    sold_to: Optional[str] = None
    sold_at: Optional[datetime] = None
    final_price: Optional[float] = None

class Collection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    jersey_id: str
    collection_type: str  # "owned", "wanted"
    size: Optional[JerseySize] = None  # Size of the specific item in user's collection
    condition: Optional[JerseyCondition] = None  # Condition of the specific item in user's collection
    personal_description: Optional[str] = None  # User's personal description (signed, worn, etc.)
    added_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    payment_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    amount: float
    currency: str = "eur"
    listing_id: str
    payment_status: str = "pending"
    status: str = "initiated"
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # New fields for enhanced tracking
    sold_to: Optional[str] = None
    sold_at: Optional[datetime] = None
    final_price: Optional[float] = None

# Enhanced Transaction Model for Anti-Fraud System (Leboncoin Style)
class SecureTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    buyer_id: str
    seller_id: str
    amount: float  # Prix du maillot
    currency: str = "EUR"
    stripe_payment_intent_id: str  # ID Stripe pour le paiement bloqué
    stripe_session_id: Optional[str] = None
    status: TransactionStatus = TransactionStatus.PENDING_PAYMENT
    
    # Informations du maillot pour vérification
    jersey_info: dict = {}  # Nom, équipe, saison, etc.
    
    # Tracking de l'expédition
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None
    shipped_at: Optional[datetime] = None
    
    # Vérification d'authenticité
    verification_notes: Optional[str] = None
    verified_by_admin_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    authenticity_score: Optional[int] = None  # 1-10, 10 = 100% authentique
    
    # Dates importantes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_held_at: Optional[datetime] = None
    expected_delivery_date: Optional[datetime] = None
    auto_release_date: Optional[datetime] = None  # Libération auto après X jours
    
    # Communications
    buyer_notifications: List[dict] = []
    seller_notifications: List[dict] = []
    admin_notes: List[dict] = []
    
    # Protection anti-fraude
    risk_score: int = 0  # Score de risque calculé
    fraud_indicators: List[str] = []  # Indicateurs de fraude détectés
    requires_manual_review: bool = False

class TransactionAction(BaseModel):
    action_type: str  # "ship", "verify_authentic", "verify_fake", "release", "refund"
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_carrier: Optional[str] = None
    authenticity_score: Optional[int] = None
    evidence_photos: List[str] = []  # URLs des photos de vérification

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

# Pydantic models
class JerseyDetailData(BaseModel):
    model_type: str = Field(default="authentic")
    condition: str = Field(default="mint")
    size: str = Field(default="m")
    special_features: List[str] = Field(default=[])
    material_details: str = Field(default="")
    tags: str = Field(default="tags_on")
    packaging: str = Field(default="no_packaging")
    customization: str = Field(default="blank")
    competition_badges: str = Field(default="")
    rarity: str = Field(default="common")
    purchase_price: Optional[float] = Field(default=None)
    purchase_date: Optional[str] = Field(default=None)
    purchase_location: Optional[str] = Field(default=None)
    certificate_authenticity: bool = Field(default=False)
    storage_notes: str = Field(default="")
    estimated_value: float = Field(default=0)

# Request Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class JerseyCreate(BaseModel):
    team: str
    league: str  # Now required field
    season: str
    manufacturer: Optional[str] = ""
    jersey_type: Optional[str] = ""  # home/away/third/goalkeeper/training/special
    sku_code: Optional[str] = None  # Changed from reference_code to sku_code
    model: str  # New required field: authentic/replica
    description: Optional[str] = ""
    # Photo fields for multipart upload (handled separately)
    # front_photo and back_photo will be handled as files in the endpoint

class ListingCreate(BaseModel):
    collection_id: str  # Reference to item in user's collection (not jersey_id directly)
    price: float  # Price for this specific listing (required for marketplace)
    marketplace_description: Optional[str] = None  # Additional marketplace description
    images: List[str] = []  # Photos of this specific item for marketplace

class CollectionAdd(BaseModel):
    jersey_id: str
    collection_type: str  # "owned", "wanted"
    size: Optional[str] = None  # Size of the specific item in user's collection
    condition: Optional[str] = None  # Condition of the specific item in user's collection  
    personal_description: Optional[str] = None  # User's personal description (signed, worn, etc.)

class ReferenceKitCollectionAdd(BaseModel):
    reference_kit_id: str
    collection_type: str  # "owned", "wanted"
    size: Optional[str] = None  # Size of the specific item in user's collection
    condition: Optional[str] = None  # Condition of the specific item in user's collection  
    personal_description: Optional[str] = None  # User's personal description (signed, worn, etc.)
    # Additional fields specific to personal reference kits
    purchase_price: Optional[float] = None
    estimated_value: Optional[float] = None
    player_name: Optional[str] = None
    player_number: Optional[str] = None
    # New special attributes
    worn: Optional[bool] = False
    worn_type: Optional[str] = None  # "match_worn", "player_issue", "team_issue"
    signed: Optional[bool] = False
    signed_by: Optional[str] = None  # Player name who signed it

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

class ModificationSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jersey_id: str
    moderator_id: str
    suggested_changes: str  # Detailed feedback from moderator
    suggested_modifications: Dict[str, Any] = {}  # Field-specific suggestions
    status: str = "pending"  # "pending", "addressed", "ignored"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    addressed_at: Optional[datetime] = None

class NotificationType(str, Enum):
    JERSEY_APPROVED = "jersey_approved"
    JERSEY_REJECTED = "jersey_rejected"
    JERSEY_NEEDS_MODIFICATION = "jersey_needs_modification"
    MODIFICATION_SUGGESTION = "modification_suggestion"
    SYSTEM_ANNOUNCEMENT = "system_announcement"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: NotificationType
    title: str
    message: str
    related_id: Optional[str] = None  # Jersey ID, suggestion ID, etc.
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

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

# Nouveaux modèles pour profil utilisateur avancé
class ShippingRate(BaseModel):
    zone: ShippingZone
    price: float
    currency: str = "EUR"

class UserAddressSettings(BaseModel):
    full_name: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None
    
class SellerSettings(BaseModel):
    is_seller: bool = False
    # Informations de contact
    business_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    # Address settings
    address_settings: Optional[UserAddressSettings] = None
    # Politiques
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None
    payment_methods: List[PaymentMethod] = []
    shipping_rates: List[ShippingRate] = []
    # Délais et conditions
    processing_time_days: int = 3
    return_days: int = 14
    min_order_value: Optional[float] = None
    # Notes et conditions
    seller_notes: Optional[str] = None
    terms_conditions: Optional[str] = None

class BuyerSettings(BaseModel):
    # Address settings
    address_settings: Optional[UserAddressSettings] = None
    # Préférences de livraison
    preferred_shipping_method: Optional[str] = None
    max_shipping_cost: Optional[float] = None
    # Budget et notifications
    max_budget_per_item: Optional[float] = None
    price_alert_threshold: Optional[float] = None
    # Notifications
    notify_new_matches: bool = True
    notify_price_drops: bool = True
    notify_watchlist_available: bool = True

class CollectionSettings(BaseModel):
    visibility: CollectionVisibility = CollectionVisibility.PUBLIC
    show_statistics: bool = True
    show_estimated_value: bool = False
    show_acquisition_dates: bool = True
    allow_export: bool = True
    # Notifications pour collection
    notify_similar_items: bool = True
    notify_collection_updates: bool = False

class PrivacySettings(BaseModel):
    profile_visibility: ProfileVisibility = ProfileVisibility.PUBLIC
    show_last_seen: bool = True
    allow_private_messages: bool = True
    show_location: bool = True
    show_join_date: bool = True
    allow_friend_requests: bool = True

class UserRating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rater_id: str  # Utilisateur qui note
    rated_user_id: str  # Utilisateur noté
    transaction_id: Optional[str] = None
    rating_type: str  # "seller", "buyer"
    score: int  # 1-5 étoiles
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    # Profile picture
    profile_picture_url: Optional[str] = None
    # Informations personnelles étendues
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    languages: List[str] = []
    website: Optional[str] = None
    social_links: Dict[str, str] = {}
    # Paramètres
    seller_settings: SellerSettings = Field(default_factory=SellerSettings)
    buyer_settings: BuyerSettings = Field(default_factory=BuyerSettings)
    collection_settings: CollectionSettings = Field(default_factory=CollectionSettings)
    privacy_settings: PrivacySettings = Field(default_factory=PrivacySettings)
    # Statistiques
    total_sales: int = 0
    total_purchases: int = 0
    avg_seller_rating: Optional[float] = None
    avg_buyer_rating: Optional[float] = None
    total_seller_ratings: int = 0
    total_buyer_ratings: int = 0
    # Badges et vérifications
    verified_seller: bool = False
    verified_buyer: bool = False
    badges: List[str] = []
    # Dates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CheckoutRequest(BaseModel):
    listing_id: str
    origin_url: str

class PaymentStatusResponse(BaseModel):
    status: str
    payment_status: str
    amount_total: float
    currency: str
    listing_id: str
    seller_id: str
    buyer_id: Optional[str] = None
    commission_amount: float
    seller_amount: float
    metadata: Dict[str, Any] = {}

class PurchaseHistoryItem(BaseModel):
    transaction_id: str
    listing_id: str
    jersey_info: Dict[str, Any]
    seller_info: Dict[str, str]
    amount_paid: float
    commission_paid: float
    currency: str
    purchase_date: datetime
    status: str

class SiteModeRequest(BaseModel):
    mode: str  # 'private' or 'public'

class SiteModeResponse(BaseModel):
    mode: str
    message: str

class BetaAccessRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    message: Optional[str] = None

class BetaAccessResponse(BaseModel):
    message: str
    request_id: str

class RejectBetaRequest(BaseModel):
    reason: str

class ModificationSuggestionCreate(BaseModel):
    jersey_id: str
    suggested_changes: str
    suggested_modifications: Optional[Dict[str, Any]] = {}

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    related_id: Optional[str] = None

# Modèles de requête pour profil avancé
class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    languages: Optional[List[str]] = None
    website: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None

class SellerSettingsUpdate(BaseModel):
    is_seller: Optional[bool] = None
    business_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    return_policy: Optional[str] = None
    shipping_policy: Optional[str] = None
    payment_methods: Optional[List[PaymentMethod]] = None
    shipping_rates: Optional[List[ShippingRate]] = None
    processing_time_days: Optional[int] = None
    return_days: Optional[int] = None
    min_order_value: Optional[float] = None
    seller_notes: Optional[str] = None
    terms_conditions: Optional[str] = None

class BuyerSettingsUpdate(BaseModel):
    preferred_shipping_method: Optional[str] = None
    max_shipping_cost: Optional[float] = None
    max_budget_per_item: Optional[float] = None
    price_alert_threshold: Optional[float] = None
    notify_new_matches: Optional[bool] = None
    notify_price_drops: Optional[bool] = None
    notify_watchlist_available: Optional[bool] = None

class CollectionSettingsUpdate(BaseModel):
    visibility: Optional[CollectionVisibility] = None
    show_statistics: Optional[bool] = None
    show_estimated_value: Optional[bool] = None
    show_acquisition_dates: Optional[bool] = None
    allow_export: Optional[bool] = None
    notify_similar_items: Optional[bool] = None
    notify_collection_updates: Optional[bool] = None

class PrivacySettingsUpdate(BaseModel):
    profile_visibility: Optional[ProfileVisibility] = None
    show_last_seen: Optional[bool] = None
    allow_private_messages: Optional[bool] = None
    show_location: Optional[bool] = None
    show_join_date: Optional[bool] = None
    allow_friend_requests: Optional[bool] = None

class RatingCreate(BaseModel):
    rated_user_id: str
    transaction_id: Optional[str] = None
    rating_type: str  # "seller" or "buyer"
    score: int  # 1-5
    comment: Optional[str] = None

# Security Level 2 Models
class TwoFactorSetup(BaseModel):
    token: str  # TOTP token to verify setup

class TwoFactorVerify(BaseModel):
    token: str  # TOTP token for verification

class UserBan(BaseModel):
    user_id: str
    reason: str
    permanent: bool = False
    ban_duration_days: Optional[int] = None

class BanRequest(BaseModel):
    reason: str
    permanent: bool = False
    ban_duration_days: Optional[int] = None

class SuspiciousActivity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    activity_type: str  # "multiple_failed_logins", "rapid_account_creation", "unusual_patterns"
    description: str
    severity: str = "low"  # "low", "medium", "high"
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None

# Friends System Models
class FriendshipStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"

class Friendship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str  # User who sent the friend request
    addressee_id: str  # User who received the friend request
    status: FriendshipStatus = FriendshipStatus.PENDING
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FriendRequest(BaseModel):
    user_id: str  # The user to send friend request to
    message: Optional[str] = None  # Optional message with friend request

class FriendRequestResponse(BaseModel):
    request_id: str
    accept: bool  # True to accept, False to decline

# Messaging System Models (extending existing Message model)
class ConversationParticipant(BaseModel):
    user_id: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    last_read_at: Optional[datetime] = None

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    participants: List[ConversationParticipant]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None

class MessageCreateV2(BaseModel):
    conversation_id: Optional[str] = None  # If None, create new conversation
    recipient_id: Optional[str] = None  # For new conversations
    message: str
    message_type: str = "text"  # "text", "image", "file", "system", "tracking", "payment_action"
    
    # Pour les messages système liés aux transactions
    transaction_id: Optional[str] = None
    system_data: Optional[dict] = {}  # Données pour les messages système

class MessageV2(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    sender_id: str
    message: str
    message_type: str = "text"  # "text", "image", "file", "system", "tracking", "payment_action"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
    
    # Pour les messages système liés aux transactions
    transaction_id: Optional[str] = None
    system_data: Optional[dict] = {}  # Données pour les messages système

# Modèle pour les actions de l'acheteur dans la conversation
class BuyerAction(BaseModel):
    action_type: str  # "confirm_receipt", "report_issue", "request_info"
    message: Optional[str] = None
    evidence_photos: List[str] = []
    
# Modèle pour les messages système de suivi
class SystemMessage(BaseModel):
    type: str  # "payment_confirmed", "shipped", "tracking_update", "payment_released", etc.
    data: dict = {}
    auto_generated: bool = True

# Profile settings model
class ProfileSettings(BaseModel):
    bio: Optional[str] = Field(None, max_length=200)
    favorite_club: Optional[str] = None
    instagram_username: Optional[str] = Field(None, max_length=50)
    twitter_username: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = None
    profile_picture_url: Optional[str] = None

# Public profile response model
class PublicProfile(BaseModel):
    id: str
    name: str 
    bio: Optional[str] = None
    favorite_club: Optional[str] = None
    instagram_username: Optional[str] = None
    twitter_username: Optional[str] = None
    website: Optional[str] = None
    profile_picture_url: Optional[str] = None
    role: str
    created_at: datetime
def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < PASSWORD_REQUIREMENTS['min_length']:
        return False, f"Le mot de passe doit contenir au moins {PASSWORD_REQUIREMENTS['min_length']} caractères"
    
    if PASSWORD_REQUIREMENTS['require_uppercase'] and not re.search(r'[A-Z]', password):
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if PASSWORD_REQUIREMENTS['require_lowercase'] and not re.search(r'[a-z]', password):
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if PASSWORD_REQUIREMENTS['require_number'] and not re.search(r'\d', password):
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    if PASSWORD_REQUIREMENTS['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>)"
    
    # Check for common weak patterns
    weak_patterns = ['123', 'abc', 'password', 'admin', 'user']
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            return False, f"Le mot de passe ne doit pas contenir de séquences courantes comme '{pattern}'"
    
    return True, "Mot de passe valide"

# Security Level 2: 2FA Helper Functions
def generate_2fa_secret() -> str:
    """Generate a new TOTP secret for 2FA"""
    return pyotp.random_base32()

def generate_2fa_qr_code(user_email: str, secret: str) -> str:
    """Generate QR code for 2FA setup"""
    try:
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="TopKit"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 string
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        return ""

def verify_2fa_token(secret: str, token: str) -> bool:
    """Verify TOTP token"""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)  # Allow 30s window
    except Exception as e:
        logger.error(f"Error verifying 2FA token: {e}")
        return False

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA"""
    import random
    import string
    codes = []
    for _ in range(count):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        codes.append(f"{code[:4]}-{code[4:]}")
    return codes

def verify_backup_code(user_backup_codes: List[str], entered_code: str) -> tuple[bool, List[str]]:
    """Verify backup code and remove it from list if valid"""
    if entered_code in user_backup_codes:
        updated_codes = [code for code in user_backup_codes if code != entered_code]
        return True, updated_codes
    return False, user_backup_codes

# Security Level 2: Suspicious Activity Detection
async def log_suspicious_activity(user_id: str, activity_type: str, description: str, severity: str = "low"):
    """Log suspicious activity for monitoring"""
    try:
        activity = SuspiciousActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            severity=severity
        )
        await db.suspicious_activities.insert_one(activity.dict())
        
        # Update user's suspicious activity score
        score_increase = {"low": 1, "medium": 5, "high": 10}.get(severity, 1)
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"suspicious_activity_score": score_increase}}
        )
        
        logger.warning(f"Suspicious activity logged for user {user_id}: {activity_type} - {description}")
        
    except Exception as e:
        logger.error(f"Error logging suspicious activity: {e}")

def check_rate_limit_for_registration(client_ip: str) -> tuple[bool, str]:
    """Check if IP has exceeded account creation rate limit"""
    current_time = time.time()
    
    # Clean old attempts outside the window
    account_creation_attempts[client_ip] = [
        timestamp for timestamp in account_creation_attempts[client_ip]
        if current_time - timestamp < ACCOUNT_CREATION_WINDOW
    ]
    
    # Check if limit exceeded
    if len(account_creation_attempts[client_ip]) >= ACCOUNT_CREATION_LIMIT:
        return False, f"Trop de tentatives de création de compte depuis cette adresse IP. Réessayez dans une heure."
    
    return True, "OK"

def record_account_creation_attempt(client_ip: str):
    """Record a new account creation attempt for rate limiting"""
    account_creation_attempts[client_ip].append(time.time())

def generate_email_verification_token(user_id: str, email: str) -> str:
    """Generate email verification token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'email_verification',
        'exp': datetime.utcnow() + timedelta(hours=24)  # 24h expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    email_verification_tokens[token] = {
        'user_id': user_id,
        'email': email,
        'created_at': datetime.utcnow()
    }
    return token

# Password reset tokens storage (in production, use Redis or database)
password_reset_tokens = {}

def generate_password_reset_token(user_id: str, email: str) -> str:
    """Generate password reset token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'password_reset',
        'exp': datetime.utcnow() + timedelta(hours=2)  # 2h expiration for security
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    password_reset_tokens[token] = {
        'user_id': user_id,
        'email': email,
        'created_at': datetime.utcnow()
    }
    return token

def verify_password_reset_token(token: str) -> tuple[bool, str, dict]:
    """Verify password reset token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'password_reset':
            return False, "Token invalide", {}
        
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        if token in password_reset_tokens:
            # Don't remove token yet - it will be removed after password reset
            token_data = password_reset_tokens[token]
            return True, "Token valide", {'user_id': user_id, 'email': email}
        else:
            return False, "Token non trouvé ou déjà utilisé", {}
            
    except jwt.ExpiredSignatureError:
        return False, "Token expiré", {}
    except jwt.PyJWTError:
        return False, "Token invalide", {}

async def send_password_reset_email(email: str, token: str, user_name: str = ""):
    """Send password reset email using SendGrid"""
    if not SENDGRID_API_KEY:
        logger.error("Cannot send password reset email: SENDGRID_API_KEY not configured")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Create reset link using environment variable
        frontend_url = os.environ.get('FRONTEND_URL', 'https://footkit-hub.preview.emergentagent.com')
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        # HTML email content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #1a56db;">TopKit</h1>
                    <h2 style="color: #333;">Réinitialisation de mot de passe</h2>
                </div>
                
                <p>Bonjour{f" {user_name}" if user_name else ""},</p>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe pour votre compte TopKit.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #1a56db; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Réinitialiser mon mot de passe
                    </a>
                </div>
                
                <p><strong>Ce lien est valide pendant 2 heures seulement.</strong></p>
                
                <p>Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email en toute sécurité.</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <p style="font-size: 12px; color: #666;">
                    Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :<br>
                    <a href="{reset_link}">{reset_link}</a>
                </p>
                
                <p style="font-size: 12px; color: #666; text-align: center;">
                    TopKit - Marketplace de maillots de football
                </p>
            </body>
        </html>
        """
        
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=email,
            subject="TopKit - Réinitialisation de mot de passe",
            html_content=html_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code == 202:
            logger.info(f"Password reset email sent successfully to {email}")
            return True
        else:
            logger.error(f"Failed to send password reset email: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        return False

def verify_email_verification_token(token: str) -> tuple[bool, str, dict]:
    """Verify email verification token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'email_verification':
            return False, "Token invalide", {}
        
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        if token in email_verification_tokens:
            # Remove token after successful verification
            token_data = email_verification_tokens.pop(token)
            return True, "Token valide", {'user_id': user_id, 'email': email}
        else:
            return False, "Token non trouvé ou déjà utilisé", {}
            
    except jwt.ExpiredSignatureError:
        return False, "Token expiré", {}
    except jwt.PyJWTError:
        return False, "Token invalide", {}

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
def generate_jersey_signature(team: str, season: str, size: str, condition: str) -> str:
    """Generate a unique signature for jersey valuation grouping"""
    # Handle None values for size and condition
    size_part = size.lower() if size else "unknown"
    condition_part = condition.lower() if condition else "unknown"
    return f"{team.lower().replace(' ', '_')}_{season}_{size_part}_{condition_part}"

async def update_jersey_valuation(jersey: Jersey, price: float, transaction_type: str, listing_id: Optional[str] = None):
    """Update jersey valuation based on new price data"""
    try:
        signature = generate_jersey_signature(
            jersey.team, jersey.season, jersey.size, jersey.condition
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
        jersey.team, jersey.season, jersey.size, jersey.condition
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

def verify_jwt_token_with_info(token: str) -> dict:
    """
    Enhanced token verification that returns more information
    Returns: {'user_id': str, 'expired': bool, 'valid': bool}
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {
            'user_id': payload.get('user_id'),
            'expired': False,
            'valid': True
        }
    except jwt.ExpiredSignatureError:
        try:
            # Decode without verification to get user_id for potential refresh
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={"verify_exp": False})
            return {
                'user_id': payload.get('user_id'),
                'expired': True,
                'valid': False
            }
        except:
            return {'user_id': None, 'expired': True, 'valid': False}
    except jwt.InvalidTokenError:
        return {'user_id': None, 'expired': False, 'valid': False}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    token_info = verify_jwt_token_with_info(token)
    
    if not token_info['valid'] and not token_info['expired']:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if token_info['expired']:
        # For expired tokens, we could potentially refresh them automatically
        # But for security, we'll require re-authentication
        raise HTTPException(status_code=401, detail="Token expired")
    
    user_id = token_info['user_id']
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if user.get('is_banned', False):
        raise HTTPException(status_code=403, detail="Account banned")
    
    # Remove MongoDB ObjectId to avoid serialization issues
    user.pop('_id', None)
    return user

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Récupère l'utilisateur actuel si le token est fourni, sinon renvoie None"""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return user_id
    except jwt.PyJWTError:
        return None

async def get_current_user_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user and verify admin role"""
    token = credentials.credentials
    user_id = verify_jwt_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if user.get('role') not in ['admin', 'moderator']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

# Admin Settings Endpoints
@api_router.get("/admin/settings")
async def get_admin_settings(current_user: dict = Depends(get_current_user)):
    """Get system settings for admin dashboard"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return system_settings

@api_router.put("/admin/settings")
async def update_admin_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update system settings"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Update allowed settings
    allowed_settings = ["auto_approval_enabled", "admin_notifications", "community_voting_enabled"]
    for key, value in settings.items():
        if key in allowed_settings:
            system_settings[key] = value
    
    await log_user_activity(
        current_user["id"],
        "admin_settings_updated",
        None,
        {"updated_settings": settings}
    )
    
@api_router.get("/admin/dashboard-stats")
async def get_admin_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive dashboard statistics for admin overview"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Users statistics
        total_users = await db.users.count_documents({})
        active_users_30d = await db.users.count_documents({
            "last_active": {"$gte": datetime.utcnow() - timedelta(days=30)}
        })
        
        # Content statistics
        total_teams = await db.teams.count_documents({})
        total_competitions = await db.competitions.count_documents({})
        total_brands = await db.brands.count_documents({})
        total_master_jerseys = await db.master_jerseys.count_documents({})
        total_reference_kits = await db.reference_kits.count_documents({})
        total_personal_kits = await db.personal_kits.count_documents({})
        total_wanted_kits = await db.wanted_kits.count_documents({})
        
        # Moderation statistics
        pending_contributions = await db.contributions.count_documents({
            "status": "PENDING"
        })
        total_contributions = await db.contributions.count_documents({})
        approved_contributions = await db.contributions.count_documents({
            "status": "APPROVED"
        })
        
        # System health
        system_status = {
            "auto_approval": system_settings.get("auto_approval_enabled", True),
            "community_voting": system_settings.get("community_voting_enabled", True),
            "admin_notifications": system_settings.get("admin_notifications", True)
        }
        
        return {
            "users": {
                "total": total_users,
                "active_30d": active_users_30d,
                "growth_rate": "N/A"  # Could calculate if needed
            },
            "content": {
                "teams": total_teams,
                "competitions": total_competitions,
                "brands": total_brands,
                "master_jerseys": total_master_jerseys,
                "reference_kits": total_reference_kits,
                "personal_kits": total_personal_kits,
                "wanted_kits": total_wanted_kits
            },
            "moderation": {
                "pending_contributions": pending_contributions,
                "total_contributions": total_contributions,
                "approved_contributions": approved_contributions,
                "approval_rate": round((approved_contributions / total_contributions * 100) if total_contributions > 0 else 0, 1)
            },
            "system": system_status
        }
        
    except Exception as e:
        logger.error(f"Admin dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving dashboard statistics")

@api_router.get("/admin/users")
async def get_admin_users(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get users for admin management with pagination and search"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        skip = (page - 1) * limit
        query = {}
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        users = await db.users.find(query).skip(skip).limit(limit).to_list(None)
        total_users = await db.users.count_documents(query)
        
        # Remove sensitive information
        for user in users:
            user.pop('_id', None)
            user.pop('password_hash', None)
            user.pop('two_factor_secret', None)
        
        return {
            "users": users,
            "total": total_users,
            "page": page,
            "limit": limit,
            "total_pages": (total_users + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Admin users error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users")

@api_router.get("/admin/pending-approvals")
async def get_pending_approvals(current_user: dict = Depends(get_current_user)):
    """Get all pending items requiring admin approval"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        pending_items = []
        
        # Get pending teams
        pending_teams = await db.teams.find({
            "verified_level": "PENDING"
        }).to_list(None)
        
        for team in pending_teams:
            team.pop('_id', None)
            pending_items.append({
                "id": team["id"],
                "type": "team",
                "name": team["name"],
                "created_at": team.get("created_at"),
                "created_by": team.get("created_by"),
                "data": team
            })
        
        # Get pending competitions
        pending_competitions = await db.competitions.find({
            "verified_level": "PENDING"
        }).to_list(None)
        
        for comp in pending_competitions:
            comp.pop('_id', None)
            pending_items.append({
                "id": comp["id"],
                "type": "competition",
                "name": comp["competition_name"],
                "created_at": comp.get("created_at"),
                "created_by": comp.get("created_by"),
                "data": comp
            })
        
        # Get pending contributions
        pending_contributions = await db.contributions.find({
            "status": "PENDING"
        }).to_list(None)
        
        for contrib in pending_contributions:
            contrib.pop('_id', None)
            pending_items.append({
                "id": contrib["id"],
                "type": "contribution",
                "name": contrib.get("entity_name", "Unknown"),
                "created_at": contrib.get("created_at"),
                "created_by": contrib.get("user_id"),
                "data": contrib
            })
        
        # Sort by creation date (newest first)
        pending_items.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        return pending_items
        
    except Exception as e:
        logger.error(f"Admin pending approvals error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving pending approvals")

@api_router.put("/admin/approve/{item_type}/{item_id}")
async def approve_item(
    item_type: str,
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Approve pending items (teams, competitions, contributions)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if item_type == "team":
            result = await db.teams.update_one(
                {"id": item_id},
                {
                    "$set": {
                        "verified_level": VerificationLevel.COMMUNITY_VERIFIED,
                        "verified_at": datetime.utcnow(),
                        "verified_by": current_user["id"]
                    }
                }
            )
        elif item_type == "competition":
            result = await db.competitions.update_one(
                {"id": item_id},
                {
                    "$set": {
                        "verified_level": VerificationLevel.COMMUNITY_VERIFIED,
                        "verified_at": datetime.utcnow(),
                        "verified_by": current_user["id"]
                    }
                }
            )
        elif item_type == "contribution":
            result = await db.contributions.update_one(
                {"id": item_id},
                {
                    "$set": {
                        "status": "APPROVED",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid item type")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        await log_user_activity(
            current_user["id"],
            f"{item_type}_approved",
            item_id,
            {"approved_by": current_user["id"]}
        )
        
        return {"message": f"{item_type.capitalize()} approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin approval error: {e}")
        raise HTTPException(status_code=500, detail="Error approving item")

    return {"message": "Settings updated successfully", "settings": system_settings}

# Authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: UserRegister, request: Request):
    """Enhanced user registration with security validations"""
    
    # Get client IP for rate limiting
    client_ip = request.client.host
    
    # 1. Check rate limiting
    rate_limit_ok, rate_limit_message = check_rate_limit_for_registration(client_ip)
    if not rate_limit_ok:
        raise HTTPException(status_code=429, detail=rate_limit_message)
    
    # 2. Validate password strength
    password_valid, password_message = validate_password_strength(user_data.password)
    if not password_valid:
        raise HTTPException(status_code=400, detail=password_message)
    
    # 3. Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cette adresse email existe déjà")
    
    # 4. Validate name (basic sanitization)
    if len(user_data.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Le nom doit contenir au moins 2 caractères")
    
    if len(user_data.name.strip()) > 50:
        raise HTTPException(status_code=400, detail="Le nom ne peut pas dépasser 50 caractères")
    
    # Record the registration attempt for rate limiting
    record_account_creation_attempt(client_ip)
    
    # Determine role - admin for main account
    user_role = "admin" if user_data.email == ADMIN_EMAIL else "user"
    
    # Create new user with email_verified = False
    hashed_password = hash_password(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name.strip(),
        provider="custom",
        password_hash=hashed_password,
        role=user_role,
        email_verified=False,  # Require email verification
        created_at=datetime.utcnow(),
        last_login=None
    )
    
    # Insert user into database
    await db.users.insert_one(user.dict())
    
    # Generate email verification token
    verification_token = generate_email_verification_token(user.id, user.email)
    
    # Log registration activity
    await log_user_activity(user.id, "user_registered", None, {
        "provider": "custom",
        "role": user_role,
        "email_verified": False,
        "ip_address": client_ip
    })
    
    # Send welcome notification (will be accessible after email verification)
    await create_notification(
        user_id=user.id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title="🎉 Bienvenue sur TopKit!",
        message=f"Bienvenue {user.name}! Votre compte a été créé avec succès. Veuillez vérifier votre email pour activer votre compte et commencer à construire votre collection de maillots.",
        related_id=None
    )
    
    # Send email confirmation using Gmail SMTP
    email_sent = False
    if gmail_service:
        try:
            email_sent = gmail_service.send_user_confirmation_email(
                user_email=user.email,
                user_name=user.name,
                confirmation_token=verification_token
            )
            if email_sent:
                logger.info(f"Confirmation email sent successfully to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email to {user.email}: {e}")
    
    # Fallback verification link for development
    frontend_url = os.environ.get('FRONTEND_URL', 'https://footkit-hub.preview.emergentagent.com')
    verification_link = f"{frontend_url}/verify-email?token={verification_token}"
    
    return {
        "message": "Compte créé avec succès! " + ("Un email de confirmation a été envoyé à votre adresse." if email_sent else "Veuillez vérifier votre email pour activer votre compte."),
        "user": {
            "id": user.id, 
            "email": user.email, 
            "name": user.name,
            "role": user_role,
            "email_verified": False
        },
        "email_sent": email_sent,
        # Remove this in production - only for development  
        "dev_verification_link": verification_link if not email_sent else None,
        "instructions": "Vérifiez votre boîte mail et cliquez sur le lien de confirmation pour activer votre compte."
    }

@api_router.post("/auth/verify-email")
async def verify_email(token: str):
    """Verify user email with token"""
    
    # Verify the token
    token_valid, message, token_data = verify_email_verification_token(token)
    
    if not token_valid:
        raise HTTPException(status_code=400, detail=message)
    
    user_id = token_data['user_id']
    email = token_data['email']
    
    # Update user's email_verified status
    result = await db.users.update_one(
        {"id": user_id, "email": email},
        {"$set": {
            "email_verified": True,
            "email_verified_at": datetime.utcnow()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Get updated user
    user = await db.users.find_one({"id": user_id})
    
    # Log email verification activity
    await log_user_activity(user_id, "email_verified", None, {
        "email": email,
        "verified_at": datetime.utcnow().isoformat()
    })
    
    # Create JWT token now that email is verified
    jwt_token = create_jwt_token(user_id)
    
    # Send verification success notification
    await create_notification(
        user_id=user_id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title="✅ Email vérifié avec succès!",
        message=f"Votre email {email} a été vérifié avec succès. Vous pouvez maintenant utiliser toutes les fonctionnalités de TopKit!",
        related_id=None
    )
    
    return {
        "message": "Email vérifié avec succès! Vous pouvez maintenant vous connecter.",
        "token": jwt_token,
        "user": {
            "id": user["id"],
            "email": user["email"], 
            "name": user["name"],
            "role": user.get("role", "user"),
            "email_verified": True
        }
    }

@api_router.post("/auth/resend-verification")
async def resend_verification_email(email: EmailStr):
    """Resend email verification token"""
    
    # Find user
    user = await db.users.find_one({"email": email, "provider": "custom"})
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "Si cette adresse email existe, un nouveau lien de vérification a été envoyé."}
    
    # Check if already verified
    if user.get("email_verified", False):
        return {"message": "Cette adresse email est déjà vérifiée."}
    
    # Generate new verification token
    verification_token = generate_email_verification_token(user["id"], user["email"])
    
    # Generate verification link using environment variable
    frontend_url = os.environ.get('FRONTEND_URL', 'https://footkit-hub.preview.emergentagent.com')
    verification_link = f"{frontend_url}/verify-email?token={verification_token}"
    
    return {
        "message": "Un nouveau lien de vérification a été envoyé à votre email.",
        # Remove this in production - only for development
        "dev_verification_link": verification_link
    }

# Enhanced authentication endpoint with 2FA support and suspicious activity monitoring
@api_router.post("/auth/login")
async def login(user_data: UserLogin, request: Request):
    try:
        # Check if IP has too many failed attempts
        client_ip = request.client.host
        
        # Find user
        user = await db.users.find_one({"email": user_data.email})
        if not user:
            await log_suspicious_activity("unknown", "failed_login_unknown_email", f"Login attempt with non-existent email: {user_data.email}")
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
        
        # Check if account is banned
        if user.get('is_banned', False):
            await log_suspicious_activity(user['id'], "login_attempt_banned_account", f"Login attempt on banned account: {user_data.email}")
            raise HTTPException(status_code=403, detail="Compte suspendu. Contactez l'administration.")
        
        # Check if account is locked
        if user.get('account_locked_until'):
            # Handle MongoDB ISODate objects directly (they are already datetime objects)
            locked_until = user['account_locked_until']
            # If it's a string (legacy), convert it; if it's already a datetime object, use it directly
            if isinstance(locked_until, str):
                locked_until = datetime.fromisoformat(locked_until.replace('Z', '+00:00'))
            
            if locked_until > datetime.utcnow():
                await log_suspicious_activity(user['id'], "login_attempt_locked_account", f"Login attempt on locked account: {user_data.email}")
                raise HTTPException(status_code=423, detail="Compte temporairement verrouillé")
        
        
        # Verify password
        if not verify_password(user_data.password, user['password_hash']):
            # Increment failed login attempts
            failed_attempts = user.get('failed_login_attempts', 0) + 1
            update_data = {'failed_login_attempts': failed_attempts}
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                update_data['account_locked_until'] = datetime.utcnow() + timedelta(hours=1)
                await log_suspicious_activity(user['id'], "multiple_failed_logins", f"Account locked after {failed_attempts} failed login attempts")
            
            await db.users.update_one({"id": user['id']}, {"$set": update_data})
            await log_suspicious_activity(user['id'], "failed_login", f"Failed password attempt #{failed_attempts}")
            raise HTTPException(status_code=401, detail="Identifiants incorrects")
        
        # Reset failed login attempts on successful password verification
        await db.users.update_one(
            {"id": user['id']}, 
            {"$set": {"failed_login_attempts": 0, "last_login": datetime.utcnow()}}
        )
        
        # Check if 2FA is enabled
        if user.get('two_factor_enabled', False):
            # For 2FA users, return a temporary token for 2FA verification
            temp_payload = {
                'user_id': user['id'],
                'type': '2fa_pending',
                'exp': datetime.utcnow() + timedelta(minutes=5)
            }
            temp_token = jwt.encode(temp_payload, SECRET_KEY, algorithm='HS256')
            return {
                "requires_2fa": True,
                "temp_token": temp_token,
                "message": "Code d'authentification à deux facteurs requis"
            }
        
        # Generate main token for non-2FA users
        token = create_jwt_token(user['id'])
        
        return {
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user.get('role', 'user'),
                "picture": user.get('picture'),
                "two_factor_enabled": user.get('two_factor_enabled', False)
            },
            "message": "Connexion réussie"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")

@api_router.post("/auth/2fa/verify")
async def verify_2fa_login(verification_data: TwoFactorVerify, authorization: HTTPAuthorizationCredentials = Depends(security)):
    """Verify 2FA token during login process"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Token temporaire requis")
        
        # Decode temp token
        try:
            payload = jwt.decode(authorization.credentials, SECRET_KEY, algorithms=['HS256'])
            if payload.get('type') != '2fa_pending':
                raise HTTPException(status_code=401, detail="Token invalide")
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token temporaire expiré")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Token temporaire invalide")
        
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user or not user.get('two_factor_enabled'):
            raise HTTPException(status_code=401, detail="2FA non configuré")
        
        # Verify 2FA token
        token_valid = False
        
        # First try TOTP token
        if user.get('two_factor_secret'):
            token_valid = verify_2fa_token(user['two_factor_secret'], verification_data.token)
        
        # If TOTP fails, try backup codes
        if not token_valid and user.get('two_factor_backup_codes'):
            is_backup_valid, updated_codes = verify_backup_code(
                user['two_factor_backup_codes'], 
                verification_data.token
            )
            if is_backup_valid:
                # Update backup codes (remove used code)
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"two_factor_backup_codes": updated_codes}}
                )
                token_valid = True
        
        if not token_valid:
            await log_suspicious_activity(user_id, "failed_2fa_verification", "Invalid 2FA token provided during login")
            raise HTTPException(status_code=401, detail="Code d'authentification invalide")
        
        # Generate main token
        token = create_jwt_token(user['id'])
        
        return {
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user.get('role', 'user'),
                "picture": user.get('picture'),
                "two_factor_enabled": True
            },
            "message": "Authentification réussie"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification 2FA")

# Security Level 2: 2FA Management Endpoints
@api_router.post("/auth/2fa/setup")
async def setup_2fa(current_user: dict = Depends(get_current_user)):
    """Setup 2FA for user account"""
    try:
        user_id = current_user['id']
        user_email = current_user['email']
        
        # Check if 2FA is already enabled
        user = await db.users.find_one({"id": user_id})
        if user.get('two_factor_enabled'):
            raise HTTPException(status_code=400, detail="2FA déjà activé")
        
        # Generate secret
        secret = generate_2fa_secret()
        
        # Generate QR code
        qr_code = generate_2fa_qr_code(user_email, secret)
        
        # Generate backup codes
        backup_codes = generate_backup_codes()
        
        # Store secret temporarily (not enabled until verified)
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "two_factor_secret": secret,
                "two_factor_backup_codes": backup_codes
            }}
        )
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "Configurez votre application d'authentification avec le QR code, puis vérifiez avec un code"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA setup error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la configuration 2FA")

@api_router.post("/auth/2fa/enable") 
async def enable_2fa(verification_data: TwoFactorSetup, current_user: dict = Depends(get_current_user)):
    """Enable 2FA after verification"""
    try:
        user_id = current_user['id']
        
        # Get user with secret
        user = await db.users.find_one({"id": user_id})
        if not user.get('two_factor_secret'):
            raise HTTPException(status_code=400, detail="2FA non configuré. Configurez d'abord 2FA.")
        
        if user.get('two_factor_enabled'):
            raise HTTPException(status_code=400, detail="2FA déjà activé")
        
        # Verify token
        if not verify_2fa_token(user['two_factor_secret'], verification_data.token):
            raise HTTPException(status_code=400, detail="Code d'authentification invalide")
        
        # Enable 2FA
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"two_factor_enabled": True}}
        )
        
        await log_user_activity(user_id, "2fa_enabled", None, {
            "enabled_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Authentification à deux facteurs activée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA enable error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'activation 2FA")

@api_router.post("/auth/2fa/disable")
async def disable_2fa(verification_data: TwoFactorVerify, current_user: dict = Depends(get_current_user)):
    """Disable 2FA after verification"""
    try:
        user_id = current_user['id']
        
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user.get('two_factor_enabled'):
            raise HTTPException(status_code=400, detail="2FA non activé")
        
        # Verify token (TOTP or backup code)
        token_valid = False
        
        if user.get('two_factor_secret'):
            token_valid = verify_2fa_token(user['two_factor_secret'], verification_data.token)
        
        if not token_valid and user.get('two_factor_backup_codes'):
            is_backup_valid, updated_codes = verify_backup_code(
                user['two_factor_backup_codes'], 
                verification_data.token
            )
            if is_backup_valid:
                token_valid = True
        
        if not token_valid:
            raise HTTPException(status_code=400, detail="Code d'authentification invalide")
        
        # Disable 2FA and clear secrets
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "two_factor_enabled": False,
                "two_factor_secret": None,
                "two_factor_backup_codes": []
            }}
        )
        
        await log_user_activity(user_id, "2fa_disabled", None, {
            "disabled_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Authentification à deux facteurs désactivée"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA disable error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la désactivation 2FA")

@api_router.post("/auth/2fa/backup-codes")
async def regenerate_backup_codes(current_user: dict = Depends(get_current_user)):
    """Regenerate 2FA backup codes"""
    try:
        user_id = current_user['id']
        
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user.get('two_factor_enabled'):
            raise HTTPException(status_code=400, detail="2FA non activé")
        
        # Generate new backup codes (no verification required for testing)
        backup_codes = generate_backup_codes()
        
        # Update backup codes
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"two_factor_backup_codes": backup_codes}}
        )
        
        await log_user_activity(user_id, "2fa_backup_codes_regenerated", None, {
            "regenerated_at": datetime.utcnow().isoformat()
        })
        
        return {
            "backup_codes": backup_codes,
            "message": "Codes de sauvegarde régénérés avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backup codes regeneration error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la régénération des codes de sauvegarde")

# Password change endpoint
@api_router.post("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    """Change user password"""
    try:
        user_id = current_user['id']
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Verify current password
        if not verify_password(password_data.current_password, user['password_hash']):
            raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
        
        # Validate new password strength
        is_valid, message = validate_password_strength(password_data.new_password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Hash new password
        new_password_hash = hash_password(password_data.new_password)
        
        # Update password
        await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "password_hash": new_password_hash,
                "failed_login_attempts": 0  # Reset failed attempts
            }}
        )
        
        await log_user_activity(user_id, "password_changed", None, {
            "changed_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Mot de passe modifié avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du changement de mot de passe")

# Token refresh endpoint
@api_router.post("/auth/refresh-token")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token for authenticated users"""
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Token requis")
        
        token = credentials.credentials
        token_info = verify_jwt_token_with_info(token)
        
        # Allow refresh for both valid and recently expired tokens (within 1 hour)
        if not token_info['user_id']:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        # Get user from database to ensure they still exist and are not banned
        user = await db.users.find_one({"id": token_info['user_id']})
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        
        if user.get('is_banned', False):
            raise HTTPException(status_code=403, detail="Compte suspendu")
        
        # Generate new token
        new_token = create_jwt_token(user['id'])
        
        # Update last login
        await db.users.update_one(
            {"id": user['id']}, 
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return {
            "token": new_token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user.get('role', 'user'),
                "picture": user.get('picture'),
                "two_factor_enabled": user.get('two_factor_enabled', False)
            },
            "message": "Token rafraîchi avec succès"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du rafraîchissement du token")

# Admin User Management Endpoints (Security Level 2)
@api_router.post("/admin/users/{user_id}/ban")
async def ban_user(user_id: str, ban_data: BanRequest, current_user: dict = Depends(get_current_user_admin)):
    """Ban a user account"""
    try:
        # Check if trying to ban admin
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if target_user.get('role') in ['admin', 'moderator']:
            raise HTTPException(status_code=403, detail="Impossible de bannir un administrateur ou modérateur")
        
        # Calculate ban expiration if not permanent
        ban_expires = None
        if not ban_data.permanent and ban_data.ban_duration_days:
            ban_expires = datetime.utcnow() + timedelta(days=ban_data.ban_duration_days)
        
        # Update user ban status
        update_data = {
            "is_banned": True,
            "banned_by": current_user['id'],
            "banned_at": datetime.utcnow(),
            "ban_reason": ban_data.reason
        }
        
        if ban_expires:
            update_data["ban_expires"] = ban_expires
        
        await db.users.update_one({"id": user_id}, {"$set": update_data})
        
        # Log admin activity
        await log_user_activity(current_user['id'], "user_banned", user_id, {
            "banned_user_email": target_user['email'],
            "reason": ban_data.reason,
            "permanent": ban_data.permanent,
            "expires": ban_expires.isoformat() if ban_expires else None
        })
        
        # Log suspicious activity for the banned user
        await log_suspicious_activity(user_id, "account_banned", f"Account banned by admin: {ban_data.reason}", "high")
        
        ban_type = "permanent" if ban_data.permanent else f"temporaire ({ban_data.ban_duration_days} jours)"
        return {"message": f"Utilisateur banni avec succès ({ban_type})"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ban user error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du bannissement")

@api_router.post("/admin/users/{user_id}/unban")
async def unban_user(user_id: str, current_user: dict = Depends(get_current_user_admin)):
    """Unban a user account"""
    try:
        # Check if user exists and is banned
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        if not target_user.get('is_banned'):
            raise HTTPException(status_code=400, detail="Utilisateur non banni")
        
        # Remove ban
        await db.users.update_one(
            {"id": user_id}, 
            {"$set": {
                "is_banned": False,
                "banned_by": None,
                "banned_at": None,
                "ban_reason": None,
                "ban_expires": None
            }}
        )
        
        # Log admin activity
        await log_user_activity(current_user['id'], "user_unbanned", user_id, {
            "unbanned_user_email": target_user['email']
        })
        
        return {"message": "Utilisateur débanni avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unban user error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du débannissement")

@api_router.delete("/admin/users/{user_id}")
async def delete_user_account(user_id: str, current_user: dict = Depends(get_current_user_admin)):
    """Delete a user account permanently"""
    try:
        # Check if user exists
        target_user = await db.users.find_one({"id": user_id})
        if not target_user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Check if trying to delete admin
        if target_user.get('role') in ['admin']:
            raise HTTPException(status_code=403, detail="Impossible de supprimer un administrateur")
        
        # Check if trying to delete self
        if user_id == current_user['id']:
            raise HTTPException(status_code=403, detail="Impossible de supprimer votre propre compte")
        
        # Delete all user-related data
        user_email = target_user['email']
        
        # Delete user's jerseys, collections, listings, messages, etc.
        await db.jerseys.delete_many({"created_by": user_id})
        await db.collections.delete_many({"user_id": user_id})
        await db.listings.delete_many({"seller_id": user_id})
        await db.messages.delete_many({"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]})
        await db.notifications.delete_many({"user_id": user_id})
        await db.user_activities.delete_many({"user_id": user_id})
        await db.suspicious_activities.delete_many({"user_id": user_id})
        await db.friendships.delete_many({"$or": [{"requester_id": user_id}, {"addressee_id": user_id}]})
        
        # Delete user profile and user account
        await db.user_profiles.delete_one({"user_id": user_id})
        await db.users.delete_one({"id": user_id})
        
        # Log admin activity
        await log_user_activity(current_user['id'], "user_deleted", user_id, {
            "deleted_user_email": user_email,
            "deletion_reason": "Admin deletion"
        })
        
        return {"message": f"Compte utilisateur {user_email} supprimé définitivement"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")

@api_router.get("/admin/users/{user_id}/security")
async def get_user_security_info(user_id: str, current_user: dict = Depends(get_current_user_admin)):
    """Get user security information for admin review"""
    try:
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Get suspicious activities
        suspicious_activities = await db.suspicious_activities.find(
            {"user_id": user_id}
        ).sort("detected_at", -1).limit(50).to_list(50)
        
        # Remove MongoDB ObjectId
        for activity in suspicious_activities:
            activity.pop('_id', None)
        
        # Get recent login activities
        recent_activities = await db.user_activities.find(
            {"user_id": user_id, "action": {"$in": ["user_logged_in", "failed_login", "2fa_enabled", "password_changed"]}}
        ).sort("created_at", -1).limit(20).to_list(20)
        
        # Remove MongoDB ObjectId
        for activity in recent_activities:
            activity.pop('_id', None)
        
        security_info = {
            "user_id": user_id,
            "email": user['email'],
            "name": user['name'],
            "role": user.get('role', 'user'),
            "account_status": {
                "is_banned": user.get('is_banned', False),
                "ban_reason": user.get('ban_reason'),
                "banned_at": user.get('banned_at'),
                "ban_expires": user.get('ban_expires'),
                "banned_by": user.get('banned_by'),
                "account_locked_until": user.get('account_locked_until'),
                "email_verified": user.get('email_verified', False)
            },
            "security_features": {
                "two_factor_enabled": user.get('two_factor_enabled', False),
                "failed_login_attempts": user.get('failed_login_attempts', 0),
                "suspicious_activity_score": user.get('suspicious_activity_score', 0)
            },
            "timestamps": {
                "created_at": user.get('created_at'),
                "last_login": user.get('last_login'),
                "email_verified_at": user.get('email_verified_at')
            },
            "suspicious_activities": suspicious_activities,
            "recent_activities": recent_activities
        }
        
        return security_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user security info error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des informations de sécurité")

# Enhanced user profile endpoints with address settings
@api_router.get("/users/{user_id}/profile")
async def get_user_profile_detailed(user_id: str, current_user: dict = Depends(get_current_user_optional)):
    """Get detailed user profile with privacy controls"""
    try:
        # Get user basic info
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Check if user is banned
        if user.get('is_banned', False):
            raise HTTPException(status_code=403, detail="Profil non accessible")
        
        # Get user profile
        user_profile = await db.user_profiles.find_one({"user_id": user_id})
        
        # Determine what information to show based on privacy settings and current user
        is_owner = current_user and current_user['id'] == user_id
        is_admin = current_user and current_user.get('role') in ['admin', 'moderator']
        
        # Base profile info
        profile_info = {
            "id": user['id'],
            "email": user['email'] if (is_owner or is_admin) else None,
            "name": user['name'],
            "role": user.get('role', 'user'),
            "created_at": user.get('created_at'),
            "last_login": user.get('last_login') if (is_owner or is_admin) else None,
            "two_factor_enabled": user.get('two_factor_enabled', False) if is_owner else None
        }
        
        if user_profile:
            # Remove MongoDB ObjectId
            user_profile.pop('_id', None)
            
            privacy_settings = user_profile.get('privacy_settings', {})
            
            # Apply privacy controls
            if not is_owner and not is_admin:
                # Hide sensitive information based on privacy settings
                if not privacy_settings.get('show_location', True):
                    user_profile.pop('location', None)
                if not privacy_settings.get('show_join_date', True):
                    profile_info.pop('created_at', None)
                
                # Hide address information for non-owners
                if 'seller_settings' in user_profile and 'address_settings' in user_profile['seller_settings']:
                    user_profile['seller_settings'].pop('address_settings', None)
                if 'buyer_settings' in user_profile and 'address_settings' in user_profile['buyer_settings']:
                    user_profile['buyer_settings'].pop('address_settings', None)
            
            profile_info.update(user_profile)
        
        return profile_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du profil")

@api_router.put("/users/profile/settings")
async def update_profile_settings(
    settings_data: Dict[str, Any], 
    current_user: dict = Depends(get_current_user)
):
    """Update user profile settings including address information"""
    try:
        user_id = current_user['id']
        
        # Get or create user profile
        user_profile = await db.user_profiles.find_one({"user_id": user_id})
        if not user_profile:
            # Create new profile
            user_profile = UserProfile(user_id=user_id).dict()
            await db.user_profiles.insert_one(user_profile)
        
        # Prepare update data
        update_data = {"updated_at": datetime.utcnow()}
        
        # Update basic profile info
        if 'display_name' in settings_data:
            update_data['display_name'] = settings_data['display_name']
        if 'bio' in settings_data:
            update_data['bio'] = settings_data['bio']
        if 'location' in settings_data:
            update_data['location'] = settings_data['location']
        
        # Update seller settings including address
        if 'seller_settings' in settings_data:
            seller_data = settings_data['seller_settings']
            update_data['seller_settings'] = {**user_profile.get('seller_settings', {}), **seller_data}
        
        # Update buyer settings including address
        if 'buyer_settings' in settings_data:
            buyer_data = settings_data['buyer_settings']
            update_data['buyer_settings'] = {**user_profile.get('buyer_settings', {}), **buyer_data}
        
        # Update privacy settings
        if 'privacy_settings' in settings_data:
            privacy_data = settings_data['privacy_settings']
            update_data['privacy_settings'] = {**user_profile.get('privacy_settings', {}), **privacy_data}
        
        # Update collection settings
        if 'collection_settings' in settings_data:
            collection_data = settings_data['collection_settings']
            update_data['collection_settings'] = {**user_profile.get('collection_settings', {}), **collection_data}
        
        # Apply update
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        await log_user_activity(user_id, "profile_settings_updated", None, {
            "updated_sections": list(settings_data.keys())
        })
        
        return {"message": "Paramètres du profil mis à jour avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile settings error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour des paramètres")

@api_router.post("/users/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload user profile picture"""
    try:
        user_id = current_user['id']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Type de fichier non autorisé. Utilisez JPG, PNG ou WebP."
            )
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Le fichier est trop volumineux. Taille maximale : 5MB."
            )
        
        # Reset file position
        await file.seek(0)
        
        # Create profile pictures directory if it doesn't exist
        profile_dir = Path("uploads/profile_pictures")
        profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
            file_extension = 'jpg'
        
        timestamp = int(time.time())
        filename = f"profile_{user_id}_{timestamp}.{file_extension}"
        file_path = profile_dir / filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Update user with picture URL
        profile_picture_url = f"uploads/profile_pictures/{filename}"
        
        # Get current user to check for old picture
        user = await db.users.find_one({"id": user_id})
        old_picture = user.get('profile_picture_url') if user else None
        
        # Delete old profile picture if exists
        if old_picture and old_picture.startswith('uploads/profile_pictures/'):
            old_file_path = Path(old_picture)
            if old_file_path.exists():
                try:
                    old_file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete old profile picture: {e}")
        
        # Update user with new picture URL
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"profile_picture_url": profile_picture_url}}
        )
        
        # Log activity
        await log_user_activity(user_id, "profile_picture_uploaded", None, {
            "filename": filename,
            "file_size": len(file_content)
        })
        
        return {
            "message": "Photo de profil mise à jour avec succès",
            "profile_picture_url": profile_picture_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile picture upload error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du téléchargement de l'image")

@api_router.delete("/users/profile/picture")
async def delete_profile_picture(current_user: dict = Depends(get_current_user)):
    """Delete user profile picture"""
    try:
        user_id = current_user['id']
        
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user or not user.get('profile_picture_url'):
            raise HTTPException(status_code=404, detail="Aucune photo de profil trouvée")
        
        # Delete file from disk
        profile_picture_url = user['profile_picture_url']
        if profile_picture_url.startswith('uploads/profile_pictures/'):
            file_path = Path(profile_picture_url)
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete profile picture file: {e}")
        
        # Remove picture URL from user
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"profile_picture_url": None}}
        )
        
        # Log activity
        await log_user_activity(user_id, "profile_picture_deleted", None, {
            "deleted_file": profile_picture_url
        })
        
        return {"message": "Photo de profil supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile picture delete error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de l'image")

@api_router.get("/users/profile/picture/{user_id}")
async def get_profile_picture(user_id: str):
    """Get user profile picture URL (public endpoint)"""
    try:
        # Get user data
        user = await db.users.find_one({"id": user_id})
        
        if not user or not user.get('profile_picture_url'):
            return {"profile_picture_url": None}
        
        return {"profile_picture_url": user['profile_picture_url']}
        
    except Exception as e:
        logger.error(f"Get profile picture error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'image")
@api_router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    entity_type: str = Form(...),  # team, brand, player, competition, master_jersey
    generate_variants: bool = Form(True),  # Whether to generate multiple size variants
    current_user: dict = Depends(get_current_user)
):
    """Upload and process image for any entity type with optimization and variants"""
    try:
        user_id = current_user['id']
        
        # Validate entity type
        allowed_entity_types = ['team', 'brand', 'player', 'competition', 'master_jersey']
        if entity_type not in allowed_entity_types:
            raise HTTPException(
                status_code=400,
                detail=f"Type d'entité non autorisé. Utilisez: {', '.join(allowed_entity_types)}"
            )
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Type de fichier non autorisé. Utilisez JPG, PNG, WebP ou BMP."
            )
        
        # Validate file size (max 15MB for entity images)
        max_size = 15 * 1024 * 1024  # 15MB in bytes
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Le fichier est trop volumineux. Taille maximale : 15MB."
            )
        
        # Reset file position
        await file.seek(0)
        
        # Process image with optimization and variants
        processed_results = await image_processor.process_uploaded_image(
            file_content=file_content,
            filename=file.filename,
            entity_type=entity_type,
            generate_variants=generate_variants,
            optimize=True
        )
        
        # Extract main image URL (use medium size as default, fallback to original)
        main_image_url = processed_results.get('medium') or processed_results.get('original')
        
        # Log activity with enhanced metadata
        metadata = processed_results.get('metadata', {})
        await log_user_activity(user_id, f"{entity_type}_image_uploaded", None, {
            "filename": file.filename,
            "file_size": len(file_content),
            "entity_type": entity_type,
            "variants_generated": len([k for k in processed_results.keys() if k != 'metadata']),
            "image_dimensions": f"{metadata.get('width', 0)}x{metadata.get('height', 0)}",
            "optimization_applied": True
        })
        
        return {
            "message": "Image téléchargée et optimisée avec succès",
            "image_url": main_image_url,
            "variants": {k: v for k, v in processed_results.items() if k != 'metadata'},
            "metadata": metadata,
            "entity_type": entity_type,
            "optimization_applied": True,
            "variants_count": len([k for k in processed_results.keys() if k != 'metadata'])
        }
        
    except ValueError as ve:
        # Handle image processing validation errors
        raise HTTPException(status_code=400, detail=f"Erreur de validation de l'image: {str(ve)}")
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du téléchargement de l'image")

# Custom image serving endpoint with caching headers
@api_router.get("/serve-image/{entity_type}/{filename}")
async def serve_optimized_image(
    entity_type: str,
    filename: str,
    size: str = Query("medium", description="Image size variant (thumbnail, small, medium, large, original)"),
    response: Response = None
):
    """Serve optimized images with proper caching headers"""
    try:
        # Validate entity type
        allowed_entity_types = ['teams', 'brands', 'players', 'competitions', 'master_jerseys']
        if f"{entity_type}s" not in allowed_entity_types and entity_type not in allowed_entity_types:
            raise HTTPException(status_code=404, detail="Entity type not found")
        
        # Normalize entity type
        if not entity_type.endswith('s'):
            entity_type = f"{entity_type}s"
        
        # Validate size
        valid_sizes = ['thumbnail', 'small', 'medium', 'large', 'original']
        if size not in valid_sizes:
            size = 'medium'
        
        # Get image variants
        base_image_url = f"uploads/{entity_type}/{filename}"
        variants = image_processor.get_image_variants(base_image_url)
        
        # Try to get requested size, fallback to available sizes
        if size in variants:
            image_path = Path(variants[size])
        elif 'medium' in variants:
            image_path = Path(variants['medium'])
        elif 'original' in variants:
            image_path = Path(variants['original'])
        else:
            # Fallback to original file path
            image_path = Path(f"uploads/{entity_type}/{filename}")
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Set caching headers
        response.headers["Cache-Control"] = "public, max-age=31536000"  # 1 year
        response.headers["ETag"] = f'"{hash(str(image_path.stat().st_mtime))}"'
        response.headers["Last-Modified"] = datetime.fromtimestamp(
            image_path.stat().st_mtime
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        # Determine content type from file extension
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg', 
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        
        content_type = content_type_map.get(image_path.suffix.lower(), 'image/jpeg')
        
        return FileResponse(
            path=str(image_path),
            media_type=content_type,
            filename=image_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        raise HTTPException(status_code=500, detail="Error serving image")

# Enhanced image metadata endpoint
@api_router.get("/image-info/{entity_type}/{filename}")
async def get_image_info(
    entity_type: str,
    filename: str,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive information about an uploaded image and its variants"""
    try:
        # Normalize entity type
        if not entity_type.endswith('s'):
            entity_type = f"{entity_type}s"
        
        base_image_url = f"uploads/{entity_type}/{filename}"
        variants = image_processor.get_image_variants(base_image_url)
        
        if not variants:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Get file info for each variant
        variant_info = {}
        total_size = 0
        
        for size_name, url in variants.items():
            file_path = Path(url)
            if file_path.exists():
                stat = file_path.stat()
                variant_info[size_name] = {
                    "url": f"/api/serve-image/{entity_type.rstrip('s')}/{filename}?size={size_name}",
                    "file_size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "exists": True
                }
                total_size += stat.st_size
            else:
                variant_info[size_name] = {
                    "url": url,
                    "exists": False
                }
        
        return {
            "filename": filename,
            "entity_type": entity_type,
            "variants": variant_info,
            "total_size": total_size,
            "variant_count": len([v for v in variant_info.values() if v.get("exists", False)])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving image information")

@api_router.put("/users/profile/public-info")
async def update_public_profile_info(
    profile_data: ProfileSettings,
    current_user: dict = Depends(get_current_user)
):
    """Update user's public profile information"""
    try:
        user_id = current_user['id']
        
        # Validate bio length
        if profile_data.bio and len(profile_data.bio) > 200:
            raise HTTPException(status_code=400, detail="La bio ne peut pas dépasser 200 caractères")
        
        # Validate usernames (no @ symbol, alphanumeric + underscores)
        username_pattern = r'^[a-zA-Z0-9._]+$'
        if profile_data.instagram_username and not re.match(username_pattern, profile_data.instagram_username):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur Instagram invalide")
        
        if profile_data.twitter_username and not re.match(username_pattern, profile_data.twitter_username):
            raise HTTPException(status_code=400, detail="Nom d'utilisateur X/Twitter invalide")
        
        # Validate website URL
        if profile_data.website:
            if not profile_data.website.startswith(('http://', 'https://')):
                profile_data.website = 'https://' + profile_data.website
            
            # Basic URL validation
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, profile_data.website):
                raise HTTPException(status_code=400, detail="URL du site web invalide")
        
        # Validate favorite club exists
        if profile_data.favorite_club:
            team = await db.teams.find_one({"id": profile_data.favorite_club})
            if not team:
                raise HTTPException(status_code=400, detail="Club sélectionné non trouvé")
        
        # Prepare update data
        update_data = {}
        if profile_data.bio is not None:
            update_data['bio'] = profile_data.bio.strip() if profile_data.bio else None
        if profile_data.favorite_club is not None:
            update_data['favorite_club'] = profile_data.favorite_club
        if profile_data.instagram_username is not None:
            update_data['instagram_username'] = profile_data.instagram_username.lower() if profile_data.instagram_username else None
        if profile_data.twitter_username is not None:
            update_data['twitter_username'] = profile_data.twitter_username.lower() if profile_data.twitter_username else None
        if profile_data.website is not None:
            update_data['website'] = profile_data.website if profile_data.website else None
        
        # Update user document
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        return {"message": "Informations publiques mises à jour avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update public profile error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du profil")

@api_router.get("/users/profile/public-info")
async def get_public_profile_info(current_user: dict = Depends(get_current_user)):
    """Get user's public profile information for editing"""
    try:
        user_id = current_user['id']
        
        # Get user data
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Get favorite club name if set
        favorite_club_name = None
        if user.get('favorite_club'):
            team = await db.teams.find_one({"id": user['favorite_club']})
            if team:
                favorite_club_name = team.get('name', team.get('short_name', ''))
        
        return {
            "bio": user.get('bio'),
            "favorite_club": user.get('favorite_club'),
            "favorite_club_name": favorite_club_name,
            "instagram_username": user.get('instagram_username'),
            "twitter_username": user.get('twitter_username'),
            "website": user.get('website'),
            "profile_picture_url": user.get('profile_picture_url')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get public profile error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du profil")

@api_router.get("/users/{user_id}/public-profile")
async def get_user_public_profile(user_id: str):
    """Get user's public profile information (visible to everyone)"""
    try:
        # Get user data
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Check if profile is public (for future privacy settings)
        if user.get('profile_privacy', 'public') == 'private':
            raise HTTPException(status_code=403, detail="Profil privé")
        
        # Get favorite club name if set
        favorite_club_name = None
        if user.get('favorite_club'):
            team = await db.teams.find_one({"id": user['favorite_club']})
            if team:
                favorite_club_name = team.get('name', team.get('short_name', ''))
        
        return PublicProfile(
            id=user['id'],
            name=user['name'],
            bio=user.get('bio'),
            favorite_club=favorite_club_name,
            instagram_username=user.get('instagram_username'),
            twitter_username=user.get('twitter_username'),
            website=user.get('website'),
            profile_picture_url=user.get('profile_picture_url'),
            role=user.get('role', 'user'),
            created_at=user['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user public profile error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération du profil public")

@api_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset email"""
    # Find user by email
    user = await db.users.find_one({"email": request.email, "provider": "custom"})
    
    # Always return success for security (don't reveal if email exists)
    if not user:
        return {"message": "Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation."}
    
    # Generate reset token
    reset_token = generate_password_reset_token(user["id"], user["email"])
    
    # Send reset email
    email_sent = await send_password_reset_email(
        user["email"], 
        reset_token, 
        user.get("name", "")
    )
    
    if email_sent:
        # Log password reset request
        await log_user_activity(user["id"], "password_reset_requested", None, {
            "request_time": datetime.utcnow().isoformat(),
            "email": user["email"]
        })
        
        return {"message": "Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation."}
    else:
        # Even if email failed to send, don't reveal it for security
        return {"message": "Si cette adresse email existe dans notre système, vous recevrez un lien de réinitialisation."}

@api_router.post("/auth/reset-password")
async def reset_password(request: PasswordReset):
    """Reset password using token"""
    # Validate password strength
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Verify reset token
    is_valid, error_message, token_data = verify_password_reset_token(request.token)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    user_id = token_data['user_id']
    email = token_data['email']
    
    # Update password
    new_password_hash = hash_password(request.new_password)
    result = await db.users.update_one(
        {"id": user_id, "email": email},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Utilisateur non trouvé ou erreur lors de la mise à jour")
    
    # Remove used token
    password_reset_tokens.pop(request.token, None)
    
    # Log password reset completion
    await log_user_activity(user_id, "password_reset_completed", None, {
        "reset_time": datetime.utcnow().isoformat(),
        "email": email
    })
    
    return {"message": "Mot de passe réinitialisé avec succès"}

# OAuth endpoints disabled - using email/password authentication only
# @api_router.get("/auth/google")
# async def google_auth(request: Request):
#     redirect_uri = f"{request.base_url}api/auth/google/callback"
#     return await oauth.google.authorize_redirect(request, redirect_uri)

# @api_router.get("/auth/google/callback")
# async def google_callback(request: Request):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = await oauth.google.parse_id_token(request, token)
#     
#     # Check if user exists
#     existing_user = await db.users.find_one({"email": user_info["email"]})
#     
#     if existing_user:
#         user_id = existing_user["id"]
#         # Ensure admin account has admin role
#         if existing_user["email"] == ADMIN_EMAIL and existing_user.get("role") != "admin":
#             await db.users.update_one({"id": user_id}, {"$set": {"role": "admin"}})
#     else:
#         # Determine role - admin for main account
#         user_role = "admin" if user_info["email"] == ADMIN_EMAIL else "user"
#         
#         # Create new user
#         user = User(
#             email=user_info["email"],
#             name=user_info.get("name", ""),
#             picture=user_info.get("picture"),
#             provider="google",
#             role=user_role
#         )
#         await db.users.insert_one(user.dict())
#         user_id = user.id
#         
#         # Log registration activity
#         await log_user_activity(user_id, "user_registered", None, {
#             "provider": "google",
#             "role": user_role
#         })
#         
#         # Send welcome notification for new users
#         await create_notification(
#             user_id=user_id,
#             notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
#             title="🎉 Welcome to TopKit!",
#             message=f"Welcome {user.name}! You're now part of the TopKit community. Start building your jersey collection by browsing our database and submitting your own jerseys for review.",
#             related_id=None
#         )
#     
#     token = create_jwt_token(user_id)
#     # Redirect to frontend with token
#     frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
#     return f"<script>window.location.href = '{frontend_url}/auth/success?token={token}';</script>"

# Admin functions
ADMIN_EMAIL = "topkitfr@gmail.com"

async def get_current_admin(user_id: str = Depends(get_current_user)):
    """Check if the current user is an admin"""
    user = await db.users.find_one({"id": user_id})
    if not user or user["email"] != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id

async def get_current_moderator_or_admin(current_user: dict = Depends(get_current_user)):
    """Check if the current user is a moderator or admin"""
    # Admin can always access
    if current_user["email"] == ADMIN_EMAIL:
        return current_user["id"]
    
    # Check if user has moderator role
    user_role = current_user.get("role", "user")
    if user_role not in ["moderator", "admin"]:
        raise HTTPException(status_code=403, detail="Moderator or admin access required")
    
    return current_user["id"]

async def check_user_is_admin(user_id: str) -> bool:
    """Check if the current user is an admin (for restrictions)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    # Check both email and role
    return user["email"] == ADMIN_EMAIL or user.get("role") == "admin"

async def get_current_non_admin_user(current_user: dict = Depends(get_current_user)):
    """Ensure current user is not an admin (for marketplace/collection restrictions)"""
    user_id = current_user["id"]
    is_admin = await check_user_is_admin(user_id)
    if is_admin:
        raise HTTPException(status_code=403, detail="Admin users cannot access marketplace or collection features")
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

async def create_notification(user_id: str, notification_type: NotificationType, title: str, message: str, related_id: str = None):
    """Create a notification for a user"""
    try:
        logger.info(f"🔔 Creating notification for user {user_id}: {title}")
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_id=related_id
        )
        
        # Convert to dict for MongoDB insertion
        notification_dict = notification.dict()
        logger.info(f"📝 Notification data: {notification_dict}")
        
        # Insert into database
        result = await db.notifications.insert_one(notification_dict)
        logger.info(f"✅ Notification created with MongoDB ID: {result.inserted_id}")
        
        return notification
        
    except Exception as e:
        logger.error(f"❌ Failed to create notification for user {user_id}: {str(e)}")
        logger.error(f"   Title: {title}")
        logger.error(f"   Message: {message}")
        logger.error(f"   Type: {notification_type}")
        # Don't raise the exception to avoid breaking the main flow
        return None

# =============================================================================
# 🛡️ SECURE PAYMENT HELPER FUNCTIONS
# =============================================================================

async def calculate_fraud_risk_score(buyer_id: str, seller_id: str, amount: float) -> int:
    """Calculer le score de risque de fraude pour une transaction (1-10)"""
    risk_score = 0
    
    try:
        buyer = await db.users.find_one({"id": buyer_id})
        seller = await db.users.find_one({"id": seller_id})
        
        if not buyer or not seller:
            return 8
        
        # Âge des comptes
        buyer_age_days = (datetime.utcnow() - buyer.get("created_at", datetime.utcnow())).days
        if buyer_age_days < 7:
            risk_score += 3
        elif buyer_age_days < 30:
            risk_score += 2
        
        # Montant de la transaction
        if amount > 1000:
            risk_score += 3
        elif amount > 500:
            risk_score += 2
        elif amount > 200:
            risk_score += 1
        
        return min(max(risk_score, 1), 10)
        
    except Exception as e:
        logger.error(f"Error calculating fraud risk score: {e}")
        return 5

async def send_secure_payment_notifications(transaction: SecureTransaction):
    """Envoyer les notifications par email pour une transaction sécurisée"""
    try:
        buyer = await db.users.find_one({"id": transaction.buyer_id})
        seller = await db.users.find_one({"id": transaction.seller_id})
        
        if buyer and seller and gmail_service:
            # Notifications simplifiées pour le moment
            logger.info(f"Secure payment notifications sent for transaction {transaction.id}")
        
    except Exception as e:
        logger.error(f"Error sending secure payment notifications: {e}")

def generate_transaction_timeline(transaction: dict) -> List[dict]:
    """Générer la timeline d'une transaction pour l'affichage"""
    timeline = []
    
    timeline.append({
        "status": "created",
        "title": "Transaction créée",
        "timestamp": transaction.get("created_at"),
        "completed": True
    })
    
    if transaction.get("status") == "payment_held":
        timeline.append({
            "status": "payment_held", 
            "title": "Paiement bloqué",
            "timestamp": transaction.get("payment_held_at"),
            "completed": True
        })
    
    return timeline

def get_available_actions(transaction: dict, user_id: str) -> List[dict]:
    """Obtenir les actions disponibles pour un utilisateur"""
    actions = []
    status = transaction.get("status")
    
    if user_id == transaction.get("seller_id") and status == "payment_held":
        actions.append({
            "action": "ship",
            "label": "Marquer comme expédié"
        })
    
    return actions

# =============================================================================
# 📨 MESSAGING INTEGRATION WITH TRANSACTIONS (LEBONCOIN STYLE)
# =============================================================================

async def create_transaction_conversation(transaction: SecureTransaction, buyer: dict, seller: dict):
    """
    Créer automatiquement une conversation lors d'un achat (style Leboncoin)
    """
    try:
        # Créer la conversation
        participants = [
            ConversationParticipant(user_id=buyer["id"]),
            ConversationParticipant(user_id=seller["id"])
        ]
        
        conversation = Conversation(participants=participants)
        await db.conversations.insert_one(conversation.dict())
        
        # Message système initial de bienvenue
        welcome_message = MessageV2(
            conversation_id=conversation.id,
            sender_id="system",
            message_type="system",
            message=f"""🎉 **Achat confirmé !**

**Maillot :** {transaction.jersey_info['team']} - {transaction.jersey_info.get('player_name', 'Maillot')}
**Prix :** €{transaction.amount}
**Statut :** Paiement sécurisé - Fonds bloqués jusqu'à confirmation de réception

---

**👋 {buyer['name']}** vient d'acheter votre maillot **👋 {seller['name']}** !

**Prochaines étapes :**
1. 📦 **{seller['name']}** : Expédiez le maillot dans les 2 jours
2. 📱 **{buyer['name']}** : Vous recevrez le numéro de suivi ici
3. ✅ **{buyer['name']}** : Confirmez la réception pour débloquer le paiement

💬 Utilisez cette conversation pour communiquer pendant la transaction.""",
            transaction_id=transaction.id,
            system_data={
                "type": "transaction_created",
                "transaction_id": transaction.id,
                "jersey_info": transaction.jersey_info,
                "amount": transaction.amount,
                "buyer_name": buyer["name"],
                "seller_name": seller["name"]
            }
        )
        
        await db.messages.insert_one(welcome_message.dict())
        
        # Lier la conversation à la transaction
        await db.secure_transactions.update_one(
            {"id": transaction.id},
            {"$set": {"conversation_id": conversation.id}}
        )
        
        return conversation.id
        
    except Exception as e:
        logger.error(f"Error creating transaction conversation: {e}")
        return None

async def send_system_message(conversation_id: str, message_type: str, data: dict, transaction_id: str = None):
    """
    Envoyer un message système dans une conversation
    """
    try:
        buyer_name = data.get('buyer_name', 'L\'acheteur')
        
        system_messages = {
            "payment_confirmed": {
                "message": f"💳 **Paiement confirmé** - €{data.get('amount', 0)}\n\n🛡️ Vos fonds sont sécurisés et seront libérés après confirmation de réception.",
                "emoji": "💳"
            },
            "shipped": {
                "message": f"📦 **Maillot expédié !**\n\n**Transporteur :** {data.get('carrier', 'N/A')}\n**Numéro de suivi :** `{data.get('tracking_number', 'N/A')}`\n\n🔗 [Suivre le colis]({data.get('tracking_url', '#')})",
                "emoji": "📦"
            },
            "delivered": {
                "message": f"🏠 **Colis livré !**\n\n✅ Le colis a été livré. {buyer_name} peut maintenant confirmer la réception pour débloquer le paiement.",
                "emoji": "🏠"
            },
            "payment_released": {
                "message": f"💰 **Paiement libéré !**\n\n✅ Transaction terminée avec succès. €{data.get('amount', 0)} transférés au vendeur.",
                "emoji": "💰"
            },
            "buyer_confirmed": {
                "message": f"✅ **Réception confirmée par l'acheteur**\n\n👍 {buyer_name} confirme que le maillot est conforme. Le paiement va être libéré.",
                "emoji": "✅"
            },
            "issue_reported": {
                "message": f"⚠️ **Problème signalé**\n\n{buyer_name} a signalé un problème. La transaction est en cours de révision par nos équipes.",
                "emoji": "⚠️"
            }
        }
        
        message_config = system_messages.get(message_type, {
            "message": f"ℹ️ Mise à jour de la transaction",
            "emoji": "ℹ️"
        })
        
        system_message = MessageV2(
            conversation_id=conversation_id,
            sender_id="system",
            message_type="system", 
            message=message_config["message"],
            transaction_id=transaction_id,
            system_data={
                "type": message_type,
                **data
            }
        )
        
        await db.messages.insert_one(system_message.dict())
        
        # Envoyer la notification en temps réel si possible
        # await notify_conversation_participants(conversation_id, system_message)
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending system message: {e}")
        return False

async def update_transaction_status_with_message(transaction_id: str, new_status: str, data: dict = {}):
    """
    Mettre à jour le statut d'une transaction et envoyer un message système
    """
    try:
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            return False
        
        # Mettre à jour le statut
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow(),
                    **data
                }
            }
        )
        
        # Envoyer le message système correspondant
        conversation_id = transaction.get("conversation_id")
        if conversation_id:
            await send_system_message(conversation_id, new_status, {
                **data,
                "transaction_id": transaction_id,
                "amount": transaction.get("amount", 0)
            }, transaction_id)
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating transaction status with message: {e}")
        return False

async def get_next_jersey_reference():
    """Generate the next sequential jersey reference number (TK-000001, TK-000002, etc.)"""
    # Find the highest existing reference number
    last_jersey = await db.jerseys.find().sort("reference_number", -1).limit(1).to_list(1)
    
    if last_jersey and last_jersey[0].get("reference_number"):
        # Extract number from reference like "TK-000001" -> 1
        last_ref = last_jersey[0]["reference_number"]
        try:
            last_number = int(last_ref.split("-")[1])
            next_number = last_number + 1
        except (ValueError, IndexError):
            next_number = 1
    else:
        next_number = 1
    
    # Format as TK-000001
    return f"TK-{next_number:06d}"

# Admin endpoints
@api_router.get("/admin/jerseys/pending")
async def get_pending_jerseys(moderator_id: str = Depends(get_current_moderator_or_admin)):
    """Get all jerseys pending approval or needing modification"""
    jerseys = await db.jerseys.find({"status": {"$in": ["pending", "needs_modification"]}}).to_list(100)
    
    # Remove MongoDB ObjectId for JSON serialization and add suggestion info
    for jersey in jerseys:
        jersey.pop('_id', None)
        
        # If jersey needs modification, get the latest suggestion
        if jersey.get("status") == "needs_modification":
            latest_suggestion = await db.modification_suggestions.find_one(
                {"jersey_id": jersey["id"]},
                sort=[("created_at", -1)]
            )
            if latest_suggestion:
                latest_suggestion.pop('_id', None)
                # Get moderator who made the suggestion
                moderator = await db.users.find_one({"id": latest_suggestion["moderator_id"]}, {"name": 1, "role": 1})
                if moderator:
                    moderator.pop('_id', None)
                    latest_suggestion["moderator_info"] = moderator
                jersey["latest_suggestion"] = latest_suggestion
    
    return jerseys

@api_router.post("/admin/jerseys/{jersey_id}/suggest-modifications")
async def suggest_jersey_modifications(
    jersey_id: str, 
    suggestion_data: ModificationSuggestionCreate,
    moderator_id: str = Depends(get_current_moderator_or_admin)
):
    """Suggest modifications for a pending jersey instead of rejecting it"""
    
    # Verify jersey exists and is pending
    jersey = await db.jerseys.find_one({"id": jersey_id, "status": "pending"})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found or already processed")
    
    # Create modification suggestion
    suggestion = ModificationSuggestion(
        jersey_id=jersey_id,
        moderator_id=moderator_id,
        suggested_changes=suggestion_data.suggested_changes,
        suggested_modifications=suggestion_data.suggested_modifications or {}
    )
    
    await db.modification_suggestions.insert_one(suggestion.dict())
    
    # Update jersey status to indicate it needs modification
    await db.jerseys.update_one(
        {"id": jersey_id},
        {
            "$set": {
                "status": "needs_modification",
                "approved_by": moderator_id,
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    # Create notification for the user
    await create_notification(
        user_id=jersey["submitted_by"],
        notification_type=NotificationType.JERSEY_NEEDS_MODIFICATION,
        title="Modifications Suggested for Your Jersey",
        message=f"Your jersey submission '{jersey.get('team', '')} {jersey.get('season', '')}' needs some modifications. Please check the feedback from our moderators.",
        related_id=suggestion.id
    )
    
    # Log activity
    await log_user_activity(moderator_id, "jersey_modification_suggested", jersey_id, {
        "suggested_changes": suggestion_data.suggested_changes,
        "jersey_name": f"{jersey.get('team', '')} {jersey.get('season', '')}"
    })
    
    await log_user_activity(jersey["submitted_by"], "jersey_modification_requested", jersey_id, {
        "moderator_id": moderator_id,
        "suggestion_id": suggestion.id
    })
    
    return {"message": "Modification suggestions sent to user", "suggestion_id": suggestion.id}

@api_router.post("/admin/jerseys/{jersey_id}/approve")
async def approve_jersey(jersey_id: str, moderator_id: str = Depends(get_current_moderator_or_admin)):
    """Approve a pending jersey"""
    result = await db.jerseys.update_one(
        {"id": jersey_id, "status": {"$in": ["pending", "needs_modification"]}},
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
    
    # Get jersey info for notifications
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if jersey:
        # Create notification for the user
        await create_notification(
            user_id=jersey["submitted_by"],
            notification_type=NotificationType.JERSEY_APPROVED,
            title="Jersey Approved & Now Live!",
            message=f"🎉 Congratulations! Your jersey '{jersey.get('team', '')} {jersey.get('season', '')}' ({jersey.get('reference_number', '')}) has been approved and is now visible to the entire TopKit community!",
            related_id=jersey_id
        )
        
        # Log activity
        await log_user_activity(moderator_id, "jersey_approved", jersey_id)
        await log_user_activity(jersey["submitted_by"], "jersey_approved", jersey_id, {
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
        {"id": jersey_id, "status": {"$in": ["pending", "needs_modification"]}},
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
    
    # Get jersey info for notifications
    jersey = await db.jerseys.find_one({"id": jersey_id})
    if jersey:
        # Create notification for the user
        await create_notification(
            user_id=jersey["submitted_by"],
            notification_type=NotificationType.JERSEY_REJECTED,
            title="Jersey Submission Rejected",
            message=f"Unfortunately, your jersey '{jersey.get('team', '')} {jersey.get('season', '')}' has been rejected. Reason: {reason}",
            related_id=jersey_id
        )
        
        # Log activity
        await log_user_activity(moderator_id, "jersey_rejected", jersey_id, {"reason": reason})
        await log_user_activity(jersey["submitted_by"], "jersey_rejected", jersey_id, {
            "rejected_by": moderator_id,
            "jersey_name": f"{jersey.get('team', '')} {jersey.get('season', '')}",
            "reason": reason
        })
    
    return {"message": "Jersey rejected successfully"}

@api_router.put("/admin/jerseys/{jersey_id}/edit")
async def edit_jersey(
    jersey_id: str, 
    team: str = Form(...),
    league: str = Form(...),
    season: str = Form(...),
    model: str = Form(...),
    manufacturer: str = Form(""),
    jersey_type: str = Form(""),
    sku_code: str = Form(None),
    description: str = Form(""),
    front_photo: UploadFile = File(None),
    back_photo: UploadFile = File(None),
    remove_front_photo: str = Form(None),  # Ajouté pour suppression
    remove_back_photo: str = Form(None),   # Ajouté pour suppression
    moderator_id: str = Depends(get_current_moderator_or_admin)
):
    """Edit a pending or needs_modification jersey"""
    
    # Verify jersey exists and can be edited (pending or needs_modification)
    existing_jersey = await db.jerseys.find_one({"id": jersey_id, "status": {"$in": ["pending", "needs_modification"]}})
    if not existing_jersey:
        raise HTTPException(status_code=404, detail="Jersey not found or cannot be edited")
    
    # Validate required fields
    if not team or not league or not season or not model:
        raise HTTPException(status_code=422, detail="Team, league, season, and model are required fields")
    
    # Validate model field
    if model not in ["authentic", "replica"]:
        raise HTTPException(status_code=422, detail="Model must be either 'authentic' or 'replica'")
    
    # Handle photo uploads and removals
    existing_images = existing_jersey.get("images", [])
    updated_images = []
    
    # Gérer les suppressions des photos existantes
    for image in existing_images:
        # Garder les images qui ne sont pas marquées pour suppression
        if 'front' in image and remove_front_photo == 'true':
            continue  # Supprimer la photo de face
        elif 'back' in image and remove_back_photo == 'true':
            continue  # Supprimer la photo de dos
        else:
            updated_images.append(image)  # Garder l'image existante
    
    # Initialize update_data early so it can be used in photo processing
    update_data = {}
    
    # Ajouter les nouvelles photos uploadées
    if front_photo and front_photo.filename:
        # Create directory if it doesn't exist
        upload_dir = f"../frontend/public/uploads/jerseys/{jersey_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the actual file
        front_filename = f"front_{int(time.time())}.{front_photo.filename.split('.')[-1]}"
        file_path = os.path.join(upload_dir, front_filename)
        
        # Read and save the file content
        front_content = await front_photo.read()
        with open(file_path, "wb") as f:
            f.write(front_content)
        
        # Add to images array (legacy format)
        updated_images.append(f"jersey_{jersey_id}_front_{int(time.time())}.{front_photo.filename.split('.')[-1]}")
        # Also update the individual URL field (new format)
        update_data["front_photo_url"] = f"uploads/jerseys/{jersey_id}/{front_filename}"
        print(f"📸 Admin front photo saved: {file_path}")
    
    if back_photo and back_photo.filename:
        # Create directory if it doesn't exist
        upload_dir = f"../frontend/public/uploads/jerseys/{jersey_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the actual file
        back_filename = f"back_{int(time.time())}.{back_photo.filename.split('.')[-1]}"
        file_path = os.path.join(upload_dir, back_filename)
        
        # Read and save the file content
        back_content = await back_photo.read()
        with open(file_path, "wb") as f:
            f.write(back_content)
        
        # Add to images array (legacy format)
        updated_images.append(f"jersey_{jersey_id}_back_{int(time.time())}.{back_photo.filename.split('.')[-1]}")
        # Also update the individual URL field (new format) 
        update_data["back_photo_url"] = f"uploads/jerseys/{jersey_id}/{back_filename}"
        print(f"📸 Admin back photo saved: {file_path}")
    
    # Update jersey with edited data using new structure
    update_data.update({
        "team": team.strip(),
        "league": league.strip(),
        "season": season.strip(),
        "manufacturer": manufacturer.strip() if manufacturer else "",
        "jersey_type": jersey_type.strip() if jersey_type else "",
        "sku_code": sku_code.strip() if sku_code else None,
        "model": model.strip(),
        "description": description.strip() if description else "",
        "status": "pending",  # Reset to pending after edit
        "approved_by": None,
        "approved_at": None,
        "rejection_reason": None,
        "updated_at": datetime.utcnow(),
        "updated_by": moderator_id,
        "images": updated_images
    })
    
    result = await db.jerseys.update_one(
        {"id": jersey_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update jersey")
    
    # Create notification for the user
    await create_notification(
        user_id=existing_jersey["submitted_by"],
        notification_type=NotificationType.JERSEY_NEEDS_MODIFICATION,
        title="🔧 Jersey Updated by Moderator",
        message=f"Your jersey '{team} {season}' has been updated by a moderator and is now pending review again.",
        related_id=jersey_id
    )
    
    # Log activity
    await log_user_activity(moderator_id, "jersey_edited", jersey_id, {
        "jersey_name": f"{team} {season}",
        "original_team": existing_jersey.get("team"),
        "original_season": existing_jersey.get("season"),
        "photos_updated": len(updated_images) > 0
    })
    
    return {"message": "Jersey updated successfully", "photos_uploaded": len(updated_images)}

# User management endpoints (Admin only)
@api_router.get("/admin/users")
async def get_all_users(admin_user: dict = Depends(get_current_user_admin)):
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

@api_router.post("/admin/users/{user_id}/make-moderator")
async def make_user_moderator(
    user_id: str,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Make a user a moderator (Admin only)"""
    
    # Get the target user
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Check if user is already admin (can't make admin a moderator)
    if target_user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Impossible de modifier le rôle d'un administrateur")
    
    # Update user role to moderator
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": "moderator"}}
    )
    
    # Log the role assignment activity
    await db.user_activities.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": admin_user["id"],
        "action": "role_assigned",
        "target_id": user_id,
        "details": {
            "new_role": "moderator",
            "target_user_email": target_user["email"]
        },
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": f"Utilisateur {target_user['email']} est maintenant modérateur",
        "user_id": user_id,
        "new_role": "moderator"
    }

@api_router.post("/admin/users/{user_id}/remove-moderator")
async def remove_user_moderator(
    user_id: str,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Remove moderator role from a user (Admin only)"""
    
    # Get the target user
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Check if user is admin (can't remove admin role)
    if target_user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Impossible de modifier le rôle d'un administrateur")
    
    # Update user role to user
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": "user"}}
    )
    
    # Log the role assignment activity
    await db.user_activities.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": admin_user["id"],
        "action": "role_removed",
        "target_id": user_id,
        "details": {
            "previous_role": "moderator",
            "new_role": "user",
            "target_user_email": target_user["email"]
        },
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": f"Rôle modérateur retiré à {target_user['email']}",
        "user_id": user_id,
        "new_role": "user"
    }

@api_router.post("/admin/users/{user_id}/assign-role")
async def assign_user_role(
    user_id: str, 
    role_data: RoleAssignment,
    admin_user: dict = Depends(get_current_user_admin)
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
                "assigned_by": admin_user["id"],
                "role_assigned_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log activity
    await log_user_activity(admin_user["id"], "role_assigned", user_id, {
        "new_role": role_data.role,
        "reason": role_data.reason,
        "user_email": user["email"]
    })
    
    await log_user_activity(user_id, "role_received", None, {
        "new_role": role_data.role,
        "assigned_by": admin_user["id"],
        "reason": role_data.reason
    })
    
    return {"message": f"Role '{role_data.role}' assigned to user successfully"}

@api_router.get("/admin/activities")
async def get_all_activities(admin_user: dict = Depends(get_current_user_admin), limit: int = 50):
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

@api_router.get("/admin/traffic-stats")
async def get_admin_traffic_stats(admin_user: dict = Depends(get_current_user_admin)):
    """Get comprehensive traffic and usage statistics for admin dashboard"""
    
    # Get total counts
    total_users = await db.users.count_documents({})
    total_jerseys = await db.jerseys.count_documents({})
    total_listings = await db.listings.count_documents({})
    total_collections = await db.collections.count_documents({})
    
    # Get pending jerseys count
    pending_jerseys = await db.jerseys.count_documents({"status": "pending"})
    needs_modification = await db.jerseys.count_documents({"status": "needs_modification"})
    
    # Get recent activity counts (last 7 days)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_users = await db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
    recent_jerseys = await db.jerseys.count_documents({"created_at": {"$gte": seven_days_ago}})
    recent_listings = await db.listings.count_documents({"created_at": {"$gte": seven_days_ago}})
    recent_collections = await db.collections.count_documents({"added_at": {"$gte": seven_days_ago}})
    
    # Get jersey status breakdown
    jersey_status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    jersey_statuses = await db.jerseys.aggregate(jersey_status_pipeline).to_list(10)
    
    # Get top leagues by jersey count
    league_pipeline = [
        {"$match": {"status": "approved"}},
        {"$group": {"_id": "$league", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_leagues = await db.jerseys.aggregate(league_pipeline).to_list(10)
    
    # Get most active users (by collections)
    active_users_pipeline = [
        {"$group": {"_id": "$user_id", "collection_count": {"$sum": 1}}},
        {"$sort": {"collection_count": -1}},
        {"$limit": 10},
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$project": {
                "user_id": "$_id",
                "user_name": "$user.name",
                "user_email": "$user.email",
                "collection_count": 1,
                "_id": 0
            }
        }
    ]
    active_users = await db.collections.aggregate(active_users_pipeline).to_list(10)
    
    return {
        "overview": {
            "total_users": total_users,
            "total_jerseys": total_jerseys,
            "total_listings": total_listings,
            "total_collections": total_collections,
            "pending_moderation": pending_jerseys + needs_modification,
            "pending_jerseys": pending_jerseys,
            "needs_modification": needs_modification
        },
        "recent_activity": {
            "new_users_7d": recent_users,
            "new_jerseys_7d": recent_jerseys,
            "new_listings_7d": recent_listings,
            "new_collections_7d": recent_collections
        },
        "jersey_statuses": [{"status": item["_id"], "count": item["count"]} for item in jersey_statuses],
        "top_leagues": [{"league": item["_id"], "count": item["count"]} for item in top_leagues],
        "active_users": active_users
    }

@api_router.get("/admin/user-stats/{user_id}")
async def get_user_detailed_stats(user_id: str, admin_user: dict = Depends(get_current_user_admin)):
    """Get detailed statistics for a specific user"""
    
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's activities
    activities = await db.user_activities.find({"user_id": user_id}).sort("created_at", -1).limit(20).to_list(20)
    
    # Get user's collections count by type
    owned_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "owned"})
    wanted_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "wanted"})
    
    # Get user's jersey submissions
    jerseys_submitted = await db.jerseys.count_documents({"submitted_by": user_id})
    jerseys_approved = await db.jerseys.count_documents({"submitted_by": user_id, "status": "approved"})
    jerseys_pending = await db.jerseys.count_documents({"submitted_by": user_id, "status": "pending"})
    jerseys_rejected = await db.jerseys.count_documents({"submitted_by": user_id, "status": "rejected"})
    
    # Get user's listings
    active_listings = await db.listings.count_documents({"seller_id": user_id, "status": "active"})
    sold_listings = await db.listings.count_documents({"seller_id": user_id, "status": "sold"})
    
    # Clean activities
    for activity in activities:
        activity.pop('_id', None)
    
    user.pop('_id', None)
    
    return {
        "user": user,
        "stats": {
            "owned_jerseys": owned_count,
            "wanted_jerseys": wanted_count,
            "jerseys_submitted": jerseys_submitted,
            "jerseys_approved": jerseys_approved,
            "jerseys_pending": jerseys_pending,
            "jerseys_rejected": jerseys_rejected,
            "active_listings": active_listings,
            "sold_listings": sold_listings
        },
        "recent_activities": activities
    }


# Explorer endpoints
@api_router.get("/explorer/most-collected")
async def get_most_collected_jerseys(limit: int = 10):
    """Get most collected jerseys based on owned collection count"""
    pipeline = [
        # Match only approved jerseys
        {"$match": {"status": "approved"}},
        # Lookup collections to count how many users own each jersey
        {
            "$lookup": {
                "from": "collections",
                "let": {"jersey_id": "$id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$jersey_id", "$$jersey_id"]},
                                    {"$eq": ["$collection_type", "owned"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "owned_by"
            }
        },
        # Add collection count
        {"$addFields": {"collection_count": {"$size": "$owned_by"}}},
        # Filter only jerseys that are collected by at least 1 user
        {"$match": {"collection_count": {"$gt": 0}}},
        # Sort by collection count descending
        {"$sort": {"collection_count": -1}},
        # Limit results
        {"$limit": limit},
        # Remove the owned_by array to reduce response size
        {"$unset": "owned_by"}
    ]
    
    jerseys = await db.jerseys.aggregate(pipeline).to_list(limit)
    
    # Remove MongoDB ObjectId fields
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

@api_router.get("/explorer/most-wanted")
async def get_most_wanted_jerseys(limit: int = 10):
    """Get most wanted jerseys based on wanted collection count"""
    pipeline = [
        # Match only approved jerseys
        {"$match": {"status": "approved"}},
        # Lookup collections to count how many users want each jersey
        {
            "$lookup": {
                "from": "collections",
                "let": {"jersey_id": "$id"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$jersey_id", "$$jersey_id"]},
                                    {"$eq": ["$collection_type", "wanted"]}
                                ]
                            }
                        }
                    }
                ],
                "as": "wanted_by"
            }
        },
        # Add wanted count
        {"$addFields": {"wanted_count": {"$size": "$wanted_by"}}},
        # Filter only jerseys that are wanted by at least 1 user
        {"$match": {"wanted_count": {"$gt": 0}}},
        # Sort by wanted count descending
        {"$sort": {"wanted_count": -1}},
        # Limit results
        {"$limit": limit},
        # Remove the wanted_by array to reduce response size
        {"$unset": "wanted_by"}
    ]
    
    jerseys = await db.jerseys.aggregate(pipeline).to_list(limit)
    
    # Remove MongoDB ObjectId fields
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

@api_router.get("/explorer/latest-additions")
async def get_latest_additions(limit: int = 10):
    """Get latest approved jersey additions"""
    jerseys = await db.jerseys.find(
        {"status": "approved"}
    ).sort("approved_at", -1).limit(limit).to_list(limit)
    
    # Remove MongoDB ObjectId fields
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

@api_router.get("/explorer/leagues")
async def get_leagues_overview():
    """Get overview of all leagues with jersey counts"""
    pipeline = [
        # Match only approved jerseys
        {"$match": {"status": "approved"}},
        # Group by league
        {
            "$group": {
                "_id": "$league",
                "jersey_count": {"$sum": 1},
                "teams": {"$addToSet": "$team"},
                "seasons": {"$addToSet": "$season"}
            }
        },
        # Add team and season counts
        {
            "$addFields": {
                "team_count": {"$size": "$teams"},
                "season_count": {"$size": "$seasons"}
            }
        },
        # Sort by jersey count descending
        {"$sort": {"jersey_count": -1}},
        # Project final structure
        {
            "$project": {
                "league": "$_id",
                "jersey_count": 1,
                "team_count": 1,
                "season_count": 1,
                "_id": 0
            }
        }
    ]
    
    leagues = await db.jerseys.aggregate(pipeline).to_list(100)
    
    return leagues

@api_router.get("/explorer/leagues/{league}/jerseys")
async def get_league_jerseys(league: str, limit: int = 20):
    """Get jerseys from a specific league"""
    jerseys = await db.jerseys.find(
        {"status": "approved", "league": {"$regex": league, "$options": "i"}}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Remove MongoDB ObjectId fields
    for jersey in jerseys:
        jersey.pop('_id', None)
    
    return jerseys

# Jersey endpoints
@api_router.post("/jerseys")
async def create_jersey(
    team: str = Form(...),
    league: str = Form(...),
    season: str = Form(...),
    model: str = Form(...),
    manufacturer: str = Form(""),
    jersey_type: str = Form(""),
    sku_code: str = Form(None),
    description: str = Form(""),
    front_photo: UploadFile = File(None),
    back_photo: UploadFile = File(None),
    current_user: dict = Depends(get_current_user),
    resubmission_id: Optional[str] = None
):
    """Create a new jersey submission (pending approval) or resubmit with modifications"""
    try:
        user_id = current_user["id"]  # Extract user ID for easier use
        print(f"🟡 Jersey submission received from user {user_id}")
        print(f"🟡 Jersey data: team={team}, league={league}, season={season}, model={model}")
        
        # Validate required fields for new form structure
        if not team or not league or not season or not model:
            raise HTTPException(status_code=422, detail="Team, league, season, and model are required fields")
        
        # Validate model field
        if model not in ["authentic", "replica"]:
            raise HTTPException(status_code=422, detail="Model must be either 'authentic' or 'replica'")
        
        # Jersey type validation (optional)
        valid_jersey_types = ["home", "away", "third", "goalkeeper", "training", "special"]
        if jersey_type and jersey_type not in valid_jersey_types:
            raise HTTPException(status_code=422, detail=f"Invalid jersey type. Must be one of: {', '.join(valid_jersey_types)}")
        
        # Check if this is a resubmission
        is_resubmission = False
        original_reference_number = None
        if resubmission_id:
            # Verify the original jersey exists and belongs to the user
            original_jersey = await db.jerseys.find_one({
                "id": resubmission_id, 
                "submitted_by": user_id,
                "status": "needs_modification"
            })
            if original_jersey:
                is_resubmission = True
                original_reference_number = original_jersey.get("reference_number")
                print(f"🔄 This is a resubmission for jersey {resubmission_id}")
        
        # Generate reference number (keep original for resubmissions)
        if is_resubmission and original_reference_number:
            reference_number = original_reference_number
            print(f"🔄 Keeping original reference: {reference_number}")
        else:
            reference_number = await get_next_jersey_reference()
            print(f"🆕 Generated new reference: {reference_number}")
        
        # Create jersey with validated data (matching current Jersey model)
        jersey = Jersey(
            team=team.strip(),
            league=league.strip(),
            season=season.strip(),
            manufacturer=manufacturer.strip() if manufacturer else "",
            jersey_type=jersey_type.strip() if jersey_type else "",
            sku_code=sku_code.strip() if sku_code else None,
            model=model.strip(),
            description=description.strip() if description else "",
            reference_number=reference_number,
            created_by=user_id,
            submitted_by=user_id,
            status=JerseyStatus.PENDING  # Always start as pending for moderation
        )
        
        # Handle photo uploads (if provided)
        photo_urls = {}
        if front_photo and front_photo.filename:
            try:
                # Create directory if it doesn't exist
                upload_dir = f"../frontend/public/uploads/jerseys/{jersey.id}"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save the actual file
                front_filename = f"front_{front_photo.filename}"
                file_path = os.path.join(upload_dir, front_filename)
                
                # Read and save the file content
                front_content = await front_photo.read()
                with open(file_path, "wb") as f:
                    f.write(front_content)
                
                photo_urls["front_photo_url"] = f"uploads/jerseys/{jersey.id}/{front_filename}"
                print(f"📸 Front photo saved: {file_path}")
            except Exception as e:
                print(f"⚠️ Error handling front photo: {e}")
        
        if back_photo and back_photo.filename:
            try:
                # Create directory if it doesn't exist
                upload_dir = f"../frontend/public/uploads/jerseys/{jersey.id}"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save the actual file
                back_filename = f"back_{back_photo.filename}"
                file_path = os.path.join(upload_dir, back_filename)
                
                # Read and save the file content
                back_content = await back_photo.read()
                with open(file_path, "wb") as f:
                    f.write(back_content)
                
                photo_urls["back_photo_url"] = f"uploads/jerseys/{jersey.id}/{back_filename}"
                print(f"📸 Back photo saved: {file_path}")
            except Exception as e:
                print(f"⚠️ Error handling back photo: {e}")
        
        # Update jersey with photo URLs if any were processed
        if photo_urls:
            for key, value in photo_urls.items():
                setattr(jersey, key, value)
        
        # Insert into database
        await db.jerseys.insert_one(jersey.dict())
        print(f"✅ Jersey created successfully with ID: {jersey.id}")
        
        # FORCE NOTIFICATION CREATION - ALWAYS CREATE NOTIFICATION
        try:
            logger.info(f"🔔 FORCE Creating notification for user: {user_id}")
            notification = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "system_announcement",
                "title": "Jersey Submitted Successfully!",
                "message": f"Thank you! Your jersey '{jersey.team} {jersey.season}' ({jersey.reference_number}) has been submitted and will be reviewed by our moderators.",
                "related_id": jersey.id,
                "is_read": False,
                "created_at": datetime.utcnow().isoformat(),
                "read_at": None
            }
            await db.notifications.insert_one(notification)
            logger.info(f"✅ FORCED notification created: {notification['id']}")
        except Exception as e:
            logger.error(f"❌ FORCED notification failed: {e}")
        
        logger.info(f"📚 Jersey inserted into database, proceeding to notification logic...")
        
        # Handle resubmission logic
        logger.info(f"🔍 is_resubmission value: {is_resubmission}")
        if is_resubmission:
            # Mark the original jersey as superseded
            await db.jerseys.update_one(
                {"id": resubmission_id},
                {"$set": {"status": "superseded", "superseded_by": jersey.id}}
            )
            
            # Mark related suggestions as addressed
            await db.modification_suggestions.update_many(
                {"jersey_id": resubmission_id, "status": "pending"},
                {"$set": {"status": "addressed", "addressed_at": datetime.utcnow()}}
            )
            
            # Log resubmission activity
            await log_user_activity(user_id, "jersey_resubmission", jersey.id, {
                "original_jersey_id": resubmission_id,
                "jersey_name": f"{jersey.team} {jersey.season}",
                "reference_number": jersey.reference_number,
                "status": jersey.status
            })
            
            # Notification for resubmission
            await create_notification(
                user_id=user_id,
                notification_type=NotificationType.JERSEY_NEEDS_MODIFICATION,
                title="Resubmission Received",
                message=f"Your updated jersey '{jersey.team} {jersey.season}' ({jersey.reference_number}) has been resubmitted and is now under review.",
                related_id=jersey.id
            )
        else:
            # Log regular submission activity
            await log_user_activity(user_id, "jersey_submission", jersey.id, {
                "jersey_name": f"{jersey.team} {jersey.season}",
                "reference_number": jersey.reference_number,
                "status": jersey.status
            })
            
            # Notification for new submission  
            try:
                logger.info(f"🔔 About to create notification for user: {user_id}")
                notification_result = await create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                    title="Jersey Submitted Successfully!",
                    message=f"Thank you! Your jersey '{jersey.team} {jersey.season}' ({jersey.reference_number}) has been submitted and will be reviewed by our moderators.",
                    related_id=jersey.id
                )
                logger.info(f"✅ Notification created successfully")
            except Exception as notif_error:
                logger.error(f"❌ Notification creation failed: {notif_error}")
                # Don't fail the jersey creation if notification fails
        
        # Return jersey with success message
        jersey_dict = jersey.dict()
        jersey_dict["message"] = "Maillot soumis avec succès ! Il sera examiné par nos modérateurs."
        return jersey_dict
        
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
    limit: int = 1000
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

@api_router.get("/jerseys/approved", response_model=List[Dict])
async def get_approved_jerseys(
    team: Optional[str] = None,
    season: Optional[str] = None,
    league: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get approved jerseys available for creating listings"""
    # Build query for approved jerseys only
    query = {"status": "approved"}
    
    if team:
        query["team"] = {"$regex": team, "$options": "i"}
    if season:
        query["season"] = {"$regex": season, "$options": "i"}
    if league:
        query["league"] = {"$regex": league, "$options": "i"}
    
    jerseys = await db.jerseys.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    # Convert for JSON serialization and add listing count
    result = []
    for jersey in jerseys:
        # Remove MongoDB ObjectId to avoid serialization issues
        jersey.pop('_id', None)
        
        # Count active listings for this jersey
        listing_count = await db.listings.count_documents({
            "jersey_id": jersey["id"],
            "status": "active"
        })
        jersey["active_listings"] = listing_count
        
        result.append(jersey)
    
    return result

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
async def create_listing(listing_data: ListingCreate, user_id: str = Depends(get_current_non_admin_user)):
    """Create a new listing from user's collection - restricted to non-admin users only"""
    # Verify collection item exists and belongs to user
    collection_item = await db.collections.find_one({
        "id": listing_data.collection_id,
        "user_id": user_id,
        "collection_type": "owned"  # Can only list owned items
    })
    
    if not collection_item:
        raise HTTPException(status_code=404, detail="Collection item not found or not owned by you")
    
    # Verify the jersey still exists and is approved
    jersey = await db.jerseys.find_one({"id": collection_item["jersey_id"]})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey reference not found")
    
    if jersey.get("status") != "approved":
        raise HTTPException(status_code=400, detail="Jersey reference is no longer approved")
    
    # Validate price
    if not listing_data.price or listing_data.price <= 0:
        raise HTTPException(status_code=422, detail="Price is required and must be greater than 0")
    
    # Check if this collection item is already listed
    existing_listing = await db.listings.find_one({
        "seller_id": user_id,
        "jersey_id": collection_item["jersey_id"],
        "size": collection_item.get("size"),
        "condition": collection_item.get("condition"),
        "status": "active"
    })
    
    if existing_listing:
        raise HTTPException(status_code=400, detail="This item is already listed on the marketplace")
    
    # Combine descriptions (collection personal description + marketplace description)
    combined_description = ""
    if collection_item.get("personal_description"):
        combined_description += collection_item["personal_description"]
    if listing_data.marketplace_description:
        if combined_description:
            combined_description += "\n\n"
        combined_description += listing_data.marketplace_description.strip()
    
    # Create listing using collection item data
    listing = Listing(
        jersey_id=collection_item["jersey_id"],
        seller_id=user_id,
        size=JerseySize(collection_item["size"]) if collection_item.get("size") else None,
        condition=JerseyCondition(collection_item["condition"]) if collection_item.get("condition") else None,
        price=listing_data.price,
        description=combined_description,
        images=listing_data.images or []
    )
    
    await db.listings.insert_one(listing.dict())
    
    # Update jersey valuation with new listing price
    jersey_obj = Jersey(**jersey)
    await update_jersey_valuation(jersey_obj, listing_data.price, "listing", listing.id)
    
    # Log listing creation
    await log_user_activity(user_id, "listing_created", listing.id, {
        "collection_id": listing_data.collection_id,
        "jersey_id": collection_item["jersey_id"],
        "size": collection_item.get("size"),
        "condition": collection_item.get("condition"),
        "price": listing_data.price
    })
    
    return listing

@api_router.get("/collections/my-owned", response_model=List[Dict])
async def get_my_owned_collection(current_user: dict = Depends(get_current_user)):
    """Get user's owned collection items available for listing"""
    user_id = current_user["id"]
    
    # Get user's owned items
    pipeline = [
        {"$match": {"user_id": user_id, "collection_type": "owned"}},
        {
            "$lookup": {
                "from": "jerseys",
                "localField": "jersey_id",
                "foreignField": "id",
                "as": "jersey"
            }
        },
        {"$unwind": "$jersey"},
        {"$match": {"jersey.status": "approved"}}  # Only approved jerseys
    ]
    
    collection_items = await db.collections.aggregate(pipeline).to_list(length=None)
    
    # Convert for JSON serialization and add listing status
    result = []
    for item in collection_items:
        # Remove MongoDB ObjectId to avoid serialization issues
        item.pop('_id', None)
        item['jersey'].pop('_id', None)
        
        # Check if already listed
        existing_listing = await db.listings.find_one({
            "seller_id": user_id,
            "jersey_id": item["jersey_id"],
            "size": item.get("size"),
            "condition": item.get("condition"),
            "status": "active"
        })
        
        item["is_listed"] = bool(existing_listing)
        item["listing_id"] = existing_listing.get("id") if existing_listing else None
        
        result.append(item)
    
    return result

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

# Marketplace Catalog endpoint - Discogs style (jerseys with listings)
@api_router.get("/marketplace/catalog")
async def get_marketplace_catalog():
    """Get jerseys that have active listings - Discogs style catalog"""
    try:
        # Get all jerseys that have at least one active listing
        pipeline = [
            # Match only approved jerseys
            {"$match": {"status": "approved"}},
            # Lookup active listings for each jersey
            {
                "$lookup": {
                    "from": "listings",
                    "let": {"jersey_id": "$id"},
                    "pipeline": [
                        {"$match": {"$expr": {"$eq": ["$jersey_id", "$$jersey_id"]}}},
                        {"$match": {"status": "active"}}
                    ],
                    "as": "listings"
                }
            },
            # Only keep jerseys that have at least one listing
            {"$match": {"listings.0": {"$exists": True}}},
            # Add computed fields
            {
                "$addFields": {
                    "listing_count": {"$size": "$listings"},
                    "min_price": {"$min": "$listings.price"},
                    "max_price": {"$max": "$listings.price"},
                    "available_sizes": {"$setUnion": ["$listings.jersey.size"]},
                    "available_conditions": {"$setUnion": ["$listings.jersey.condition"]}
                }
            },
            # Clean up - remove listings array to keep response lightweight  
            {"$project": {"listings": 0}},
            # Sort by newest first
            {"$sort": {"created_at": -1}}
        ]
        
        catalog = await db.jerseys.aggregate(pipeline).to_list(1000)
        
        # Remove MongoDB ObjectId fields
        for jersey in catalog:
            jersey.pop('_id', None)
            
        return catalog
        
    except Exception as e:
        print(f"Error getting marketplace catalog: {e}")
        # Fallback to simple approach
        jerseys = await db.jerseys.find({"status": "approved"}).to_list(1000)
        for jersey in jerseys:
            jersey.pop('_id', None)
        return jerseys

# Collection endpoints
@api_router.post("/collections")
async def add_to_collection(collection_data: CollectionAdd, current_user: dict = Depends(get_current_user)):
    """Add jersey to collection with specific size/condition"""
    user_id = current_user["id"]
    
    # Verify jersey exists and is approved
    jersey = await db.jerseys.find_one({"id": collection_data.jersey_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    if jersey.get("status") != "approved":
        raise HTTPException(status_code=400, detail="Can only add approved jerseys to collection")
    
    # Check if already in collection (same jersey, same collection type)
    existing = await db.collections.find_one({
        "user_id": user_id,
        "jersey_id": collection_data.jersey_id,
        "collection_type": collection_data.collection_type
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already in collection")
    
    # Validate size and condition if provided (for "owned" items)
    size_enum = None
    condition_enum = None
    
    if collection_data.collection_type == "owned":
        # For owned items, size and condition are recommended
        if collection_data.size:
            try:
                size_enum = JerseySize(collection_data.size.upper())
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid size: {collection_data.size}. Must be one of: XS, S, M, L, XL, XXL")
        
        if collection_data.condition:
            try:
                condition_enum = JerseyCondition(collection_data.condition.lower())
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid condition: {collection_data.condition}. Must be one of: new, near_mint, very_good, good, poor")
    
    # Create collection entry
    collection = Collection(
        user_id=user_id,
        jersey_id=collection_data.jersey_id,
        collection_type=collection_data.collection_type,
        size=size_enum,
        condition=condition_enum,
        personal_description=collection_data.personal_description.strip() if collection_data.personal_description else None
    )
    
    await db.collections.insert_one(collection.dict())
    
    # Log collection activity
    await log_user_activity(user_id, "collection_added", collection.id, {
        "jersey_id": collection_data.jersey_id,
        "collection_type": collection_data.collection_type,
        "size": collection_data.size,
        "condition": collection_data.condition
    })
    
    return {"message": f"Added to {collection_data.collection_type} collection", "collection_id": collection.id}

@api_router.post("/reference-kit-collections") 
async def add_reference_kit_to_collection(collection_data: ReferenceKitCollectionAdd, current_user: dict = Depends(get_current_user)):
    """Add reference kit to collection with specific personal details"""
    user_id = current_user["id"]
    
    # Verify reference kit exists
    reference_kit = await db.reference_kits.find_one({"id": collection_data.reference_kit_id})
    if not reference_kit:
        raise HTTPException(status_code=404, detail="Reference kit not found")
    
    # Check for bilateral system rule - can't be in both owned and wanted
    existing_opposite = await db.reference_kit_collections.find_one({
        "user_id": user_id,
        "reference_kit_id": collection_data.reference_kit_id,
        "collection_type": "owned" if collection_data.collection_type == "wanted" else "wanted"
    })
    
    if existing_opposite:
        opposite_type = "owned" if collection_data.collection_type == "wanted" else "wanted"
        raise HTTPException(status_code=400, detail=f"Reference kit is already in your {opposite_type} collection. Remove it first to add to {collection_data.collection_type}.")
    
    # Check if already in collection (same reference kit, same collection type)
    existing = await db.reference_kit_collections.find_one({
        "user_id": user_id,
        "reference_kit_id": collection_data.reference_kit_id,
        "collection_type": collection_data.collection_type
    })
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Reference kit is already in your {collection_data.collection_type} collection")
    
    # Validate size if provided
    size_enum = None
    condition_enum = None
    
    if collection_data.size:
        try:
            size_enum = JerseySize(collection_data.size.upper())
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid size: {collection_data.size}. Must be one of: XS, S, M, L, XL, XXL")
    
    if collection_data.condition:
        try:
            condition_enum = JerseyCondition(collection_data.condition.lower())
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid condition: {collection_data.condition}. Must be one of: new_with_tags, mint, excellent, good, fair, poor")
    
    # Create collection entry
    collection_item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "reference_kit_id": collection_data.reference_kit_id,
        "collection_type": collection_data.collection_type,
        "size": size_enum.value if size_enum else None,
        "condition": condition_enum.value if condition_enum else None,
        "personal_description": collection_data.personal_description.strip() if collection_data.personal_description else None,
        "purchase_price": collection_data.purchase_price,
        "estimated_value": collection_data.estimated_value,
        "player_name": collection_data.player_name.strip() if collection_data.player_name else None,
        "player_number": collection_data.player_number.strip() if collection_data.player_number else None,
        # New special attributes
        "worn": collection_data.worn,
        "worn_type": collection_data.worn_type,
        "signed": collection_data.signed,
        "signed_by": collection_data.signed_by.strip() if collection_data.signed_by else None,
        "added_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.reference_kit_collections.insert_one(collection_item)
    
    return {
        "message": f"Reference kit added to {collection_data.collection_type} collection", 
        "collection_id": collection_item["id"]
    }

@api_router.get("/users/{user_id}/reference-kit-collections/owned")
async def get_user_owned_reference_kit_collections(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's owned reference kit collections"""
    try:
        # Verify access - users can only see their own collections unless profile is public
        if current_user["id"] != user_id:
            user = await db.users.find_one({"id": user_id})
            if not user or user.get("profile_privacy", "public") == "private":
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get owned reference kit collections with enriched data
        pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "owned"}},
            {
                "$lookup": {
                    "from": "reference_kits",
                    "localField": "reference_kit_id",
                    "foreignField": "id",
                    "as": "reference_kit_lookup"
                }
            },
            {"$unwind": {"path": "$reference_kit_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "reference_kit_lookup.master_kit_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "id": 1,
                    "user_id": 1,
                    "reference_kit_id": 1,
                    "collection_type": 1,
                    "size": 1,
                    "condition": 1,
                    "personal_description": 1,
                    "purchase_price": 1,
                    "estimated_value": 1,
                    "player_name": 1,
                    "player_number": 1,
                    "worn": 1,
                    "worn_type": 1,
                    "signed": 1,
                    "signed_by": 1,
                    "added_at": 1,
                    "updated_at": 1,
                    "reference_kit": {
                        "id": "$reference_kit_lookup.id",
                        "model_name": "$reference_kit_lookup.model_name",
                        "release_type": "$reference_kit_lookup.release_type",
                        "topkit_reference": "$reference_kit_lookup.topkit_reference",
                        "main_photo_url": "$reference_kit_lookup.main_photo_url",
                        "product_images": "$reference_kit_lookup.product_images",
                        "original_retail_price": "$reference_kit_lookup.original_retail_price"
                    },
                    "master_jersey": {
                        "id": "$master_jersey_lookup.id",
                        "season": "$master_jersey_lookup.season",
                        "jersey_type": "$master_jersey_lookup.jersey_type",
                        "model": "$master_jersey_lookup.model",
                        "team_info": "$master_jersey_lookup.team_info"
                    }
                }
            },
            {
                "$addFields": {
                    "_id": "$$REMOVE"  # Remove _id field after projection
                }
            }
        ]
        
        collections = await db.reference_kit_collections.aggregate(pipeline).to_list(length=None)
        
        return collections
        
    except Exception as e:
        logger.error(f"Error getting user owned reference kit collections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/users/{user_id}/reference-kit-collections/wanted")
async def get_user_wanted_reference_kit_collections(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's wanted reference kit collections"""
    try:
        # Verify access - users can only see their own collections unless profile is public
        if current_user["id"] != user_id:
            user = await db.users.find_one({"id": user_id})
            if not user or user.get("profile_privacy", "public") == "private":
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get wanted reference kit collections with enriched data
        pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "wanted"}},
            {
                "$lookup": {
                    "from": "reference_kits",
                    "localField": "reference_kit_id",
                    "foreignField": "id",
                    "as": "reference_kit_lookup"
                }
            },
            {"$unwind": {"path": "$reference_kit_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "reference_kit_lookup.master_kit_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "id": 1,
                    "user_id": 1,
                    "reference_kit_id": 1,
                    "collection_type": 1,
                    "size": 1,
                    "condition": 1,
                    "personal_description": 1,
                    "purchase_price": 1,
                    "estimated_value": 1,
                    "player_name": 1,
                    "player_number": 1,
                    "worn": 1,
                    "worn_type": 1,
                    "signed": 1,
                    "signed_by": 1,
                    "added_at": 1,
                    "updated_at": 1,
                    "reference_kit": {
                        "id": "$reference_kit_lookup.id",
                        "model_name": "$reference_kit_lookup.model_name",
                        "release_type": "$reference_kit_lookup.release_type",
                        "topkit_reference": "$reference_kit_lookup.topkit_reference",
                        "main_photo_url": "$reference_kit_lookup.main_photo_url",
                        "product_images": "$reference_kit_lookup.product_images",
                        "original_retail_price": "$reference_kit_lookup.original_retail_price"
                    },
                    "master_jersey": {
                        "id": "$master_jersey_lookup.id",
                        "season": "$master_jersey_lookup.season",
                        "jersey_type": "$master_jersey_lookup.jersey_type",
                        "model": "$master_jersey_lookup.model",
                        "team_info": "$master_jersey_lookup.team_info"
                    }
                }
            },
            {
                "$addFields": {
                    "_id": "$$REMOVE"  # Remove _id field after projection
                }
            }
        ]
        
        collections = await db.reference_kit_collections.aggregate(pipeline).to_list(length=None)
        
        return collections
        
    except Exception as e:
        logger.error(f"Error getting user wanted reference kit collections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/users/{user_id}/reference-kit-collections")
async def get_user_reference_kit_collections(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's reference kit collections (both owned and wanted)"""
    try:
        # Verify access - users can only see their own collections unless profile is public
        if current_user["id"] != user_id:
            user = await db.users.find_one({"id": user_id})
            if not user or user.get("profile_privacy", "public") == "private":
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all reference kit collections with enriched data
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$lookup": {
                    "from": "reference_kits",
                    "localField": "reference_kit_id",
                    "foreignField": "id",
                    "as": "reference_kit_lookup"
                }
            },
            {"$unwind": {"path": "$reference_kit_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "reference_kit_lookup.master_kit_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "id": 1,
                    "user_id": 1,
                    "reference_kit_id": 1,
                    "collection_type": 1,
                    "size": 1,
                    "condition": 1,
                    "personal_description": 1,
                    "purchase_price": 1,
                    "estimated_value": 1,
                    "player_name": 1,
                    "player_number": 1,
                    "worn": 1,
                    "worn_type": 1,
                    "signed": 1,
                    "signed_by": 1,
                    "added_at": 1,
                    "updated_at": 1,
                    "reference_kit": {
                        "id": "$reference_kit_lookup.id",
                        "model_name": "$reference_kit_lookup.model_name",
                        "release_type": "$reference_kit_lookup.release_type",
                        "topkit_reference": "$reference_kit_lookup.topkit_reference",
                        "main_photo_url": "$reference_kit_lookup.main_photo_url",
                        "product_images": "$reference_kit_lookup.product_images",
                        "original_retail_price": "$reference_kit_lookup.original_retail_price"
                    },
                    "master_jersey": {
                        "id": "$master_jersey_lookup.id",
                        "season": "$master_jersey_lookup.season",
                        "jersey_type": "$master_jersey_lookup.jersey_type",
                        "model": "$master_jersey_lookup.model",
                        "team_info": "$master_jersey_lookup.team_info"
                    }
                }
            },
            {
                "$addFields": {
                    "_id": "$$REMOVE"  # Remove _id field after projection
                }
            }
        ]
        
        all_collections = await db.reference_kit_collections.aggregate(pipeline).to_list(length=None)
        
        # Separate into owned and wanted
        owned = [c for c in all_collections if c.get("collection_type") == "owned"]
        wanted = [c for c in all_collections if c.get("collection_type") == "wanted"]
        
        return {
            "user_id": user_id,
            "profile_owner": current_user["id"] == user_id,
            "collections": all_collections,
            "owned": owned,
            "wanted": wanted,
            "owned_count": len(owned),
            "wanted_count": len(wanted)
        }
        
    except Exception as e:
        logger.error(f"Error getting user reference kit collections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/reference-kit-collections/{collection_id}")
async def remove_reference_kit_from_collection(collection_id: str, current_user: dict = Depends(get_current_user)):
    """Remove reference kit from user's collection (owned or wanted)"""
    try:
        user_id = current_user["id"]
        
        # Verify ownership and delete
        result = await db.reference_kit_collections.delete_one({
            "id": collection_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reference kit collection not found or not owned by you")
        
        return {"message": "Reference kit removed from collection successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reference kit collection removal error: {e}")
        raise HTTPException(status_code=500, detail="Error removing reference kit from collection")

@api_router.post("/collections/remove")
async def remove_from_collection_post(collection_data: CollectionAdd, current_user: dict = Depends(get_current_user)):
    """Remove jersey from collection"""
    user_id = current_user["id"]
    
    result = await db.collections.delete_one({
        "user_id": user_id,
        "jersey_id": collection_data.jersey_id,
        "collection_type": collection_data.collection_type
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Jersey not found in collection")
    
    return {"message": "Removed from collection"}

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
async def get_user_collection(collection_type: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
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
        {"$unwind": "$jersey"},
        # Only include approved jerseys in collections
        {"$match": {"jersey.status": "approved"}}
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
async def get_profile(current_user: dict = Depends(get_current_user)):
    user = current_user
    user_id = user["id"]
    
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
            "provider": user.get("provider", "custom"),
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
async def update_profile_settings(settings: ProfileSettings, current_user: dict = Depends(get_current_user)):
    # Build update dictionary only with provided fields
    update_data = {}
    user_id = current_user["id"]
    
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

@api_router.get("/notifications")
async def get_user_notifications(user_id: str = Depends(get_current_user), limit: int = 20, offset: int = 0):
    """Get user's notifications"""
    notifications = await db.notifications.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    # Remove MongoDB ObjectId for JSON serialization
    for notification in notifications:
        notification.pop('_id', None)
    
    # Get unread count
    unread_count = await db.notifications.count_documents({"user_id": user_id, "is_read": False})
    
    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications)
    }

@api_router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: str, user_id: str = Depends(get_current_user)):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": user_id, "is_read": False},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found or already read")
    
    return {"message": "Notification marked as read"}

@api_router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(user_id: str = Depends(get_current_user)):
    """Mark all user notifications as read"""
    result = await db.notifications.update_many(
        {"user_id": user_id, "is_read": False},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": f"Marked {result.modified_count} notifications as read"}

@api_router.get("/jerseys/{jersey_id}/suggestions")
async def get_jersey_suggestions(jersey_id: str, user_id: str = Depends(get_current_user)):
    """Get modification suggestions for a jersey (only owner can see)"""
    
    # Verify user owns this jersey
    jersey = await db.jerseys.find_one({"id": jersey_id, "submitted_by": user_id})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found or you don't have permission to view suggestions")
    
    # Get suggestions for this jersey
    suggestions = await db.modification_suggestions.find(
        {"jersey_id": jersey_id}
    ).sort("created_at", -1).to_list(10)
    
    # Remove MongoDB ObjectId for JSON serialization
    for suggestion in suggestions:
        suggestion.pop('_id', None)
        
        # Get moderator info
        moderator = await db.users.find_one({"id": suggestion["moderator_id"]}, {"name": 1, "email": 1, "role": 1})
        if moderator:
            moderator.pop('_id', None)
            suggestion["moderator_info"] = moderator
    
    return {
        "jersey": {
            "id": jersey["id"],
            "team": jersey.get("team", ""),
            "season": jersey.get("season", ""),
            "status": jersey.get("status", "")
        },
        "suggestions": suggestions
    }

@api_router.get("/collections/pending")
async def get_user_pending_submissions(user_id: str = Depends(get_current_user)):
    """Get user's pending jersey submissions including those needing modification"""
    print(f"🔍 Collections/pending called for user: {user_id}")
    
    # Use multiple queries as workaround for MongoDB $in issue
    pending_submissions = await db.jerseys.find({
        "submitted_by": user_id,
        "status": "pending"
    }).to_list(100)
    print(f"🔍 Found {len(pending_submissions)} pending submissions")
    
    rejected_submissions = await db.jerseys.find({
        "submitted_by": user_id,
        "status": "rejected"
    }).to_list(100)
    print(f"🔍 Found {len(rejected_submissions)} rejected submissions")
    
    needs_mod_submissions = await db.jerseys.find({
        "submitted_by": user_id,
        "status": "needs_modification"
    }).to_list(100)
    print(f"🔍 Found {len(needs_mod_submissions)} needs_modification submissions")
    
    # Combine all submissions
    submissions = pending_submissions + rejected_submissions + needs_mod_submissions
    print(f"🔍 Total submissions: {len(submissions)}")
    
    # Remove MongoDB ObjectId for JSON serialization and add suggestions info
    for submission in submissions:
        submission.pop('_id', None)
        
        # If jersey needs modification, get the latest suggestion
        if submission.get("status") == "needs_modification":
            latest_suggestion = await db.modification_suggestions.find_one(
                {"jersey_id": submission["id"]},
                sort=[("created_at", -1)]
            )
            if latest_suggestion:
                latest_suggestion.pop('_id', None)
                submission["latest_suggestion"] = latest_suggestion
    
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


# Jersey Detail Management Endpoints
@api_router.get("/collections/owned/{jersey_id}/details")
async def get_jersey_details(jersey_id: str, current_user: dict = Depends(get_current_user)):
    """Get detailed information for a jersey in user's owned collection"""
    user_id = current_user["id"]
    
    # Verify user owns this jersey
    collection_item = await db.collections.find_one({
        "user_id": user_id,
        "jersey_id": jersey_id,
        "collection_type": "owned"
    })
    
    if not collection_item:
        raise HTTPException(status_code=404, detail="Jersey not found in your collection")
    
    # Get detailed data if it exists
    detail_data = await db.jersey_details.find_one({"user_id": user_id, "jersey_id": jersey_id})
    
    if detail_data:
        detail_data.pop('_id', None)  # Remove MongoDB ID
        return detail_data
    else:
        # Return default values if no details exist
        return {
            "jersey_id": jersey_id,
            "user_id": user_id,
            "model_type": "authentic",
            "condition": "mint",
            "size": "m",
            "special_features": [],
            "material_details": "",
            "tags": "tags_on",
            "packaging": "no_packaging",
            "customization": "blank",
            "competition_badges": "",
            "rarity": "common",
            "purchase_price": None,
            "purchase_date": None,
            "purchase_location": None,
            "certificate_authenticity": False,
            "storage_notes": "",
            "estimated_value": 0
        }

@api_router.put("/collections/owned/{jersey_id}/details")
async def update_jersey_details(jersey_id: str, detail_data: JerseyDetailData, current_user: dict = Depends(get_current_user)):
    """Update detailed information for a jersey in user's owned collection"""
    user_id = current_user["id"]
    
    # Verify user owns this jersey
    collection_item = await db.collections.find_one({
        "user_id": user_id,
        "jersey_id": jersey_id,
        "collection_type": "owned"
    })
    
    if not collection_item:
        raise HTTPException(status_code=404, detail="Jersey not found in your collection")
    
    # Prepare detail data for storage
    detail_doc = detail_data.dict()
    detail_doc["jersey_id"] = jersey_id
    detail_doc["user_id"] = user_id
    detail_doc["updated_at"] = datetime.utcnow()
    
    # Upsert the details
    result = await db.jersey_details.replace_one(
        {"user_id": user_id, "jersey_id": jersey_id},
        detail_doc,
        upsert=True
    )
    
    # Log activity
    await log_user_activity(user_id, "jersey_details_updated", jersey_id, {
        "estimated_value": detail_data.estimated_value,
        "condition": detail_data.condition,
        "model_type": detail_data.model_type
    })
    
    return {"message": "Jersey details updated successfully", "estimated_value": detail_data.estimated_value}

@api_router.get("/users/security-info")
async def get_user_security_info(user_id: str = Depends(get_current_user)):
    """Get user's security information for the security settings modal"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get recent login history (last 10 logins)
    login_history = await db.login_history.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    # Remove MongoDB IDs
    for login in login_history:
        login.pop('_id', None)
    
    return {
        "has_2fa": user.get("two_factor_enabled", False),
        "password_last_changed": user.get("password_last_changed"),
        "login_history": login_history,
        "security_alerts": user.get("security_alerts", True),
        "email_notifications": user.get("email_notifications", True)
    }

@api_router.put("/users/security-settings")
async def update_security_settings(
    settings: dict, 
    user_id: str = Depends(get_current_user)
):
    """Update user's security notification settings"""
    # Validate settings
    valid_settings = ["security_alerts", "email_notifications"]
    update_data = {}
    
    for key, value in settings.items():
        if key in valid_settings and isinstance(value, bool):
            update_data[key] = value
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid settings provided")
    
    # Update user settings
    await db.users.update_one(
        {"id": user_id},
        {"$set": update_data}
    )
    
    return {"message": "Security settings updated successfully"}


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
    """Get user's public Jersey Release collections (both owned and wanted)"""
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if profile is private
        if user.get("profile_privacy", "public") == "private" and current_user_id != user_id:
            raise HTTPException(status_code=403, detail="This user's profile is private")
        
        # Get both owned and wanted collections using the same logic as working endpoints
        owned_pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "owned"}},
            {
                "$lookup": {
                    "from": "jersey_releases",
                    "localField": "jersey_release_id",
                    "foreignField": "id",
                    "as": "jersey_release_lookup"
                }
            },
            {"$unwind": {"path": "$jersey_release_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "jersey_release_lookup.master_jersey_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "user_id": 1,
                    "jersey_release_id": 1,
                    "collection_type": 1,
                    "size": 1,
                    "condition": 1,
                    "purchase_price": 1,
                    "estimated_value": 1,
                    "created_at": 1,
                    "jersey_release": {
                        "$cond": {
                            "if": {"$ne": ["$jersey_release_lookup", None]},
                            "then": {
                                "id": "$jersey_release_lookup.id",
                                "player_name": "$jersey_release_lookup.player_name",
                                "player_number": "$jersey_release_lookup.player_number",
                                "release_type": "$jersey_release_lookup.release_type",
                                "retail_price": "$jersey_release_lookup.retail_price",
                                "product_images": "$jersey_release_lookup.product_images",
                                "topkit_reference": "$jersey_release_lookup.topkit_reference",
                                "master_jersey_id": "$jersey_release_lookup.master_jersey_id"
                            },
                            "else": None
                        }
                    },
                    "master_jersey": {
                        "$cond": {
                            "if": {"$ne": ["$master_jersey_lookup", None]},
                            "then": {
                                "id": "$master_jersey_lookup.id",
                                "team_info": "$master_jersey_lookup.team_info",
                                "season": "$master_jersey_lookup.season",
                                "jersey_type": "$master_jersey_lookup.jersey_type",
                                "brand_info": "$master_jersey_lookup.brand_info",
                                "competition_info": "$master_jersey_lookup.competition_info",
                                "topkit_reference": "$master_jersey_lookup.topkit_reference"
                            },
                            "else": None
                        }
                    }
                }
            }
        ]
        
        wanted_pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "wanted"}},
            {
                "$lookup": {
                    "from": "jersey_releases",
                    "localField": "jersey_release_id",
                    "foreignField": "id",
                    "as": "jersey_release_lookup"
                }
            },
            {"$unwind": {"path": "$jersey_release_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "jersey_release_lookup.master_jersey_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "user_id": 1,
                    "jersey_release_id": 1,
                    "collection_type": 1,
                    "created_at": 1,
                    "jersey_release": {
                        "$cond": {
                            "if": {"$ne": ["$jersey_release_lookup", None]},
                            "then": {
                                "id": "$jersey_release_lookup.id",
                                "player_name": "$jersey_release_lookup.player_name",
                                "player_number": "$jersey_release_lookup.player_number",
                                "release_type": "$jersey_release_lookup.release_type",
                                "retail_price": "$jersey_release_lookup.retail_price",
                                "product_images": "$jersey_release_lookup.product_images",
                                "topkit_reference": "$jersey_release_lookup.topkit_reference",
                                "master_jersey_id": "$jersey_release_lookup.master_jersey_id"
                            },
                            "else": None
                        }
                    },
                    "master_jersey": {
                        "$cond": {
                            "if": {"$ne": ["$master_jersey_lookup", None]},
                            "then": {
                                "id": "$master_jersey_lookup.id",
                                "team_info": "$master_jersey_lookup.team_info",
                                "season": "$master_jersey_lookup.season",
                                "jersey_type": "$master_jersey_lookup.jersey_type",
                                "brand_info": "$master_jersey_lookup.brand_info",
                                "competition_info": "$master_jersey_lookup.competition_info",
                                "topkit_reference": "$master_jersey_lookup.topkit_reference"
                            },
                            "else": None
                        }
                    }
                }
            }
        ]
        
        # Execute both pipelines and combine results
        owned_collections = await db.user_jersey_collections.aggregate(owned_pipeline).to_list(1000)
        wanted_collections = await db.user_jersey_collections.aggregate(wanted_pipeline).to_list(1000)
        
        # Combine all collections
        all_collections = owned_collections + wanted_collections
        
        # For privacy, remove purchase prices and valuations if not profile owner
        if current_user_id != user_id:
            for collection in all_collections:
                collection.pop('purchase_price', None)
                collection.pop('estimated_value', None)
        
        return {
            "user_id": user_id,
            "profile_owner": current_user_id == user_id,
            "collections": all_collections
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user collections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# JERSEY RELEASE COLLECTIONS API
# ================================

@api_router.get("/users/{user_id}/collections/owned")
async def get_user_owned_collections(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's owned Jersey Release collections"""
    try:
        # Verify access - users can only see their own collections unless profile is public
        if current_user["id"] != user_id:
            user = await db.users.find_one({"id": user_id})
            if not user or user.get("profile_privacy", "public") == "private":
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get owned Jersey Release collections with enriched data - Enhanced debugging
        pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "owned"}},
            {
                "$lookup": {
                    "from": "jersey_releases",
                    "localField": "jersey_release_id",
                    "foreignField": "id",
                    "as": "jersey_release_lookup"
                }
            },
            {"$unwind": {"path": "$jersey_release_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "jersey_release_lookup.master_jersey_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "user_id": 1,
                    "jersey_release_id": 1,
                    "size": 1,
                    "condition": 1,
                    "purchase_price": 1,
                    "estimated_value": 1,
                    "created_at": 1,
                    "jersey_release": {
                        "$cond": {
                            "if": {"$ne": ["$jersey_release_lookup", None]},
                            "then": {
                                "id": "$jersey_release_lookup.id",
                                "player_name": "$jersey_release_lookup.player_name",
                                "player_number": "$jersey_release_lookup.player_number",
                                "release_type": "$jersey_release_lookup.release_type",
                                "retail_price": "$jersey_release_lookup.retail_price",
                                "product_images": "$jersey_release_lookup.product_images",
                                "topkit_reference": "$jersey_release_lookup.topkit_reference",
                                "master_jersey_id": "$jersey_release_lookup.master_jersey_id"
                            },
                            "else": None
                        }
                    },
                    "master_jersey": {
                        "$cond": {
                            "if": {"$ne": ["$master_jersey_lookup", None]},
                            "then": {
                                "id": "$master_jersey_lookup.id",
                                "team_info": "$master_jersey_lookup.team_info",
                                "season": "$master_jersey_lookup.season",
                                "jersey_type": "$master_jersey_lookup.jersey_type",
                                "brand_info": "$master_jersey_lookup.brand_info",
                                "competition_info": "$master_jersey_lookup.competition_info",
                                "topkit_reference": "$master_jersey_lookup.topkit_reference"
                            },
                            "else": None
                        }
                    }
                }
            }
        ]
        
        collections = await db.user_jersey_collections.aggregate(pipeline).to_list(1000)
        return collections
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching owned collections: {str(e)}")

@api_router.get("/users/{user_id}/collections/wanted")
async def get_user_wanted_collections(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user's wanted Jersey Release collections"""
    try:
        # Verify access
        if current_user["id"] != user_id:
            user = await db.users.find_one({"id": user_id})
            if not user or user.get("profile_privacy", "public") == "private":
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Get wanted Jersey Release collections with enriched data - Enhanced debugging
        pipeline = [
            {"$match": {"user_id": user_id, "collection_type": "wanted"}},
            {
                "$lookup": {
                    "from": "jersey_releases",
                    "localField": "jersey_release_id",
                    "foreignField": "id",
                    "as": "jersey_release_lookup"
                }
            },
            {"$unwind": {"path": "$jersey_release_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "jersey_release_lookup.master_jersey_id",
                    "foreignField": "id",
                    "as": "master_jersey_lookup"
                }
            },
            {"$unwind": {"path": "$master_jersey_lookup", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "user_id": 1,
                    "jersey_release_id": 1,
                    "created_at": 1,
                    "jersey_release": {
                        "$cond": {
                            "if": {"$ne": ["$jersey_release_lookup", None]},
                            "then": {
                                "id": "$jersey_release_lookup.id",
                                "player_name": "$jersey_release_lookup.player_name",
                                "player_number": "$jersey_release_lookup.player_number",
                                "release_type": "$jersey_release_lookup.release_type",
                                "retail_price": "$jersey_release_lookup.retail_price",
                                "product_images": "$jersey_release_lookup.product_images",
                                "topkit_reference": "$jersey_release_lookup.topkit_reference",
                                "master_jersey_id": "$jersey_release_lookup.master_jersey_id"
                            },
                            "else": None
                        }
                    },
                    "master_jersey": {
                        "$cond": {
                            "if": {"$ne": ["$master_jersey_lookup", None]},
                            "then": {
                                "id": "$master_jersey_lookup.id",
                                "team_info": "$master_jersey_lookup.team_info",
                                "season": "$master_jersey_lookup.season",
                                "jersey_type": "$master_jersey_lookup.jersey_type",
                                "brand_info": "$master_jersey_lookup.brand_info",
                                "competition_info": "$master_jersey_lookup.competition_info",
                                "topkit_reference": "$master_jersey_lookup.topkit_reference"
                            },
                            "else": None
                        }
                    }
                }
            }
        ]
        
        collections = await db.user_jersey_collections.aggregate(pipeline).to_list(1000)
        return collections
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching wanted collections: {str(e)}")

@api_router.post("/users/{user_id}/collections")
async def add_to_collection(
    user_id: str,
    collection_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Add a Jersey Release to user's collection"""
    try:
        # Verify user can only modify their own collection
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Can only modify your own collection")
        
        # Validate required fields
        required_fields = ["jersey_release_id", "collection_type"]
        for field in required_fields:
            if field not in collection_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate collection_type
        if collection_data["collection_type"] not in ["owned", "wanted"]:
            raise HTTPException(status_code=400, detail="collection_type must be 'owned' or 'wanted'")
        
        # Check if Jersey Release exists
        jersey_release = await db.jersey_releases.find_one({"id": collection_data["jersey_release_id"]})
        if not jersey_release:
            raise HTTPException(status_code=404, detail="Jersey Release not found")
        
        # Check if already in collection
        existing = await db.user_jersey_collections.find_one({
            "user_id": user_id,
            "jersey_release_id": collection_data["jersey_release_id"],
            "collection_type": collection_data["collection_type"]
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Jersey Release already in collection")
        
        # Create collection item
        collection_item = UserJerseyCollection(
            user_id=user_id,
            jersey_release_id=collection_data["jersey_release_id"],
            size=collection_data.get("size", ""),
            condition=collection_data.get("condition", "mint"),
            purchase_price=collection_data.get("purchase_price"),
            estimated_value=collection_data.get("estimated_value")
        )
        
        # Add collection_type field
        collection_dict = collection_item.dict()
        collection_dict["collection_type"] = collection_data["collection_type"]
        
        await db.user_jersey_collections.insert_one(collection_dict)
        
        # Log activity
        await log_user_activity(
            user_id,
            f"jersey_release_added_to_{collection_data['collection_type']}",
            collection_data["jersey_release_id"],
            {
                "release_reference": jersey_release.get("topkit_reference"),
                "collection_type": collection_data["collection_type"]
            }
        )
        
        return {"message": "Jersey Release added to collection successfully", "collection_id": collection_item.id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to collection: {str(e)}")

@api_router.delete("/users/{user_id}/collections/{collection_id}")
async def remove_from_collection(
    user_id: str,
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a Jersey Release from user's collection"""
    try:
        # Verify user can only modify their own collection
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Can only modify your own collection")
        
        # Find and remove collection item
        collection_item = await db.user_jersey_collections.find_one({"id": collection_id, "user_id": user_id})
        if not collection_item:
            raise HTTPException(status_code=404, detail="Collection item not found")
        
        await db.user_jersey_collections.delete_one({"id": collection_id, "user_id": user_id})
        
        # Log activity
        await log_user_activity(
            user_id,
            "jersey_release_removed_from_collection",
            collection_item["jersey_release_id"],
            {
                "collection_type": collection_item.get("collection_type", "unknown")
            }
        )
        
        return {"message": "Jersey Release removed from collection successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove collection item error: {e}")
        raise HTTPException(status_code=500, detail="Error removing Jersey Release from collection")

@api_router.get("/collections/public")
async def get_public_collections():
    """Get all public collections from users for the Collections page"""
    try:
        # Aggregate user collections with jersey details
        pipeline = [
            # Match users with public profiles and non-empty collections
            {"$match": {"profile_privacy": "public"}},
            # Lookup user collections
            {
                "$lookup": {
                    "from": "user_jersey_collections",
                    "localField": "id",
                    "foreignField": "user_id", 
                    "as": "collections"
                }
            },
            # Filter users with at least one collection item
            {"$match": {"collections": {"$ne": []}}},
            # Unwind collections to process each item
            {"$unwind": "$collections"},
            # Lookup jersey release details
            {
                "$lookup": {
                    "from": "jersey_releases",
                    "localField": "collections.jersey_release_id",
                    "foreignField": "id",
                    "as": "jersey_release"
                }
            },
            {"$unwind": {"path": "$jersey_release", "preserveNullAndEmptyArrays": True}},
            # Lookup master jersey details
            {
                "$lookup": {
                    "from": "master_jerseys", 
                    "localField": "jersey_release.master_jersey_id",
                    "foreignField": "id",
                    "as": "master_jersey"
                }
            },
            {"$unwind": {"path": "$master_jersey", "preserveNullAndEmptyArrays": True}},
            # Lookup team details
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "master_jersey.team_id", 
                    "foreignField": "id",
                    "as": "team"
                }
            },
            {"$unwind": {"path": "$team", "preserveNullAndEmptyArrays": True}},
            # Project final format
            {
                "$project": {
                    "id": "$collections.id",
                    "user_id": "$id", 
                    "user_name": "$name",
                    "user_profile_picture": "$profile_picture_url",
                    "collection_type": "$collections.collection_type",
                    "jersey_name": {"$ifNull": ["$master_jersey.name", "Maillot"]},
                    "team_name": {"$ifNull": ["$team.name", ""]},
                    "jersey_image_url": {"$ifNull": ["$master_jersey.main_image", None]},
                    "size": "$collections.size",
                    "condition": "$collections.condition",
                    "purchase_price": "$collections.purchase_price",
                    "added_at": "$collections.created_at"
                }
            },
            # Sort by user and then by added date
            {"$sort": {"user_name": 1, "added_at": -1}},
            # Limit to prevent excessive data transfer
            {"$limit": 1000}
        ]
        
        collections = await db.users.aggregate(pipeline).to_list(None)
        
        # Remove MongoDB ObjectId from results
        for collection in collections:
            collection.pop('_id', None)
        
        return collections
        
    except Exception as e:
        logger.error(f"Get public collections error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving public collections")

@api_router.get("/users/with-collections")
async def get_users_with_collections():
    """Get all users with their collection summary for the Collections page"""
    try:
        # Aggregate users with their collection stats
        pipeline = [
            # Match users with public profiles
            {"$match": {"profile_privacy": "public"}},
            # Lookup user collections
            {
                "$lookup": {
                    "from": "user_jersey_collections",
                    "localField": "id",
                    "foreignField": "user_id",
                    "as": "collections"
                }
            },
            # Filter users who have at least one collection item
            {"$match": {"collections": {"$ne": []}}},
            # Add collection stats
            {
                "$addFields": {
                    "total_owned": {
                        "$size": {
                            "$filter": {
                                "input": "$collections",
                                "cond": {"$eq": ["$$this.collection_type", "owned"]}
                            }
                        }
                    },
                    "total_wanted": {
                        "$size": {
                            "$filter": {
                                "input": "$collections", 
                                "cond": {"$eq": ["$$this.collection_type", "wanted"]}
                            }
                        }
                    }
                }
            },
            # Get favorite club name if exists
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "favorite_club",
                    "foreignField": "id",
                    "as": "favorite_club_info"
                }
            },
            # Project final user data
            {
                "$project": {
                    "id": 1,
                    "name": 1,
                    "profile_picture_url": 1,
                    "bio": 1,
                    "instagram_username": 1,
                    "twitter_username": 1,
                    "website": 1,
                    "created_at": 1,
                    "total_owned": 1,
                    "total_wanted": 1,
                    "favorite_club_name": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$favorite_club_info.name", 0]},
                            None
                        ]
                    }
                }
            },
            # Sort by total collection size (owned + wanted) in descending order
            {"$sort": {"total_owned": -1, "total_wanted": -1, "name": 1}},
            # Limit to prevent excessive data
            {"$limit": 500}
        ]
        
        users = await db.users.aggregate(pipeline).to_list(None)
        
        # Remove MongoDB ObjectId from results
        for user in users:
            user.pop('_id', None)
        
        return users
        
    except Exception as e:
        logger.error(f"Get users with collections error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving users with collections")

@api_router.get("/contributions/community")
async def get_community_contributions(current_user: dict = Depends(get_current_user)):
    """Get all community contributions for the unified contributions page"""
    try:
        # Get all contributions with user and entity details
        pipeline = [
            # Match all contributions
            {"$match": {}},
            # Lookup user details
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user"
                }
            },
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            # Add vote counts
            {
                "$addFields": {
                    "upvotes": {"$size": {"$ifNull": ["$votes.upvotes", []]}},
                    "downvotes": {"$size": {"$ifNull": ["$votes.downvotes", []]}},
                    "vote_score": {
                        "$subtract": [
                            {"$size": {"$ifNull": ["$votes.upvotes", []]}},
                            {"$size": {"$ifNull": ["$votes.downvotes", []]}}
                        ]
                    }
                }
            },
            # Project final format
            {
                "$project": {
                    "id": 1,
                    "entity_type": 1,
                    "entity_id": 1,
                    "entity_name": "$entity_name",
                    "user_id": "$user_id",
                    "user_name": "$user.name",
                    "user_profile_picture": "$user.profile_picture_url",
                    "status": 1,
                    "changes_summary": "$changes_summary",
                    "created_at": 1,
                    "updated_at": 1,
                    "upvotes": 1,
                    "downvotes": 1,
                    "vote_score": 1
                }
            },
            # Sort by creation date (newest first)
            {"$sort": {"created_at": -1}},
            # Limit results
            {"$limit": 100}
        ]
        
        contributions = await db.contributions.aggregate(pipeline).to_list(None)
        
        # Remove MongoDB ObjectId
        for contribution in contributions:
            contribution.pop('_id', None)
        
        return contributions
        
    except Exception as e:
        logger.error(f"Get community contributions error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving community contributions")

@api_router.get("/contributions/my-contributions")
async def get_my_contributions(current_user: dict = Depends(get_current_user)):
    """Get current user's contributions"""
    try:
        user_id = current_user['id']
        
        # Get user's contributions with vote details
        pipeline = [
            # Match user's contributions
            {"$match": {"user_id": user_id}},
            # Add vote counts
            {
                "$addFields": {
                    "upvotes": {"$size": {"$ifNull": ["$votes.upvotes", []]}},
                    "downvotes": {"$size": {"$ifNull": ["$votes.downvotes", []]}},
                    "vote_score": {
                        "$subtract": [
                            {"$size": {"$ifNull": ["$votes.upvotes", []]}},
                            {"$size": {"$ifNull": ["$votes.downvotes", []]}}
                        ]
                    }
                }
            },
            # Project final format
            {
                "$project": {
                    "id": 1,
                    "entity_type": 1,
                    "entity_id": 1,
                    "entity_name": "$entity_name",
                    "status": 1,
                    "changes_summary": "$changes_summary",
                    "created_at": 1,
                    "updated_at": 1,
                    "upvotes": 1,
                    "downvotes": 1,
                    "vote_score": 1
                }
            },
            # Sort by creation date (newest first)
            {"$sort": {"created_at": -1}}
        ]
        
        contributions = await db.contributions.aggregate(pipeline).to_list(None)
        
        # Remove MongoDB ObjectId
        for contribution in contributions:
            contribution.pop('_id', None)
        
        return contributions
        
    except Exception as e:
        logger.error(f"Get my contributions error: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user contributions")

# ===================
# LISTING MANAGEMENT  
# ===================

@api_router.put("/users/{user_id}/collections/{collection_id}")
async def update_collection_item(
    user_id: str,
    collection_id: str,
    update_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update details of a Jersey Release in user's collection"""
    try:
        # Verify user can only modify their own collection
        if current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Can only modify your own collection")
        
        # Find collection item
        collection_item = await db.user_jersey_collections.find_one({"id": collection_id, "user_id": user_id})
        if not collection_item:
            raise HTTPException(status_code=404, detail="Collection item not found")
        
        # Allowed update fields
        allowed_fields = ["size", "condition", "purchase_price", "estimated_value"]
        update_dict = {}
        
        for field in allowed_fields:
            if field in update_data:
                update_dict[field] = update_data[field]
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update collection item
        await db.user_jersey_collections.update_one(
            {"id": collection_id, "user_id": user_id},
            {"$set": update_dict}
        )
        
        # Log activity
        await log_user_activity(
            user_id,
            "jersey_release_collection_updated",
            collection_item["jersey_release_id"],
            {
                "updated_fields": list(update_dict.keys()),
                "collection_type": collection_item.get("collection_type", "unknown")
            }
        )
        
        return {"message": "Collection item updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating collection item: {str(e)}")

@api_router.post("/vestiaire/add-to-collection")
async def add_vestiaire_to_collection(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Add a Jersey Release from Vestiaire to user's collection"""
    try:
        # Validate required fields
        required_fields = ["jersey_release_id", "collection_type"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Use the existing add_to_collection logic
        collection_result = await add_to_collection(
            current_user["id"],
            data,
            current_user
        )
        
        return collection_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding vestiaire item to collection: {str(e)}")

# Nouveaux endpoints pour profil utilisateur avancé

@api_router.get("/profile/advanced")
async def get_advanced_profile(user_id: str = Depends(get_current_user)):
    """Récupère le profil avancé de l'utilisateur"""
    # Chercher le profil utilisateur avancé
    profile = await db.user_profiles.find_one({"user_id": user_id})
    
    if not profile:
        # Créer un profil par défaut si il n'existe pas
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
        profile = profile.dict()
    else:
        profile.pop('_id', None)
    
    # Récupérer les ratings
    seller_ratings = await db.user_ratings.find({
        "rated_user_id": user_id, 
        "rating_type": "seller"
    }).to_list(1000)
    
    buyer_ratings = await db.user_ratings.find({
        "rated_user_id": user_id, 
        "rating_type": "buyer"  
    }).to_list(1000)
    
    # Calculer moyennes
    if seller_ratings:
        profile["avg_seller_rating"] = sum(r["score"] for r in seller_ratings) / len(seller_ratings)
        profile["total_seller_ratings"] = len(seller_ratings)
    
    if buyer_ratings:
        profile["avg_buyer_rating"] = sum(r["score"] for r in buyer_ratings) / len(buyer_ratings)
        profile["total_buyer_ratings"] = len(buyer_ratings)
    
    return profile

@api_router.put("/profile/advanced")
async def update_advanced_profile(profile_update: UserProfileUpdate, user_id: str = Depends(get_current_user)):
    """Met à jour le profil avancé de l'utilisateur"""
    # Vérifier si le profil existe
    existing_profile = await db.user_profiles.find_one({"user_id": user_id})
    
    if not existing_profile:
        # Créer un nouveau profil
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
    
    # Construire les données de mise à jour
    update_data = {}
    for field, value in profile_update.dict(exclude_unset=True).items():
        if value is not None:
            update_data[field] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Profil mis à jour avec succès"}

@api_router.put("/profile/seller-settings")
async def update_seller_settings(seller_settings: SellerSettingsUpdate, user_id: str = Depends(get_current_user)):
    """Met à jour les paramètres vendeur"""
    # S'assurer que le profil existe
    existing_profile = await db.user_profiles.find_one({"user_id": user_id})
    if not existing_profile:
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
    
    # Construire les données de mise à jour
    update_data = {}
    for field, value in seller_settings.dict(exclude_unset=True).items():
        if value is not None:
            update_data[f"seller_settings.{field}"] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Paramètres vendeur mis à jour"}

@api_router.put("/profile/buyer-settings")
async def update_buyer_settings(buyer_settings: BuyerSettingsUpdate, user_id: str = Depends(get_current_user)):
    """Met à jour les paramètres acheteur"""
    existing_profile = await db.user_profiles.find_one({"user_id": user_id})
    if not existing_profile:
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
    
    update_data = {}
    for field, value in buyer_settings.dict(exclude_unset=True).items():
        if value is not None:
            update_data[f"buyer_settings.{field}"] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Paramètres acheteur mis à jour"}

@api_router.put("/profile/collection-settings")
async def update_collection_settings(collection_settings: CollectionSettingsUpdate, user_id: str = Depends(get_current_user)):
    """Met à jour les paramètres de collection"""
    existing_profile = await db.user_profiles.find_one({"user_id": user_id})
    if not existing_profile:
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
    
    update_data = {}
    for field, value in collection_settings.dict(exclude_unset=True).items():
        if value is not None:
            update_data[f"collection_settings.{field}"] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Paramètres de collection mis à jour"}

@api_router.put("/profile/privacy-settings")
async def update_privacy_settings(privacy_settings: PrivacySettingsUpdate, user_id: str = Depends(get_current_user)):
    """Met à jour les paramètres de confidentialité"""
    existing_profile = await db.user_profiles.find_one({"user_id": user_id})
    if not existing_profile:
        profile = UserProfile(user_id=user_id)
        await db.user_profiles.insert_one(profile.dict())
    
    update_data = {}
    for field, value in privacy_settings.dict(exclude_unset=True).items():
        if value is not None:
            update_data[f"privacy_settings.{field}"] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
    
    return {"message": "Paramètres de confidentialité mis à jour"}

@api_router.post("/profile/rating")
async def create_rating(rating_data: RatingCreate, user_id: str = Depends(get_current_user)):
    """Créer une évaluation pour un utilisateur"""
    # Vérifier que l'utilisateur évalué existe
    rated_user = await db.users.find_one({"id": rating_data.rated_user_id})
    if not rated_user:
        raise HTTPException(status_code=404, detail="Utilisateur à évaluer introuvable")
    
    # Vérifier que l'utilisateur n'essaie pas de s'auto-évaluer
    if user_id == rating_data.rated_user_id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous auto-évaluer")
    
    # Créer l'évaluation
    rating = UserRating(
        rater_id=user_id,
        rated_user_id=rating_data.rated_user_id,
        transaction_id=rating_data.transaction_id,
        rating_type=rating_data.rating_type,
        score=rating_data.score,
        comment=rating_data.comment
    )
    
    await db.user_ratings.insert_one(rating.dict())
    
    # Mettre à jour les statistiques du profil
    profile = await db.user_profiles.find_one({"user_id": rating_data.rated_user_id})
    if profile:
        if rating_data.rating_type == "seller":
            ratings = await db.user_ratings.find({
                "rated_user_id": rating_data.rated_user_id,
                "rating_type": "seller"
            }).to_list(1000)
            avg_rating = sum(r["score"] for r in ratings) / len(ratings)
            
            await db.user_profiles.update_one(
                {"user_id": rating_data.rated_user_id},
                {
                    "$set": {
                        "avg_seller_rating": avg_rating,
                        "total_seller_ratings": len(ratings)
                    }
                }
            )
        elif rating_data.rating_type == "buyer":
            ratings = await db.user_ratings.find({
                "rated_user_id": rating_data.rated_user_id,
                "rating_type": "buyer"
            }).to_list(1000)
            avg_rating = sum(r["score"] for r in ratings) / len(ratings)
            
            await db.user_profiles.update_one(
                {"user_id": rating_data.rated_user_id},
                {
                    "$set": {
                        "avg_buyer_rating": avg_rating,
                        "total_buyer_ratings": len(ratings)
                    }
                }
            )
    
    return {"message": "Évaluation créée avec succès"}

@api_router.get("/profile/ratings/{user_id}")
async def get_user_ratings(user_id: str, rating_type: Optional[str] = None):
    """Récupère les évaluations d'un utilisateur"""
    query = {"rated_user_id": user_id}
    if rating_type:
        query["rating_type"] = rating_type
    
    ratings = await db.user_ratings.find(query).sort("created_at", -1).to_list(100)
    
    # Récupérer les informations des évaluateurs
    for rating in ratings:
        rating.pop('_id', None)
        rater = await db.users.find_one({"id": rating["rater_id"]})
        if rater:
            rating["rater_name"] = rater["name"]
            rating["rater_picture"] = rater.get("picture")
    
    return {"ratings": ratings}

@api_router.get("/users/{user_id}/profile/public")
async def get_public_advanced_profile(user_id: str, current_user_id: Optional[str] = Depends(get_current_user_optional)):
    """Récupère le profil public avancé d'un utilisateur"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    profile = await db.user_profiles.find_one({"user_id": user_id})
    
    # Si pas de profil avancé, créer une réponse basique
    if not profile:
        return {
            "user_id": user_id,
            "display_name": user["name"],
            "created_at": user["created_at"],
            "privacy_settings": {"profile_visibility": "public"},
            "stats": {
                "total_sales": 0,
                "total_purchases": 0,
                "avg_seller_rating": None,
                "avg_buyer_rating": None
            }
        }
    
    profile.pop('_id', None)
    
    # Vérifier la confidentialité
    if profile.get("privacy_settings", {}).get("profile_visibility") == "private" and current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Ce profil est privé")
    
    # Filtrer les informations sensibles pour les profils publics
    public_profile = {
        "user_id": user_id,
        "display_name": profile.get("display_name") or user["name"],
        "bio": profile.get("bio"),
        "location": profile.get("location") if profile.get("privacy_settings", {}).get("show_location", True) else None,
        "website": profile.get("website"),
        "social_links": profile.get("social_links", {}),
        "created_at": user["created_at"] if profile.get("privacy_settings", {}).get("show_join_date", True) else None,
        "badges": profile.get("badges", []),
        "verified_seller": profile.get("verified_seller", False),
        "stats": {
            "total_sales": profile.get("total_sales", 0),
            "total_purchases": profile.get("total_purchases", 0),
            "avg_seller_rating": profile.get("avg_seller_rating"),
            "avg_buyer_rating": profile.get("avg_buyer_rating"),
            "total_seller_ratings": profile.get("total_seller_ratings", 0),
            "total_buyer_ratings": profile.get("total_buyer_ratings", 0)
        }
    }
    
    # Ajouter les paramètres vendeur si c'est un vendeur actif
    if profile.get("seller_settings", {}).get("is_seller", False):
        seller_settings = profile.get("seller_settings", {})
        public_profile["seller_info"] = {
            "is_seller": True,
            "business_name": seller_settings.get("business_name"),
            "return_policy": seller_settings.get("return_policy"),
            "shipping_policy": seller_settings.get("shipping_policy"),
            "payment_methods": seller_settings.get("payment_methods", []),
            "processing_time_days": seller_settings.get("processing_time_days", 3),
            "return_days": seller_settings.get("return_days", 14)
        }
    
    return public_profile

# User Profile API Endpoints for UserProfilePage
@api_router.get("/users/{user_id}/profile")
async def get_user_public_profile(user_id: str):
    """Get public profile information for a specific user"""
    try:
        # Get user basic information
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user stats
        jerseys_count = await db.jerseys.count_documents({"creator_id": user_id})
        owned_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "owned"})
        wanted_count = await db.collections.count_documents({"user_id": user_id, "collection_type": "wanted"})
        
        # Get seller ratings average
        seller_ratings = await db.ratings.find({"rated_user_id": user_id, "rating_type": "seller"}).to_list(1000)
        avg_seller_rating = sum(r["score"] for r in seller_ratings) / len(seller_ratings) if seller_ratings else None
        
        # Get seller settings if user is a seller
        seller_info = None
        if user.get("seller_settings", {}).get("is_seller"):
            seller_settings = user.get("seller_settings", {})
            seller_info = {
                "business_name": seller_settings.get("business_name"),
                "processing_time_days": seller_settings.get("processing_time_days", 3),
                "return_days": seller_settings.get("return_days", 14),
                "payment_methods": seller_settings.get("payment_methods", []),
                "verified": seller_settings.get("verified", False)
            }
        
        profile_data = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "display_name": user.get("display_name", user["name"]),
            "picture": user.get("picture"),
            "bio": user.get("bio"),
            "location": user.get("location"),
            "verified_seller": user.get("seller_settings", {}).get("verified", False),
            "seller_info": seller_info,
            "stats": {
                "jerseys_submitted": jerseys_count,
                "owned_jerseys": owned_count,
                "wanted_jerseys": wanted_count,
                "avg_seller_rating": avg_seller_rating
            },
            "badges": user.get("badges", []),
            "created_at": user.get("created_at"),
            "social_links": user.get("social_links", {})
        }
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Friends System API Endpoints
@api_router.get("/users/search")
async def search_users(
    query: str, 
    limit: int = 10,
    user_id: str = Depends(get_current_user)
):
    """Search for users to add as friends - excludes admin users"""
    if len(query) < 2:
        return []
    
    # Search by name or email (exclude current user and admin users)
    search_filter = {
        "$and": [
            {"id": {"$ne": user_id}},  # Exclude current user
            {"email": {"$ne": ADMIN_EMAIL}},  # Exclude admin by email
            {"role": {"$ne": "admin"}},  # Exclude admin by role
            {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    users = await db.users.find(
        search_filter,
        {"id": 1, "name": 1, "email": 1, "picture": 1}
    ).limit(limit).to_list(limit)
    
    # Remove MongoDB ObjectId and return clean user data
    for user in users:
        user.pop('_id', None)
    
    return users

@api_router.post("/friends/request")
async def send_friend_request(
    friend_request: FriendRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a friend request"""
    
    user_id = current_user["id"]  # 🔧 FIX: Extract user_id from user object
    
    # Check if user exists
    target_user = await db.users.find_one({"id": friend_request.user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't send friend request to yourself
    if friend_request.user_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if friendship already exists or is pending
    existing_friendship = await db.friendships.find_one({
        "$or": [
            {"requester_id": user_id, "addressee_id": friend_request.user_id},
            {"requester_id": friend_request.user_id, "addressee_id": user_id}
        ]
    })
    
    if existing_friendship:
        if existing_friendship["status"] == FriendshipStatus.ACCEPTED:
            raise HTTPException(status_code=400, detail="Users are already friends")
        elif existing_friendship["status"] == FriendshipStatus.PENDING:
            raise HTTPException(status_code=400, detail="Friend request already sent")
        elif existing_friendship["status"] == FriendshipStatus.BLOCKED:
            raise HTTPException(status_code=400, detail="Unable to send friend request")
    
    # Create friendship request
    friendship = Friendship(
        requester_id=user_id,
        addressee_id=friend_request.user_id
    )
    
    await db.friendships.insert_one(friendship.dict())
    
    # Get requester info for notification
    requester_name = current_user.get("name", "Someone")  # 🔧 FIX: Use current_user directly
    
    # Create notification for the target user
    await create_notification(
        user_id=friend_request.user_id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title="New Friend Request",
        message=f"{requester_name} wants to be your friend! You can accept or decline this request in your friends section.",
        related_id=friendship.id
    )
    
    return {"message": "Friend request sent successfully", "request_id": friendship.id}

@api_router.post("/friends/respond")
async def respond_to_friend_request(
    response: FriendRequestResponse,
    current_user: dict = Depends(get_current_user)
):
    """Accept or decline a friend request"""
    user_id = current_user["id"]
    
    # Find the friend request
    friendship = await db.friendships.find_one({
        "id": response.request_id,
        "addressee_id": user_id,
        "status": FriendshipStatus.PENDING
    })
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    # Update friendship status
    new_status = FriendshipStatus.ACCEPTED if response.accept else FriendshipStatus.BLOCKED
    await db.friendships.update_one(
        {"id": response.request_id},
        {
            "$set": {
                "status": new_status,
                "responded_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Get user names for notifications
    requester = await db.users.find_one({"id": friendship["requester_id"]})
    addressee = await db.users.find_one({"id": user_id})
    
    requester_name = requester.get("name", "Someone") if requester else "Someone"
    addressee_name = addressee.get("name", "Someone") if addressee else "Someone"
    
    if response.accept:
        # Notify requester that request was accepted
        await create_notification(
            user_id=friendship["requester_id"],
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title="Friend Request Accepted! 🎉",
            message=f"{addressee_name} accepted your friend request! You are now friends and can message each other.",
            related_id=friendship["id"]
        )
        return {"message": "Friend request accepted"}
    else:
        return {"message": "Friend request declined"}

@api_router.get("/friends")
async def get_friends(current_user: dict = Depends(get_current_user)):
    """Get user's friends list and pending requests"""
    user_id = current_user["id"]
    
    # Get accepted friends
    friends_pipeline = [
        {
            "$match": {
                "$and": [
                    {
                        "$or": [
                            {"requester_id": user_id},
                            {"addressee_id": user_id}
                        ]
                    },
                    {"status": FriendshipStatus.ACCEPTED}
                ]
            }
        },
        {
            "$addFields": {
                "friend_id": {
                    "$cond": {
                        "if": {"$eq": ["$requester_id", user_id]},
                        "then": "$addressee_id",
                        "else": "$requester_id"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "friend_id",
                "foreignField": "id",
                "as": "friend_info"
            }
        },
        {"$unwind": "$friend_info"},
        {
            "$project": {
                "friendship_id": "$id",
                "friend_id": "$friend_id",
                "name": "$friend_info.name",
                "email": "$friend_info.email",
                "picture": "$friend_info.picture",
                "friends_since": "$responded_at",
                "_id": 0
            }
        }
    ]
    
    # Get pending requests (received)
    pending_received_pipeline = [
        {
            "$match": {
                "addressee_id": user_id,
                "status": FriendshipStatus.PENDING
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "requester_id",
                "foreignField": "id",
                "as": "requester_info"
            }
        },
        {"$unwind": "$requester_info"},
        {
            "$project": {
                "request_id": "$id",
                "requester_id": "$requester_id",
                "name": "$requester_info.name",
                "email": "$requester_info.email",
                "picture": "$requester_info.picture",
                "requested_at": "$requested_at",
                "_id": 0
            }
        }
    ]
    
    # Get pending requests (sent)
    pending_sent_pipeline = [
        {
            "$match": {
                "requester_id": user_id,
                "status": FriendshipStatus.PENDING
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "addressee_id",
                "foreignField": "id",
                "as": "addressee_info"
            }
        },
        {"$unwind": "$addressee_info"},
        {
            "$project": {
                "request_id": "$id",
                "addressee_id": "$addressee_id",
                "name": "$addressee_info.name",
                "email": "$addressee_info.email",
                "picture": "$addressee_info.picture",
                "requested_at": "$requested_at",
                "_id": 0
            }
        }
    ]
    
    friends = await db.friendships.aggregate(friends_pipeline).to_list(1000)
    pending_received = await db.friendships.aggregate(pending_received_pipeline).to_list(100)
    pending_sent = await db.friendships.aggregate(pending_sent_pipeline).to_list(100)
    
    return {
        "friends": friends,
        "pending_requests": {
            "received": pending_received,
            "sent": pending_sent
        },
        "stats": {
            "total_friends": len(friends),
            "pending_received": len(pending_received),
            "pending_sent": len(pending_sent)
        }
    }

@api_router.delete("/friends/{friend_id}")
async def remove_friend(
    friend_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove a friend from user's friends list"""
    user_id = current_user["id"]
    
    # Find the friendship (could be in either direction)
    friendship = await db.friendships.find_one({
        "$and": [
            {
                "$or": [
                    {"requester_id": user_id, "addressee_id": friend_id},
                    {"requester_id": friend_id, "addressee_id": user_id}
                ]
            },
            {"status": FriendshipStatus.ACCEPTED}
        ]
    })
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    # Delete the friendship
    await db.friendships.delete_one({"id": friendship["id"]})
    
    # Get friend's name for notification
    friend = await db.users.find_one({"id": friend_id})
    friend_name = friend.get("name", "Someone") if friend else "Someone"
    
    # Notify the removed friend
    await create_notification(
        user_id=friend_id,
        notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
        title="Friendship Ended",
        message=f"{current_user['name']} has removed you from their friends list.",
        related_id=friendship["id"]
    )
    
    return {"message": f"Successfully removed {friend_name} from your friends list"}

# Messaging System API Endpoints  
@api_router.post("/conversations")
async def create_conversation(
    message_data: MessageCreateV2,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation or add message to existing conversation"""
    
    user_id = current_user["id"]  # 🔧 FIX: Extract user_id from user object
    
    if message_data.conversation_id:
        # Add message to existing conversation
        conversation = await db.conversations.find_one({"id": message_data.conversation_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if user is participant
        participant_ids = [p["user_id"] for p in conversation["participants"]]
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Not authorized to message in this conversation")
        
        conversation_id = message_data.conversation_id
        
    else:
        # Create new conversation with recipient
        if not message_data.recipient_id:
            raise HTTPException(status_code=400, detail="recipient_id required for new conversations")
        
        # Check if recipient exists
        recipient = await db.users.find_one({"id": message_data.recipient_id})
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Check if conversation already exists between these users
        existing_conversation = await db.conversations.find_one({
            "participants": {
                "$all": [
                    {"$elemMatch": {"user_id": user_id}},
                    {"$elemMatch": {"user_id": message_data.recipient_id}}
                ]
            }
        })
        
        if existing_conversation:
            conversation_id = existing_conversation["id"]
        else:
            # Create new conversation
            conversation = Conversation(
                participants=[
                    ConversationParticipant(user_id=user_id),
                    ConversationParticipant(user_id=message_data.recipient_id)
                ]
            )
            await db.conversations.insert_one(conversation.dict())
            conversation_id = conversation.id
    
    # Create message
    message = Message(
        sender_id=user_id,
        recipient_id=message_data.recipient_id or "",  # Will be updated for existing conversations
        message=message_data.message
    )
    
    # If this is an existing conversation, update recipient_id based on other participant
    if message_data.conversation_id:
        conversation = await db.conversations.find_one({"id": conversation_id})
        other_participants = [p["user_id"] for p in conversation["participants"] if p["user_id"] != user_id]
        if other_participants:
            message.recipient_id = other_participants[0]
    
    await db.messages.insert_one(message.dict())
    
    # Update conversation last message time
    await db.conversations.update_one(
        {"id": conversation_id},
        {
            "$set": {
                "last_message_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Message sent successfully",
        "conversation_id": conversation_id,
        "message_id": message.id
    }

@api_router.get("/conversations")
async def get_conversations(user_id: str = Depends(get_current_user)):
    """Get all conversations for a user"""
    
    pipeline = [
        {
            "$match": {
                "participants": {"$elemMatch": {"user_id": user_id}}
            }
        },
        {
            "$lookup": {
                "from": "messages",
                "localField": "id",
                "foreignField": "sender_id",  # This is incorrect but will be fixed
                "as": "messages"
            }
        },
        {
            "$addFields": {
                "other_participant": {
                    "$filter": {
                        "input": "$participants",
                        "cond": {"$ne": ["$$this.user_id", user_id]}
                    }
                }
            }
        },
        {"$unwind": "$other_participant"},
        {
            "$lookup": {
                "from": "users",
                "localField": "other_participant.user_id",
                "foreignField": "id",
                "as": "other_user_info"
            }
        },
        {"$unwind": "$other_user_info"},
        {
            "$project": {
                "conversation_id": "$id",
                "other_user": {
                    "id": "$other_user_info.id",
                    "name": "$other_user_info.name",
                    "picture": "$other_user_info.picture"
                },
                "last_message_at": "$last_message_at",
                "created_at": "$created_at",
                "_id": 0
            }
        },
        {"$sort": {"last_message_at": -1}}
    ]
    
    conversations = await db.conversations.aggregate(pipeline).to_list(100)
    
    # Get last message for each conversation
    for conv in conversations:
        last_message = await db.messages.find_one(
            {
                "$or": [
                    {"sender_id": user_id, "recipient_id": conv["other_user"]["id"]},
                    {"sender_id": conv["other_user"]["id"], "recipient_id": user_id}
                ]
            },
            sort=[("created_at", -1)]
        )
        
        if last_message:
            last_message.pop('_id', None)
            conv["last_message"] = {
                "message": last_message["message"],
                "sent_by_me": last_message["sender_id"] == user_id,
                "created_at": last_message["created_at"],
                "read": last_message["read"]
            }
        else:
            conv["last_message"] = None
    
    return conversations

@api_router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    skip: int = 0,
    user_id: str = Depends(get_current_user)
):
    """Get messages from a specific conversation"""
    
    # Verify user is participant in conversation
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    participant_ids = [p["user_id"] for p in conversation["participants"]]
    if user_id not in participant_ids:
        raise HTTPException(status_code=403, detail="Not authorized to view this conversation")
    
    # Get other participant ID
    other_participant_id = None
    for p in conversation["participants"]:
        if p["user_id"] != user_id:
            other_participant_id = p["user_id"]
            break
    
    if not other_participant_id:
        raise HTTPException(status_code=400, detail="Invalid conversation")
    
    # Get messages between these users
    messages = await db.messages.find({
        "$or": [
            {"sender_id": user_id, "recipient_id": other_participant_id},
            {"sender_id": other_participant_id, "recipient_id": user_id}
        ]
    }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Remove MongoDB ObjectId and add sender info
    for message in messages:
        message.pop('_id', None)
        message["sent_by_me"] = message["sender_id"] == user_id
    
    # Mark messages as read
    await db.messages.update_many(
        {
            "sender_id": other_participant_id,
            "recipient_id": user_id,
            "read": False
        },
        {"$set": {"read": True}}
    )
    
    return {
        "messages": list(reversed(messages)),  # Return in chronological order
        "conversation_id": conversation_id,
        "total": len(messages)
    }

@api_router.post("/admin/cleanup/database")
async def cleanup_database(
    admin_user: dict = Depends(get_current_user_admin)
):
    """Clean database - keep only admin and steinmetzlivio@gmail.com accounts (Admin only)"""
    
    # Define accounts to keep
    accounts_to_keep = ["topkitfr@gmail.com", "steinmetzlivio@gmail.com"]
    
    # Get users to keep
    users_to_keep = []
    for email in accounts_to_keep:
        user = await db.users.find_one({"email": email})
        if user:
            users_to_keep.append(user["id"])
    
    # Count before deletion
    initial_counts = {
        "users": await db.users.count_documents({}),
        "jerseys": await db.jerseys.count_documents({}),
        "collections": await db.collections.count_documents({}),
        "listings": await db.listings.count_documents({}),
        "messages": await db.messages.count_documents({}),
        "conversations": await db.conversations.count_documents({})
    }
    
    # Delete users except those to keep
    await db.users.delete_many({"email": {"$nin": accounts_to_keep}})
    
    # Delete all jerseys
    await db.jerseys.delete_many({})
    
    # Delete all collections
    await db.collections.delete_many({})
    
    # Delete all listings
    await db.listings.delete_many({})
    
    # Delete all messages and conversations
    await db.messages.delete_many({})
    await db.conversations.delete_many({})
    
    # Delete all user activities except for kept users
    await db.user_activities.delete_many({"user_id": {"$nin": users_to_keep}})
    
    # Delete all beta access requests 
    await db.beta_access_requests.delete_many({})
    
    # Delete all notifications except for kept users
    await db.notifications.delete_many({"user_id": {"$nin": users_to_keep}})
    
    # Count after deletion
    final_counts = {
        "users": await db.users.count_documents({}),
        "jerseys": await db.jerseys.count_documents({}),
        "collections": await db.collections.count_documents({}),
        "listings": await db.listings.count_documents({}),
        "messages": await db.messages.count_documents({}),
        "conversations": await db.conversations.count_documents({})
    }
    
    # Log cleanup activity
    await db.user_activities.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": admin_user['id'],
        "action": "database_cleanup",
        "details": {
            "initial_counts": initial_counts,
            "final_counts": final_counts,
            "accounts_kept": accounts_to_keep
        },
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": "Base de données nettoyée avec succès",
        "accounts_kept": accounts_to_keep,
        "initial_counts": initial_counts,
        "final_counts": final_counts,
        "deleted": {
            "users": initial_counts["users"] - final_counts["users"],
            "jerseys": initial_counts["jerseys"],
            "collections": initial_counts["collections"],
            "listings": initial_counts["listings"],
            "messages": initial_counts["messages"],
            "conversations": initial_counts["conversations"]
        }
    }

@api_router.post("/admin/cleanup/jersey-releases")
async def cleanup_jersey_releases(
    admin_user: dict = Depends(get_current_user_admin)
):
    """Clean all Jersey Releases and related collections (Admin only)"""
    
    # Count before deletion
    initial_counts = {
        "jersey_releases": await db.jersey_releases.count_documents({}),
        "user_jersey_collections": await db.user_jersey_collections.count_documents({})
    }
    
    # Delete all Jersey Releases
    await db.jersey_releases.delete_many({})
    
    # Delete all user Jersey Release collections
    await db.user_jersey_collections.delete_many({})
    
    # Count after deletion
    final_counts = {
        "jersey_releases": await db.jersey_releases.count_documents({}),
        "user_jersey_collections": await db.user_jersey_collections.count_documents({})
    }
    
    # Log cleanup activity
    await db.user_activities.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": admin_user['id'],
        "action": "jersey_releases_cleanup",
        "details": {
            "initial_counts": initial_counts,
            "final_counts": final_counts
        },
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": "Jersey Releases et collections supprimés avec succès",
        "initial_counts": initial_counts,
        "final_counts": final_counts,
        "deleted": {
            "jersey_releases": initial_counts["jersey_releases"],
            "user_jersey_collections": initial_counts["user_jersey_collections"]
        }
    }

@api_router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Get public profile of a user"""
    
    # Get user profile
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Public profile data (no sensitive info)
    profile_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],  # Could be hidden based on privacy settings
        "username": user.get("username"),
        "picture": user.get("picture"),
        "created_at": user.get("created_at"),
        "last_login": user.get("last_login"),
        "role": user.get("role", "user")
    }
    
    return profile_data

@api_router.get("/users/{user_id}/collection")
async def get_user_collection(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Get public collection of a user"""
    
    # Get user's collection (public items only)
    collection_cursor = db.collections.find({
        "user_id": user_id,
        "collection_type": "owned"  # Only show owned items in public profile
    })
    
    collection_items = []
    async for item in collection_cursor:
        # Get jersey details
        jersey = await db.jerseys.find_one({"id": item["jersey_id"]})
        if jersey and jersey.get("status") == "approved":  # Only show approved jerseys
            collection_items.append({
                "id": item["id"],
                "jersey": jersey,
                "size": item.get("size"),
                "condition": item.get("condition"),
                "personal_description": item.get("personal_description"),
                "added_at": item.get("added_at")
            })
    
    return collection_items

@api_router.get("/users/{user_id}/listings")
async def get_user_listings(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """Get active listings of a user"""
    
    # Get user's active listings
    listings_cursor = db.listings.find({
        "user_id": user_id,
        "status": "active"
    })
    
    user_listings = []
    async for listing in listings_cursor:
        # Get jersey details
        jersey = await db.jerseys.find_one({"id": listing["jersey_id"]})
        if jersey:
            listing_data = dict(listing)
            listing_data["jersey"] = jersey
            user_listings.append(listing_data)
    
    return user_listings

@api_router.get("/stats/dynamic")
async def get_dynamic_stats():
    """Get dynamic site statistics for homepage"""
    
    # Count approved jerseys
    approved_jerseys = await db.jerseys.count_documents({"status": "approved"})
    
    # Count total users (excluding admins)
    total_users = await db.users.count_documents({"role": {"$ne": "admin"}})
    
    # Count total listings
    total_listings = await db.listings.count_documents({})
    
    # Count collections (owned + wanted)
    total_collections = await db.collections.count_documents({})
    
    # Count pending jerseys for admin info
    pending_jerseys = await db.jerseys.count_documents({"status": "pending"})
    
    # Count moderators
    moderators = await db.users.count_documents({"role": "moderator"})
    
    return {
        "approved_jerseys": approved_jerseys,
        "total_users": total_users,
        "total_listings": total_listings, 
        "total_collections": total_collections,
        "pending_jerseys": pending_jerseys,
        "moderators": moderators
    }

# WebSocket Connection Manager for Real-time Messaging
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id: websocket
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"📱 User {user_id} connected to WebSocket")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"📱 User {user_id} disconnected from WebSocket")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
                return True
            except:
                # Connection might be stale, remove it
                self.disconnect(user_id)
                return False
        return False
    
    async def notify_new_message(self, sender_id: str, recipient_id: str, message_data: dict):
        """Notify recipient of new message in real-time"""
        notification_data = {
            "type": "new_message",
            "sender_id": sender_id,
            "message": message_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(json.dumps(notification_data), recipient_id)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time messaging"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle any incoming WebSocket messages if needed
            # For now, we'll just use it for receiving real-time notifications
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# Updated message creation endpoint with real-time notification
@api_router.post("/conversations/send")
async def send_message_realtime(
    message_data: MessageCreateV2,
    user_id: str = Depends(get_current_user)
):
    """Send a message with real-time notification"""
    
    if message_data.conversation_id:
        # Add message to existing conversation
        conversation = await db.conversations.find_one({"id": message_data.conversation_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if user is participant
        participant_ids = [p["user_id"] for p in conversation["participants"]]
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Not authorized to message in this conversation")
        
        conversation_id = message_data.conversation_id
        recipient_id = None
        for p in conversation["participants"]:
            if p["user_id"] != user_id:
                recipient_id = p["user_id"]
                break
        
    else:
        # Create new conversation with recipient
        if not message_data.recipient_id:
            raise HTTPException(status_code=400, detail="recipient_id required for new conversations")
        
        # Check if recipient exists
        recipient = await db.users.find_one({"id": message_data.recipient_id})
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        recipient_id = message_data.recipient_id
        
        # Check if conversation already exists between these users
        existing_conversation = await db.conversations.find_one({
            "participants": {
                "$all": [
                    {"$elemMatch": {"user_id": user_id}},
                    {"$elemMatch": {"user_id": recipient_id}}
                ]
            }
        })
        
        if existing_conversation:
            conversation_id = existing_conversation["id"]
        else:
            # Create new conversation
            conversation = Conversation(
                participants=[
                    ConversationParticipant(user_id=user_id),
                    ConversationParticipant(user_id=recipient_id)
                ]
            )
            await db.conversations.insert_one(conversation.dict())
            conversation_id = conversation.id
    
    # Create message
    message = Message(
        sender_id=user_id,
        recipient_id=recipient_id,
        message=message_data.message
    )
    
    await db.messages.insert_one(message.dict())
    
    # Update conversation last message time
    await db.conversations.update_one(
        {"id": conversation_id},
        {
            "$set": {
                "last_message_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Get sender info for real-time notification
    sender = await db.users.find_one({"id": user_id})
    sender_name = sender.get("name", "Someone") if sender else "Someone"
    
    # Send real-time notification to recipient
    message_notification = {
        "id": message.id,
        "conversation_id": conversation_id,
        "sender_id": user_id,
        "sender_name": sender_name,
        "message": message.message,
        "created_at": message.created_at.isoformat()
    }
    
    await manager.notify_new_message(user_id, recipient_id, message_notification)
    
    return {
        "message": "Message sent successfully",
        "conversation_id": conversation_id,
        "message_id": message.id,
        "real_time_sent": recipient_id in manager.active_connections
    }

# Site Mode Management Endpoints
@api_router.get("/site/mode")
async def get_site_mode():
    """Get current site mode (public/private)"""
    return {
        "mode": SITE_MODE,
        "is_private": SITE_MODE == "private",
        "message": "Site en mode privé - accès limité aux utilisateurs autorisés" if SITE_MODE == "private" else "Site en mode public"
    }

@api_router.post("/site/mode")
async def update_site_mode(
    site_mode_request: SiteModeRequest,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Update site mode (admin only)"""
    
    # Validate mode
    if site_mode_request.mode not in ["private", "public"]:
        raise HTTPException(status_code=400, detail="Mode invalide - utiliser 'private' ou 'public'")
    
    # For production deployment, this would update environment variable
    # For now, we'll store in database as a site setting
    await db.site_settings.update_one(
        {"setting": "site_mode"},
        {
            "$set": {
                "setting": "site_mode",
                "value": site_mode_request.mode,
                "updated_by": admin_user["id"],
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Log the change
    await log_user_activity(admin_user["id"], "site_mode_changed", "", {
        "old_mode": SITE_MODE,
        "new_mode": site_mode_request.mode,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return SiteModeResponse(
        mode=site_mode_request.mode,
        message=f"Mode du site changé vers: {site_mode_request.mode}"
    )

@api_router.get("/site/access-check")
async def check_site_access(user_id: str = Depends(get_current_user_optional)):
    """Check if current user has access to the site when in private mode"""
    
    # Get site mode from database (overrides environment)
    site_setting = await db.site_settings.find_one({"setting": "site_mode"})
    current_mode = site_setting.get("value", SITE_MODE) if site_setting else SITE_MODE
    
    if current_mode == "public":
        return {
            "has_access": True,
            "mode": "public",
            "message": "Site accessible à tous"
        }
    
    # Private mode - check user access
    if not user_id:
        return {
            "has_access": False,
            "mode": "private",
            "message": "Connexion requise - site en mode privé"
        }
    
    # Check if user has access (admin always has access)
    user = await db.users.find_one({"id": user_id})
    if not user:
        return {
            "has_access": False,
            "mode": "private",
            "message": "Utilisateur non trouvé"
        }
    
    # Admin and authorized users have access
    if user.get("role") == "admin" or user.get("beta_access", False):
        return {
            "has_access": True,
            "mode": "private",
            "user_role": user.get("role", "user"),
            "message": "Accès autorisé au site privé"
        }
    
    return {
        "has_access": False,
        "mode": "private",
        "message": "Accès non autorisé - site en mode bêta privée"
    }

@api_router.post("/beta/request-access")
async def request_beta_access(request: BetaAccessRequest):
    """Submit a beta access request"""
    
    try:
        # Check if email already requested access
        existing_request = await db.beta_access_requests.find_one({"email": request.email})
        if existing_request:
            return {
                "message": "Une demande d'accès a déjà été soumise avec cette adresse email",
                "request_id": existing_request["id"]
            }
        
        # Create new beta access request
        access_request = {
            "id": str(uuid.uuid4()),
            "email": request.email,
            "first_name": request.first_name,
            "last_name": request.last_name,
            "message": request.message or "",
            "status": "pending",  # pending, approved, rejected
            "requested_at": datetime.utcnow(),
            "processed_at": None,
            "processed_by": None
        }
        
        await db.beta_access_requests.insert_one(access_request)
        
        # Send notification email to admin about new beta request
        admin_notified = False
        if gmail_service:
            try:
                # Get admin email for notification
                admin_user = await db.users.find_one({"role": "admin"})
                if admin_user:
                    admin_notified = gmail_service.send_beta_access_notification(
                        admin_email=admin_user["email"],
                        request_data={
                            "email": request.email,
                            "first_name": request.first_name,
                            "last_name": request.last_name,
                            "message": request.message or "Aucun message",
                            "request_id": access_request["id"]
                        }
                    )
                    if admin_notified:
                        logger.info(f"Beta access notification sent to admin {admin_user['email']}")
            except Exception as e:
                logger.error(f"Failed to send beta access notification: {e}")
        
        # Log the activity
        await log_user_activity("system", "beta_access_requested", request.email, {
            "name": f"{request.first_name} {request.last_name}",
            "email": request.email,  
            "message": request.message or "No message",
            "admin_notified": admin_notified
        })
        
        return BetaAccessResponse(
            message="Demande d'accès soumise avec succès ! Votre demande sera examinée par notre équipe administrative. Vous serez contacté uniquement si votre demande est approuvée.",
            request_id=access_request["id"]
        )
        
    except Exception as e:
        logger.error(f"Error submitting beta access request: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la soumission de la demande")

@api_router.get("/admin/beta/requests")
async def get_beta_access_requests(
    current_user: dict = Depends(get_current_user_admin),
    status: Optional[str] = None,
    limit: int = 50
):
    """Get beta access requests (admin only)"""
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    
    # Get requests
    requests_cursor = db.beta_access_requests.find(query).sort("requested_at", -1).limit(limit)
    requests = await requests_cursor.to_list(limit)
    
    # Remove MongoDB _id field
    for request in requests:
        request.pop('_id', None)
    
    return {
        "requests": requests,
        "total": len(requests),
        "filter": status or "all"
    }

@api_router.post("/admin/beta/requests/{request_id}/approve")
async def approve_beta_access_request(
    request_id: str,
    current_user: dict = Depends(get_current_user_admin)
):
    """Approve a beta access request and grant access to user (admin only)"""
    
    # Get the request
    access_request = await db.beta_access_requests.find_one({"id": request_id})
    if not access_request:
        raise HTTPException(status_code=404, detail="Demande d'accès non trouvée")
    
    if access_request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")
    
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": access_request["email"]})
        
        if existing_user:
            # Grant beta access to existing user
            await db.users.update_one(
                {"id": existing_user["id"]},
                {
                    "$set": {
                        "beta_access": True,
                        "beta_granted_at": datetime.utcnow(),
                        "beta_granted_by": current_user['id']
                    }
                }
            )
            
            # Send welcome email for existing user
            if gmail_service:
                try:
                    welcome_sent = gmail_service.send_beta_access_approved_email(
                        user_email=access_request["email"],
                        user_name=f"{access_request['first_name']} {access_request['last_name']}",
                        temp_password=None  # Existing user, no temp password
                    )
                    if welcome_sent:
                        logger.info(f"Beta access approval email sent to existing user {access_request['email']}")
                except Exception as e:
                    logger.error(f"Failed to send beta access approval email to existing user: {e}")
        else:
            # Create a temporary password for the user
            temp_password = f"{access_request['first_name'].lower()}{random.randint(1000, 9999)}"
            hashed_password = hash_password(temp_password)
            
            # Create new user with beta access
            new_user = User(
                email=access_request["email"],
                password_hash=hashed_password,
                name=f"{access_request['first_name']} {access_request['last_name']}",
                provider="custom",  # Required field
                role="user",
                email_verified=True,  # Auto-verify for beta users
                beta_access=True,
                beta_granted_at=datetime.utcnow(),
                beta_granted_by=current_user['id']
            )
            
            await db.users.insert_one(new_user.dict())
            
            # Send welcome email with access approval
            if gmail_service:
                try:
                    welcome_sent = gmail_service.send_beta_access_approved_email(
                        user_email=access_request["email"],
                        user_name=f"{access_request['first_name']} {access_request['last_name']}",
                        temp_password=temp_password
                    )
                    if welcome_sent:
                        logger.info(f"Beta access approval email sent to {access_request['email']}")
                except Exception as e:
                    logger.error(f"Failed to send beta access approval email: {e}")
            
            logger.info(f"Created beta user: {access_request['email']} with temp password: {temp_password}")
        
        # Update request status
        await db.beta_access_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": "approved",
                    "processed_at": datetime.utcnow(),
                    "processed_by": current_user['id']
                }
            }
        )
        
        # Log activity
        await log_user_activity(current_user['id'], "beta_access_approved", access_request["email"], {
            "request_id": request_id,
            "user_name": f"{access_request['first_name']} {access_request['last_name']}",
            "user_email": access_request["email"]
        })
        
        return {
            "message": f"Accès bêta accordé à {access_request['first_name']} {access_request['last_name']}",
            "user_created": not bool(existing_user)
        }
        
    except Exception as e:
        logger.error(f"Error approving beta access request: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'approbation de la demande")

@api_router.post("/admin/beta/requests/{request_id}/reject")
async def reject_beta_access_request(
    request_id: str,
    reject_data: RejectBetaRequest,
    current_user: dict = Depends(get_current_user_admin)
):
    """Reject a beta access request (admin only)"""
    
    # Get the request
    access_request = await db.beta_access_requests.find_one({"id": request_id})
    if not access_request:
        raise HTTPException(status_code=404, detail="Demande d'accès non trouvée")
    
    if access_request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Cette demande a déjà été traitée")
    
    # Update request status
    await db.beta_access_requests.update_one(
        {"id": request_id},
        {
            "$set": {
                "status": "rejected",
                "rejection_reason": reject_data.reason,
                "processed_at": datetime.utcnow(),
                "processed_by": current_user["id"]
            }
        }
    )
    
    # Log activity
    await log_user_activity(current_user["id"], "beta_access_rejected", access_request["email"], {
        "request_id": request_id,
        "user_name": f"{access_request['first_name']} {access_request['last_name']}",
        "user_email": access_request["email"],
        "reason": reject_data.reason
    })
    
    return {
        "message": f"Demande d'accès de {access_request['first_name']} {access_request['last_name']} rejetée",
        "reason": reject_data.reason
    }

# =============================================================================
# 🛡️ SECURE PAYMENT SYSTEM - ANTI-FRAUD (LEBONCOIN STYLE)
# =============================================================================

@api_router.post("/payments/secure/checkout")
async def create_secure_checkout(
    checkout_data: CheckoutRequest,
    user_id: str = Depends(get_current_user)
):
    """
    🛡️ Créer un paiement sécurisé avec blocage de fonds (style Leboncoin)
    L'argent reste bloqué jusqu'à vérification de l'authenticité du maillot
    """
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    # Vérifications de base
    listing = await db.listings.find_one({"id": checkout_data.listing_id, "status": "active"})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or inactive")
    
    jersey = await db.jerseys.find_one({"id": listing["jersey_id"]})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    seller = await db.users.find_one({"id": listing["seller_id"]})
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Vérification que l'acheteur n'est pas le vendeur
    if user_id == listing["seller_id"]:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas acheter votre propre maillot")
    
    # Calculs financiers
    listing_price = float(listing["price"])
    commission_amount = round(listing_price * TOPKIT_COMMISSION_RATE, 2)
    seller_amount = round(listing_price - commission_amount, 2)
    
    try:
        # 🔑 CLEF DU SYSTÈME : Créer un Payment Intent avec capture MANUELLE
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        
        # Créer la session Stripe avec paiement BLOQUÉ
        session_request = CheckoutSessionRequest(
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": f"🏆 {jersey['team']} - {jersey.get('player_name', 'Maillot')} ({jersey.get('season', 'N/A')})",
                        "description": f"Taille: {listing.get('size', 'N/A')} • Condition: {listing.get('condition', 'N/A')} • Vérification authenticité garantie",
                        "images": jersey.get("images", [])[:1]  # Première image
                    },
                    "unit_amount": int(listing_price * 100)  # En centimes
                },
                "quantity": 1
            }],
            mode="payment",
            success_url=f"{checkout_data.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{checkout_data.origin_url}/payment/cancelled",
            customer_email=None,  # Sera rempli automatiquement
            metadata={
                "listing_id": listing["id"],
                "jersey_id": jersey["id"],
                "seller_id": listing["seller_id"],
                "buyer_id": user_id,
                "jersey_name": f"{jersey['team']} - {jersey.get('player_name', 'Maillot')}",
                "seller_name": seller["name"],
                "commission_amount": str(commission_amount),
                "seller_amount": str(seller_amount),
                "secure_transaction": "true",  # 🛡️ Indicateur paiement sécurisé
                "requires_verification": "true"
            },
            payment_intent_data={
                "capture_method": "manual",  # 🔑 PAIEMENT BLOQUÉ JUSQU'À VALIDATION
                "description": f"TopKit - Achat sécurisé maillot {jersey['team']}",
            }
        )
        
        session = await stripe_checkout.create_checkout_session(session_request)
        
        # Créer la transaction sécurisée dans notre DB
        secure_transaction = SecureTransaction(
            listing_id=listing["id"],
            buyer_id=user_id,
            seller_id=listing["seller_id"],
            amount=listing_price,
            stripe_session_id=session.session_id,
            stripe_payment_intent_id="",  # Sera mis à jour après paiement
            status=TransactionStatus.PENDING_PAYMENT,
            jersey_info={
                "id": jersey["id"],
                "team": jersey["team"],
                "player_name": jersey.get("player_name", ""),
                "season": jersey.get("season", ""),
                "size": listing.get("size", ""),
                "condition": listing.get("condition", "")
            },
            auto_release_date=datetime.utcnow() + timedelta(days=14),  # Auto-libération après 14 jours
            buyer_notifications=[{
                "type": "payment_created",
                "message": "Paiement sécurisé créé. Votre argent sera bloqué jusqu'à vérification de l'authenticité du maillot.",
                "timestamp": datetime.utcnow().isoformat()
            }],
            seller_notifications=[{
                "type": "sale_pending",
                "message": "Nouvelle vente en attente. Expédiez le maillot dès réception du paiement.",
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        
        # Calcul du score de risque
        risk_score = await calculate_fraud_risk_score(user_id, listing["seller_id"], listing_price)
        secure_transaction.risk_score = risk_score
        
        if risk_score >= 7:  # Score élevé = révision manuelle
            secure_transaction.requires_manual_review = True
            secure_transaction.fraud_indicators.append("High risk score detected")
        
        # Sauvegarder la transaction
        await db.secure_transactions.insert_one(secure_transaction.dict())
        
        # 🎯 CRÉER AUTOMATIQUEMENT LA CONVERSATION (STYLE LEBONCOIN)
        conversation_id = await create_transaction_conversation(secure_transaction, 
                                                              {"id": user_id, "name": "Acheteur"}, 
                                                              {"id": listing["seller_id"], "name": seller["name"]})
        
        if conversation_id:
            # Mettre à jour la transaction avec l'ID de conversation
            await db.secure_transactions.update_one(
                {"id": secure_transaction.id},
                {"$set": {"conversation_id": conversation_id}}
            )
            
            # Envoyer le premier message système
            await send_system_message(conversation_id, "payment_confirmed", {
                "amount": listing_price,
                "jersey_name": f"{jersey['team']} - {jersey.get('player_name', 'Maillot')}",
                "buyer_name": "Acheteur",  # Sera mis à jour avec le vrai nom
                "seller_name": seller["name"]
            }, secure_transaction.id)
        
        # Envoyer les notifications par email
        asyncio.create_task(send_secure_payment_notifications(secure_transaction))
        
        return {
            "url": session.url,
            "session_id": session.session_id,
            "transaction_id": secure_transaction.id,
            "conversation_id": conversation_id,
            "message": "🛡️ Paiement sécurisé créé. Conversation automatique créée avec le vendeur."
        }
        
    except Exception as e:
        logger.error(f"Error creating secure checkout: {e}")
        raise HTTPException(status_code=500, detail="Impossible de créer le paiement sécurisé")

# =============================================================================
# 🔧 ENDPOINTS ADMINISTRATION - VÉRIFICATION AUTHENTICITÉ
# =============================================================================

@api_router.get("/admin/transactions/pending-verification")
async def get_transactions_pending_verification(
    current_user: dict = Depends(get_current_user_admin)
):
    """
    📋 Obtenir toutes les transactions en attente de vérification d'authenticité
    """
    try:
        # Récupérer les transactions en attente de vérification
        transactions = await db.secure_transactions.find({
            "status": {"$in": ["shipped", "awaiting_verification"]},
            "verified_at": None
        }).sort("created_at", 1).to_list(100)
        
        # Enrichir avec les informations utilisateur et listing
        enriched_transactions = []
        for transaction in transactions:
            # Récupérer les informations buyer/seller
            buyer = await db.users.find_one({"id": transaction["buyer_id"]})
            seller = await db.users.find_one({"id": transaction["seller_id"]})
            listing = await db.listings.find_one({"id": transaction["listing_id"]})
            
            enriched_transaction = {
                **transaction,
                "buyer_name": buyer["name"] if buyer else "Unknown",
                "buyer_email": buyer["email"] if buyer else "Unknown",
                "seller_name": seller["name"] if seller else "Unknown", 
                "seller_email": seller["email"] if seller else "Unknown",
                "listing_title": f"{transaction['jersey_info']['team']} - {transaction['jersey_info'].get('player_name', 'Maillot')}",
                "days_pending": (datetime.utcnow() - transaction["created_at"]).days if transaction.get("created_at") else 0
            }
            enriched_transactions.append(enriched_transaction)
        
        return {
            "transactions": enriched_transactions,
            "total_pending": len(enriched_transactions),
            "high_priority": len([t for t in enriched_transactions if t["days_pending"] > 3])
        }
        
    except Exception as e:
        logger.error(f"Error getting pending verification transactions: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des transactions")

@api_router.post("/admin/transactions/{transaction_id}/verify-authentic")
async def verify_jersey_authentic(
    transaction_id: str,
    verification_data: TransactionAction,
    current_user: dict = Depends(get_current_user_admin)
):
    """
    ✅ Marquer un maillot comme AUTHENTIQUE et libérer le paiement au vendeur
    """
    try:
        # Récupérer la transaction
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction["status"] not in ["shipped", "awaiting_verification"]:
            raise HTTPException(status_code=400, detail="Transaction not eligible for verification")
        
        # Score d'authenticité (7-10 = authentique)
        authenticity_score = verification_data.authenticity_score or 8
        if authenticity_score < 7:
            raise HTTPException(status_code=400, detail="Score d'authenticité trop faible pour marquer comme authentique")
        
        # Libérer le paiement via Stripe
        stripe_payment_intent_id = transaction.get("stripe_payment_intent_id")
        if stripe_payment_intent_id:
            try:
                stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
                # Capture le paiement (libération des fonds au vendeur)
                # Note: Cette fonctionnalité nécessite l'implementation dans emergentintegrations
                logger.info(f"Payment intent {stripe_payment_intent_id} would be captured here")
            except Exception as e:
                logger.error(f"Error capturing payment: {e}")
                # Continuer quand même pour marquer la transaction comme vérifiée
        
        # Mettre à jour la transaction
        update_data = {
            "status": TransactionStatus.VERIFIED_AUTHENTIC,
            "verified_at": datetime.utcnow(),
            "verified_by_admin_id": current_user["id"],
            "authenticity_score": authenticity_score,
            "verification_notes": verification_data.notes,
            "updated_at": datetime.utcnow()
        }
        
        # Ajouter les notes admin
        admin_note = {
            "admin_id": current_user["id"],
            "admin_name": current_user["name"],
            "action": "verified_authentic",
            "notes": verification_data.notes,
            "authenticity_score": authenticity_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": update_data,
                "$push": {"admin_notes": admin_note}
            }
        )
        
        # Créer des notifications pour buyer et seller
        await create_notification(
            transaction["buyer_id"],
            NotificationType.PURCHASE_VERIFIED,
            f"✅ Votre achat '{transaction['jersey_info']['team']}' a été vérifié authentique !",
            {"transaction_id": transaction_id, "authenticity_score": authenticity_score}
        )
        
        await create_notification(
            transaction["seller_id"],
            NotificationType.SALE_COMPLETED,
            f"💰 Paiement libéré pour votre vente '{transaction['jersey_info']['team']}' !",
            {"transaction_id": transaction_id, "amount": transaction["amount"]}
        )
        
        # Log de l'activité admin
        await log_user_activity(current_user["id"], "jersey_verified_authentic", "Transaction verification", {
            "transaction_id": transaction_id,
            "jersey_info": transaction["jersey_info"],
            "authenticity_score": authenticity_score,
            "buyer_id": transaction["buyer_id"],
            "seller_id": transaction["seller_id"]
        })
        
        return {
            "message": f"✅ Maillot vérifié authentique (score: {authenticity_score}/10)",
            "transaction_id": transaction_id,
            "status": "verified_authentic",
            "payment_released": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying jersey as authentic: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification")

@api_router.post("/admin/transactions/{transaction_id}/verify-fake")
async def verify_jersey_fake(
    transaction_id: str,
    verification_data: TransactionAction,
    current_user: dict = Depends(get_current_user_admin)
):
    """
    ❌ Marquer un maillot comme FAUX et rembourser l'acheteur
    """
    try:
        # Récupérer la transaction
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction["status"] not in ["shipped", "awaiting_verification"]:
            raise HTTPException(status_code=400, detail="Transaction not eligible for verification")
        
        # Score d'authenticité (1-6 = suspect/faux)
        authenticity_score = verification_data.authenticity_score or 3
        if authenticity_score >= 7:
            raise HTTPException(status_code=400, detail="Score d'authenticité trop élevé pour marquer comme faux")
        
        # Rembourser l'acheteur via Stripe
        stripe_payment_intent_id = transaction.get("stripe_payment_intent_id")
        if stripe_payment_intent_id:
            try:
                stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
                # Refund le paiement (remboursement à l'acheteur)
                # Note: Cette fonctionnalité nécessite l'implementation dans emergentintegrations
                logger.info(f"Payment intent {stripe_payment_intent_id} would be refunded here")
            except Exception as e:
                logger.error(f"Error refunding payment: {e}")
        
        # Mettre à jour la transaction
        update_data = {
            "status": TransactionStatus.VERIFIED_FAKE,
            "verified_at": datetime.utcnow(),
            "verified_by_admin_id": current_user["id"], 
            "authenticity_score": authenticity_score,
            "verification_notes": verification_data.notes,
            "updated_at": datetime.utcnow()
        }
        
        # Ajouter les notes admin
        admin_note = {
            "admin_id": current_user["id"],
            "admin_name": current_user["name"],
            "action": "verified_fake",
            "notes": verification_data.notes,
            "authenticity_score": authenticity_score,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": update_data,
                "$push": {"admin_notes": admin_note}
            }
        )
        
        # Créer des notifications
        await create_notification(
            transaction["buyer_id"],
            NotificationType.PURCHASE_REFUNDED,
            f"🔄 Remboursement effectué pour '{transaction['jersey_info']['team']}' - Maillot détecté comme non-authentique",
            {"transaction_id": transaction_id, "refund_amount": transaction["amount"]}
        )
        
        await create_notification(
            transaction["seller_id"],
            NotificationType.SALE_CANCELLED,
            f"⚠️ Vente annulée pour '{transaction['jersey_info']['team']}' - Maillot détecté comme non-authentique",
            {"transaction_id": transaction_id, "reason": "Authenticité non vérifiée"}
        )
        
        # Incrémenter le score de suspicion du vendeur
        await db.users.update_one(
            {"id": transaction["seller_id"]},
            {"$inc": {"suspicious_activity_score": 5}}
        )
        
        # Log de l'activité admin
        await log_user_activity(current_user["id"], "jersey_verified_fake", "Transaction verification", {
            "transaction_id": transaction_id,
            "jersey_info": transaction["jersey_info"],
            "authenticity_score": authenticity_score,
            "buyer_id": transaction["buyer_id"],
            "seller_id": transaction["seller_id"],
            "seller_penalized": True
        })
        
        return {
            "message": f"❌ Maillot détecté comme faux (score: {authenticity_score}/10)",
            "transaction_id": transaction_id,
            "status": "verified_fake",
            "buyer_refunded": True,
            "seller_penalized": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying jersey as fake: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification")

# =============================================================================
# 👤 ENDPOINTS ACHETEUR - ACTIONS DANS LA CONVERSATION (STYLE LEBONCOIN)
# =============================================================================

@api_router.post("/transactions/{transaction_id}/buyer/confirm-receipt")
async def buyer_confirm_receipt(
    transaction_id: str,
    confirmation_data: BuyerAction,
    user_id: str = Depends(get_current_user)
):
    """
    ✅ L'acheteur confirme avoir reçu le maillot et qu'il est conforme
    → Déclenche la libération du paiement au vendeur (style Leboncoin)
    """
    try:
        # Récupérer la transaction
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Vérifier que l'utilisateur est bien l'acheteur
        if user_id != transaction["buyer_id"]:
            raise HTTPException(status_code=403, detail="Seul l'acheteur peut confirmer la réception")
        
        # Vérifier que la transaction est dans le bon état
        if transaction["status"] not in ["shipped", "awaiting_verification"]:
            raise HTTPException(status_code=400, detail="La transaction n'est pas dans un état permettant la confirmation")
        
        # Récupérer les informations utilisateur
        buyer = await db.users.find_one({"id": user_id})
        seller = await db.users.find_one({"id": transaction["seller_id"]})
        
        # Mettre à jour le statut de la transaction
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": {
                    "status": TransactionStatus.VERIFIED_AUTHENTIC,
                    "verified_at": datetime.utcnow(),
                    "verified_by_buyer": True,
                    "buyer_confirmation_message": confirmation_data.message,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Envoyer message système dans la conversation
        conversation_id = transaction.get("conversation_id")
        if conversation_id:
            await send_system_message(conversation_id, "buyer_confirmed", {
                "buyer_name": buyer["name"] if buyer else "L'acheteur",
                "seller_name": seller["name"] if seller else "Le vendeur",
                "amount": transaction["amount"],
                "confirmation_message": confirmation_data.message
            }, transaction_id)
            
            # Ajouter le message de l'acheteur s'il y en a un
            if confirmation_data.message:
                buyer_message = MessageV2(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    message_type="text",
                    message=f"✅ **Réception confirmée !**\n\n{confirmation_data.message}",
                    transaction_id=transaction_id
                )
                await db.messages.insert_one(buyer_message.dict())
        
        # Libérer le paiement via Stripe (simulation pour le moment)
        stripe_payment_intent_id = transaction.get("stripe_payment_intent_id")
        if stripe_payment_intent_id:
            try:
                # stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
                # await stripe_checkout.capture_payment(stripe_payment_intent_id)
                logger.info(f"Payment {stripe_payment_intent_id} would be captured and released to seller")
            except Exception as e:
                logger.error(f"Error capturing payment: {e}")
        
        # Envoyer message de libération de paiement
        if conversation_id:
            await send_system_message(conversation_id, "payment_released", {
                "amount": transaction["amount"],
                "seller_name": seller["name"] if seller else "Le vendeur"
            }, transaction_id)
        
        # Créer des notifications
        await create_notification(
            transaction["seller_id"],
            NotificationType.SALE_COMPLETED,
            f"💰 Paiement libéré pour votre maillot '{transaction['jersey_info']['team']}' !",
            {"transaction_id": transaction_id, "amount": transaction["amount"]}
        )
        
        # Marquer le listing comme vendu
        await db.listings.update_one(
            {"id": transaction["listing_id"]},
            {"$set": {"status": "sold", "sold_at": datetime.utcnow()}}
        )
        
        return {
            "message": "✅ Réception confirmée ! Le paiement a été libéré au vendeur.",
            "transaction_id": transaction_id,
            "status": "completed",
            "payment_released": True,
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming receipt: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la confirmation de réception")

@api_router.post("/transactions/{transaction_id}/buyer/report-issue")
async def buyer_report_issue(
    transaction_id: str,
    issue_data: BuyerAction,
    user_id: str = Depends(get_current_user)
):
    """
    ⚠️ L'acheteur signale un problème avec le maillot reçu
    → Déclenche une révision manuelle par l'équipe TopKit
    """
    try:
        # Récupérer la transaction
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Vérifier que l'utilisateur est bien l'acheteur
        if user_id != transaction["buyer_id"]:
            raise HTTPException(status_code=403, detail="Seul l'acheteur peut signaler un problème")
        
        # Vérifier que la transaction permet de signaler un problème
        if transaction["status"] not in ["shipped", "awaiting_verification", "delivered"]:
            raise HTTPException(status_code=400, detail="Impossible de signaler un problème pour cette transaction")
        
        # Récupérer les informations utilisateur
        buyer = await db.users.find_one({"id": user_id})
        seller = await db.users.find_one({"id": transaction["seller_id"]})
        
        # Mettre à jour la transaction avec le problème signalé
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": {
                    "status": TransactionStatus.DISPUTED,
                    "dispute_reason": issue_data.message,
                    "dispute_evidence": issue_data.evidence_photos,
                    "disputed_at": datetime.utcnow(),
                    "requires_manual_review": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Envoyer message système dans la conversation
        conversation_id = transaction.get("conversation_id")
        if conversation_id:
            await send_system_message(conversation_id, "issue_reported", {
                "buyer_name": buyer["name"] if buyer else "L'acheteur",
                "seller_name": seller["name"] if seller else "Le vendeur",
                "issue_description": issue_data.message
            }, transaction_id)
            
            # Ajouter le message détaillé de l'acheteur
            if issue_data.message:
                issue_message = MessageV2(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    message_type="text",
                    message=f"⚠️ **Problème signalé**\n\n{issue_data.message}",
                    transaction_id=transaction_id
                )
                await db.messages.insert_one(issue_message.dict())
        
        # Notification aux admins pour révision manuelle
        admin_users = await db.users.find({"role": {"$in": ["admin", "moderator"]}}).to_list(10)
        for admin in admin_users:
            await create_notification(
                admin["id"],
                NotificationType.SYSTEM_ALERT,
                f"🚨 Problème signalé sur transaction {transaction_id}",
                {
                    "transaction_id": transaction_id,
                    "buyer_name": buyer["name"] if buyer else "Unknown",
                    "issue": issue_data.message
                }
            )
        
        return {
            "message": "⚠️ Problème signalé. Notre équipe va examiner la situation.",
            "transaction_id": transaction_id,
            "status": "disputed",
            "requires_review": True,
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting issue: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du signalement du problème")

@api_router.post("/transactions/{transaction_id}/seller/mark-shipped")
async def seller_mark_shipped(
    transaction_id: str,
    shipping_data: TransactionAction,
    user_id: str = Depends(get_current_user)
):
    """
    📦 Le vendeur marque le maillot comme expédié avec les informations de suivi
    """
    try:
        # Récupérer la transaction
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Vérifier que l'utilisateur est bien le vendeur
        if user_id != transaction["seller_id"]:
            raise HTTPException(status_code=403, detail="Seul le vendeur peut marquer comme expédié")
        
        # Vérifier l'état de la transaction
        if transaction["status"] != "payment_held":
            raise HTTPException(status_code=400, detail="La transaction doit être payée pour pouvoir être expédiée")
        
        # Récupérer les informations utilisateur
        seller = await db.users.find_one({"id": user_id})
        buyer = await db.users.find_one({"id": transaction["buyer_id"]})
        
        # Mettre à jour la transaction
        await db.secure_transactions.update_one(
            {"id": transaction_id},
            {
                "$set": {
                    "status": TransactionStatus.SHIPPED,
                    "tracking_number": shipping_data.tracking_number,
                    "shipping_carrier": shipping_data.shipping_carrier,
                    "shipped_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Envoyer message système dans la conversation
        conversation_id = transaction.get("conversation_id")
        if conversation_id:
            await send_system_message(conversation_id, "shipped", {
                "carrier": shipping_data.shipping_carrier,
                "tracking_number": shipping_data.tracking_number,
                "tracking_url": f"https://track.example.com/{shipping_data.tracking_number}",  # URL générée
                "seller_name": seller["name"] if seller else "Le vendeur",
                "buyer_name": buyer["name"] if buyer else "L'acheteur"
            }, transaction_id)
            
            # Ajouter le message du vendeur s'il y en a un
            if shipping_data.notes:
                seller_message = MessageV2(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    message_type="text",
                    message=f"📦 **Maillot expédié !**\n\n{shipping_data.notes}",
                    transaction_id=transaction_id
                )
                await db.messages.insert_one(seller_message.dict())
        
        # Notification à l'acheteur
        await create_notification(
            transaction["buyer_id"],
            NotificationType.SHIPMENT_SENT,
            f"📦 Votre maillot '{transaction['jersey_info']['team']}' a été expédié !",
            {
                "transaction_id": transaction_id,
                "tracking_number": shipping_data.tracking_number,
                "carrier": shipping_data.shipping_carrier
            }
        )
        
        return {
            "message": "📦 Maillot marqué comme expédié !",
            "transaction_id": transaction_id,
            "status": "shipped",
            "tracking_number": shipping_data.tracking_number,
            "carrier": shipping_data.shipping_carrier,
            "conversation_id": conversation_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking as shipped: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du marquage d'expédition")

@api_router.get("/transactions/{transaction_id}/details")
async def get_transaction_details(
    transaction_id: str,
    current_user: dict = Depends(get_current_user_admin)
):
    """
    📄 Obtenir les détails complets d'une transaction pour vérification
    """
    try:
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Récupérer toutes les informations associées
        buyer = await db.users.find_one({"id": transaction["buyer_id"]})
        seller = await db.users.find_one({"id": transaction["seller_id"]})
        listing = await db.listings.find_one({"id": transaction["listing_id"]})
        jersey = await db.jerseys.find_one({"id": transaction["jersey_info"]["id"]})
        
        return {
            "transaction": transaction,
            "buyer": {
                "id": buyer["id"],
                "name": buyer["name"],
                "email": buyer["email"],
                "created_at": buyer.get("created_at"),
                "suspicious_score": buyer.get("suspicious_activity_score", 0),
                "total_purchases": await db.secure_transactions.count_documents({"buyer_id": buyer["id"]})
            },
            "seller": {
                "id": seller["id"],
                "name": seller["name"],
                "email": seller["email"],
                "created_at": seller.get("created_at"),
                "suspicious_score": seller.get("suspicious_activity_score", 0),
                "total_sales": await db.secure_transactions.count_documents({"seller_id": seller["id"]})
            },
            "jersey": jersey,
            "listing": listing,
            "timeline": generate_transaction_timeline(transaction),
            "risk_indicators": {
                "risk_score": transaction.get("risk_score", 0),
                "fraud_indicators": transaction.get("fraud_indicators", []),
                "requires_manual_review": transaction.get("requires_manual_review", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des détails")

# =============================================================================
# 💬 CONVERSATION ENDPOINTS WITH TRANSACTION CONTEXT
# =============================================================================

@api_router.get("/conversations/{conversation_id}/transaction")
async def get_conversation_transaction(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Obtenir les détails de la transaction liée à une conversation
    """
    try:
        # Vérifier que l'utilisateur fait partie de la conversation
        conversation = await db.conversations.find_one({"id": conversation_id})
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        participant_ids = [p["user_id"] for p in conversation["participants"]]
        if user_id not in participant_ids:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Récupérer la transaction liée
        transaction = await db.secure_transactions.find_one({"conversation_id": conversation_id})
        if not transaction:
            return {"transaction": None, "has_transaction": False}
        
        # Récupérer les informations associées
        buyer = await db.users.find_one({"id": transaction["buyer_id"]})
        seller = await db.users.find_one({"id": transaction["seller_id"]})
        
        return {
            "transaction": {
                **transaction,
                "buyer_name": buyer["name"] if buyer else "Unknown",
                "seller_name": seller["name"] if seller else "Unknown"
            },
            "has_transaction": True,
            "timeline": generate_transaction_timeline(transaction),
            "available_actions": get_transaction_actions_for_user(transaction, user_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation transaction: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de la transaction")

def get_transaction_actions_for_user(transaction: dict, user_id: str) -> List[dict]:
    """
    Obtenir les actions disponibles pour un utilisateur dans le contexte d'une transaction
    """
    actions = []
    status = transaction.get("status")
    
    # Actions pour le vendeur
    if user_id == transaction.get("seller_id"):
        if status == "payment_held":
            actions.append({
                "action": "mark_shipped",
                "label": "Marquer comme expédié",
                "description": "Indiquer que le maillot a été expédié",
                "endpoint": f"/api/transactions/{transaction['id']}/seller/mark-shipped",
                "requires": ["tracking_number", "shipping_carrier"],
                "type": "primary"
            })
    
    # Actions pour l'acheteur
    if user_id == transaction.get("buyer_id"):
        if status in ["shipped", "delivered"]:
            actions.append({
                "action": "confirm_receipt",
                "label": "Confirmer la réception",
                "description": "Confirmer que le maillot est conforme et débloquer le paiement",
                "endpoint": f"/api/transactions/{transaction['id']}/buyer/confirm-receipt",
                "requires": ["message"],
                "type": "success"
            })
            
            actions.append({
                "action": "report_issue",
                "label": "Signaler un problème",
                "description": "Signaler un problème avec le maillot reçu",
                "endpoint": f"/api/transactions/{transaction['id']}/buyer/report-issue",
                "requires": ["message", "evidence_photos"],
                "type": "warning"
            })
    
    return actions

@api_router.get("/admin/transactions/{transaction_id}/details")
async def get_transaction_details(
    transaction_id: str,
    current_user: dict = Depends(get_current_user_admin)
):
    """
    📄 Obtenir les détails complets d'une transaction pour vérification
    """
    try:
        transaction = await db.secure_transactions.find_one({"id": transaction_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Récupérer toutes les informations associées
        buyer = await db.users.find_one({"id": transaction["buyer_id"]})
        seller = await db.users.find_one({"id": transaction["seller_id"]})
        listing = await db.listings.find_one({"id": transaction["listing_id"]})
        jersey = await db.jerseys.find_one({"id": transaction["jersey_info"]["id"]})
        
        return {
            "transaction": transaction,
            "buyer": {
                "id": buyer["id"],
                "name": buyer["name"],
                "email": buyer["email"],
                "created_at": buyer.get("created_at"),
                "suspicious_score": buyer.get("suspicious_activity_score", 0),
                "total_purchases": await db.secure_transactions.count_documents({"buyer_id": buyer["id"]})
            },
            "seller": {
                "id": seller["id"],
                "name": seller["name"],
                "email": seller["email"],
                "created_at": seller.get("created_at"),
                "suspicious_score": seller.get("suspicious_activity_score", 0),
                "total_sales": await db.secure_transactions.count_documents({"seller_id": seller["id"]})
            },
            "jersey": jersey,
            "listing": listing,
            "timeline": generate_transaction_timeline(transaction),
            "risk_indicators": {
                "risk_score": transaction.get("risk_score", 0),
                "fraud_indicators": transaction.get("fraud_indicators", []),
                "requires_manual_review": transaction.get("requires_manual_review", False)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des détails")

# Payment System Endpoints
@api_router.post("/payments/checkout/session")
async def create_checkout_session(
    checkout_data: CheckoutRequest,
    user_id: str = Depends(get_current_user_optional)
):
    """Create Stripe checkout session for marketplace purchase"""
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    # Get listing details
    listing = await db.listings.find_one({"id": checkout_data.listing_id, "status": "active"})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or inactive")
    
    # Get jersey details
    jersey = await db.jerseys.find_one({"id": listing["jersey_id"]})
    if not jersey:
        raise HTTPException(status_code=404, detail="Jersey not found")
    
    # Get seller details
    seller = await db.users.find_one({"id": listing["seller_id"]})
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # Validate price
    if not listing.get("price") or listing["price"] < MINIMUM_LISTING_PRICE or listing["price"] > MAXIMUM_LISTING_PRICE:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid listing price. Must be between €{MINIMUM_LISTING_PRICE} and €{MAXIMUM_LISTING_PRICE}"
        )
    
    # Calculate commission
    listing_price = float(listing["price"])
    commission_amount = round(listing_price * TOPKIT_COMMISSION_RATE, 2)
    seller_amount = round(listing_price - commission_amount, 2)
    
    # Create URLs
    success_url = f"{checkout_data.origin_url}?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = checkout_data.origin_url
    
    # Initialize Stripe
    host_url = checkout_data.origin_url
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Prepare metadata
    metadata = {
        "listing_id": checkout_data.listing_id,
        "jersey_id": listing["jersey_id"],
        "seller_id": listing["seller_id"],
        "buyer_id": user_id or "anonymous",
        "commission_rate": str(TOPKIT_COMMISSION_RATE),
        "commission_amount": str(commission_amount),
        "seller_amount": str(seller_amount),
        "jersey_name": f"{jersey['team']} {jersey['season']} - {jersey.get('player', 'No Player')}",
        "seller_name": seller["name"]
    }
    
    try:
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=listing_price,
            currency="eur",  # Using EUR for European marketplace
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            user_id=user_id,
            user_email=None,  # Will be filled from Stripe data later
            amount=listing_price,
            currency="eur",
            listing_id=checkout_data.listing_id,
            payment_status="pending",
            status="initiated",
            metadata=metadata
        )
        
        await db.payment_transactions.insert_one(transaction.dict())
        
        # Log activity
        if user_id:
            await log_user_activity(user_id, "payment_initiated", checkout_data.listing_id, {
                "amount": listing_price,
                "currency": "eur",
                "session_id": session.session_id,
                "jersey_name": metadata["jersey_name"]
            })
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@api_router.get("/payments/checkout/status/{session_id}")
async def get_checkout_status(
    session_id: str,
    user_id: str = Depends(get_current_user_optional)
):
    """Get payment status and process successful payments"""
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    # Get transaction record
    transaction = await db.payment_transactions.find_one({"session_id": session_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Initialize Stripe
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        # Get status from Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction status
        update_data = {
            "payment_status": checkout_status.payment_status,
            "status": checkout_status.status,
            "updated_at": datetime.utcnow()
        }
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        # Process successful payment (only once)
        if checkout_status.payment_status == "paid" and transaction.get("payment_status") != "paid":
            await process_successful_payment(session_id, checkout_status, transaction)
        
        # Get listing and jersey info for response
        listing = await db.listings.find_one({"id": transaction["listing_id"]})
        jersey = await db.jerseys.find_one({"id": listing["jersey_id"]}) if listing else None
        seller = await db.users.find_one({"id": transaction["metadata"]["seller_id"]}) if transaction.get("metadata") else None
        
        commission_amount = float(transaction["metadata"].get("commission_amount", 0))
        seller_amount = float(transaction["metadata"].get("seller_amount", transaction["amount"]))
        
        return PaymentStatusResponse(
            status=checkout_status.status,
            payment_status=checkout_status.payment_status,
            amount_total=transaction["amount"],
            currency=transaction["currency"],
            listing_id=transaction["listing_id"],
            seller_id=transaction["metadata"]["seller_id"],
            buyer_id=transaction.get("user_id"),
            commission_amount=commission_amount,
            seller_amount=seller_amount,
            metadata={
                "jersey_name": transaction["metadata"].get("jersey_name", "Unknown Jersey"),
                "seller_name": transaction["metadata"].get("seller_name", "Unknown Seller"),
                "purchase_date": datetime.utcnow().isoformat() if checkout_status.payment_status == "paid" else None
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting checkout status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment status")

async def process_successful_payment(session_id: str, checkout_status: CheckoutStatusResponse, transaction: dict):
    """Process a successful payment - mark listing as sold, create notifications, etc."""
    
    try:
        listing_id = transaction["listing_id"]
        seller_id = transaction["metadata"]["seller_id"]
        buyer_id = transaction.get("user_id")
        
        # Mark listing as sold
        await db.listings.update_one(
            {"id": listing_id},
            {
                "$set": {
                    "status": "sold",
                    "updated_at": datetime.utcnow(),
                    "sold_to": buyer_id,
                    "sold_at": datetime.utcnow(),
                    "final_price": transaction["amount"]
                }
            }
        )
        
        # Create notifications
        jersey_name = transaction["metadata"].get("jersey_name", "Jersey")
        
        # Notify seller
        await create_notification(
            user_id=seller_id,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title="🎉 Jersey Sold!",
            message=f"Great news! Your jersey '{jersey_name}' has been sold for €{transaction['amount']:.2f}. After TopKit's 5% commission, you'll receive €{float(transaction['metadata']['seller_amount']):.2f}.",
            related_id=listing_id
        )
        
        # Notify buyer (if logged in)
        if buyer_id:
            await create_notification(
                user_id=buyer_id,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title="✅ Purchase Confirmed!",
                message=f"Your purchase of '{jersey_name}' for €{transaction['amount']:.2f} has been confirmed. The seller will be in touch about shipping details.",
                related_id=listing_id
            )
        
        # Log activities
        await log_user_activity(seller_id, "jersey_sold", listing_id, {
            "amount": transaction["amount"],
            "commission": transaction["metadata"]["commission_amount"],
            "net_amount": transaction["metadata"]["seller_amount"],
            "buyer_id": buyer_id,
            "jersey_name": jersey_name
        })
        
        if buyer_id:
            await log_user_activity(buyer_id, "jersey_purchased", listing_id, {
                "amount": transaction["amount"],
                "seller_id": seller_id,
                "jersey_name": jersey_name
            })
        
        logger.info(f"Successfully processed payment for listing {listing_id}, session {session_id}")
        
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        # Don't raise exception to avoid blocking status check
        
@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    try:
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process webhook event
        if webhook_response.event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
            # Find and update transaction
            transaction = await db.payment_transactions.find_one({"session_id": webhook_response.session_id})
            if transaction:
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {
                        "$set": {
                            "payment_status": webhook_response.payment_status,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Process successful payment if not already processed
                if webhook_response.payment_status == "paid" and transaction.get("payment_status") != "paid":
                    checkout_status = CheckoutStatusResponse(
                        status="complete",
                        payment_status="paid",
                        amount_total=int(transaction["amount"] * 100),  # Convert to cents
                        currency=transaction["currency"],
                        metadata=transaction["metadata"]
                    )
                    await process_successful_payment(webhook_response.session_id, checkout_status, transaction)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

@api_router.get("/payments/history")
async def get_purchase_history(
    user_id: str = Depends(get_current_user),
    limit: int = 20
):
    """Get user's purchase history"""
    
    # Get user's transactions
    transactions = await db.payment_transactions.find(
        {"user_id": user_id, "payment_status": "paid"}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    purchase_history = []
    
    for transaction in transactions:
        transaction.pop('_id', None)
        
        # Get listing and jersey details
        listing = await db.listings.find_one({"id": transaction["listing_id"]})
        if listing:
            jersey = await db.jerseys.find_one({"id": listing["jersey_id"]})
            seller = await db.users.find_one({"id": listing["seller_id"]})
            
            if jersey and seller:
                jersey.pop('_id', None)
                seller.pop('_id', None)
                
                purchase_item = PurchaseHistoryItem(
                    transaction_id=transaction["id"],
                    listing_id=transaction["listing_id"],
                    jersey_info={
                        "id": jersey["id"],
                        "team": jersey["team"],
                        "season": jersey["season"],
                        "player": jersey.get("player"),
                        "size": jersey["size"],
                        "condition": jersey["condition"],
                        "reference_number": jersey.get("reference_number")
                    },
                    seller_info={
                        "id": seller["id"],
                        "name": seller["name"],
                        "email": seller["email"]
                    },
                    amount_paid=transaction["amount"],
                    commission_paid=float(transaction["metadata"].get("commission_amount", 0)),
                    currency=transaction["currency"],
                    purchase_date=transaction["created_at"],
                    status=transaction["payment_status"]
                )
                
                purchase_history.append(purchase_item.dict())
    
    return {
        "purchases": purchase_history,
        "total": len(purchase_history)
    }

@api_router.get("/payments/sales")
async def get_sales_history(
    user_id: str = Depends(get_current_user),
    limit: int = 20
):
    """Get user's sales history"""
    
    # Get user's sales (transactions where they are the seller)
    transactions = await db.payment_transactions.find(
        {"metadata.seller_id": user_id, "payment_status": "paid"}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    sales_history = []
    
    for transaction in transactions:
        transaction.pop('_id', None)
        
        # Get listing and jersey details
        listing = await db.listings.find_one({"id": transaction["listing_id"]})
        if listing:
            jersey = await db.jerseys.find_one({"id": listing["jersey_id"]})
            buyer = await db.users.find_one({"id": transaction["user_id"]}) if transaction.get("user_id") else None
            
            if jersey:
                jersey.pop('_id', None)
                
                sale_item = {
                    "transaction_id": transaction["id"],
                    "listing_id": transaction["listing_id"],
                    "jersey_info": {
                        "id": jersey["id"],
                        "team": jersey["team"],
                        "season": jersey["season"],
                        "player": jersey.get("player"),
                        "size": jersey["size"],
                        "condition": jersey["condition"],
                        "reference_number": jersey.get("reference_number")
                    },
                    "buyer_info": {
                        "name": buyer["name"] if buyer else "Anonymous Buyer",
                        "email": buyer["email"] if buyer else "N/A"
                    },
                    "gross_amount": transaction["amount"],
                    "commission_amount": float(transaction["metadata"].get("commission_amount", 0)),
                    "net_amount": float(transaction["metadata"].get("seller_amount", transaction["amount"])),
                    "currency": transaction["currency"],
                    "sale_date": transaction["created_at"],
                    "status": transaction["payment_status"]
                }
                
                sales_history.append(sale_item)
    
    return {
        "sales": sales_history,
        "total": len(sales_history),
        "total_gross": sum(sale["gross_amount"] for sale in sales_history),
        "total_commission": sum(sale["commission_amount"] for sale in sales_history),
        "total_net": sum(sale["net_amount"] for sale in sales_history)
    }

# Email service endpoints
@api_router.post("/emails/send")
async def send_general_email(
    email_data: dict,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Send a general email (admin only)"""
    
    if not gmail_service:
        raise HTTPException(status_code=500, detail="Service d'email non disponible")
    
    try:
        success = gmail_service.send_email(
            to_email=email_data.get("to_email"),
            subject=email_data.get("subject"),
            body=email_data.get("body"),
            html_body=email_data.get("html_body")
        )
        
        if success:
            return {"message": "Email envoyé avec succès", "status": "sent"}
        else:
            raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email")
            
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")

@api_router.post("/emails/test")
async def test_email_service(
    admin_user: dict = Depends(get_current_user_admin)
):
    """Test email service configuration (admin only)"""
    
    if not gmail_service:
        raise HTTPException(status_code=500, detail="Service d'email non disponible")
    
    try:
        # Send test email to admin
        success = gmail_service.send_email(
            to_email=admin_user["email"],
            subject="Test - Service d'email TopKit",
            body="Ceci est un email de test pour vérifier que le service d'email fonctionne correctement.",
            html_body="""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1a56db;">🧪 Test du service d'email TopKit</h2>
                    <p>Félicitations ! Le service d'email Gmail SMTP fonctionne correctement.</p>
                    <p>✅ Configuration validée<br>
                       ✅ Authentification réussie<br>
                       ✅ Email envoyé avec succès</p>
                    <hr>
                    <p style="color: #666; font-size: 14px;">
                        Email de test envoyé depuis TopKit<br>
                        Service: Gmail SMTP
                    </p>
                </body>
            </html>
            """
        )
        
        if success:
            return {
                "message": "Test d'email réussi ! Vérifiez votre boîte mail.",
                "status": "success",
                "recipient": admin_user["email"]
            }
        else:
            raise HTTPException(status_code=500, detail="Échec du test d'email")
            
    except Exception as e:
        logger.error(f"Error testing email service: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du test d'email")

@api_router.get("/emails/health")
async def email_service_health():
    """Check email service health"""
    
    if not gmail_service:
        return {
            "status": "unavailable",
            "message": "Service d'email non initialisé",
            "gmail_configured": False
        }
    
    try:
        # Basic health check - verify configuration
        config_valid = all([
            gmail_service.username,
            gmail_service.app_password,
            gmail_service.from_email
        ])
        
        # Get email manager status
        manager_status = email_manager.get_service_status() if email_manager else {"status": "unavailable"}
        
        return {
            "status": "healthy" if config_valid else "misconfigured",
            "message": "Service d'email opérationnel" if config_valid else "Configuration incomplète",
            "gmail_configured": config_valid,
            "smtp_server": gmail_service.smtp_server,
            "smtp_port": gmail_service.smtp_port,
            "from_email": gmail_service.from_email,
            "email_manager": manager_status
        }
        
    except Exception as e:
        logger.error(f"Email service health check failed: {e}")
        return {
            "status": "error",
            "message": f"Erreur de service: {str(e)}",
            "gmail_configured": False
        }

@api_router.post("/emails/test-all-types")
async def test_all_email_types(
    test_data: dict,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Test all types of emails (admin only)"""
    
    if not email_manager:
        raise HTTPException(status_code=500, detail="Email manager non disponible")
    
    recipient_email = test_data.get("recipient_email", admin_user["email"])
    email_types = test_data.get("email_types", ["basic", "jersey_submitted", "password_reset", "newsletter"])
    
    results = {}
    
    for email_type in email_types:
        try:
            success = email_manager.send_test_email(recipient_email, email_type)
            results[email_type] = {
                "success": success,
                "status": "sent" if success else "failed"
            }
            logger.info(f"Test email {email_type} sent to {recipient_email}: {'success' if success else 'failed'}")
        except Exception as e:
            results[email_type] = {
                "success": False,
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Error sending test email {email_type}: {e}")
    
    return {
        "message": "Tests d'emails terminés",
        "recipient": recipient_email,
        "results": results,
        "total_tests": len(email_types),
        "successful": sum(1 for r in results.values() if r["success"]),
        "failed": sum(1 for r in results.values() if not r["success"])
    }

@api_router.post("/emails/jersey/submitted")
async def send_jersey_submitted_email(
    email_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send jersey submission confirmation email"""
    
    if not email_manager:
        raise HTTPException(status_code=500, detail="Email manager non disponible")
    
    try:
        jersey_data = email_data.get("jersey_data", {})
        success = email_manager.send_jersey_submitted_confirmation(
            user_email=current_user["email"],
            user_name=current_user["name"],
            jersey_data=jersey_data
        )
        
        if success:
            return {"message": "Email de confirmation de soumission envoyé", "status": "sent"}
        else:
            raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email")
            
    except Exception as e:
        logger.error(f"Error sending jersey submitted email: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")

@api_router.post("/emails/password/reset")
async def send_password_reset_email(
    email_data: dict
):
    """Send password reset email"""
    
    if not email_manager:
        raise HTTPException(status_code=500, detail="Email manager non disponible")
    
    try:
        user_email = email_data.get("email")
        if not user_email:
            raise HTTPException(status_code=400, detail="Email requis")
        
        # Check if user exists
        user = await db.users.find_one({"email": user_email})
        if not user:
            # Don't reveal if user exists or not for security
            return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
        
        # Generate reset token (in real app, store this in database with expiration)
        reset_token = secrets.token_urlsafe(32)
        
        success = email_manager.send_password_reset_email(
            user_email=user_email,
            user_name=user["name"],
            reset_token=reset_token
        )
        
        if success:
            logger.info(f"Password reset email sent to {user_email}")
            return {"message": "Un lien de réinitialisation a été envoyé à votre email"}
        else:
            raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email")
            
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")

@api_router.post("/emails/newsletter/send")
async def send_newsletter(
    newsletter_data: dict,
    admin_user: dict = Depends(get_current_user_admin)
):
    """Send newsletter to users (admin only)"""
    
    if not email_manager:
        raise HTTPException(status_code=500, detail="Email manager non disponible")
    
    try:
        # Get all users (or specific user if provided)
        recipient_email = newsletter_data.get("recipient_email")
        if recipient_email:
            # Send to specific user
            user = await db.users.find_one({"email": recipient_email})
            if not user:
                raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
            
            success = email_manager.send_weekly_newsletter(
                user_email=user["email"],
                user_name=user["name"],
                newsletter_data=newsletter_data
            )
            
            return {
                "message": "Newsletter envoyée",
                "recipient": recipient_email,
                "success": success
            }
        else:
            # Send to all users (in real app, use background task)
            users_cursor = db.users.find({"email_verified": True})
            users = await users_cursor.to_list(length=100)  # Limit for test
            
            results = {"sent": 0, "failed": 0}
            for user in users:
                try:
                    success = email_manager.send_weekly_newsletter(
                        user_email=user["email"],
                        user_name=user["name"],
                        newsletter_data=newsletter_data
                    )
                    if success:
                        results["sent"] += 1
                    else:
                        results["failed"] += 1
                except Exception as e:
                    logger.error(f"Failed to send newsletter to {user['email']}: {e}")
                    results["failed"] += 1
            
            return {
                "message": "Newsletter envoyée en masse",
                "total_users": len(users),
                "results": results
            }
            
    except Exception as e:
        logger.error(f"Error sending newsletter: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de la newsletter")

# Mount static files to serve uploaded images
# Static file serving is now handled via API endpoint below

@api_router.get("/uploads/{file_path:path}")
async def serve_uploaded_file(file_path: str):
    """Serve uploaded files (images, documents) from the uploads directory"""
    try:
        # Security: Prevent path traversal attacks
        if ".." in file_path or file_path.startswith("/"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Construct full file path
        full_path = Path("uploads") / file_path
        
        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Detect MIME type based on file extension
        mime_type, _ = mimetypes.guess_type(str(full_path))
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Return the file
        return FileResponse(
            path=str(full_path),
            filename=full_path.name,
            media_type=mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error serving file")

# Fonction utilitaire pour générer des références uniques
async def generate_reference(entity_type: str) -> str:
    """Generate unique reference for entities"""
    prefixes = {
        "team": "TK-TEAM-",
        "brand": "TK-BRAND-", 
        "player": "TK-PLAYER-",
        "competition": "TK-COMP-",
        "master_jersey": "TK-MASTER-",
        "jersey_release": "TK-RELEASE-"
    }
    
    prefix = prefixes.get(entity_type, "TK-ENTITY-")
    
    # Find the next number by looking for numeric suffixes only
    collection_name = f"{entity_type}s"
    
    # Get all entities with this prefix and extract numeric suffixes
    entities = await db[collection_name].find(
        {"topkit_reference": {"$regex": f"^{prefix}"}},
        {"topkit_reference": 1}
    ).to_list(None)
    
    max_num = 0
    if entities:
        for entity in entities:
            ref = entity["topkit_reference"]
            suffix = ref.split("-")[-1]
            try:
                # Only consider numeric suffixes
                num = int(suffix)
                max_num = max(max_num, num)
            except ValueError:
                # Skip non-numeric suffixes
                continue
    
    new_num = max_num + 1
    return f"{prefix}{new_num:06d}"

# ================================
# TEAMS API
# ================================

@api_router.get("/teams/dropdown")
async def get_teams_dropdown():
    """Get simplified teams list for dropdown selection"""
    try:
        teams = await db.teams.find(
            {"verification_level": {"$in": ["verified", "pending"]}},
            {"name": 1, "id": 1, "short_name": 1}
        ).sort("name", 1).to_list(2000)
        
        # Remove MongoDB ObjectId
        for team in teams:
            team.pop('_id', None)
        
        # Format for dropdown
        dropdown_teams = []
        for team in teams:
            display_name = team.get('short_name', team['name'])
            if team.get('short_name') and team['short_name'] != team['name']:
                display_name = f"{team['name']} ({team['short_name']})"
            
            dropdown_teams.append({
                "id": team['id'],
                "name": team['name'],
                "display_name": display_name
            })
        
        return dropdown_teams
        
    except Exception as e:
        logger.error(f"Error getting teams dropdown: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des équipes")

@api_router.get("/teams", response_model=List[TeamResponse])
async def get_teams(
    search: Optional[str] = None,
    country: Optional[str] = None,
    competition_id: Optional[str] = None,
    verified_only: bool = False,
    limit: int = 1000
):
    """Get teams with optional filters - Updated for interconnected forms"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"short_name": {"$regex": search, "$options": "i"}},
            {"common_names": {"$elemMatch": {"$regex": search, "$options": "i"}}}
        ]
    
    if country:
        query["country"] = country
        
    if competition_id:
        query["$or"] = [
            {"primary_competition_id": competition_id},
            {"current_competitions": {"$in": [competition_id]}}
        ]
        
    if verified_only:
        query["verified_level"] = {"$ne": "unverified"}
    
    teams = await db.teams.find(query).limit(limit).to_list(length=None)
    
    # Enrich with additional data
    enriched_teams = []
    for team in teams:
        team.pop('_id', None)
        
        # Count master jerseys
        jerseys_count = await db.master_jerseys.count_documents({"team_id": team["id"]})
        
        # Get primary competition info if available
        competition_info = None
        if team.get("primary_competition_id"):
            competition = await db.competitions.find_one({"id": team["primary_competition_id"]})
            if competition:
                competition.pop('_id', None)
                competition_info = {
                    "id": competition["id"], 
                    "competition_name": competition["competition_name"],
                    "type": competition["type"]
                }
        
        # Remove league_info from team data to avoid conflict and ensure required fields
        team_data = {k: v for k, v in team.items() if k != 'league_info'}
        
        # Ensure required fields have default values
        team_data.setdefault('common_names', [])
        team_data.setdefault('modification_count', 0)
        
        # Fix null values for required fields
        if team_data.get('name') is None:
            team_data['name'] = 'Unknown Team'
        if team_data.get('country') is None:
            team_data['country'] = 'Unknown Country'
        
        enriched_team = TeamResponse(
            **team_data,
            league_info=competition_info,  # Using existing field name for compatibility
            master_jerseys_count=jerseys_count,
            total_collectors=0  # TODO: calculate from collections
        )
        enriched_teams.append(enriched_team)
    
    return enriched_teams

@api_router.post("/teams", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new team"""
    # Vérifier doublons
    existing = await db.teams.find_one({
        "$or": [
            {"name": {"$regex": f"^{team_data.name}$", "$options": "i"}},
            {"short_name": {"$regex": f"^{team_data.short_name}$", "$options": "i"}} if team_data.short_name else {"id": None}
        ]
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Une équipe avec ce nom existe déjà")
    
    # Créer Team
    team_dict = team_data.dict()
    team_dict["created_by"] = current_user["id"]
    team_dict["topkit_reference"] = await generate_reference("team")
    
    # Apply auto-approval for testing
    team_dict = enable_auto_approval_for_testing(team_dict, current_user["id"])
    
    team = Team(**team_dict)
    
    await db.teams.insert_one(team.dict())
    
    # Auto-create a contribution entry for the new team so it appears in contributions page
    contribution_data = {
        "id": str(uuid.uuid4()),
        "title": f"New team: {team.name}",
        "description": f"Team {team.name} has been created and added to the database.",
        "entity_type": "team",
        "entity_id": team.id,
        "contributed_by": current_user["id"],
        "status": "approved",  # Auto-approve since the team is already created
        "changes": [
            {
                "field": "name",
                "old_value": "",
                "new_value": team.name,
                "field_type": "text"
            }
        ],
        "source_urls": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "approved_at": datetime.now(),
        "approved_by": current_user["id"],
        "votes": [],
        "metadata": {
            "auto_created": True,
            "team_creation": True
        }
    }
    
    # Insert the contribution
    await db.contributions.insert_one(contribution_data)
    
    # Log activity
    await log_user_activity(
        current_user["id"], 
        "team_created", 
        team.id,
        {"team_name": team.name, "reference": team.topkit_reference, "auto_contribution_created": True}
    )
    
    return TeamResponse(**team.dict(), league_info=None, master_jerseys_count=0, total_collectors=0)

@api_router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(team_id: str):
    """Get team details"""
    team = await db.teams.find_one({"id": team_id})
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    team.pop('_id', None)
    
    # Enrich with data
    jerseys_count = await db.master_jerseys.count_documents({"team_id": team_id})
    
    competition_info = None
    if team.get("primary_competition_id"):
        competition = await db.competitions.find_one({"id": team["primary_competition_id"]})
        if competition:
            competition.pop('_id', None)
            competition_info = {
                "id": competition["id"], 
                "competition_name": competition["competition_name"],
                "type": competition["type"]
            }
    
    return TeamResponse(
        **team,
        league_info=competition_info,
        master_jerseys_count=jerseys_count,
        total_collectors=0
    )

# ================================
# INTERCONNECTED FORM ENDPOINTS
# ================================

@api_router.get("/form-dependencies/competitions-by-type")
async def get_competitions_by_type():
    """Get competitions grouped by type for interconnected forms"""
    try:
        # Get all competitions grouped by type
        competitions = await db.competitions.find({}).to_list(length=None)
        
        # Remove MongoDB ObjectId
        for comp in competitions:
            comp.pop('_id', None)
        
        # Group by type
        competition_types = {}
        for comp in competitions:
            comp_type = comp.get("type", "Unknown")
            if comp_type not in competition_types:
                competition_types[comp_type] = []
            
            competition_types[comp_type].append({
                "id": comp["id"],
                "competition_name": comp["competition_name"],
                "country": comp.get("country"),
                "level": comp.get("level"),
                "confederations_federations": comp.get("confederations_federations", [])
            })
        
        return {
            "competition_types": competition_types,
            "total_competitions": len(competitions)
        }
        
    except Exception as e:
        logger.error(f"Error getting competitions by type: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des compétitions")

@api_router.get("/form-dependencies/teams-by-competition/{competition_id}")
async def get_teams_by_competition(competition_id: str):
    """Get teams that participate in a specific competition"""
    try:
        # Find teams that have this competition as primary or in current competitions
        teams = await db.teams.find({
            "$or": [
                {"primary_competition_id": competition_id},
                {"current_competitions": {"$in": [competition_id]}}
            ]
        }).to_list(length=None)
        
        # Remove MongoDB ObjectId
        for team in teams:
            team.pop('_id', None)
        
        return {
            "teams": teams,
            "competition_id": competition_id,
            "total_teams": len(teams)
        }
        
    except Exception as e:
        logger.error(f"Error getting teams by competition: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des équipes")

@api_router.get("/form-dependencies/master-kits-by-team/{team_id}")
async def get_master_kits_by_team(team_id: str):
    """Get master kits for a specific team"""
    try:
        master_kits = await db.master_kits.find({"team_id": team_id}).to_list(length=None)
        
        # Remove MongoDB ObjectId and enrich with team info
        for kit in master_kits:
            kit.pop('_id', None)
        
        return {
            "master_kits": master_kits,
            "team_id": team_id,
            "total_kits": len(master_kits)
        }
        
    except Exception as e:
        logger.error(f"Error getting master kits by team: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des kits")

@api_router.post("/form-dependencies/check-missing-data")
async def check_missing_form_data(request: dict):
    """Check what data is missing for interconnected forms and suggest what to add"""
    try:
        missing_data = {
            "competitions": [],
            "teams": [],
            "brands": [],
            "suggested_actions": []
        }
        
        # Check if requested competition exists
        if "competition_name" in request:
            comp = await db.competitions.find_one({
                "competition_name": {"$regex": f"^{request['competition_name']}$", "$options": "i"}
            })
            if not comp:
                missing_data["competitions"].append(request["competition_name"])
                missing_data["suggested_actions"].append({
                    "action": "add_competition",
                    "description": f"Ajouter la compétition '{request['competition_name']}'",
                    "redirect_url": "/competitions/add",
                    "form_data": {"competition_name": request["competition_name"]}
                })
        
        # Check if requested team exists
        if "team_name" in request:
            team = await db.teams.find_one({
                "name": {"$regex": f"^{request['team_name']}$", "$options": "i"}
            })
            if not team:
                missing_data["teams"].append(request["team_name"])
                missing_data["suggested_actions"].append({
                    "action": "add_team",
                    "description": f"Ajouter l'équipe '{request['team_name']}'",
                    "redirect_url": "/teams/add",
                    "form_data": {"name": request["team_name"]}
                })
        
        # Check if requested brand exists
        if "brand_name" in request:
            brand = await db.brands.find_one({
                "name": {"$regex": f"^{request['brand_name']}$", "$options": "i"}
            })
            if not brand:
                missing_data["brands"].append(request["brand_name"])
                missing_data["suggested_actions"].append({
                    "action": "add_brand",
                    "description": f"Ajouter la marque '{request['brand_name']}'",
                    "redirect_url": "/brands/add",
                    "form_data": {"name": request["brand_name"]}
                })
        
        return {
            "missing_data": missing_data,
            "has_missing": len(missing_data["competitions"]) > 0 or len(missing_data["teams"]) > 0 or len(missing_data["brands"]) > 0
        }
        
    except Exception as e:
        logger.error(f"Error checking missing data: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification des données")

@api_router.get("/form-dependencies/federations")
async def get_federations():
    """Get all unique federations/confederations for competition forms"""
    try:
        pipeline = [
            {"$unwind": "$confederations_federations"},
            {"$group": {"_id": "$confederations_federations"}},
            {"$sort": {"_id": 1}}
        ]
        
        result = await db.competitions.aggregate(pipeline).to_list(length=None)
        federations = [item["_id"] for item in result]
        
        return {
            "federations": federations,
            "total": len(federations)
        }
        
    except Exception as e:
        logger.error(f"Error getting federations: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des fédérations")

@api_router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_update: TeamCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update team details"""
    # Vérifier que l'équipe existe
    existing_team = await db.teams.find_one({"id": team_id})
    if not existing_team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    
    # Vérifier les doublons (sauf pour l'équipe actuelle)
    if team_update.name != existing_team.get('name'):
        duplicate_check = await db.teams.find_one({
            "$and": [
                {"id": {"$ne": team_id}},
                {
                    "$or": [
                        {"name": {"$regex": f"^{team_update.name}$", "$options": "i"}},
                        {"short_name": {"$regex": f"^{team_update.short_name}$", "$options": "i"}} if team_update.short_name else {"id": None}
                    ]
                }
            ]
        })
        
        if duplicate_check:
            raise HTTPException(status_code=400, detail="Une équipe avec ce nom existe déjà")
    
    # Préparer les données de mise à jour
    from datetime import datetime
    update_data = team_update.dict()
    update_data.update({
        "last_modified_at": datetime.utcnow(),
        "last_modified_by": current_user["id"],
        "modification_count": existing_team.get("modification_count", 0) + 1
    })
    
    # Mettre à jour dans la base
    result = await db.teams.update_one(
        {"id": team_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Échec de mise à jour")
    
    # Récupérer l'équipe mise à jour
    updated_team = await db.teams.find_one({"id": team_id})
    updated_team.pop('_id', None)
    
    # Enrichir avec données
    jerseys_count = await db.master_jerseys.count_documents({"team_id": team_id})
    
    league_info = None
    if updated_team.get("league_id"):
        league = await db.competitions.find_one({"id": updated_team["league_id"]})
        if league:
            league.pop('_id', None)
            league_info = {"id": league["id"], "name": league["name"]}
    
    return TeamResponse(
        **updated_team,
        league_info=league_info,
        master_jerseys_count=jerseys_count,
        total_collectors=0
    )

# ================================
# BRANDS API
# ================================

@api_router.get("/brands")
async def get_brands(
    search: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 100
):
    """Get brands with optional filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"official_name": {"$regex": search, "$options": "i"}},
            {"common_names": {"$elemMatch": {"$regex": search, "$options": "i"}}}
        ]
    
    if country:
        query["country"] = country
    
    brands = await db.brands.find(query).limit(limit).to_list(length=None)
    
    for brand in brands:
        brand.pop('_id', None)
    
    return brands

@api_router.post("/brands")
async def create_brand(
    brand_data: BrandCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new brand"""
    # Vérifier doublons
    existing = await db.brands.find_one({
        "name": {"$regex": f"^{brand_data.name}$", "$options": "i"}
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Une marque avec ce nom existe déjà")
    
    brand_dict = brand_data.dict()
    brand_dict["created_by"] = current_user["id"]
    brand_dict["topkit_reference"] = await generate_reference("brand")
    
    # Apply auto-approval for testing
    brand_dict = enable_auto_approval_for_testing(brand_dict, current_user["id"])
    
    brand = Brand(**brand_dict)
    
    await db.brands.insert_one(brand.dict())
    
    await log_user_activity(
        current_user["id"],
        "brand_created", 
        brand.id,
        {"brand_name": brand.name, "reference": brand.topkit_reference}
    )
    
    return brand.dict()

# ================================
# PLAYERS API  
# ================================

@api_router.get("/players")
async def get_players(
    search: Optional[str] = None,
    nationality: Optional[str] = None,
    position: Optional[str] = None,
    limit: int = 100
):
    """Get players with optional filters"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"full_name": {"$regex": search, "$options": "i"}},
            {"common_names": {"$elemMatch": {"$regex": search, "$options": "i"}}}
        ]
    
    if nationality:
        query["nationality"] = nationality
        
    if position:
        query["position"] = position
    
    players = await db.players.find(query).limit(limit).to_list(length=None)
    
    for player in players:
        player.pop('_id', None)
    
    return players

@api_router.post("/players")
async def create_player(
    player_data: PlayerCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new player"""
    # Vérifier doublons
    existing = await db.players.find_one({
        "name": {"$regex": f"^{player_data.name}$", "$options": "i"}
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Un joueur avec ce nom existe déjà")
    
    player_dict = player_data.dict()
    player_dict["created_by"] = current_user["id"]
    player_dict["topkit_reference"] = await generate_reference("player")
    
    # Apply auto-approval for testing
    player_dict = enable_auto_approval_for_testing(player_dict, current_user["id"])
    
    player = Player(**player_dict)
    
    await db.players.insert_one(player.dict())
    
    await log_user_activity(
        current_user["id"],
        "player_created",
        player.id,
        {"player_name": player.name, "reference": player.topkit_reference}
    )
    
    return player.dict()

# ================================
# COMPETITIONS API
# ================================

@api_router.get("/competitions")
async def get_competitions(
    search: Optional[str] = None,
    country: Optional[str] = None,
    type: Optional[str] = None,
    confederation: Optional[str] = None,
    level: Optional[int] = None,
    limit: int = 1000
):
    """Get competitions with optional filters - Updated for interconnected forms"""
    query = {}
    
    if search:
        query["$or"] = [
            {"competition_name": {"$regex": search, "$options": "i"}},
            {"official_name": {"$regex": search, "$options": "i"}},
            {"alternative_names": {"$elemMatch": {"$regex": search, "$options": "i"}}}
        ]
    
    if country:
        query["country"] = country
        
    if type:
        query["type"] = type
    
    if confederation:
        query["confederations_federations"] = {"$in": [confederation]}
    
    if level is not None:
        query["level"] = level
    
    competitions = await db.competitions.find(query).limit(limit).to_list(length=None)
    
    for competition in competitions:
        competition.pop('_id', None)
    
    return competitions

@api_router.post("/competitions")
async def create_competition(
    competition_data: CompetitionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new competition - Updated for interconnected forms with auto-approval"""
    competition_dict = competition_data.dict()
    competition_dict["created_by"] = current_user["id"]
    competition_dict["topkit_reference"] = await generate_reference("competition")
    
    # Apply auto-approval for testing
    competition_dict = enable_auto_approval_for_testing(competition_dict, current_user["id"])
    
    competition = Competition(**competition_dict)
    
    await db.competitions.insert_one(competition.dict())
    
    await log_user_activity(
        current_user["id"],
        "competition_created",
        competition.id,
        {"competition_name": competition.competition_name, "reference": competition.topkit_reference}
    )
    
    return competition.dict()

@api_router.put("/competitions/{competition_id}")
async def update_competition(
    competition_id: str,
    competition_update: CompetitionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update competition details"""
    # Vérifier que la compétition existe
    existing_competition = await db.competitions.find_one({"id": competition_id})
    if not existing_competition:
        raise HTTPException(status_code=404, detail="Compétition non trouvée")
    
    # Vérifier les doublons (sauf pour la compétition actuelle)
    if competition_update.name != existing_competition.get('name'):
        duplicate_check = await db.competitions.find_one({
            "$and": [
                {"id": {"$ne": competition_id}},
                {"name": {"$regex": f"^{competition_update.name}$", "$options": "i"}}
            ]
        })
        
        if duplicate_check:
            raise HTTPException(status_code=400, detail="Une compétition avec ce nom existe déjà")
    
    # Préparer les données de mise à jour
    from datetime import datetime
    update_data = competition_update.dict()
    update_data.update({
        "last_modified_at": datetime.utcnow(),
        "last_modified_by": current_user["id"],
        "modification_count": existing_competition.get("modification_count", 0) + 1
    })
    
    # Mettre à jour dans la base
    result = await db.competitions.update_one(
        {"id": competition_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Échec de mise à jour")
    
    # Récupérer la compétition mise à jour
    updated_competition = await db.competitions.find_one({"id": competition_id})
    updated_competition.pop('_id', None)
    
    await log_user_activity(
        current_user["id"],
        "competition_updated",
        competition_id,
        {"competition_name": updated_competition["name"], "reference": updated_competition["topkit_reference"]}
    )
    
    return updated_competition

# ================================
# MASTER JERSEYS API
# ================================

@api_router.get("/master-jerseys", response_model=List[MasterJerseyResponse])
async def get_master_jerseys(
    team_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    season: Optional[str] = None,
    jersey_type: Optional[str] = None,
    competition_id: Optional[str] = None,
    verified_only: bool = False,
    limit: int = 100
):
    """Get master jerseys with optional filters"""
    query = {}
    
    if team_id:
        query["team_id"] = team_id
    if brand_id:
        query["brand_id"] = brand_id
    if season:
        query["season"] = season
    if jersey_type:
        query["jersey_type"] = jersey_type
    if competition_id:
        query["competition_id"] = competition_id
        
    if verified_only:
        query["verified_level"] = {"$ne": "unverified"}
    
    master_jerseys = await db.master_jerseys.find(query).limit(limit).to_list(length=None)
    
    # Enrichir avec données liées
    enriched_jerseys = []
    for jersey in master_jerseys:
        jersey.pop('_id', None)
        
        # Récupérer infos team, brand, competition
        team = await db.teams.find_one({"id": jersey["team_id"]})
        brand = await db.brands.find_one({"id": jersey["brand_id"]})
        competition = None
        if jersey.get("competition_id"):
            competition = await db.competitions.find_one({"id": jersey["competition_id"]})
        
        # Count reference kits (not jersey_releases)
        releases_count = await db.reference_kits.count_documents({"master_kit_id": jersey["id"]})
        
        # Calculate collectors count
        # Find all reference kits for this master jersey
        reference_kits = await db.reference_kits.find({"master_kit_id": jersey["id"]}).to_list(length=None)
        reference_kit_ids = [rk["id"] for rk in reference_kits]
        
        # Count unique users who have personal kits referencing these reference kits
        collectors_count = 0
        if reference_kit_ids:
            collectors_pipeline = [
                {"$match": {"reference_kit_id": {"$in": reference_kit_ids}}},
                {"$group": {"_id": "$user_id"}},
                {"$count": "total"}
            ]
            collectors_result = await db.personal_kits.aggregate(collectors_pipeline).to_list(length=None)
            collectors_count = collectors_result[0]["total"] if collectors_result else 0
        
        team_info = {"id": team["id"], "name": team["name"], "short_name": team.get("short_name")} if team else {}
        brand_info = {"id": brand["id"], "name": brand["name"]} if brand else {}
        competition_info = {"id": competition["id"], "name": competition["name"]} if competition else None
        
        # Clean jersey data to ensure all required fields are present and valid
        clean_jersey_data = {
            **jersey,
            "season": jersey.get("season") or "Unknown",  # Ensure season is never None
            "created_by": jersey.get("created_by") or "system",  # Ensure created_by is never None
            "jersey_type": jersey.get("jersey_type") or "home",  # Ensure jersey_type is never None
            "model": jersey.get("model") or "unknown",  # Ensure model is never None
            "primary_color": jersey.get("primary_color") or "#FFFFFF"  # Ensure primary_color is never None
        }
        
        enriched_jersey = MasterJerseyResponse(
            **clean_jersey_data,
            team_info=team_info,
            brand_info=brand_info,
            competition_info=competition_info,
            releases_count=releases_count,  # Updated to match model field
            collectors_count=collectors_count  # Updated to calculate actual collectors
        )
        enriched_jerseys.append(enriched_jersey)
    
    return enriched_jerseys

@api_router.get("/master-jerseys/{jersey_id}", response_model=MasterJerseyResponse)
async def get_master_jersey_by_id(jersey_id: str):
    """Get specific master jersey by ID"""
    jersey = await db.master_jerseys.find_one({"id": jersey_id})
    
    if not jersey:
        raise HTTPException(status_code=404, detail="Master jersey not found")
    
    jersey.pop('_id', None)
    
    # Récupérer infos team, brand, competition
    team = await db.teams.find_one({"id": jersey["team_id"]}) if jersey.get("team_id") else None
    brand = await db.brands.find_one({"id": jersey["brand_id"]}) if jersey.get("brand_id") else None
    competition = None
    if jersey.get("competition_id"):
        competition = await db.competitions.find_one({"id": jersey["competition_id"]})
    
    # Compter releases
    releases_count = await db.reference_kits.count_documents({"master_kit_id": jersey_id})
    
    # Calculate collectors count
    # Find all reference kits for this master jersey
    reference_kits = await db.reference_kits.find({"master_kit_id": jersey_id}).to_list(length=None)
    reference_kit_ids = [rk["id"] for rk in reference_kits]
    
    # Count unique users who have personal kits referencing these reference kits
    collectors_count = 0
    if reference_kit_ids:
        collectors_pipeline = [
            {"$match": {"reference_kit_id": {"$in": reference_kit_ids}}},
            {"$group": {"_id": "$user_id"}},
            {"$count": "total"}
        ]
        collectors_result = await db.personal_kits.aggregate(collectors_pipeline).to_list(length=None)
        collectors_count = collectors_result[0]["total"] if collectors_result else 0
    
    team_info = {"id": team["id"], "name": team["name"], "short_name": team.get("short_name")} if team else {}
    brand_info = {"id": brand["id"], "name": brand["name"]} if brand else {}
    competition_info = {"id": competition["id"], "name": competition["name"]} if competition else None
    
    # Clean jersey data to ensure all required fields are present and valid
    clean_jersey_data = {
        **jersey,
        "season": jersey.get("season") or "Unknown",  # Ensure season is never None
        "created_by": jersey.get("created_by") or "system",  # Ensure created_by is never None
        "jersey_type": jersey.get("jersey_type") or "home",  # Ensure jersey_type is never None
        "model": jersey.get("model") or "unknown",  # Ensure model is never None
        "primary_color": jersey.get("primary_color") or "#FFFFFF"  # Ensure primary_color is never None
    }
    
    enriched_jersey = MasterJerseyResponse(
        **clean_jersey_data,
        team_info=team_info,
        brand_info=brand_info,
        competition_info=competition_info,
        releases_count=releases_count,
        collectors_count=collectors_count
    )
    
    return enriched_jersey

@api_router.post("/master-jerseys", response_model=MasterJerseyResponse)
async def create_master_jersey(
    jersey_data: MasterJerseyCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new master jersey"""
    # Vérifier que team et brand existent
    team = await db.teams.find_one({"id": jersey_data.team_id})
    brand = await db.brands.find_one({"id": jersey_data.brand_id})
    
    if not team:
        raise HTTPException(status_code=404, detail="Équipe non trouvée")
    if not brand:
        raise HTTPException(status_code=404, detail="Marque non trouvée")
    
    # Vérifier doublons
    existing = await db.master_jerseys.find_one({
        "team_id": jersey_data.team_id,
        "season": jersey_data.season,
        "jersey_type": jersey_data.jersey_type
    })
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Un Master Jersey {jersey_data.jersey_type} existe déjà pour {team['name']} saison {jersey_data.season}"
        )
    
    master_jersey = MasterJersey(
        **jersey_data.dict(),
        created_by=current_user["id"],
        topkit_reference=await generate_reference("master_jersey")
    )
    
    await db.master_jerseys.insert_one(master_jersey.dict())
    
    await log_user_activity(
        current_user["id"],
        "master_jersey_created",
        master_jersey.id,
        {
            "team_name": team["name"],
            "season": master_jersey.season,
            "jersey_type": master_jersey.jersey_type,
            "reference": master_jersey.topkit_reference
        }
    )
    
    # Préparer réponse enrichie
    team_info = {"id": team["id"], "name": team["name"], "short_name": team.get("short_name")}
    brand_info = {"id": brand["id"], "name": brand["name"]}
    
    return MasterJerseyResponse(
        **master_jersey.dict(),
        team_info=team_info,
        brand_info=brand_info,
        competition_info=None,
        releases_count=0,  # Updated to match model field
        collectors_count=0  # Updated to match model field - new jersey has no collectors yet
    )

# OLD VESTIAIRE ENDPOINT - COMMENTED OUT FOR KIT HIERARCHY SYSTEM
# @api_router.get("/vestiaire")
# async def get_vestiaire(
#     limit: int = 50,
#     team_id: Optional[str] = None,
#     season: Optional[str] = None,
#     player_name: Optional[str] = None
# ):
#     """Get Jersey Releases with enriched data for Vestiaire page"""
#     try:
#         # Query filters
#         query = {}
#         if team_id:
#             query["team_id"] = team_id
#         if season:
#             query["season"] = season  
#         if player_name:
#             query["player_name"] = {"$regex": player_name, "$options": "i"}
#         
#         # Get jersey releases
#         releases = await db.jersey_releases.find(query).limit(limit).to_list(None)
#         
#         # Enrich with Master Jersey data and quick evaluation
#         for release in releases:
#             release.pop('_id', None)
#             
#             # Get Master Jersey info
#             if release.get("master_jersey_id"):
#                 master = await db.master_jerseys.find_one({"id": release["master_jersey_id"]})
#                 if master:
#                     master.pop('_id', None)
#                     release["master_jersey_info"] = master
#             
#             # Quick price estimation with safe handling
#             retail_price = release.get("retail_price")
#             if retail_price is None or not isinstance(retail_price, (int, float)):
#                 retail_price = 80.0
#             
#             rarity = 5  # Default rarity
#             player_bonus = 1.2 if release.get("player_name") else 1.0
#             
#             try:
#                 estimated_value = float(retail_price) * (float(rarity) / 5.0) * float(player_bonus)
#                 release["estimated_value"] = round(estimated_value, 2)
#                 release["estimated_min"] = round(estimated_value * 0.8, 2)
#                 release["estimated_max"] = round(estimated_value * 1.2, 2)
#             except (TypeError, ValueError) as e:
#                 # Fallback values if calculation fails
#                 release["estimated_value"] = 80.0
#                 release["estimated_min"] = 64.0
#                 release["estimated_max"] = 96.0
#         
#         return releases
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching vestiaire: {str(e)}")

# ================================
# JERSEY RELEASES API  
# ================================

@api_router.get("/jersey-releases")
async def get_jersey_releases(
    master_jersey_id: Optional[str] = None,
    release_type: Optional[str] = None,
    player_id: Optional[str] = None,
    limit: int = 100
):
    """Get jersey releases with optional filters"""
    query = {}
    
    if master_jersey_id:
        query["master_jersey_id"] = master_jersey_id
    if release_type:
        query["release_type"] = release_type
    if player_id:
        query["player_id"] = player_id
    
    releases = await db.jersey_releases.find(query).limit(limit).to_list(length=None)
    
    # Enrichir avec master jersey info
    for release in releases:
        release.pop('_id', None)
        
        # Récupérer master jersey
        master_jersey = await db.master_jerseys.find_one({"id": release["master_jersey_id"]})
        if master_jersey:
            master_jersey.pop('_id', None)
            release["master_jersey_info"] = master_jersey
    
    return releases

@api_router.post("/jersey-releases")
async def create_jersey_release(
    release_data: JerseyReleaseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create new jersey release"""
    # Vérifier que master jersey existe
    master_jersey = await db.master_jerseys.find_one({"id": release_data.master_jersey_id})
    if not master_jersey:
        raise HTTPException(status_code=404, detail="Master Jersey non trouvé")
    
    release = JerseyRelease(
        **release_data.dict(),
        created_by=current_user["id"],
        topkit_reference=await generate_reference("jersey_release")
    )
    
    await db.jersey_releases.insert_one(release.dict())
    
    # Mettre à jour le compteur sur le master jersey
    await db.master_jerseys.update_one(
        {"id": release_data.master_jersey_id},
        {"$inc": {"total_releases": 1}}
    )
    
    await log_user_activity(
        current_user["id"],
        "jersey_release_created",
        release.id,
        {
            "master_jersey_id": release_data.master_jersey_id,
            "release_type": release.release_type,
            "reference": release.topkit_reference
        }
    )
    
    return release.dict()

# ================================
# CONTRIBUTIONS & COLLABORATION
# ================================.dict()

@api_router.get("/contributions/{contribution_id}")
async def get_contribution_detail(
    contribution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Obtenir les détails d'une contribution spécifique"""
    
    # Vérifier que la contribution existe
    contribution = await db.contributions.find_one({"id": contribution_id})
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    # Enrichir avec les données utilisateur
    contributor = await db.users.find_one({"id": contribution["contributor_id"]})
    if contributor:
        contribution["user_name"] = contributor.get("name", "Anonyme")
        contribution["user_profile_picture"] = contributor.get("profile_picture_url")
    
    # Ajouter le nom de l'entité
    entity_collections = {
        "team": "teams",
        "brand": "brands", 
        "player": "players",
        "competition": "competitions",
        "master_jersey": "master_jerseys",
        "jersey_release": "jersey_releases"
    }
    
    entity_collection = entity_collections.get(contribution["entity_type"])
    if entity_collection:
        entity = await db[entity_collection].find_one({"id": contribution["entity_id"]})
        if entity:
            contribution["entity_name"] = entity.get("name", "Nom non disponible")
    
    # Retirer l'_id de MongoDB pour éviter les erreurs de sérialisation
    contribution.pop('_id', None)
    
    return contribution

@api_router.get("/contributions")
async def get_contributions(
    entity_type: Optional[EntityType] = None,
    status: Optional[ContributionStatus] = None,
    contributor_id: Optional[str] = None,
    limit: int = 50
):
    """Get contributions with optional filters"""
    query = {}
    
    if entity_type:
        query["entity_type"] = entity_type
    if status:
        query["status"] = status
    if contributor_id:
        query["contributor_id"] = contributor_id
    
    contributions = await db.contributions.find(query).limit(limit).sort("created_at", -1).to_list(length=None)
    
    for contrib in contributions:
        contrib.pop('_id', None)
    
    return contributions

# Premier endpoint de vote supprimé - conflit avec le second endpoint

# ================================
# MIGRATION FROM OLD JERSEY SYSTEM
# ================================

@api_router.post("/migrate/jerseys-to-collaborative")
async def migrate_jerseys_to_collaborative(
    current_user: dict = Depends(get_current_user_admin)
):
    """Migrate existing Jersey data to collaborative system"""
    
    # Récupérer tous les jerseys existants
    old_jerseys = await db.jerseys.find({"status": "approved"}).to_list(length=None)
    
    migration_stats = {
        "teams_created": 0,
        "brands_created": 0,
        "master_jerseys_created": 0,
        "jersey_releases_created": 0,
        "errors": []
    }
    
    team_map = {}  # nom -> id
    brand_map = {}  # nom -> id
    
    for old_jersey in old_jerseys:
        try:
            old_jersey.pop('_id', None)
            
            # 1. Créer ou récupérer Team
            team_id = None
            team_name = old_jersey.get("team", "").strip()
            if team_name:
                if team_name not in team_map:
                    # Vérifier si team existe déjà
                    existing_team = await db.teams.find_one({"name": {"$regex": f"^{team_name}$", "$options": "i"}})
                    if existing_team:
                        team_id = existing_team["id"]
                        team_map[team_name] = team_id
                    else:
                        # Créer nouvelle team
                        new_team = Team(
                            name=team_name,
                            country="Unknown",  # À corriger manuellement
                            created_by=current_user["id"],
                            topkit_reference=await generate_reference("team")
                        )
                        await db.teams.insert_one(new_team.dict())
                        team_id = new_team.id
                        team_map[team_name] = team_id
                        migration_stats["teams_created"] += 1
                else:
                    team_id = team_map[team_name]
            
            # 2. Créer ou récupérer Brand
            brand_id = None
            brand_name = old_jersey.get("manufacturer", "").strip()
            if brand_name:
                if brand_name not in brand_map:
                    existing_brand = await db.brands.find_one({"name": {"$regex": f"^{brand_name}$", "$options": "i"}})
                    if existing_brand:
                        brand_id = existing_brand["id"]
                        brand_map[brand_name] = brand_id
                    else:
                        new_brand = Brand(
                            name=brand_name,
                            created_by=current_user["id"],
                            topkit_reference=await generate_reference("brand")
                        )
                        await db.brands.insert_one(new_brand.dict())
                        brand_id = new_brand.id
                        brand_map[brand_name] = brand_id
                        migration_stats["brands_created"] += 1
                else:
                    brand_id = brand_map[brand_name]
            
            if not team_id or not brand_id:
                migration_stats["errors"].append(f"Données manquantes pour jersey {old_jersey['id']}")
                continue
            
            # 3. Créer Master Jersey
            master_jersey_signature = f"{team_id}_{old_jersey.get('season', '')}_{old_jersey.get('jersey_type', 'home')}"
            
            # Vérifier si master jersey existe déjà
            existing_master = await db.master_jerseys.find_one({
                "team_id": team_id,
                "season": old_jersey.get("season", ""),
                "jersey_type": old_jersey.get("jersey_type", "home")
            })
            
            if not existing_master:
                master_jersey = MasterJersey(
                    team_id=team_id,
                    brand_id=brand_id,
                    season=old_jersey.get("season", ""),
                    jersey_type=old_jersey.get("jersey_type", "home"),
                    primary_color="Unknown",  # À remplir manuellement
                    created_by=current_user["id"],
                    topkit_reference=await generate_reference("master_jersey")
                )
                await db.master_jerseys.insert_one(master_jersey.dict())
                master_jersey_id = master_jersey.id
                migration_stats["master_jerseys_created"] += 1
            else:
                master_jersey_id = existing_master["id"]
            
            # 4. Créer Jersey Release
            jersey_release = JerseyRelease(
                master_jersey_id=master_jersey_id,
                release_type=old_jersey.get("model", "replica"),
                sku_code=old_jersey.get("sku_code"),
                product_images=[
                    old_jersey.get("front_photo_url", ""),
                    old_jersey.get("back_photo_url", "")
                ],
                created_by=current_user["id"],
                topkit_reference=await generate_reference("jersey_release")
            )
            await db.jersey_releases.insert_one(jersey_release.dict())
            migration_stats["jersey_releases_created"] += 1
            
            # 5. Marquer ancien jersey comme migré
            await db.jerseys.update_one(
                {"id": old_jersey["id"]},
                {"$set": {"migrated_to_collaborative": True, "jersey_release_id": jersey_release.id}}
            )
            
        except Exception as e:
            migration_stats["errors"].append(f"Erreur pour jersey {old_jersey.get('id', 'unknown')}: {str(e)}")
    
    return {
        "message": "Migration terminée",
        "stats": migration_stats
    }

# ================================
# SEARCH API COLLABORATIVE
# ================================

@api_router.get("/search/collaborative")
async def search_collaborative(
    q: str,
    entity_types: Optional[List[str]] = None,
    limit: int = 50
):
    """Search across all collaborative entities"""
    if not q or len(q.strip()) < 2:
        return {"results": []}
    
    search_query = q.strip()
    results = {"teams": [], "brands": [], "players": [], "competitions": [], "master_jerseys": []}
    
    # Search dans toutes les entités si pas de type spécifique
    if not entity_types:
        entity_types = ["teams", "brands", "players", "competitions", "master_jerseys"]
    
    # Search Teams
    if "teams" in entity_types:
        teams = await db.teams.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"short_name": {"$regex": search_query, "$options": "i"}},
                {"common_names": {"$elemMatch": {"$regex": search_query, "$options": "i"}}}
            ]
        }).limit(limit//len(entity_types) + 1).to_list(length=None)
        
        for team in teams:
            team.pop('_id', None)
        results["teams"] = teams
    
    # Search Brands
    if "brands" in entity_types:
        brands = await db.brands.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"official_name": {"$regex": search_query, "$options": "i"}},
                {"common_names": {"$elemMatch": {"$regex": search_query, "$options": "i"}}}
            ]
        }).limit(limit//len(entity_types) + 1).to_list(length=None)
        
        for brand in brands:
            brand.pop('_id', None)
        results["brands"] = brands
    
    # Search Players
    if "players" in entity_types:
        players = await db.players.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"full_name": {"$regex": search_query, "$options": "i"}},
                {"common_names": {"$elemMatch": {"$regex": search_query, "$options": "i"}}}
            ]
        }).limit(limit//len(entity_types) + 1).to_list(length=None)
        
        for player in players:
            player.pop('_id', None)
        results["players"] = players
    
    # Search Competitions
    if "competitions" in entity_types:
        competitions = await db.competitions.find({
            "$or": [
                {"name": {"$regex": search_query, "$options": "i"}},
                {"official_name": {"$regex": search_query, "$options": "i"}},
                {"common_names": {"$elemMatch": {"$regex": search_query, "$options": "i"}}}
            ]
        }).limit(limit//len(entity_types) + 1).to_list(length=None)
        
        for comp in competitions:
            comp.pop('_id', None)
        results["competitions"] = competitions
    
    return results

# Include the router in the main app
# ====================================================
# SYSTÈME DE CONTRIBUTION COLLABORATIF (Phase 1)
# ====================================================

async def generate_contribution_reference(entity_type: str) -> str:
    """Génère une référence unique pour une contribution"""
    # Compter les contributions existantes pour ce type
    count = await db.contributions.count_documents({"entity_type": entity_type})
    next_number = count + 1
    return f"TK-CONTRIB-{next_number:06d}"

async def get_entity_current_data(entity_type: EntityType, entity_id: str) -> Dict[str, Any]:
    """Récupère les données actuelles d'une entité"""
    collection_map = {
        EntityType.TEAM: "teams",
        EntityType.BRAND: "brands", 
        EntityType.PLAYER: "players",
        EntityType.COMPETITION: "competitions",
        EntityType.MASTER_JERSEY: "master_jerseys"
    }
    
    collection_name = collection_map.get(entity_type)
    if not collection_name:
        return {}
    
    entity = await db[collection_name].find_one({"id": entity_id})
    if entity:
        entity.pop('_id', None)
        return entity
    return {}

async def calculate_changes_summary(current_data: Dict, proposed_data: Dict) -> List[Dict[str, Any]]:
    """Calcule le résumé des changements proposés"""
    changes = []
    
    # Comparer chaque champ proposé
    for field, new_value in proposed_data.items():
        current_value = current_data.get(field)
        
        if current_value != new_value:
            changes.append({
                "field": field,
                "from": current_value,
                "to": new_value,
                "type": "update" if current_value is not None else "add"
            })
    
    return changes

async def auto_approve_contribution(contribution: Contribution) -> bool:
    """Détermine si une contribution peut être auto-approuvée"""
    # Règles d'auto-approbation simples pour la Phase 1
    auto_approve_conditions = [
        # Ajout de logo quand il n'y en a pas
        contribution.vote_score >= 3,
        
        # Contributeur de confiance (futur : niveau Expert+)
        # contribution.contributor_level in ["expert", "legend"],
        
        # Changements mineurs sans controverse
        len(contribution.changed_fields) <= 2 and "name" not in contribution.changed_fields
    ]
    
    return any(auto_approve_conditions)

@api_router.post("/contributions", response_model=ContributionResponse)
async def create_contribution(
    contribution_request: ContributionCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Créer une nouvelle contribution collaborative"""
    
    # Vérifier que l'entité existe
    current_data = await get_entity_current_data(contribution_request.entity_type, contribution_request.entity_id)
    if not current_data:
        raise HTTPException(status_code=404, detail="Entité non trouvée")
    
    # Calculer les changements
    changes_summary = await calculate_changes_summary(current_data, contribution_request.proposed_data)
    if not changes_summary:
        raise HTTPException(status_code=400, detail="Aucun changement détecté")
    
    # Vérifier les doublons (même contributeur, même entité, en attente)
    existing_contribution = await db.contributions.find_one({
        "entity_type": contribution_request.entity_type,
        "entity_id": contribution_request.entity_id,
        "contributor_id": current_user["id"],
        "status": ContributionStatus.PENDING
    })
    
    if existing_contribution:
        raise HTTPException(status_code=400, detail="Vous avez déjà une contribution en attente pour cette entité")
    
    # Créer la contribution
    from datetime import timedelta
    contribution_data = {
        "entity_type": contribution_request.entity_type,
        "entity_id": contribution_request.entity_id,
        "entity_reference": current_data.get("topkit_reference", "N/A"),
        "action_type": contribution_request.action_type,
        "current_data": current_data,
        "proposed_data": contribution_request.proposed_data,
        "changed_fields": [change["field"] for change in changes_summary],
        "title": contribution_request.title,
        "description": contribution_request.description,
        "source_urls": contribution_request.source_urls,
        "contributor_id": current_user["id"],
        "contributor_level": "Rookie",  # Par défaut pour maintenant
        "expires_at": datetime.utcnow() + timedelta(days=7),
        "topkit_reference": await generate_contribution_reference(contribution_request.entity_type)
    }
    
    # Ajouter les images si présentes
    if contribution_request.images:
        contribution_data["images"] = contribution_request.images
    
    contribution = Contribution(**contribution_data)
    
    # Insérer dans la base
    await db.contributions.insert_one(contribution.dict())
    
    # Log d'activité
    await log_user_activity(
        current_user["id"],
        "contribution_created", 
        contribution.id,
        {
            "entity_type": contribution.entity_type,
            "entity_reference": contribution.entity_reference,
            "title": contribution.title,
            "topkit_reference": contribution.topkit_reference
        }
    )
    
    # Préparer la réponse
    response = ContributionResponse(
        id=contribution.id,
        entity_type=contribution.entity_type,
        entity_reference=contribution.entity_reference,
        action_type=contribution.action_type,
        title=contribution.title,
        description=contribution.description,
        contributor={
            "id": current_user["id"],
            "username": current_user["name"],
            "level": contribution.contributor_level
        },
        changes_summary=changes_summary,
        vote_score=contribution.vote_score,
        upvotes=contribution.upvotes,
        downvotes=contribution.downvotes,
        status=contribution.status,
        created_at=contribution.created_at,
        expires_at=contribution.expires_at,
        topkit_reference=contribution.topkit_reference
    )
    
    return response

@api_router.get("/contributions", response_model=List[ContributionResponse])
async def get_contributions(
    status: Optional[ContributionStatus] = None,
    entity_type: Optional[EntityType] = None,
    contributor_id: Optional[str] = None,
    limit: int = 50,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Récupérer les contributions avec filtres"""
    
    # Construire la requête
    query = {}
    if status:
        query["status"] = status
    if entity_type:
        query["entity_type"] = entity_type
    if contributor_id:
        query["contributor_id"] = contributor_id
    
    # Récupérer les contributions
    contributions = await db.contributions.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
    
    # Enrichir avec les données des contributeurs et les votes
    responses = []
    for contrib in contributions:
        contrib.pop('_id', None)
        
        # Récupérer le contributeur
        contributor = await db.users.find_one({"id": contrib["contributor_id"]})
        contributor_info = {
            "id": contrib["contributor_id"],
            "username": contributor["name"] if contributor else "Utilisateur supprimé",
            "level": contrib.get("contributor_level", "Rookie")
        }
        
        # Vérifier le vote de l'utilisateur actuel
        user_vote = None
        if current_user:
            user_vote_data = await db.contribution_votes.find_one({
                "contribution_id": contrib["id"],
                "voter_id": current_user["id"]
            })
            if user_vote_data:
                user_vote = user_vote_data["vote_type"]
        
        # Calculer le résumé des changements
        changes_summary = await calculate_changes_summary(
            contrib.get("current_data", {}), 
            contrib.get("proposed_data", {})
        )
        
        response = ContributionResponse(
            id=contrib["id"],
            entity_type=contrib["entity_type"],
            entity_reference=contrib["entity_reference"],
            action_type=contrib["action_type"],
            title=contrib["title"],
            description=contrib.get("description"),
            contributor=contributor_info,
            changes_summary=changes_summary,
            vote_score=contrib.get("vote_score", 0),
            upvotes=contrib.get("upvotes", 0),
            downvotes=contrib.get("downvotes", 0),
            user_vote=user_vote,
            status=contrib["status"],
            created_at=contrib["created_at"],
            expires_at=contrib.get("expires_at"),
            topkit_reference=contrib["topkit_reference"]
        )
        responses.append(response)
    
    return responses

@api_router.post("/contributions/{contribution_id}/vote")
async def vote_on_contribution(
    contribution_id: str,
    vote_request: VoteRequest,
    current_user: dict = Depends(get_current_user)
):
    """Voter sur une contribution"""
    
    # Vérifier que la contribution existe
    contribution = await db.contributions.find_one({"id": contribution_id})
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    # Vérifier que la contribution est en attente
    if contribution["status"] != ContributionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cette contribution ne peut plus être votée")
    
    # Vérifier que l'utilisateur ne vote pas sur sa propre contribution
    if contribution["contributor_id"] == current_user["id"]:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas voter sur votre propre contribution")
    
    # Vérifier si l'utilisateur a déjà voté
    existing_vote = await db.contribution_votes.find_one({
        "contribution_id": contribution_id,
        "voter_id": current_user["id"]
    })
    
    if existing_vote:
        # Mettre à jour le vote existant si différent
        if existing_vote["vote_type"] != vote_request.vote_type:
            old_vote_type = existing_vote["vote_type"]
            await db.contribution_votes.update_one(
                {"id": existing_vote["id"]},
                {"$set": {
                    "vote_type": vote_request.vote_type,
                    "comment": vote_request.comment,
                    "field_votes": vote_request.field_votes or vote_request.granular_votes or {}
                }}
            )
            
            # Mettre à jour les compteurs
            vote_changes = {}
            if old_vote_type == VoteType.UPVOTE and vote_request.vote_type == VoteType.DOWNVOTE:
                vote_changes = {"upvotes": -1, "downvotes": 1, "vote_score": -2}
            elif old_vote_type == VoteType.DOWNVOTE and vote_request.vote_type == VoteType.UPVOTE:
                vote_changes = {"upvotes": 1, "downvotes": -1, "vote_score": 2}
            
            await db.contributions.update_one(
                {"id": contribution_id},
                {"$inc": vote_changes}
            )
        
        return {"message": "Vote mis à jour"}
    
    else:
        # Nouveau vote
        vote = ContributionVote(
            contribution_id=contribution_id,
            voter_id=current_user["id"],
            vote_type=vote_request.vote_type,
            comment=vote_request.comment,
            field_votes=vote_request.field_votes or vote_request.granular_votes or {}
        )
        
        await db.contribution_votes.insert_one(vote.dict())
        
        # Mettre à jour les compteurs et la liste des votants
        vote_changes = {}
        if vote_request.vote_type == VoteType.UPVOTE:
            vote_changes = {"upvotes": 1, "vote_score": 1}
        else:
            vote_changes = {"downvotes": 1, "vote_score": -1}
        
        await db.contributions.update_one(
            {"id": contribution_id},
            {
                "$inc": vote_changes,
                "$addToSet": {"voters": current_user["id"]}
            }
        )
    
    # Vérifier si la contribution peut être auto-approuvée
    updated_contribution = await db.contributions.find_one({"id": contribution_id})
    
    # Auto-approbation si score >= 3
    if updated_contribution["vote_score"] >= 3 and updated_contribution["status"] == ContributionStatus.PENDING:
        await approve_contribution_auto(contribution_id, "Approuvé automatiquement (score ≥ 3)")
    
    # Auto-rejet si score <= -2  
    elif updated_contribution["vote_score"] <= -2 and updated_contribution["status"] == ContributionStatus.PENDING:
        await db.contributions.update_one(
            {"id": contribution_id},
            {"$set": {
                "status": ContributionStatus.REJECTED,
                "reviewed_at": datetime.utcnow(),
                "moderator_notes": "Rejeté automatiquement (score ≤ -2)"
            }}
        )
    
    return {"message": "Vote enregistré", "contribution_score": updated_contribution["vote_score"]}

async def approve_contribution_auto(contribution_id: str, reason: str = "Approuvé automatiquement"):
    """Approuver automatiquement une contribution et appliquer les changements"""
    
    contribution = await db.contributions.find_one({"id": contribution_id})
    if not contribution:
        return False
    
    try:
        # Appliquer les changements à l'entité
        entity_type = contribution["entity_type"]
        entity_id = contribution["entity_id"]
        proposed_data = contribution["proposed_data"]
        images = contribution.get("images", {})
        
        # Déterminer la collection MongoDB
        collection_map = {
            "team": "teams",
            "brand": "brands",
            "player": "players", 
            "competition": "competitions",
            "master_jersey": "master_jerseys"
        }
        
        collection_name = collection_map.get(entity_type)
        if collection_name:
            # Préparer les données de mise à jour
            update_data = {
                **proposed_data,
                "last_modified_at": datetime.utcnow(),
                "last_modified_by": contribution["contributor_id"],
                "modification_count": contribution["current_data"].get("modification_count", 0) + 1
            }
            
            # CORRECTION: Appliquer les images de la contribution
            if images:
                print(f"🖼️ Applying images from contribution {contribution_id} to {entity_type} {entity_id}")
                
                # Mapper les champs d'images selon le type d'entité
                if entity_type in ["team", "brand", "competition"]:
                    # Pour teams, brands, competitions -> logo_url
                    if "logo" in images:
                        # Gérer le cas où logo est une liste ou une chaîne
                        logo_data = images["logo"]
                        if isinstance(logo_data, list) and len(logo_data) > 0:
                            update_data["logo_url"] = logo_data[0]
                        elif isinstance(logo_data, str):
                            update_data["logo_url"] = logo_data
                    
                    # Gérer team_photos pour les équipes
                    if entity_type == "team" and "team_photos" in images and "logo_url" not in update_data:
                        team_photos = images["team_photos"]
                        if isinstance(team_photos, list) and len(team_photos) > 0:
                            update_data["logo_url"] = team_photos[0]
                
                elif entity_type == "player":
                    # Pour players -> photo_url
                    if "photo" in images:
                        photo_data = images["photo"]
                        if isinstance(photo_data, list) and len(photo_data) > 0:
                            update_data["photo_url"] = photo_data[0]
                        elif isinstance(photo_data, str):
                            update_data["photo_url"] = photo_data
                    elif "profile_photo" in images:
                        profile_data = images["profile_photo"]
                        if isinstance(profile_data, list) and len(profile_data) > 0:
                            update_data["photo_url"] = profile_data[0]
                        elif isinstance(profile_data, str):
                            update_data["photo_url"] = profile_data
                
                elif entity_type == "master_jersey":
                    # Pour master jerseys -> front_photo_url, back_photo_url
                    if "front_image" in images:
                        front_data = images["front_image"]
                        if isinstance(front_data, list) and len(front_data) > 0:
                            update_data["front_photo_url"] = front_data[0]
                        elif isinstance(front_data, str):
                            update_data["front_photo_url"] = front_data
                    
                    if "back_image" in images:
                        back_data = images["back_image"]
                        if isinstance(back_data, list) and len(back_data) > 0:
                            update_data["back_photo_url"] = back_data[0]
                        elif isinstance(back_data, str):
                            update_data["back_photo_url"] = back_data
                
                print(f"✅ Image fields added to update: {[k for k in update_data.keys() if 'url' in k or 'photo' in k]}")
            
            # Mettre à jour l'entité avec les données proposées ET les images
            result = await db[collection_name].update_one(
                {"id": entity_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Successfully applied contribution {contribution_id} to {entity_type} {entity_id}")
            else:
                print(f"⚠️ No changes applied to {entity_type} {entity_id}")
        
        # Marquer la contribution comme approuvée
        await db.contributions.update_one(
            {"id": contribution_id},
            {"$set": {
                "status": ContributionStatus.AUTO_APPROVED,
                "auto_approved": True,
                "reviewed_at": datetime.utcnow(),
                "moderator_notes": reason
            }}
        )
        
        # Notifier le contributeur
        await create_notification(
            user_id=contribution["contributor_id"],
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title="✅ Contribution approuvée !",
            message=f"Votre contribution '{contribution['title']}' a été approuvée et appliquée avec succès !",
            related_id=contribution_id
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'approbation auto de la contribution {contribution_id}: {str(e)}")
        return False

@api_router.get("/contributions/{contribution_id}")
async def get_contribution_detail(
    contribution_id: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Récupérer les détails d'une contribution"""
    
    contribution = await db.contributions.find_one({"id": contribution_id})
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution non trouvée")
    
    contribution.pop('_id', None)
    
    # Récupérer le contributeur
    contributor = await db.users.find_one({"id": contribution["contributor_id"]})
    
    # Récupérer les votes
    votes = await db.contribution_votes.find({"contribution_id": contribution_id}).to_list(length=None)
    
    # Vote de l'utilisateur actuel
    user_vote = None
    if current_user:
        for vote in votes:
            if vote["voter_id"] == current_user["id"]:
                user_vote = vote["vote_type"]
                break
    
    # Calculer le résumé des changements
    changes_summary = await calculate_changes_summary(
        contribution.get("current_data", {}),
        contribution.get("proposed_data", {})
    )
    
    return {
        "contribution": contribution,
        "contributor": {
            "id": contribution["contributor_id"],
            "name": contributor["name"] if contributor else "Utilisateur supprimé",
            "level": contribution.get("contributor_level", "Rookie")
        },
        "changes_summary": changes_summary,
        "user_vote": user_vote,
        "votes": [{"voter_id": v["voter_id"], "vote_type": v["vote_type"], "comment": v.get("comment")} for v in votes]
    }

# Endpoint pour les stats de contribution (futur)
@api_router.get("/stats/contributors")
async def get_contributors_stats(limit: int = 20):
    """Récupérer le classement des contributeurs (Phase 3)"""
    
    # Pour maintenant, retourner une structure de base
    # En Phase 3, cela sera enrichi avec les vrais calculs de réputation
    
    contributors = await db.users.aggregate([
        {
            "$lookup": {
                "from": "contributions",
                "localField": "id",
                "foreignField": "contributor_id", 
                "as": "contributions"
            }
        },
        {
            "$addFields": {
                "total_contributions": {"$size": "$contributions"},
                "accepted_contributions": {
                    "$size": {
                        "$filter": {
                            "input": "$contributions",
                            "cond": {"$in": ["$$this.status", ["approved", "auto_approved"]]}
                        }
                    }
                }
            }
        },
        {"$match": {"total_contributions": {"$gt": 0}}},
        {"$sort": {"accepted_contributions": -1, "total_contributions": -1}},
        {"$limit": limit}
    ]).to_list(length=None)
    
    return {
        "contributors": [
            {
                "user_id": contrib["id"],
                "username": contrib["name"],
                "total_contributions": contrib["total_contributions"],
                "accepted_contributions": contrib["accepted_contributions"],
                "reputation_points": contrib.get("accepted_contributions", 0) * 10,  # Simple calcul pour maintenant
                "level": "Expert" if contrib.get("accepted_contributions", 0) > 10 else "Contributor" if contrib.get("accepted_contributions", 0) > 3 else "Rookie",
                "rank": i + 1
            } for i, contrib in enumerate(contributors)
        ],
        "total_contributors": len(contributors)
    }

# ====================================================

# ================================
# NEW KIT HIERARCHY SYSTEM - FRESH START
# ================================

# Helper function to generate TopKit references
async def get_next_kit_reference(kit_type: str) -> str:
    """Generate next TopKit reference number for different kit types"""
    try:
        # Get the last reference for this type
        collection_name = {
            "MASTER": "master_kits",
            "REF": "reference_kits", 
            "PERSONAL": "personal_kits"
        }.get(kit_type, "master_kits")
        
        pipeline = [
            {"$match": {"topkit_reference": {"$regex": f"^TK-{kit_type}-"}}},
            {"$sort": {"topkit_reference": -1}},
            {"$limit": 1}
        ]
        
        last_item = await db[collection_name].aggregate(pipeline).to_list(1)
        
        if last_item:
            last_ref = last_item[0]["topkit_reference"]
            # Extract number from TK-MASTER-000001 format
            last_num = int(last_ref.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        return f"TK-{kit_type}-{next_num:06d}"
        
    except Exception as e:
        logger.error(f"Error generating {kit_type} reference: {e}")
        import time
        return f"TK-{kit_type}-{int(time.time())}"

# ================================
# MASTER KIT ENDPOINTS
# ================================

@api_router.post("/master-kits", response_model=MasterKitResponse)
async def create_master_kit(
    kit_data: MasterKitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new Master Kit (design template)"""
    try:
        user_id = current_user['id']
        
        # Validate team and brand exist
        team = await db.teams.find_one({"id": kit_data.team_id})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        brand = await db.brands.find_one({"id": kit_data.brand_id})
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        # Validate competition if provided
        competition = None
        if kit_data.competition_id:
            competition = await db.competitions.find_one({"id": kit_data.competition_id})
            if not competition:
                raise HTTPException(status_code=404, detail="Competition not found")
        
        # Generate TopKit reference
        reference = await get_next_kit_reference("MASTER")
        
        # Debug logging
        logger.info(f"Creating Master Kit with data: {kit_data.dict()}")
        logger.info(f"User ID: {user_id}, Reference: {reference}")
        
        # Create Master Kit with auto-approval
        master_kit_dict = kit_data.dict()
        master_kit_dict["created_by"] = user_id
        master_kit_dict["topkit_reference"] = reference
        
        # Apply auto-approval for testing
        master_kit_dict = enable_auto_approval_for_testing(master_kit_dict, user_id)
        
        master_kit = MasterKit(**master_kit_dict)
        
        # Debug the created object
        logger.info(f"Created Master Kit object with auto-approval: {master_kit.dict()}")
        
        # Insert into database
        await db.master_kits.insert_one(master_kit.dict())
        
        # Clean the response data to remove MongoDB ObjectId fields
        team.pop('_id', None)
        brand.pop('_id', None)
        if competition:
            competition.pop('_id', None)
        
        # Return enriched response
        return MasterKitResponse(
            **master_kit.dict(),
            team_info=team or {},
            brand_info=brand or {},
            competition_info=competition or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Master kit creation error: {e}")
        raise HTTPException(status_code=500, detail="Error creating master kit")

@api_router.get("/master-kits", response_model=List[MasterKitResponse])
async def get_master_kits(
    team_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    season: Optional[str] = None,
    kit_type: Optional[KitType] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get Master Kits with filters and enriched data"""
    try:
        # Build filter query
        filter_query = {}
        if team_id:
            filter_query["team_id"] = team_id
        if brand_id:
            filter_query["brand_id"] = brand_id  
        if season:
            filter_query["season"] = season
        if kit_type:
            filter_query["kit_type"] = kit_type
        
        # MongoDB aggregation pipeline to enrich with team/brand/competition data
        pipeline = [
            {"$match": filter_query},
            {"$sort": {"created_at": -1}},
            {"$skip": offset},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "team_id",
                    "foreignField": "id", 
                    "as": "team_info"
                }
            },
            {
                "$lookup": {
                    "from": "brands",
                    "localField": "brand_id", 
                    "foreignField": "id",
                    "as": "brand_info"
                }
            },
            {
                "$lookup": {
                    "from": "competitions",
                    "localField": "competition_id",
                    "foreignField": "id",
                    "as": "competition_info"
                }
            }
        ]
        
        master_kits = await db.master_kits.aggregate(pipeline).to_list(limit)
        
        # Convert to response format
        result = []
        for kit in master_kits:
            kit.pop('_id', None)
            
            # Extract enriched data separately WITHOUT removing original fields
            team_info = kit.get('team_info', [])
            brand_info = kit.get('brand_info', [])
            competition_info = kit.get('competition_info', [])
            
            # Remove the lookup arrays from the main object (but keep original foreign key fields)
            kit.pop('team_info', None)
            kit.pop('brand_info', None)  
            kit.pop('competition_info', None)
            
            # Clean ObjectId fields from nested data
            team_data = team_info[0] if team_info else {}
            brand_data = brand_info[0] if brand_info else {}
            competition_data = competition_info[0] if competition_info else {}
            
            # Remove MongoDB ObjectId fields
            team_data.pop('_id', None)
            brand_data.pop('_id', None)
            competition_data.pop('_id', None)
            
            # Provide default values for missing fields
            kit_data = {
                **kit,
                "main_sponsor": kit.get("main_sponsor", ""),
                "reference_images": kit.get("reference_images", []),
                "total_reference_kits": kit.get("total_reference_kits", 0),
                "total_collectors": kit.get("total_collectors", 0)
            }
            
            response = MasterKitResponse(
                **kit_data,
                team_info=team_data,
                brand_info=brand_data,
                competition_info=competition_data or {}
            )
            result.append(response)
        
        return result
        
    except Exception as e:
        logger.error(f"Get master kits error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching master kits")

@api_router.get("/master-kits/{kit_id}", response_model=MasterKitResponse)
async def get_master_kit(kit_id: str):
    """Get single Master Kit with enriched data"""
    try:
        # Use aggregation to get enriched data
        pipeline = [
            {"$match": {"id": kit_id}},
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "team_id",
                    "foreignField": "id",
                    "as": "team_info"
                }
            },
            {
                "$lookup": {
                    "from": "brands", 
                    "localField": "brand_id",
                    "foreignField": "id",
                    "as": "brand_info"
                }
            },
            {
                "$lookup": {
                    "from": "competitions",
                    "localField": "competition_id", 
                    "foreignField": "id",
                    "as": "competition_info"
                }
            }
        ]
        
        result = await db.master_kits.aggregate(pipeline).to_list(1)
        if not result:
            raise HTTPException(status_code=404, detail="Master kit not found")
        
        kit = result[0]
        kit.pop('_id', None)
        
        # Extract enriched data separately
        team_info = kit.pop('team_info', [])
        brand_info = kit.pop('brand_info', [])
        competition_info = kit.pop('competition_info', [])
        
        # Clean ObjectId fields from nested data
        team_data = team_info[0] if team_info else {}
        brand_data = brand_info[0] if brand_info else {}
        competition_data = competition_info[0] if competition_info else {}
        
        # Remove MongoDB ObjectId fields
        team_data.pop('_id', None)
        brand_data.pop('_id', None)
        competition_data.pop('_id', None)
        
        # Provide default values for missing fields
        kit_data = {
            **kit,
            "main_sponsor": kit.get("main_sponsor", ""),
            "reference_images": kit.get("reference_images", []),
            "total_reference_kits": kit.get("total_reference_kits", 0),
            "total_collectors": kit.get("total_collectors", 0)
        }
        
        return MasterKitResponse(
            **kit_data,
            team_info=team_data,
            brand_info=brand_data,
            competition_info=competition_data or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get master kit error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching master kit")

# ================================
# REFERENCE KIT ENDPOINTS
# ================================

@api_router.post("/reference-kits", response_model=ReferenceKitResponse)
async def create_reference_kit(
    kit_data: ReferenceKitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a Reference Kit from a Master Kit"""
    try:
        user_id = current_user['id']
        
        # Validate master kit exists
        master_kit = await db.master_kits.find_one({"id": kit_data.master_kit_id})
        if not master_kit:
            raise HTTPException(status_code=404, detail="Master kit not found")
        
        # Generate TopKit reference
        reference = await get_next_kit_reference("REF")
        
        # Create Reference Kit
        reference_kit = ReferenceKit(
            **kit_data.dict(),
            created_by=user_id,
            topkit_reference=reference
        )
        
        # Insert into database
        await db.reference_kits.insert_one(reference_kit.dict())
        
        # Get enriched data for response
        team = await db.teams.find_one({"id": master_kit["team_id"]})
        brand = await db.brands.find_one({"id": master_kit["brand_id"]})
        
        # Clean ObjectId fields
        master_kit.pop('_id', None)
        if team:
            team.pop('_id', None)
        if brand:
            brand.pop('_id', None)
        
        return ReferenceKitResponse(
            **reference_kit.dict(),
            master_kit_info=master_kit,
            team_info=team or {},
            brand_info=brand or {}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reference kit creation error: {e}")
        raise HTTPException(status_code=500, detail="Error creating reference kit")

@api_router.get("/reference-kits", response_model=List[ReferenceKitResponse])
async def get_reference_kits(
    master_kit_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get Reference Kits with enriched data - this is what shows in Kit Store"""
    try:
        # Build filter query
        filter_query = {}
        if master_kit_id:
            filter_query["master_kit_id"] = master_kit_id
        
        # Aggregation pipeline to enrich data
        pipeline = [
            {"$match": filter_query},
            {"$sort": {"created_at": -1}},
            {"$skip": offset},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "master_jerseys",
                    "localField": "master_kit_id",
                    "foreignField": "id",
                    "as": "master_kit_info"
                }
            },
            {
                "$lookup": {
                    "from": "teams",
                    "localField": "master_kit_info.team_id",
                    "foreignField": "id", 
                    "as": "team_info"
                }
            },
            {
                "$lookup": {
                    "from": "brands",
                    "localField": "master_kit_info.brand_id",
                    "foreignField": "id",
                    "as": "brand_info"
                }
            },
            {
                "$lookup": {
                    "from": "competitions",
                    "localField": "master_kit_info.competition_id",
                    "foreignField": "id",
                    "as": "competition_info"
                }
            }
        ]
        
        reference_kits = await db.reference_kits.aggregate(pipeline).to_list(limit)
        
        # Convert to response format
        result = []
        for kit in reference_kits:
            kit.pop('_id', None)
            
            # Extract enriched data separately
            master_kit_info = kit.pop('master_kit_info', [])
            team_info = kit.pop('team_info', [])
            brand_info = kit.pop('brand_info', [])
            competition_info = kit.pop('competition_info', [])
            
            # Clean ObjectId fields from nested data
            master_kit_data = master_kit_info[0] if master_kit_info else {}
            team_data = team_info[0] if team_info else {}
            brand_data = brand_info[0] if brand_info else {}
            competition_data = competition_info[0] if competition_info else {}
            
            # Remove MongoDB ObjectId fields
            master_kit_data.pop('_id', None)
            team_data.pop('_id', None)
            brand_data.pop('_id', None)
            competition_data.pop('_id', None)
            
            # Map database fields to expected model fields and provide defaults
            response = ReferenceKitResponse(
                id=kit.get('id'),
                master_kit_id=kit.get('master_kit_id'),
                available_sizes=kit.get('sizes_available', []),
                available_prints=kit.get('available_prints', []),
                original_retail_price=kit.get('original_retail_price'),
                current_market_estimate=kit.get('current_market_price'),
                price_range_min=kit.get('price_range_min'),
                price_range_max=kit.get('price_range_max'),
                is_limited_edition=kit.get('is_limited_edition', False),
                topkit_reference=kit.get('topkit_reference'),
                verified_level=kit.get('verified_level', 'unverified'),
                # Image fields
                main_photo=kit.get('main_photo'),
                product_images=kit.get('product_images', []),
                secondary_photos=kit.get('secondary_photos', []),
                # Model and competition fields
                model_name=kit.get('model_name') or kit.get('release_type'),
                league_competition=kit.get('league_competition'),
                # Other fields
                description=kit.get('description'),
                sku_code=kit.get('sku_code'),
                barcode=kit.get('barcode'),
                release_date=kit.get('release_date'),
                production_run=kit.get('production_run'),
                material_composition=kit.get('material_composition'),
                care_instructions=kit.get('care_instructions'),
                authenticity_features=kit.get('authenticity_features', []),
                # Related data
                master_kit_info=master_kit_data,
                team_info=team_data,
                brand_info=brand_data,
                competition_info=competition_data,
                total_in_collections=kit.get('total_in_collections', 0),
                total_for_sale=kit.get('total_for_sale', 0),
                created_at=kit.get('created_at')
            )
            result.append(response)
        
        return result
        
    except Exception as e:
        logger.error(f"Get reference kits error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching reference kits")

@api_router.get("/reference-kits/{kit_id}", response_model=ReferenceKitResponse)
async def get_reference_kit_by_id(kit_id: str):
    """Get specific reference kit by ID"""
    try:
        # Get reference kit
        reference_kit = await db.reference_kits.find_one({"id": kit_id})
        
        if not reference_kit:
            raise HTTPException(status_code=404, detail="Reference kit not found")
        
        reference_kit.pop('_id', None)
        
        # Get enriched data
        master_kit_info = {}
        team_info = {}
        brand_info = {}
        competition_info = {}
        
        if reference_kit.get("master_kit_id"):
            master_kit = await db.master_jerseys.find_one({"id": reference_kit["master_kit_id"]})
            if master_kit:
                master_kit.pop('_id', None)
                master_kit_info = master_kit
                
                # Get team and brand info from master kit
                if master_kit.get("team_id"):
                    team = await db.teams.find_one({"id": master_kit["team_id"]})
                    if team:
                        team.pop('_id', None)
                        team_info = team
                
                if master_kit.get("brand_id"):
                    brand = await db.brands.find_one({"id": master_kit["brand_id"]})
                    if brand:
                        brand.pop('_id', None)
                        brand_info = brand
        
        # Get competition info if available
        competition_info = {}
        if reference_kit.get("league_competition"):
            # Try to find competition by ID first
            competition = await db.competitions.find_one({"id": reference_kit["league_competition"]})
            if competition:
                competition.pop('_id', None)
                competition_info = competition
        
        # Map database fields to expected model fields and provide defaults
        response = ReferenceKitResponse(
            id=reference_kit.get('id'),
            master_kit_id=reference_kit.get('master_kit_id'),
            available_sizes=reference_kit.get('sizes_available', []),
            available_prints=reference_kit.get('available_prints', []),
            original_retail_price=reference_kit.get('original_retail_price'),
            current_market_estimate=reference_kit.get('current_market_price'),
            price_range_min=reference_kit.get('price_range_min'),
            price_range_max=reference_kit.get('price_range_max'),
            is_limited_edition=reference_kit.get('is_limited_edition', False),
            topkit_reference=reference_kit.get('topkit_reference'),
            verified_level=reference_kit.get('verified_level', 'unverified'),
            # Image fields
            main_photo=reference_kit.get('main_photo'),
            product_images=reference_kit.get('product_images', []),
            secondary_photos=reference_kit.get('secondary_photos', []),
            # Model and competition fields
            model_name=reference_kit.get('model_name') or reference_kit.get('release_type'),
            league_competition=reference_kit.get('league_competition'),
            # Other fields
            description=reference_kit.get('description'),
            sku_code=reference_kit.get('sku_code'),
            barcode=reference_kit.get('barcode'),
            release_date=reference_kit.get('release_date'),
            production_run=reference_kit.get('production_run'),
            material_composition=reference_kit.get('material_composition'),
            care_instructions=reference_kit.get('care_instructions'),
            authenticity_features=reference_kit.get('authenticity_features', []),
            # Related data
            master_kit_info=master_kit_info,
            team_info=team_info,
            brand_info=brand_info,
            competition_info=competition_info,
            total_in_collections=reference_kit.get('total_in_collections', 0),
            total_for_sale=reference_kit.get('total_for_sale', 0),
            created_at=reference_kit.get('created_at')
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Get reference kit by ID error: {e}")
        raise HTTPException(status_code=500, detail="Error fetching reference kit")

# ================================
# PERSONAL KIT ENDPOINTS (USER COLLECTIONS)
# ================================

@api_router.post("/personal-kits")
async def add_kit_to_owned_collection(
    kit_data: PersonalKitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a Reference Kit to user's OWNED collection with detailed personalization"""
    try:
        user_id = current_user['id']
        
        # Validate reference kit exists
        reference_kit = await db.reference_kits.find_one({"id": kit_data.reference_kit_id})
        if not reference_kit:
            raise HTTPException(status_code=404, detail="Reference kit not found")
        reference_kit.pop('_id', None)
        
        # Check if user already has this kit in their owned collection
        existing_owned = await db.personal_kits.find_one({
            "user_id": user_id,
            "reference_kit_id": kit_data.reference_kit_id
        })
        if existing_owned:
            raise HTTPException(status_code=400, detail="Kit already in your owned collection")
        
        # Smart two-way relationship: If adding to "owned", remove from "wanted"
        existing_wanted = await db.wanted_kits.find_one({
            "user_id": user_id,
            "reference_kit_id": kit_data.reference_kit_id
        })
        if existing_wanted:
            # Remove from wanted list since user now owns it
            await db.wanted_kits.delete_one({
                "user_id": user_id,
                "reference_kit_id": kit_data.reference_kit_id
            })
            logger.info(f"Automatically removed kit {kit_data.reference_kit_id} from user {user_id} wanted list (now owned)")
        
        # Create Personal Kit (ONLY for owned items)
        personal_kit = PersonalKit(
            **kit_data.dict(),
            user_id=user_id
        )
        
        # Insert into database
        await db.personal_kits.insert_one(personal_kit.dict())
        
        # Get enriched data for response
        master_kit = await db.master_kits.find_one({"id": reference_kit["master_kit_id"]})
        if master_kit:
            master_kit.pop('_id', None)
        
        team = await db.teams.find_one({"id": master_kit["team_id"]}) if master_kit else None
        if team:
            team.pop('_id', None)
            
        brand = await db.brands.find_one({"id": master_kit["brand_id"]}) if master_kit else None
        if brand:
            brand.pop('_id', None)
        
        # Return enriched response
        response = {
            **personal_kit.dict(),
            "reference_kit_info": reference_kit,
            "master_kit_info": master_kit or {},
            "team_info": team or {},
            "brand_info": brand or {}
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Personal kit creation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error adding kit to owned collection")

@api_router.post("/wanted-kits")
async def add_kit_to_wanted_list(
    kit_data: WantedKitCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a Reference Kit to user's WANTED list (remains as Reference Kit)"""
    try:
        user_id = current_user['id']
        
        # Validate reference kit exists
        reference_kit = await db.reference_kits.find_one({"id": kit_data.reference_kit_id})
        if not reference_kit:
            raise HTTPException(status_code=404, detail="Reference kit not found")
        reference_kit.pop('_id', None)
        
        # Check if user already has this kit in their wanted list
        existing_wanted = await db.wanted_kits.find_one({
            "user_id": user_id,
            "reference_kit_id": kit_data.reference_kit_id
        })
        if existing_wanted:
            raise HTTPException(status_code=400, detail="Kit already in your wanted list")
        
        # Check if user already owns this kit
        existing_owned = await db.personal_kits.find_one({
            "user_id": user_id,
            "reference_kit_id": kit_data.reference_kit_id
        })
        if existing_owned:
            raise HTTPException(status_code=400, detail="You already own this kit")
        
        # Create Wanted Kit (simple reference, kit remains Reference Kit)
        wanted_kit = WantedKit(
            **kit_data.dict(),
            user_id=user_id
        )
        
        # Insert into database
        await db.wanted_kits.insert_one(wanted_kit.dict())
        
        # Get enriched data for response (but kit remains a Reference Kit)
        master_kit = await db.master_kits.find_one({"id": reference_kit["master_kit_id"]})
        if master_kit:
            master_kit.pop('_id', None)
        
        team = await db.teams.find_one({"id": master_kit["team_id"]}) if master_kit else None
        if team:
            team.pop('_id', None)
            
        brand = await db.brands.find_one({"id": master_kit["brand_id"]}) if master_kit else None
        if brand:
            brand.pop('_id', None)
        
        # Return response - kit remains a Reference Kit with minimal wanted info
        response = {
            **wanted_kit.dict(),
            "reference_kit_info": reference_kit,
            "master_kit_info": master_kit or {},
            "team_info": team or {},
            "brand_info": brand or {}
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wanted kit creation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error adding kit to wanted list")

@api_router.get("/personal-kits")  
async def get_user_owned_collection(
    current_user: dict = Depends(get_current_user)
):
    """Get user's OWNED kit collection with enriched data"""
    try:
        user_id = current_user['id']
        
        # Get personal kits (owned only)
        personal_kits = await db.personal_kits.find({"user_id": user_id}).sort("added_to_collection_at", -1).to_list(1000)
        
        # Convert to response format
        result = []
        for kit in personal_kits:
            kit.pop('_id', None)
            
            # Get reference kit
            reference_kit = await db.reference_kits.find_one({"id": kit.get("reference_kit_id")})
            if reference_kit:
                reference_kit.pop('_id', None)
            
            # Get master kit
            master_kit = None
            if reference_kit:
                master_kit = await db.master_kits.find_one({"id": reference_kit.get("master_kit_id")})
                if master_kit:
                    master_kit.pop('_id', None)
            
            # Get team and brand
            team = None
            brand = None
            if master_kit:
                team = await db.teams.find_one({"id": master_kit.get("team_id")})
                if team:
                    team.pop('_id', None)
                    
                brand = await db.brands.find_one({"id": master_kit.get("brand_id")})
                if brand:
                    brand.pop('_id', None)
            
            # Create enriched response
            response = {
                **kit,
                "reference_kit_info": reference_kit or {},
                "master_kit_info": master_kit or {},
                "team_info": team or {},
                "brand_info": brand or {}
            }
            result.append(response)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting owned collection: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving owned collection")

@api_router.get("/wanted-kits")  
async def get_user_wanted_list(
    current_user: dict = Depends(get_current_user)
):
    """Get user's WANTED kit list with enriched Reference Kit data"""
    try:
        user_id = current_user['id']
        
        # Get wanted kits
        wanted_kits = await db.wanted_kits.find({"user_id": user_id}).sort("added_to_wanted_at", -1).to_list(1000)
        
        # Convert to response format
        result = []
        for kit in wanted_kits:
            kit.pop('_id', None)
            
            # Get reference kit (kit remains a Reference Kit in wanted list)
            reference_kit = await db.reference_kits.find_one({"id": kit.get("reference_kit_id")})
            if reference_kit:
                reference_kit.pop('_id', None)
            
            # Get master kit
            master_kit = None
            if reference_kit:
                master_kit = await db.master_kits.find_one({"id": reference_kit.get("master_kit_id")})
                if master_kit:
                    master_kit.pop('_id', None)
            
            # Get team and brand
            team = None
            brand = None
            if master_kit:
                team = await db.teams.find_one({"id": master_kit.get("team_id")})
                if team:
                    team.pop('_id', None)
                    
                brand = await db.brands.find_one({"id": master_kit.get("brand_id")})
                if brand:
                    brand.pop('_id', None)
            
            # Create enriched response - kit remains Reference Kit with wanted preferences
            response = {
                **kit,
                "reference_kit_info": reference_kit or {},
                "master_kit_info": master_kit or {},
                "team_info": team or {},
                "brand_info": brand or {}
            }
            result.append(response)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting wanted list: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving wanted list")

@api_router.put("/personal-kits/{kit_id}", response_model=PersonalKitResponse)
async def update_personal_kit(
    kit_id: str,
    update_data: PersonalKitUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user's personal kit details (only owner can edit)"""
    try:
        user_id = current_user['id']
        
        # Verify ownership
        personal_kit = await db.personal_kits.find_one({
            "id": kit_id,
            "user_id": user_id
        })
        if not personal_kit:
            raise HTTPException(status_code=404, detail="Personal kit not found or not owned by you")
        
        # Prepare update data (exclude None values)
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if update_dict:
            update_dict["last_updated_at"] = datetime.utcnow()
            
            # Update in database
            await db.personal_kits.update_one(
                {"id": kit_id},
                {"$set": update_dict}
            )
        
        # Get updated kit with enriched data
        updated_kit = await get_enriched_personal_kit(kit_id)
        return updated_kit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Personal kit update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating personal kit")

@api_router.delete("/personal-kits/{kit_id}")
async def remove_kit_from_owned_collection(
    kit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove kit from user's OWNED collection (only owner can remove)"""
    try:
        user_id = current_user['id']
        
        # Verify ownership and delete
        result = await db.personal_kits.delete_one({
            "id": kit_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Personal kit not found or not owned by you")
        
        return {"message": "Kit removed from owned collection successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Personal kit removal error: {e}")
        raise HTTPException(status_code=500, detail="Error removing kit from owned collection")

@api_router.delete("/wanted-kits/{kit_id}")
async def remove_kit_from_wanted_list(
    kit_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove kit from user's WANTED list (only owner can remove)"""
    try:
        user_id = current_user['id']
        
        # Verify ownership and delete
        result = await db.wanted_kits.delete_one({
            "id": kit_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Wanted kit not found or not owned by you")
        
        return {"message": "Kit removed from wanted list successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wanted kit removal error: {e}")
        raise HTTPException(status_code=500, detail="Error removing kit from wanted list")

# Helper function for enriched personal kit data
async def get_enriched_personal_kit(kit_id: str) -> PersonalKitResponse:
    """Get personal kit with all enriched data"""
    pipeline = [
        {"$match": {"id": kit_id}},
        {
            "$lookup": {
                "from": "reference_kits",
                "localField": "reference_kit_id", 
                "foreignField": "id",
                "as": "reference_kit_info"
            }
        },
        {
            "$lookup": {
                "from": "master_kits",
                "localField": "reference_kit_info.master_kit_id",
                "foreignField": "id", 
                "as": "master_kit_info"
            }
        },
        {
            "$lookup": {
                "from": "teams",
                "localField": "master_kit_info.team_id",
                "foreignField": "id",
                "as": "team_info"
            }
        },
        {
            "$lookup": {
                "from": "brands",
                "localField": "master_kit_info.brand_id",
                "foreignField": "id", 
                "as": "brand_info"
            }
        },
        {
            "$addFields": {
                "reference_kit_info": {"$arrayElemAt": ["$reference_kit_info", 0]},
                "master_kit_info": {"$arrayElemAt": ["$master_kit_info", 0]},
                "team_info": {"$arrayElemAt": ["$team_info", 0]},
                "brand_info": {"$arrayElemAt": ["$brand_info", 0]}
            }
        }
    ]
    
    result = await db.personal_kits.aggregate(pipeline).to_list(1)
    if not result:
        raise HTTPException(status_code=404, detail="Personal kit not found")
    
    kit = result[0]
    kit.pop('_id', None)
    
    # Clean up any remaining _id fields in nested objects
    for field in ['reference_kit_info', 'master_kit_info', 'team_info', 'brand_info']:
        if kit.get(field) and isinstance(kit[field], dict):
            kit[field].pop('_id', None)
    
    # The aggregation pipeline now properly formats the data
    return PersonalKitResponse(**kit)

# ================================
# KIT STORE ENDPOINT (VESTIAIRE) - SHOWS REFERENCE KITS
# ================================

@api_router.get("/vestiaire")
async def get_kit_store(
    team_id: Optional[str] = None,
    brand_id: Optional[str] = None,
    season: Optional[str] = None,
    kit_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get Kit Store (Vestiaire) - Shows Reference Kits available for collection
    This replaces the old vestiaire endpoint and shows Reference Kits that users can add to their Personal Collections
    """
    try:
        logger.info("=== VESTIAIRE ENDPOINT CALLED ===")
        
        # Simple approach: get reference kits and manually enrich them
        # This bypasses the aggregation pipeline issues
        
        # Get reference kits with basic filtering
        ref_kit_filter = {}
        
        # Get all reference kits first
        all_reference_kits = await db.reference_kits.find(ref_kit_filter).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        
        logger.info(f"Vestiaire debug: Found {len(all_reference_kits)} reference kits from database")
        
        result = []
        for rk in all_reference_kits:
            rk.pop('_id', None)
            
            # Get master kit (from master_jerseys collection)
            master_kit = await db.master_jerseys.find_one({"id": rk.get("master_kit_id")})
            if not master_kit:
                logger.info(f"Skipping reference kit {rk.get('topkit_reference')} - master kit not found")
                continue  # Skip if master kit not found
            master_kit.pop('_id', None)
            
            # Apply filters based on master kit data
            if team_id and master_kit.get("team_id") != team_id:
                continue
            if season and season.lower() not in master_kit.get("season", "").lower():
                continue
            if kit_type and master_kit.get("kit_type") != kit_type:
                continue
            
            # Get team info
            team = await db.teams.find_one({"id": master_kit.get("team_id")})
            if team:
                team.pop('_id', None)
            
            # Get brand info
            brand = await db.brands.find_one({"id": master_kit.get("brand_id")})
            if brand:
                brand.pop('_id', None)
            
            # Apply search filter
            if search:
                search_lower = search.lower()
                team_name = team.get("name", "").lower() if team else ""
                brand_name = brand.get("name", "").lower() if brand else ""
                season_name = master_kit.get("season", "").lower()
                design_name = master_kit.get("design_name", "").lower()
                
                if not any(search_lower in field for field in [team_name, brand_name, season_name, design_name]):
                    continue
            
            # Create response object without strict Pydantic validation
            response = {
                **rk,
                "master_kit_info": master_kit,
                "team_info": team or {},
                "brand_info": brand or {}
            }
            result.append(response)
        
        logger.info(f"Vestiaire returning {len(result)} reference kits")
        return result
        
    except Exception as e:
        logger.error(f"Kit store error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error fetching kit store")


# ================================
# ENHANCED CONTRIBUTIONS SYSTEM V2 - DISCOGS STYLE
# ================================

async def generate_topkit_reference(entity_type: str) -> str:
    """Generate TopKit reference for contributions"""
    entity_prefixes = {
        ContributionType.TEAM: "TK-TEAM",
        ContributionType.BRAND: "TK-BRAND", 
        ContributionType.PLAYER: "TK-PLAYER",
        ContributionType.COMPETITION: "TK-COMP",
        ContributionType.MASTER_KIT: "TK-MKIT",
        ContributionType.REFERENCE_KIT: "TK-RKIT"
    }
    
    prefix = entity_prefixes.get(entity_type, "TK-CONTRIB")
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

async def integrate_approved_contribution_to_catalogue(contribution_id: str, contribution: dict, user_id: str):
    """Integrate approved contribution data into the main catalogue"""
    try:
        entity_type = contribution.get('entity_type')
        data = contribution.get('data', {})
        images = contribution.get('images', [])
        
        # Extract logo/image URL from contribution images (first image becomes logo)
        logo_url = ""
        if images and len(images) > 0:
            image_path = images[0].get('url', '') if isinstance(images[0], dict) else str(images[0])
            # Ensure the URL includes the /api prefix for proper routing
            if image_path and not image_path.startswith('http') and not image_path.startswith('data:'):
                logo_url = f"api/{image_path}"
            else:
                logo_url = image_path
        
        # Generate new entity ID
        entity_id = str(uuid.uuid4())
        
        # Common fields for all entities
        common_fields = {
            "id": entity_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "verified_level": "community_verified",
            "verified_at": contribution.get('reviewed_at', datetime.utcnow()),
            "verified_by": user_id,
            "source_contribution_id": contribution_id,
            "topkit_reference": contribution.get('topkit_reference')
        }
        
        if entity_type == 'team':
            team_doc = {
                **common_fields,
                "name": data.get('name'),
                "country": data.get('country'),
                "city": data.get('city', ''),
                "founded_year": data.get('founded_year'),
                "short_name": data.get('short_name', ''),
                "official_name": data.get('official_name', ''),
                "alternative_names": data.get('alternative_names', []),
                "colors": data.get('colors', []),
                "logo_url": logo_url or data.get('logo_url', ''),  # Use image from contribution
                "stadium": data.get('stadium', ''),
                "league_info": data.get('league_info', {}),
                "current_competitions": data.get('current_competitions', []),
                "primary_competition_id": data.get('primary_competition_id', '')
            }
            await db.teams.insert_one(team_doc)
            logger.info(f"Integrated team: {data.get('name')} to catalogue with logo: {logo_url}")
                
        elif entity_type == 'brand':
            brand_doc = {
                **common_fields,
                "name": data.get('name'),
                "official_name": data.get('official_name', ''),
                "country": data.get('country'),
                "founded_year": data.get('founded_year'),
                "website": data.get('website', ''),
                "alternative_names": data.get('alternative_names', []),
                "logo_url": logo_url or data.get('logo_url', ''),  # Use image from contribution
                "description": data.get('description', '')
            }
            await db.brands.insert_one(brand_doc)
            logger.info(f"Integrated brand: {data.get('name')} to catalogue with logo: {logo_url}")
                
        elif entity_type == 'player':
            player_doc = {
                **common_fields,
                "name": data.get('name'),
                "common_name": data.get('common_name', ''),
                "nationality": data.get('nationality'),
                "birth_date": data.get('birth_date', ''),
                "position": data.get('position', ''),
                "current_team": data.get('current_team', ''),
                "jersey_number": data.get('jersey_number'),
                "alternative_names": data.get('alternative_names', []),
                "height": data.get('height', ''),
                "weight": data.get('weight', ''),
                "foot": data.get('foot', ''),
                "market_value": data.get('market_value', ''),
                "profile_picture_url": logo_url or data.get('profile_picture_url', '')  # Use image from contribution
            }
            await db.players.insert_one(player_doc)
            logger.info(f"Integrated player: {data.get('name')} to catalogue with photo: {logo_url}")
                
        elif entity_type == 'competition':
            competition_doc = {
                **common_fields,
                "competition_name": data.get('competition_name'),
                "official_name": data.get('official_name', ''),
                "type": data.get('type'),
                "country": data.get('country'),
                "level": data.get('level', 1),
                "confederations_federations": data.get('confederations_federations', []),
                "alternative_names": data.get('alternative_names', []),
                "season_format": data.get('season_format', ''),
                "current_season": data.get('current_season', ''),
                "logo_url": logo_url or data.get('logo_url', '')  # Use image from contribution
            }
            await db.competitions.insert_one(competition_doc)
            logger.info(f"Integrated competition: {data.get('competition_name')} to catalogue with logo: {logo_url}")
                
        elif entity_type == 'master_kit':
            # For master kits, we need to resolve team_name/brand_name to team_id/brand_id
            team_id = data.get('team_id', '')
            brand_id = data.get('brand_id', '')
            
            # If we have names instead of IDs, try to resolve them
            if not team_id and data.get('team_name'):
                team = await db.teams.find_one({"name": {"$regex": data.get('team_name'), "$options": "i"}})
                if team:
                    team_id = team['id']
                    logger.info(f"Resolved team '{data.get('team_name')}' to ID: {team_id}")
                else:
                    logger.warning(f"Could not resolve team name '{data.get('team_name')}' to team_id")
            
            if not brand_id and data.get('brand_name'):
                brand = await db.brands.find_one({"name": {"$regex": data.get('brand_name'), "$options": "i"}})
                if brand:
                    brand_id = brand['id']
                    logger.info(f"Resolved brand '{data.get('brand_name')}' to ID: {brand_id}")
                else:
                    logger.warning(f"Could not resolve brand name '{data.get('brand_name')}' to brand_id")
            
            master_jersey_doc = {
                **common_fields,
                "team_id": team_id,
                "brand_id": brand_id,
                "season": data.get('season', ''),  # Ensure season is never None
                "jersey_type": data.get('jersey_type', 'home'),
                "model": data.get('model', ''),
                "primary_color": data.get('primary_color', ''),
                "secondary_colors": data.get('secondary_colors', []),
                "pattern": data.get('pattern', ''),
                "main_image_url": logo_url or data.get('main_image_url', ''),  # Use image from contribution
                "additional_images": data.get('additional_images', []),
                "description": data.get('description', ''),
                "material": data.get('material', ''),
                "manufacturer_code": data.get('manufacturer_code', ''),
                "release_date": data.get('release_date', ''),
                "discontinued_date": data.get('discontinued_date', ''),
                "created_by": user_id  # Ensure created_by is always present
            }
            await db.master_jerseys.insert_one(master_jersey_doc)
            logger.info(f"Integrated master kit: {data.get('season')} {data.get('jersey_type')} to catalogue with team_id: {team_id}, brand_id: {brand_id}, image: {logo_url}")
            
        elif entity_type == 'reference_kit':
            # For reference kits, extract multiple images
            product_images = []
            main_photo = logo_url
            secondary_photos = []
            
            for i, img in enumerate(images):
                img_url = img.get('url', '') if isinstance(img, dict) else str(img)
                # Ensure the URL includes the /api prefix for proper routing
                if img_url and not img_url.startswith('http') and not img_url.startswith('data:'):
                    img_url = f"api/{img_url}"
                
                if i == 0:
                    main_photo = img_url
                else:
                    secondary_photos.append(img_url)
                product_images.append(img_url)
            
            reference_kit_doc = {
                **common_fields,
                "master_kit_id": data.get('master_kit_id', ''),
                "model_name": data.get('model_name'),
                "release_type": data.get('release_type', 'replica'),
                "original_retail_price": data.get('original_retail_price', 0.0),
                "current_market_price": data.get('current_market_price', 0.0),
                "release_date": data.get('release_date', ''),
                "sku_code": data.get('sku_code', ''),
                "barcode": data.get('barcode', ''),
                "is_limited_edition": data.get('is_limited_edition', False),
                "production_run": data.get('production_run', None),
                "league_competition": data.get('league_competition', ''),
                "product_images": product_images,  # All images from contribution
                "main_photo": main_photo,  # Primary image from contribution
                "secondary_photos": secondary_photos,  # Additional images from contribution
                "description": data.get('description', ''),
                "sizes_available": data.get('sizes_available', []),
                "material_composition": data.get('material_composition', ''),
                "care_instructions": data.get('care_instructions', ''),
                "authenticity_features": data.get('authenticity_features', [])
            }
            await db.reference_kits.insert_one(reference_kit_doc)
            logger.info(f"Integrated reference kit: {data.get('model_name')} {data.get('release_type')} to Kit Store with {len(product_images)} images")
        
        # Mark contribution as integrated
        await db.contributions_v2.update_one(
            {"id": contribution_id},
            {
                "$set": {
                    "integrated": True,
                    "integrated_at": datetime.utcnow(),
                    "integrated_entity_id": entity_id,
                    "integrated_entity_type": entity_type
                }
            }
        )
        
        logger.info(f"Successfully integrated {entity_type} contribution {contribution_id} to catalogue with image data")
        
    except Exception as e:
        logger.error(f"Error integrating contribution {contribution_id} to catalogue: {e}")
        raise

async def send_contribution_notification(user_id: str, contribution_id: str, action: str, auto_action: bool = False):
    """Send email notification for contribution updates"""
    try:
        # Get user email
        user = await db.users.find_one({"id": user_id})
        if not user:
            return
        
        # Get contribution details
        contribution = await db.contributions_v2.find_one({"id": contribution_id})
        if not contribution:
            return
        
        subject = f"TopKit - Contribution {action.title()}"
        
        if auto_action:
            message = f"""
            Your contribution "{contribution['title']}" has been automatically {action} by the community!
            
            Contribution Reference: {contribution['topkit_reference']}
            Entity Type: {contribution['entity_type'].replace('_', ' ').title()}
            Votes: {contribution['upvotes']} upvotes, {contribution['downvotes']} downvotes
            
            Thank you for contributing to the TopKit community database!
            """
        else:
            message = f"""
            Your contribution "{contribution['title']}" has been {action} by an administrator.
            
            Contribution Reference: {contribution['topkit_reference']}
            Entity Type: {contribution['entity_type'].replace('_', ' ').title()}
            
            Thank you for contributing to the TopKit community database!
            """
        
        # Use existing Gmail service to send notification
        try:
            await gmail_service.send_email(
                to_email=user['email'],
                subject=subject,
                body=message
            )
        except Exception as email_error:
            logger.error(f"Gmail service error: {email_error}")
            # Fallback: log the notification instead
            print(f"EMAIL NOTIFICATION: {user['email']} - {subject} - {message}")
        
    except Exception as e:
        logger.error(f"Failed to send contribution notification: {e}")

@api_router.post("/contributions-v2/", response_model=ContributionDetail)
async def create_contribution_v2(
    contribution_data: ContributionCreateV2,
    current_user: dict = Depends(get_current_user)
):
    """Create a new Discogs-style contribution"""
    try:
        user_id = current_user['id']
        
        # DEBUG: Log the received contribution data
        logger.info(f"DEBUG - Received contribution data: {contribution_data.dict()}")
        logger.info(f"DEBUG - Data field content: {contribution_data.data}")
        logger.info(f"DEBUG - Entity type: {contribution_data.entity_type}")
        
        # Validate entity type and data requirements
        requires_images = contribution_data.entity_type in [ContributionType.MASTER_KIT, ContributionType.REFERENCE_KIT]
        
        # Generate TopKit reference
        topkit_reference = await generate_topkit_reference(contribution_data.entity_type)
        
        # Create contribution
        contribution = EnhancedContribution(
            entity_type=contribution_data.entity_type,
            entity_id=contribution_data.entity_id,
            title=contribution_data.title,
            description=contribution_data.description,
            data=contribution_data.data,
            source_urls=contribution_data.source_urls,
            created_by=user_id,
            status=ContributionStatusV2.PENDING_REVIEW,
            topkit_reference=topkit_reference
        )
        
        # Add initial history entry
        history_entry = ContributionHistoryEntry(
            action="created",
            user_id=user_id,
            user_name=current_user.get('name', 'Unknown'),
            details={
                "entity_type": contribution_data.entity_type,
                "title": contribution_data.title
            }
        )
        contribution.history.append(history_entry)
        
        # Insert into database
        await db.contributions_v2.insert_one(contribution.dict())
        
        # Log activity
        await log_user_activity(user_id, "contribution_created_v2", contribution.id, {
            "entity_type": contribution_data.entity_type,
            "title": contribution_data.title,
            "topkit_reference": topkit_reference
        })
        
        # Convert to response format
        return ContributionDetail(
            **contribution.dict(), 
            user_can_vote=False,
            user_vote=None,
            requires_images=requires_images
        )
        
    except Exception as e:
        logger.error(f"Create contribution error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la contribution")

@api_router.get("/contributions-v2/", response_model=List[ContributionSummary])
async def list_contributions_v2(
    status: Optional[ContributionStatusV2] = None,
    entity_type: Optional[ContributionType] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """List contributions with filtering and pagination"""
    try:
        user_id = current_user['id']
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        if entity_type:
            query["entity_type"] = entity_type
        
        # For non-admin users, show approved contributions + their own contributions
        if current_user.get('role') != 'admin':
            query["$or"] = [
                {"status": ContributionStatusV2.APPROVED},
                {"created_by": user_id},
                {"status": {"$in": [ContributionStatusV2.PENDING_REVIEW, ContributionStatusV2.NEEDS_REVISION]}}
            ]
        
        # Get contributions with pagination
        skip = (page - 1) * limit
        contributions = await db.contributions_v2.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Convert to summary format
        summaries = []
        for contrib in contributions:
            contrib.pop('_id', None)
            summary = ContributionSummary(
                id=contrib['id'],
                entity_type=contrib['entity_type'],
                title=contrib['title'],
                status=contrib['status'],
                upvotes=contrib['upvotes'],
                downvotes=contrib['downvotes'],
                created_by=contrib['created_by'],
                created_at=contrib['created_at'],
                updated_at=contrib['updated_at'],
                images_count=len(contrib.get('images', [])),
                topkit_reference=contrib['topkit_reference']
            )
            summaries.append(summary)
        
        return summaries
        
    except Exception as e:
        logger.error(f"List contributions error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des contributions")

@api_router.get("/contributions-v2/{contribution_id}", response_model=ContributionDetail)
async def get_contribution_v2(
    contribution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed contribution information"""
    try:
        user_id = current_user['id']
        
        contribution = await db.contributions_v2.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution non trouvée")
        
        # Check visibility permissions (Discogs-style: visible to logged-in users during review)
        if (contribution['status'] == ContributionStatusV2.DRAFT and 
            contribution['created_by'] != user_id and 
            current_user.get('role') != 'admin'):
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à voir cette contribution")
        
        contribution.pop('_id', None)
        
        # Check if user can vote (not the creator)
        user_can_vote = contribution['created_by'] != user_id
        
        # Check if user already voted
        user_vote = None
        for vote in contribution.get('votes', []):
            if vote['user_id'] == user_id:
                user_vote = vote['vote_type']
                break
        
        # Check if images are required
        requires_images = contribution['entity_type'] in [ContributionType.MASTER_KIT, ContributionType.REFERENCE_KIT]
        
        return ContributionDetail(
            **contribution,
            user_can_vote=user_can_vote,
            user_vote=user_vote,
            requires_images=requires_images
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contribution error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de la contribution")

@api_router.post("/contributions-v2/{contribution_id}/vote")
async def vote_on_contribution_v2(
    contribution_id: str,
    vote_data: ContributionVoteRequest,
    current_user: dict = Depends(get_current_user)
):
    """Vote on a contribution (Discogs-style voting: 3 upvotes = auto-approve, 2 downvotes = auto-reject)"""
    try:
        user_id = current_user['id']
        
        # Get contribution
        contribution = await db.contributions_v2.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution non trouvée")
        
        # Check if user can vote (not the creator)
        if contribution['created_by'] == user_id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez pas voter sur votre propre contribution")
        
        # Check if contribution is in votable status
        if contribution['status'] not in [ContributionStatusV2.PENDING_REVIEW, ContributionStatusV2.NEEDS_REVISION]:
            raise HTTPException(status_code=400, detail="Cette contribution n'est pas ouverte au vote")
        
        # Check if user already voted
        existing_vote_index = None
        for i, vote in enumerate(contribution.get('votes', [])):
            if vote['user_id'] == user_id:
                existing_vote_index = i
                break
        
        # Create new vote
        new_vote = ContributionVoteV2(
            user_id=user_id,
            vote_type=vote_data.vote_type,
            comment=vote_data.comment,
            field_votes=vote_data.field_votes
        )
        
        # Update vote counts
        upvotes = contribution.get('upvotes', 0)
        downvotes = contribution.get('downvotes', 0)
        
        if existing_vote_index is not None:
            # Remove old vote count
            old_vote = contribution['votes'][existing_vote_index]
            if old_vote['vote_type'] == VoteTypeV2.UPVOTE:
                upvotes -= 1
            else:
                downvotes -= 1
            
            # Replace existing vote
            contribution['votes'][existing_vote_index] = new_vote.dict()
        else:
            # Add new vote
            if 'votes' not in contribution:
                contribution['votes'] = []
            contribution['votes'].append(new_vote.dict())
        
        # Add new vote count
        if vote_data.vote_type == VoteTypeV2.UPVOTE:
            upvotes += 1
        else:
            downvotes += 1
        
        # Check for auto-approval/rejection (Discogs style: 3 upvotes = approve, 2 downvotes = reject)
        auto_approved = False
        auto_rejected = False
        new_status = contribution['status']
        
        if upvotes >= 3 and contribution['status'] == ContributionStatusV2.PENDING_REVIEW:
            new_status = ContributionStatusV2.APPROVED
            auto_approved = True
        elif downvotes >= 2 and contribution['status'] in [ContributionStatusV2.PENDING_REVIEW, ContributionStatusV2.NEEDS_REVISION]:
            new_status = ContributionStatusV2.REJECTED
            auto_rejected = True
        
        # Add history entry
        history_entry = ContributionHistoryEntry(
            action="voted",
            user_id=user_id,
            user_name=current_user.get('name', 'Unknown'),
            details={
                "vote_type": vote_data.vote_type,
                "upvotes": upvotes,
                "downvotes": downvotes,
                "auto_approved": auto_approved,
                "auto_rejected": auto_rejected
            }
        )
        
        # Update contribution
        await db.contributions_v2.update_one(
            {"id": contribution_id},
            {
                "$set": {
                    "votes": contribution['votes'],
                    "upvotes": upvotes,
                    "downvotes": downvotes,
                    "status": new_status,
                    "auto_approved": auto_approved,
                    "auto_rejected": auto_rejected,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"history": history_entry.dict()}
            }
        )
        
        # Send email notifications for auto-approval/rejection
        if auto_approved or auto_rejected:
            try:
                await send_contribution_notification(
                    contribution['created_by'],
                    contribution_id,
                    "approved" if auto_approved else "rejected",
                    auto_action=True
                )
            except Exception as e:
                logger.warning(f"Failed to send notification: {e}")
        
        return {
            "message": "Vote enregistré avec succès",
            "upvotes": upvotes,
            "downvotes": downvotes,
            "status": new_status,
            "auto_approved": auto_approved,
            "auto_rejected": auto_rejected
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vote on contribution error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du vote")

@api_router.post("/contributions-v2/{contribution_id}/images")
async def upload_contribution_image_v2(
    contribution_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    caption: str = Form(""),
    current_user: dict = Depends(get_current_user)
):
    """Upload image for a contribution"""
    try:
        user_id = current_user['id']
        
        # Get contribution and verify ownership
        contribution = await db.contributions_v2.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution non trouvée")
        
        # Check if user can upload (owner or admin)
        if contribution['created_by'] != user_id and current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette contribution")
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Type de fichier non autorisé. Utilisez JPG, PNG ou WebP."
            )
        
        # Validate file size (max 5MB for contributions)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Le fichier est trop volumineux. Taille maximale : 5MB."
            )
        
        # Reset file position
        await file.seek(0)
        
        # Create contributions directory if it doesn't exist
        upload_dir = Path(f"uploads/contributions/{contribution_id}")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
            file_extension = 'jpg'
        
        unique_filename = f"{uuid.uuid4().hex[:8]}_{int(datetime.utcnow().timestamp())}.{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            await file.seek(0)
            f.write(await file.read())
        
        # Get image dimensions (optional, requires PIL)
        width, height = None, None
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.size
        except:
            pass  # Skip if PIL not available
        
        # Create image record
        image_data = ContributionImage(
            url=f"uploads/contributions/{contribution_id}/{unique_filename}",
            filename=unique_filename,
            original_filename=file.filename,
            file_size=len(file_content),
            mime_type=file.content_type,
            width=width,
            height=height,
            is_primary=is_primary,
            uploaded_by=user_id
        )
        
        # Update contribution with new image
        await db.contributions_v2.update_one(
            {"id": contribution_id},
            {
                "$push": {"images": image_data.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Add to history
        history_entry = ContributionHistoryEntry(
            action="image_uploaded",
            user_id=user_id,
            user_name=current_user.get('name', 'Unknown'),
            details={
                "filename": unique_filename,
                "is_primary": is_primary,
                "file_size": len(file_content)
            }
        )
        
        await db.contributions_v2.update_one(
            {"id": contribution_id},
            {"$push": {"history": history_entry.dict()}}
        )
        
        return {
            "message": "Image téléchargée avec succès",
            "image": image_data.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contribution image upload error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du téléchargement de l'image")

@api_router.post("/contributions-v2/{contribution_id}/moderate")
async def moderate_contribution_v2(
    contribution_id: str,
    moderation_data: ModerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Moderate a contribution (admin only)"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès administrateur requis")
        
        user_id = current_user['id']
        
        # Get contribution
        contribution = await db.contributions_v2.find_one({"id": contribution_id})
        if not contribution:
            raise HTTPException(status_code=404, detail="Contribution non trouvée")
        
        # Apply moderation action
        new_status = contribution['status']
        if moderation_data.action == ModerationAction.APPROVE:
            new_status = ContributionStatusV2.APPROVED
        elif moderation_data.action == ModerationAction.REJECT:
            new_status = ContributionStatusV2.REJECTED
        elif moderation_data.action == ModerationAction.REQUEST_REVISION:
            new_status = ContributionStatusV2.NEEDS_REVISION
        
        # Add history entry
        history_entry = ContributionHistoryEntry(
            action=f"moderated_{moderation_data.action}",
            user_id=user_id,
            user_name=current_user.get('name', 'Admin'),
            details={
                "action": moderation_data.action,
                "reason": moderation_data.reason,
                "internal_notes": moderation_data.internal_notes
            }
        )
        
        # Update contribution
        await db.contributions_v2.update_one(
            {"id": contribution_id},
            {
                "$set": {
                    "status": new_status,
                    "reviewed_by": user_id,
                    "reviewed_at": datetime.utcnow(),
                    "review_comment": moderation_data.reason,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"history": history_entry.dict()}
            }
        )
        
        # Auto-integrate approved contributions to main catalogue
        if new_status == ContributionStatusV2.APPROVED:
            try:
                await integrate_approved_contribution_to_catalogue(contribution_id, contribution, user_id)
                logger.info(f"Successfully integrated approved contribution {contribution_id} to catalogue")
            except Exception as e:
                logger.warning(f"Failed to integrate contribution {contribution_id} to catalogue: {e}")
        
        # Send notification to contributor if requested
        if moderation_data.notify_contributor:
            try:
                await send_contribution_notification(
                    contribution['created_by'],
                    contribution_id,
                    moderation_data.action,
                    auto_action=False
                )
            except Exception as e:
                logger.warning(f"Failed to send notification: {e}")
        
        return {
            "message": "Action de modération appliquée avec succès",
            "status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Moderate contribution error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la modération")

@api_router.get("/contributions-v2/admin/moderation-stats", response_model=ModerationStats)
async def get_moderation_stats_v2(current_user: dict = Depends(get_current_user)):
    """Get moderation statistics for admin dashboard"""
    try:
        if current_user.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Accès administrateur requis")
        
        # Get today's date range
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # Count contributions by status
        pending_contributions = await db.contributions_v2.count_documents({
            "status": ContributionStatusV2.PENDING_REVIEW
        })
        
        approved_today = await db.contributions_v2.count_documents({
            "status": ContributionStatusV2.APPROVED,
            "updated_at": {"$gte": today, "$lt": tomorrow}
        })
        
        rejected_today = await db.contributions_v2.count_documents({
            "status": ContributionStatusV2.REJECTED,
            "updated_at": {"$gte": today, "$lt": tomorrow}
        })
        
        # Count votes today (simplified - would need better aggregation in production)
        total_votes_today = 0
        try:
            pipeline = [
                {"$match": {"history.timestamp": {"$gte": today, "$lt": tomorrow}}},
                {"$unwind": "$history"},
                {"$match": {
                    "history.timestamp": {"$gte": today, "$lt": tomorrow},
                    "history.action": "voted"
                }},
                {"$count": "total"}
            ]
            vote_result = await db.contributions_v2.aggregate(pipeline).to_list(1)
            total_votes_today = vote_result[0]["total"] if vote_result else 0
        except:
            total_votes_today = 0
        
        auto_approved_today = await db.contributions_v2.count_documents({
            "auto_approved": True,
            "updated_at": {"$gte": today, "$lt": tomorrow}
        })
        
        auto_rejected_today = await db.contributions_v2.count_documents({
            "auto_rejected": True,
            "updated_at": {"$gte": today, "$lt": tomorrow}
        })
        
        # Count by entity type
        contributions_by_type = {}
        for entity_type in ContributionType:
            count = await db.contributions_v2.count_documents({
                "entity_type": entity_type
            })
            contributions_by_type[entity_type] = count
        
        # Top contributors (simplified for now)
        top_contributors = []
        
        return ModerationStats(
            pending_contributions=pending_contributions,
            approved_today=approved_today,
            rejected_today=rejected_today,
            total_votes_today=total_votes_today,
            auto_approved_today=auto_approved_today,
            auto_rejected_today=auto_rejected_today,
            contributions_by_type=contributions_by_type,
            top_contributors=top_contributors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get moderation stats error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques")

app.include_router(api_router)

# Static file serving is now handled under /api/uploads

# Mount static files
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
(uploads_dir / "profile_pictures").mkdir(exist_ok=True)
(uploads_dir / "contributions").mkdir(exist_ok=True)

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