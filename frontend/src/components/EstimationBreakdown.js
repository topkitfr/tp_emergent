// src/components/EstimationBreakdown.js
// Display + form component — owns advanced form state, receives basic props from parent
import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import {
  calculateEstimation,
  PATCH_OPTIONS,
  ORIGIN_COEFF,
  STATE_COEFF,
  SIGNED_PROOF_COEFF,
  PLAYER_PROFILE_LABELS,
} from '@/utils/estimation';

const fs       = { fontFamily: 'Barlow Condensed' };
const labelCls = 'text-[10px] uppercase tracking-wider text-muted-foreground';
const fieldLbl = 'block text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5';
const selectCls = 'w-full bg-background border border-border text-xs px-2 py-1.5 rounded focus:outline-none focus:ring-1 focus:ring-primary';
const inputCls  = 'w-full bg-background border border-border text-xs px-2 py-1.5 rounded focus:outline-none focus:ring-1 focus:ring-primary';

// ─── Helper: form row ────────────────────────────────────────────────────────
function Field({ label, children }) {
  return (
    <div>
      <label className={fieldLbl}>{label}</label>
      {children}
    </div>
  );
}

// ─── Main component ──────────────────────────────────────────────────────────
export default function EstimationBreakdown({
  mode = 'basic',
  modelType = 'Replica',
  competition = '',
  // Basic props (pré-remplis depuis la fiche item)
  conditionOrigin: conditionOriginProp = '',
  physicalState: physicalStateProp = '',
  seasonYear: seasonYearProp = 0,
  // Advanced props sauvegardés (hydration depuis item existant)
  flockingOrigin: flockingOriginProp = 'None',
  patches: patchesProp = [],
  patchOtherText: patchOtherTextProp = '',
  signed: signedProp = false,
  signedType: signedTypeProp = '',
  signedOtherText: signedOtherTextProp = '',
  playerProfile: playerProfileProp = 'none',
  signedProofLevel: signedProofLevelProp = 'none',
  isRare: isRareProp = false,
  rareReason: rareReasonProp = '',
  otherInfo: otherInfoProp = '',
  // Legacy compat
  hasPatch = false,
  auraLevel = 0,
  // Callback optionnel pour sauvegarder l'état advanced
  onAdvancedChange,
}) {
  const [open, setOpen] = useState(false);

  // ── Advanced form state (local) ──────────────────────────────────────────
  const [conditionOrigin, setConditionOrigin] = useState(conditionOriginProp);
  const [physicalState, setPhysicalState]     = useState(physicalStateProp);
  const [flockingOrigin, setFlockingOrigin]   = useState(flockingOriginProp);
  const [patches, setPatches]                 = useState(patchesProp);
  const [patchOtherText, setPatchOtherText]   = useState(patchOtherTextProp);
  const [signed, setSigned]                   = useState(signedProp);
  const [signedType, setSignedType]           = useState(signedTypeProp);
  const [signedOtherText, setSignedOtherText] = useState(signedOtherTextProp);
  const [playerProfile, setPlayerProfile]     = useState(playerProfileProp);
  const [signedProofLevel, setSignedProofLevel] = useState(signedProofLevelProp);
  const [isRare, setIsRare]                   = useState(isRareProp);
  const [rareReason, setRareReason]           = useState(rareReasonProp);
  const [otherInfo, setOtherInfo]             = useState(otherInfoProp);

  // ── Season year — extraire l'année depuis la prop (ex: "2018-2019" → 2018) ─
  const seasonYear = (() => {
    if (seasonYearProp && typeof seasonYearProp === 'number') return seasonYearProp;
    if (seasonYearProp && typeof seasonYearProp === 'string') {
      const m = seasonYearProp.match(/(\d{4})/);
      return m ? parseInt(m[1], 10) : 0;
    }
    return 0;
  })();

  // ── Notify parent on advanced change ────────────────────────────────────
  const notify = (patch) => {
    if (!onAdvancedChange) return;
    onAdvancedChange({
      conditionOrigin, physicalState, flockingOrigin, patches, patchOtherText,
      signed, signedType, signedOtherText, playerProfile, signedProofLevel,
      isRare, rareReason, otherInfo,
      ...patch,
    });
  };

  const update = (setter, field) => (val) => { setter(val); notify({ [field]: val }); };

  // ── Patch toggle ─────────────────────────────────────────────────────────
  const togglePatch = (val) => {
    const next = patches.includes(val) ? patches.filter(p => p !== val) : [...patches, val];
    setPatches(next);
    notify({ patches: next });
  };

  // ── Calcul ───────────────────────────────────────────────────────────────
  const result = calculateEstimation({
    mode,
    modelType,
    competition,
    conditionOrigin,
    physicalState,
    flockingOrigin,
    patches,
    patchOtherText,
    signed,
    signedType,
    signedOtherText,
    playerProfile,
    signedProofLevel,
    isRare,
    rareReason,
    seasonYear,
    auraLevel,
    hasPatch,
  });

  const isFlockingOfficial = flockingOrigin === 'Official';
  const isSignedYes        = signed === true || signed === 'yes';

  return (
    <div className="border border-border bg-card" style={fs}>

      {/* ── Header avec prix ── */}
      <div className="flex items-center justify-between px-3 py-2">
        <span className={labelCls}>ESTIMATION</span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-base text-accent font-semibold">
            {result.estimatedPrice}€
          </span>
          <button
            onClick={() => setOpen(v => !v)}
            className="text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Toggle breakdown"
          >
            {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="px-3 pb-3 border-t border-border pt-2 space-y-3">

          {/* ────────────────── MODE BASIC ────────────────── */}
          {mode === 'basic' && (
            <p className="text-[10px] text-muted-foreground italic">
              Basic estimate from model &amp; physical state. Switch to Advanced for full breakdown.
            </p>
          )}

          {/* ────────────────── MODE ADVANCED ────────────────── */}
          {mode === 'advanced' && (
            <div className="space-y-3">

              {/* Row 1 – Origin + Physical State */}
              <div className="grid grid-cols-2 gap-2">
                <Field label="Origin (Condition)">
                  <select className={selectCls} value={conditionOrigin} onChange={e => update(setConditionOrigin, 'conditionOrigin')(e.target.value)}>
                    <option value="">— Select —</option>
                    {Object.keys(ORIGIN_COEFF).map(k => <option key={k} value={k}>{k}</option>)}
                  </select>
                </Field>
                <Field label="Physical State">
                  <select className={selectCls} value={physicalState} onChange={e => update(setPhysicalState, 'physicalState')(e.target.value)}>
                    <option value="">— Select —</option>
                    {Object.keys(STATE_COEFF).map(k => <option key={k} value={k}>{k}</option>)}
                  </select>
                </Field>
              </div>

              {/* Row 2 – Flocking */}
              <Field label="Flocking">
                <select className={selectCls} value={flockingOrigin} onChange={e => { update(setFlockingOrigin, 'flockingOrigin')(e.target.value); if (e.target.value !== 'Official') { update(setPlayerProfile, 'playerProfile')('none'); } }}>
                  <option value="None">None</option>
                  <option value="Official">Official (name + number)</option>
                  <option value="Personalized">Personalized</option>
                </select>
              </Field>

              {/* Joueur flocqué — visible uniquement si Official */}
              {isFlockingOfficial && (
                <Field label="Player profile">
                  <select className={selectCls} value={playerProfile} onChange={e => update(setPlayerProfile, 'playerProfile')(e.target.value)}>
                    <option value="none">Standard player</option>
                    <option value="star">Club Star</option>
                    <option value="legend">Football Legend</option>
                  </select>
                </Field>
              )}

              {/* Row 3 – Patches (checkboxes) */}
              <div>
                <span className={fieldLbl}>Patches</span>
                <div className="flex flex-col gap-1 mt-0.5">
                  {PATCH_OPTIONS.map(opt => (
                    <label key={opt.value} className="flex items-center gap-2 text-xs cursor-pointer">
                      <input
                        type="checkbox"
                        checked={patches.includes(opt.value)}
                        onChange={() => togglePatch(opt.value)}
                        className="accent-primary"
                      />
                      <span>{opt.label}</span>
                      <span className="text-muted-foreground text-[10px]">+{opt.coeff}</span>
                    </label>
                  ))}
                </div>
                {/* Texte libre si "Other" coché */}
                {patches.includes('other') && (
                  <input
                    type="text"
                    placeholder="Specify patch…"
                    className={`${inputCls} mt-1`}
                    value={patchOtherText}
                    onChange={e => update(setPatchOtherText, 'patchOtherText')(e.target.value)}
                  />
                )}
              </div>

              {/* Row 4 – Signed */}
              <div className="grid grid-cols-2 gap-2">
                <Field label="Signed">
                  <select className={selectCls} value={signed ? 'yes' : 'no'} onChange={e => { const val = e.target.value === 'yes'; update(setSigned, 'signed')(val); if (!val) { update(setSignedType, 'signedType')(''); update(setSignedProofLevel, 'signedProofLevel')('none'); } }}>
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                  </select>
                </Field>
                {isSignedYes && (
                  <Field label="Signed by">
                    <select className={selectCls} value={signedType} onChange={e => update(setSignedType, 'signedType')(e.target.value)}>
                      <option value="">— Select —</option>
                      <option value="player_flocked">Flocked player</option>
                      <option value="team">The team</option>
                      <option value="other">Other – specify</option>
                    </select>
                  </Field>
                )}
              </div>

              {/* Précision si "Other" */}
              {isSignedYes && signedType === 'other' && (
                <Field label="Specify">
                  <input type="text" placeholder="Who signed?" className={inputCls} value={signedOtherText} onChange={e => update(setSignedOtherText, 'signedOtherText')(e.target.value)} />
                </Field>
              )}

              {/* Preuve si signé */}
              {isSignedYes && signedType && (
                <Field label="Proof / Certificate">
                  <select className={selectCls} value={signedProofLevel} onChange={e => update(setSignedProofLevel, 'signedProofLevel')(e.target.value)}>
                    <option value="none">No proof</option>
                    <option value="light">Light certificate / weak provenance</option>
                    <option value="strong">Solid proof (photo/video + COA)</option>
                  </select>
                </Field>
              )}

              {/* Row 5 – Rare */}
              <div className="grid grid-cols-2 gap-2">
                <Field label="Rare jersey">
                  <select className={selectCls} value={isRare ? 'yes' : 'no'} onChange={e => { const val = e.target.value === 'yes'; update(setIsRare, 'isRare')(val); if (!val) update(setRareReason, 'rareReason')(''); }}>
                    <option value="no">No</option>
                    <option value="yes">Yes</option>
                  </select>
                </Field>
                {isRare && (
                  <Field label="Why rare?">
                    <input type="text" placeholder="Limited edition, error…" className={inputCls} value={rareReason} onChange={e => update(setRareReason, 'rareReason')(e.target.value)} />
                  </Field>
                )}
              </div>

              {/* Row 6 – Other info (no coeff) */}
              <Field label="Other info (no effect on price)">
                <input type="text" placeholder="Long sleeve, prototype, banned sponsor…" className={inputCls} value={otherInfo} onChange={e => update(setOtherInfo, 'otherInfo')(e.target.value)} />
              </Field>

            </div>
          )}

          {/* ── Breakdown coefficients ── */}
          <div className="space-y-1 border-t border-border pt-2 mt-1">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Base ({modelType})</span>
              <span className="font-mono">{result.basePrice}€</span>
            </div>

            {result.breakdown.length === 0 && (
              <p className="text-[10px] text-muted-foreground italic">No additional coefficients applied.</p>
            )}

            {result.breakdown.map((b, i) => (
              <div key={i} className="flex justify-between text-[10px]">
                <span className="text-muted-foreground flex items-center gap-1">
                  {b.source === 'version' && (
                    <span className="text-[8px] text-primary/40 uppercase tracking-wider" style={fs}>version</span>
                  )}
                  {b.label}
                </span>
                <span className={`font-mono ${
                  b.coeff > 0 ? 'text-green-500' : b.coeff < 0 ? 'text-destructive' : 'text-muted-foreground'
                }`}>
                  {b.coeff > 0 ? '+' : ''}{b.coeff}
                </span>
              </div>
            ))}

            <div className="flex justify-between text-[10px] border-t border-border pt-1 mt-1">
              <span className="text-muted-foreground">Multiplier</span>
              <span className="font-mono">× {(1 + result.coeffSum).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-xs font-semibold border-t border-border pt-1">
              <span>Estimated price</span>
              <span className="font-mono text-accent">{result.estimatedPrice}€</span>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
