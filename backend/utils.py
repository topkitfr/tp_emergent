import os
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException

from .database import db, client


# ─── Rôles ────────────────────────────────────────────────────────────────────
MODERATOR_EMAILS: list[str] = [
    e.strip()
    for e in os.getenv("MODERATOR_EMAILS", "topkitfr@gmail.com,dev@topkit.fr,steinmetzolivier@gmail.com").split(",")
    if e.strip()
]

ADMIN_EMAILS: list[str] = [
    e.strip()
    for e in os.getenv("ADMIN_EMAILS", "").split(",")
    if e.strip()
]

# ─── Vote ────────────────────────────────────────────────────────────────────
APPROVAL_THRESHOLD: int = int(os.getenv("APPROVAL_THRESHOLD", "5"))
MODERATOR_APPROVAL_THRESHOLD: int = 1

# ─── Uploads ─────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ─── Maintenance ─────────────────────────────────────────────────────────────
MAINTENANCE_MODE: bool = os.getenv("MAINTENANCE_MODE", "false").lower() == "true"

# ─── Quotas soumissions (par user, par 24h) ──────────────────────────────────
QUOTA_PER_TYPE: dict[str, int] = {
    "master_kit": int(os.getenv("QUOTA_MASTER_KIT", "10")),
    "version":    int(os.getenv("QUOTA_VERSION",    "20")),
    "team":       int(os.getenv("QUOTA_ENTITY",     "15")),
    "league":     int(os.getenv("QUOTA_ENTITY",     "15")),
    "brand":      int(os.getenv("QUOTA_ENTITY",     "15")),
    "player":     int(os.getenv("QUOTA_ENTITY",     "15")),
    "sponsor":    int(os.getenv("QUOTA_ENTITY",     "15")),
}


# ─── Slug ─────────────────────────────────────────────────────────────────────
def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


# ─── Normalisation saison ─────────────────────────────────────────────────────
def normalize_season(raw: str) -> str:
    if not raw:
        return raw
    raw = raw.strip()
    parts = re.split(r"[\-\./ ]+", raw)
    if len(parts) == 2:
        y1, y2 = parts
        if len(y1) == 2:
            y1 = "20" + y1
        if len(y2) == 2:
            y2 = "20" + y2
        try:
            return f"{int(y1)}/{int(y2)}"
        except ValueError:
            return raw
    elif len(parts) == 1:
        try:
            y = int(parts[0])
            return f"{y}/{y + 1}"
        except ValueError:
            return raw
    return raw


# ─── Teams ─────────────────────────────────────────────────────────────────────
async def get_or_create_team_by_name(name: str) -> str:
    if not name:
        raise ValueError("Team name is required")
    existing = await db.teams.find_one({"name": name}, {"_id": 0, "team_id": 1})
    if existing and existing.get("team_id"):
        return existing["team_id"]
    now = datetime.now(timezone.utc).isoformat()
    team_id = f"team_{uuid.uuid4().hex[:12]}"
    await db.teams.insert_one({
        "team_id": team_id, "name": name, "slug": slugify(name),
        "country": "", "city": "", "founded": None,
        "primary_color": "", "secondary_color": "",
        "crest_url": "", "aka": [], "kit_count": 0,
        "created_at": now, "updated_at": now,
    })
    return team_id


# ─── Quota check ───────────────────────────────────────────────────────────────
async def check_user_quota(db, user_id: str, sub_type: str) -> None:
    limit = QUOTA_PER_TYPE.get(sub_type)
    if not limit:
        return
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    count = await db.submissions.count_documents({
        "submitted_by": user_id,
        "submission_type": sub_type,
        "created_at": {"$gte": since},
    })
    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Quota dépassé : max {limit} soumissions de type '{sub_type}' par 24h."
        )


# ─── Estimation ──────────────────────────────────────────────────────────────────

ESTIMATION_BASE_PRICES = {"Authentic": 140, "Replica": 90, "Other": 60}

