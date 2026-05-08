"""
Tests sur `backend.utils.calculate_estimation`.

Pourquoi en priorité ?
  La formule est dupliquée Python ↔ JS (`backend/utils.py` ↔
  `frontend/src/utils/estimation.js`). Plusieurs régressions historiques :
    - "fix(estimation): add printed_sign and signed_personal_message to frontend calculation"
    - "fix(estimation): add printed sign and personal message support"
  → Ces tests servent de spec exécutable du backend ; côté front il
  faudra ensuite garder la même grille de coeffs.
"""
from datetime import datetime, timezone

import pytest

from backend.utils import (
    calculate_estimation,
    ESTIMATION_BASE_PRICES,
    ESTIMATION_PATCH_COEFF,
    ESTIMATION_RARITY_COEFF,
    ESTIMATION_AGE_DELAY_YEARS,
    ESTIMATION_AGE_COEFF_PER_YEAR,
)


# ─── Cas dégénérés / sanity checks ──────────────────────────────────────────

class TestBasePrice:
    """Le prix de base dépend uniquement du type de modèle."""

    def test_authentic_base_price(self):
        r = calculate_estimation(
            model_type="Authentic", competition="", condition_origin="",
            physical_state="", flocking_origin="", signed=False,
            signed_proof="none", season_year=0,
        )
        assert r["base_price"] == ESTIMATION_BASE_PRICES["Authentic"]
        assert r["estimated_price"] == r["base_price"]  # pas de coeff

    def test_replica_base_price(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="", signed=False,
            signed_proof="none", season_year=0,
        )
        assert r["base_price"] == ESTIMATION_BASE_PRICES["Replica"]

    def test_unknown_model_type_falls_back_to_60(self):
        r = calculate_estimation(
            model_type="Bootleg",  # pas dans ESTIMATION_BASE_PRICES
            competition="", condition_origin="", physical_state="",
            flocking_origin="", signed=False, signed_proof="none",
            season_year=0,
        )
        assert r["base_price"] == 60


# ─── Mode basic vs advanced ─────────────────────────────────────────────────

class TestModeBasicAdvanced:
    """En mode basic, seuls compétition et état physique comptent."""

    def test_basic_ignores_signed_and_origin_and_age(self):
        r = calculate_estimation(
            model_type="Replica",
            competition="World Cup",       # 0.60
            condition_origin="Match Worn",  # ignoré en basic
            physical_state="Used",          # 0
            flocking_origin="Official",     # ignoré
            signed=True,                    # ignoré
            signed_proof="strong",          # ignoré
            season_year=2000,               # ignoré
            mode="basic",
        )
        # base 90 × (1 + 0.60) = 144
        assert r["estimated_price"] == 144.0
        assert r["coeff_sum"] == 0.60

    def test_advanced_applies_all_coeffs(self):
        r = calculate_estimation(
            model_type="Replica",
            competition="World Cup",          # 0.60
            condition_origin="Match Worn",     # 1.20
            physical_state="New with tag",     # 0.30
            flocking_origin="None",            # 0
            signed=False,
            signed_proof="none",
            season_year=datetime.now(timezone.utc).year,  # pas d'âge
            mode="advanced",
        )
        # 0.60 + 1.20 + 0.30 = 2.10 → base 90 × 3.10 = 279.0
        assert r["coeff_sum"] == pytest.approx(2.10)
        assert r["estimated_price"] == 279.0


# ─── Combinaison signature + profil joueur (Option A) ──────────────────────

