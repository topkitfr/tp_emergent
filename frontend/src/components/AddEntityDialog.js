// frontend/src/components/AddEntityDialog.js
// Dialog générique pour soumettre une nouvelle entité (player/team/brand/league/sponsor)
// Les soumissions créées ici sont VOTABLES par la communauté (pas de parent kit)
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import {
  createPlayerPending,
  createTeamPending,
  createBrandPending,
  createLeaguePending,
  createSponsorPending,
} from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import UnifiedEntitySearch from '@/components/UnifiedEntitySearch';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];
const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];
const fieldLabel = 'text-xs uppercase tracking-wider';
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none';

// ── Mapping position API → codes Topkit ────────────────────────────────────
const API_POSITION_MAP = {
  'Goalkeeper': ['GK'],
  'Defender': ['CB'], 'Centre-Back': ['CB'], 'Center Back': ['CB'],
  'Left Back': ['LB'], 'Right Back': ['RB'],
  'Left Wing Back': ['LWB'], 'Right Wing Back': ['RWB'],
  'Midfielder': ['CM'], 'Defensive Midfielder': ['CDM'],
  'Central Midfielder': ['CM'], 'Attacking Midfielder': ['CAM'],
  'Left Midfielder': ['LM'], 'Right Midfielder': ['RM'],
  'Left Winger': ['LW'], 'Right Winger': ['RW'],
  'Attacker': ['ST'], 'Centre Forward': ['CF'], 'Center Forward': ['CF'],
  'Striker': ['ST'], 'Forward': ['ST'], 'Second Striker': ['SS'],
};

