import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Plus } from 'lucide-react';
import { getEntityAutocomplete, createTeam, createLeague, createBrand, createPlayer } from '@/lib/api';
import { toast } from 'sonner';

const API_MAP = { team: createTeam, league: createLeague, brand: createBrand, player: createPlayer };

const ENTITY_FIELDS = {
  team: [
    { key: 'name', label: 'Name', required: true },
    { key: 'country', label: 'Country' },
    { key: 'city', label: 'City' },
  ],
  league: [
    { key: 'name', label: 'Name', required: true },
    { key: 'country_or_region', label: 'Country / Region' },
    { key: 'level', label: 'Level', type: 'select', options: ['domestic', 'continental', 'international', 'cup'] },
  ],
  brand: [
    { key: 'name', label: 'Name', required: true },
    { key: 'country', label: 'Country' },
  ],
  player: [
    { key: 'full_name', label: 'Full Name', required: true },
    { key: 'nationality', label: 'Nationality' },
    { key: 'positions', label: 'Positions (comma-separated)' },
  ],
};

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };

export default function EntityAutocomplete({ entityType, value, onChange, onSelect, placeholder, className, testId }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({});
  const [creating, setCreating] = useState(false);
  const wrapperRef = useRef(null);
  const debounceRef = useRef(null);
  const displayValue = typeof value === 'object' ? value?.label || '' : value || '';

  useEffect(() => {
    if (!focused || !displayValue || displayValue.length < 1) { setSuggestions([]); return; }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      getEntityAutocomplete(entityType, displayValue)
        .then(res => {
          const data = res.data || [];
          setSuggestions(data);
          setOpen(data.length > 0 || displayValue.length >= 2);
        })
        .catch(() => setSuggestions([]));
    }, 200);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [displayValue, entityType, focused]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    if (onSelect) onSelect(item);
    else onChange(item.label);
    setOpen(false);
  };

  const handleInputChange = (text) => {
    onChange(text);
  };

  const openCreateDialog = () => {
    const nameKey = entityType === 'player' ? 'full_name' : 'name';
    setCreateForm({ [nameKey]: displayValue });
    setShowCreate(true);
    setOpen(false);
  };

  const handleCreate = async () => {
    const createFn = API_MAP[entityType];
    if (!createFn) return;
    setCreating(true);
    try {
      const payload = { ...createForm };
      if (payload.positions && typeof payload.positions === 'string') {
        payload.positions = payload.positions.split(',').map(p => p.trim()).filter(Boolean);
      }
      const res = await createFn(payload);
      const entity = res.data;
      const labelField = entityType === 'player' ? 'full_name' : 'name';
      const idField = `${entityType}_id`;
      if (onSelect) onSelect({ id: entity[idField], label: entity[labelField], extra: '' });
      else onChange(entity[labelField]);
      toast.success(`${entityType.charAt(0).toUpperCase() + entityType.slice(1)} created`);
      setShowCreate(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || `Failed to create ${entityType}`);
    } finally {
      setCreating(false);
    }
  };

  const fields = ENTITY_FIELDS[entityType] || [];

  return (
    <>
      <div ref={wrapperRef} className="relative">
        <Input
          value={displayValue}
          onChange={e => handleInputChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 200)}
          placeholder={placeholder}
          className={className}
          data-testid={testId}
          autoComplete="off"
        />
        {open && (
          <div className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-card max-h-48 overflow-y-auto shadow-lg" data-testid={`${testId}-suggestions`}>
            {suggestions.map((s, i) => (
              <button
                key={s.id || i}
                type="button"
                className="w-full text-left px-3 py-2 text-sm hover:bg-secondary/50 flex items-center justify-between"
                style={{ transition: 'background-color 0.15s' }}
                onMouseDown={() => handleSelect(s)}
                data-testid={`${testId}-suggestion-${i}`}
              >
                <span className="truncate">{s.label}</span>
                {s.extra && <span className="text-xs text-muted-foreground ml-2 shrink-0">{s.extra}</span>}
              </button>
            ))}
            {displayValue.length >= 2 && (
              <button
                type="button"
                className="w-full text-left px-3 py-2 text-sm text-primary hover:bg-primary/10 flex items-center gap-2 border-t border-border"
                style={{ transition: 'background-color 0.15s' }}
                onMouseDown={openCreateDialog}
                data-testid={`${testId}-create-new`}
              >
                <Plus className="w-3 h-3" />
                Create "{displayValue}"
              </button>
            )}
          </div>
        )}
      </div>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="bg-card border-border sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg tracking-tight" style={labelStyle}>
              CREATE NEW {entityType.toUpperCase()}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 pt-2">
            {fields.map(f => (
              <div key={f.key} className="space-y-1">
                <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                  {f.label} {f.required && '*'}
                </Label>
                {f.type === 'select' ? (
                  <select
                    value={createForm[f.key] || ''}
                    onChange={e => setCreateForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                    className="w-full h-9 px-3 bg-card border border-border rounded-none text-sm"
                    data-testid={`create-${entityType}-${f.key}`}
                  >
                    <option value="">Select...</option>
                    {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : (
                  <Input
                    value={createForm[f.key] || ''}
                    onChange={e => setCreateForm(prev => ({ ...prev, [f.key]: e.target.value }))}
                    className="bg-card border-border rounded-none"
                    data-testid={`create-${entityType}-${f.key}`}
                  />
                )}
              </div>
            ))}
            <Button
              onClick={handleCreate}
              disabled={creating}
              className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid={`create-${entityType}-submit`}
            >
              {creating ? 'Creating...' : `Create ${entityType.charAt(0).toUpperCase() + entityType.slice(1)}`}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
