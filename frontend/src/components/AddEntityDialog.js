// frontend/src/components/AddEntityDialog.js
// Dialog générique pour soumettre une nouvelle entité (player/team/brand/league/sponsor)
// Les soumissions créées ici sont VOTABLES par la communauté (pas de parent kit)
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2, Search, CheckCircle2 } from 'lucide-react';
import { createPlayerPending, createTeamPending, createBrandPending, createLeaguePending, createSponsorPending, searchApiFootballPlayers } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];
const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];
const fieldLabel = 'text-xs uppercase tracking-wider';
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none';

/**
 * Mapping position API-Football → codes Topkit.
 * API-Football renvoie des strings en anglais (ex: "Goalkeeper", "Midfielder").
 * On essaie d'abord un match exact, puis un match partiel.
 */
const API_POSITION_MAP = {
  // Gardien
  'Goalkeeper': ['GK'],
  // Défenseurs
  'Defender': ['CB'],
  'Centre-Back': ['CB'],
  'Center Back': ['CB'],
  'Left Back': ['LB'],
  'Right Back': ['RB'],
  'Left Wing Back': ['LWB'],
  'Right Wing Back': ['RWB'],
  // Milieux
  'Midfielder': ['CM'],
  'Defensive Midfielder': ['CDM'],
  'Central Midfielder': ['CM'],
  'Attacking Midfielder': ['CAM'],
  'Left Midfielder': ['LM'],
  'Right Midfielder': ['RM'],
  // Ailiers
  'Left Winger': ['LW'],
  'Right Winger': ['RW'],
  // Attaquants
  'Attacker': ['ST'],
  'Centre Forward': ['CF'],
  'Center Forward': ['CF'],
  'Striker': ['ST'],
  'Forward': ['ST'],
  'Second Striker': ['SS'],
};

/**
 * Convertit une position API-Football en tableau de codes Topkit.
 * Fallback : tableau vide si non reconnu.
 */
function mapApiPosition(apiPosition) {
  if (!apiPosition) return [];
  // Match exact
  if (API_POSITION_MAP[apiPosition]) return API_POSITION_MAP[apiPosition];
  // Match partiel (insensible à la casse)
  const lower = apiPosition.toLowerCase();
  for (const [key, val] of Object.entries(API_POSITION_MAP)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) {
      return val;
    }
  }
  return [];
}

/**
 * ApiFootballSearch — champ de recherche live API-Football avec dropdown auto-fill.
 * Props:
 *   onSelect(player) : appelé quand l'utilisateur choisit un résultat
 *   selectedName     : nom affiché une fois sélectionné
 */
function ApiFootballSearch({ onSelect, selectedName }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef(null);
  const wrapperRef = useRef(null);

  // Fermer le dropdown en cliquant à l'extérieur
  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
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
        const res = await searchApiFootballPlayers(val);
        setResults(res.data.players || []);
        setOpen(true);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500);
  }, []);

  const handleSelect = (player) => {
    setQuery('');
    setResults([]);
    setOpen(false);
    onSelect(player);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <Input
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          placeholder="Search on API-Football (min 3 chars)..."
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
          {results.map((p) => (
            <li
              key={p.apifootball_id}
              onClick={() => handleSelect(p)}
              className="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-accent transition-colors"
            >
              {p.photo && (
                <img
                  src={p.photo}
                  alt={p.name}
                  className="w-8 h-8 rounded-full object-cover flex-shrink-0 bg-muted"
                />
              )}
              <div className="min-w-0">
                <p className="text-sm font-medium truncate" style={fieldStyle}>{p.name}</p>
                <p className="text-xs text-muted-foreground truncate">
                  {[p.nationality, p.birth_date, p.position].filter(Boolean).join(' · ')}
                </p>
              </div>
              <span className="ml-auto text-[10px] text-muted-foreground flex-shrink-0 font-mono">
                #{p.apifootball_id}
              </span>
            </li>
          ))}
        </ul>
      )}

      {open && results.length === 0 && !loading && query.length >= 3 && (
        <div className="absolute z-50 w-full mt-1 bg-popover border border-border px-3 py-2 text-xs text-muted-foreground">
          No results found for « {query} »
        </div>
      )}

      {/* Badge joueur sélectionné */}
      {selectedName && (
        <div className="flex items-center gap-1.5 mt-1.5 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span style={fieldStyle}>Auto-filled from API-Football: <strong>{selectedName}</strong></span>
        </div>
      )}
    </div>
  );
}

