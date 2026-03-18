import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { createSubmission } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };

const ENTITY_CONFIGS = {
  team: {
    label: 'Team', nameField: 'name',
    // FIXED: était 'logo_url' — le champ réel en DB est 'crest_url'
    imageField: 'crest_url', imageLabel: 'Crest / Badge',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'country', label: 'Country' },
      { key: 'city', label: 'City' },
      { key: 'founded', label: 'Founded (year)', type: 'number' },
      { key: 'primary_color', label: 'Primary Color' },
      { key: 'secondary_color', label: 'Secondary Color' },
    ],
  },
  league: {
    label: 'League', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'country_or_region', label: 'Country / Region' },
      { key: 'level', label: 'Level', type: 'select', options: ['domestic', 'continental', 'international', 'cup'] },
      { key: 'organizer', label: 'Organizer' },
    ],
  },
  sponsor: {
    label: 'Sponsor', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'country', label: 'Country' },
    ],
  },
  brand: {
    label: 'Brand', nameField: 'name', imageField: 'logo_url', imageLabel: 'Logo',
    fields: [
      { key: 'name', label: 'Name', required: true },
      { key: 'country', label: 'Country' },
      { key: 'founded', label: 'Founded (year)', type: 'number' },
    ],
  },
  player: {
    label: 'Player', nameField: 'full_name', imageField: 'photo_url', imageLabel: 'Photo',
    fields: [
      { key: 'full_name', label: 'Full Name', required: true },
      { key: 'nationality', label: 'Nationality' },
      { key: 'birth_date', label: 'Date of birth (DD/MM/YYYY)' },
      { key: 'birth_year', label: 'Birth Year', type: 'number' },
      { key: 'positions', label: 'Positions (comma-separated)' },
      { key: 'preferred_number', label: 'Preferred Number', type: 'number' },
      { key: 'bio', label: 'Bio', type: 'textarea', span: 2 },
    ],
  },
};

export default function EntityEditDialog({ open, onOpenChange, entityType, mode = 'create', initialData = {}, entityId = null, onSuccess }) {
  const config = ENTITY_CONFIGS[entityType];
  const [form, setForm] = useState(() => ({ ...initialData }));
  const [submitting, setSubmitting] = useState(false);
  const [showRemoval, setShowRemoval] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

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
      toast.success(mode === 'create'
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
        data: { mode: 'removal', entity_id: entityId, entity_type: entityType, notes: removalNotes }
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

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg tracking-tight" style={labelStyle}>
            {mode === 'create' ? `SUBMIT NEW ${entityType.toUpperCase()}` : `SUGGEST EDIT — ${entityType.toUpperCase()}`}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {config.fields.map(f => (
              <div key={f.key} className={`space-y-1 ${f.key === config.nameField || f.span === 2 ? 'sm:col-span-2' : ''}`}>
                <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                  {f.label} {f.required && '*'}
                </Label>
                {f.type === 'select' ? (
                  <select
                    value={form[f.key] || ''}
                    onChange={e => handleChange(f.key, e.target.value)}
                    className="w-full h-9 px-3 bg-card border border-border rounded-none text-sm"
                    data-testid={`entity-edit-${f.key}`}
                  >
                    <option value="">Select...</option>
                    {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : f.type === 'textarea' ? (
                  <Textarea
                    value={form[f.key] ?? ''}
                    onChange={e => handleChange(f.key, e.target.value)}
                    className="bg-card border-border rounded-none min-h-[80px] text-sm"
                    placeholder="..."
                    data-testid={`entity-edit-${f.key}`}
                  />
                ) : (
                  <Input
                    type={f.type === 'number' ? 'number' : 'text'}
                    value={form[f.key] ?? ''}
                    onChange={e => handleChange(f.key, e.target.value)}
                    className="bg-card border-border rounded-none"
                    data-testid={`entity-edit-${f.key}`}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="space-y-1">
            <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
              {config.imageLabel}
            </Label>
            <ImageUpload
              value={form[config.imageField] || ''}
              onChange={v => handleChange(config.imageField, v)}
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
