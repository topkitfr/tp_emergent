// src/components/CollectionItemForm.js
// Formulaire unifié pour ajouter OU modifier un item de collection.
// Utilisé par : AddToCollectionDialog.js (VersionDetail) + MyCollection.js (edit)

import { Zap, SlidersHorizontal } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { PATCH_OPTIONS } from '@/utils/estimation';

export const PHYSICAL_STATES   = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
export const CONDITION_ORIGINS = ['Shop', 'Training', 'Club Stock', 'Match Prepared', 'Match Worn'];
export const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];

export const FLOCKING_OPTIONS = [
  { value: 'none',         label: 'None' },
  { value: 'Official',     label: 'Official (name + number)' },
  { value: 'Personalized', label: 'Personalized' },
];

export const SIGNED_TYPES = [
  { value: 'player_flocked', label: 'Signed by flocked player' },
  { value: 'team',           label: 'Signed by the team' },
  { value: 'handsigned',     label: 'Handsigned autograph' },
  { value: 'printed_sign',   label: 'Printed sign (marketing)' },
  { value: 'other',          label: 'Other (specify)' },
];

export const PROOF_LEVELS = [
  { value: 'none',   label: 'No proof' },
  { value: 'light',  label: 'Light certificate / weak provenance' },
  { value: 'strong', label: 'Solid proof (photo/video + COA)' },
];

export const INITIAL_FORM_STATE = {
  physical_state:           '',
  size:                     '',
  flocking_origin:          'none',
  flocking_detail:          '',
  flocking_player_id:       '',
  condition_origin:         '',
  patches:                  [],
  patch_other_text:         '',
  signed:                   false,
  signed_type:              '',
  signed_other_text:        '',
  signed_player_id:         '',
  signed_personal_message:  false,
  signed_proof_level:       'none',
  is_rare:                  false,
  rare_reason:              '',
  notes:                    '',
};

export function formFromItem(item) {
  let patches = [];
  if (Array.isArray(item.patches) && item.patches.length > 0) {
    patches = item.patches;
  } else if (item.has_patch || item.patch) {
    patches = ['competition'];
  }

  return {
    physical_state:          item.physical_state || item.condition || '',
    size:                    item.size || '',
    flocking_origin:         item.flocking_origin || 'none',
    flocking_detail:         item.flocking_detail || item.printing || '',
    flocking_player_id:      item.flocking_player_id || '',
    condition_origin:        item.condition_origin || '',
    patches,
    patch_other_text:        item.patch_other_text || '',
    signed:                  item.signed || false,
    signed_type:             item.signed_type || '',
    signed_other_text:       item.signed_other_text || item.signed_by || '',
    signed_player_id:        item.signed_by_player_id || '',
    signed_personal_message: item.signed_personal_message || false,
    signed_proof_level:      item.signed_proof_level
                              ? item.signed_proof_level
                              : item.signed_proof ? 'light' : 'none',
    is_rare:                 item.is_rare || false,
    rare_reason:             item.rare_reason || '',
    notes:                   item.notes || '',
  };
}

export function formToPayload(form, estimation) {
  const proofLevel = form.signed_proof_level || 'none';
  const hasPatch = Array.isArray(form.patches) && form.patches.length > 0;

  return {
    physical_state: form.physical_state || undefined,
    size: form.size || undefined,
    flocking_origin: form.flocking_origin !== 'none' ? form.flocking_origin : undefined,
    flocking_detail: form.flocking_origin === 'Official' ? (form.flocking_detail || undefined) : undefined,
    flocking_player_id: form.flocking_origin === 'Official' ? (form.flocking_player_id || undefined) : undefined,
    condition_origin: form.condition_origin || undefined,
    patch: hasPatch || undefined,
    signed: form.signed,
    signed_type: form.signed ? (form.signed_type || undefined) : undefined,
    signed_other_detail: form.signed && form.signed_type === 'other' ? (form.signed_other_text || undefined) : undefined,
    signed_by_player_id: form.signed && form.signed_type === 'other' ? (form.signed_player_id || undefined) : undefined,
    signed_personal_message: form.signed ? !!form.signed_personal_message : undefined,
    signed_proof: form.signed ? proofLevel : 'none',
    signed_proof_level: form.signed ? proofLevel : undefined,
    is_rare: form.is_rare || undefined,
    rare_reason: form.is_rare && form.rare_reason ? form.rare_reason : undefined,
    notes: form.notes || undefined,
    estimated_price: estimation?.estimatedPrice ?? estimation?.estimated_price,
  };
}

