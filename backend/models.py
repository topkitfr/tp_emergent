from pydantic import BaseModel, ConfigDict
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
    condition_origin: Optional[str] = ""
    physical_state: Optional[str] = ""
    size: Optional[str] = ""
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = False
    signed_by: Optional[str] = ""
    signed_proof: Optional[bool] = False
    condition: Optional[str] = ""
    printing: Optional[str] = ""


class CollectionUpdate(BaseModel):
    category: Optional[str] = None
    notes: Optional[str] = None
    flocking_type: Optional[str] = None
    flocking_origin: Optional[str] = None
    flocking_detail: Optional[str] = None
    condition_origin: Optional[str] = None
    physical_state: Optional[str] = None
    size: Optional[str] = None
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = None
    signed_by: Optional[str] = None
    signed_proof: Optional[bool] = None
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
    condition_origin: Optional[str] = ""
    physical_state: Optional[str] = ""
    size: Optional[str] = ""
    purchase_cost: Optional[float] = None
    estimated_price: Optional[float] = None
    price_estimate: Optional[float] = None
    value_estimate: Optional[float] = None
    signed: Optional[bool] = False
    signed_by: Optional[str] = ""
    signed_proof: Optional[bool] = False
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
    report_type: Optional[str] = "error"  # "error" or "removal"


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
    condition_origin: Optional[str] = ""
    physical_state: Optional[str] = ""
    flocking_origin: Optional[str] = ""
    signed: Optional[bool] = False
    signed_proof: Optional[bool] = False
    season_year: Optional[int] = 0


# Entity models

class TeamCreate(BaseModel):
    name: str
    country: Optional[str] = ""
    city: Optional[str] = ""
    founded: Optional[int] = None
    primary_color: Optional[str] = ""
    secondary_color: Optional[str] = ""
    crest_url: Optional[str] = ""
    aka: Optional[List[str]] = []


class TeamOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    team_id: str
    name: str
    slug: str
    country: Optional[str] = ""
    city: Optional[str] = ""
    founded: Optional[int] = None
    primary_color: Optional[str] = ""
    secondary_color: Optional[str] = ""
    crest_url: Optional[str] = ""
    aka: Optional[List[str]] = []
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LeagueCreate(BaseModel):
    name: str
    country_or_region: Optional[str] = ""
    level: Optional[str] = "domestic"
    organizer: Optional[str] = ""
    logo_url: Optional[str] = ""


class LeagueOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    league_id: str
    name: str
    slug: str
    country_or_region: Optional[str] = ""
    level: Optional[str] = "domestic"
    organizer: Optional[str] = ""
    logo_url: Optional[str] = ""
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
    name: str
    slug: str
    country: Optional[str] = ""
    founded: Optional[int] = None
    logo_url: Optional[str] = ""
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PlayerCreate(BaseModel):
    full_name: str
    nationality: Optional[str] = ""
    birth_year: Optional[int] = None
    positions: Optional[List[str]] = []
    preferred_number: Optional[int] = None
    photo_url: Optional[str] = ""


class PlayerOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    player_id: str
    full_name: str
    slug: str
    nationality: Optional[str] = ""
    birth_year: Optional[int] = None
    positions: Optional[List[str]] = []
    preferred_number: Optional[int] = None
    photo_url: Optional[str] = ""
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