/**
 * AddEntityDialog — modal d'ajout direct d'une entité de référence.
 *
 * Props:
 * - open: bool
 * - onClose: fn
 * - entityType: 'player' | 'team' | 'brand' | 'league' | 'sponsor'
 * - onSuccess: fn() — appelé après soumission réussie (pour refetch)
 */
export default function AddEntityDialog({ open, onClose, entityType, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({});
  const [apiSelectedName, setApiSelectedName] = useState('');

  const set = (key, val) => setForm(p => ({ ...p, [key]: val }));

  const handleClose = () => {
    setForm({});
    setApiSelectedName('');
    onClose();
  };

  /** Auto-fill le formulaire depuis un résultat API-Football */
  const handleApiSelect = (player) => {
    const mappedPositions = mapApiPosition(player.position);
    setForm(prev => ({
      ...prev,
      full_name:      player.name || `${player.firstname || ''} ${player.lastname || ''}`.trim(),
      nationality:    player.nationality || prev.nationality || '',
      birth_date:     player.birth_date  || prev.birth_date  || '',
      photo_url:      player.photo       || prev.photo_url   || '',
      apifootball_id: player.apifootball_id,
      positions:      mappedPositions.length > 0 ? mappedPositions : (prev.positions || []),
    }));
    setApiSelectedName(player.name || player.firstname);
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      // Validation minimale
      if (entityType === 'player' && !form.full_name?.trim()) {
        toast.error('Full name is required'); setLoading(false); return;
      }
      if (entityType !== 'player' && !form.name?.trim()) {
        toast.error('Name is required'); setLoading(false); return;
      }

      // Appel API selon le type (sans parent_submission_id → votable)
      const fns = {
        player:  createPlayerPending,
        team:    createTeamPending,
        brand:   createBrandPending,
        league:  createLeaguePending,
        sponsor: createSponsorPending,
      };
      await fns[entityType](form);

      const labels = {
        player: 'Player', team: 'Team', brand: 'Brand', league: 'League', sponsor: 'Sponsor',
      };
      toast.success(`${labels[entityType]} submitted for community review`);
      handleClose();
      onSuccess?.();
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  const titles = {
    player: 'Add a new Player',
    team: 'Add a new Team',
    brand: 'Add a new Brand',
    league: 'Add a new League',
    sponsor: 'Add a new Sponsor',
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg bg-background border-border rounded-none p-0 gap-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-border">
          <DialogTitle className="text-xl tracking-tighter" style={fieldStyle}>
            {titles[entityType] || 'Add Entity'}
          </DialogTitle>
          <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            Will be submitted for community vote before appearing in the database.
          </p>
        </DialogHeader>

        <div className="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">

          {/* ── PLAYER ── */}
          {entityType === 'player' && (
            <>
              {/* ✨ Recherche API-Football */}
              <div className="space-y-1.5 pb-2 border-b border-border">
                <Label className={fieldLabel} style={fieldStyle}>
                  🔍 Auto-fill from API-Football
                </Label>
                <ApiFootballSearch
                  onSelect={handleApiSelect}
                  selectedName={apiSelectedName}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Full Name *</Label>
                  <Input
                    value={form.full_name || ''}
                    onChange={e => set('full_name', e.target.value)}
                    placeholder="Zinédine Zidane"
                    className={inputClass}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Nationality</Label>
                  <Input
                    value={form.nationality || ''}
                    onChange={e => set('nationality', e.target.value)}
                    placeholder="French"
                    className={inputClass}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Date of Birth</Label>
                  <Input
                    value={form.birth_date || ''}
                    onChange={e => set('birth_date', e.target.value)}
                    placeholder="DD/MM/YYYY"
                    className={inputClass}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Preferred Number</Label>
                  <Input
                    type="number"
                    value={form.preferred_number || ''}
                    onChange={e => set('preferred_number', e.target.value ? parseInt(e.target.value) : '')}
                    placeholder="10"
                    className={inputClass}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>API-Football ID</Label>
                  <Input
                    type="number"
                    value={form.apifootball_id || ''}
                    onChange={e => set('apifootball_id', e.target.value ? parseInt(e.target.value) : '')}
                    className={inputClass}
                    placeholder="Auto-filled above, or enter manually"
                  />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Positions</Label>
                  <div className="flex flex-wrap gap-1.5">
                    {POSITIONS.map(pos => (
                      <button
                        key={pos}
                        type="button"
                        onClick={() => {
                          const current = form.positions || [];
                          set('positions', current.includes(pos)
                            ? current.filter(p => p !== pos)
                            : [...current, pos]
                          );
                        }}
                        className={`px-2 py-0.5 text-[11px] border rounded-none transition-colors ${
                          (form.positions || []).includes(pos)
                            ? 'bg-primary text-primary-foreground border-primary'
                            : 'bg-card border-border text-muted-foreground hover:border-primary/50'
                        }`}
                        style={fieldStyle}
                      >
                        {pos}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Bio</Label>
                  <Textarea
                    value={form.bio || ''}
                    onChange={e => set('bio', e.target.value)}
                    placeholder="Brief biography..."
                    className={`${inputClass} min-h-[80px]`}
                  />
                </div>

                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Photo</Label>
                  <ImageUpload
                    value={form.photo_url || ''}
                    onChange={url => set('photo_url', url)}
                    folder="player"
                  />
                </div>
              </div>
            </>
          )}

          {/* ── TEAM ── */}
          {entityType === 'team' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Team Name *</Label>
                <Input value={form.name || ''} onChange={e => set('name', e.target.value)} placeholder="FC Barcelona" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Country</Label>
                <Input value={form.country || ''} onChange={e => set('country', e.target.value)} placeholder="Spain" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>City</Label>
                <Input value={form.city || ''} onChange={e => set('city', e.target.value)} placeholder="Barcelona" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Founded</Label>
                <Input type="number" value={form.founded || ''} onChange={e => set('founded', e.target.value ? parseInt(e.target.value) : '')} placeholder="1899" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Primary Color</Label>
                <Input value={form.primary_color || ''} onChange={e => set('primary_color', e.target.value)} placeholder="#A50044" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Crest / Badge</Label>
                <ImageUpload value={form.crest_url || ''} onChange={url => set('crest_url', url)} folder="team" />
              </div>
            </div>
          )}

          {/* ── BRAND ── */}
          {entityType === 'brand' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Brand Name *</Label>
                <Input value={form.name || ''} onChange={e => set('name', e.target.value)} placeholder="Adidas" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Country</Label>
                <Input value={form.country || ''} onChange={e => set('country', e.target.value)} placeholder="Germany" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Founded</Label>
                <Input type="number" value={form.founded || ''} onChange={e => set('founded', e.target.value ? parseInt(e.target.value) : '')} placeholder="1949" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} folder="brand" />
              </div>
            </div>
          )}

          {/* ── LEAGUE ── */}
          {entityType === 'league' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>League Name *</Label>
                <Input value={form.name || ''} onChange={e => set('name', e.target.value)} placeholder="Premier League" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Country / Region</Label>
                <Input value={form.country_or_region || ''} onChange={e => set('country_or_region', e.target.value)} placeholder="England" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Level</Label>
                <Select value={form.level || ''} onValueChange={v => set('level', v)}>
                  <SelectTrigger className={`${inputClass} h-9`}>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    {LEAGUE_LEVELS.map(l => (
                      <SelectItem key={l} value={l}>{l}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Organizer</Label>
                <Input value={form.organizer || ''} onChange={e => set('organizer', e.target.value)} placeholder="UEFA" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} folder="league" />
              </div>
            </div>
          )}

          {/* ── SPONSOR ── */}
          {entityType === 'sponsor' && (
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Sponsor Name *</Label>
                <Input value={form.name || ''} onChange={e => set('name', e.target.value)} placeholder="Emirates" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Country</Label>
                <Input value={form.country || ''} onChange={e => set('country', e.target.value)} placeholder="UAE" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Website</Label>
                <Input value={form.website || ''} onChange={e => set('website', e.target.value)} placeholder="https://..." className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} folder="sponsor" />
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="rounded-none"
          >
            {loading && <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />}
            Submit for Review
          </Button>
          <Button variant="outline" onClick={handleClose} className="rounded-none">
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
