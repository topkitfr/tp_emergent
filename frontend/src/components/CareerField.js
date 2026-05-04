// frontend/src/components/CareerField.js
// Champ liste dynamique pour la carrière d'un joueur
// Format : [{ club_id: string|null, club_name: string, type: string, year_start: number|string, year_end: number|string, fee: string }]
import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Plus, Trash2 } from 'lucide-react';
import { getEntityAutocomplete } from '@/lib/api';

const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none h-8 text-sm';

const TRANSFER_TYPES = ['Permanent', 'Prêt', 'Free', 'Youth', 'Inconnu'];

function ClubAutocomplete({ value, onChange, onSelect }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const wrapperRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (!focused || !value || value.length < 1) { setSuggestions([]); setOpen(false); return; }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      getEntityAutocomplete('team', value)
        .then(res => {
          const data = res.data || [];
          setSuggestions(data);
          setOpen(data.length > 0);
        })
        .catch(() => setSuggestions([]));
    }, 200);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [value, focused]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={wrapperRef} className="relative flex-1">
      <Input
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder="AS Roma"
        className={inputClass}
        autoComplete="off"
      />
      {open && suggestions.length > 0 && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-card max-h-40 overflow-y-auto shadow-lg">
          {suggestions.map((s, i) => (
            <button
              key={s.id || i}
              type="button"
              className="w-full text-left px-3 py-1.5 text-xs hover:bg-secondary/50 flex items-center gap-2"
              style={{ transition: 'background-color 0.15s' }}
              onMouseDown={() => {
                onSelect(s);
                setOpen(false);
              }}
            >
              {s.extra_img && (
                <img src={s.extra_img} alt="" className="w-4 h-4 object-contain shrink-0" />
              )}
              <span className="truncate">{s.label}</span>
              {s.extra && <span className="text-muted-foreground ml-auto shrink-0">{s.extra}</span>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * CareerField
 *
 * Props:
 * - value: Array<{ club_id, club_name, type, year_start, year_end, fee }>
 * - onChange: fn(newArray)
 */
export default function CareerField({ value = [], onChange }) {
  const entries = Array.isArray(value) ? value : [];

  const handleAdd = () => {
    onChange([...entries, { club_id: null, club_name: '', type: 'Permanent', year_start: '', year_end: '', fee: '' }]);
  };

  const handleRemove = (idx) => {
    onChange(entries.filter((_, i) => i !== idx));
  };

  const handleChange = (idx, field, val) => {
    const updated = entries.map((e, i) =>
      i === idx ? { ...e, [field]: val } : e
    );
    onChange(updated);
  };

  const handleClubSelect = (idx, suggestion) => {
    const updated = entries.map((e, i) =>
      i === idx ? { ...e, club_name: suggestion.label, club_id: suggestion.id || null } : e
    );
    onChange(updated);
  };

  return (
    <div className="space-y-2">
      {entries.length === 0 && (
        <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          Aucune entrée de carrière renseignée.
        </p>
      )}

      {entries.length > 0 && (
        <div className="flex gap-2 text-[10px] text-muted-foreground mb-1" style={fieldStyle}>
          <span className="flex-1 pl-0.5">CLUB</span>
          <span className="w-24 pl-0.5">TYPE</span>
          <span className="w-16 pl-0.5">DÉBUT</span>
          <span className="w-16 pl-0.5">FIN</span>
          <span className="w-20 pl-0.5">MONTANT</span>
          <span className="w-6" />
        </div>
      )}

      {entries.map((entry, idx) => (
        <div key={idx} className="flex gap-2 items-center">
          {/* Club avec autocomplete */}
          <ClubAutocomplete
            value={entry.club_name || ''}
            onChange={val => handleChange(idx, 'club_name', val)}
            onSelect={s => handleClubSelect(idx, s)}
          />

          {/* Type de transfert */}
          <div className="w-24">
            <Select
              value={entry.type || 'Permanent'}
              onValueChange={val => handleChange(idx, 'type', val)}
            >
              <SelectTrigger className="bg-card border-border rounded-none h-8 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TRANSFER_TYPES.map(t => (
                  <SelectItem key={t} value={t} className="text-xs">{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Année début */}
          <Input
            type="number"
            value={entry.year_start || ''}
            onChange={e => handleChange(idx, 'year_start', e.target.value ? parseInt(e.target.value) : '')}
            placeholder="2000"
            className={`${inputClass} w-16`}
          />

          {/* Année fin */}
          <Input
            type="number"
            value={entry.year_end || ''}
            onChange={e => handleChange(idx, 'year_end', e.target.value ? parseInt(e.target.value) : '')}
            placeholder="2017"
            className={`${inputClass} w-16`}
          />

          {/* Montant */}
          <Input
            value={entry.fee || ''}
            onChange={e => handleChange(idx, 'fee', e.target.value)}
            placeholder="Free"
            className={`${inputClass} w-20`}
          />

          <button
            type="button"
            onClick={() => handleRemove(idx)}
            className="text-destructive hover:text-destructive/80 transition-colors p-1 shrink-0"
            aria-label="Supprimer cette entrée"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleAdd}
        className="rounded-none border-dashed h-7 text-xs w-full"
        style={fieldStyle}
      >
        <Plus className="w-3 h-3 mr-1" />
        Ajouter une entrée de carrière
      </Button>
    </div>
  );
}