ESTIMATION_COMPETITION_COEFF = {
    "National Championship": 0.0,
    "National Cup": 0.10,
    "Continental Cup": 0.60,
    "Intercontinental Cup": 0.60,
    "World Cup": 0.60,
}

ESTIMATION_ORIGIN_COEFF = {
    "Shop": 0.0,
    "Training": 0.0,
    "Club Stock": 0.40,
    "Match Prepared": 0.80,
    "Match Worn": 1.20,
}

ESTIMATION_STATE_COEFF = {
    "New with tag": 0.30,
    "Very good": 0.15,
    "Used": 0.0,
    "Damaged": -0.30,
    "Needs restoration": -0.50,
}

ESTIMATION_FLOCKING_COEFF = {"Official": 0.20, "Personalized": 0.0, "None": 0.0}

ESTIMATION_PATCH_COEFF = 0.10

ESTIMATION_SIGNED_TYPE_COEFF = {
    "player_flocked": 0.80,
    "team": 1.00,
    "other": 0.40,
}

ESTIMATION_SIGNED_PROOF_COEFF = {
    "none": 0.0,
    "light": 0.20,
    "strong": 0.40,
}

ESTIMATION_RARITY_COEFF = 0.40

ESTIMATION_AGE_DELAY_YEARS = 2
ESTIMATION_AGE_COEFF_PER_YEAR = 0.05
ESTIMATION_AGE_MAX = 1.0

# Profil du joueur flocqué — appliqué dès que flocking_origin == "Official",
# qu'il soit signé ou non. Bonus supplémentaire si signé par le joueur.
# Enum : "legend" | "star" | "none"
ESTIMATION_PLAYER_PROFILE_COEFF: dict[str, float] = {
    "legend": 0.60,   # Légende du foot (Pelé, Maradona, Zidane, Ronaldo, Messi…)
    "star": 0.25,     # Star du club / icône de l'histoire du club
    "none": 0.0,      # Joueur lambda / non précisé
}

# Bonus supplémentaire si le maillot est aussi signé PAR le joueur flocqué
ESTIMATION_PLAYER_PROFILE_SIGNED_BONUS: dict[str, float] = {
    "legend": 0.40,   # signature d'une légende = valeur encore plus importante
    "star": 0.20,
    "none": 0.0,
}


