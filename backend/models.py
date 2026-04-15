from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional, Union


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
    # Sprint 1 — Club vs Nation
    entity_type: Optional[str] = "club"         # "club" | "nation"
    confederation_id: Optional[str] = None      # league_id d'une confédération, si entity_type = "nation"
    # Sprint 1 — Couleurs
    color: Optional[List[str]] = []             # ["red", "white", "blue"]


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
    # Sprint 1
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
    # Sprint 4 — lien compétition réelle (#15)
    competition_id: Optional[str] = None        # league_id de la collection leagues
    competition_name: Optional[str] = ""        # dénormalisé pour affichage rapide


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
    # Sprint 4
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
    """
    Requête d'estimation de prix d'un maillot.

    mode : "basic" | "advanced"
      - "basic"    : Modèle + Compétition + État physique uniquement
      - "advanced" : Tous les critères (origine, flocage, patch, signature, rareté, ancienneté)

    Option A — profil joueur automatique :
      Fournir flocking_player_id (player_id en DB) pour que la note du joueur
      soit récupérée automatiquement et convertie en coefficient.
      L'ancien champ flocking_player_profile est conservé pour compatibilité
      descendante mais ignoré si flocking_player_id est fourni.
    """
    model_type: str
    competition: Optional[str] = ""
    physical_state: Optional[str] = ""
    mode: Optional[str] = "advanced"
    condition_origin: Optional[str] = ""
    flocking_origin: Optional[str] = ""
    flocking_player_id: Optional[str] = ""       # Option A : player_id DB → note auto
    flocking_player_profile: Optional[str] = "none"  # Conservé pour rétrocompat (ignoré si player_id fourni)
    signed: Optional[bool] = False
    signed_type: Optional[str] = ""
    signed_other_detail: Optional[str] = ""
    signed_proof: Optional[str] = "none"
    season_year: Optional[int] = 0
    patch: Optional[bool] = False
    is_rare: Optional[bool] = False
    rare_reason: Optional[str] = ""


# ─── Team ─────────────────────────────────────────────────────────────────────

class TeamCreate(BaseModel):
    name: str
    country: Optional[str] = ""
    city: Optional[str] = ""
    founded: Optional[int] = None
    primary_color: Optional[str] = ""
    secondary_color: Optional[str] = ""
    crest_url: Optional[str] = ""
    aka: Optional[List[str]] = []
    # Sprint 2 — champs API-Football (#14)
    apifootball_team_id: Optional[int] = None   # team.id API-Football
    is_national: Optional[bool] = False          # team.national
    stadium_name: Optional[str] = ""            # venue.name
    stadium_capacity: Optional[int] = None      # venue.capacity
    stadium_surface: Optional[str] = ""         # venue.surface
    stadium_image_url: Optional[str] = ""       # venue.image


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
    # Sprint 2
    apifootball_team_id: Optional[int] = None
    is_national: Optional[bool] = False
    stadium_name: Optional[str] = ""
    stadium_capacity: Optional[int] = None
    stadium_surface: Optional[str] = ""
    stadium_image_url: Optional[str] = ""
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ─── League ───────────────────────────────────────────────────────────────────

class LeagueSeasonEntry(BaseModel):
    """Une saison d'une compétition (issues de API-Football /leagues?id=X)."""
    year: int                               # ex: 2024
    start: Optional[str] = None            # ex: "2024-08-16"
    end: Optional[str] = None              # ex: "2025-05-25"
    current: Optional[bool] = False        # saison en cours


