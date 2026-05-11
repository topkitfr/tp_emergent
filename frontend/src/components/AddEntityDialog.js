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
  parseApiError,
} from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import UnifiedEntitySearch from '@/components/UnifiedEntitySearch';
import IndividualAwardsField from '@/components/IndividualAwardsField';
import PositionsToggle from '@/components/entity-form/PositionsToggle';
import TeamTypeToggle from '@/components/entity-form/TeamTypeToggle';
import FlagPreview from '@/components/entity-form/FlagPreview';
import {
  LEAGUE_LEVELS,
  SURFACE_OPTIONS,
  GENDER_OPTIONS,
  FOOT_OPTIONS,
  LEAGUE_TYPE_OPTIONS,
  LEAGUE_ENTITY_TYPE_OPTIONS,
  LEAGUE_SCOPE_OPTIONS,
} from '@/lib/entityFields';

const fieldLabel = 'text-xs uppercase tracking-wider';
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none';

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

  // ── Handlers DB séléct ────────────────────────────────────────────────────
  const handleDbSelect = (item) => {
    toast.warning(
      `« ${item.name || item.full_name || item.label} » existe déjà en base de données. Préremplissage effectué.`,
      { duration: 5000 }
    );
    if (entityType === 'player')  handlePlayerDbSelect(item);
    if (entityType === 'team')    handleTeamDbSelect(item);
    if (entityType === 'league')  handleLeagueDbSelect(item);
    if (entityType === 'brand')   set('name', item.name || '');
    if (entityType === 'sponsor') set('name', item.name || '');
  };

  const handlePlayerDbSelect = (item) => {
    setForm(prev => ({
      ...prev,
      full_name:         item.full_name || item.name || '',
      first_name:        item.first_name || '',
      last_name:         item.last_name || '',
      nationality:       item.nationality || '',
      birth_date:        item.birth_date || '',
      birth_place:       item.birth_place || '',
      birth_country:     item.birth_country || '',
      photo_url:         item.photo_url || item.photo || '',
      height:            item.height ?? '',
      weight:            item.weight ?? '',
      preferred_foot:    item.preferred_foot || '',
      preferred_number:  item.preferred_number ?? '',
      individual_awards: item.individual_awards || [],
      positions:         item.positions || [],
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
      gender:              item.gender || '',
      crest_url:           item.crest_url || '',
      stadium_name:        item.stadium_name || '',
      stadium_capacity:    item.stadium_capacity || '',
      stadium_surface:     item.stadium_surface || '',
      stadium_city:        item.stadium_city || '',
      stadium_country:     item.stadium_country || '',
      stadium_image_url:   item.stadium_image_url || '',
    }));
  };

  const handleLeagueDbSelect = (item) => {
    setForm(prev => ({
      ...prev,
      name:                item.name || '',
      country_or_region:   item.country_or_region || '',
      country_code:        item.country_code || '',
      country_flag:        item.country_flag || '',
      type:                item.type || '',
      entity_type:         item.entity_type || '',
      scope:               item.scope || '',
      gender:              item.gender || '',
      organizer:           item.organizer || '',
      logo_url:            item.logo_url || '',
    }));
  };

  // ── Mapper form → payload backend ─────────────────────────────────────────
  // Normalise les types pour correspondre au modèle Pydantic backend :
  // - height / weight : str | null (le backend attend Optional[str])
  // - preferred_number : int | null ("" doit devenir null)
  const buildPlayerPayload = (f) => ({
    ...f,
    firstname:        f.first_name || f.firstname || '',
    lastname:         f.last_name  || f.lastname  || '',
    first_name:       undefined,
    last_name:        undefined,
    height:           f.height != null && f.height !== ''
                        ? String(f.height)
                        : null,
    weight:           f.weight != null && f.weight !== ''
                        ? String(f.weight)
                        : null,
    preferred_number: f.preferred_number != null && f.preferred_number !== ''
                        ? parseInt(f.preferred_number, 10)
                        : null,
  });

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

      const payload = entityType === 'player' ? buildPlayerPayload(form) : form;
      await fns[entityType](payload);

      const labels = { player: 'Player', team: 'Team', brand: 'Brand', league: 'League', sponsor: 'Sponsor' };
      toast.success(`${labels[entityType]} submitted for community review`);
      handleClose();
      onSuccess?.();
    } catch (e) {
      // parseApiError normalise les erreurs Pydantic [{type,loc,msg}] en string
      // pour éviter React error #31 (objet rendu comme noeud DOM dans le toast)
      toast.error(parseApiError(e, 'Submission failed'));
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
                  placeholder="Nom du joueur..."
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Full Name *</Label>
                  <Input value={form.full_name || ''} onChange={e => set('full_name', e.target.value)} placeholder="Zinédine Zidane" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Prénom</Label>
                  <Input value={form.first_name || ''} onChange={e => set('first_name', e.target.value)} placeholder="Zinédine" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Nom de famille</Label>
                  <Input value={form.last_name || ''} onChange={e => set('last_name', e.target.value)} placeholder="Zidane" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Nationality</Label>
                  <Input value={form.nationality || ''} onChange={e => set('nationality', e.target.value)} placeholder="French" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Date of Birth (DD/MM/YYYY)</Label>
                  <Input value={form.birth_date || ''} onChange={e => set('birth_date', e.target.value)} placeholder="23/06/1972" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Lieu de naissance</Label>
                  <Input value={form.birth_place || ''} onChange={e => set('birth_place', e.target.value)} placeholder="Marseille" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Pays de naissance</Label>
                  <Input value={form.birth_country || ''} onChange={e => set('birth_country', e.target.value)} placeholder="France" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Height (cm)</Label>
                  <Input type="number" value={form.height || ''} onChange={e => set('height', e.target.value ? parseInt(e.target.value) : '')} placeholder="185" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Weight (kg)</Label>
                  <Input type="number" value={form.weight || ''} onChange={e => set('weight', e.target.value ? parseInt(e.target.value) : '')} placeholder="80" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Preferred Foot</Label>
                  <Select value={form.preferred_foot || ''} onValueChange={v => set('preferred_foot', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="Pied" /></SelectTrigger>
                    <SelectContent>
                      {FOOT_OPTIONS.map(f => <SelectItem key={f} value={f}>{f.charAt(0).toUpperCase() + f.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Preferred Number</Label>
                  <Input type="number" value={form.preferred_number || ''} onChange={e => set('preferred_number', e.target.value ? parseInt(e.target.value) : '')} placeholder="10" className={inputClass} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Positions</Label>
                  <PositionsToggle
                    value={form.positions || []}
                    onChange={val => set('positions', val)}
                  />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Distinctions individuelles</Label>
                  <IndividualAwardsField
                    value={form.individual_awards || []}
                    onChange={val => set('individual_awards', val)}
                  />
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
                  <Label className={fieldLabel} style={fieldStyle}>Genre</Label>
                  <Select value={form.gender || ''} onValueChange={v => set('gender', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="Genre" /></SelectTrigger>
                    <SelectContent>
                      {GENDER_OPTIONS.map(g => <SelectItem key={g} value={g}>{g.charAt(0).toUpperCase() + g.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Type</Label>
                  <TeamTypeToggle
                    value={form.is_national}
                    onChange={val => set('is_national', val)}
                  />
                </div>
                <div className="col-span-2 flex items-center gap-2 pt-1">
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground whitespace-nowrap" style={fieldStyle}>Stadium</p>
                  <div className="flex-1 border-t border-border" />
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
                  <Select value={form.stadium_surface || ''} onValueChange={v => set('stadium_surface', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="Surface" /></SelectTrigger>
                    <SelectContent>
                      {SURFACE_OPTIONS.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Ville du stade</Label>
                  <Input value={form.stadium_city || ''} onChange={e => set('stadium_city', e.target.value)} placeholder="Barcelona" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Pays du stade</Label>
                  <Input value={form.stadium_country || ''} onChange={e => set('stadium_country', e.target.value)} placeholder="Spain" className={inputClass} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Crest / Badge</Label>
                  <ImageUpload value={form.crest_url || ''} onChange={url => set('crest_url', url)} folder="team" />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Stadium Image</Label>
                  <ImageUpload value={form.stadium_image_url || ''} onChange={url => set('stadium_image_url', url)} folder="team" />
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
                  <Label className={fieldLabel} style={fieldStyle}>Country Code</Label>
                  <Input value={form.country_code || ''} onChange={e => set('country_code', e.target.value)} placeholder="GB" className={inputClass} />
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Type</Label>
                  <Select value={form.type || ''} onValueChange={v => set('type', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="League / Cup" /></SelectTrigger>
                    <SelectContent>
                      {LEAGUE_TYPE_OPTIONS.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Entity Type</Label>
                  <Select value={form.entity_type || ''} onValueChange={v => set('entity_type', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="league / cup / confederation" /></SelectTrigger>
                    <SelectContent>
                      {LEAGUE_ENTITY_TYPE_OPTIONS.map(t => <SelectItem key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Scope</Label>
                  <Select value={form.scope || ''} onValueChange={v => set('scope', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="domestic / international" /></SelectTrigger>
                    <SelectContent>
                      {LEAGUE_SCOPE_OPTIONS.map(s => <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
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
                  <Label className={fieldLabel} style={fieldStyle}>Genre</Label>
                  <Select value={form.gender || ''} onValueChange={v => set('gender', v)}>
                    <SelectTrigger className={`${inputClass} h-9`}><SelectValue placeholder="Genre" /></SelectTrigger>
                    <SelectContent>
                      {GENDER_OPTIONS.map(g => <SelectItem key={g} value={g}>{g.charAt(0).toUpperCase() + g.slice(1)}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Organizer</Label>
                  <Input value={form.organizer || ''} onChange={e => set('organizer', e.target.value)} placeholder="UEFA" className={inputClass} />
                </div>
                <div className="col-span-2 space-y-1.5">
                  <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                  <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} folder="league" />
                </div>
                {form.country_flag && (
                  <div className="col-span-2">
                    <FlagPreview flagUrl={form.country_flag} code={form.country_code} />
                  </div>
                )}
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
