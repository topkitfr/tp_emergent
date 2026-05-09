"""Scoring joueurs Topkit — palmarès, awards individuels, note finale sur 100.

Pondération de la note :
  - 40 pts : palmarès collectif (CL, WC, championnats…)  — normalisé sur Messi
  - 20 pts : awards individuels (Ballon d'Or, Golden Boot, POTY…)
  - 25 pts : aura (popularité / icône, saisie 0-100)
  - 15 pts : présence TopKit (nb maillots floqués au joueur)
"""

from typing import List


# ── Poids des compétitions (fallback si pas en DB) ────────────────────────────
HONOUR_WEIGHTS: dict[str, float] = {
    "world cup": 20.0,
    "coupe du monde": 20.0,
    "champions league": 15.0,
    "ligue des champions": 15.0,
    "copa libertadores": 12.0,
    "euro": 10.0,
    "copa america": 10.0,
    "african cup": 10.0,
    "afcon": 10.0,
    "la liga": 7.0,
    "premier league": 7.0,
    "bundesliga": 7.0,
    "serie a": 7.0,
    "ligue 1": 6.0,
    "primeira division": 7.0,
    "fa cup": 4.0,
    "copa del rey": 4.0,
    "dfb pokal": 4.0,
    "coppa italia": 4.0,
    "coupe de france": 3.0,
    "supercoupe": 2.0,
    "supercopa": 2.0,
    "super cup": 2.0,
    "community shield": 2.0,
    "intercontinental": 8.0,
    "nations league": 6.0,
}

# Poids des awards individuels (fallback si pas en DB)
AWARD_WEIGHTS: dict[str, float] = {
    "ballon d'or": 8.0,
    "ballon dor": 8.0,
    "the best": 5.0,
    "fifa best": 5.0,
    "golden boot": 3.0,
    "golden ball": 3.0,
    "golden glove": 2.0,
    "best player": 3.0,
    "player of the year": 3.0,
}

# Multiplicateur selon place
PLACE_MULTIPLIER: dict[str, float] = {
    "winner": 1.0,
    "2nd place": 0.15,
    "runner-up": 0.15,
    "3rd place": 0.05,
}

DEFAULT_HONOUR_WEIGHT = 1.5

# ── Références de normalisation ───────────────────────────────────────────────
# Score palmarès collectif de référence (Messi ≈ 100 pts bruts)
SCORE_PALMARES_REF = 100.0
# Score awards individuels de référence (Messi : ~7 Ballons d'Or = 56 pts bruts)
SCORE_AWARDS_REF = 56.0
# Nombre de maillots TopKit de référence (joueur très présent ≈ 20 maillots)
TOPKIT_KITS_REF = 20

# ── Pondération de la note finale sur 100 ────────────────────────────────────
WEIGHT_PALMARES = 40.0
WEIGHT_AWARDS = 20.0
WEIGHT_AURA = 25.0
WEIGHT_TOPKIT = 15.0


# ── Helpers couleurs ──────────────────────────────────────────────────────────

def parse_colors(raw: str) -> list[str]:
    """Parse une chaîne CSV de couleurs en liste normalisée.

    Exemple : parse_colors("Red, White, red, BLUE ") → ["red", "white", "blue"]
    """
    return list(dict.fromkeys(
        c.strip().lower()
        for c in raw.split(",")
        if c.strip()
    ))


# ── Scoring ──────────────────────────────────────────────────────────────────

def _dedup_honours(honours: List[dict]) -> List[dict]:
    """Supprime les doublons sans saison quand le même titre existe avec une saison."""
    has_season: set[tuple] = set()
    for h in honours:
        season = (h.get("strSeason") or h.get("season") or "").strip()
        league = (h.get("strHonour") or h.get("league") or "").strip()
        place = (h.get("place") or "").strip()
        if season:
            has_season.add((league.lower(), place.lower()))

    result = []
    for h in honours:
        season = (h.get("strSeason") or h.get("season") or "").strip()
        league = (h.get("strHonour") or h.get("league") or "").strip()
        place = (h.get("place") or "").strip()
        if not season and (league.lower(), place.lower()) in has_season:
            continue
        result.append(h)
    return result


def compute_score_palmares(honours: List[dict], individual_awards: List[dict] | None = None) -> float:
    """Calcule le score brut du palmarès COLLECTIF uniquement (hors awards individuels).

    Retourne un score brut non plafonné — la normalisation se fait dans compute_note().
    Les awards individuels ont leur propre composante via compute_score_awards().
    """
    clean_honours = _dedup_honours(honours)

    total = 0.0
    for h in clean_honours:
        place = (h.get("place") or "").lower().strip()
        multiplier = PLACE_MULTIPLIER.get(place, 0.0)
        if multiplier == 0.0:
            continue
        honour_name = (h.get("strHonour") or h.get("league") or "").lower()
        weight = h.get("scoring_weight") or DEFAULT_HONOUR_WEIGHT
        for keyword, w in HONOUR_WEIGHTS.items():
            if keyword in honour_name:
                weight = w
                break
        total += weight * multiplier

    # Rétrocompatibilité : si individual_awards passés ici, on les inclut dans le total
    # (ancienne signature) mais on les exclut de la normalisation awards séparée.
    for award in (individual_awards or []):
        award_name = (award.get("award_name") or "").lower()
        weight = award.get("scoring_weight") or DEFAULT_HONOUR_WEIGHT
        for keyword, w in AWARD_WEIGHTS.items():
            if keyword in award_name:
                weight = w
                break
        count = award.get("count") or 1
        total += weight * count

    return round(total, 2)


def compute_score_awards(individual_awards: List[dict] | None) -> float:
    """Calcule le score brut des awards INDIVIDUELS uniquement.

    Séparé de compute_score_palmares pour permettre une pondération indépendante
    dans la note finale.
    """
    total = 0.0
    for award in (individual_awards or []):
        award_name = (award.get("award_name") or "").lower()
        weight = award.get("scoring_weight") or DEFAULT_HONOUR_WEIGHT
        for keyword, w in AWARD_WEIGHTS.items():
            if keyword in award_name:
                weight = w
                break
        count = award.get("count") or 1
        total += weight * count
    return round(total, 2)


def compute_note(
    score_palmares: float,
    aura: float,
    individual_awards: List[dict] | None = None,
    topkit_kits_count: int = 0,
) -> tuple[float, dict]:
    """Note finale sur 100 compilant toutes les données disponibles.

    Retourne (note, breakdown) où breakdown détaille chaque composante.
    """
    palmares_part = min(score_palmares / SCORE_PALMARES_REF, 1.0) * WEIGHT_PALMARES

    score_awards = compute_score_awards(individual_awards)
    awards_part = min(score_awards / SCORE_AWARDS_REF, 1.0) * WEIGHT_AWARDS if SCORE_AWARDS_REF > 0 else 0.0

    aura_part = min(aura / 100.0, 1.0) * WEIGHT_AURA

    topkit_part = min(topkit_kits_count / TOPKIT_KITS_REF, 1.0) * WEIGHT_TOPKIT

    note = round(palmares_part + awards_part + aura_part + topkit_part, 1)

    breakdown = {
        "palmares": round(palmares_part, 1),
        "awards": round(awards_part, 1),
        "aura": round(aura_part, 1),
        "topkit": round(topkit_part, 1),
        "score_palmares_brut": score_palmares,
        "score_awards_brut": score_awards,
        "topkit_kits_count": topkit_kits_count,
    }

    return note, breakdown
