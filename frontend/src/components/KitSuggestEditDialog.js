// frontend/src/components/KitSuggestEditDialog.js
// Dialog "Suggest Edit" unifié pour Master Kit et Version Kit.
// Identique en logique à EntityEditDialog :
//   - pré-rempli avec les données existantes
//   - soumet via createSubmission (pas createReport)
//   - Request Removal intégré en bas
//
// Props:
//   open         : bool
//   onOpenChange : fn(bool)
//   type         : 'master_kit' | 'version'
//   initialData  : object  — données actuelles du kit/version
//   entityId     : string  — kit_id ou version_id
//   kitId        : string  — (version only) kit_id du master kit parent
//   onSuccess    : fn()    — callback après succès

import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { createSubmission } from '@/lib/api';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';
import { toast } from 'sonner';
import { Pencil, Trash2 } from 'lucide-react';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };

const KIT_TYPES    = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const GENDERS      = ['Man', 'Woman', 'Kid'];
const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];
const MODELS       = ['Authentic', 'Replica', 'Other'];

// ─── Config des champs par type ───────────────────────────────────────────────
const CONFIGS = {
  master_kit: {
    title: 'SUGGEST EDIT — MASTER KIT',
    fields: [
      // Autocomplete entités
      { key: 'club',        label: 'Team',    type: 'entity_autocomplete', entityType: 'team' },
      { key: 'brand',       label: 'Brand',   type: 'entity_autocomplete', entityType: 'brand' },
      { key: 'league',      label: 'League',  type: 'entity_autocomplete', entityType: 'league' },
      { key: 'sponsor',     label: 'Sponsor', type: 'entity_autocomplete', entityType: 'sponsor' },
      // Champs simples
      { key: 'season',      label: 'Season',   type: 'text' },
      { key: 'design',      label: 'Design',   type: 'text' },
      { key: 'kit_type',    label: 'Type',     type: 'select', options: KIT_TYPES },
      { key: 'gender',      label: 'Gender',   type: 'select', options: GENDERS },
    ],
    imageField: 'front_photo',
    imageLabel: 'Front Photo',
    imageFolder: 'master_kit',
  },
  version: {
    title: 'SUGGEST EDIT — VERSION',
    fields: [
      { key: 'competition', label: 'Competition', type: 'select', options: COMPETITIONS },
      { key: 'model',       label: 'Model',       type: 'select', options: MODELS },
      { key: 'sku_code',    label: 'SKU Code',    type: 'text' },
      { key: 'ean_code',    label: 'EAN Code',    type: 'text' },
    ],
    // Version a deux photos
    imageFields: [
      { key: 'front_photo', label: 'Front Photo', folder: 'version', side: 'front' },
      { key: 'back_photo',  label: 'Back Photo',  folder: 'version', side: 'back' },
    ],
  },
};

