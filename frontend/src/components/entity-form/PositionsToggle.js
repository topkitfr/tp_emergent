// frontend/src/components/entity-form/PositionsToggle.js
// Sélecteur multi-positions joueur (GK, CB, ST...). Toggle indépendant par
// position. Utilisé en saisie d'un player aussi bien à la création qu'à
// l'édition.
import React from 'react';
import { POSITIONS } from '@/lib/entityFields';

const fieldStyle = { fontFamily: 'Barlow Condensed' };

export default function PositionsToggle({ value, onChange }) {
  const current = Array.isArray(value) ? value : [];

  const toggle = (pos) => {
    onChange(
      current.includes(pos)
        ? current.filter(p => p !== pos)
        : [...current, pos]
    );
  };

  return (
    <div className="flex flex-wrap gap-1.5">
      {POSITIONS.map(pos => (
        <button
          key={pos}
          type="button"
          onClick={() => toggle(pos)}
          className={`px-2 py-0.5 text-[11px] border rounded-none transition-colors ${
            current.includes(pos)
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-card border-border text-muted-foreground hover:border-primary/50'
          }`}
          style={fieldStyle}
        >
          {pos}
        </button>
      ))}
    </div>
  );
}
