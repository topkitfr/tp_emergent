// frontend/src/components/EntityEditDialog.js
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { createSubmission } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import ApiFootballSearch from '@/components/ApiFootballSearch';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };
const inputClass = 'bg-card border-border rounded-none';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];
const AURA_LEVELS = [1, 2, 3, 4, 5];
const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];
const FOOT_OPTIONS = ['right', 'left', 'both'];

const API_POSITION_MAP = {
  'Goalkeeper': ['GK'],
  'Defender': ['CB'], 'Centre-Back': ['CB'], 'Left Back': ['LB'], 'Right Back': ['RB'],
  'Left Wing Back': ['LWB'], 'Right Wing Back': ['RWB'],
  'Midfielder': ['CM'], 'Central Midfield': ['CM'], 'Defensive Midfield': ['CDM'],
  'Attacking Midfield': ['CAM'], 'Left Midfield': ['LM'], 'Right Midfield': ['RM'],
  'Attacker': ['CF'], 'Forward': ['CF'], 'Centre Forward': ['CF'],
  'Striker': ['ST'], 'Left Winger': ['LW'], 'Right Winger': ['RW'], 'Second Striker': ['SS'],
};

function normalizePositions(apiPosition) {
  if (!apiPosition) return [];
  if (Array.isArray(apiPosition)) return apiPosition.filter(p => POSITIONS.includes(p));
  return API_POSITION_MAP[apiPosition] || [];
}

const ENTITY_CONFIGS = {
  team: {
    label: 'Team', nameField: 'name',
    imageField: 'crest_url', imageLabel: 'Crest / Badge',
    folder: 'team',
    apiSearchType: 'team',
    fields: [
      { key: '_apifootball_search', label: '', type: 'apifootball_search', span: 2 },
      // Identité
      { key: 'name',               label: 'Team Name',        required: true },
      { key: 'country',            label: 'Country' },
      { key: 'city',               label: 'City' },
      { key: 'founded',            label: 'Founded (year)',   type: 'number' },
      { key: 'apifootball_team_id',label: 'API-Football ID',  type: 'number' },
      // Stade
      { key: '_stadium_divider',   label: 'Stadium',          type: 'divider', span: 2 },
      { key: 'stadium_name',       label: 'Stadium Name',     span: 2 },
      { key: 'stadium_capacity',   label: 'Capacity',         type: 'number' },
      { key: 'stadium_surface',    label: 'Surface' },
    ],
  },
  league: {
    label: 'League', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    folder: 'league',
    apiSearchType: 'league',
    fields: [
      { key: '_apifootball_search',   label: '', type: 'apifootball_search', span: 2 },
      { key: 'name',                  label: 'League Name',     required: true },
      { key: 'country_or_region',     label: 'Country / Region' },
      { key: 'type',                  label: 'Type (League/Cup)' },
      { key: 'level',                 label: 'Level',           type: 'select', options: LEAGUE_LEVELS },
      { key: 'organizer',             label: 'Organizer' },
      { key: 'apifootball_league_id', label: 'API-Football ID',  type: 'number' },
    ],
  },
  sponsor: {
    label: 'Sponsor', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    folder: 'sponsor',
    fields: [
      { key: 'name',    label: 'Sponsor Name', required: true },
      { key: 'country', label: 'Country' },
      { key: 'website', label: 'Website' },
    ],
  },
  brand: {
    label: 'Brand', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    folder: 'brand',
    fields: [
      { key: 'name',    label: 'Brand Name',    required: true },
      { key: 'country', label: 'Country' },
      { key: 'founded', label: 'Founded (year)', type: 'number' },
    ],
  },
  player: {
    label: 'Player', nameField: 'full_name', imageField: 'photo_url', imageLabel: 'Photo',
    folder: 'player',
    apiSearchType: 'player',
    fields: [
      { key: '_apifootball_search', label: '', type: 'apifootball_search', span: 2 },
      { key: 'full_name',        label: 'Full Name',           required: true, span: 2 },
      { key: 'nationality',      label: 'Nationality' },
      { key: 'birth_date',       label: 'Date of Birth (DD/MM/YYYY)' },
      { key: 'height',           label: 'Height (cm)',          type: 'number' },
      { key: 'weight',           label: 'Weight (kg)',          type: 'number' },
      { key: 'preferred_foot',   label: 'Preferred Foot',       type: 'select', options: FOOT_OPTIONS },
      { key: 'preferred_number', label: 'Preferred Number',     type: 'number' },
      { key: 'positions',        label: 'Positions',            type: 'positions', span: 2 },
      { key: 'bio',              label: 'Bio',                  type: 'textarea',  span: 2 },
    ],
  },
};

