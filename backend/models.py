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
    flocking_player_id: Optional[str] = ""
    # Profil du joueur flocqué : "legend" | "star" | "none"
    # "legend" = légende mondiale, "star" = star du club, "none" = joueur lambda / pas précisé
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
    # signed_proof: "none" | "light" | "strong"
    signed_proof: Optional[str] = "none"
    # signed_type: "player_flocked" | "team" | "other"
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
    """
    Requête d'estimation de prix d'un maillot.

    mode : "basic" | "advanced"
      - "basic"    : Modèle + Compétition + État physique uniquement
      - "advanced" : Tous les critères (origine, flocage, patch, signature, rareté, ancienneté)

    Logique flocage (côté UI) :
      - flocking_origin == "Official"     -> afficher le champ joueur flocqué
      - flocking_origin == "Personalized" -> NE PAS afficher le champ joueur
      - flocking_origin == "None"         -> rien

    Logique signature :
      - signed_type == "player_flocked" -> joueur dont le nom est flocqué
      - signed_type == "team"           -> toute l'équipe
      - signed_type == "other"          -> préciser via signed_other_detail
    """
    # Champs communs basic + advanced
    model_type: str
    competition: Optional[str] = ""
    physical_state: Optional[str] = ""

    # Champs advanced uniquement
    mode: Optional[str] = "advanced"          # "basic" | "advanced"
    condition_origin: Optional[str] = ""
    # Flocage : "Official" | "Personalized" | "None"
    flocking_origin: Optional[str] = ""
    # Profil du joueur flocqué (utilisé uniquement si signé par le joueur flocqué)
    # "football_legend" | "club_star" | "none"
    flocking_player_profile: Optional[str] = "none"
    signed: Optional[bool] = False
    # signed_type: "player_flocked" | "team" | "other"
    signed_type: Optional[str] = ""
    # Précision si signed_type == "other"
    signed_other_detail: Optional[str] = ""
    # signed_proof: "none" | "light" | "strong"
    signed_proof: Optional[str] = "none"
    # Année de début de saison (ex: 2018 pour la saison 2018/2019)
    season_year: Optional[int] = 0
    patch: Optional[bool] = False
    is_rare: Optional[bool] = False
    # Raison de la rareté (texte libre, affiché dans le breakdown)
    rare_reason: Optional[str] = ""


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
    status: Optional[str] = "approved"
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
    status: Optional[str] = "approved"
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
    birth_date: Optional[str] = ""
    birth_year: Optional[int] = None
    positions: Optional[List[str]] = []
    preferred_number: Optional[int] = None
    photo_url: Optional[str] = ""
    bio: Optional[str] = ""
    aura_level: Optional[int] = 1      # conservé pour compat DB, non utilisé dans l'estimation
    # --- Scoring TheSportsDB ---
    tsdb_id: Optional[str] = ""        # ID TheSportsDB pour enrichissement auto
    honours: Optional[List[dict]] = [] # Palmarès brut (lookuphonours)
    score_palmares: Optional[float] = 0.0
    aura: Optional[float] = 0.0        # 0–100, vote communautaire
    note: Optional[float] = 0.0        # score final calculé


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
    aura_level: Optional[int] = 1      # conservé pour compat DB, non utilisé dans l'estimation
    # --- Scoring TheSportsDB ---
    tsdb_id: Optional[str] = ""
    honours: Optional[List[dict]] = []
    score_palmares: Optional[float] = 0.0
    aura: Optional[float] = 0.0
    note: Optional[float] = 0.0
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


# ─── Scoring joueur (TheSportsDB) ────────────────────────────────────────────

class PlayerScoringEnrichRequest(BaseModel):
    """Body pour enrichir/mettre à jour le scoring d'un joueur via TheSportsDB."""
    player_id: str          # player_id Topkit (UUID stocké en Mongo)
    tsdb_id: str            # ID numérique TheSportsDB (ex: "34146212")
    aura: Optional[float] = 0.0  # 0–100


class PlayerScoringOut(BaseModel):
    """Réponse après enrichissement scoring."""
    model_config = ConfigDict(extra="ignore")
    player_id: str
    full_name: str
    tsdb_id: Optional[str] = ""
    honours_count: int = 0
    score_palmares: float = 0.0
    aura: float = 0.0
    note: float = 0.0
    updated_at: Optional[str] = None
