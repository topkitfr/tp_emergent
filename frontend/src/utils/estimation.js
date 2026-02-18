// Estimation logic matching backend formula exactly
// Formula: Estimated Price = Base Price × (1 + sum of coefficients)

const BASE_PRICES = { Authentic: 140, Replica: 90, Other: 60 };

const COMPETITION_COEFF = {
  'National Championship': 0.0,
  'National Cup': 0.05,
  'Continental Cup': 1.0,
  'Intercontinental Cup': 1.0,
  'World Cup': 1.0,
};

const ORIGIN_COEFF = {
  'Club Stock': 0.5,
  'Match Prepared': 1.0,
  'Match Worn': 1.5,
  'Training': 0.0,
  'Shop': 0.0,
};

const STATE_COEFF = {
  'New with tag': 0.3,
  'Very good': 0.1,
  'Used': 0.0,
  'Damaged': -0.2,
  'Needs restoration': -0.4,
};

const FLOCKING_COEFF = {
  'Official': 0.15,
  'Personalized': 0.0,
};

const SIGNED_COEFF = 1.5;
const SIGNED_PROOF_COEFF = 1.0;
const AGE_COEFF_PER_YEAR = 0.05;
const AGE_MAX = 1.0;

export function calculateEstimation({
  modelType = 'Replica',
  competition = '',
  conditionOrigin = '',
  physicalState = '',
  flockingOrigin = '',
  signed = false,
  signedProof = false,
  seasonYear = 0,
}) {
  const base = BASE_PRICES[modelType] || 60;
  let coeffSum = 0;
  const breakdown = [];

  // Competition
  const compC = COMPETITION_COEFF[competition] ?? 0;
  coeffSum += compC;
  if (competition) {
    breakdown.push({ label: `Competition: ${competition}`, coeff: compC });
  }

  // Origin
  const originC = ORIGIN_COEFF[conditionOrigin] ?? 0;
  coeffSum += originC;
  if (conditionOrigin) {
    breakdown.push({ label: `Origin: ${conditionOrigin}`, coeff: originC });
  }

  // Physical State
  const stateC = STATE_COEFF[physicalState] ?? 0;
  coeffSum += stateC;
  if (physicalState) {
    breakdown.push({ label: `State: ${physicalState}`, coeff: stateC });
  }

  // Flocking
  const flockingC = FLOCKING_COEFF[flockingOrigin] ?? 0;
  coeffSum += flockingC;
  if (flockingOrigin) {
    breakdown.push({ label: `Flocking: ${flockingOrigin}`, coeff: flockingC });
  }

  // Signed
  if (signed) {
    coeffSum += SIGNED_COEFF;
    breakdown.push({ label: 'Signed', coeff: SIGNED_COEFF });
    if (signedProof) {
      coeffSum += SIGNED_PROOF_COEFF;
      breakdown.push({ label: 'Proof/Certificate', coeff: SIGNED_PROOF_COEFF });
    }
  }

  // Age
  const currentYear = new Date().getFullYear();
  const age = seasonYear > 0 ? Math.max(0, currentYear - seasonYear) : 0;
  const ageC = Math.min(age * AGE_COEFF_PER_YEAR, AGE_MAX);
  coeffSum += ageC;
  if (age > 0) {
    breakdown.push({ label: `Age: ${age} years`, coeff: parseFloat(ageC.toFixed(2)) });
  }

  const estimatedPrice = parseFloat((base * (1 + coeffSum)).toFixed(2));

  return {
    basePrice: base,
    modelType,
    coeffSum: parseFloat(coeffSum.toFixed(2)),
    estimatedPrice,
    breakdown,
  };
}
