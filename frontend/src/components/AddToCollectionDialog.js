// src/components/AddToCollectionDialog.js
import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { proxyImageUrl, addToCollection, createPlayerPending } from '@/lib/api';
import { Check, Loader2, Zap, SlidersHorizontal } from 'lucide-react';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';

const CONDITION_ORIGINS = ['Shop', 'Training', 'Club Stock', 'Match Prepared', 'Match Worn'];
const PHYSICAL_STATES   = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_ORIGINS  = ['Official', 'Personalized'];
const SIGNED_TYPES      = [
  { value: 'player_flocked', label: 'Signed by flocked player' },
  { value: 'team',           label: 'Signed by the team' },
  { value: 'other',          label: 'Other (specify)' },
];
const PROOF_LEVELS = [
  { value: 'none',   label: 'No proof' },
  { value: 'light',  label: 'Light certificate / weak provenance' },
  { value: 'strong', label: 'Solid proof (photo/video + COA)' },
];
const PLAYER_PROFILES = [
  { value: 'legend', label: 'Football Legend' },
  { value: 'star',   label: 'Club Star' },
  { value: 'none',   label: 'Standard player' },
];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];

const fieldLabel = 'text-[10px] uppercase tracking-wider text-muted-foreground';
const fs         = { fontFamily: 'Barlow Condensed' };
const inputCls   = 'bg-card border-border rounded-none';

function parseSeasonYear(season) {
  if (!season) return 0;
  const match = season.match(/(\d{4})/);
  return match ? parseInt(match[1]) : 0;
}

