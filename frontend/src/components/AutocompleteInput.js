import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AutocompleteInput({ field, value, onChange, placeholder, className, testId }) {
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(false);
  const wrapperRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (!focused || !value || value.length < 1) { setSuggestions([]); return; }
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetch(`${API}/autocomplete?field=${field}&q=${encodeURIComponent(value)}`, { credentials: 'include' })
        .then(r => r.json())
        .then(data => {
          const filtered = data.filter(s => s.toLowerCase() !== value.toLowerCase());
          setSuggestions(filtered);
          setOpen(filtered.length > 0);
        })
        .catch(() => setSuggestions([]));
    }, 200);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [value, field, focused]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={wrapperRef} className="relative">
      <Input
        value={value}
        onChange={e => onChange(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setTimeout(() => setFocused(false), 200)}
        placeholder={placeholder}
        className={className}
        data-testid={testId}
        autoComplete="off"
      />
      {open && suggestions.length > 0 && (
        <div className="absolute z-50 top-full left-0 right-0 mt-1 border border-border bg-card max-h-48 overflow-y-auto shadow-lg" data-testid={`${testId}-suggestions`}>
          {suggestions.map((s, i) => (
            <button
              key={i}
              type="button"
              className="w-full text-left px-3 py-2 text-sm hover:bg-secondary/50 truncate"
              style={{ transition: 'background-color 0.15s' }}
              onMouseDown={() => { onChange(s); setOpen(false); }}
              data-testid={`${testId}-suggestion-${i}`}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
