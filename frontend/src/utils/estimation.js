// Estimation logic — Basic & Advanced modes
// Formula: Estimated Price = Base Price × (1 + sum of coefficients)

export const BASE_PRICES = { Authentic: 140, Replica: 90, Other: 60 };

// ─── Coefficients ────────────────────────────────────────────────────────────

export const COMPETITION_COEFF = {
  'National Championship': 0.0,
  'National Cup': 0.10,
  'Continental Cup': 0.60,
  'Intercontinental Cup': 0.60,
  'World Cup': 0.60,
};

export const ORIGIN_COEFF = {
  'Shop': 0.0,
  'Training': 0.0,
  'Club Stock': 0.40,
  'Match Prepared': 0.80,
  'Match Worn': 1.20,
};

export const STATE_COEFF = {
  'New with tag': 0.30,
  'Very good': 0.15,
  'Used': 0.0,
  'Damaged': -0.30,
  'Needs restoration': -0.50,
};

// Flocking — origin
export const FLOCKING_COEFF = {
  'Official': 0.20,
  'Personalized': 0.0,
  'None': 0.0,
};

// Patch officiel de compétition
export const PATCH_COEFF = 0.10;

// Signature — type
export const SIGNED_TYPE_COEFF = {
  'player_flocked': 0.80,   // Signé par le joueur flocqué
  'team': 1.00,             // Signé par l'équipe entière
  'other': 0.40,            // Autre(s) joueur(s)
};

// Signature — qualité de la preuve
export const SIGNED_PROOF_COEFF = {
  'none': 0.0,
  'light': 0.20,  // Certif léger / provenance faible
  'strong': 0.40, // Photo/vidéo + COA crédible
};

// Rareté
export const RARITY_COEFF = 0.40;

// Ancienneté : commence à compter 2 ans après la saison, +0.05/an, max +1.0
export const AGE_GRACE_YEARS = 2;
export const AGE_COEFF_PER_YEAR = 0.05;
export const AGE_MAX = 1.0;

// Aura joueur (uniquement signé)
export const AURA_COEFF = { 1: 0.05, 2: 0.25, 3: 0.50, 4: 0.75, 5: 1.00 };

// ─── Main function ────────────────────────────────────────────────────────────

/**
 * @param {object} params
 * @param {'basic'|'advanced'} params.mode
 * @param {'Authentic'|'Replica'|'Other'} params.modelType
 * @param {string} params.competition
 * @param {string} params.conditionOrigin          — advanced only
 * @param {string} params.physicalState
 * @param {'Official'|'Personalized'|'None'} params.flockingOrigin  — advanced only
 * @param {boolean} params.hasPatch                — advanced only
 * @param {boolean} params.signed
 * @param {'player_flocked'|'team'|'other'|''} params.signedType   — advanced only
 * @param {'none'|'light'|'strong'} params.signedProofLevel        — advanced only
 * @param {boolean} params.isRare                  — advanced only
 * @param {number} params.seasonYear               — 0 if unknown
 * @param {number} params.auraLevel                — 0–5, advanced only
 */
