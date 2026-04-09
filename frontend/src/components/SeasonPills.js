// frontend/src/components/SeasonPills.js
// Pills scrollables horizontales pour les saisons d'une ligue
// Props:
//   seasons: [{ year, start, end, current }]
//   selected: number | null
//   onSelect: (year) => void
import React, { useRef } from 'react';

export default function SeasonPills({ seasons = [], selected, onSelect }) {
  const rowRef = useRef(null);

  if (!seasons.length) return null;

  // Tri décroissant — saison la plus récente en premier
  const sorted = [...seasons].sort((a, b) => b.year - a.year);

  return (
    <div
      ref={rowRef}
      className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      {sorted.map((s) => {
        const isActive = selected === s.year;
        const isCurrent = s.current;
        return (
          <button
            key={s.year}
            onClick={() => onSelect(isActive ? null : s.year)}
            className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 border text-xs font-medium transition-colors"
            style={{
              fontFamily: 'Barlow Condensed, sans-serif',
              letterSpacing: '0.05em',
              borderColor: isActive ? 'hsl(var(--primary))' : 'hsl(var(--border))',
              color: isActive ? 'hsl(var(--primary))' : isCurrent ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))',
              backgroundColor: isActive ? 'hsl(var(--primary) / 0.08)' : 'transparent',
              borderRadius: 0,
            }}
          >
            {isCurrent && (
              <span
                className="w-1.5 h-1.5 rounded-full animate-pulse"
                style={{ backgroundColor: 'hsl(var(--primary))' }}
              />
            )}
            {s.year}
            {isCurrent && (
              <span
                className="text-[9px] uppercase tracking-wider"
                style={{ color: 'hsl(var(--primary))', fontFamily: 'Barlow Condensed, sans-serif' }}
              >
                EN COURS
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
