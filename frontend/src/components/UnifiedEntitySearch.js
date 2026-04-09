// frontend/src/components/UnifiedEntitySearch.js
// Barre de recherche unifiée pour les dialogs d'entités (team, player, league, brand, sponsor).
// Affiche dans le même dropdown :
//   - Section « Déjà en base »  → /api/autocomplete?type=<entity>&q=<query>   (route existante)
//   - Section « API-Football »  → /api/apifootball/search/<entity>?q=<query>
//
// Props:
//   entityType   : 'team' | 'player' | 'league' | 'brand' | 'sponsor'
//   onSelectDb   : fn(item)  — item DB sélectionné { id, label, extra, status, logo_url, ... }
//   onSelectApi  : fn(normalized)  — item API-Football normalisé (à plat, prêt pour préfill)
//   placeholder  : string (optionnel)
//   disabled     : bool (optionnel)

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Search, Database, Zap, AlertCircle, RefreshCw, CheckCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const BACKEND = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/+$/, '');
const DEBOUNCE_DB  = 200;
const DEBOUNCE_API = 350;

const fieldStyle = { fontFamily: 'Barlow Condensed' };
const dmSans     = { fontFamily: 'DM Sans' };

function getDbEndpoint(entityType, query) {
  return `${BACKEND}/api/autocomplete?type=${entityType}&q=${encodeURIComponent(query)}`;
}
function getApiEndpoint(entityType, query) {
  return `${BACKEND}/api/apifootball/search/${entityType}?q=${encodeURIComponent(query)}`;
}

// ── Normalisation API-Football → objet à plat ──────────────────────────────────
function normalizeTeam(item) {
  const t = item.team  || item;
  const v = item.venue || {};
  return {
    name:                t.name            || '',
    country:             t.country         || '',
    city:                t.city            || v.city || '',
    founded:             t.founded         ?? '',
    is_national:         t.national        ?? false,
    gender:              t.gender          || '',
    logo:                t.logo            || '',
    stadium_name:        v.name            || '',
    stadium_capacity:    v.capacity        ?? '',
    stadium_surface:     v.surface         || '',
    stadium_image_url:   v.image           || '',
    stadium_city:        v.city            || '',
    stadium_country:     v.country         || t.country || '',
    apifootball_team_id: t.id              ?? '',
  };
}

function normalizeLeague(item) {
  const l = item.league  || item;
  const c = item.country || {};
  const typeRaw  = (l.type || '').toLowerCase();
  const typeNorm = typeRaw === 'cup' ? 'Cup' : typeRaw === 'league' ? 'League' : (l.type || '');
  return {
    name:                  l.name  || '',
    country_name:          c.name  || '',
    country_or_region:     c.name  || '',
    country_code:          c.code  || '',
    country_flag:          c.flag  || '',
    type:                  typeNorm,
    entity_type:           '',
    scope:                 '',
    gender:                '',
    organizer:             '',
    apifootball_logo:      l.logo  || '',
    logo_url:              l.logo  || '',
    apifootball_league_id: l.id    ?? '',
  };
}

function normalizePlayer(item) {
  const p    = item.player     || item;
  const b    = p.birth         || {};
  const stat = (item.statistics || [])[0];
  const parseNum = (v) => {
    if (!v && v !== 0) return '';
    const n = parseInt(String(v).replace(/[^0-9]/g, ''), 10);
    return isNaN(n) ? '' : n;
  };
  return {
    full_name:        p.name       || `${p.firstname || ''} ${p.lastname || ''}`.trim() || '',
    first_name:       p.firstname  || '',
    last_name:        p.lastname   || '',
    nationality:      p.nationality || stat?.team?.country || '',
    birth_date:       b.date       || '',
    birth_place:      b.place      || '',
    birth_country:    b.country    || '',
    photo:            p.photo      || '',
    photo_url:        p.photo      || '',
    height:           parseNum(p.height),
    weight:           parseNum(p.weight),
    preferred_foot:   '',
    preferred_number: '',
    positions:        stat?.games?.position ? [stat.games.position] : [],
    apifootball_id:   p.id         ?? '',
  };
}

function normalizeApiItem(item, entityType) {
  if (entityType === 'team')   return normalizeTeam(item);
  if (entityType === 'league') return normalizeLeague(item);
  if (entityType === 'player') return normalizePlayer(item);
  return item;
}