class TestSignedPlayerProfile:
    """
    Le coeff "profil joueur" n'est appliqué QUE si :
      signed=True ET signed_type="player_flocked" ET flocking_origin="Official"
    Le profil est dérivé de la note /100 du joueur.
    """

    def _call(self, **overrides):
        defaults = dict(
            model_type="Authentic",
            competition="",
            condition_origin="",
            physical_state="",
            flocking_origin="Official",
            signed=True,
            signed_type="player_flocked",
            signed_proof="none",
            season_year=datetime.now(timezone.utc).year,
            mode="advanced",
        )
        defaults.update(overrides)
        return calculate_estimation(**defaults)

    def test_legend_profile_applied(self):
        r = self._call(flocking_player_note=92)
        assert r["flocking_player_profile"] == "football_legend"
        # flocking Official = 0.20, signed player_flocked = 0.80, profil legend = 1.00 → 2.00
        assert r["coeff_sum"] == pytest.approx(2.00)

    def test_no_profile_below_40(self):
        r = self._call(flocking_player_note=10)
        assert r["flocking_player_profile"] == "none"
        # flocking Official = 0.20, signed player_flocked = 0.80, pas de profil → 1.00
        assert r["coeff_sum"] == pytest.approx(1.00)

    def test_profile_thresholds(self):
        """Les seuils 40/65/80/90 doivent matcher exactement la grille du PRD."""
        # 39 = none, 40 = good_player
        assert self._call(flocking_player_note=39)["flocking_player_profile"] == "none"
        assert self._call(flocking_player_note=40)["flocking_player_profile"] == "good_player"
        # 64 = good, 65 = club_star
        assert self._call(flocking_player_note=64)["flocking_player_profile"] == "good_player"
        assert self._call(flocking_player_note=65)["flocking_player_profile"] == "club_star"
        # 79 = club_star, 80 = world_star
        assert self._call(flocking_player_note=79)["flocking_player_profile"] == "club_star"
        assert self._call(flocking_player_note=80)["flocking_player_profile"] == "world_star"
        # 89 = world_star, 90 = legend
        assert self._call(flocking_player_note=89)["flocking_player_profile"] == "world_star"
        assert self._call(flocking_player_note=90)["flocking_player_profile"] == "football_legend"

    def test_profile_ignored_if_not_player_flocked(self):
        """Signed handsigned ne doit PAS appliquer le coeff profil joueur."""
        r = self._call(
            signed_type="handsigned",
            flocking_player_note=95,  # serait legend (+1.00) avec player_flocked
        )
        # flocking Official = 0.20, handsigned = 0.40, pas de coeff profil → 0.60
        assert r["coeff_sum"] == pytest.approx(0.60)

    def test_profile_ignored_if_flocking_not_official(self):
        r = self._call(
            flocking_origin="Personalized",
            flocking_player_note=95,
        )
        # flocking Personalized = 0, signed player_flocked = 0.80, pas de coeff profil
        assert r["coeff_sum"] == pytest.approx(0.80)


# ─── Signature : message personnel (régression historique) ──────────────────

class TestSignedPersonalMessage:
    """Régression : le coeff -0.20 du message personnel doit être appliqué."""

    def test_personal_message_subtracts_coeff(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=True, signed_type="handsigned",
            signed_personal_message=True,
            signed_proof="none", season_year=2025,
        )
        # handsigned = 0.40 ; personal_message = -0.20 → 0.20
        assert r["coeff_sum"] == pytest.approx(0.20)

    def test_personal_message_ignored_if_not_signed(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False,
            signed_personal_message=True,  # ignoré car signed=False
            signed_proof="none", season_year=2025,
        )
        assert r["coeff_sum"] == 0.0


# ─── Patch + rareté ─────────────────────────────────────────────────────────

class TestPatchAndRarity:
    def test_patch_adds_010(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none", season_year=2025,
            patch=True,
        )
        assert r["coeff_sum"] == pytest.approx(ESTIMATION_PATCH_COEFF)

    def test_rarity_adds_040(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none", season_year=2025,
            is_rare=True, rare_reason="GK warmup short run",
        )
        assert r["coeff_sum"] == pytest.approx(ESTIMATION_RARITY_COEFF)


# ─── Ancienneté ─────────────────────────────────────────────────────────────

class TestAgeCoefficient:
    """+0.05/an au-delà des 2 premières années, plafond 1.00."""

    def test_age_below_delay_no_coeff(self):
        current = datetime.now(timezone.utc).year
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none",
            season_year=current,  # âge 0
        )
        assert r["coeff_sum"] == 0.0

    def test_age_just_over_delay(self):
        current = datetime.now(timezone.utc).year
        # âge effectif = 1 → coeff = 0.05
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none",
            season_year=current - (ESTIMATION_AGE_DELAY_YEARS + 1),
        )
        assert r["coeff_sum"] == pytest.approx(ESTIMATION_AGE_COEFF_PER_YEAR)

    def test_age_capped_at_max(self):
        # 50 ans → effective_age=48 → 48*0.05=2.40 mais cap à 1.00
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none",
            season_year=datetime.now(timezone.utc).year - 50,
        )
        assert r["coeff_sum"] == pytest.approx(1.0)


# ─── Format de sortie ───────────────────────────────────────────────────────

class TestOutputShape:
    """Le dict de retour doit contenir les clés que le front attend."""

    def test_breakdown_is_list_of_dicts(self):
        r = calculate_estimation(
            model_type="Authentic", competition="World Cup",
            condition_origin="Match Worn", physical_state="New with tag",
            flocking_origin="None",
            signed=False, signed_proof="none", season_year=2024,
        )
        assert isinstance(r["breakdown"], list)
        assert all("label" in item and "coeff" in item for item in r["breakdown"])

    def test_required_keys_present(self):
        r = calculate_estimation(
            model_type="Replica", competition="", condition_origin="",
            physical_state="", flocking_origin="None",
            signed=False, signed_proof="none", season_year=2025,
        )
        for key in ("base_price", "model_type", "coeff_sum", "estimated_price",
                    "breakdown", "mode", "flocking_player_profile"):
            assert key in r, f"Clé manquante : {key}"
