from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
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
import websockets
import asyncio
import re
from collections import defaultdict
import time
import random

# Import Stripe integration
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Import for 2FA
import pyotp
import qrcode
import io
import base64

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
    NEW = "new"
    NEAR_MINT = "near_mint"
    VERY_GOOD = "very_good"
    GOOD = "good"
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
    season: str
    player: Optional[str] = None
    size: Optional[JerseySize] = None  # Optional - specified when creating listings
    condition: Optional[JerseyCondition] = None  # Optional - specified when creating listings
    manufacturer: str
    home_away: str  # "home", "away", "third"
    league: str
    description: str
    images: List[str] = []
    reference_code: Optional[str] = None
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
    season: str
    player: Optional[str] = None
    size: Optional[str] = None  # Optional - will be specified when creating listings
    condition: Optional[str] = None  # Optional - will be specified when creating listings
    manufacturer: Optional[str] = ""
    home_away: Optional[str] = ""
    league: Optional[str] = ""
    description: Optional[str] = ""
    images: List[str] = []
    reference_code: Optional[str] = None

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
    message_type: str = "text"  # "text", "image", "file"

# Security helpers
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
        
        # Create reset link (in production, use your actual domain)
        reset_link = f"https://soccer-ui-fix.preview.emergentagent.com/reset-password?token={token}"
        
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
    
    # In production, send actual email here
    # For now, return the verification link in response (development only)
    verification_link = f"https://soccer-ui-fix.preview.emergentagent.com/verify-email?token={verification_token}"
    
    return {
        "message": "Compte créé avec succès! Veuillez vérifier votre email pour activer votre compte.",
        "user": {
            "id": user.id, 
            "email": user.email, 
            "name": user.name,
            "role": user_role,
            "email_verified": False
        },
        # Remove this in production - only for development
        "dev_verification_link": verification_link,
        "instructions": "Cliquez sur le lien de vérification envoyé à votre email pour activer votre compte."
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
    
    # In production, send actual email here
    verification_link = f"https://soccer-ui-fix.preview.emergentagent.com/verify-email?token={verification_token}"
    
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
        if user.get('account_locked_until') and datetime.fromisoformat(user['account_locked_until'].replace('Z', '+00:00')) > datetime.utcnow():
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
async def regenerate_backup_codes(verification_data: TwoFactorVerify, current_user: dict = Depends(get_current_user)):
    """Regenerate 2FA backup codes"""
    try:
        user_id = current_user['id']
        
        # Get user
        user = await db.users.find_one({"id": user_id})
        if not user.get('two_factor_enabled'):
            raise HTTPException(status_code=400, detail="2FA non activé")
        
        # Verify token
        if not verify_2fa_token(user['two_factor_secret'], verification_data.token):
            raise HTTPException(status_code=400, detail="Code d'authentification invalide")
        
        # Generate new backup codes
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

# Admin User Management Endpoints (Security Level 2)
@api_router.post("/admin/users/{user_id}/ban")
async def ban_user(user_id: str, ban_data: UserBan, current_user: dict = Depends(get_current_user_admin)):
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

@api_router.post("/auth/change-password")
async def change_password(request: PasswordChange, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Change password for authenticated user"""
    # Get current user
    current_user = await get_current_user(credentials)
    
    # Verify current password
    user = await db.users.find_one({"id": current_user["id"]})
    if not user or not verify_password(request.current_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    
    # Validate new password strength
    is_valid, message = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Check that new password is different from current
    if verify_password(request.new_password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit être différent de l'ancien")
    
    # Update password
    new_password_hash = hash_password(request.new_password)
    result = await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du mot de passe")
    
    # Log password change
    await log_user_activity(current_user["id"], "password_changed", None, {
        "change_time": datetime.utcnow().isoformat()
    })
    
    return {"message": "Mot de passe modifié avec succès"}

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

async def check_user_is_admin(user_id: str) -> bool:
    """Check if the current user is an admin (for restrictions)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        return False
    
    # Check both email and role
    return user["email"] == ADMIN_EMAIL or user.get("role") == "admin"

async def get_current_non_admin_user(user_id: str = Depends(get_current_user)):
    """Ensure current user is not an admin (for marketplace/collection restrictions)"""
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
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_id=related_id
    )
    
    await db.notifications.insert_one(notification.dict())
    return notification

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
    jersey_data: JerseyCreate,
    moderator_id: str = Depends(get_current_moderator_or_admin)
):
    """Edit a pending or needs_modification jersey"""
    
    # Verify jersey exists and can be edited (pending or needs_modification)
    existing_jersey = await db.jerseys.find_one({"id": jersey_id, "status": {"$in": ["pending", "needs_modification"]}})
    if not existing_jersey:
        raise HTTPException(status_code=404, detail="Jersey not found or cannot be edited")
    
    # Validate condition
    valid_conditions = ["new", "near_mint", "very_good", "good", "poor"]
    if jersey_data.condition not in valid_conditions:
        raise HTTPException(status_code=400, detail=f"Invalid condition: {jersey_data.condition}")
    
    # Validate size
    valid_sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    if jersey_data.size not in valid_sizes:
        raise HTTPException(status_code=400, detail=f"Invalid size: {jersey_data.size}")
    
    # Update jersey with edited data
    update_data = {
        "team": jersey_data.team,
        "season": jersey_data.season,
        "player": jersey_data.player,
        "size": jersey_data.size,
        "condition": jersey_data.condition,
        "manufacturer": jersey_data.manufacturer or "",
        "home_away": jersey_data.home_away or "home",
        "league": jersey_data.league or "",
        "description": jersey_data.description or "",
        "images": jersey_data.images or [],
        "reference_code": jersey_data.reference_code,
        "status": "pending",  # Reset to pending after edit
        "approved_by": None,
        "approved_at": None,
        "rejection_reason": None
    }
    
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
        message=f"Your jersey '{existing_jersey.get('team', '')} {existing_jersey.get('season', '')}' has been updated by a moderator and is now pending review again.",
        related_id=jersey_id
    )
    
    # Log activity
    await log_user_activity(moderator_id, "jersey_edited", jersey_id, {
        "jersey_name": f"{jersey_data.team} {jersey_data.season}",
        "original_team": existing_jersey.get("team"),
        "original_season": existing_jersey.get("season")
    })
    
    return {"message": "Jersey updated successfully"}

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

