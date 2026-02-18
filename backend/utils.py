import re
from datetime import datetime, timezone

MODERATOR_EMAILS = ["topkitfr@gmail.com"]
APPROVAL_THRESHOLD = 5
MODERATOR_APPROVAL_THRESHOLD = 1

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


# Estimation constants
ESTIMATION_BASE_PRICES = {"Authentic": 140, "Replica": 90, "Other": 60}
ESTIMATION_COMPETITION_COEFF = {
    "National Championship": 0.0,
    "National Cup": 0.05,
    "Continental Cup": 1.0,
    "Intercontinental Cup": 1.0,
    "World Cup": 1.0,
}
ESTIMATION_ORIGIN_COEFF = {"Club Stock": 0.5, "Match Prepared": 1.0, "Match Worn": 1.5, "Training": 0.0, "Shop": 0.0}
ESTIMATION_STATE_COEFF = {"New with tag": 0.3, "Very good": 0.1, "Used": 0.0, "Damaged": -0.2, "Needs restoration": -0.4}
ESTIMATION_FLOCKING_COEFF = {"Official": 0.15, "Personalized": 0.0}
ESTIMATION_SIGNED_COEFF = 1.5
ESTIMATION_SIGNED_PROOF_COEFF = 1.0
ESTIMATION_AGE_COEFF_PER_YEAR = 0.05
ESTIMATION_AGE_MAX = 1.0


def calculate_estimation(model_type: str, competition: str, condition_origin: str,
                         physical_state: str, flocking_origin: str,
                         signed: bool, signed_proof: bool, season_year: int):
    base = ESTIMATION_BASE_PRICES.get(model_type, 60)
    coeff_sum = 0.0
    breakdown = []

    comp_c = ESTIMATION_COMPETITION_COEFF.get(competition, 0.0)
    coeff_sum += comp_c
    if competition:
        breakdown.append({"label": f"Competition: {competition}", "coeff": comp_c})

    origin_c = ESTIMATION_ORIGIN_COEFF.get(condition_origin, 0.0)
    coeff_sum += origin_c
    if condition_origin:
        breakdown.append({"label": f"Origin: {condition_origin}", "coeff": origin_c})

    state_c = ESTIMATION_STATE_COEFF.get(physical_state, 0.0)
    coeff_sum += state_c
    if physical_state:
        breakdown.append({"label": f"State: {physical_state}", "coeff": state_c})

    flocking_c = ESTIMATION_FLOCKING_COEFF.get(flocking_origin, 0.0)
    coeff_sum += flocking_c
    if flocking_origin:
        breakdown.append({"label": f"Flocking: {flocking_origin}", "coeff": flocking_c})

    if signed:
        coeff_sum += ESTIMATION_SIGNED_COEFF
        breakdown.append({"label": "Signed", "coeff": ESTIMATION_SIGNED_COEFF})
        if signed_proof:
            coeff_sum += ESTIMATION_SIGNED_PROOF_COEFF
            breakdown.append({"label": "Proof/Certificate", "coeff": ESTIMATION_SIGNED_PROOF_COEFF})

    current_year = datetime.now(timezone.utc).year
    age = max(0, current_year - season_year) if season_year else 0
    age_c = min(age * ESTIMATION_AGE_COEFF_PER_YEAR, ESTIMATION_AGE_MAX)
    coeff_sum += age_c
    if age > 0:
        breakdown.append({"label": f"Age: {age} years", "coeff": round(age_c, 2)})

    estimated_price = round(base * (1 + coeff_sum), 2)
    return {
        "base_price": base,
        "model_type": model_type,
        "coeff_sum": round(coeff_sum, 2),
        "estimated_price": estimated_price,
        "breakdown": breakdown
    }
