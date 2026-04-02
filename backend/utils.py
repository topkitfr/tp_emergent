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
#
# FORMULE : Prix estimé = Prix de base × (1 + Σ coefficients)
#
# Modes :
#   - "basic"    → Modèle + Compétition + État physique uniquement
#   - "advanced" → Tous les critères ci-dessous
#
# PRIX DE BASE
ESTIMATION_BASE_PRICES = {"Authentic": 140, "Replica": 90, "Other": 60}

# COMPÉTITION
# National Championship : 0 (base, pas de bonus)
# National Cup : +0.10
# Continental / Intercontinental / World Cup : +0.60
ESTIMATION_COMPETITION_COEFF = {
    "National Championship": 0.0,
    "National Cup": 0.10,
    "Continental Cup": 0.60,
    "Intercontinental Cup": 0.60,
    "World Cup": 0.60,
}

# ORIGINE (condition_origin)
# Shop / Training : 0 (standard)
# Club Stock : +0.40
# Match Prepared : +0.80
# Match Worn : +1.20
ESTIMATION_ORIGIN_COEFF = {
    "Shop": 0.0,
    "Training": 0.0,
    "Club Stock": 0.40,
    "Match Prepared": 0.80,
    "Match Worn": 1.20,
}

# ÉTAT PHYSIQUE
ESTIMATION_STATE_COEFF = {
    "New with tag": 0.30,
    "Very good": 0.15,
    "Used": 0.0,
    "Damaged": -0.30,
    "Needs restoration": -0.50,
}

# FLOCAGE
# "Official"     → flocage officiel club/compétition → +0.20
#                   → afficher le champ joueur flocqué côté UI
# "Personalized" → flocage perso → 0.0
#                   → NE PAS afficher le champ joueur côté UI
# "None"         → pas de flocage → 0.0
ESTIMATION_FLOCKING_COEFF = {"Official": 0.20, "Personalized": 0.0, "None": 0.0}

# PATCH OFFICIEL DE COMPÉTITION (bool)
ESTIMATION_PATCH_COEFF = 0.10

# SIGNATURE — type de signataire
# "player_flocked" : signé par le joueur dont le nom est flocqué → +0.80
# "team"           : signé par l'équipe (multi signatures) → +1.00
# "other"          : autre signature (préciser via signed_other_detail) → +0.40
ESTIMATION_SIGNED_TYPE_COEFF = {
    "player_flocked": 0.80,
    "team": 1.00,
    "other": 0.40,
}

# PREUVE / CERTIFICAT D'AUTHENTICITÉ
# "none"   : aucune preuve → 0 bonus supplémentaire
# "light"  : certificat léger / simple provenance → +0.20
# "strong" : preuve solide (photo/vidéo + COA crédible) → +0.40
ESTIMATION_SIGNED_PROOF_COEFF = {
    "none": 0.0,
    "light": 0.20,
    "strong": 0.40,
}

# RARETÉ (bool + texte libre rare_reason)
ESTIMATION_RARITY_COEFF = 0.40

# ANCIENNETÉ
# On ne commence à compter qu'à partir de 2 ans après l'année de saison
# (avant 2 ans, le maillot est encore facilement trouvable dans le commerce)
# +0.05 par année effective, plafonné à +1.0
# Exemple en 2026 :
#   saison 2024 → age=2 → effective=0 → coeff=0.00
#   saison 2018 → age=8 → effective=6 → coeff=0.30
#   saison 2000 → age=26 → effective=24 → coeff=1.00 (plafonné)
ESTIMATION_AGE_DELAY_YEARS = 2
ESTIMATION_AGE_COEFF_PER_YEAR = 0.05
ESTIMATION_AGE_MAX = 1.0

