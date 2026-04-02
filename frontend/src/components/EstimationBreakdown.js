import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Zap, SlidersHorizontal } from 'lucide-react';
import { calculateEstimation } from '@/utils/estimation';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

const fs = { fontFamily: 'Barlow Condensed' };
const labelCls = 'text-[10px] uppercase tracking-wider text-muted-foreground';
const inputCls = 'bg-card border-border rounded-none h-8 text-xs';

const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];
const PHYSICAL_STATES = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const CONDITION_ORIGINS = ['Shop', 'Training', 'Club Stock', 'Match Prepared', 'Match Worn'];
const SIGNED_TYPES = [
  { value: 'player_flocked', label: 'Signed by flocked player' },
  { value: 'team', label: 'Signed by the team' },
  { value: 'other', label: 'Other (specify)' },
];
const PROOF_LEVELS = [
  { value: 'none', label: 'No proof' },
  { value: 'light', label: 'Light certificate / weak provenance' },
  { value: 'strong', label: 'Solid proof (photo/video + COA)' },
];
const PLAYER_PROFILES = [
  { value: 'none', label: '—' },
  { value: 'club_star', label: 'Club star' },
  { value: 'football_legend', label: 'Football legend' },
];

export default function EstimationBreakdown({
  modelType = 'Replica',
  competition = '',
  physicalState = '',
  conditionOrigin = '',
  flockingOrigin = 'None',
  flockingDetail = '',
  flockingPlayerProfile = 'none',
  signed = false,
  signedType = '',
  signedProofLevel = 'none',
  signedDetails = '',
  hasPatch = false,
  isRare = false,
  rareReason = '',
  seasonYear = 0,
  editable = false,
  onChange,
}) {
  const [mode, setMode] = useState(() =>
    typeof window !== 'undefined'
      ? (window.__tkEstimationMode || 'basic')
      : 'basic'
  );
  const [open, setOpen] = useState(false);

  const switchMode = (next) => {
    if (typeof window !== 'undefined') window.__tkEstimationMode = next;
    setMode(next);
  };

  const result = calculateEstimation({
    mode,
    modelType,
    competition,
    conditionOrigin,
    physicalState,
    flockingOrigin,
    flockingPlayerProfile,
    hasPatch,
    signed,
    signedType,
    signedProofLevel,
    isRare,
    seasonYear,
  });

  const set = (field) => (val) => onChange && onChange(field, val);

  // Profil joueur : visible uniquement si signed + player_flocked + Official
  const showPlayerProfile =
    signed && signedType === 'player_flocked' && flockingOrigin === 'Official';

  return (
    <div className="border border-border bg-card" style={fs}>

      {/* ── Header ── */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border">
        <span className={labelCls}>ESTIMATION</span>
        <div className="flex items-center gap-2">

          {/* Toggle Basic / Advanced */}
          <button
            onClick={() => switchMode(mode === 'basic' ? 'advanced' : 'basic')}
            className={`flex items-center gap-1 text-[10px] uppercase tracking-wider px-2 py-1 border transition-colors ${
              mode === 'advanced'
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border text-muted-foreground hover:border-primary/40'
            }`}
          >
            {mode === 'advanced'
              ? <SlidersHorizontal className="w-3 h-3" />
              : <Zap className="w-3 h-3" />}
            {mode === 'advanced' ? 'Advanced' : 'Basic'}
          </button>

          <span className="font-mono text-base text-accent font-semibold">
            {result.estimatedPrice}€
          </span>

          <button onClick={() => setOpen(v => !v)} className="text-muted-foreground hover:text-foreground">
            {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* ── Breakdown detail ── */}
      {open && (
        <div className="px-3 py-2 space-y-1">
          <div className="flex justify-between text-[10px] text-muted-foreground">
            <span>Base ({modelType})</span>
            <span className="font-mono">{result.basePrice}€</span>
          </div>
          {result.breakdown.map((b, i) => (
            <div key={i} className="flex justify-between text-[10px]">
              <span className="text-muted-foreground">{b.label}</span>
              <span className={`font-mono ${
                b.coeff > 0 ? 'text-green-500' : b.coeff < 0 ? 'text-destructive' : 'text-muted-foreground'
              }`}>
                {b.coeff > 0 ? '+' : ''}{b.coeff}
              </span>
            </div>
          ))}
          <div className="flex justify-between text-[10px] border-t border-border pt-1">
            <span className="text-muted-foreground">Multiplier</span>
            <span className="font-mono">× {(1 + result.coeffSum).toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-xs font-semibold border-t border-border pt-1">
            <span>Estimated price</span>
            <span className="font-mono text-accent">{result.estimatedPrice}€</span>
          </div>
        </div>
      )}

      {/* ── Form (editable only) ── */}
      {editable && (
        <div className="px-3 pt-2 pb-3 space-y-3 border-t border-border">

          {/* ─ ALWAYS: Model + Physical state ─ */}
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label className={labelCls} style={fs}>Model</Label>
              <Select value={modelType} onValueChange={set('modelType')}>
                <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="Authentic">Authentic</SelectItem>
                  <SelectItem value="Replica">Replica</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className={labelCls} style={fs}>Physical state</Label>
              <Select value={physicalState || 'none'} onValueChange={v => set('physicalState')(v === 'none' ? '' : v)}>
                <SelectTrigger className={inputCls}><SelectValue placeholder="—" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="none">—</SelectItem>
                  {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* ─ ALWAYS: Flocking ─ */}
          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <Label className={labelCls} style={fs}>Flocking</Label>
              <Select value={flockingOrigin || 'None'} onValueChange={set('flockingOrigin')}>
                <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="None">None</SelectItem>
                  <SelectItem value="Official">Official</SelectItem>
                  <SelectItem value="Personalized">Personalized</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {/* Joueur flocqué — si Official uniquement */}
            {flockingOrigin === 'Official' && (
              <div className="space-y-1">
                <Label className={labelCls} style={fs}>Flocked player</Label>
                <Input
                  placeholder="Ex: Ronaldo 7"
                  className={inputCls}
                  value={flockingDetail}
                  onChange={e => onChange && onChange('flocking_detail', e.target.value)}
                />
              </div>
            )}
          </div>

          {/* ─ ADVANCED ONLY ─────────────────────────────────── */}
          {mode === 'advanced' && (
            <>
              {/* Competition + Origin */}
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <Label className={labelCls} style={fs}>Competition</Label>
                  <Select value={competition || 'none'} onValueChange={v => set('competition')(v === 'none' ? '' : v)}>
                    <SelectTrigger className={inputCls}><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      <SelectItem value="none">—</SelectItem>
                      {COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <Label className={labelCls} style={fs}>Origin</Label>
                  <Select value={conditionOrigin || 'none'} onValueChange={v => set('conditionOrigin')(v === 'none' ? '' : v)}>
                    <SelectTrigger className={inputCls}><SelectValue placeholder="—" /></SelectTrigger>
                    <SelectContent className="bg-card border-border">
                      <SelectItem value="none">—</SelectItem>
                      {CONDITION_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Patch + Rareté */}
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <Switch id="est-patch" checked={hasPatch} onCheckedChange={set('hasPatch')} />
                  <Label htmlFor="est-patch" className={labelCls} style={fs}>Official patch</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Switch id="est-rare" checked={isRare} onCheckedChange={set('isRare')} />
                  <Label htmlFor="est-rare" className={labelCls} style={fs}>Rare jersey</Label>
                </div>
              </div>

              {/* Raison rareté */}
              {isRare && (
                <div className="space-y-1">
                  <Label className={labelCls} style={fs}>Why rare? (optional)</Label>
                  <Input
                    placeholder="Ex: limited edition, printing error, unreleased..."
                    className={inputCls}
                    value={rareReason}
                    onChange={e => onChange && onChange('rareReason', e.target.value)}
                  />
                </div>
              )}

              {/* Signature */}
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Switch id="est-signed" checked={signed} onCheckedChange={set('signed')} />
                  <Label htmlFor="est-signed" className={labelCls} style={fs}>Signed</Label>
                </div>

                {signed && (
                  <div className="space-y-2 pl-1 border-l border-border ml-1">
                    <div className="space-y-1">
                      <Label className={labelCls} style={fs}>Signed by</Label>
                      <Select value={signedType || 'none'} onValueChange={v => set('signedType')(v === 'none' ? '' : v)}>
                        <SelectTrigger className={inputCls}><SelectValue placeholder="Select..." /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          <SelectItem value="none">—</SelectItem>
                          {SIGNED_TYPES.map(t => (
                            <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Précision si "other" */}
                    {signedType === 'other' && (
                      <div className="space-y-1">
                        <Label className={labelCls} style={fs}>Specify</Label>
                        <Input
                          placeholder="Ex: Signed by Zidane during..."
                          className={inputCls}
                          value={signedDetails}
                          onChange={e => onChange && onChange('signedDetails', e.target.value)}
                        />
                      </div>
                    )}

                    <div className="space-y-1">
                      <Label className={labelCls} style={fs}>Proof / certificate</Label>
                      <Select value={signedProofLevel || 'none'} onValueChange={set('signedProofLevel')}>
                        <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {PROOF_LEVELS.map(p => (
                            <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Profil joueur flocqué — conditionnel strict */}
                    {showPlayerProfile && (
                      <div className="space-y-1">
                        <Label className={labelCls} style={fs}>Flocked player profile</Label>
                        <Select value={flockingPlayerProfile || 'none'} onValueChange={set('flockingPlayerProfile')}>
                          <SelectTrigger className={inputCls}><SelectValue /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            {PLAYER_PROFILES.map(p => (
                              <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Notes libres */}
              <div className="space-y-1">
                <Label className={labelCls} style={fs}>Other info (no price impact)</Label>
                <Textarea
                  placeholder="Ex: long sleeve version, pre-season prototype, banned sponsor..."
                  className={`${inputCls} h-14 resize-none`}
                  onChange={e => onChange && onChange('estimation_notes', e.target.value)}
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
