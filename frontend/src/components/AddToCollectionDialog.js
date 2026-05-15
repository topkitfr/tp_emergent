// src/components/AddToCollectionDialog.js
import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { proxyImageUrl, addToCollection, createPlayerPending, estimatePrice } from '@/lib/api';
import { Check, Loader2 } from 'lucide-react';
import { calculateEstimation } from '@/utils/estimation';
import CollectionItemForm, {
  INITIAL_FORM_STATE,
  formToPayload,
} from '@/components/CollectionItemForm';

function parseSeasonYear(season) {
  if (!season) return 0;
  const match = season.match(/(\d{4})/);
  return match ? parseInt(match[1]) : 0;
}

/** Normalise un detail FastAPI/Pydantic en string lisible */
function normalizeDetail(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(d => d?.msg || d?.message || JSON.stringify(d)).join(' · ');
  }
  if (typeof detail === 'object') return detail.msg || detail.message || JSON.stringify(detail);
  return String(detail);
}

export default function AddToCollectionDialog({ version, onClose, onSuccess }) {
  const kit   = version?.master_kit || {};
  const photo = version?.front_photo || kit?.front_photo;

  // Estimation mode — persisté via window pour survie entre ouvertures
  const [mode, setMode] = useState(() =>
    typeof window !== 'undefined' ? (window.__tkEstimationMode || 'basic') : 'basic'
  );
  const switchMode = (next) => {
    if (typeof window !== 'undefined') window.__tkEstimationMode = next;
    setMode(next);
  };

  const [form, setForm] = useState(INITIAL_FORM_STATE);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const handleChange = (field, value) => setForm(f => ({ ...f, [field]: value }));

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

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    try {
      // Résoudre le joueur flocqué si pas encore en DB
      let resolvedFlockingPlayerId = form.flocking_player_id;
      if (form.flocking_origin === 'Official' && form.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: form.flocking_detail });
          resolvedFlockingPlayerId = r.data?.player_id;
        } catch {}
      }

      // Résoudre le joueur signataire si type = 'other'
      let resolvedSignedByPlayerId = form.signed_player_id || '';
      if (form.signed && form.signed_other_text && !resolvedSignedByPlayerId && form.signed_type === 'other') {
        try {
          const r = await createPlayerPending({ full_name: form.signed_other_text });
          resolvedSignedByPlayerId = r.data?.player_id;
        } catch {}
      }

      const estRes = await estimatePrice({
        model_type:         version?.model || 'Replica',
        competition:        version?.competition || '',
        condition_origin:   form.condition_origin || '',
        physical_state:     form.physical_state || '',
        flocking_origin:    form.flocking_origin === 'none' ? 'None' : (form.flocking_origin || ''),
        flocking_player_id: resolvedFlockingPlayerId || '',
        signed:             form.signed || false,
        signed_type:        form.signed_type || '',
        signed_other_detail: form.signed_other_text || '',
        signed_proof:       form.signed_proof_level || 'none',
        season_year:        seasonYear,
        patch:              (form.patches?.length > 0) || !!form.patch_other_text,
        is_rare:            form.is_rare || false,
        rare_reason:        form.rare_reason || '',
        mode,
      }).catch(() => ({ data: estimation }));
      const finalEstimation = estRes.data || estimation;

      const payload = formToPayload(
        { ...form, flocking_player_id: resolvedFlockingPlayerId, signed_player_id: resolvedSignedByPlayerId },
        finalEstimation,
      );

      await addToCollection({ version_id: version.version_id, ...payload });
      onSuccess?.();
    } catch (err) {
      if (err?.response?.status === 400) {
        setError('This version is already in your collection.');
      } else {
        const detail = normalizeDetail(err?.response?.data?.detail);
        setError(detail || 'An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

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

        {/* Aperçu version */}
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

        {/* Formulaire unifié */}
        <CollectionItemForm
          form={form}
          onChange={handleChange}
          mode={mode}
          onModeChange={switchMode}
          version={version}
          seasonYear={seasonYear}
          showEstimation
        />

        {error && <p className="text-sm text-destructive mt-3">{error}</p>}

        {/* Actions */}
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