export default function EntityEditDialog({
  open,
  onOpenChange,
  entityType,
  mode = 'create',
  initialData = {},
  entityId = null,
  onSuccess,
}) {
  const config = ENTITY_CONFIGS[entityType];
  const [form, setForm] = useState(() => ({ ...initialData }));
  const [submitting, setSubmitting] = useState(false);
  const [showRemoval, setShowRemoval] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');
  const [apiFillName, setApiFillName] = useState('');

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  // ── Auto-fill player ────────────────────────────────────────────────────────
  const handleApiFillPlayer = (player) => {
    setApiFillName(player.name || `${player.firstname || ''} ${player.lastname || ''}`.trim() || '');
    const normalizedPositions = normalizePositions(player.positions || player.position);
    setForm(prev => ({
      ...prev,
      full_name:        player.name || `${player.firstname || ''} ${player.lastname || ''}`.trim() || prev.full_name,
      nationality:      player.nationality    || prev.nationality    || '',
      birth_date:       player.birth_date     || prev.birth_date     || '',
      photo_url:        player.photo          || prev.photo_url      || '',
      height:           player.height         ?? prev.height         ?? '',
      weight:           player.weight         ?? prev.weight         ?? '',
      preferred_foot:   player.preferred_foot || prev.preferred_foot || '',
      preferred_number: player.preferred_number ?? prev.preferred_number ?? '',
      positions:        normalizedPositions.length > 0 ? normalizedPositions : (prev.positions || []),
      apifootball_id:   player.apifootball_id,
    }));
  };

  // ── Auto-fill team ───────────────────────────────────────────────────────────
  const handleApiFillTeam = (team) => {
    setApiFillName(team.name || '');
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

  // ── Auto-fill league ─────────────────────────────────────────────────────────
  const handleApiFillLeague = (league) => {
    setApiFillName(league.name || '');
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

  const getApiFillHandler = () => {
    if (entityType === 'player') return handleApiFillPlayer;
    if (entityType === 'team') return handleApiFillTeam;
    if (entityType === 'league') return handleApiFillLeague;
    return () => {};
  };

  const handleSubmit = async () => {
    const nameKey = config.nameField;
    if (!form[nameKey]?.trim()) {
      toast.error(`${config.label} name is required`);
      return;
    }
    setSubmitting(true);
    try {
      const payload = { ...form, mode };
      if (payload.positions && typeof payload.positions === 'string') {
        payload.positions = payload.positions.split(',').map(p => p.trim()).filter(Boolean);
      }
      for (const f of config.fields) {
        if (f.type === 'number' && payload[f.key]) {
          payload[f.key] = parseInt(payload[f.key], 10) || null;
        }
      }
      if (mode === 'edit' && entityId) payload.entity_id = entityId;
      // Nettoyer les pseudo-champs
      delete payload._apifootball_search;
      delete payload._stadium_divider;
      await createSubmission({ submission_type: entityType, data: payload });
      toast.success(
        mode === 'create'
          ? `${config.label} submitted for review`
          : 'Edit suggestion submitted for review'
      );
      onOpenChange(false);
      if (onSuccess) onSuccess(form[nameKey]);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRequestRemoval = async () => {
    if (!removalNotes.trim()) { toast.error('Please provide a reason for removal'); return; }
    if (!entityId) { toast.error('Entity ID missing'); return; }
    setSubmitting(true);
    try {
      await createSubmission({
        submission_type: entityType,
        data: { mode: 'removal', entity_id: entityId, entity_type: entityType, notes: removalNotes },
      });
      toast.success('Removal request submitted for community review');
      setShowRemoval(false);
      setRemovalNotes('');
      onOpenChange(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (f) => {
    if (f.type === 'divider') {
      return (
        <div className="sm:col-span-2 flex items-center gap-2 pt-1">
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground whitespace-nowrap" style={labelStyle}>
            {f.label}
          </p>
          <div className="flex-1 border-t border-border" />
        </div>
      );
    }

    if (f.type === 'apifootball_search') {
      return (
        <div className="sm:col-span-2 pb-2 border-b border-border">
          <ApiFootballSearch
            entityType={config.apiSearchType || entityType}
            onSelect={getApiFillHandler()}
            filledName={apiFillName}
          />
        </div>
      );
    }

    if (f.type === 'positions') {
      const current = Array.isArray(form.positions) ? form.positions : [];
      return (
        <div className="flex flex-wrap gap-1.5">
          {POSITIONS.map(pos => (
            <button key={pos} type="button"
              onClick={() => handleChange('positions', current.includes(pos) ? current.filter(p => p !== pos) : [...current, pos])}
              className={`px-2 py-0.5 text-[11px] border rounded-none transition-colors ${
                current.includes(pos)
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-card border-border text-muted-foreground hover:border-primary/50'
              }`}
              style={labelStyle}>{pos}</button>
          ))}
        </div>
      );
    }

    if (f.type === 'aura') {
      return (
        <div className="flex gap-1">
          {AURA_LEVELS.map(level => (
            <button key={level} type="button" onClick={() => handleChange('aura_level', level)}
              className={`px-2 py-1 text-xs border rounded-none transition-colors ${
                form.aura_level === level
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-card border-border text-muted-foreground hover:border-primary/50'
              }`}
              style={labelStyle}>{'\u2605'.repeat(level)}</button>
          ))}
        </div>
      );
    }

    if (f.type === 'select') {
      return (
        <Select value={form[f.key] || ''} onValueChange={v => handleChange(f.key, v)}>
          <SelectTrigger className="bg-card border-border rounded-none h-9" data-testid={`entity-edit-${f.key}`}>
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {f.options.map(o => (
              <SelectItem key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    }

    if (f.type === 'textarea') {
      return (
        <Textarea
          value={form[f.key] ?? ''}
          onChange={e => handleChange(f.key, e.target.value)}
          className="bg-card border-border rounded-none min-h-[80px] text-sm"
          placeholder="..."
          data-testid={`entity-edit-${f.key}`}
        />
      );
    }

    return (
      <Input
        type={f.type === 'number' ? 'number' : 'text'}
        value={form[f.key] ?? ''}
        onChange={e => handleChange(f.key, e.target.value)}
        className="bg-card border-border rounded-none"
        data-testid={`entity-edit-${f.key}`}
      />
    );
  };

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg tracking-tight" style={labelStyle}>
            {mode === 'create'
              ? `SUBMIT NEW ${entityType.toUpperCase()}`
              : `SUGGEST EDIT — ${entityType.toUpperCase()}`}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {config.fields.map(f => {
              // Les types structurels (divider, apifootball_search) gèrent leur propre layout
              if (f.type === 'divider' || f.type === 'apifootball_search') {
                return <React.Fragment key={f.key}>{renderField(f)}</React.Fragment>;
              }
              return (
                <div
                  key={f.key}
                  className={`space-y-1 ${
                    f.key === config.nameField || f.span === 2 ? 'sm:col-span-2' : ''
                  }`}
                >
                  <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                    {f.label} {f.required && '*'}
                  </Label>
                  {renderField(f)}
                </div>
              );
            })}
          </div>

          <div className="space-y-1">
            <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
              {config.imageLabel}
            </Label>
            <ImageUpload
              value={form[config.imageField] || ''}
              onChange={v => handleChange(config.imageField, v)}
              folder={config.folder}
              testId={`entity-edit-${config.imageField}`}
            />
          </div>

          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            {mode === 'create'
              ? 'This will be submitted for community review before being added.'
              : 'Your suggested changes will be reviewed by the community.'}
          </p>

          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
            data-testid="entity-edit-submit"
          >
            {submitting ? 'Submitting...' : mode === 'create' ? 'Submit for Review' : 'Submit Edit'}
          </Button>

          {mode === 'edit' && entityId && (
            <div className="border-t border-border pt-4">
              {!showRemoval ? (
                <Button
                  variant="outline" size="sm"
                  onClick={() => setShowRemoval(true)}
                  className="rounded-none border-destructive/50 text-destructive hover:bg-destructive/10 w-full"
                  data-testid="entity-request-removal-btn"
                >
                  <Trash2 className="w-4 h-4 mr-1" /> Request Removal
                </Button>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-wider text-destructive" style={labelStyle}>REQUEST REMOVAL</p>
                  <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    The community will vote on this removal request.
                  </p>
                  <Textarea
                    value={removalNotes}
                    onChange={e => setRemovalNotes(e.target.value)}
                    placeholder="Explain why this entry should be removed..."
                    className="bg-card border-border rounded-none min-h-[80px] text-sm"
                    data-testid="entity-removal-notes"
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleRequestRemoval}
                      disabled={submitting || !removalNotes.trim()}
                      className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      data-testid="entity-submit-removal-btn">
                      <Trash2 className="w-3 h-3 mr-1" /> Submit Removal Request
                    </Button>
                    <Button size="sm" variant="outline"
                      onClick={() => { setShowRemoval(false); setRemovalNotes(''); }}
                      className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
