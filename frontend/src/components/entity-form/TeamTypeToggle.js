// frontend/src/components/entity-form/TeamTypeToggle.js
// Toggle binaire Club / Nationale pour le champ `is_national` d'une équipe.
import React from 'react';

const fieldStyle = { fontFamily: 'Barlow Condensed' };

const OPTIONS = [
  { label: '🏟️ Club',     value: false },
  { label: '🚩 Nationale', value: true  },
];

export default function TeamTypeToggle({ value, onChange }) {
  return (
    <div className="flex gap-2">
      {OPTIONS.map(opt => (
        <button
          key={String(opt.value)}
          type="button"
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 text-xs border rounded-none transition-colors ${
            value === opt.value
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-card border-border text-muted-foreground hover:border-primary/50'
          }`}
          style={fieldStyle}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
