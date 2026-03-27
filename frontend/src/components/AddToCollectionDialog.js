// src/components/AddToCollectionDialog.js
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { proxyImageUrl, addToCollection, createPlayerPending } from '@/lib/api';
import { Shirt, Loader2 } from 'lucide-react';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';

const SIZES             = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];
const CONDITION_ORIGINS = ['Club Stock', 'Match Prepared', 'Match Worn', 'Training', 'Shop'];
const PHYSICAL_STATES  = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_TYPES   = ['Name+Number', 'Name', 'Number'];
const FLOCKING_ORIGINS = ['Official', 'Personalized'];
const CATEGORIES       = ['General', 'Match Worn', 'Signed', 'Display', 'Loan'];

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
    category:          'General',
    size:              '',
    condition_origin:  '',
    physical_state:    '',
    flocking_type:     '',
    flocking_origin:   '',
    flocking_detail:   '',
    flocking_player_id:'',
    signed:            false,
    signed_by:         '',
    signed_by_player_id: '',
    signed_proof:      false,
    purchase_cost:     '',
    notes:             '',
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

  const seasonYear = parseSeasonYear(kit?.season);
  const estimation = calculateEstimation({
    modelType:       version?.model || 'Replica',
    competition:     version?.competition || '',
    conditionOrigin: form.condition_origin,
    physicalState:   form.physical_state,
    flockingOrigin:  form.flocking_origin,
    signed:          form.signed,
    signedProof:     form.signed_proof,
    seasonYear,
    auraLevel:       0,
  });

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      let resolvedFlockingPlayerId   = form.flocking_player_id;
      let resolvedSignedByPlayerId   = form.signed_by_player_id;

      if (form.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const res = await createPlayerPending({ full_name: form.flocking_detail });
          resolvedFlockingPlayerId = res.data?.player_id;
        } catch {}
      }
      if (form.signed && form.signed_by && !resolvedSignedByPlayerId) {
        try {
          const res = await createPlayerPending({ full_name: form.signed_by });
          resolvedSignedByPlayerId = res.data?.player_id;
        } catch {}
      }

      await addToCollection({
        version_id:          version.version_id,
        category:            form.category,
        size:                form.size || undefined,
        condition_origin:    form.condition_origin || undefined,
        physical_state:      form.physical_state || undefined,
        flocking_type:       form.flocking_type || undefined,
        flocking_origin:     form.flocking_origin || undefined,
        flocking_detail:     form.flocking_detail || undefined,
        flocking_player_id:  resolvedFlockingPlayerId || undefined,
        signed:              form.signed,
        signed_by:           form.signed_by || undefined,
        signed_by_player_id: resolvedSignedByPlayerId || undefined,
        signed_proof:        form.signed_proof,
        purchase_cost:       form.purchase_cost ? parseFloat(form.purchase_cost) : undefined,
        estimated_price:     estimation.estimatedPrice,
        notes:               form.notes || undefined,
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
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle style={{ ...fieldStyle, textTransform: 'uppercase', fontSize: '1.1rem' }}>
            Add to Collection
          </DialogTitle>
        </DialogHeader>

        {/* Aperçu version */}
        <div className="flex items-center gap-3 p-3 bg-secondary/30 border border-border">
          <div className="w-14 h-14 bg-secondary border border-border flex items-center justify-center overflow-hidden shrink-0">
            {photo
              ? <img src={proxyImageUrl(photo)} alt={kit.club} className="w-full h-full object-cover" />
              : <Shirt className="w-6 h-6 text-muted-foreground" />}
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-sm truncate uppercase" style={fieldStyle}>{kit.club ?? '—'}</p>
            <p className="text-xs text-muted-foreground">{kit.season} · {version.competition} · {version.model}</p>
            {kit.brand && <p className="font-mono text-[10px] text-muted-foreground">{kit.brand}</p>}
          </div>
        </div>

        <div className="space-y-4">

          {/* Catégorie */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Category</Label>
            <Select value={form.category} onValueChange={v => set('category', v)}>
              <SelectTrigger className={inputClass}><SelectValue /></SelectTrigger>
              <SelectContent className="bg-card border-border">
                {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Taille + Provenance */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Size</Label>
              <Select value={form.size} onValueChange={v => set('size', v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Origin</Label>
              <Select value={form.condition_origin} onValueChange={v => set('condition_origin', v)}>
                <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {CONDITION_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* État physique */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Condition</Label>
            <Select value={form.physical_state} onValueChange={v => set('physical_state', v)}>
              <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
              <SelectContent className="bg-card border-border">
                {PHYSICAL_STATES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* Flocage */}
          <div className="border border-border/50 p-3 space-y-3">
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={fieldStyle}>Flocking / Printing</p>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Type</Label>
                <Select value={form.flocking_type} onValueChange={v => set('flocking_type', v)}>
                  <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {FLOCKING_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Origin</Label>
                <Select value={form.flocking_origin} onValueChange={v => set('flocking_origin', v)}>
                  <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                  <SelectContent className="bg-card border-border">
                    {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            {form.flocking_type && (
              <div className="space-y-1.5">
                <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Player Name / Detail</Label>
                <EntityAutocomplete
                  entityType="player"
                  value={form.flocking_detail}
                  onChange={val => set('flocking_detail', val)}
                  onSelect={item => { set('flocking_detail', item.label); set('flocking_player_id', item.id); }}
                  placeholder="e.g., Zidane"
                  className={inputClass}
                />
              </div>
            )}
          </div>

          {/* Signed */}
          <div className="border border-border/50 p-3 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={fieldStyle}>Signed</p>
              <Switch checked={form.signed} onCheckedChange={v => set('signed', v)} />
            </div>
            {form.signed && (
              <>
                <div className="space-y-1.5">
                  <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Signed by</Label>
                  <EntityAutocomplete
                    entityType="player"
                    value={form.signed_by}
                    onChange={val => set('signed_by', val)}
                    onSelect={item => { set('signed_by', item.label); set('signed_by_player_id', item.id); }}
                    placeholder="e.g., Ronaldo"
                    className={inputClass}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Proof of signature</Label>
                  <Switch checked={form.signed_proof} onCheckedChange={v => set('signed_proof', v)} />
                </div>
              </>
            )}
          </div>

          {/* Prix d'achat */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Purchase Cost (€)</Label>
            <Input
              type="number"
              placeholder="Optional"
              value={form.purchase_cost}
              onChange={e => set('purchase_cost', e.target.value)}
              className={`${inputClass} font-mono`}
            />
          </div>

          {/* Estimation live */}
          <EstimationBreakdown estimation={estimation} />

          {/* Notes */}
          <div className="space-y-1.5">
            <Label className="text-xs uppercase tracking-wide text-muted-foreground" style={fieldStyle}>Notes</Label>
            <Textarea
              placeholder="Optional notes..."
              value={form.notes}
              onChange={e => set('notes', e.target.value)}
              rows={2}
              className={`${inputClass} resize-none text-sm`}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading} className="rounded-none">Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
            {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Adding...</> : 'Add to collection'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
