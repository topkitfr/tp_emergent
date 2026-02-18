import React from 'react';
import { calculateEstimation } from '@/utils/estimation';
import { TrendingUp } from 'lucide-react';

export default function EstimationBreakdown({
  modelType, competition, conditionOrigin, physicalState, flockingOrigin,
  signed, signedProof, seasonYear
}) {
  const est = calculateEstimation({
    modelType, competition, conditionOrigin, physicalState, flockingOrigin,
    signed, signedProof, seasonYear,
  });

  return (
    <div className="border border-accent/30 bg-accent/5 p-4 space-y-3" data-testid="estimation-breakdown">
      <div className="flex items-center justify-between">
        <h4 className="text-xs uppercase tracking-wider flex items-center gap-1.5" style={{ fontFamily: 'Barlow Condensed' }}>
          <TrendingUp className="w-4 h-4 text-accent" />
          TOPKIT ESTIMATION
        </h4>
        <div className="font-mono text-xl text-accent" data-testid="estimation-total">
          {est.estimatedPrice.toFixed(2)} &euro;
        </div>
      </div>

      <div className="h-px bg-accent/20" />

      {/* Formula */}
      <div className="text-[11px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
        Base ({est.modelType}): <span className="font-mono text-foreground">{est.basePrice} &euro;</span>
        {' '}&times;{' '}
        (1 + <span className="font-mono text-foreground">{est.coeffSum >= 0 ? '+' : ''}{est.coeffSum}</span>)
      </div>

      {/* Breakdown lines */}
      {est.breakdown.length > 0 && (
        <div className="space-y-1">
          {est.breakdown.map((item, i) => (
            <div key={i} className="flex items-center justify-between text-[11px]" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              <span className="text-muted-foreground">{item.label}</span>
              <span className={`font-mono ${item.coeff >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {item.coeff >= 0 ? '+' : ''}{item.coeff}
              </span>
            </div>
          ))}
        </div>
      )}

      {est.breakdown.length === 0 && (
        <p className="text-[11px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          Fill in the fields above to see the estimation breakdown
        </p>
      )}
    </div>
  );
}
