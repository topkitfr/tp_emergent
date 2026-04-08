// frontend/src/components/ApiFootballSearch.js
// Composant générique de recherche API-Football (DB-first) pour les forms
// Supporte les types : 'player' | 'team' | 'league'
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, Search, CheckCircle2, UserSearch, Building2, Trophy } from 'lucide-react';
import { searchApiFootballPlayers, searchApiFootballTeams, searchApiFootballLeagues } from '@/lib/api';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };
const inputClass = 'bg-card border-border rounded-none';

const TYPE_CONFIG = {
  player: {
    icon: UserSearch,
    label: 'Auto-fill from API-Football',
    placeholder: 'Search a player (min 3 chars)...',
    search: (q) => searchApiFootballPlayers(q).then(r => (r.data.players || r.data || [])),
    getId: (item) => item.apifootball_id,
    getLabel: (item) => item.name || `${item.firstname || ''} ${item.lastname || ''}`.trim(),
    getSub: (item) => [item.nationality, item.birth_date, item.position].filter(Boolean).join(' · '),
    getLogo: (item) => item.photo || '',
    logoRound: true,
  },
  team: {
    icon: Building2,
    label: 'Auto-fill from API-Football',
    placeholder: 'Search a club (min 3 chars)...',
    // teams-api retourne { db_results, api_results } — on fusionne en préférant DB
    search: async (q) => {
      const r = await searchApiFootballTeams(q);
      const data = r.data || {};
      const db = (data.db_results || []).map(t => ({ ...t, _source: 'db' }));
      const api = (data.api_results || []).map(t => ({ ...t, _source: 'api' }));
      // déduplique par apifootball_team_id
      const seen = new Set(db.map(t => t.apifootball_team_id).filter(Boolean));
      const apiDedup = api.filter(t => !seen.has(t.apifootball_team_id));
      return [...db, ...apiDedup].slice(0, 10);
    },
    getId: (item) => item.apifootball_team_id || item.team_id,
    getLabel: (item) => item.name,
    getSub: (item) => [item.country, item.city, item.founded ? `est. ${item.founded}` : ''].filter(Boolean).join(' · '),
    getLogo: (item) => item.logo || item.crest_url || '',
    logoRound: false,
  },
  league: {
    icon: Trophy,
    label: 'Auto-fill from API-Football',
    placeholder: 'Search a competition (min 3 chars)...',
    search: async (q) => {
      const r = await searchApiFootballLeagues(q);
      const data = r.data || {};
      const db = (data.db_results || []).map(l => ({ ...l, _source: 'db' }));
      const api = (data.api_results || []).map(l => ({ ...l, _source: 'api' }));
      const seen = new Set(db.map(l => l.apifootball_league_id).filter(Boolean));
      const apiDedup = api.filter(l => !seen.has(l.apifootball_league_id));
      return [...db, ...apiDedup].slice(0, 10);
    },
    getId: (item) => item.apifootball_league_id || item.league_id,
    getLabel: (item) => item.name,
    getSub: (item) => [item.country_name || item.country_or_region, item.type, item.scope].filter(Boolean).join(' · '),
    getLogo: (item) => item.logo_url || item.apifootball_logo || '',
    logoRound: false,
  },
};

/**
 * ApiFootballSearch
 *
 * Props:
 *   entityType   : 'player' | 'team' | 'league'
 *   onSelect     : fn(item) appelé quand l'utilisateur choisit un résultat
 *   filledName   : string — nom affiché dans le badge de confirmation
 *   className    : classes supplémentaires sur le wrapper
 */
export default function ApiFootballSearch({ entityType = 'player', onSelect, filledName, className = '' }) {
  const config = TYPE_CONFIG[entityType];
  const Icon = config?.icon || Search;

  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef(null);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleInput = useCallback((val) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (val.length < 3) { setResults([]); setOpen(false); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const items = await config.search(val);
        setResults(Array.isArray(items) ? items : []);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 450);
  }, [config]);

  const handleSelect = (item) => {
    setQuery('');
    setResults([]);
    setOpen(false);
    onSelect?.(item);
  };

  if (!config) return null;

  return (
    <div ref={wrapperRef} className={`relative space-y-1.5 ${className}`}>
      <Label className="text-xs uppercase tracking-wider flex items-center gap-1.5 text-primary" style={labelStyle}>
        <Icon className="w-3.5 h-3.5" />
        {config.label}
      </Label>

      <div className="relative">
        <Input
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          placeholder={config.placeholder}
          className={`${inputClass} pr-8`}
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
          {loading
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Search className="w-3.5 h-3.5" />}
        </span>
      </div>

      {/* Dropdown résultats */}
      {open && results.length > 0 && (
        <ul className="absolute z-50 w-full mt-1 bg-popover border border-border shadow-lg max-h-64 overflow-y-auto">
          {results.map((item, idx) => {
            const logo = config.getLogo(item);
            const label = config.getLabel(item);
            const sub = config.getSub(item);
            const isDb = item._source === 'db';
            return (
              <li
                key={`${config.getId(item)}-${idx}`}
                onClick={() => handleSelect(item)}
                className="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-accent transition-colors"
              >
                {logo ? (
                  <img
                    src={logo}
                    alt={label}
                    className={`w-8 h-8 object-contain flex-shrink-0 bg-muted ${
                      config.logoRound ? 'rounded-full' : ''
                    }`}
                  />
                ) : (
                  <div className="w-8 h-8 flex-shrink-0 bg-muted rounded-sm" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate" style={labelStyle}>{label}</p>
                  {sub && (
                    <p className="text-xs text-muted-foreground truncate">{sub}</p>
                  )}
                </div>
                {/* Badge source */}
                <span className={`ml-auto text-[9px] uppercase tracking-widest flex-shrink-0 px-1.5 py-0.5 rounded-sm font-mono ${
                  isDb
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
                    : 'bg-primary/10 text-primary'
                }`} style={labelStyle}>
                  {isDb ? 'DB' : 'API'}
                </span>
              </li>
            );
          })}
        </ul>
      )}

      {open && results.length === 0 && !loading && query.length >= 3 && (
        <div className="absolute z-50 w-full mt-1 bg-popover border border-border px-3 py-2 text-xs text-muted-foreground">
          No results for « {query} »
        </div>
      )}

      {/* Séparateur */}
      <div className="flex items-center gap-2 pt-1">
        <div className="flex-1 border-t border-border" />
        <span className="text-[10px] text-muted-foreground uppercase tracking-widest" style={labelStyle}>
          or fill manually
        </span>
        <div className="flex-1 border-t border-border" />
      </div>

      {/* Badge entité sélectionnée */}
      {filledName && (
        <div className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span style={labelStyle}>
            Auto-filled: <strong>{filledName}</strong>
          </span>
        </div>
      )}
    </div>
  );
}