export default function AddToCollectionDialog({ version, onClose, onSuccess }) {
  const kit   = version?.master_kit || {};
  const photo = version?.front_photo || kit?.front_photo;

  // ─── Estimation mode ───────────────────────────────────────────────────────
  const [mode, setMode] = useState(() =>
    typeof window !== 'undefined' ? (window.__tkEstimationMode || 'basic') : 'basic'
  );
  const switchMode = (next) => {
    if (typeof window !== 'undefined') window.__tkEstimationMode = next;
    setMode(next);
  };

  // ─── Form state ────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    // ── Basic
    physical_state:      '',
    flocking_origin:     '',
    flocking_detail:     '',
    flocking_player_id:  '',
    size:                '',
    // ── Advanced extras
    condition_origin:    '',
    has_patch:           false,
    signed:              false,
    signed_type:         '',
    player_profile:      'none',
    signed_details:      '',
    signed_player_id:    '',
    signed_proof_level:  'none',
    is_rare:             false,
    rare_reason:         '',
    // ── Always
    notes:               '',
  });

  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

  // ─── Live estimation ───────────────────────────────────────────────────────
  const seasonYear = parseSeasonYear(kit?.season);
  const estimation = calculateEstimation({
    mode,
    modelType:        version?.model       || 'Replica',
    competition:      version?.competition || '',
    conditionOrigin:  form.condition_origin,
    physicalState:    form.physical_state,
    flockingOrigin:   form.flocking_origin || 'None',
    hasPatch:         form.has_patch,
    signed:           form.signed,
    signedType:       form.signed_type,
    playerProfile:    form.player_profile,
    signedProofLevel: form.signed_proof_level,
    isRare:           form.is_rare,
    seasonYear,
  });

  // ─── Submit ────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      let resolvedFlockingPlayerId = form.flocking_player_id;
      if (form.flocking_detail && !resolvedFlockingPlayerId) {
        try { const r = await createPlayerPending({ full_name: form.flocking_detail }); resolvedFlockingPlayerId = r.data?.player_id; } catch {}
      }
      let resolvedSignedByPlayerId = form.signed_player_id || '';
      if (form.signed && form.signed_details && !resolvedSignedByPlayerId &&
          (form.signed_type === 'player_flocked' || form.signed_type === 'other')) {
        try { const r = await createPlayerPending({ full_name: form.signed_details }); resolvedSignedByPlayerId = r.data?.player_id; } catch {}
      }

      await addToCollection({
        version_id:          version.version_id,
        size:                form.size                || undefined,
        condition_origin:    form.condition_origin    || undefined,
        physical_state:      form.physical_state      || undefined,
        flocking_origin:     form.flocking_origin     || undefined,
        flocking_detail:     form.flocking_detail     || undefined,
        flocking_player_id:  resolvedFlockingPlayerId || undefined,
        has_patch:           form.has_patch           || undefined,
        signed:              form.signed,
        signed_type:         form.signed_type         || undefined,
        player_profile:      form.signed && form.signed_type === 'player_flocked'
                               ? (form.player_profile || 'none')
                               : undefined,
        signed_by:           form.signed_details      || undefined,
        signed_by_player_id: resolvedSignedByPlayerId || undefined,
        // signed_proof_level sent as string ('none' | 'light' | 'strong')
        signed_proof_level:  form.signed ? form.signed_proof_level : undefined,
        is_rare:             form.is_rare             || undefined,
        rare_reason:         form.is_rare && form.rare_reason ? form.rare_reason : undefined,
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

  const showFlockingPlayer = form.flocking_origin === 'Official';
  const showPlayerProfile  = form.signed && form.signed_type === 'player_flocked';
  const showSignedDetails  = form.signed && (form.signed_type === 'player_flocked' || form.signed_type === 'other');

  return (
    <Sheet open onOpenChange={(open) => { if (!open) onClose(); }}>
      <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader className="mb-4">
          <SheetTitle className="text-left tracking-tighter" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>ADD TO COLLECTION</SheetTitle>
        </SheetHeader>

        {/* ── Aperçu version ── */}
        <div className="flex gap-4 mb-4">
          <img
            src={proxyImageUrl(photo)}
            alt={kit.club}
            className="w-20 h-28 object-cover border border-border shrink-0"
          />
          <div className="flex-1">
            <h3 className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{kit.club}</h3>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>{kit.season} — {kit.kit_type}</p>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>{kit.brand}</p>
            <div className="flex gap-2 mt-2">
              <Badge variant="outline" className="rounded-none text-[10px]">{version?.model || '—'}</Badge>
              <Badge variant="outline" className="rounded-none text-[10px]">{version?.competition || '—'}</Badge>
            </div>
          </div>
        </div>

        {/* ══ TOGGLE BASIC / ADVANCED ══ */}
        <div className="flex items-center gap-2 mb-5 border border-border p-1" style={fs}>
          <button
            onClick={() => switchMode('basic')}
            className={`flex items-center gap-1.5 flex-1 justify-center text-[11px] uppercase tracking-wider py-1.5 transition-colors ${
              mode === 'basic'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Zap className="w-3 h-3" />
            Basic
          </button>
          <button
            onClick={() => switchMode('advanced')}
            className={`flex items-center gap-1.5 flex-1 justify-center text-[11px] uppercase tracking-wider py-1.5 transition-colors ${
              mode === 'advanced'
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <SlidersHorizontal className="w-3 h-3" />
            Advanced
          </button>
        </div>

        <div className="space-y-4">

          {/* ══ BASIC FIELDS ══ */}

          {/* Row 1 : Physical State + Flocking */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className={fieldLabel} style={fs}>Physical State</Label>
              <Select value={form.physical_state || 'none'} onValueChange={v => set('physical_state', v === 'none' ? '' : v)}>
                <SelectTrigger className={inputCls}><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">—</SelectItem>
                  {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={fieldLabel} style={fs}>Flocking</Label>
              <Select value={form.flocking_origin || 'none'} onValueChange={v => {
                set('flocking_origin', v === 'none' ? '' : v);
                if (v !== 'Official') {
                  set('flocking_detail', '');
                  set('flocking_player_id', '');
                }
              }}>
                <SelectTrigger className={inputCls}><SelectValue placeholder="None" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">None</SelectItem>
                  {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Flocked player — uniquement si Official */}
          {showFlockingPlayer && (
            <div className="space-y-1">
              <Label className={fieldLabel} style={fs}>Flocked Player</Label>
              <EntityAutocomplete
                entityType="player"
                value={form.flocking_detail}
                onChange={val => set('flocking_detail', val)}
                onSelect={item => { set('flocking_detail', item.label); set('flocking_player_id', item.id); }}
                placeholder="e.g. Ronaldo 7"
                className={inputCls}
              />
            </div>
          )}

          {/* Size */}
          <div className="space-y-1">
            <Label className={fieldLabel} style={fs}>Size</Label>
            <Select value={form.size || 'none'} onValueChange={v => set('size', v === 'none' ? '' : v)}>
              <SelectTrigger className={inputCls}><SelectValue placeholder="Select" /></SelectTrigger>
              <SelectContent className="bg-card border-border">
                <SelectItem value="none">—</SelectItem>
                {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>

          {/* ══ ADVANCED ONLY ══ */}
          {mode === 'advanced' && (
            <>
              <div className="flex items-center gap-2">
                <div className="h-px flex-1 bg-border" />
                <span className="text-[9px] uppercase tracking-widest text-muted-foreground" style={fs}>Advanced</span>
                <div className="h-px flex-1 bg-border" />
              </div>

              {/* Competition (readonly display) + Origin */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Competition</Label>
                  <div className={`${inputCls} border px-3 py-2 text-xs text-muted-foreground flex items-center gap-2`}>
                    <span className="flex-1 truncate">{version?.competition || '—'}</span>
                    <span className="text-[9px] text-primary/50 uppercase tracking-wider" style={fs}>from version</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Origin (Condition)</Label>
                  <Select value={form.condition_origin || 'none'} onValueChange={v => set('condition_origin', v === 'none' ? '' : v)}>
                    <SelectTrigger className={inputCls}><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      <SelectItem value="none">—</SelectItem>
                      {CONDITION_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Patch + Rare */}
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <Switch checked={form.has_patch} onCheckedChange={v => set('has_patch', v)} />
                  <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Official Patch</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Switch checked={form.is_rare} onCheckedChange={v => set('is_rare', v)} />
                  <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Rare Jersey</Label>
                </div>
              </div>

              {form.is_rare && (
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Why rare? <span className="normal-case text-muted-foreground/70">(optional)</span></Label>
                  <Input
                    value={form.rare_reason}
                    onChange={e => set('rare_reason', e.target.value)}
                    placeholder="Ex: limited edition, printing error, unreleased..."
                    className={`${inputCls} text-xs`}
                  />
                </div>
              )}

              {/* ── Signature ── */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Switch checked={form.signed} onCheckedChange={v => {
                    set('signed', v);
                    if (!v) {
                      set('signed_type', '');
                      set('player_profile', 'none');
                      set('signed_details', '');
                      set('signed_player_id', '');
                      set('signed_proof_level', 'none');
                    }
                  }} />
                  <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Signed</Label>
                </div>

                {form.signed && (
                  <div className="space-y-3 pl-2 border-l-2 border-primary/30 ml-1">
                    {/* Signed by */}
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fs}>Signed by</Label>
                      <Select value={form.signed_type || 'none'} onValueChange={v => {
                        set('signed_type', v === 'none' ? '' : v);
                        set('player_profile', 'none');
                        set('signed_details', '');
                        set('signed_player_id', '');
                      }}>
                        <SelectTrigger className={inputCls}><SelectValue placeholder="Select..." /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          <SelectItem value="none">—</SelectItem>
                          {SIGNED_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Nom / précision — uniquement si player_flocked ou other (pas team) */}
                    {showSignedDetails && (
                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fs}>
                          {form.signed_type === 'player_flocked' ? 'Flocked player (signed)' : 'Specify (signed by)'}
                        </Label>
                        <EntityAutocomplete
                          entityType="player"
                          value={form.signed_details}
                          onChange={val => set('signed_details', val)}
                          onSelect={item => {
                            set('signed_details', item.label);
                            set('signed_player_id', item.id || '');
                          }}
                          placeholder={form.signed_type === 'player_flocked' ? 'e.g. Maldini' : 'e.g. Zidane'}
                          className={inputCls}
                        />
                      </div>
                    )}

                    {/* Player Profile — uniquement si player_flocked */}
                    {showPlayerProfile && (
                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fs}>Player Profile</Label>
                        <Select value={form.player_profile} onValueChange={v => set('player_profile', v)}>
                          <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            {PLAYER_PROFILES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Proof */}
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fs}>Proof / Certificate</Label>
                      <Select value={form.signed_proof_level} onValueChange={v => set('signed_proof_level', v)}>
                        <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {PROOF_LEVELS.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}

          {/* ── Notes (Basic + Advanced) ── */}
          <div className="space-y-1">
            <Label className={fieldLabel} style={fs}>Notes</Label>
            <Textarea
              value={form.notes}
              onChange={e => set('notes', e.target.value)}
              placeholder="Any notes, details, context..."
              className="bg-card border-border rounded-none min-h-[70px]"
            />
          </div>

          {/* ── Estimation live ── */}
          <EstimationBreakdown
            mode={mode}
            modelType={version?.model || 'Replica'}
            competition={version?.competition || ''}
            conditionOrigin={form.condition_origin}
            physicalState={form.physical_state}
            flockingOrigin={form.flocking_origin || 'None'}
            hasPatch={form.has_patch}
            signed={form.signed}
            signedType={form.signed_type}
            playerProfile={form.player_profile}
            signedProofLevel={form.signed_proof_level}
            isRare={form.is_rare}
            seasonYear={seasonYear}
          />

          {error && <p className="text-sm text-destructive">{error}</p>}
        </div>

        {/* ── Actions ── */}
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