@api_router.post("/admin/users/{user_id}/make-moderator")
async def make_user_moderator(
    user_id: str,
    admin_id: str = Depends(get_current_admin)
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
        "user_id": admin_id,
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
    admin_id: str = Depends(get_current_admin)
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
        "user_id": admin_id,
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

@api_router.get("/admin/users")
async def get_all_users(
    role: Optional[str] = None,
    admin_id: str = Depends(get_current_admin)
):
    """Get all users with their roles (Admin only)"""
    
    # Build query filter
    query = {}
    if role and role in ["user", "moderator", "admin"]:
        query["role"] = role
    
    # Get users
    users_cursor = db.users.find(query).sort("created_at", -1)
    users = []
    
    async for user in users_cursor:
        users.append({
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "user"),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login"),
            "email_verified": user.get("email_verified", False)
        })
    
    return {"users": users}

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

@api_router.get("/admin/traffic-stats")
async def get_admin_traffic_stats(admin_id: str = Depends(get_current_admin)):
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
async def get_user_detailed_stats(user_id: str, admin_id: str = Depends(get_current_admin)):
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
@api_router.post("/jerseys", response_model=Jersey)
async def create_jersey(jersey_data: JerseyCreate, user_id: str = Depends(get_current_user), resubmission_id: Optional[str] = None):
    """Create a new jersey submission (pending approval) or resubmit with modifications"""
    try:
        print(f"🟡 Jersey submission received from user {user_id}")
        print(f"🟡 Jersey data: {jersey_data.dict()}")
        
        # Validate required fields
        if not jersey_data.team or not jersey_data.season:
            raise HTTPException(status_code=422, detail="Team and season are required")
        
        # Size and condition are now optional for catalog submissions
        # They will be specified when creating listings on the marketplace
        size_enum = None
        condition_enum = None
        
        if jersey_data.size:
            try:
                size_enum = JerseySize(jersey_data.size.upper())
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid size: {jersey_data.size}. Must be one of: XS, S, M, L, XL, XXL")
        
        if jersey_data.condition:
            try:
                condition_enum = JerseyCondition(jersey_data.condition.lower())
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid condition: {jersey_data.condition}. Must be one of: new, near_mint, very_good, good, poor")
        
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
        
        # Create jersey with validated data
        jersey = Jersey(
            team=jersey_data.team.strip(),
            season=jersey_data.season.strip(),
            player=jersey_data.player.strip() if jersey_data.player else None,
            size=size_enum if size_enum else None,  # Optional for catalog submissions
            condition=condition_enum if condition_enum else None,  # Optional for catalog submissions
            manufacturer=jersey_data.manufacturer.strip() if jersey_data.manufacturer else "",
            home_away=jersey_data.home_away.strip() if jersey_data.home_away else "",
            league=jersey_data.league.strip() if jersey_data.league else "",
            description=jersey_data.description.strip() if jersey_data.description else "",
            images=jersey_data.images or [],
            reference_code=jersey_data.reference_code.strip() if jersey_data.reference_code else None,
            reference_number=reference_number,
            created_by=user_id,
            submitted_by=user_id,
            status=JerseyStatus.PENDING  # Always start as pending for moderation
        )
        
        # Insert into database
        await db.jerseys.insert_one(jersey.dict())
        print(f"✅ Jersey created successfully with ID: {jersey.id}")
        
        # Handle resubmission logic
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
                "player": jersey.player,
                "reference_number": jersey.reference_number,
                "status": jersey.status
            })
            
            # Notification for new submission
            await create_notification(
                user_id=user_id,
                notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
                title="Jersey Submitted Successfully!",
                message=f"Thank you! Your jersey '{jersey.team} {jersey.season}' ({jersey.reference_number}) has been submitted and will be reviewed by our moderators.",
                related_id=jersey.id
            )
        
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