export default function KitSuggestEditDialog({
  open,
  onOpenChange,
  type = 'master_kit',
  initialData = {},
  entityId,
  kitId,        // ← kit_id du master kit parent (requis quand type === 'version')
  onSuccess,
}) {
  const config = CONFIGS[type];
  const [form, setForm]               = useState(() => ({ ...initialData }));
  const [submitting, setSubmitting]   = useState(false);
  const [showRemoval, setShowRemoval] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');

  const set = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  // ─── Submit Suggest Edit ─────────────────────────────────────────────────────
  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        mode: 'edit',
        entity_id: entityId,
        entity_type: type,
      };
      // Pour master_kit, on s'assure que kit_id est explicite
      if (type === 'master_kit') payload.kit_id = entityId;
      // Pour version, on s'assure que version_id et kit_id sont explicites
      if (type === 'version') {
        payload.version_id = entityId;
        if (kitId) payload.kit_id = kitId;
      }

      await createSubmission({ submission_type: type, data: payload });
      toast.success('Edit suggestion submitted for community review');
      onOpenChange(false);
      onSuccess?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  // ─── Submit Removal ──────────────────────────────────────────────────────────
  const handleRemoval = async () => {
    if (!removalNotes.trim()) { toast.error('Please provide a reason for removal'); return; }
    setSubmitting(true);
    try {
      const removalData = {
        mode: 'removal',
        entity_id: entityId,
        entity_type: type,
        notes: removalNotes,
      };
      // Passe kit_id / version_id explicitement pour que le backend
      // puisse identifier la cible sans ambiguïté
      if (type === 'master_kit') {
        removalData.kit_id = entityId;
      }
      if (type === 'version') {
        removalData.version_id = entityId;
        // FIX: inclure kit_id pour que Contributions.js puisse résoudre
        // le nom du master kit parent dans getSubmissionTitle
        if (kitId) removalData.kit_id = kitId;
      }

      await createSubmission({ submission_type: type, data: removalData });
      toast.success('Removal request submitted for community review');
      setShowRemoval(false);
      setRemovalNotes('');
      onOpenChange(false);
      onSuccess?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  // ─── Render d'un champ ───────────────────────────────────────────────────────
  const renderField = (f) => {
    if (f.type === 'entity_autocomplete') {
      return (
        <EntityAutocomplete
          entityType={f.entityType}
          value={form[f.key] || ''}
          onChange={v => set(f.key, v)}
          onSelect={item => set(f.key, item.label)}
          className="bg-card border-border rounded-none"
        />
      );
    }
    if (f.type === 'select') {
      return (
        <Select value={form[f.key] || ''} onValueChange={v => set(f.key, v)}>
          <SelectTrigger className="bg-card border-border rounded-none h-9">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {f.options.map(o => (
              <SelectItem key={o} value={o}>{o}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    }
    return (
      <Input
        value={form[f.key] ?? ''}
        onChange={e => set(f.key, e.target.value)}
        className="bg-card border-border rounded-none"
      />
    );
  };

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg tracking-tight flex items-center gap-2" style={labelStyle}>
            <Pencil className="w-4 h-4" />
            {config.title}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 pt-2">

          {/* Champs */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {config.fields.map(f => (
              <div key={f.key} className="space-y-1">
                <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                  {f.label}
                </Label>
                {renderField(f)}
              </div>
            ))}
          </div>

          {/* Photo(s) */}
          {config.imageField && (
            <div className="space-y-1">
              <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                {config.imageLabel}
              </Label>
              <ImageUpload
                value={form[config.imageField] || ''}
                onChange={v => set(config.imageField, v)}
                folder={config.imageFolder}
              />
            </div>
          )}

          {config.imageFields && (
            <div className="grid grid-cols-2 gap-4">
              {config.imageFields.map(img => (
                <div key={img.key} className="space-y-1">
                  <Label className="text-xs uppercase tracking-wider" style={labelStyle}>
                    {img.label}
                  </Label>
                  <ImageUpload
                    value={form[img.key] || ''}
                    onChange={v => set(img.key, v)}
                    folder={img.folder}
                    side={img.side}
                  />
                </div>
              ))}
            </div>
          )}

          {/* Notes */}
          <div className="space-y-1">
            <Label className="text-xs uppercase tracking-wider" style={labelStyle}>Notes (optionnel)</Label>
            <Textarea
              value={form._notes ?? ''}
              onChange={e => set('_notes', e.target.value)}
              placeholder="Précisez la correction si nécessaire..."
              className="bg-card border-border rounded-none min-h-[60px] text-sm"
              rows={2}
            />
          </div>

          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            Votre suggestion sera soumise à la communauté pour validation.
          </p>

          <Button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {submitting ? 'Submitting...' : 'Submit Edit'}
          </Button>

          {/* Request Removal */}
          {entityId && (
            <div className="border-t border-border pt-4">
              {!showRemoval ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRemoval(true)}
                  className="rounded-none border-destructive/50 text-destructive hover:bg-destructive/10 w-full"
                >
                  <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Request Removal
                </Button>
              ) : (
                <div className="space-y-3">
                  <p className="text-[10px] uppercase tracking-wider text-destructive" style={labelStyle}>REQUEST REMOVAL</p>
                  <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    La communauté votera sur cette demande de suppression.
                  </p>
                  <Textarea
                    value={removalNotes}
                    onChange={e => setRemovalNotes(e.target.value)}
                    placeholder="Expliquez pourquoi cette entrée doit être supprimée..."
                    className="bg-card border-border rounded-none min-h-[80px] text-sm"
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={handleRemoval}
                      disabled={submitting || !removalNotes.trim()}
                      className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90"
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