# PROFIL DU JOUEUR FLOCQUÉ
# Actif UNIQUEMENT quand : signed == True ET signed_type == "player_flocked" ET flocking_origin == "Official"
# "football_legend" : légende mondiale → +1.00
# "club_star"       : star / icône du club → +0.50
# "none"            : joueur lambda → 0.0
ESTIMATION_PLAYER_PROFILE_COEFF: dict[str, float] = {
    "football_legend": 1.00,
    "club_star": 0.50,
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
    signed_other_detail: str = "",
    patch: bool = False,
    is_rare: bool = False,
    rare_reason: str = "",
    mode: str = "advanced",
):
    """
    Calcule l'estimation du prix d'un maillot.

    mode="basic"    → uniquement Modèle + Compétition + État physique
    mode="advanced" → tous les critères

    Retourne un dict avec :
      - base_price     : prix de base selon le modèle
      - model_type     : type de modèle
      - coeff_sum      : somme totale des coefficients
      - estimated_price: prix final arrondi
      - breakdown      : liste de {label, coeff} pour l'affichage détaillé
      - mode           : "basic" ou "advanced"
    """
    base = ESTIMATION_BASE_PRICES.get(model_type, 60)
    coeff_sum = 0.0
    breakdown = []

    # ── Compétition (basic + advanced) ──
    comp_c = ESTIMATION_COMPETITION_COEFF.get(competition, 0.0)
    coeff_sum += comp_c
    if competition:
        breakdown.append({"label": f"Competition: {competition}", "coeff": comp_c})

    # ── État physique (basic + advanced) ──
    state_c = ESTIMATION_STATE_COEFF.get(physical_state, 0.0)
    coeff_sum += state_c
    if physical_state:
        breakdown.append({"label": f"State: {physical_state}", "coeff": state_c})

    # ── Champs avancés uniquement ──
    if mode == "advanced":

        # Origine
        origin_c = ESTIMATION_ORIGIN_COEFF.get(condition_origin, 0.0)
        coeff_sum += origin_c
        if condition_origin:
            breakdown.append({"label": f"Origin: {condition_origin}", "coeff": origin_c})

        # Flocage
        # "Official"     → +0.20 + afficher champ joueur côté UI
        # "Personalized" → 0.00 + NE PAS afficher champ joueur côté UI
        # "None"         → 0.00
        flocking_c = ESTIMATION_FLOCKING_COEFF.get(flocking_origin, 0.0)
        coeff_sum += flocking_c
        if flocking_origin and flocking_origin != "None":
            breakdown.append({"label": f"Flocking: {flocking_origin}", "coeff": flocking_c})

        # Patch officiel
        if patch:
            coeff_sum += ESTIMATION_PATCH_COEFF
            breakdown.append({"label": "Official competition patch", "coeff": ESTIMATION_PATCH_COEFF})

        # Signature
        if signed:
            signed_type_c = ESTIMATION_SIGNED_TYPE_COEFF.get(signed_type, 0.40)
            coeff_sum += signed_type_c
            type_labels = {
                "player_flocked": "Signed by flocked player",
                "team": "Signed by entire team",
                "other": f"Signed (other{': ' + signed_other_detail if signed_other_detail else ''})",
            }
            breakdown.append({"label": type_labels.get(signed_type, "Signed"), "coeff": signed_type_c})

            # Preuve / COA
            proof_c = ESTIMATION_SIGNED_PROOF_COEFF.get(signed_proof, 0.0)
            coeff_sum += proof_c
            if proof_c > 0:
                proof_labels = {
                    "light": "Certificate (light proof)",
                    "strong": "Certificate (strong proof + COA)",
                }
                breakdown.append({"label": proof_labels.get(signed_proof, "Certificate"), "coeff": proof_c})

            # Profil joueur — uniquement si signé par le joueur flocqué en officiel
            if signed_type == "player_flocked" and flocking_origin == "Official":
                profile_c = ESTIMATION_PLAYER_PROFILE_COEFF.get(flocking_player_profile or "none", 0.0)
                if profile_c > 0:
                    coeff_sum += profile_c
                    profile_labels = {
                        "football_legend": "Signed by flocked player: Football legend",
                        "club_star": "Signed by flocked player: Club star",
                    }
                    breakdown.append({
                        "label": profile_labels.get(flocking_player_profile, "Signed by flocked player profile"),
                        "coeff": profile_c,
                    })

        # Rareté
        if is_rare:
            coeff_sum += ESTIMATION_RARITY_COEFF
            rare_label = f"Rare shirt{': ' + rare_reason if rare_reason else ''}"
            breakdown.append({"label": rare_label, "coeff": ESTIMATION_RARITY_COEFF})

        # Ancienneté
        # Calcul : on part de l'année de saison, on déduit 2 ans de délai
        # avant que le maillot soit considéré difficile à trouver dans le commerce,
        # puis +0.05 par année effective, plafonné à +1.0
        current_year = datetime.now(timezone.utc).year
        age = max(0, current_year - season_year) if season_year else 0
        effective_age = max(0, age - ESTIMATION_AGE_DELAY_YEARS)
        age_c = min(effective_age * ESTIMATION_AGE_COEFF_PER_YEAR, ESTIMATION_AGE_MAX)
        coeff_sum += age_c
        if age_c > 0:
            breakdown.append({
                "label": f"Age: {age} years (effective: {effective_age} yrs)",
                "coeff": round(age_c, 2),
            })

    estimated_price = round(base * (1 + coeff_sum), 2)
    return {
        "base_price": base,
        "model_type": model_type,
        "coeff_sum": round(coeff_sum, 2),
        "estimated_price": estimated_price,
        "breakdown": breakdown,
        "mode": mode,
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
    signed_other_detail: str = "",
    patch: bool = False,
    is_rare: bool = False,
    rare_reason: str = "",
    mode: str = "advanced",
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
        signed_other_detail=signed_other_detail,
        patch=patch,
        is_rare=is_rare,
        rare_reason=rare_reason,
        mode=mode,
    )
