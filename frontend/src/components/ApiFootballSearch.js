// frontend/src/components/ApiFootballSearch.js
// Composant de recherche réutilisable vers API-Football (via backend proxy)
// Utilisé par: EntityEditDialog
//
// Props:
//   entityType : 'team' | 'league' | 'player'
//   onSelect   : fn(normalizedResult) → appelée quand l'utilisateur clique sur un résultat
//   placeholder: string (optionnel)
//   label      : string (optionnel)
//   filledName : string (optionnel) — affiché en badge quand un item est sélectionné

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Search, AlertCircle, RefreshCw } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';

const API_BASE = (process.env.REACT_APP_API_URL || 'http://localhost:8000/api').replace(/\/api$/, '');
const DEBOUNCE_MS = 400;

// ─── Normalisation ─────────────────────────────────────────────────────────────
// API-Football retourne des structures imbriquées selon le type :
//   team   → { team: { id, name, logo, country, city, founded, national }, venue: { name, capacity, surface, city, country, image } }
//   league → { league: { id, name, type, logo }, country: { name, code, flag } }
//   player → { player: { id, name, firstname, lastname, photo, nationality, birth:{date,place,country}, height, weight }, statistics: [...] }
//
// On aplatit tout pour que EntityEditDialog puisse lire les clés directement.

function normalizeTeam(item) {
  const t = item.team   || item;
  const v = item.venue  || {};
  return {
    // identité
    name:                 t.name             || '',
    country:              t.country          || '',
    city:                 t.city             || v.city || '',
    founded:              t.founded          ?? '',
    is_national:          t.national         ?? false,
    gender:               t.gender           || '',
    logo:                 t.logo             || '',
    // stade
    stadium_name:         v.name             || '',
    stadium_capacity:     v.capacity         ?? '',
    stadium_surface:      v.surface          || '',
    stadium_image_url:    v.image            || '',
    stadium_city:         v.city             || '',
    stadium_country:      v.country          || t.country || '',
    // ID interne
    apifootball_team_id:  t.id               ?? '',
  };
}

function normalizeLeague(item) {
  const l = item.league  || item;
  const c = item.country || {};
  const typeRaw   = (l.type || '').toLowerCase();
  const typeNorm  = typeRaw === 'cup' ? 'Cup' : typeRaw === 'league' ? 'League' : (l.type || '');
  return {
    name:                   l.name          || '',
    country_name:           c.name          || '',
    country_or_region:      c.name          || '',
    country_code:           c.code          || '',
    country_flag:           c.flag          || '',
    type:                   typeNorm,
    entity_type:            '',
    scope:                  '',
    gender:                 '',
    organizer:              '',
    apifootball_logo:       l.logo          || '',
    logo_url:               l.logo          || '',
    apifootball_league_id:  l.id            ?? '',
  };
}

function normalizePlayer(item) {
  const p    = item.player     || item;
  const b    = p.birth         || {};
  const stat = (item.statistics || [])[0];
  // hauteur / poids : API renvoie "183 cm" ou juste 183
  const parseNum = (v) => {
    if (!v && v !== 0) return '';
    const n = parseInt(String(v).replace(/[^0-9]/g, ''), 10);
    return isNaN(n) ? '' : n;
  };
  return {
    full_name:        p.name        || `${p.firstname || ''} ${p.lastname || ''}`.trim() || '',
    first_name:       p.firstname   || '',
    last_name:        p.lastname    || '',
    nationality:      p.nationality || stat?.team?.country || '',
    birth_date:       b.date        || '',
    birth_place:      b.place       || '',
    birth_country:    b.country     || '',
    photo:            p.photo       || '',
    photo_url:        p.photo       || '',
    height:           parseNum(p.height),
    weight:           parseNum(p.weight),
    preferred_foot:   '',
    preferred_number: '',
    positions:        stat?.games?.position ? [stat.games.position] : [],
    // ID interne
    apifootball_id:   p.id          ?? '',
  };
}

