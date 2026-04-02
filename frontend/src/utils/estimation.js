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

// Patches — multi-select, coeff appliqué par patch coché
export const PATCH_OPTIONS = [
  { value: 'competition', label: 'Competition patch', coeff: 0.10 },
  { value: 'title_winning', label: 'Title winning patch', coeff: 0.10 },
  { value: 'other', label: 'Other patch', coeff: 0.05 },
];

// Signature — type
export const SIGNED_TYPE_COEFF = {
  'player_flocked': 0.80,   // Signé par le joueur flocqué
  'team': 1.00,             // Signé par l'équipe entière
  'other': 0.40,            // Autre(s) joueur(s)
};

// Signature — profil joueur (uniquement si signed_type = player_flocked)
export const PLAYER_PROFILE_COEFF = {
  'legend': 0.75,   // Football Legend (Ronaldo, Zidane, Maldini...)
  'star': 0.25,     // Club Star (joueur majeur du club)
  'none': 0.0,      // Standard / autre
};

export const PLAYER_PROFILE_LABELS = {
  'legend': 'Football Legend',
  'star': 'Club Star',
  'none': 'Standard player',
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

// ─── Main function ────────────────────────────────────────────────────────────

/**
 * @param {object} params
 * @param {'basic'|'advanced'} params.mode
 * @param {'Authentic'|'Replica'|'Other'} params.modelType
 * @param {string} params.competition         — depuis version, jamais saisi
 * @param {string} params.conditionOrigin     — advanced only
 * @param {string} params.physicalState
 * @param {'Official'|'Personalized'|'None'} params.flockingOrigin — advanced only
 * @param {string[]} params.patches           — advanced only, array of PATCH_OPTIONS.value
 * @param {string}   params.patchOtherText    — advanced only, si 'other' coché
 * @param {boolean} params.signed             — advanced only
 * @param {'player_flocked'|'team'|'other'|''} params.signedType   — advanced only
 * @param {string}  params.signedOtherText    — advanced only, si type = 'other'
 * @param {'legend'|'star'|'none'} params.playerProfile            — si signed_type = player_flocked
 * @param {'none'|'light'|'strong'} params.signedProofLevel
 * @param {boolean} params.isRare             — advanced only
 * @param {string}  params.rareReason         — advanced only, text
 * @param {string}  params.otherInfo          — advanced only, text libre
 * @param {number}  params.seasonYear         — 0 if unknown
 */
export function calculateEstimation({
  mode = 'basic',
  modelType = 'Replica',
  competition = '',
  conditionOrigin = '',
  physicalState = '',
  flockingOrigin = 'None',
  patches = [],
  patchOtherText = '',
  signed = false,
  signedType = '',
  signedOtherText = '',
  playerProfile = 'none',
  signedProofLevel = 'none',
  // legacy support
  signedProof = false,
  hasPatch = false,       // legacy compat
  isRare = false,
  rareReason = '',
  otherInfo = '',
  seasonYear = 0,
  // legacy auraLevel kept for backward compat with MyCollection old items
  auraLevel = 0,
}) {
  const base = BASE_PRICES[modelType] || 60;
  let coeffSum = 0;
  const breakdown = [];

  // ── Competition (basic + advanced) — depuis version ──────────────────────
  const compC = COMPETITION_COEFF[competition] ?? 0;
  if (compC !== 0) {
    coeffSum += compC;
    breakdown.push({ label: `Competition: ${competition}`, coeff: compC, source: 'version' });
  }

  // ── Physical State (basic + advanced) ────────────────────────────────────
  const stateC = STATE_COEFF[physicalState] ?? 0;
  coeffSum += stateC;
  if (physicalState) {
    breakdown.push({ label: `State: ${physicalState}`, coeff: stateC });
  }

  if (mode === 'advanced') {
    // ── Origin ──────────────────────────────────────────────────────────────
    const originC = ORIGIN_COEFF[conditionOrigin] ?? 0;
    coeffSum += originC;
    if (conditionOrigin) {
      breakdown.push({ label: `Origin: ${conditionOrigin}`, coeff: originC });
    }

    // ── Flocking ────────────────────────────────────────────────────────────
    const flockingC = FLOCKING_COEFF[flockingOrigin] ?? 0;
    coeffSum += flockingC;
    if (flockingOrigin && flockingOrigin !== 'None') {
      breakdown.push({ label: `Flocking: ${flockingOrigin}`, coeff: flockingC });
    }

    // ── Patches (multi) ─────────────────────────────────────────────────────
    // Support nouveau format (array) + legacy (boolean hasPatch)
    const patchList = Array.isArray(patches) && patches.length > 0
      ? patches
      : hasPatch ? ['competition'] : [];

    patchList.forEach(pKey => {
      const opt = PATCH_OPTIONS.find(o => o.value === pKey);
      if (!opt) return;
      coeffSum += opt.coeff;
      const suffix = pKey === 'other' && patchOtherText ? ` (${patchOtherText})` : '';
      breakdown.push({ label: `Patch: ${opt.label}${suffix}`, coeff: opt.coeff });
    });

    // ── Signature ───────────────────────────────────────────────────────────
    if (signed && signedType) {
      const signedC = SIGNED_TYPE_COEFF[signedType] ?? 0;
      coeffSum += signedC;
      const signedLabel = {
        player_flocked: 'Signed by flocked player',
        team: 'Signed by the team',
        other: `Signed: ${signedOtherText || 'other'}`,
      }[signedType] || 'Signed';
      breakdown.push({ label: signedLabel, coeff: signedC });

      // Player profile — uniquement si signed_type = player_flocked
      if (signedType === 'player_flocked') {
        let profileKey = playerProfile && playerProfile !== 'none' ? playerProfile : null;
        if (!profileKey && auraLevel >= 4) profileKey = 'legend';
        else if (!profileKey && auraLevel >= 2) profileKey = 'star';

        if (profileKey) {
          const profileC = PLAYER_PROFILE_COEFF[profileKey] ?? 0;
          if (profileC > 0) {
            coeffSum += profileC;
            breakdown.push({
              label: `Player profile: ${PLAYER_PROFILE_LABELS[profileKey]}`,
              coeff: profileC,
            });
          }
        }
      }

      // Proof level
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

    // ── Rarity ──────────────────────────────────────────────────────────────
    if (isRare) {
      coeffSum += RARITY_COEFF;
      breakdown.push({ label: rareReason ? `Rare: ${rareReason}` : 'Rare jersey', coeff: RARITY_COEFF });
    }

    // ── Age (starts after 2-year grace period) ────────────────────────────
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