// ── Helpers affichage (item brut) ──────────────────────────────────────────────
function extractName(item, entityType, source) {
  if (source === 'db') return item.label || item.name || item.full_name || '';
  if (entityType === 'player') return item.player?.name || item.name || '';
  if (entityType === 'league') return item.league?.name || item.name || '';
  return item.team?.name || item.name || '';
}

function extractSub(item, entityType, source) {
  if (source === 'db') {
    const parts = [item.extra, item.status !== 'approved' ? `(${item.status})` : null].filter(Boolean);
    return parts.join(' · ');
  }
  if (entityType === 'player') return [item.statistics?.[0]?.team?.name, item.player?.nationality].filter(Boolean).join(' · ');
  if (entityType === 'league') return item.country?.name || '';
  return item.team?.country || '';
}

function extractLogo(item, entityType, source) {
  if (source === 'db') return item.logo_url || item.crest_url || item.photo_url || null;
  if (entityType === 'player') return item.photo || item.player?.photo || null;
  if (entityType === 'league') return item.league?.logo || item.logo || null;
  return item.team?.logo || item.logo || null;
}

function extractFlag(item, entityType, source) {
  if (source === 'api' && (entityType === 'league' || entityType === 'team')) {
    return item.country?.flag || null;
  }
  return null;
}

// ── Skeleton ───────────────────────────────────────────────────────────────────
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