class LeagueCreate(BaseModel):
    name: str
    country_or_region: Optional[str] = ""
    level: Optional[str] = "domestic"
    organizer: Optional[str] = ""
    logo_url: Optional[str] = ""
    # Champs API-Football
    apifootball_league_id: Optional[int] = None
    apifootball_logo: Optional[str] = ""
    scoring_weight: Optional[float] = None
    # Sprint 1 — normalisation domestic/international
    entity_type: Optional[str] = "league"   # "league" | "cup" | "confederation"
    scope: Optional[str] = None             # "domestic" | "international"
    region: Optional[str] = None            # "country" | "europe" | "world" | "africa" | ...
    country_name: Optional[str] = None      # seulement si scope = "domestic"
    country_code: Optional[str] = None
    country_flag: Optional[str] = None
    source_payload: Optional[dict] = None   # réponse brute API-Football pour re-sync
    # Phase 1 — enrichissement detail page
    gender: Optional[str] = None            # "male" | "female" — API-Football league.gender (via seasons endpoint)
    level_type: Optional[str] = None        # "League" | "Cup" | "Friendly" — API-Football league.type
    seasons: Optional[List[LeagueSeasonEntry]] = []  # liste des saisons issues de API-Football


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
    apifootball_league_id: Optional[int] = None
    apifootball_logo: Optional[str] = ""
    scoring_weight: Optional[float] = None
    # Sprint 1
    entity_type: Optional[str] = "league"
    scope: Optional[str] = None
    region: Optional[str] = None
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_flag: Optional[str] = None
    source_payload: Optional[dict] = None
    # Phase 1
    gender: Optional[str] = None
    level_type: Optional[str] = None
    seasons: Optional[List[dict]] = []
    kit_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ─── Brand ────────────────────────────────────────────────────────────────────

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


# ─── Award (trophée individuel) ───────────────────────────────────────────────

class AwardCreate(BaseModel):
    """Trophée individuel (Ballon d'Or, Golden Boot, FIFA Best…)"""
    name: str                              # ex: "Ballon d'Or"
    category: Optional[str] = "individual" # individual | collective
    scoring_weight: Optional[float] = 5.0  # poids dans score_palmares
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
    """Référence à un award dans le profil d'un joueur."""
    award_id: str          # référence à awards collection
    award_name: str        # dénormalisé pour affichage rapide
    year: Optional[str] = ""
    count: Optional[int] = 1


# ─── Player ───────────────────────────────────────────────────────────────────

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
    # Sprint 2 — champs API-Football (#10)
    apifootball_id: Optional[str] = ""
    firstname: Optional[str] = ""           # player.firstname
    lastname: Optional[str] = ""            # player.lastname
    birth_place: Optional[str] = ""         # player.birth.place
    birth_country: Optional[str] = ""       # player.birth.country
    height: Optional[str] = ""              # player.height (ex: "180 cm")
    weight: Optional[str] = ""              # player.weight (ex: "75 kg")
    # Scoring API-Football
    honours: Optional[List[dict]] = []
    individual_awards: Optional[List[IndividualAwardEntry]] = []
    score_palmares: Optional[float] = 0.0
    aura: Optional[float] = 0.0
    note: Optional[float] = 0.0
    # Phase 1 — enrichissement detail page
    gender: Optional[str] = None            # "male" | "female" — API-Football player.gender
    level: Optional[str] = None             # "Professional" | "Semi-Pro" | "Amateur" | "Youth"
    position_detail: Optional[str] = None   # poste précis enrichi (ex: "Centre-Back", "Goalkeeper")
    jersey_number: Optional[int] = None     # numéro de maillot actuel — API-Football statistics[0].games.number
    current_team_id: Optional[str] = None   # référence vers teams collection


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
    apifootball_id: Optional[str] = ""
    # Sprint 2
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
    # Phase 1
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


# ─── Scoring joueur (API-Football) ───────────────────────────────────────────

class PlayerScoringEnrichRequest(BaseModel):
    """Body pour enrichir/mettre à jour le scoring d'un joueur via API-Football."""
    player_id: str
    apifootball_id: Optional[Union[str, int]] = None
    aura: Optional[float] = 0.0


class PlayerScoringOut(BaseModel):
    """Réponse après enrichissement scoring."""
    model_config = ConfigDict(extra="ignore")
    player_id: str
    full_name: str
    apifootball_id: Optional[str] = ""

    @field_validator("apifootball_id", mode="before")
    @classmethod
    def coerce_apifootball_id(cls, v):
        return str(v) if v is not None else ""
    honours_count: int = 0
    score_palmares: float = 0.0
    aura: float = 0.0
    note: float = 0.0
    updated_at: Optional[str] = None