@api_router.get("/jerseys/approved", response_model=List[Dict])
async def get_approved_jerseys(
    team: Optional[str] = None,
    season: Optional[str] = None,
    league: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
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
async def get_my_owned_collection(user_id: str = Depends(get_current_non_admin_user)):
    """Get user's owned collection items available for listing"""
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
async def add_to_collection(collection_data: CollectionAdd, user_id: str = Depends(get_current_non_admin_user)):
    """Add jersey to collection with specific size/condition - restricted to non-admin users only"""
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

@api_router.post("/collections/remove")
async def remove_from_collection_post(collection_data: CollectionAdd, user_id: str = Depends(get_current_non_admin_user)):
    """Remove jersey from collection - restricted to non-admin users only"""
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
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if profile is private
        if user.get("profile_privacy", "public") == "private" and current_user_id != user_id:
            raise HTTPException(status_code=403, detail="This user's profile is private")
        
        # Get collection without valuations - fixed to exclude MongoDB ObjectId
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
            {"$unwind": {"path": "$jersey", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "id": 1,
                    "collection_type": 1,
                    "added_at": 1,
                    "user_id": 1,
                    "jersey_id": 1,
                    "jersey": {
                        "id": "$jersey.id",
                        "team": "$jersey.team",
                        "season": "$jersey.season",
                        "player": "$jersey.player",
                        "league": "$jersey.league",
                        "manufacturer": "$jersey.manufacturer",
                        "images": "$jersey.images",
                        "status": "$jersey.status"
                    },
                    "_id": 0  # Exclude MongoDB ObjectId to prevent serialization errors
                }
            }
        ]
        
        collections = await db.collections.aggregate(pipeline).to_list(1000)
        
        # Remove valuation data for privacy (already excluded in projection)
        for collection in collections:
            collection.pop('valuation', None)
        
        return {
            "user_id": user_id,
            "profile_owner": current_user_id == user_id,
            "collections": collections
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user collections: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    user_id: str = Depends(get_current_user)
):
    """Send a friend request"""
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
    requester = await db.users.find_one({"id": user_id})
    requester_name = requester.get("name", "Someone") if requester else "Someone"
    
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
    user_id: str = Depends(get_current_user)
):
    """Accept or decline a friend request"""
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
async def get_friends(user_id: str = Depends(get_current_user)):
    """Get user's friends list and pending requests"""
    
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

