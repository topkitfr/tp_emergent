// frontend/src/components/AddEntityDialog.js
// Dialog d'ajout d'une nouvelle entité de référence (player/team/brand/
// league/sponsor). Pose la fiche en base avec status='for_review' et crée
// une submission liée pour le vote communautaire.
//
// Fine coquille autour de <EntityForm /> (cf. components/entity-form/) qui
// porte tout le rendu du formulaire. Ici on gère uniquement : titre,
// validation du nom, appel API, préremplissage anti-doublon, et boutons.
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';
import {
  createPlayerPending,
  createTeamPending,
  createBrandPending,
  createLeaguePending,
  createSponsorPending,
  parseApiError,
} from '@/lib/api';
import EntityForm from '@/components/entity-form/EntityForm';
import { ENTITY_FIELD_CONFIGS, buildEntityPayload } from '@/lib/entityFields';

const fieldStyle = { fontFamily: 'Barlow Condensed' };

const TITLES = {
  player:  'Add a new Player',
  team:    'Add a new Team',
  brand:   'Add a new Brand',
  league:  'Add a new League',
  sponsor: 'Add a new Sponsor',
};

const CREATE_FNS = {
  player:  createPlayerPending,
  team:    createTeamPending,
  brand:   createBrandPending,
  league:  createLeaguePending,
  sponsor: createSponsorPending,
};

/**
 * Props :
 * - open: bool
 * - onClose: fn
 * - entityType: 'player' | 'team' | 'brand' | 'league' | 'sponsor'
 * - onSuccess: fn() — appelé après soumission réussie (refetch)
 */
export default function AddEntityDialog({ open, onClose, entityType, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({});

  const config = ENTITY_FIELD_CONFIGS[entityType];

  const handleClose = () => {
    setForm({});
    onClose();
  };

  // ── Préremplissage depuis la barre de recherche anti-doublon ─────────────
  // Les champs préfixés _ (`_career_divider`, etc.) ne sont jamais touchés ici.
  const handleDbSelect = (item) => {
    toast.warning(
      `« ${item.name || item.full_name || item.label} » existe déjà en base de données. Préremplissage effectué.`,
      { duration: 5000 }
    );
    if (entityType === 'player') {
      setForm(prev => ({
        ...prev,
        full_name:         item.full_name || item.name || '',
        first_name:        item.first_name || '',
        last_name:         item.last_name || '',
        nationality:       item.nationality || '',
        birth_date:        item.birth_date || '',
        birth_place:       item.birth_place || '',
        birth_country:     item.birth_country || '',
        photo_url:         item.photo_url || item.photo || '',
        height:            item.height ?? '',
        weight:            item.weight ?? '',
        preferred_foot:    item.preferred_foot || '',
        preferred_number:  item.preferred_number ?? '',
        individual_awards: item.individual_awards || [],
        positions:         item.positions || [],
      }));
    } else if (entityType === 'team') {
      setForm(prev => ({
        ...prev,
        name:                item.name || '',
        country:             item.country || '',
        city:                item.city || '',
        founded:             item.founded || '',
        is_national:         item.is_national ?? false,
        gender:              item.gender || '',
        crest_url:           item.crest_url || '',
        stadium_name:        item.stadium_name || '',
        stadium_capacity:    item.stadium_capacity || '',
        stadium_surface:     item.stadium_surface || '',
        stadium_city:        item.stadium_city || '',
        stadium_country:     item.stadium_country || '',
        stadium_image_url:   item.stadium_image_url || '',
      }));
    } else if (entityType === 'league') {
      setForm(prev => ({
        ...prev,
        name:              item.name || '',
        country_or_region: item.country_or_region || '',
        country_code:      item.country_code || '',
        country_flag:      item.country_flag || '',
        type:              item.type || '',
        entity_type:       item.entity_type || '',
        scope:             item.scope || '',
        gender:            item.gender || '',
        organizer:         item.organizer || '',
        logo_url:          item.logo_url || '',
      }));
    } else {
      // brand / sponsor : juste le nom suffit (le reste à compléter à la main)
      setForm(prev => ({ ...prev, name: item.name || '' }));
    }
  };

  const handleSubmit = async () => {
    const nameKey = config?.nameField || 'name';
    if (!form[nameKey]?.trim()) {
      toast.error(`${config?.label || 'Entity'} name is required`);
      return;
    }
    setLoading(true);
    try {
      const payload = buildEntityPayload(entityType, form, {}, 'create');
      await CREATE_FNS[entityType](payload);
      toast.success(`${config.label} submitted for community review`);
      handleClose();
      onSuccess?.();
    } catch (e) {
      // parseApiError normalise les erreurs Pydantic [{type,loc,msg}] en string
      // pour éviter React error #31 (objet rendu comme noeud DOM dans le toast)
      toast.error(parseApiError(e, 'Submission failed'));
    } finally {
      setLoading(false);
    }
  };

  if (!config) return null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-lg bg-background border-border rounded-none p-0 gap-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-border">
          <DialogTitle className="text-xl tracking-tighter" style={fieldStyle}>
            {TITLES[entityType] || 'Add Entity'}
          </DialogTitle>
          <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            Will be submitted for community vote before appearing in the database.
          </p>
        </DialogHeader>

        <div className="px-6 py-5 max-h-[70vh] overflow-y-auto">
          <EntityForm
            entityType={entityType}
            value={form}
            onChange={setForm}
            onDbSelect={handleDbSelect}
            mode="create"
          />
        </div>

        <div className="px-6 py-4 border-t border-border flex justify-end gap-3">
          <Button onClick={handleSubmit} disabled={loading} className="rounded-none">
            {loading && <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" />}
            Submit for Review
          </Button>
          <Button variant="outline" onClick={handleClose} className="rounded-none">Cancel</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
