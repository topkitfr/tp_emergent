import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { getEntityAutocomplete } from '@/lib/api';

export default function EntityAutocomplete({ entityType, value, onChange, onSelect, placeholder, className, testId }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
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
          setOpen(data.length > 0);
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

  return (
    <div ref={wrapperRef} className="relative">
      <Input
        value={displayValue}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder={placeholder}
        className={className}
        data-testid={testId}
        autoComplete="off"
      />
      {open && suggestions.length > 0 && (
        <div
          className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-card max-h-48 overflow-y-auto shadow-lg"
          data-testid={`${testId}-suggestions`}
        >
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
        </div>
      )}
    </div>
  );
}
