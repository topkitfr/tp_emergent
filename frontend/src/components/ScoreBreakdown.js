// frontend/src/components/ScoreBreakdown.js
// Breakdown visuel du score d'un joueur (palmarès + aura + awards)
// Props:
//   scorePalmares: number
//   aura: number
//   note: number           — total
//   individualAwards: [{ award_name, year, count }]
//   collapsible: boolean   — affiche un toggle (défaut: true)
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Trophy, Users, Star } from 'lucide-react';

const SCORE_TIER = (s) => {
  if (s >= 800) return { label: 'Légende',  color: '#f59e0b' };
  if (s >= 500) return { label: 'Élite',    color: '#a855f7' };
  if (s >= 200) return { label: 'Confirmé', color: '#3b82f6' };
  if (s >= 50)  return { label: 'Pro',      color: '#22c55e' };
  return              { label: 'Émergent',  color: '#6b7280' };
};

function Bar({ value, max, color }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="flex-1 h-1 bg-border rounded-full overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${pct}%`, backgroundColor: color }}
      />
    </div>
  );
}

export default function ScoreBreakdown({
  scorePalmares = 0,
  aura = 0,
  note = 0,
  individualAwards = [],
  collapsible = true,
}) {
  const [open, setOpen] = useState(false);
  const tier = SCORE_TIER(note);

  // Score awards individuels ≈ somme des poids (approx. depuis IndividualAwardEntry.count)
  const awardsScore = individualAwards.reduce((acc, a) => acc + (a.count ?? 1) * 5, 0);
  const palmScore   = Math.max(0, scorePalmares - awardsScore);
  const maxVal      = Math.max(note, 1);

  const rows = [
    { icon: <Trophy  className="w-3.5 h-3.5" />, label: 'Trophées collectifs', value: palmScore,   color: '#f59e0b' },
    { icon: <Star    className="w-3.5 h-3.5" />, label: 'Awards individuels',   value: awardsScore, color: '#a855f7' },
    { icon: <Users   className="w-3.5 h-3.5" />, label: 'Aura communautaire',   value: aura,        color: '#01696f' },
  ];

  return (
    <div className="border border-border bg-card">
      {/* Header — toujours visible */}
      <button
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-muted/40 transition-colors"
        onClick={() => collapsible && setOpen(o => !o)}
        style={{ cursor: collapsible ? 'pointer' : 'default' }}
      >
        <div className="flex items-center gap-3">
          <span
            className="text-[11px] uppercase tracking-wider font-semibold"
            style={{ fontFamily: 'Barlow Condensed, sans-serif', color: tier.color }}
          >
            {tier.label}
          </span>
          <span
            className="font-mono font-bold text-sm"
            style={{ color: tier.color }}
          >
            {Math.round(note)}
          </span>
          <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>pts</span>
        </div>
        {collapsible && (
          open
            ? <ChevronUp  className="w-4 h-4 text-muted-foreground" />
            : <ChevronDown className="w-4 h-4 text-muted-foreground" />
        )}
      </button>

      {/* Détail — collapsible */}
      {(!collapsible || open) && (
        <div className="px-4 pb-4 pt-1 border-t border-border space-y-3">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center gap-3">
              <span style={{ color: row.color }}>{row.icon}</span>
              <span
                className="w-40 text-xs text-muted-foreground shrink-0"
                style={{ fontFamily: 'DM Sans' }}
              >
                {row.label}
              </span>
              <Bar value={row.value} max={maxVal} color={row.color} />
              <span
                className="w-12 text-right text-xs font-mono"
                style={{ color: row.color }}
              >
                {Math.round(row.value)}
              </span>
            </div>
          ))}
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>TOTAL</span>
            <span className="font-mono font-bold text-sm" style={{ color: tier.color }}>
              {Math.round(note)} pts
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