function normalizeItem(item, entityType) {
  if (entityType === 'team')   return normalizeTeam(item);
  if (entityType === 'league') return normalizeLeague(item);
  if (entityType === 'player') return normalizePlayer(item);
  return item;
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────
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

// ─── ResultRow ────────────────────────────────────────────────────────────────
function ResultRow({ item, entityType, onClick }) {
  const logoSrc =
    entityType === 'player'
      ? item.player?.photo || item.photo
      : entityType === 'league'
      ? item.league?.logo  || item.logo
      : item.team?.logo    || item.logo;

  const name =
    entityType === 'player'
      ? item.player?.name  || item.name
      : entityType === 'league'
      ? item.league?.name  || item.name
      : item.team?.name    || item.name;

  const sub =
    entityType === 'player'
      ? [item.statistics?.[0]?.team?.name, item.player?.nationality].filter(Boolean).join(' · ')
      : entityType === 'league'
      ? item.country?.name
      : item.team?.country;

  const flagSrc = item.country?.flag;

  return (
    <button
      type="button"
      onClick={() => onClick(item)}
      className="w-full flex items-center gap-3 px-3 py-2 hover:bg-accent transition-colors text-left group"
    >
      {logoSrc ? (
        <img src={logoSrc} alt="" className="w-7 h-7 object-contain shrink-0" loading="lazy"
          onError={e => { e.currentTarget.style.opacity = '0.3'; }} />
      ) : (
        <div className="w-7 h-7 bg-muted rounded-sm shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate" style={{ fontFamily: 'Barlow Condensed' }}>{name}</p>
        {sub && (
          <p className="text-xs text-muted-foreground flex items-center gap-1 truncate">
            {flagSrc && <img src={flagSrc} alt="" className="w-4 h-3 object-cover" />}
            {sub}
          </p>
        )}
      </div>
      <Badge variant="outline" className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
        style={{ fontFamily: 'Barlow Condensed' }}>API-Football</Badge>
    </button>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function ApiFootballSearch({
  entityType = 'team',
  onSelect,
  placeholder,
  label,
  filledName = '',
}) {
  const [query, setQuery]     = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);
  const [open, setOpen]       = useState(false);
  const [selected, setSelected] = useState(null);

  const timerRef     = useRef(null);
  const containerRef = useRef(null);

  const defaultPlaceholders = {
    team:   'Rechercher un club via API-Football...',
    league: 'Rechercher une compétition via API-Football...',
    player: 'Rechercher un joueur via API-Football...',
  };

  const fetchResults = useCallback(async (q) => {
    if (!q || q.trim().length < 2) { setResults([]); setOpen(false); return; }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_BASE}/api/apifootball/search/${entityType}?q=${encodeURIComponent(q.trim())}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResults(data.results || data || []);
      setOpen(true);
    } catch (err) {
      setError(err.message || 'Erreur réseau');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [entityType]);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setSelected(null);
    clearTimeout(timerRef.current);
    if (val.trim().length < 2) { setOpen(false); setResults([]); return; }
    timerRef.current = setTimeout(() => fetchResults(val), DEBOUNCE_MS);
  };

  const handleSelect = (item) => {
    // Afficher le nom brut dans l'input de recherche
    const rawName =
      entityType === 'player' ? item.player?.name || item.name
      : entityType === 'league' ? item.league?.name || item.name
      : item.team?.name || item.name;
    setQuery(rawName);
    setSelected(item);
    setOpen(false);
    // ✅ On passe les données NORMALISÉES (à plat) au parent
    onSelect?.(normalizeItem(item, entityType));
  };

  // Fermer au clic extérieur
  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="space-y-1" ref={containerRef}>
      {label && (
        <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
          {label}
        </Label>
      )}

      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
        <Input
          value={query}
          onChange={handleChange}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder || defaultPlaceholders[entityType]}
          className="pl-8 rounded-none h-8 text-sm bg-card border-border"
          autoComplete="off"
        />
        {(selected || filledName) && (
          <Badge variant="secondary"
            className="absolute right-2 top-1/2 -translate-y-1/2 text-[9px] px-1.5 py-0 rounded-sm"
            style={{ fontFamily: 'Barlow Condensed' }}
          >
            API ✓
          </Badge>
        )}
      </div>

      {open && (
        <div className="absolute z-50 w-full max-w-sm bg-card border border-border shadow-md rounded-sm overflow-hidden">
          {loading && <><SkeletonRow /><SkeletonRow /><SkeletonRow /></>}

          {!loading && error && (
            <div className="flex items-center justify-between px-3 py-2 text-xs text-destructive gap-2">
              <span className="flex items-center gap-1.5">
                <AlertCircle className="w-3.5 h-3.5" />{error}
              </span>
              <button type="button" onClick={() => fetchResults(query)}
                className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors">
                <RefreshCw className="w-3 h-3" /> Réessayer
              </button>
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="px-3 py-3 text-xs text-muted-foreground text-center" style={{ fontFamily: 'DM Sans' }}>
              Aucun résultat pour «&nbsp;<em>{query}</em>&nbsp;»
            </div>
          )}

          {!loading && !error && results.length > 0 && (
            <div className="max-h-52 overflow-y-auto">
              {results.slice(0, 8).map((item, idx) => (
                <ResultRow key={idx} item={item} entityType={entityType} onClick={handleSelect} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