// ── En-tête de section ────────────────────────────────────────────────────────────
function SectionHeader({ icon: Icon, label, count, color }) {
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 border-b border-border ${color || 'bg-muted/40'}`}>
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

// ── Ligne de résultat ──────────────────────────────────────────────────────────────
function ResultRow({ item, entityType, source, onClick }) {
  const name = extractName(item, entityType, source);
  const sub  = extractSub(item, entityType, source);
  const logo = extractLogo(item, entityType, source);
  const flag = extractFlag(item, entityType, source);
  const isDb = source === 'db';

  return (
    <button
      type="button"
      onClick={() => onClick(item, source)}
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
          <p className="text-xs text-muted-foreground flex items-center gap-1 truncate" style={dmSans}>
            {flag && <img src={flag} alt="" width={16} height={12} className="object-cover shrink-0" />}
            {sub}
          </p>
        )}
      </div>

      {isDb ? (
        <Badge
          variant="outline"
          className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 border-emerald-500/40 text-emerald-600 dark:text-emerald-400 opacity-80 group-hover:opacity-100 transition-opacity"
          style={fieldStyle}
        >
          <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />
          En base
        </Badge>
      ) : (
        <Badge
          variant="outline"
          className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
          style={fieldStyle}
        >
          <Zap className="w-2.5 h-2.5 mr-0.5 inline" />
          API
        </Badge>
      )}
    </button>
  );
}

// ── Composant principal ──────────────────────────────────────────────────────────────
export default function UnifiedEntitySearch({
  entityType = 'team',
  onSelectDb,
  onSelectApi,
  placeholder,
  disabled = false,
}) {
  const [query, setQuery]           = useState('');
  const [dbResults, setDbResults]   = useState([]);
  const [apiResults, setApiResults] = useState([]);
  const [loadingDb, setLoadingDb]   = useState(false);
  const [loadingApi, setLoadingApi] = useState(false);
  const [dbSearched, setDbSearched] = useState(false);
  const [errorApi, setErrorApi]     = useState(null);
  const [open, setOpen]             = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);

  const timerDb      = useRef(null);
  const timerApi     = useRef(null);
  const containerRef = useRef(null);

  const defaultPlaceholders = {
    team:    'Rechercher un club... (DB + API-Football)',
    player:  'Rechercher un joueur... (DB + API-Football)',
    league:  'Rechercher une compétition... (DB + API-Football)',
    brand:   'Rechercher une marque dans la base...',
    sponsor: 'Rechercher un sponsor dans la base...',
  };

  const fetchDb = useCallback(async (q) => {
    setLoadingDb(true);
    setDbSearched(false);
    try {
      const res = await fetch(getDbEndpoint(entityType, q));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.results || []);
      setDbResults(items.slice(0, 6));
    } catch {
      setDbResults([]);
    } finally {
      setLoadingDb(false);
      setDbSearched(true);
    }
  }, [entityType]);

  const fetchApi = useCallback(async (q) => {
    setLoadingApi(true);
    setErrorApi(null);
    try {
      const res = await fetch(getApiEndpoint(entityType, q));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const items = Array.isArray(data) ? data : (data.results || data.response || []);
      setApiResults(items.slice(0, 6));
    } catch (err) {
      setErrorApi(err.message || 'Erreur réseau');
      setApiResults([]);
    } finally {
      setLoadingApi(false);
    }
  }, [entityType]);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    setSelectedSource(null);
    if (val.trim().length < 2) {
      setOpen(false);
      setDbResults([]);
      setApiResults([]);
      setDbSearched(false);
      clearTimeout(timerDb.current);
      clearTimeout(timerApi.current);
      return;
    }
    clearTimeout(timerDb.current);
    clearTimeout(timerApi.current);
    timerDb.current  = setTimeout(() => fetchDb(val.trim()), DEBOUNCE_DB);
    timerApi.current = setTimeout(() => fetchApi(val.trim()), DEBOUNCE_API);
    setOpen(true);
  };

  // ✔️ Normalise l'item API avant de le passer au parent
  const handleSelect = (item, source) => {
    const name = extractName(item, entityType, source);
    setQuery(name);
    setSelectedSource(source);
    setOpen(false);
    if (source === 'db')  onSelectDb?.(item);
    if (source === 'api') onSelectApi?.(normalizeApiItem(item, entityType));
  };

  const isLoading      = loadingDb || loadingApi;
  const hasResults     = dbResults.length > 0 || apiResults.length > 0;
  const showDropdown   = open && query.trim().length >= 2;
  const showApiSection = ['team', 'player', 'league'].includes(entityType);

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
          onFocus={() => (hasResults || dbSearched) && query.trim().length >= 2 && setOpen(true)}
          placeholder={placeholder || defaultPlaceholders[entityType]}
          className="pl-8 pr-20 rounded-none h-9 text-sm bg-card border-border"
          autoComplete="off"
          disabled={disabled}
        />
        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1.5 pointer-events-none">
          {isLoading && (
            <svg className="w-3.5 h-3.5 animate-spin text-muted-foreground" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeDashoffset="20" />
            </svg>
          )}
          {!isLoading && selectedSource === 'db' && (
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0 rounded-sm border-emerald-500/40 text-emerald-600 dark:text-emerald-400" style={fieldStyle}>
              <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />DB
            </Badge>
          )}
          {!isLoading && selectedSource === 'api' && (
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0 rounded-sm" style={fieldStyle}>
              <Zap className="w-2.5 h-2.5 mr-0.5 inline" />API ✓
            </Badge>
          )}
        </div>
      </div>

      {showDropdown && (
        <div className="absolute z-50 left-0 right-0 top-full mt-0.5 bg-card border border-border shadow-lg rounded-sm overflow-hidden max-h-80 overflow-y-auto">
          {(loadingDb || dbSearched) && (
            <>
              <SectionHeader icon={Database} label="Déjà en base" count={dbResults.length} color="bg-emerald-500/5" />
              {loadingDb ? (
                <><SkeletonRow /><SkeletonRow /></>
              ) : dbResults.length === 0 ? (
                <p className="px-3 py-2 text-xs text-muted-foreground italic" style={dmSans}>
                  Aucune fiche existante pour « <em>{query}</em> »
                </p>
              ) : (
                dbResults.map((item, idx) => (
                  <ResultRow key={`db-${item.id || idx}`} item={item} entityType={entityType} source="db" onClick={handleSelect} />
                ))
              )}
            </>
          )}

          {showApiSection && (
            <>
              <SectionHeader icon={Zap} label="API-Football" count={apiResults.length} color="bg-blue-500/5" />
              {loadingApi ? (
                <><SkeletonRow /><SkeletonRow /><SkeletonRow /></>
              ) : errorApi ? (
                <div className="flex items-center gap-2 px-3 py-2 text-xs text-destructive" style={dmSans}>
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  <span className="flex-1">{errorApi}</span>
                  <button type="button" className="pointer-events-auto flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors" onClick={() => fetchApi(query.trim())}>
                    <RefreshCw className="w-3 h-3" /> Réessayer
                  </button>
                </div>
              ) : apiResults.length === 0 ? (
                <p className="px-3 py-2 text-xs text-muted-foreground" style={dmSans}>
                  Aucun résultat API pour « <em>{query}</em> »
                </p>
              ) : (
                apiResults.map((item, idx) => (
                  <ResultRow key={`api-${idx}`} item={item} entityType={entityType} source="api" onClick={handleSelect} />
                ))
              )}
            </>
          )}

          {!loadingDb && !dbSearched && !showApiSection && (
            <p className="px-3 py-4 text-xs text-muted-foreground text-center" style={dmSans}>
              Aucun résultat pour « <em>{query}</em> »
            </p>
          )}
        </div>
      )}
    </div>
  );
}
