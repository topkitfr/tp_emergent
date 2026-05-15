from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    role: Optional[str] = "user"
    created_at: Optional[str] = None


class MasterKitCreate(BaseModel):
    club: str
    season: str
    kit_type: str
    brand: str
    front_photo: str
    league: Optional[str] = ""
    design: Optional[str] = ""
    sponsor: Optional[str] = ""
    gender: Optional[str] = ""
    team_id: Optional[str] = ""
    league_id: Optional[str] = ""
    brand_id: Optional[str] = ""
    sponsor_id: Optional[str] = ""
    entity_type: Optional[str] = "club"
    confederation_id: Optional[str] = None
    color: Optional[List[str]] = []


class MasterKitOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    kit_id: str
    club: str
    season: str
    kit_type: str
    brand: str
    front_photo: str
    league: Optional[str] = ""
    design: Optional[str] = ""
    sponsor: Optional[str] = ""
    gender: Optional[str] = ""
    team_id: Optional[str] = ""
    league_id: Optional[str] = ""
    brand_id: Optional[str] = ""
    sponsor_id: Optional[str] = ""
    entity_type: Optional[str] = "club"
    confederation_id: Optional[str] = None
    color: Optional[List[str]] = []
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    version_count: Optional[int] = 0
    avg_rating: Optional[float] = 0.0


class VersionCreate(BaseModel):
    kit_id: str
    competition: str
    model: str
    sku_code: Optional[str] = ""
    ean_code: Optional[str] = ""
    front_photo: Optional[str] = ""
    back_photo: Optional[str] = ""
    main_player_id: Optional[str] = ""
    competition_id: Optional[str] = None
    competition_name: Optional[str] = ""


class VersionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    version_id: str
    kit_id: str
    competition: str
    model: str
    sku_code: Optional[str] = ""
    ean_code: Optional[str] = ""
    front_photo: Optional[str] = ""
    back_photo: Optional[str] = ""
    main_player_id: Optional[str] = ""
    competition_id: Optional[str] = None
    competition_name: Optional[str] = ""
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    avg_rating: Optional[float] = 0.0
    review_count: Optional[int] = 0


class CollectionAdd(BaseModel):
    version_id: str
    category: Optional[str] = "General"
    notes: Optional[str] = ""
    flocking_type: Optional[str] = ""
    flocking_origin: Optional[str] = ""
    flocking_detail: Optional[str] = ""
    flocking_player_id: Optional[str] = ""
    flocking_player_profile: Optional[str] = "none"
    condition_origin: Optional[str] = ""
    physical_state: Optional[str] = ""
    size: Optional[str] = ""
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = False
    signed_by: Optional[str] = ""
    signed_by_player_id: Optional[str] = ""
    signed_proof: Optional[str] = "none"
    signed_type: Optional[str] = ""
    signed_other_detail: Optional[str] = ""
    patch: Optional[bool] = False
    is_rare: Optional[bool] = False
    rare_reason: Optional[str] = ""
    condition: Optional[str] = ""
    printing: Optional[str] = ""


class CollectionUpdate(BaseModel):
    category: Optional[str] = None
    notes: Optional[str] = None
    flocking_type: Optional[str] = None
    flocking_origin: Optional[str] = None
    flocking_detail: Optional[str] = None
    flocking_player_id: Optional[str] = None
    flocking_player_profile: Optional[str] = None
    condition_origin: Optional[str] = None
    physical_state: Optional[str] = None
    size: Optional[str] = None
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = None
    signed_by: Optional[str] = None
    signed_by_player_id: Optional[str] = None
    signed_proof: Optional[str] = None
    signed_type: Optional[str] = None
    signed_other_detail: Optional[str] = None
    patch: Optional[bool] = None
    is_rare: Optional[bool] = None
    rare_reason: Optional[str] = None
    condition: Optional[str] = None
    printing: Optional[str] = None


class CollectionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    collection_id: str
    user_id: str
    version_id: str
    category: str
    notes: Optional[str] = ""
    flocking_type: Optional[str] = ""
    flocking_origin: Optional[str] = ""
    flocking_detail: Optional[str] = ""
    flocking_player_id: Optional[str] = ""
    flocking_player_profile: Optional[str] = "none"
    condition_origin: Optional[str] = ""
    physical_state: Optional[str] = ""
    size: Optional[str] = ""
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = False
    signed_by: Optional[str] = ""
    signed_by_player_id: Optional[str] = ""
    signed_proof: Optional[str] = "none"
    signed_type: Optional[str] = ""
    signed_other_detail: Optional[str] = ""
    patch: Optional[bool] = False
    is_rare: Optional[bool] = False
    rare_reason: Optional[str] = ""
    condition: Optional[str] = ""
    printing: Optional[str] = ""
    added_at: Optional[str] = None


