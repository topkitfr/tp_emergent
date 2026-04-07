// frontend/src/components/EntityEditDialog.js
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { createSubmission, searchApiFootballPlayers } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import { toast } from 'sonner';
import { Trash2, Loader2, Search, CheckCircle2 } from 'lucide-react';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };
const inputClass = 'bg-card border-border rounded-none';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];
const AURA_LEVELS = [1, 2, 3, 4, 5];
const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];

const ENTITY_CONFIGS = {
  team: {
    label: 'Team', nameField: 'name',
    imageField: 'crest_url', imageLabel: 'Crest / Badge',
    folder: 'team',
    fields: [
      { key: 'name',            label: 'Team Name',       required: true },
      { key: 'country',         label: 'Country' },
      { key: 'city',            label: 'City' },
      { key: 'founded',         label: 'Founded (year)',   type: 'number' },
      { key: 'primary_color',   label: 'Primary Color' },
      { key: 'secondary_color', label: 'Secondary Color' },
    ],
  },
  league: {
    label: 'League', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    folder: 'league',
    fields: [
      { key: 'name',              label: 'League Name',     required: true },
      { key: 'country_or_region', label: 'Country / Region' },
      { key: 'level',             label: 'Level',           type: 'select', options: LEAGUE_LEVELS },
      { key: 'organizer',         label: 'Organizer' },
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
    fields: [
      { key: 'full_name',        label: 'Full Name',              required: true, span: 2 },
      { key: 'nationality',      label: 'Nationality' },
      { key: 'birth_date',       label: 'Date of Birth (DD/MM/YYYY)' },
      { key: 'preferred_number', label: 'Preferred Number',       type: 'number' },
      { key: 'apifootball_id',   label: 'API-Football ID',        type: 'apifootball_search', span: 2 },
      { key: 'positions',        label: 'Positions',              type: 'positions', span: 2 },
      { key: 'bio',              label: 'Bio',                    type: 'textarea',  span: 2 },
    ],
  },
};

/**
 * ApiFootballSearchField — champ recherche live + dropdown pour EntityEditDialog.
 * Gestion locale de la query, auto-fill via onFill(player).
 */
function ApiFootballSearchField({ currentId, onFill }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [filledName, setFilledName] = useState('');
  const debounceRef = useRef(null);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleInput = useCallback((val) => {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (val.length < 3) { setResults([]); setOpen(false); return; }
    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchApiFootballPlayers(val);
        setResults(res.data.players || []);
        setOpen(true);
      } catch { setResults([]); }
      finally { setLoading(false); }
    }, 500);
  }, []);

  const handleSelect = (player) => {
    setQuery('');
    setResults([]);
    setOpen(false);
    setFilledName(player.name || player.firstname || '');
    onFill(player);
  };

  return (
    <div ref={wrapperRef} className="space-y-1.5">
      {/* Affichage de l'ID actuel */}
      {currentId && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
          <span style={labelStyle}>Current ID:</span>
          <code className="px-1.5 py-0.5 bg-muted rounded text-xs font-mono">{currentId}</code>
        </div>
      )}

      {/* Input de recherche */}
      <div className="relative">
        <Input
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          placeholder="Search player on API-Football..."
          className={`${inputClass} pr-8`}
        />
        <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none">
          {loading
            ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
            : <Search className="w-3.5 h-3.5" />}
        </span>
      </div>

      {/* Dropdown */}
      {open && results.length > 0 && (
        <ul className="absolute z-50 w-full mt-1 bg-popover border border-border shadow-lg max-h-64 overflow-y-auto">
          {results.map((p) => (
            <li
              key={p.apifootball_id}
              onClick={() => handleSelect(p)}
              className="flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-accent transition-colors"
            >
              {p.photo && (
                <img src={p.photo} alt={p.name} className="w-8 h-8 rounded-full object-cover flex-shrink-0 bg-muted" />
              )}
              <div className="min-w-0">
                <p className="text-sm font-medium truncate" style={labelStyle}>{p.name}</p>
                <p className="text-xs text-muted-foreground truncate">
                  {[p.nationality, p.birth_date].filter(Boolean).join(' · ')}
                </p>
              </div>
              <span className="ml-auto text-[10px] text-muted-foreground flex-shrink-0 font-mono">#{p.apifootball_id}</span>
            </li>
          ))}
        </ul>
      )}

      {open && results.length === 0 && !loading && query.length >= 3 && (
        <div className="text-xs text-muted-foreground px-1 mt-1">No results for « {query} »</div>
      )}

      {filledName && (
        <div className="flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span style={labelStyle}>Auto-filled: <strong>{filledName}</strong></span>
        </div>
      )}
    </div>
  );
}

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

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  /** Auto-fill depuis résultat API-Football */
  const handleApiFill = (player) => {
    setForm(prev => ({
      ...prev,
      full_name:      player.name || `${player.firstname || ''} ${player.lastname || ''}`.trim() || prev.full_name,
      nationality:    player.nationality || prev.nationality || '',
      birth_date:     player.birth_date  || prev.birth_date  || '',
      photo_url:      player.photo       || prev.photo_url   || '',
      apifootball_id: player.apifootball_id,
    }));
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
    if (!removalNotes.trim()) {
      toast.error('Please provide a reason for removal');
      return;
    }
    if (!entityId) {
      toast.error('Entity ID missing');
      return;
    }
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
    if (f.type === 'apifootball_search') {
      return (
        <ApiFootballSearchField
          currentId={form.apifootball_id || ''}
          onFill={handleApiFill}
        />
      );
    }

    if (f.type === 'positions') {
      const current = Array.isArray(form.positions) ? form.positions : [];
      return (
        <div className="flex flex-wrap gap-1.5">
          {POSITIONS.map(pos => (
            <button
              key={pos}
              type="button"
              onClick={() =>
                handleChange(
                  'positions',
                  current.includes(pos)
                    ? current.filter(p => p !== pos)
                    : [...current, pos]
                )
              }
              className={`px-2 py-0.5 text-[11px] border rounded-none transition-colors ${
                current.includes(pos)
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-card border-border text-muted-foreground hover:border-primary/50'
              }`}
              style={labelStyle}
            >
              {pos}
            </button>
          ))}
        </div>
      );
    }

    if (f.type === 'aura') {
      return (
        <div className="flex gap-1">
          {AURA_LEVELS.map(level => (
            <button
              key={level}
              type="button"
              onClick={() => handleChange('aura_level', level)}
              className={`px-2 py-1 text-xs border rounded-none transition-colors ${
                form.aura_level === level
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-card border-border text-muted-foreground hover:border-primary/50'
              }`}
              style={labelStyle}
            >
              {'\u2605'.repeat(level)}
            </button>
          ))}
        </div>
      );
    }

    if (f.type === 'select') {
      return (
        <Select
          value={form[f.key] || ''}
          onValueChange={v => handleChange(f.key, v)}
        >
          <SelectTrigger
            className="bg-card border-border rounded-none h-9"
            data-testid={`entity-edit-${f.key}`}
          >
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {f.options.map(o => (
              <SelectItem key={o} value={o}>
                {o.charAt(0).toUpperCase() + o.slice(1)}
              </SelectItem>
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
            {config.fields.map(f => (
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
            ))}
          </div>

          {/* Image upload */}
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

          {/* Removal section — mode edit uniquement */}
          {mode === 'edit' && entityId && (
            <div className="border-t border-border pt-4">
              {!showRemoval ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRemoval(true)}
                  className="rounded-none border-destructive/50 text-destructive hover:bg-destructive/10 w-full"
                  data-testid="entity-request-removal-btn"
                >
                  <Trash2 className="w-4 h-4 mr-1" /> Request Removal
                </Button>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs uppercase tracking-wider text-destructive" style={labelStyle}>
                    REQUEST REMOVAL
                  </p>
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
                    <Button
                      size="sm"
                      onClick={handleRequestRemoval}
                      disabled={submitting || !removalNotes.trim()}
                      className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      data-testid="entity-submit-removal-btn"
                    >
                      <Trash2 className="w-3 h-3 mr-1" /> Submit Removal Request
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => { setShowRemoval(false); setRemovalNotes(''); }}
                      className="rounded-none"
                    >
                      Cancel
                    </Button>
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
