// frontend/src/components/UnifiedEntitySearch.js
// Barre de recherche unifiée pour les dialogs d'entités (team, player, league, brand, sponsor).
// Affiche dans le même dropdown :
//   - Section « Déjà en base » (résultats DB locale via /api/<entity>/search)
//   - Section « API-Football » (résultats API externe via /api/apifootball/search/<entity>)
//
// Props:
//   entityType   : 'team' | 'player' | 'league' | 'brand' | 'sponsor'
//   onSelectDb   : fn(item)    — item DB sélectionné (prefill + indique doublon potentiel)
//   onSelectApi  : fn(item)    — item API-Football sélectionné (prefill depuis API)
//   placeholder  : string (optionnel)
//   disabled     : bool (optionnel)

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Search, Database, Zap, AlertCircle, RefreshCw, CheckCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.REACT_APP_API_URL || '';
const DEBOUNCE_MS = 350;

// ─── Helpers ──────────────────────────────────────────────────────────────────
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const dmSans = { fontFamily: 'DM Sans' };

function getApiEndpoint(entityType, query) {
  return `${API_BASE}/api/apifootball/search/${entityType}?q=${encodeURIComponent(query)}`;
}

function getDbEndpoint(entityType, query) {
  // Route DB locale : /api/teams/search?q=, /api/players/search?q=, etc.
  const plural = { team: 'teams', player: 'players', league: 'leagues', brand: 'brands', sponsor: 'sponsors' };
  const col = plural[entityType] || entityType + 's';
  return `${API_BASE}/api/${col}/search?q=${encodeURIComponent(query)}`;
}

function extractName(item, entityType, source) {
  if (source === 'db') return item.name || item.full_name || item.label || '';
  // API-Football
  if (entityType === 'player') return item.player?.name || item.name || '';
  if (entityType === 'league') return item.league?.name || item.name || '';
  return item.team?.name || item.name || '';
}

function extractSub(item, entityType, source) {
  if (source === 'db') {
    if (entityType === 'player') return [item.nationality, item.birth_date].filter(Boolean).join(' · ');
    if (entityType === 'team')   return [item.country, item.city].filter(Boolean).join(', ');
    if (entityType === 'league') return [item.country_or_region, item.type].filter(Boolean).join(' · ');
    return item.country || '';
  }
  // API-Football
  if (entityType === 'player') return [item.statistics?.[0]?.team?.name, item.player?.nationality].filter(Boolean).join(' · ');
  if (entityType === 'league') return item.country?.name || '';
  return item.team?.country || '';
}

