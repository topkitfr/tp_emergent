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
import { createPlayerPending, createTeamPending, createBrandPending, createLeaguePending, createSponsorPending } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];
const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];

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
                  <Label className={fieldLabel} style={fieldStyle}>Date of Birth (DD/MM/YYYY)</Label>
                  <Input
                    value={form.birth_date || ''}
                    onChange={e => set('birth_date', e.target.value)}
                    placeholder="23/06/1972"
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
                    placeholder="Player photo URL or upload"
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
                <Input
                  value={form.name || ''}
                  onChange={e => set('name', e.target.value)}
                  placeholder="Real Madrid"
                  className={inputClass}
                />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Country</Label>
                <Input value={form.country || ''} onChange={e => set('country', e.target.value)} placeholder="Spain" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>City</Label>
                <Input value={form.city || ''} onChange={e => set('city', e.target.value)} placeholder="Madrid" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Founded Year</Label>
                <Input type="number" value={form.founded || ''} onChange={e => set('founded', e.target.value ? parseInt(e.target.value) : '')} placeholder="1902" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Primary Color</Label>
                <Input value={form.primary_color || ''} onChange={e => set('primary_color', e.target.value)} placeholder="#FFFFFF" className={inputClass} />
              </div>
              <div className="space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Secondary Color</Label>
                <Input value={form.secondary_color || ''} onChange={e => set('secondary_color', e.target.value)} placeholder="#000000" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Crest / Badge</Label>
                <ImageUpload value={form.crest_url || ''} onChange={url => set('crest_url', url)} placeholder="Badge URL or upload" />
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
                <Label className={fieldLabel} style={fieldStyle}>Founded Year</Label>
                <Input type="number" value={form.founded || ''} onChange={e => set('founded', e.target.value ? parseInt(e.target.value) : '')} placeholder="1949" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} placeholder="Logo URL or upload" />
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
                  <SelectTrigger className={`${inputClass} h-10`}>
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    {LEAGUE_LEVELS.map(l => (
                      <SelectItem key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Organizer</Label>
                <Input value={form.organizer || ''} onChange={e => set('organizer', e.target.value)} placeholder="The FA" className={inputClass} />
              </div>
              <div className="col-span-2 space-y-1.5">
                <Label className={fieldLabel} style={fieldStyle}>Logo</Label>
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} placeholder="Logo URL or upload" />
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
                <ImageUpload value={form.logo_url || ''} onChange={url => set('logo_url', url)} placeholder="Logo URL or upload" />
              </div>
            </div>
          )}

        </div>

        <div className="px-6 py-4 border-t border-border flex gap-3">
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1 rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {loading ? 'Submitting…' : 'Submit for Review'}
          </Button>
          <Button variant="outline" onClick={handleClose} className="rounded-none">
            Cancel
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