export function calculateEstimation({
  mode = 'basic',
  modelType = 'Replica',
  competition = '',
  conditionOrigin = '',
  physicalState = '',
  flockingOrigin = 'None',
  hasPatch = false,
  signed = false,
  signedType = '',
  signedProofLevel = 'none',
  // legacy support
  signedProof = false,
  isRare = false,
  seasonYear = 0,
  auraLevel = 0,
}) {
  const base = BASE_PRICES[modelType] || 60;
  let coeffSum = 0;
  const breakdown = [];

  // ── Competition (basic + advanced) ────────────────────────────────────────
  const compC = COMPETITION_COEFF[competition] ?? 0;
  coeffSum += compC;
  if (competition && compC !== 0) {
    breakdown.push({ label: `Competition: ${competition}`, coeff: compC });
  }

  // ── Physical State (basic + advanced) ─────────────────────────────────────
  const stateC = STATE_COEFF[physicalState] ?? 0;
  coeffSum += stateC;
  if (physicalState) {
    breakdown.push({ label: `State: ${physicalState}`, coeff: stateC });
  }

  if (mode === 'advanced') {
    // ── Origin ────────────────────────────────────────────────────────────────
    const originC = ORIGIN_COEFF[conditionOrigin] ?? 0;
    coeffSum += originC;
    if (conditionOrigin) {
      breakdown.push({ label: `Origin: ${conditionOrigin}`, coeff: originC });
    }

    // ── Flocking ──────────────────────────────────────────────────────────────
    const flockingC = FLOCKING_COEFF[flockingOrigin] ?? 0;
    coeffSum += flockingC;
    if (flockingOrigin && flockingOrigin !== 'None') {
      breakdown.push({ label: `Flocking: ${flockingOrigin}`, coeff: flockingC });
    }

    // ── Patch ─────────────────────────────────────────────────────────────────
    if (hasPatch) {
      coeffSum += PATCH_COEFF;
      breakdown.push({ label: 'Official patch', coeff: PATCH_COEFF });
    }

    // ── Signature ─────────────────────────────────────────────────────────────
    if (signed && signedType) {
      const signedC = SIGNED_TYPE_COEFF[signedType] ?? 0;
      coeffSum += signedC;
      const signedLabel = {
        player_flocked: 'Signed by flocked player',
        team: 'Signed by the team',
        other: 'Signed (other)',
      }[signedType] || 'Signed';
      breakdown.push({ label: signedLabel, coeff: signedC });

      // Proof level — support legacy boolean signedProof
      const proofLevel = signedProofLevel !== 'none'
        ? signedProofLevel
        : signedProof ? 'light' : 'none';
      const proofC = SIGNED_PROOF_COEFF[proofLevel] ?? 0;
      if (proofC > 0) {
        coeffSum += proofC;
        const proofLabel = proofLevel === 'strong'
          ? 'Proof: solid (photo/video + COA)'
          : 'Proof: light certificate';
        breakdown.push({ label: proofLabel, coeff: proofC });
      }

      // Aura
      const auraC = AURA_COEFF[auraLevel] ?? 0;
      if (auraLevel >= 1 && auraC > 0) {
        coeffSum += auraC;
        breakdown.push({ label: `Aura ${'★'.repeat(auraLevel)} (level ${auraLevel})`, coeff: auraC });
      }
    } else if (signed && !signedType) {
      // Legacy fallback: signed = true but no type (old items)
      const legacyC = 0.80;
      coeffSum += legacyC;
      breakdown.push({ label: 'Signed', coeff: legacyC });
      if (signedProof) {
        coeffSum += SIGNED_PROOF_COEFF.light;
        breakdown.push({ label: 'Proof/Certificate', coeff: SIGNED_PROOF_COEFF.light });
      }
    }

    // ── Rarity ────────────────────────────────────────────────────────────────
    if (isRare) {
      coeffSum += RARITY_COEFF;
      breakdown.push({ label: 'Rare jersey', coeff: RARITY_COEFF });
    }

    // ── Age (starts after 2-year grace period) ────────────────────────────────
    if (seasonYear > 0) {
      const currentYear = new Date().getFullYear();
      const age = Math.max(0, currentYear - seasonYear);
      const effectiveAge = Math.max(0, age - AGE_GRACE_YEARS);
      const ageC = parseFloat(Math.min(effectiveAge * AGE_COEFF_PER_YEAR, AGE_MAX).toFixed(2));
      if (ageC > 0) {
        coeffSum += ageC;
        breakdown.push({ label: `Age: ${age} years (+${AGE_GRACE_YEARS}y grace)`, coeff: ageC });
      }
    }
  } else {
    // ── Basic mode: legacy signed support ─────────────────────────────────────
    if (signed) {
      const legacyC = 0.80;
      coeffSum += legacyC;
      breakdown.push({ label: 'Signed', coeff: legacyC });
      if (signedProof) {
        coeffSum += SIGNED_PROOF_COEFF.light;
        breakdown.push({ label: 'Proof/Certificate', coeff: SIGNED_PROOF_COEFF.light });
      }
    }
  }

  const estimatedPrice = parseFloat((base * (1 + coeffSum)).toFixed(2));

  return {
    basePrice: base,
    modelType,
    coeffSum: parseFloat(coeffSum.toFixed(2)),
    estimatedPrice,
    breakdown,
    mode,
  };
}
