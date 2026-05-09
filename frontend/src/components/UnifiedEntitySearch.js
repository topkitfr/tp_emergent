// frontend/src/components/UnifiedEntitySearch.js
// Barre de recherche dans la DB Topkit pour les dialogs d'entités
// (team, player, league, brand, sponsor). Sert principalement à éviter
// les doublons en montrant les fiches déjà existantes au moment de la saisie.
//
// Props:
//   entityType  : 'team' | 'player' | 'league' | 'brand' | 'sponsor'
//   onSelectDb  : fn(item)  — item DB sélectionné { id, label, extra, status, logo_url, ... }
//   placeholder : string (optionnel)
//   disabled    : bool (optionnel)

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Search, Database, CheckCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const BACKEND = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '');
const DEBOUNCE_DB = 200;

const fieldStyle = { fontFamily: 'Barlow Condensed' };
const dmSans     = { fontFamily: 'DM Sans' };

function getDbEndpoint(entityType, query) {
  return `${BACKEND}/api/autocomplete?type=${entityType}&q=${encodeURIComponent(query)}`;
}

function extractName(item) {
  return item.label || item.name || item.full_name || '';
}

function extractSub(item) {
  const parts = [item.extra, item.status && item.status !== 'approved' ? `(${item.status})` : null].filter(Boolean);
  return parts.join(' · ');
}

function extractLogo(item) {
  return item.logo_url || item.crest_url || item.photo_url || null;
}

function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 px-3 py-2 animate-pulse">
      <div className="w-7 h-7 rounded-sm bg-muted shrink-0" />
      <div className="flex-1 space-y-1">
        <div className="h-3 bg-muted rounded w-2/3" />
        <div className="h-2.5 bg-muted rounded w-1/3" />
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, label, count }) {
  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-border bg-muted/40">
      <Icon className="w-3 h-3 text-muted-foreground" />
      <span className="text-[10px] uppercase tracking-widest font-medium text-muted-foreground" style={fieldStyle}>
        {label}
      </span>
      {count > 0 && (
        <span className="ml-auto text-[10px] text-muted-foreground" style={dmSans}>{count}</span>
      )}
    </div>
  );
}

function ResultRow({ item, onClick }) {
  const name = extractName(item);
  const sub  = extractSub(item);
  const logo = extractLogo(item);

  return (
    <button
      type="button"
      onClick={() => onClick(item)}
      className="w-full flex items-center gap-3 px-3 py-2 hover:bg-accent transition-colors text-left group"
    >
      {logo ? (
        <img
          src={logo}
          alt=""
          width={28}
          height={28}
          className="w-7 h-7 object-contain shrink-0 rounded-sm"
          loading="lazy"
          onError={e => { e.currentTarget.style.opacity = '0.2'; }}
        />
      ) : (
        <div className="w-7 h-7 bg-muted rounded-sm shrink-0 flex items-center justify-center">
          <span className="text-[10px] text-muted-foreground" style={fieldStyle}>
            {name.charAt(0).toUpperCase()}
          </span>
        </div>
      )}

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate" style={fieldStyle}>{name}</p>
        {sub && (
          <p className="text-xs text-muted-foreground truncate" style={dmSans}>{sub}</p>
        )}
      </div>

      <Badge
        variant="outline"
        className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 border-emerald-500/40 text-emerald-600 dark:text-emerald-400 opacity-80 group-hover:opacity-100 transition-opacity"
        style={fieldStyle}
      >
        <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />
        En base
      </Badge>
    </button>
  );
}

export default function UnifiedEntitySearch({
  entityType = 'team',
  onSelectDb,
  placeholder,
  disabled = false,
}) {
  const [query, setQuery]       = useState('');
  const [results, setResults]   = useState([]);
  const [loading, setLoading]   = useState(false);
  const [searched, setSearched] = useState(false);
  const [open, setOpen]         = useState(false);
  const [selected, setSelected] = useState(false);

  const timer        = useRef(null);
  const containerRef = useRef(null);

  const defaultPlaceholders = {
    team:    'Rechercher un club dans la base...',
    player:  'Rechercher un joueur dans la base...',
    league:  'Rechercher une compétition dans la base...',
    brand:   'Rechercher une marque dans la base...',
    sponsor: 'Rechercher un sponsor dans la base...',
  };

  const fetchDb = useCallback(async (q) => {
    setLoading(true);
    setSearched(false);
    try {
      const res = await fetch(getDbEndpoint(entityType, q));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.results || []);
      setResults(items.slice(0, 8));
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
      setSearched(true);
    }
  }, [entityType]);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setSelected(false);
    if (val.trim().length < 2) {
      setOpen(false);
      setResults([]);
      setSearched(false);
      clearTimeout(timer.current);
      return;
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => fetchDb(val.trim()), DEBOUNCE_DB);
    setOpen(true);
  };

  const handleSelect = (item) => {
    setQuery(extractName(item));
    setSelected(true);
    setOpen(false);
    onSelectDb?.(item);
  };

  const showDropdown = open && query.trim().length >= 2;

  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
        <Input
          value={query}
          onChange={handleChange}
          onFocus={() => (results.length > 0 || searched) && query.trim().length >= 2 && setOpen(true)}
          placeholder={placeholder || defaultPlaceholders[entityType]}
          className="pl-8 pr-20 rounded-none h-9 text-sm bg-card border-border"
          autoComplete="off"
          disabled={disabled}
        />
        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1.5 pointer-events-none">
          {loading && (
            <svg className="w-3.5 h-3.5 animate-spin text-muted-foreground" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeDashoffset="20" />
            </svg>
          )}
          {!loading && selected && (
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0 rounded-sm border-emerald-500/40 text-emerald-600 dark:text-emerald-400" style={fieldStyle}>
              <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />DB
            </Badge>
          )}
        </div>
      </div>

      {showDropdown && (
        <div className="absolute z-50 left-0 right-0 top-full mt-0.5 bg-card border border-border shadow-lg rounded-sm overflow-hidden max-h-80 overflow-y-auto">
          <SectionHeader icon={Database} label="Déjà en base" count={results.length} />
          {loading ? (
            <><SkeletonRow /><SkeletonRow /></>
          ) : results.length === 0 ? (
            <p className="px-3 py-2 text-xs text-muted-foreground italic" style={dmSans}>
              Aucune fiche existante pour « <em>{query}</em> »
            </p>
          ) : (
            results.map((item, idx) => (
              <ResultRow key={`db-${item.id || idx}`} item={item} onClick={handleSelect} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
