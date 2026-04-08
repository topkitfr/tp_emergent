// frontend/src/components/IndividualAwardsField.js
// Champ liste dynamique pour individual_awards dans le form joueur
// Format : [{ title: string, year: number|string }]
import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Plus, Trash2 } from 'lucide-react';

const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none h-8 text-sm';

/**
 * IndividualAwardsField
 *
 * Props:
 * - value: Array<{ title: string, year: string|number }>
 * - onChange: fn(newArray)
 */
export default function IndividualAwardsField({ value = [], onChange }) {
  const awards = Array.isArray(value) ? value : [];

  const handleAdd = () => {
    onChange([...awards, { title: '', year: '' }]);
  };

  const handleRemove = (idx) => {
    onChange(awards.filter((_, i) => i !== idx));
  };

  const handleChange = (idx, field, val) => {
    const updated = awards.map((a, i) =>
      i === idx ? { ...a, [field]: val } : a
    );
    onChange(updated);
  };

  return (
    <div className="space-y-2">
      {awards.length === 0 && (
        <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          Aucune distinction renseignée.
        </p>
      )}

      {awards.map((award, idx) => (
        <div key={idx} className="flex gap-2 items-center">
          <Input
            value={award.title || ''}
            onChange={e => handleChange(idx, 'title', e.target.value)}
            placeholder="Ballon d'Or"
            className={`${inputClass} flex-1`}
          />
          <Input
            type="number"
            value={award.year || ''}
            onChange={e => handleChange(idx, 'year', e.target.value ? parseInt(e.target.value) : '')}
            placeholder="2018"
            className={`${inputClass} w-20`}
          />
          <button
            type="button"
            onClick={() => handleRemove(idx)}
            className="text-destructive hover:text-destructive/80 transition-colors p-1"
            aria-label="Supprimer cette distinction"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}

      {awards.length > 0 && (
        <div className="flex gap-4 text-[10px] text-muted-foreground mb-1" style={fieldStyle}>
          <span className="flex-1 pl-0.5">TITRE</span>
          <span className="w-20 pl-0.5">ANNÉE</span>
          <span className="w-6" />
        </div>
      )}

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleAdd}
        className="rounded-none border-dashed h-7 text-xs w-full"
        style={fieldStyle}
      >
        <Plus className="w-3 h-3 mr-1" />
        Ajouter une distinction
      </Button>
    </div>
  );
}