function mapApiPosition(apiPosition) {
  if (!apiPosition) return [];
  if (API_POSITION_MAP[apiPosition]) return API_POSITION_MAP[apiPosition];
  const lower = apiPosition.toLowerCase();
  for (const [key, val] of Object.entries(API_POSITION_MAP)) {
    if (lower.includes(key.toLowerCase()) || key.toLowerCase().includes(lower)) return val;
  }
  return [];
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

  const set = (key, val) => setForm(p => ({ ...p, [key]: val }));

  const handleClose = () => {
    setForm({});
    onClose();
  };

  // ── Handlers DB sélect (élément déjà en base) ────────────────────────────
  const handleDbSelect = (item) => {
    // Avertissement : l'élément existe déjà en base
    toast.warning(
      `« ${item.name || item.full_name || item.label} » existe déjà en base de données. Préremplissage effectué.`,
      { duration: 5000 }
    );
    // Préremplir quand même pour permettre une édition
    if (entityType === 'player')  handlePlayerDbSelect(item);
    if (entityType === 'team')    handleTeamDbSelect(item);
    if (entityType === 'league')  handleLeagueDbSelect(item);
    if (entityType === 'brand')   set('name', item.name || '');
    if (entityType === 'sponsor') set('name', item.name || '');
  };

  const handlePlayerDbSelect = (item) => {
    setForm(prev => ({
      ...prev,
      full_name:      item.full_name || item.name || '',
      nationality:    item.nationality || '',
      birth_date:     item.birth_date || '',
      photo_url:      item.photo_url || item.photo || '',
      apifootball_id: item.apifootball_id || '',
      positions:      item.positions || [],
    }));
  };

  const handleTeamDbSelect = (item) => {
    setForm(prev => ({
      ...prev,
      name:                item.name || '',
      country:             item.country || '',
      city:                item.city || '',
      founded:             item.founded || '',
      is_national:         item.is_national ?? false,
      crest_url:           item.crest_url || '',
      stadium_name:        item.stadium_name || '',
      stadium_capacity:    item.stadium_capacity || '',
      stadium_surface:     item.stadium_surface || '',
      apifootball_team_id: item.apifootball_team_id || '',
    }));
  };

  const handleLeagueDbSelect = (item) => {
    setForm(prev => ({
      ...prev,
      name:              item.name || '',
      country_or_region: item.country_or_region || '',
      country_code:      item.country_code || '',
      type:              item.type || '',
      scope:             item.scope || '',
      organizer:         item.organizer || '',
      logo_url:          item.logo_url || '',
      apifootball_league_id: item.apifootball_league_id || '',
    }));
  };

  // ── Handlers API select (préfill depuis API-Football) ───────────────────
  const handlePlayerApiSelect = (player) => {
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
  };

  const handleTeamApiSelect = (team) => {
    setForm(prev => ({
      ...prev,
      name:                  team.name              || prev.name || '',
      country:               team.country           || prev.country || '',
      city:                  team.city              || prev.city || '',
      founded:               team.founded           ?? prev.founded ?? '',
      is_national:           team.is_national       ?? prev.is_national ?? false,
      crest_url:             team.logo              || prev.crest_url || '',
      stadium_name:          team.stadium_name      || prev.stadium_name || '',
      stadium_capacity:      team.stadium_capacity  ?? prev.stadium_capacity ?? '',
      stadium_surface:       team.stadium_surface   || prev.stadium_surface || '',
      stadium_image_url:     team.stadium_image_url || prev.stadium_image_url || '',
      apifootball_team_id:   team.apifootball_team_id ?? prev.apifootball_team_id ?? '',
    }));
  };

  const handleLeagueApiSelect = (league) => {
    setForm(prev => ({
      ...prev,
      name:                    league.name                || prev.name || '',
      country_or_region:       league.country_name        || league.country_or_region || prev.country_or_region || '',
      country_code:            league.country_code        || prev.country_code || '',
      country_flag:            league.country_flag        || prev.country_flag || '',
      type:                    league.type                || prev.type || '',
      scope:                   league.scope               || prev.scope || '',
      organizer:               league.organizer           || prev.organizer || '',
      logo_url:                league.apifootball_logo    || league.logo_url || prev.logo_url || '',
      apifootball_league_id:   league.apifootball_league_id ?? prev.apifootball_league_id ?? '',
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (entityType === 'player' && !form.full_name?.trim()) {
        toast.error('Full name is required'); setLoading(false); return;
      }
      if (entityType !== 'player' && !form.name?.trim()) {
        toast.error('Name is required'); setLoading(false); return;
      }

      const fns = {
        player:  createPlayerPending,
        team:    createTeamPending,
        brand:   createBrandPending,
        league:  createLeaguePending,
        sponsor: createSponsorPending,
      };
      await fns[entityType](form);

      const labels = { player: 'Player', team: 'Team', brand: 'Brand', league: 'League', sponsor: 'Sponsor' };
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
              <div className="pb-3 border-b border-border space-y-1">
                <Label className={fieldLabel} style={fieldStyle}>Recherche rapide</Label>
                <UnifiedEntitySearch
                  entityType="player"
                  onSelectDb={handleDbSelect}
                  onSelectApi={handlePlayerApiSelect}
                  placeholder="Nom du joueur..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Full Name *</Label>
                  <Input value={form.full_name || ''} onChange={e => set('full_name', e.target.value)} placeholder="Zinédine Zidane" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Nationality</Label>
                  <Input value={form.nationality || ''} onChange={e => set('nationality', e.target.value)} placeholder="French" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Date of Birth</Label>
                  <Input value={form.birth_date || ''} onChange={e => set('birth_date', e.target.value)} placeholder="DD/MM/YYYY" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Preferred Number</Label>
                  <Input type="number" value={form.preferred_number || ''} onChange={e => set('preferred_number', e.target.value ? parseInt(e.target.value) : '')} placeholder="10" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>API-Football ID</Label>
                  <Input type="number" value={form.apifootball_id || ''} onChange={e => set('apifootball_id', e.target.value ? parseInt(e.target.value) : '')} className={inputClass} placeholder="Auto-fillé ci-dessus" />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Positions</Label>
                  <div className="flex flex-wrap gap-1.5">
                    {POSITIONS.map(pos => (
                      <button key={pos} type="button"
                        onClick={() => {
                          const current = form.positions || [];
                          set('positions', current.includes(pos) ? current.filter(p => p !== pos) : [...current, pos]);
                        }}
                        className={`px-2 py-0.5 text-[11px] border rounded-none transition-colors ${
                          (form.positions || []).includes(pos)
                            ? 'bg-primary text-primary-foreground border-primary'
                            : 'bg-card border-border text-muted-foreground hover:border-primary/50'
                        }`}
                        style={fieldStyle}>{pos}</button>
                    ))}
                  </div>
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Bio</Label>
                  <Textarea value={form.bio || ''} onChange={e => set('bio', e.target.value)} placeholder="Brief biography..." className={`${inputClass} min-h-[80px]`} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Photo</Label>
                  <ImageUpload value={form.photo_url || ''} onChange={url => set('photo_url', url)} folder="player" />
                </div>
              </div>
            </>
          )}

          {/* ── TEAM ── */}
          {entityType === 'team' && (
            <>
              <div className="pb-3 border-b border-border space-y-1">
                <Label className={fieldLabel} style={fieldStyle}>Recherche rapide</Label>
                <UnifiedEntitySearch
                  entityType="team"
                  onSelectDb={handleDbSelect}
                  onSelectApi={handleTeamApiSelect}
                  placeholder="Nom du club..."
                />
              </div>
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
                  <Label className={fieldLabel} style={fieldStyle}>API-Football ID</Label>
                  <Input type="number" value={form.apifootball_team_id || ''} onChange={e => set('apifootball_team_id', e.target.value ? parseInt(e.target.value) : '')} placeholder="Auto-fillé ci-dessus" className={inputClass} />
                </div>
                <div className="col-span-2">
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-2" style={fieldStyle}>Stadium</p>
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Stadium Name</Label>
                  <Input value={form.stadium_name || ''} onChange={e => set('stadium_name', e.target.value)} placeholder="Camp Nou" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Capacity</Label>
                  <Input type="number" value={form.stadium_capacity || ''} onChange={e => set('stadium_capacity', e.target.value ? parseInt(e.target.value) : '')} placeholder="99354" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Surface</Label>
                  <Input value={form.stadium_surface || ''} onChange={e => set('stadium_surface', e.target.value)} placeholder="grass" className={inputClass} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Crest / Badge</Label>
                  <ImageUpload value={form.crest_url || ''} onChange={url => set('crest_url', url)} folder="team" />
                </div>
              </div>
            </>
          )}

          {/* ── BRAND ── */}
          {entityType === 'brand' && (
            <>
              <div className="pb-3 border-b border-border space-y-1">
                <Label className={fieldLabel} style={fieldStyle}>Recherche rapide</Label>
                <UnifiedEntitySearch
                  entityType="brand"
                  onSelectDb={handleDbSelect}
                  onSelectApi={() => {}}
                  placeholder="Nom de la marque..."
                />
              </div>
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
            </>
          )}

          {/* ── LEAGUE ── */}
          {entityType === 'league' && (
            <>
              <div className="pb-3 border-b border-border space-y-1">
                <Label className={fieldLabel} style={fieldStyle}>Recherche rapide</Label>
                <UnifiedEntitySearch
                  entityType="league"
                  onSelectDb={handleDbSelect}
                  onSelectApi={handleLeagueApiSelect}
                  placeholder="Nom de la compétition..."
                />
              </div>
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
                  <Label className={fieldLabel} style={fieldStyle}>Type (API)</Label>
                  <Input value={form.type || ''} onChange={e => set('type', e.target.value)} placeholder="League / Cup" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Level</Label>
                  <Select value={form.level || ''} onValueChange={v => set('level', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="Select level" /></SelectTrigger>
                    <SelectContent>
                      {LEAGUE_LEVELS.map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Organizer</Label>
                  <Input value={form.organizer || ''} onChange={e => set('organizer', e.target.value)} placeholder="UEFA" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>API-Football ID</Label>
                  <Input type="number" value={form.apifootball_league_id || ''} onChange={e => set('apifootball_league_id', e.target.value ? parseInt(e.target.value) : '')} placeholder="Auto-fillé ci-dessus" className={inputClass} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                  <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} folder="league" />
                </div>
              </div>
            </>
          )}

          {/* ── SPONSOR ── */}
          {entityType === 'sponsor' && (
            <>
              <div className="pb-3 border-b border-border space-y-1">
                <Label className={fieldLabel} style={fieldStyle}>Recherche rapide</Label>
                <UnifiedEntitySearch
                  entityType="sponsor"
                  onSelectDb={handleDbSelect}
                  onSelectApi={() => {}}
                  placeholder="Nom du sponsor..."
                />
              </div>
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
            </>
          )}

        </div>

        <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
          <Button onClick={handleSubmit} disabled={loading} className="rounded-none">
            {loading && <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />}
            Submit for Review
          </Button>
          <Button variant="outline" onClick={handleClose} className="rounded-none">Cancel</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
