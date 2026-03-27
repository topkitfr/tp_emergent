// src/components/AddToCollectionDialog.js
// Sheet panel identique au formulaire d'édition de MyCollection
import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { proxyImageUrl, addToCollection, createPlayerPending, getPlayerAura } from '@/lib/api';
import { Check, Trash2, Loader2 } from 'lucide-react';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';

const CONDITION_ORIGINS = ['Club Stock', 'Match Prepared', 'Match Worn', 'Training', 'Shop'];
const PHYSICAL_STATES  = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_TYPES   = ['Name+Number', 'Name', 'Number'];
const FLOCKING_ORIGINS = ['Official', 'Personalized'];
const SIZES            = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];
const CATEGORIES       = ['General', 'Match Worn', 'Signed', 'Display', 'Loan'];

const fieldLabel = 'text-xs uppercase tracking-wider';
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none';

function parseSeasonYear(season) {
  if (!season) return 0;
  const match = season.match(/(\d{4})/);
  return match ? parseInt(match[1]) : 0;
}

export default function AddToCollectionDialog({ version, onClose, onSuccess }) {
  const kit   = version?.master_kit || {};
  const photo = version?.front_photo || kit?.front_photo;

  const [form, setForm] = useState({
    category:            'General',
    size:                '',
    condition_origin:    '',
    physical_state:      '',
    flocking_type:       '',
    flocking_origin:     '',
    flocking_detail:     '',
    flocking_player_id:  '',
    signed:              false,
    signed_by:           '',
    signed_by_player_id: '',
    signed_proof:        false,
    purchase_cost:       '',
    notes:               '',
  });
  const [loading,              setLoading]              = useState(false);
  const [error,                setError]                = useState('');
  const [signedPlayerAuraLevel, setSignedPlayerAuraLevel] = useState(0);

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

  const seasonYear = parseSeasonYear(kit?.season);
  const estimation = calculateEstimation({
    modelType:       version?.model       || 'Replica',
    competition:     version?.competition || '',
    conditionOrigin: form.condition_origin,
    physicalState:   form.physical_state,
    flockingOrigin:  form.flocking_origin,
    signed:          form.signed,
    signedProof:     form.signed_proof,
    seasonYear,
    auraLevel:       signedPlayerAuraLevel,
  });

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      let resolvedFlockingPlayerId = form.flocking_player_id;
      let resolvedSignedByPlayerId = form.signed_by_player_id;

      if (form.flocking_detail && !resolvedFlockingPlayerId) {
        try { const r = await createPlayerPending({ full_name: form.flocking_detail }); resolvedFlockingPlayerId = r.data?.player_id; } catch {}
      }
      if (form.signed && form.signed_by && !resolvedSignedByPlayerId) {
        try { const r = await createPlayerPending({ full_name: form.signed_by }); resolvedSignedByPlayerId = r.data?.player_id; } catch {}
      }

      await addToCollection({
        version_id:          version.version_id,
        category:            form.category,
        size:                form.size                || undefined,
        condition_origin:    form.condition_origin    || undefined,
        physical_state:      form.physical_state      || undefined,
        flocking_type:       form.flocking_type       || undefined,
        flocking_origin:     form.flocking_origin     || undefined,
        flocking_detail:     form.flocking_detail     || undefined,
        flocking_player_id:  resolvedFlockingPlayerId || undefined,
        signed:              form.signed,
        signed_by:           form.signed_by           || undefined,
        signed_by_player_id: resolvedSignedByPlayerId || undefined,
        signed_proof:        form.signed_proof,
        purchase_cost:       form.purchase_cost ? parseFloat(form.purchase_cost) : undefined,
        estimated_price:     estimation.estimatedPrice,
        notes:               form.notes               || undefined,
      });
      onSuccess?.();
    } catch (err) {
      if (err?.response?.status === 400) {
        setError('This version is already in your collection.');
      } else {
        setError(err?.response?.data?.detail || 'An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Sheet open onOpenChange={(open) => { if (!open) onClose(); }}>
      <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader className="mb-6">
          <SheetTitle className="text-left tracking-tighter" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>ADD TO COLLECTION</SheetTitle>
        </SheetHeader>

        {/* Aperçu version */}
        <div className="flex gap-4 mb-6">
          <img
            src={proxyImageUrl(photo)}
            alt={kit.club}
            className="w-20 h-28 object-cover border border-border shrink-0"
          />
          <div className="flex-1">
            <h3 className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{kit.club}</h3>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.season} - {kit.kit_type}</p>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.brand}</p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline" className="rounded-none text-[10px]">{version?.model || 'None'}</Badge>
              <Badge variant="outline" className="rounded-none text-[10px]">{version?.competition || 'None'}</Badge>
            </div>
          </div>
        </div>

        <div className="space-y-4">

          {/* Catégorie */}
          <div className="space-y-1">
            <Label className={fieldLabel} style={fieldStyle}>Category</Label>
            <Select value={form.category} onValueChange={v => set('category', v)}>
              <SelectTrigger className={inputClass}><SelectValue /></SelectTrigger>
              <SelectContent className="bg-card border-border">
                {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Flocking */}
          <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>FLOCKING</p>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Type</Label>
              <Select value={form.flocking_type || 'none'} onValueChange={v => set('flocking_type', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="None" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {FLOCKING_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Origin</Label>
              <Select value={form.flocking_origin || 'none'} onValueChange={v => set('flocking_origin', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="None" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Player</Label>
              <EntityAutocomplete
                entityType="player"
                value={form.flocking_detail}
                onChange={val => set('flocking_detail', val)}
                onSelect={item => { set('flocking_detail', item.label); set('flocking_player_id', item.id); }}
                placeholder="e.g., Messi"
                className={inputClass}
              />
            </div>
          </div>

          {/* Condition */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Condition (Origin)</Label>
              <Select value={form.condition_origin || 'none'} onValueChange={v => set('condition_origin', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {CONDITION_ORIGINS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Physical State</Label>
              <Select value={form.physical_state || 'none'} onValueChange={v => set('physical_state', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Size + Purchase Cost */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Size</Label>
              <Select value={form.size || 'none'} onValueChange={v => set('size', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={fieldLabel} style={fieldStyle}>Purchase Cost (€)</Label>
              <Input
                type="number"
                value={form.purchase_cost}
                onChange={e => set('purchase_cost', e.target.value)}
                placeholder="0"
                className={`${inputClass} font-mono`}
              />
            </div>
          </div>

          {/* Signed */}
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Switch checked={form.signed} onCheckedChange={v => set('signed', v)} />
                <Label className="text-xs" style={fieldStyle}>SIGNED</Label>
              </div>
              {form.signed && (
                <div className="flex-1">
                  <EntityAutocomplete
                    entityType="player"
                    value={form.signed_by}
                    onChange={val => set('signed_by', val)}
                    onSelect={item => {
                      set('signed_by', item.label);
                      set('signed_by_player_id', item.id);
                      if (item.id) {
                        getPlayerAura(item.id)
                          .then(r => setSignedPlayerAuraLevel(r.data?.aura_level || 0))
                          .catch(() => setSignedPlayerAuraLevel(0));
                      }
                    }}
                    placeholder="Player name"
                    className={inputClass}
                  />
                </div>
              )}
            </div>
            {form.signed && (
              <div className="flex items-center gap-2 ml-12">
                <Switch checked={form.signed_proof} onCheckedChange={v => set('signed_proof', v)} />
                <Label className="text-[10px] text-muted-foreground" style={fieldStyle}>PROOF / CERTIFICATE</Label>
              </div>
            )}
          </div>

          {/* Notes */}
          <div className="space-y-1">
            <Label className={fieldLabel} style={fieldStyle}>Notes</Label>
            <Textarea
              value={form.notes}
              onChange={e => set('notes', e.target.value)}
              placeholder="Any notes..."
              className="bg-card border-border rounded-none min-h-[80px]"
            />
          </div>

          {/* Estimation live */}
          <EstimationBreakdown
            modelType={version?.model || 'Replica'}
            competition={version?.competition || ''}
            conditionOrigin={form.condition_origin}
            physicalState={form.physical_state}
            flockingOrigin={form.flocking_origin}
            signed={form.signed}
            signedProof={form.signed_proof}
            seasonYear={seasonYear}
            auraLevel={signedPlayerAuraLevel}
          />

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <div className="flex gap-2 mt-6">
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 flex-1"
          >
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-1" />}
            {loading ? 'Adding...' : 'Add to Collection'}
          </Button>
          <Button variant="outline" onClick={onClose} disabled={loading} className="rounded-none">
            Cancel
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
