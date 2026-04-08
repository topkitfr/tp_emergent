// frontend/src/components/CompetitionSelector.js
// Sélecteur de compétition (league) pour MasterKit, ClubForm, etc.
//
// Stratégie : DB-first
//   1. Cherche d'abord dans la DB Topkit (/api/leagues?search=...)
//   2. Si < 3 résultats DB → ouvre un panneau secondaire "Ajouter depuis API-Football"
//      qui utilise ApiFootballSearch (entityType="league")
//   3. Quand l'utilisateur sélectionne un résultat API-Football, on propose
//      d'importer la league en DB (POST /api/leagues/import-from-apifootball)
//
// Props:
//   value      : { league_id, name, logo_url, apifootball_league_id } | null
//   onChange   : fn(value)
//   label      : string (optionnel)
//   required   : bool
//   placeholder: string

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Search, ChevronDown, X, Plus, ExternalLink, Loader2 } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import ApiFootballSearch from './ApiFootballSearch';

const API_BASE = process.env.REACT_APP_API_URL || '';
const DEBOUNCE_MS = 300;

// ─── Skeleton ────────────────────────────────────────────────────────────────
function Skeleton() {
  return (
    <div className="space-y-1 p-1">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex items-center gap-2 px-2 py-1.5 animate-pulse">
          <div className="w-6 h-6 rounded-sm bg-muted shrink-0" />
          <div className="h-3 bg-muted rounded w-2/3" />
        </div>
      ))}
    </div>
  );
}