class ReviewCreate(BaseModel):
    version_id: str
    rating: int
    comment: Optional[str] = ""


class ReviewOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    review_id: str
    version_id: str
    user_id: str
    user_name: Optional[str] = ""
    user_picture: Optional[str] = ""
    rating: int
    comment: Optional[str] = ""
    created_at: Optional[str] = None


class SubmissionCreate(BaseModel):
    submission_type: str
    data: dict


class VoteCreate(BaseModel):
    vote: str


class ReportCreate(BaseModel):
    target_type: str
    target_id: str
    corrections: dict = {}
    notes: Optional[str] = ""
    report_type: Optional[str] = "error"


class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    description: Optional[str] = None
    collection_privacy: Optional[str] = None
    profile_picture: Optional[str] = None


class WishlistAdd(BaseModel):
    version_id: str
    notes: Optional[str] = ""


class EstimationRequest(BaseModel):
    model_type: str
    competition: Optional[str] = ""
    physical_state: Optional[str] = ""
    mode: Optional[str] = "advanced"
    condition_origin: Optional[str] = ""
    flocking_origin: Optional[str] = ""
    flocking_player_id: Optional[str] = ""
    flocking_player_profile: Optional[str] = "none"
    signed: Optional[bool] = False
    signed_type: Optional[str] = ""
    signed_other_detail: Optional[str] = ""
    signed_personal_message: Optional[bool] = False
    signed_proof: Optional[str] = "none"
    season_year: Optional[int] = 0
    patch: Optional[bool] = False
    is_rare: Optional[bool] = False
    rare_reason: Optional[str] = ""


class TeamCreate(BaseModel):
    name: str
    country: Optional[str] = ""
    city: Optional[str] = ""
    founded: Optional[int] = None
    primary_color: Optional[str] = ""
    secondary_color: Optional[str] = ""
    crest_url: Optional[str] = ""
    aka: Optional[List[str]] = []
    is_national: Optional[bool] = False
    stadium_name: Optional[str] = ""
    stadium_capacity: Optional[int] = None
    stadium_surface: Optional[str] = ""
    stadium_image_url: Optional[str] = ""


class TeamOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    team_id: str
    status: Optional[str] = "approved"
    name: str
    slug: str
    country: Optional[str] = ""
    city: Optional[str] = ""
    founded: Optional[int] = None
    primary_color: Optional[str] = ""
    secondary_color: Optional[str] = ""
    crest_url: Optional[str] = ""
    aka: Optional[List[str]] = []
    is_national: Optional[bool] = False
    stadium_name: Optional[str] = ""
    stadium_capacity: Optional[int] = None
    stadium_surface: Optional[str] = ""
    stadium_image_url: Optional[str] = ""
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LeagueSeasonEntry(BaseModel):
    year: int
    start: Optional[str] = None
    end: Optional[str] = None
    current: Optional[bool] = False


class LeagueCreate(BaseModel):
    name: str
    country_or_region: Optional[str] = ""
    level: Optional[str] = "domestic"
    organizer: Optional[str] = ""
    logo_url: Optional[str] = ""
    scoring_weight: Optional[float] = None
    entity_type: Optional[str] = "league"
    scope: Optional[str] = None
    region: Optional[str] = None
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_flag: Optional[str] = None
    gender: Optional[str] = None
    level_type: Optional[str] = None
    seasons: Optional[List[LeagueSeasonEntry]] = []


class LeagueOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    league_id: str
    status: Optional[str] = "approved"
    name: str
    slug: str
    country_or_region: Optional[str] = ""
    level: Optional[str] = "domestic"
    organizer: Optional[str] = ""
    logo_url: Optional[str] = ""
    scoring_weight: Optional[float] = None
    entity_type: Optional[str] = "league"
    scope: Optional[str] = None
    region: Optional[str] = None
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_flag: Optional[str] = None
    gender: Optional[str] = None
    level_type: Optional[str] = None
    seasons: Optional[List[dict]] = []
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class BrandCreate(BaseModel):
    name: str
    country: Optional[str] = ""
    founded: Optional[int] = None
    logo_url: Optional[str] = ""


class BrandOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    brand_id: str
    status: Optional[str] = "approved"
    name: str
    slug: str
    country: Optional[str] = ""
    founded: Optional[int] = None
    logo_url: Optional[str] = ""
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AwardCreate(BaseModel):
    name: str
    category: Optional[str] = "individual"
    scoring_weight: Optional[float] = 5.0
    logo_url: Optional[str] = ""
    description: Optional[str] = ""


class AwardOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    award_id: str
    name: str
    category: Optional[str] = "individual"
    scoring_weight: Optional[float] = 5.0
    logo_url: Optional[str] = ""
    description: Optional[str] = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class IndividualAwardEntry(BaseModel):
    award_id: str
    award_name: str
    year: Optional[str] = ""
    count: Optional[int] = 1


class PlayerCreate(BaseModel):
    full_name: str
    nationality: Optional[str] = ""
    birth_date: Optional[str] = ""
    birth_year: Optional[int] = None
    positions: Optional[List[str]] = []
    preferred_number: Optional[int] = None
    photo_url: Optional[str] = ""
    bio: Optional[str] = ""
    aura_level: Optional[int] = 1
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    birth_place: Optional[str] = ""
    birth_country: Optional[str] = ""
    height: Optional[str] = ""
    weight: Optional[str] = ""
    honours: Optional[List[dict]] = []
    individual_awards: Optional[List[IndividualAwardEntry]] = []
    score_palmares: Optional[float] = 0.0
    aura: Optional[float] = 0.0
    note: Optional[float] = 0.0
    gender: Optional[str] = None
    level: Optional[str] = None
    position_detail: Optional[str] = None
    jersey_number: Optional[int] = None
    current_team_id: Optional[str] = None


class PlayerOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    status: Optional[str] = "approved"
    full_name: str
    slug: Optional[str] = ""
    nationality: Optional[str] = ""
    birth_date: Optional[str] = ""
    birth_year: Optional[int] = None
    positions: Optional[List[str]] = []
    preferred_number: Optional[int] = None
    photo_url: Optional[str] = ""
    bio: Optional[str] = ""
    aura_level: Optional[int] = 1
    firstname: Optional[str] = ""
    lastname: Optional[str] = ""
    birth_place: Optional[str] = ""
    birth_country: Optional[str] = ""
    height: Optional[str] = ""
    weight: Optional[str] = ""
    honours: Optional[List[dict]] = []
    individual_awards: Optional[List[dict]] = []
    score_palmares: Optional[float] = 0.0
    aura: Optional[float] = 0.0
    note: Optional[float] = 0.0
    gender: Optional[str] = None
    level: Optional[str] = None
    position_detail: Optional[str] = None
    jersey_number: Optional[int] = None
    current_team_id: Optional[str] = None
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @field_validator("positions", mode="before")
    @classmethod
    def coerce_positions(cls, v):
        if v is None or v == "":
            return []
        if isinstance(v, list):
            return v
        return [v]


# ─── Marketplace ────────────────────────────────────────────────────────────

class ListingCreate(BaseModel):
    collection_id: str
    listing_type: str  # "sale" | "trade" | "both"
    asking_price: Optional[float] = None
    trade_for: Optional[str] = None

class ListingOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    listing_id: str
    collection_id: str
    user_id: str
    version_id: str
    listing_type: str
    asking_price: Optional[float] = None
    trade_for: Optional[str] = None
    condition_summary: Optional[str] = None
    estimated_price: Optional[float] = None
    status: str
    created_at: str
    updated_at: str

class OfferCreate(BaseModel):
    offer_type: str  # "buy" | "trade" | "buy_and_trade"
    offered_price: Optional[float] = None
    offered_collection_id: Optional[str] = None
    message: Optional[str] = None

class OfferOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    offer_id: str
    listing_id: str
    offerer_id: str
    offer_type: str
    offered_price: Optional[float] = None
    offered_collection_id: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: str


class PlayerScoringOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    full_name: str
    honours_count: int = 0
    score_palmares: float = 0.0
    aura: float = 0.0
    note: float = 0.0
    note_breakdown: Optional[dict] = None
    updated_at: Optional[str] = None
