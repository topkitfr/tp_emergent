// frontend/src/components/EntityDetailPage.js
// Layout unifié pour toutes les pages détail d'entités (Team, League, Brand, Player, Sponsor)
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Pencil, Shirt } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';
import { proxyImageUrl } from '@/lib/api';

/**
 * EntityDetailPage — layout unifié pour toutes les pages détail d'entités.
 *
 * Props:
 * - entityType: "team" | "league" | "brand" | "player" | "sponsor"
 * - entity: object — données de l'entité (doit avoir .name / .full_name, .status, .slug ou _id)
 * - entityId: string — ID de l'entité pour le dialog d'édition
 * - backTo: { path, label } — ex: { path: '/teams', label: 'Teams' }
 * - image: string — URL de l'image (logo/crest/photo)
 * - icon: ReactNode — icône de fallback si pas d'image
 * - imageShape: "square" | "round" — forme de l'image (round pour players)
 * - title: string — nom principal affiché
 * - subtitle: ReactNode — sous-titre (pays, niveau, etc.)
 * - metaItems: array de ReactNode — infos complémentaires
 * - badges: array de { label, variant }
 * - kits: array — les kits/maillots associés
 * - filters: array de { key, label, value, onChange, options }
 * - onEditSuccess: fn — callback après édition réussie
 * - extraActions: ReactNode — actions supplémentaires à côté du bouton Suggest Edit (ex: Follow)
 * - testId: string
 */
export default function EntityDetailPage({
  entityType,
  entity,
  entityId,
  backTo,
  image,
  icon: Icon,
  imageShape = 'square',
  title,
  subtitle,
  metaItems = [],
  badges = [],
  kits = [],
  filters = [],
  onEditSuccess,
  extraActions,
  testId,
}) {
  const { user } = useAuth();
  const [showEdit, setShowEdit] = useState(false);

  const canEdit = !!user; // tout utilisateur connecté peut suggérer une édition

  const isPending = entity?.status === 'pending' || entity?.status === 'for_review';

  // Filtrage des kits en local
  const filteredKits = kits.filter(kit => {
    return filters.every(f => {
      if (!f.value) return true;
      const kitVal = kit[f.key] || '';
      return kitVal === f.value || kitVal.toLowerCase().includes(f.value.toLowerCase());
    });
  });

  return (
    <div className="animate-fade-in-up" data-testid={testId}>
      {/* ── Header ── */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Breadcrumb */}
          {backTo && (
            <Link
              to={backTo.path}
              className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground mb-5 transition-colors"
            >
              <ArrowLeft className="w-3 h-3" />
              {backTo.label}
            </Link>
          )}

          <div className="flex flex-col sm:flex-row items-start gap-6">
            {/* Image / Logo */}
            <div className={`
              shrink-0 bg-secondary flex items-center justify-center overflow-hidden border border-border
              ${imageShape === 'round' ? 'rounded-full w-24 h-24' : 'w-24 h-24 rounded-sm'}
            `}>
              {image
                ? <img
                    src={proxyImageUrl(image)}
                    alt={title}
                    className={`object-contain p-2 ${imageShape === 'round' ? 'w-24 h-24 object-cover rounded-full p-0' : 'w-20 h-20'}`}
                  />
                : Icon && <Icon className="w-10 h-10 text-muted-foreground" />
              }
            </div>

            {/* Infos principale */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  {isPending && (
                    <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent mb-2">
                      PENDING APPROVAL
                    </Badge>
                  )}
                  <h1 className="text-3xl sm:text-4xl tracking-tighter break-words" data-testid={`${testId}-title`}>
                    {title}
                  </h1>
                  {subtitle && (
                    <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-muted-foreground"
                      style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                      {subtitle}
                    </div>
                  )}
                </div>

                {/* Bouton Suggest Edit + actions extra (Follow, etc.) */}
                <div className="flex items-center gap-2 shrink-0">
                {extraActions}
                {canEdit && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowEdit(true)}
                    className="rounded-none border-border hover:border-primary/50 shrink-0"
                    data-testid={`${testId}-suggest-edit-btn`}
                  >
                    <Pencil className="w-3 h-3 mr-1.5" />
                    Suggest Edit
                  </Button>
                )}
                </div>
              </div>

              {/* Meta items (fondation, niveau, etc.) */}
              {metaItems.length > 0 && (
                <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-muted-foreground"
                  style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  {metaItems}
                </div>
              )}

              {/* Badges */}
              {badges.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {badges.map((b, i) => (
                    <Badge key={i} variant={b.variant || 'secondary'} className="rounded-none">
                      {b.label}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Kits Grid ── */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {/* Filtres kits */}
        {filters.length > 0 && kits.length > 0 && (
          <div className="flex flex-wrap gap-3 mb-6">
            {filters.map(f => (
              <select
                key={f.key}
                value={f.value}
                onChange={e => f.onChange(e.target.value)}
                className="h-9 px-3 bg-card border border-border rounded-none text-sm text-foreground"
                data-testid={`${testId}-filter-${f.key}`}
              >
                <option value="">{f.label}</option>
                {f.options.map(opt => {
                  const val = typeof opt === 'string' ? opt : opt.value;
                  const lbl = typeof opt === 'string' ? opt : opt.label;
                  return <option key={val} value={val}>{lbl}</option>;
                })}
              </select>
            ))}
          </div>
        )}

        {/* Compteur kits */}
        <p className="text-sm text-muted-foreground mb-6" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          <span className="font-mono text-foreground">{filteredKits.length}</span> kits
          {filteredKits.length !== kits.length && ` (${kits.length} total)`}
        </p>

        {kits.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-border">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              No kits found for this {entityType}
            </p>
          </div>
        ) : filteredKits.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              No kits match the selected filters
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {filteredKits.map(kit => (
              <JerseyCard key={kit.kit_id} kit={kit} />
            ))}
          </div>
        )}
      </div>

      {/* Dialog Suggest Edit */}
      {showEdit && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType={entityType}
          mode="edit"
          initialData={entity}
          entityId={entityId}
          onSuccess={onEditSuccess}
        />
      )}
    </div>
  );
}

/**
 * EntityDetailSkeleton — skeleton loading unifié
 */
export function EntityDetailSkeleton() {
  return (
    <div className="animate-fade-in-up px-4 lg:px-8 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-start gap-6 mb-8">
          <div className="w-24 h-24 bg-card animate-pulse border border-border" />
          <div className="flex-1 space-y-3">
            <div className="h-10 bg-card animate-pulse w-64" />
            <div className="h-4 bg-card animate-pulse w-40" />
            <div className="h-4 bg-card animate-pulse w-32" />
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />
          ))}
        </div>
      </div>
    </div>
  );
}
