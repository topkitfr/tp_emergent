// frontend/src/components/EntityEditDialog.js
// Dialog d'édition (mode='edit') ou de demande de suppression
// (mode='removal') d'une entité de référence existante. Crée une
// submission dans db.submissions ; l'entité d'origine reste affichée
// inchangée jusqu'à l'approbation communautaire.
//
// Fine coquille autour de <EntityForm /> qui porte tout le rendu du
// formulaire. Ici on gère uniquement : titre, validation du nom, appel
// API, bloc "Request Removal".
//
// Note : ce dialog n'est invoqué que depuis les pages détail (Edit/
// Request Removal). Le `mode='create'` reste possible côté API mais
// n'est appelé nulle part — voir AddEntityDialog pour la création.
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Trash2 } from 'lucide-react';
import { createSubmission, parseApiError } from '@/lib/api';
import EntityForm from '@/components/entity-form/EntityForm';
import { ENTITY_FIELD_CONFIGS, buildEntityPayload } from '@/lib/entityFields';

const labelStyle = { fontFamily: 'Barlow Condensed, sans-serif' };

export default function EntityEditDialog({
  open,
  onOpenChange,
  entityType,
  mode = 'edit',
  initialData = {},
  entityId = null,
  onSuccess,
}) {
  const config = ENTITY_FIELD_CONFIGS[entityType];
  const [form, setForm] = useState(() => ({ ...initialData }));
  const [submitting, setSubmitting] = useState(false);
  const [showRemoval, setShowRemoval] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');

  // Reset à chaque ouverture du dialog
  useEffect(() => {
    if (open) {
      setForm({ ...initialData });
      setShowRemoval(false);
      setRemovalNotes('');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // Préremplissage depuis la barre de recherche anti-doublon (utile pour
  // repérer une collision de renommage en édition).
  const handleDbSelect = (item) => {
    toast.warning(
      `« ${item.name || item.full_name || item.label} » existe déjà en base. Vérifie la collision avant de soumettre.`,
      { duration: 5000 }
    );
  };

  const handleSubmit = async () => {
    if (!config) return;
    const nameKey = config.nameField;
    if (!form[nameKey]?.trim()) {
      toast.error(`${config.label} name is required`);
      return;
    }
    setSubmitting(true);
    try {
      const payload = buildEntityPayload(entityType, form, initialData, mode);
      payload.mode = mode;
      if (mode === 'edit' && entityId) {
        payload.entity_id   = entityId;
        payload.entity_type = entityType;
      }
      await createSubmission({ submission_type: entityType, data: payload });
      toast.success(
        mode === 'create'
          ? `${config.label} submitted for review`
          : 'Edit suggestion submitted for review'
      );
      onOpenChange(false);
      if (onSuccess) onSuccess(form[nameKey]);
    } catch (err) {
      toast.error(parseApiError(err, 'Submission failed'));
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
      toast.error(parseApiError(err, 'Submission failed'));
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
            {mode === 'create'
              ? `SUBMIT NEW ${entityType.toUpperCase()}`
              : `SUGGEST EDIT — ${entityType.toUpperCase()}`}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 pt-2">
          <EntityForm
            entityType={entityType}
            value={form}
            onChange={setForm}
            onDbSelect={handleDbSelect}
            mode={mode}
          />

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
                  <Label className="text-[10px] uppercase tracking-wider text-destructive" style={labelStyle}>
                    REQUEST REMOVAL
                  </Label>
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