def calculate_estimation(
    model_type: str,
    competition: str,
    condition_origin: str,
    physical_state: str,
    flocking_origin: str,
    signed: bool,
    signed_proof: str,
    season_year: int,
    flocking_player_profile: str = "none",
    signed_type: str = "",
    patch: bool = False,
    is_rare: bool = False,
):
    base = ESTIMATION_BASE_PRICES.get(model_type, 60)
    coeff_sum = 0.0
    breakdown = []

    # Competition
    comp_c = ESTIMATION_COMPETITION_COEFF.get(competition, 0.0)
    coeff_sum += comp_c
    if competition:
        breakdown.append({"label": f"Competition: {competition}", "coeff": comp_c})

    # Origine
    origin_c = ESTIMATION_ORIGIN_COEFF.get(condition_origin, 0.0)
    coeff_sum += origin_c
    if condition_origin:
        breakdown.append({"label": f"Origin: {condition_origin}", "coeff": origin_c})

    # État physique
    state_c = ESTIMATION_STATE_COEFF.get(physical_state, 0.0)
    coeff_sum += state_c
    if physical_state:
        breakdown.append({"label": f"State: {physical_state}", "coeff": state_c})

    # Flocage
    flocking_c = ESTIMATION_FLOCKING_COEFF.get(flocking_origin, 0.0)
    coeff_sum += flocking_c
    if flocking_origin and flocking_origin != "None":
        breakdown.append({"label": f"Flocking: {flocking_origin}", "coeff": flocking_c})

    # Profil joueur flocqué — actif dès que flocage officiel, sans condition de signature
    if flocking_origin == "Official":
        profile_c = ESTIMATION_PLAYER_PROFILE_COEFF.get(flocking_player_profile or "none", 0.0)
        if profile_c > 0:
            coeff_sum += profile_c
            profile_labels = {
                "legend": "Flocked player: Legend",
                "star": "Flocked player: Club star",
            }
            breakdown.append({
                "label": profile_labels.get(flocking_player_profile, "Flocked player profile"),
                "coeff": profile_c,
            })

    # Patch
    if patch:
        coeff_sum += ESTIMATION_PATCH_COEFF
        breakdown.append({"label": "Official competition patch", "coeff": ESTIMATION_PATCH_COEFF})

    # Signature
    if signed:
        signed_type_c = ESTIMATION_SIGNED_TYPE_COEFF.get(signed_type, 0.40)
        coeff_sum += signed_type_c
        type_labels = {
            "player_flocked": "Signed by flocked player",
            "team": "Signed by team",
            "other": "Signed (other)",
        }
        breakdown.append({"label": type_labels.get(signed_type, "Signed"), "coeff": signed_type_c})

        proof_c = ESTIMATION_SIGNED_PROOF_COEFF.get(signed_proof, 0.0)
        coeff_sum += proof_c
        if proof_c > 0:
            proof_labels = {"light": "Certificate (light proof)", "strong": "Certificate (strong proof + COA)"}
            breakdown.append({"label": proof_labels.get(signed_proof, "Certificate"), "coeff": proof_c})

        # Bonus supplémentaire si signé par le joueur flocqué lui-même
        if signed_type == "player_flocked" and flocking_origin == "Official":
            bonus_c = ESTIMATION_PLAYER_PROFILE_SIGNED_BONUS.get(flocking_player_profile or "none", 0.0)
            if bonus_c > 0:
                coeff_sum += bonus_c
                bonus_labels = {
                    "legend": "Signed by flocked legend (bonus)",
                    "star": "Signed by flocked club star (bonus)",
                }
                breakdown.append({
                    "label": bonus_labels.get(flocking_player_profile, "Signed by flocked player (bonus)"),
                    "coeff": bonus_c,
                })

    # Rareté
    if is_rare:
        coeff_sum += ESTIMATION_RARITY_COEFF
        breakdown.append({"label": "Rare shirt", "coeff": ESTIMATION_RARITY_COEFF})

    # Ancienneté
    current_year = datetime.now(timezone.utc).year
    age = max(0, current_year - season_year) if season_year else 0
    effective_age = max(0, age - ESTIMATION_AGE_DELAY_YEARS)
    age_c = min(effective_age * ESTIMATION_AGE_COEFF_PER_YEAR, ESTIMATION_AGE_MAX)
    coeff_sum += age_c
    if age_c > 0:
        breakdown.append({"label": f"Age: {age} years (+{effective_age} effective)", "coeff": round(age_c, 2)})

    estimated_price = round(base * (1 + coeff_sum), 2)
    return {
        "base_price": base,
        "model_type": model_type,
        "coeff_sum": round(coeff_sum, 2),
        "estimated_price": estimated_price,
        "breakdown": breakdown,
    }


def calculate_estimation_for_collection_item(
    model_type: str,
    competition: str,
    condition_origin: str,
    physical_state: str,
    flocking_origin: str,
    signed: bool,
    signed_proof: str,
    season_year: int,
    flocking_player_profile: str = "none",
    signed_type: str = "",
    patch: bool = False,
    is_rare: bool = False,
):
    return calculate_estimation(
        model_type=model_type,
        competition=competition,
        condition_origin=condition_origin,
        physical_state=physical_state,
        flocking_origin=flocking_origin,
        signed=signed,
        signed_proof=signed_proof,
        season_year=season_year,
        flocking_player_profile=flocking_player_profile,
        signed_type=signed_type,
        patch=patch,
        is_rare=is_rare,
    )