// ─── Ligne résultat DB ────────────────────────────────────────────────────────
function DBRow({ item, onClick }) {
  return (
    <button
      type="button"
      onClick={() => onClick(item)}
      className="w-full flex items-center gap-2 px-3 py-2 hover:bg-accent transition-colors text-left"
    >
      {item.logo_url ? (
        <img src={item.logo_url} alt="" className="w-6 h-6 object-contain shrink-0" loading="lazy" />
      ) : (
        <div className="w-6 h-6 bg-muted rounded-sm shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate" style={{ fontFamily: 'Barlow Condensed' }}>
          {item.name}
        </p>
        {item.country && (
          <p className="text-xs text-muted-foreground truncate">{item.country}</p>
        )}
      </div>
      <Badge variant="outline" className="text-[9px] px-1.5 py-0 rounded-sm shrink-0" style={{ fontFamily: 'Barlow Condensed' }}>
        DB
      </Badge>
    </button>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function CompetitionSelector({
  value = null,
  onChange,
  label = 'Compétition',
  required = false,
  placeholder = 'Rechercher une compétition...',
}) {
  const [query, setQuery] = useState('');
  const [dbResults, setDbResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [showApiPanel, setShowApiPanel] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState(null);

  const timerRef = useRef(null);
  const containerRef = useRef(null);

  // ── Recherche DB ────────────────────────────────────────────────────────────
  const searchDB = useCallback(async (q) => {
    if (!q || q.trim().length < 2) {
      setDbResults([]);
      setOpen(false);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/leagues?search=${encodeURIComponent(q.trim())}&limit=8`);
      if (!res.ok) throw new Error();
      const data = await res.json();
      const list = data.leagues || data.results || data || [];
      setDbResults(list);
      setOpen(true);
      // Ouvre le panel API si peu de résultats DB
      setShowApiPanel(list.length < 3);
    } catch {
      setDbResults([]);
      setShowApiPanel(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    if (value) onChange(null); // reset sélection
    clearTimeout(timerRef.current);
    if (val.trim().length < 2) { setOpen(false); setDbResults([]); return; }
    timerRef.current = setTimeout(() => searchDB(val), DEBOUNCE_MS);
  };

  // ── Sélection depuis DB ─────────────────────────────────────────────────────
  const handleSelectDB = (item) => {
    setQuery(item.name);
    setOpen(false);
    setShowApiPanel(false);
    onChange({
      league_id: item.league_id || item._id,
      name: item.name,
      logo_url: item.logo_url,
      country: item.country,
      apifootball_league_id: item.apifootball_league_id || null,
      _source: 'db',
    });
  };

  // ── Import depuis API-Football ──────────────────────────────────────────────
  const handleSelectFromApi = async (apiItem) => {
    const league = apiItem.league || apiItem;
    const country = apiItem.country || {};
    setImporting(true);
    setImportError(null);
    try {
      const res = await fetch(`${API_BASE}/api/leagues/import-from-apifootball`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          apifootball_league_id: league.id,
          name: league.name,
          logo_url: league.logo,
          country: country.name || null,
          country_flag: country.flag || null,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur import');
      // Succès : on sélectionne la league importée/existante
      setQuery(data.name || league.name);
      setOpen(false);
      setShowApiPanel(false);
      onChange({
        league_id: data.league_id || data._id,
        name: data.name || league.name,
        logo_url: data.logo_url || league.logo,
        country: data.country || country.name,
        apifootball_league_id: league.id,
        _source: 'api-football',
      });
    } catch (err) {
      setImportError(err.message);
    } finally {
      setImporting(false);
    }
  };

  // ── Clear ────────────────────────────────────────────────────────────────────
  const handleClear = () => {
    setQuery('');
    setOpen(false);
    setShowApiPanel(false);
    setDbResults([]);
    onChange(null);
  };

  // ── Fermer au clic extérieur ─────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const hasValue = value && value.league_id;

  return (
    <div className="space-y-1" ref={containerRef}>
      {label && (
        <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
          {label}{required && <span className="text-destructive ml-0.5">*</span>}
        </Label>
      )}

      {/* Champ de saisie */}
      <div className="relative">
        {/* Logo si sélectionné */}
        {hasValue && value.logo_url ? (
          <img
            src={value.logo_url}
            alt=""
            className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 object-contain pointer-events-none"
          />
        ) : (
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
        )}

        <input
          type="text"
          value={hasValue ? value.name : query}
          onChange={handleChange}
          onFocus={() => dbResults.length > 0 && setOpen(true)}
          placeholder={placeholder}
          readOnly={!!hasValue}
          className={
            `w-full pl-8 pr-8 h-8 text-sm border border-border rounded-none bg-card 
             focus:outline-none focus:ring-1 focus:ring-primary transition-colors
             ${hasValue ? 'text-foreground cursor-default' : 'text-foreground'}`
          }
        />

        {/* Clear ou chevron */}
        {hasValue ? (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            aria-label="Effacer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        ) : (
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
        )}
      </div>

      {/* Badge source */}
      {hasValue && (
        <div className="flex items-center gap-1.5">
          <Badge
            variant={value._source === 'api-football' ? 'default' : 'secondary'}
            className="text-[9px] px-1.5 py-0 rounded-sm"
            style={{ fontFamily: 'Barlow Condensed' }}
          >
            {value._source === 'api-football' ? 'API-Football ✓' : 'DB ✓'}
          </Badge>
          {value.country && (
            <span className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>
              {value.country}
            </span>
          )}
        </div>
      )}

      {/* Dropdown */}
      {open && !hasValue && (
        <div className="absolute z-50 w-full max-w-sm bg-card border border-border shadow-md rounded-sm overflow-hidden">

          {/* Résultats DB */}
          {loading && <Skeleton />}

          {!loading && dbResults.length > 0 && (
            <div className="max-h-48 overflow-y-auto">
              <p className="px-3 pt-2 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                Base Topkit
              </p>
              {dbResults.map((item, i) => (
                <DBRow key={i} item={item} onClick={handleSelectDB} />
              ))}
            </div>
          )}

          {!loading && dbResults.length === 0 && query.length >= 2 && (
            <p className="px-3 py-2 text-xs text-muted-foreground text-center" style={{ fontFamily: 'DM Sans' }}>
              Aucune compétition en DB pour «&nbsp;{query}&nbsp;»
            </p>
          )}

          {/* Séparateur + panel API-Football */}
          {showApiPanel && (
            <div className="border-t border-border">
              <p className="px-3 pt-2 pb-1 text-[10px] uppercase tracking-wider text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'Barlow Condensed' }}>
                <ExternalLink className="w-3 h-3" />
                Ajouter depuis API-Football
              </p>
              <div className="px-3 pb-2">
                <ApiFootballSearch
                  entityType="league"
                  onSelect={handleSelectFromApi}
                  placeholder="Chercher sur API-Football..."
                />
              </div>
              {importing && (
                <div className="flex items-center gap-2 px-3 pb-2 text-xs text-muted-foreground">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Import en cours...
                </div>
              )}
              {importError && (
                <p className="px-3 pb-2 text-xs text-destructive">{importError}</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