function extractLogo(item, entityType, source) {
  if (source === 'db') {
    return item.logo_url || item.crest_url || item.photo_url || item.photo || null;
  }
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

// ─── Section header ───────────────────────────────────────────────────────────
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

// ─── Result row ───────────────────────────────────────────────────────────────
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
          className="w-7 h-7 object-contain shrink-0 rounded-sm"
          loading="lazy"
          onError={e => { e.currentTarget.style.opacity = '0.25'; }}
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
            {flag && <img src={flag} alt="" className="w-4 h-3 object-cover shrink-0" />}
            {sub}
          </p>
        )}
      </div>

      {isDb && (
        <Badge
          variant="outline"
          className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 border-emerald-500/40 text-emerald-600 dark:text-emerald-400 opacity-80 group-hover:opacity-100 transition-opacity"
          style={fieldStyle}
        >
          <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />
          En base
        </Badge>
      )}
      {!isDb && (
        <Badge
          variant="outline"
          className="text-[9px] px-1.5 py-0 rounded-sm shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
          style={fieldStyle}
        >
          API
        </Badge>
      )}
    </button>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function UnifiedEntitySearch({
  entityType = 'team',
  onSelectDb,
  onSelectApi,
  placeholder,
  disabled = false,
}) {
  const [query, setQuery]         = useState('');
  const [dbResults, setDbResults] = useState([]);
  const [apiResults, setApiResults] = useState([]);
  const [loadingDb, setLoadingDb] = useState(false);
  const [loadingApi, setLoadingApi] = useState(false);
  const [errorApi, setErrorApi]   = useState(null);
  const [open, setOpen]           = useState(false);
  const [selectedName, setSelectedName] = useState(null);

  const timerDb  = useRef(null);
  const timerApi = useRef(null);
  const containerRef = useRef(null);

  const defaultPlaceholders = {
    team:    'Rechercher un club... (DB + API-Football)',
    player:  'Rechercher un joueur... (DB + API-Football)',
    league:  'Rechercher une compétition... (DB + API-Football)',
    brand:   'Rechercher une marque...',
    sponsor: 'Rechercher un sponsor...',
  };

  const fetchDb = useCallback(async (q) => {
    setLoadingDb(true);
    try {
      const res = await fetch(getDbEndpoint(entityType, q));
      if (!res.ok) throw new Error();
      const data = await res.json();
      setDbResults((data.results || data || []).slice(0, 5));
    } catch {
      setDbResults([]);
    } finally {
      setLoadingDb(false);
    }
  }, [entityType]);

  const fetchApi = useCallback(async (q) => {
    setLoadingApi(true);
    setErrorApi(null);
    try {
      const res = await fetch(getApiEndpoint(entityType, q));
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setApiResults((data.results || data || []).slice(0, 6));
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
    setSelectedName(null);

    if (val.trim().length < 2) {
      setOpen(false);
      setDbResults([]);
      setApiResults([]);
      clearTimeout(timerDb.current);
      clearTimeout(timerApi.current);
      return;
    }

    clearTimeout(timerDb.current);
    clearTimeout(timerApi.current);
    timerDb.current  = setTimeout(() => fetchDb(val.trim()), 200);
    timerApi.current = setTimeout(() => fetchApi(val.trim()), DEBOUNCE_MS);
    setOpen(true);
  };

  const handleSelect = (item, source) => {
    const name = extractName(item, entityType, source);
    setQuery(name);
    setSelectedName(source);
    setOpen(false);
    if (source === 'db')  onSelectDb?.(item);
    if (source === 'api') onSelectApi?.(item);
  };

  const isLoading = loadingDb || loadingApi;
  const hasResults = dbResults.length > 0 || apiResults.length > 0;
  const showDropdown = open && query.trim().length >= 2;

  // Fermer au clic extérieur
  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="relative" ref={containerRef}>
      {/* Input */}
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
        <Input
          value={query}
          onChange={handleChange}
          onFocus={() => hasResults && setOpen(true)}
          placeholder={placeholder || defaultPlaceholders[entityType]}
          className="pl-8 pr-20 rounded-none h-9 text-sm bg-card border-border"
          autoComplete="off"
          disabled={disabled}
        />
        {/* Indicateurs de chargement / statut */}
        <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
          {(loadingDb || loadingApi) && (
            <svg className="w-3.5 h-3.5 animate-spin text-muted-foreground" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="60" strokeDashoffset="20" />
            </svg>
          )}
          {selectedName === 'db' && (
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0 rounded-sm border-emerald-500/40 text-emerald-600" style={fieldStyle}>
              <CheckCircle className="w-2.5 h-2.5 mr-0.5 inline" />DB
            </Badge>
          )}
          {selectedName === 'api' && (
            <Badge variant="secondary" className="text-[9px] px-1.5 py-0 rounded-sm" style={fieldStyle}>
              <Zap className="w-2.5 h-2.5 mr-0.5 inline" />API ✓
            </Badge>
          )}
        </div>
      </div>

      {/* Dropdown */}
      {showDropdown && (
        <div className="absolute z-50 left-0 right-0 top-full mt-0.5 bg-card border border-border shadow-lg rounded-sm overflow-hidden">

          {/* ── Section DB locale ── */}
          {(loadingDb || dbResults.length > 0) && (
            <>
              <SectionHeader
                icon={Database}
                label="Déjà en base"
                count={dbResults.length}
                color="bg-emerald-500/5"
              />
              {loadingDb ? (
                <>
                  <SkeletonRow />
                  <SkeletonRow />
                </>
              ) : (
                dbResults.map((item, idx) => (
                  <ResultRow
                    key={`db-${item.id || item._id || idx}`}
                    item={item}
                    entityType={entityType}
                    source="db"
                    onClick={handleSelect}
                  />
                ))
              )}
            </>
          )}

          {/* ── Section API-Football ── */}
          {(['team', 'player', 'league'].includes(entityType)) && (
            <>
              <SectionHeader
                icon={Zap}
                label="API-Football"
                count={apiResults.length}
                color="bg-blue-500/5"
              />
              {loadingApi ? (
                <>
                  <SkeletonRow />
                  <SkeletonRow />
                  <SkeletonRow />
                </>
              ) : errorApi ? (
                <div className="flex items-center gap-2 px-3 py-2 text-xs text-destructive" style={dmSans}>
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  {errorApi}
                  <button
                    type="button"
                    onClick={() => fetchApi(query.trim())}
                    className="ml-auto flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <RefreshCw className="w-3 h-3" /> Réessayer
                  </button>
                </div>
              ) : apiResults.length === 0 && !loadingApi ? (
                <div className="px-3 py-2 text-xs text-muted-foreground" style={dmSans}>
                  Aucun résultat API pour «&nbsp;<em>{query}</em>&nbsp;»
                </div>
              ) : (
                <div className="max-h-52 overflow-y-auto">
                  {apiResults.map((item, idx) => (
                    <ResultRow
                      key={`api-${idx}`}
                      item={item}
                      entityType={entityType}
                      source="api"
                      onClick={handleSelect}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {/* ── Empty state global ── */}
          {!isLoading && !hasResults && (
            <div className="px-3 py-4 text-xs text-muted-foreground text-center" style={dmSans}>
              Aucun résultat pour «&nbsp;<em>{query}</em>&nbsp;»
            </div>
          )}

        </div>
      )}
    </div>
  );
}