const fieldLabel = 'text-[10px] uppercase tracking-wider text-muted-foreground';
const fs = { fontFamily: 'Barlow Condensed' };
const inputCls = 'bg-card border-border rounded-none';

export default function CollectionItemForm({
  form,
  onChange,
  mode = 'basic',
  onModeChange,
  version = {},
  seasonYear = 0,
  showEstimation = true,
  flockingPlayerNote = 0,
}) {
  const set = (field, value) => onChange(field, value);

  const togglePatch = (val) => {
    const next = form.patches.includes(val)
      ? form.patches.filter(p => p !== val)
      : [...form.patches, val];
    set('patches', next);
  };

  const showFlockingPlayer = form.flocking_origin === 'Official';
  const showSignedOther = form.signed && form.signed_type === 'other';
  const isPersonalized = form.flocking_origin === 'Personalized';

  return (
    <div className="space-y-4">
      {onModeChange && (
        <div className="flex items-center gap-2 border border-border p-1" style={fs}>
          <button
            type="button"
            onClick={() => onModeChange('basic')}
            className={`flex items-center gap-1.5 flex-1 justify-center text-[11px] uppercase tracking-wider py-1.5 transition-colors ${
              mode === 'basic' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Zap className="w-3 h-3" />
            Basic
          </button>
          <button
            type="button"
            onClick={() => onModeChange('advanced')}
            className={`flex items-center gap-1.5 flex-1 justify-center text-[11px] uppercase tracking-wider py-1.5 transition-colors ${
              mode === 'advanced' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <SlidersHorizontal className="w-3 h-3" />
            Advanced
          </button>
        </div>
      )}

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

      {showFlockingPlayer && !isPersonalized && (
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

      {mode === 'advanced' && (
        <>
          <div className="flex items-center gap-2">
            <div className="h-px flex-1 bg-border" />
            <span className="text-[9px] uppercase tracking-widest text-muted-foreground" style={fs}>Advanced</span>
            <div className="h-px flex-1 bg-border" />
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

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Switch
                checked={form.signed}
                onCheckedChange={v => {
                  set('signed', v);
                  if (!v) {
                    set('signed_type', '');
                    set('signed_other_text', '');
                    set('signed_player_id', '');
                    set('signed_personal_message', false);
                    set('signed_proof_level', 'none');
                  }
                }}
              />
              <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fs}>Signed</Label>
            </div>

            {form.signed && (
              <div className="space-y-3 pl-2 border-l-2 border-primary/30 ml-1">
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Signed type</Label>
                  <Select
                    value={form.signed_type || 'none'}
                    onValueChange={v => {
                      set('signed_type', v === 'none' ? '' : v);
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

                {showSignedOther && (
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fs}>Signed by (specify)</Label>
                    <EntityAutocomplete
                      entityType="player"
                      value={form.signed_other_text}
                      onChange={val => set('signed_other_text', val)}
                      onSelect={item => {
                        set('signed_other_text', item.label);
                        set('signed_player_id', item.id || '');
                      }}
                      placeholder="e.g. Zidane, Ronaldo…"
                      className={inputCls}
                    />
                  </div>
                )}

                <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={!!form.signed_personal_message}
                    onChange={e => set('signed_personal_message', e.target.checked)}
                    className="accent-primary w-3.5 h-3.5"
                  />
                  <span style={fs} className="uppercase tracking-wide text-[11px]">Personal message</span>
                  <span className="text-muted-foreground text-[10px]">-0.20</span>
                </label>

                <div className="space-y-1">
                  <Label className={fieldLabel} style={fs}>Proof / Certificate</Label>
                  <Select value={form.signed_proof_level} onValueChange={v => set('signed_proof_level', v)}>
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

          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Switch
                checked={form.is_rare}
                onCheckedChange={v => { set('is_rare', v); if (!v) set('rare_reason', ''); }}
              />
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
        </>
      )}

      <div className="space-y-1">
        <Label className={fieldLabel} style={fs}>
          Notes
          {mode === 'advanced' && (
            <span className="normal-case text-muted-foreground/60 ml-1">(no effect on price)</span>
          )}
        </Label>
        <Textarea
          value={form.notes}
          onChange={e => set('notes', e.target.value)}
          placeholder="Any notes, details, context…"
          className="bg-card border-border rounded-none min-h-[70px]"
        />
      </div>

      {showEstimation && (
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
          signedPersonalMessage={!!form.signed_personal_message}
          signedProofLevel={form.signed_proof_level}
          isRare={form.is_rare}
          rareReason={form.rare_reason}
          seasonYear={seasonYear}
          flockingPlayerNote={flockingPlayerNote}
        />
      )}
    </div>
  );
}