# Messaging System API Endpoints  
@api_router.post("/conversations")
async def create_conversation(
    message_data: MessageCreateV2,
    user_id: str = Depends(get_current_user)
):
    """Create a new conversation or add message to existing conversation"""
    
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
    admin_id: str = Depends(get_current_admin)
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
        "user_id": admin_id,
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
    user_id: str = Depends(get_current_user)
):
    """Update site mode (admin only)"""
    
    # Check if user is admin
    user = await db.users.find_one({"id": user_id})
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
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
                "updated_by": user_id,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    # Log the change
    await log_user_activity(user_id, "site_mode_changed", "", {
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
        
        # Log the activity
        await log_user_activity("system", "beta_access_requested", request.email, {
            "name": f"{request.first_name} {request.last_name}",
            "email": request.email,
            "message": request.message or "No message"
        })
        
        return BetaAccessResponse(
            message="Demande d'accès soumise avec succès ! Nous examinerons votre demande et vous contacterons bientôt.",
            request_id=access_request["id"]
        )
        
    except Exception as e:
        logger.error(f"Error submitting beta access request: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la soumission de la demande")

@api_router.get("/admin/beta/requests")
async def get_beta_access_requests(
    user_id: str = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 50
):
    """Get beta access requests (admin only)"""
    
    # Check if user is admin
    user = await db.users.find_one({"id": user_id})
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
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
    user_id: str = Depends(get_current_user)
):
    """Approve a beta access request and grant access to user (admin only)"""
    
    # Check if user is admin
    admin_user = await db.users.find_one({"id": user_id})
    if not admin_user or admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
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
                        "beta_granted_by": user_id
                    }
                }
            )
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
                beta_granted_by=user_id
            )
            
            await db.users.insert_one(new_user.dict())
            
            # TODO: Send welcome email with temporary password
            logger.info(f"Created beta user: {access_request['email']} with temp password: {temp_password}")
        
        # Update request status
        await db.beta_access_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": "approved",
                    "processed_at": datetime.utcnow(),
                    "processed_by": user_id
                }
            }
        )
        
        # Log activity
        await log_user_activity(user_id, "beta_access_approved", access_request["email"], {
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
    user_id: str = Depends(get_current_user)
):
    """Reject a beta access request (admin only)"""
    
    # Check if user is admin
    admin_user = await db.users.find_one({"id": user_id})
    if not admin_user or admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé - Admin requis")
    
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
                "processed_by": user_id
            }
        }
    )
    
    # Log activity
    await log_user_activity(user_id, "beta_access_rejected", access_request["email"], {
        "request_id": request_id,
        "user_name": f"{access_request['first_name']} {access_request['last_name']}",
        "user_email": access_request["email"],
        "reason": reject_data.reason
    })
    
    return {
        "message": f"Demande d'accès de {access_request['first_name']} {access_request['last_name']} rejetée",
        "reason": reject_data.reason
    }

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