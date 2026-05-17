// src/components/EstimationBreakdown.js
// Display-only component — receives all props from parent, never owns form state
import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { calculateEstimation } from '@/utils/estimation';

const fs       = { fontFamily: 'Barlow Condensed' };
const labelCls = 'text-[10px] uppercase tracking-wider text-muted-foreground';

export default function EstimationBreakdown({
  mode = 'basic',
  modelType = 'Replica',
  competition = '',
  conditionOrigin = '',
  physicalState = '',
  flockingOrigin = 'None',
  // nouveau : array de patch keys ('competition', 'title_winning', 'other')
  patches = [],
  patchOtherText = '',
  // legacy compat
  hasPatch = false,
  signed = false,
  signedType = '',
  signedOtherText = '',
  playerProfile = 'none',
  signedProofLevel = 'none',
  signedPersonalMessage = false,
  isRare = false,
  rareReason = '',
  seasonYear = 0,
  flockingPlayerNote = 0,
  auraLevel = 0,
}) {
  const [open, setOpen] = useState(false);

  const result = calculateEstimation({
    mode,
    modelType,
    competition,
    conditionOrigin,
    physicalState,
    flockingOrigin,
    patches,
    patchOtherText,
    hasPatch,
    signed,
    signedType,
    signedOtherText,
    playerProfile,
    signedProofLevel,
    signedPersonalMessage,
    isRare,
    rareReason,
    seasonYear,
    flockingPlayerNote,
    auraLevel,
  });

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

      {/* ── Détail coefficients ── */}
      {open && (
        <div className="px-3 pb-3 space-y-1 border-t border-border pt-2">
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
      )}
    </div>
  );
}
