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
import { calculateEstimation, PATCH_OPTIONS } from '@/utils/estimation';

const CONDITION_ORIGINS = ['Shop', 'Training', 'Club Stock', 'Match Prepared', 'Match Worn'];
const PHYSICAL_STATES   = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];

const FLOCKING_OPTIONS = [
  { value: 'none',         label: 'None' },
  { value: 'Official',     label: 'Official (name + number)' },
  { value: 'Personalized', label: 'Personalized' },
];

const SIGNED_TYPES = [
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
  { value: 'legend', label: '⭐ Football Legend' },
  { value: 'star',   label: '🔥 Club Star' },
  { value: 'none',   label: 'Standard player' },
];

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

  // ── Estimation mode ───────────────────────────────────────────────────────────
  const [mode, setMode] = useState(() =>
    typeof window !== 'undefined' ? (window.__tkEstimationMode || 'basic') : 'basic'
  );
  const switchMode = (next) => {
    if (typeof window !== 'undefined') window.__tkEstimationMode = next;
    setMode(next);
  };

  // ── Form state ───────────────────────────────────────────────────────────────
  const [form, setForm] = useState({
    // Basic
    physical_state:      '',
    size:                '',
    // Flocking
    flocking_origin:     'none',
    flocking_detail:     '',
    flocking_player_id:  '',
    // Advanced
    condition_origin:    '',
    patches:             [],       // array de PATCH_OPTIONS.value
    patch_other_text:    '',
    // Signature
    signed:              false,
    signed_type:         '',
    signed_other_text:   '',      // précision si type = 'other'
    signed_player_id:    '',
    player_profile:      'none',
    signed_proof_level:  'none',
    // Rarity
    is_rare:             false,
    rare_reason:         '',
    // Other info
    other_info:          '',
    // Notes
    notes:               '',
  });

  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const set = (field, value) => setForm(f => ({ ...f, [field]: value }));

  // Toggle patch dans le tableau
  const togglePatch = (val) => {
    setForm(f => ({
      ...f,
      patches: f.patches.includes(val)
        ? f.patches.filter(p => p !== val)
        : [...f.patches, val],
    }));
  };

  // ── Live estimation ───────────────────────────────────────────────────────────
  const seasonYear = parseSeasonYear(kit?.season);
  const estimation = calculateEstimation({
    mode,
    modelType:        version?.model       || 'Replica',
    competition:      version?.competition || '',
    conditionOrigin:  form.condition_origin,
    physicalState:    form.physical_state,
    flockingOrigin:   form.flocking_origin === 'none' ? 'None' : form.flocking_origin,
    patches:          form.patches,
    patchOtherText:   form.patch_other_text,
    signed:           form.signed,
    signedType:       form.signed_type,
    signedOtherText:  form.signed_other_text,
    playerProfile:    form.player_profile,
    signedProofLevel: form.signed_proof_level,
    isRare:           form.is_rare,
    rareReason:       form.rare_reason,
    seasonYear,
  });

  // ── Submit ─────────────────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      let resolvedFlockingPlayerId = form.flocking_player_id;
      if (form.flocking_origin === 'Official' && form.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: form.flocking_detail });
          resolvedFlockingPlayerId = r.data?.player_id;
        } catch {}
      }

      // Pour signed_type = 'other', signed_other_text contient le nom
      // Pour signed_type = 'player_flocked', le joueur est le joueur flocqué (pas de champ séparé)
      let resolvedSignedByPlayerId = form.signed_player_id || '';
      if (
        form.signed &&
        form.signed_other_text &&
        !resolvedSignedByPlayerId &&
        form.signed_type === 'other'
      ) {
        try {
          const r = await createPlayerPending({ full_name: form.signed_other_text });
          resolvedSignedByPlayerId = r.data?.player_id;
        } catch {}
      }

      await addToCollection({
        version_id:          version.version_id,
        size:                form.size                              || undefined,
        condition_origin:    form.condition_origin                 || undefined,
        physical_state:      form.physical_state                   || undefined,
        flocking_origin:     form.flocking_origin !== 'none' ? form.flocking_origin : undefined,
        flocking_detail:     form.flocking_origin === 'Official' ? (form.flocking_detail || undefined) : undefined,
        flocking_player_id:  form.flocking_origin === 'Official' ? (resolvedFlockingPlayerId || undefined) : undefined,
        patches:             form.patches.length > 0 ? form.patches : undefined,
        patch_other_text:    form.patches.includes('other') ? (form.patch_other_text || undefined) : undefined,
        signed:              form.signed,
        signed_type:         form.signed ? (form.signed_type      || undefined) : undefined,
        signed_other_text:   form.signed && form.signed_type === 'other' ? (form.signed_other_text || undefined) : undefined,
        player_profile:      form.signed && form.signed_type === 'player_flocked'
                               ? (form.player_profile || 'none')
                               : undefined,
        signed_by_player_id: form.signed && form.signed_type === 'other' ? (resolvedSignedByPlayerId || undefined) : undefined,
        signed_proof_level:  form.signed ? form.signed_proof_level : undefined,
        is_rare:             form.is_rare                         || undefined,
        rare_reason:         form.is_rare && form.rare_reason ? form.rare_reason : undefined,
        other_info:          form.other_info                      || undefined,
        estimated_price:     estimation.estimatedPrice,
        notes:               form.notes                           || undefined,
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

  // ── Derived UI flags ─────────────────────────────────────────────────────────
  const showFlockingPlayer = form.flocking_origin === 'Official';
  // Pas de champ "signed_details" pour player_flocked (le joueur est déjà connu via le flocage)
  const showSignedOther    = form.signed && form.signed_type === 'other';
  const showPlayerProfile  = form.signed && form.signed_type === 'player_flocked';

  return (
    <Sheet open onOpenChange={(open) => { if (!open) onClose(); }}>
      <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader className="mb-4">
          <SheetTitle
            className="text-left tracking-tighter"
            style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}
          >
            ADD TO COLLECTION
          </SheetTitle>
        </SheetHeader>

        {/* ── Aperçu version ── */}
        <div className="flex gap-4 mb-4">
          <img
            src={proxyImageUrl(photo)}
            alt={kit.club}
            className="w-20 h-28 object-cover border border-border shrink-0"
          />
          <div className="flex-1">
            <h3
              className="text-lg font-semibold tracking-tight"
              style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}
            >
              {kit.club}
            </h3>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>
              {kit.season} — {kit.kit_type}
            </p>
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
              <Select
                value={form.physical_state || 'none'}
                onValueChange={v => set('physical_state', v === 'none' ? '' : v)}
              >
                <SelectTrigger className={inputCls}><SelectValue placeholder="Select" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">—</SelectItem>
                  {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1">
              <Label className={fieldLabel} style={fs}>Flocking</Label>
              <Select
                value={form.flocking_origin}
                onValueChange={v => {
                  set('flocking_origin', v);
                  if (v !== 'Official') {
                    set('flocking_detail', '');
                    set('flocking_player_id', '');
                  }
                }}
              >
                <SelectTrigger className={inputCls}><SelectValue placeholder="None" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {FLOCKING_OPTIONS.map(o => <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Joueur flocqué — UNIQUEMENT si Official */}
          {showFlockingPlayer && (
            <div className="space-y-1">
              <Label className={fieldLabel} style={fs}>Flocked Player</Label>
              <EntityAutocomplete
                entityType="player"
                value={form.flocking_detail}
                onChange={val => set('flocking_detail', val)}
                onSelect={item => {
                  set('flocking_detail', item.label);
                  set('flocking_player_id', item.id);
                }}
                placeholder="e.g. Ronaldo 7"
                className={inputCls}
              />
            </div>
          )}

          {/* Size */}
          <div className="space-y-1">
            <Label className={fieldLabel} style={fs}>Size</Label>
            <Select
              value={form.size || 'none'}
              onValueChange={v => set('size', v === 'none' ? '' : v)}
            >
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

              {/* Competition (readonly) + Origin */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Competition</Label>
                  <div className={`${inputCls} border px-3 py-2 text-xs text-muted-foreground flex items-center gap-2`}>
                    <span className="flex-1 truncate">{version?.competition || '—'}</span>
                    <span className="text-[9px] text-primary/50 uppercase tracking-wider" style={fs}>version</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Origin (Condition)</Label>
                  <Select
                    value={form.condition_origin || 'none'}
                    onValueChange={v => set('condition_origin', v === 'none' ? '' : v)}
                  >
                    <SelectTrigger className={inputCls}><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      <SelectItem value="none">—</SelectItem>
                      {CONDITION_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Patches (checkboxes) */}
              <div className="space-y-1">
                <Label className={fieldLabel} style={fs}>Patches</Label>
                <div className="flex flex-col gap-1.5">
                  {PATCH_OPTIONS.map(opt => (
                    <label key={opt.value} className="flex items-center gap-2 text-xs cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={form.patches.includes(opt.value)}
                        onChange={() => togglePatch(opt.value)}
                        className="accent-primary w-3.5 h-3.5"
                      />
                      <span style={fs} className="uppercase tracking-wide text-[11px]">{opt.label}</span>
                      <span className="text-muted-foreground text-[10px]">+{opt.coeff}</span>
                    </label>
                  ))}
                </div>
                {form.patches.includes('other') && (
                  <Input
                    value={form.patch_other_text}
                    onChange={e => set('patch_other_text', e.target.value)}
                    placeholder="Specify patch…"
                    className={`${inputCls} text-xs mt-1`}
                  />
                )}
              </div>

              {/* Rare Jersey */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Switch checked={form.is_rare} onCheckedChange={v => { set('is_rare', v); if (!v) set('rare_reason', ''); }} />
                  <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Rare Jersey</Label>
                </div>
                {form.is_rare && (
                  <Input
                    value={form.rare_reason}
                    onChange={e => set('rare_reason', e.target.value)}
                    placeholder="Ex: limited edition, printing error, unreleased…"
                    className={`${inputCls} text-xs`}
                  />
                )}
              </div>

              {/* Signature */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Switch
                    checked={form.signed}
                    onCheckedChange={v => {
                      set('signed', v);
                      if (!v) {
                        set('signed_type', '');
                        set('player_profile', 'none');
                        set('signed_other_text', '');
                        set('signed_player_id', '');
                        set('signed_proof_level', 'none');
                      }
                    }}
                  />
                  <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Signed</Label>
                </div>

                {form.signed && (
                  <div className="space-y-3 pl-2 border-l-2 border-primary/30 ml-1">

                    {/* Signed by — type */}
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fs}>Signed by</Label>
                      <Select
                        value={form.signed_type || 'none'}
                        onValueChange={v => {
                          set('signed_type', v === 'none' ? '' : v);
                          set('player_profile', 'none');
                          set('signed_other_text', '');
                          set('signed_player_id', '');
                        }}
                      >
                        <SelectTrigger className={inputCls}><SelectValue placeholder="Select…" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          <SelectItem value="none">—</SelectItem>
                          {SIGNED_TYPES.map(t => (
                            <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Précision si type = 'other' UNIQUEMENT — pas pour player_flocked */}
                    {showSignedOther && (
                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fs}>Specify (signed by)</Label>
                        <EntityAutocomplete
                          entityType="player"
                          value={form.signed_other_text}
                          onChange={val => set('signed_other_text', val)}
                          onSelect={item => {
                            set('signed_other_text', item.label);
                            set('signed_player_id', item.id || '');
                          }}
                          placeholder="e.g. Zidane"
                          className={inputCls}
                        />
                      </div>
                    )}

                    {/* Profil joueur — uniquement si player_flocked */}
                    {showPlayerProfile && (
                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fs}>Player Profile</Label>
                        <Select
                          value={form.player_profile}
                          onValueChange={v => set('player_profile', v)}
                        >
                          <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            {PLAYER_PROFILES.map(p => (
                              <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    {/* Preuve */}
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fs}>Proof / Certificate</Label>
                      <Select
                        value={form.signed_proof_level}
                        onValueChange={v => set('signed_proof_level', v)}
                      >
                        <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {PROOF_LEVELS.map(p => (
                            <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
              </div>

              {/* Other info */}
              <div className="space-y-1">
                <Label className={fieldLabel} style={fs}>
                  Other info
                  <span className="normal-case text-muted-foreground/60 ml-1">(no effect on price)</span>
                </Label>
                <Input
                  value={form.other_info}
                  onChange={e => set('other_info', e.target.value)}
                  placeholder="Long sleeve, prototype, banned sponsor…"
                  className={`${inputCls} text-xs`}
                />
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

          {/* ── Estimation live (display-only) ── */}
          <EstimationBreakdown
            mode={mode}
            modelType={version?.model || 'Replica'}
            competition={version?.competition || ''}
            conditionOrigin={form.condition_origin}
            physicalState={form.physical_state}
            flockingOrigin={form.flocking_origin === 'none' ? 'None' : form.flocking_origin}
            patches={form.patches}
            patchOtherText={form.patch_other_text}
            signed={form.signed}
            signedType={form.signed_type}
            signedOtherText={form.signed_other_text}
            playerProfile={form.player_profile}
            signedProofLevel={form.signed_proof_level}
            isRare={form.is_rare}
            rareReason={form.rare_reason}
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
            {loading
              ? <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              : <Check className="w-4 h-4 mr-1" />
            }
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
