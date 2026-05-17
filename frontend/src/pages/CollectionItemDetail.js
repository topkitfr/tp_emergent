import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, useSearchParams, Link } from "react-router-dom";
import {
  getCollectionItem,
  removeFromCollection,
  updateCollectionItem,
  createListing,
  cancelListing,
  proxyImageUrl,
  createPlayerPending,
  estimatePrice,
  uploadImage,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import {
  ArrowLeft, Edit2, Trash2, Tag, ExternalLink,
  ShoppingBag, Loader2, Check, Shield, Star, Package, Plus, Shirt,
} from "lucide-react";
import CollectionItemForm, {
  PHYSICAL_STATES,
  CONDITION_ORIGINS,
  SIGNED_TYPES,
  PROOF_LEVELS,
  INITIAL_FORM_STATE,
  formFromItem,
  formToPayload,
} from "@/components/CollectionItemForm";
import { calculateEstimation } from "@/utils/estimation";

function parseSeasonYear(season) {
  if (!season) return 0;
  const m = season.match(/(\d{4})/);
  return m ? parseInt(m[1]) : 0;
}

function InfoRow({ label, value }) {
  if (!value && value !== 0) return null;
  return (
    <div className="flex items-start gap-3 py-2 border-b border-border/50 last:border-0">
      <span className="text-xs text-muted-foreground uppercase tracking-wide w-32 shrink-0 pt-0.5"
        style={{ fontFamily: "Barlow Condensed" }}>{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  );
}

function Section({ title, icon: Icon, children }) {
  return (
    <div className="border border-border bg-card p-4 space-y-1">
      <div className="flex items-center gap-2 mb-3">
        {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
        <h2 className="text-xs font-semibold uppercase tracking-widest text-muted-foreground"
          style={{ fontFamily: "Barlow Condensed" }}>{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default function CollectionItemDetail() {
  const { collection_id } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);

  // edit sheet
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState(INITIAL_FORM_STATE);
  const [editMode, setEditMode] = useState("basic");
  const [saving, setSaving] = useState(false);

  // listing dialog
  const [listingOpen, setListingOpen] = useState(false);
  const [listingForm, setListingForm] = useState({ listing_type: "sale", asking_price: "", trade_for: "", use_topkit_price: false });
  const [listingLoading, setListingLoading] = useState(false);
  const [listingPhotos, setListingPhotos] = useState({ front: null, back: null });
  const [photoUploading, setPhotoUploading] = useState({ front: false, back: false });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getCollectionItem(collection_id);
      setItem(res.data);
    } catch {
      toast.error("Item introuvable");
      navigate("/collection");
    } finally {
      setLoading(false);
    }
  }, [collection_id, navigate]);

  useEffect(() => { load(); }, [load]);

  // Auto-ouvre le sheet d'édition si ?estimate=1 (redirigé depuis MyCollection)
  useEffect(() => {
    if (item && searchParams.get("estimate") === "1" && !editOpen) {
      setEditForm(formFromItem(item));
      setEditMode("advanced");
      setEditOpen(true);
      toast("Estimez votre maillot pour le mettre en vente", { description: "Remplissez les champs état et flocage puis sauvegardez." });
    }
  }, [item, searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  const openEdit = () => {
    if (!item) return;
    setEditForm(formFromItem(item));
    setEditOpen(true);
  };

  const saveEdit = async () => {
    setSaving(true);
    try {
      const seasonYear = parseSeasonYear(item.master_kit?.season);

      // Resolve pending flocking player
      let resolvedFlockingPlayerId = editForm.flocking_player_id;
      if (editForm.flocking_origin === "Official" && editForm.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: editForm.flocking_detail });
          resolvedFlockingPlayerId = r.data?.player_id;
        } catch {}
      }

      // Resolve pending signed player (other type)
      let resolvedSignedPlayerId = editForm.signed_player_id;
      if (editForm.signed && editForm.signed_type === "other" && editForm.signed_other_text && !resolvedSignedPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: editForm.signed_other_text });
          resolvedSignedPlayerId = r.data?.player_id;
        } catch {}
      }

      const localEst = calculateEstimation({
        mode:             editMode,
        modelType:        item.version?.model       || "Replica",
        competition:      item.version?.competition || "",
        conditionOrigin:  editForm.condition_origin,
        physicalState:    editForm.physical_state,
        flockingOrigin:   editForm.flocking_origin === "none" ? "None" : editForm.flocking_origin,
        patches:          editForm.patches,
        patchOtherText:   editForm.patch_other_text,
        signed:           editForm.signed,
        signedType:       editForm.signed_type,
        signedOtherText:  editForm.signed_other_text,
        playerProfile:    editForm.player_profile,
        signedProofLevel: editForm.signed_proof_level,
        isRare:           editForm.is_rare,
        rareReason:       editForm.rare_reason,
        seasonYear,
      });

      const estRes = await estimatePrice({
        model_type:          item.version?.model || "Replica",
        competition:         item.version?.competition || "",
        condition_origin:    editForm.condition_origin || "",
        physical_state:      editForm.physical_state || "",
        flocking_origin:     editForm.flocking_origin === "none" ? "None" : (editForm.flocking_origin || ""),
        flocking_player_id:  resolvedFlockingPlayerId || "",
        signed:              editForm.signed || false,
        signed_type:         editForm.signed_type || "",
        signed_other_detail: editForm.signed_other_text || "",
        signed_proof:        editForm.signed_proof_level || "none",
        season_year:         seasonYear,
        patch:               (editForm.patches?.length > 0) || !!editForm.patch_other_text,
        is_rare:             editForm.is_rare || false,
        rare_reason:         editForm.rare_reason || "",
        mode:                editMode,
      }).catch(() => ({ data: localEst }));

      const estimation = estRes.data || localEst;

      const payload = formToPayload(
        { ...editForm, flocking_player_id: resolvedFlockingPlayerId, signed_player_id: resolvedSignedPlayerId },
        estimation,
      );

      await updateCollectionItem(collection_id, payload);
      toast.success("Modifications enregistrées");
      setEditOpen(false);
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la sauvegarde");
    } finally {
      setSaving(false);
    }
  };

  const handleRemove = async () => {
    if (!window.confirm("Retirer ce maillot de votre collection ?")) return;
    try {
      await removeFromCollection(collection_id);
      toast.success("Retiré de la collection");
      navigate("/collection");
    } catch {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleUploadListingPhoto = async (side, file) => {
    if (!file) return;
    setPhotoUploading(p => ({ ...p, [side]: true }));
    try {
      const entityId = `${collection_id}_${user?.user_id}`;
      const res = await uploadImage(file, "listing", entityId, side);
      const url = res.data?.url || res.data?.image_url || res.data?.path;
      setListingPhotos(p => ({ ...p, [side]: url }));
    } catch {
      toast.error(`Erreur lors du chargement de la photo ${side === "front" ? "avant" : "arrière"}`);
    } finally {
      setPhotoUploading(p => ({ ...p, [side]: false }));
    }
  };

  const resetListingDialog = () => {
    setListingOpen(false);
    setListingForm({ listing_type: "sale", asking_price: "", trade_for: "", use_topkit_price: false });
    setListingPhotos({ front: null, back: null });
    setPhotoUploading({ front: false, back: false });
  };

  const handleCreateListing = async () => {
    if (!listingPhotos.front || !listingPhotos.back) {
      toast.error("Ajoutez une photo avant et une photo arrière avant de publier");
      return;
    }
    setListingLoading(true);
    try {
      const payload = {
        collection_id,
        listing_type: listingForm.listing_type,
        listing_photos: [listingPhotos.front, listingPhotos.back],
      };
      if ((listingForm.listing_type === "sale" || listingForm.listing_type === "both") && listingForm.asking_price) {
        payload.asking_price = parseFloat(listingForm.asking_price);
      }
      if ((listingForm.listing_type === "trade" || listingForm.listing_type === "both") && listingForm.trade_for) {
        payload.trade_for = listingForm.trade_for;
      }
      await createListing(payload);
      toast.success("Annonce publiée !");
      resetListingDialog();
      load();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Erreur lors de la publication");
    } finally {
      setListingLoading(false);
    }
  };

  const handleCancelListing = async () => {
    if (!item?.active_listing_id) return;
    if (!window.confirm("Annuler cette annonce ?")) return;
    try {
      await cancelListing(item.active_listing_id);
      toast.success("Annonce annulée");
      load();
    } catch {
      toast.error("Erreur");
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 flex justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!item) return null;

  const kit = item.master_kit || {};
  const version = item.version || {};
  const photo = proxyImageUrl(version.front_photo || kit.front_photo);

  const conditionLabel = PHYSICAL_STATES.includes(item.physical_state) ? item.physical_state : item.condition || null;
  const originLabel = CONDITION_ORIGINS.includes(item.condition_origin) ? item.condition_origin : null;
  const signedTypeLabel = SIGNED_TYPES.find(s => s.value === item.signed_type)?.label || item.signed_type || null;
  const proofLabel = PROOF_LEVELS.find(p => p.value === item.signed_proof_level)?.label || null;
  const flockingLabel = item.flocking_detail || item.printing || null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fade-in-up">

      {/* Back */}
      <Link to="/collection" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" /> Ma collection
      </Link>

      <div className="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-6">

        {/* ── Colonne image ── */}
        <div className="space-y-4">
          <div className="aspect-[3/4] border border-border overflow-hidden bg-secondary">
            <img src={photo} alt={kit.club} className="w-full h-full object-cover" />
          </div>

          {/* Badges état */}
          <div className="flex flex-wrap gap-2">
            {conditionLabel && <Badge variant="secondary" className="rounded-none text-xs">{conditionLabel}</Badge>}
            {item.signed && <Badge className="rounded-none text-xs bg-accent/90">Signed</Badge>}
            {item.is_rare && <Badge className="rounded-none text-xs bg-yellow-500/20 text-yellow-700 border border-yellow-500/40">Rare</Badge>}
            {item.active_listing_id && (
              <span className="text-xs bg-green-600 text-white px-2 py-0.5 font-semibold">EN VENTE</span>
            )}
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <Button onClick={openEdit} variant="outline" className="w-full rounded-none justify-start gap-2">
              <Edit2 className="w-4 h-4" /> Modifier
            </Button>
            {item.active_listing_id ? (
              <>
                <Link to={`/marketplace/${item.active_listing_id}`}>
                  <Button variant="outline" className="w-full rounded-none justify-start gap-2">
                    <ShoppingBag className="w-4 h-4" /> Voir l'annonce
                  </Button>
                </Link>
                <Button onClick={handleCancelListing} variant="ghost" className="w-full rounded-none justify-start gap-2 text-muted-foreground hover:text-destructive">
                  <Tag className="w-4 h-4" /> Annuler l'annonce
                </Button>
              </>
            ) : (
              <Button onClick={() => setListingOpen(true)} variant="outline" className="w-full rounded-none justify-start gap-2">
                <Tag className="w-4 h-4" /> Mettre en vente
              </Button>
            )}
            <Button onClick={handleRemove} variant="ghost" className="w-full rounded-none justify-start gap-2 text-muted-foreground hover:text-destructive">
              <Trash2 className="w-4 h-4" /> Retirer de la collection
            </Button>
          </div>
        </div>

        {/* ── Colonne infos ── */}
        <div className="space-y-4">

          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold tracking-tighter uppercase" style={{ fontFamily: "Barlow Condensed" }}>
              {kit.club}
            </h1>
            <p className="text-muted-foreground text-sm mt-1" style={{ fontFamily: "DM Sans" }}>
              {kit.season} — {kit.kit_type} — {version.competition}
            </p>
            <div className="flex gap-2 mt-2 flex-wrap">
              {kit.brand && <Badge variant="outline" className="rounded-none text-xs">{kit.brand}</Badge>}
              {version.model && <Badge variant="outline" className="rounded-none text-xs">{version.model}</Badge>}
              {item.size && <Badge variant="outline" className="rounded-none font-mono text-xs">{item.size}</Badge>}
            </div>
            <Link to={`/version/${item.version_id}`} className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mt-2 transition-colors">
              Voir la fiche du kit <ExternalLink className="w-3 h-3" />
            </Link>
          </div>

          {/* État */}
          <Section title="État" icon={Package}>
            <InfoRow label="État physique" value={conditionLabel} />
            <InfoRow label="Origine" value={originLabel} />
            {item.patches?.length > 0 && <InfoRow label="Patches" value={item.patches.join(", ")} />}
            {item.is_rare && <InfoRow label="Rareté" value={item.rare_reason || "Oui"} />}
          </Section>

          {/* Flocage */}
          {(flockingLabel || item.flocking_origin) && (
            <Section title="Flocage" icon={Star}>
              <InfoRow label="Type" value={item.flocking_origin} />
              <InfoRow label="Détail" value={flockingLabel} />
              {item.flocking_player_id && (
                <div className="flex items-center gap-3 py-2">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide w-32 shrink-0"
                    style={{ fontFamily: "Barlow Condensed" }}>Joueur</span>
                  <Link to={`/players/${item.flocking_player_id}`} className="text-sm hover:text-primary transition-colors flex items-center gap-1">
                    {flockingLabel} <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </Section>
          )}

          {/* Signature */}
          {item.signed && (
            <Section title="Signature" icon={Shield}>
              <InfoRow label="Type" value={signedTypeLabel} />
              <InfoRow label="Signataire" value={item.signed_by || item.signed_other_detail} />
              <InfoRow label="Preuve" value={proofLabel} />
              {item.signed_by_player_id && (
                <div className="flex items-center gap-3 py-2">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide w-32 shrink-0"
                    style={{ fontFamily: "Barlow Condensed" }}>Joueur</span>
                  <Link to={`/players/${item.signed_by_player_id}`} className="text-sm hover:text-primary transition-colors flex items-center gap-1">
                    {item.signed_by} <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </Section>
          )}

          {/* Valorisation */}
          <Section title="Valorisation">
            <InfoRow label="Prix d'achat" value={item.purchase_cost != null ? `${item.purchase_cost} €` : null} />
            <InfoRow label="Estimation" value={item.estimated_price ? `${item.estimated_price} €` : null} />
          </Section>

          {/* Notes */}
          {item.notes && (
            <Section title="Notes">
              <p className="text-sm text-muted-foreground whitespace-pre-wrap" style={{ fontFamily: "DM Sans", textTransform: "none" }}>{item.notes}</p>
            </Section>
          )}
        </div>
      </div>

      {/* ══ Edit Sheet ══ */}
      <Sheet open={editOpen} onOpenChange={open => { if (!open) setEditOpen(false); }}>
        <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto">
          <SheetHeader className="mb-4">
            <SheetTitle className="text-left tracking-tighter uppercase" style={{ fontFamily: "Barlow Condensed" }}>
              Modifier l'item
            </SheetTitle>
          </SheetHeader>

          <div className="flex gap-4 mb-4">
            <img src={photo} alt={kit.club} className="w-20 h-28 object-cover border border-border shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold tracking-tight uppercase" style={{ fontFamily: "Barlow Condensed" }}>{kit.club}</h3>
              <p className="text-sm text-muted-foreground">{kit.season} — {kit.kit_type}</p>
              <div className="flex gap-2 mt-2">
                <Badge variant="outline" className="rounded-none text-[10px]">{version.model || "—"}</Badge>
                <Badge variant="outline" className="rounded-none text-[10px]">{version.competition || "—"}</Badge>
              </div>
            </div>
          </div>

          <CollectionItemForm
            form={editForm}
            onChange={(field, value) => setEditForm(f => ({ ...f, [field]: value }))}
            mode={editMode}
            onModeChange={setEditMode}
            version={version}
            seasonYear={parseSeasonYear(kit.season)}
            showEstimation
          />

          <div className="flex gap-2 mt-6">
            <Button onClick={saveEdit} disabled={saving} className="rounded-none flex-1">
              {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-1" />}
              {saving ? "Saving…" : "Save"}
            </Button>
            <Button variant="outline" onClick={() => setEditOpen(false)} disabled={saving} className="rounded-none">
              Cancel
            </Button>
          </div>
        </SheetContent>
      </Sheet>

      {/* ══ Listing Dialog ══ */}
      <Dialog open={listingOpen} onOpenChange={open => { if (!open) resetListingDialog(); }}>
        <DialogContent className="max-w-md flex flex-col max-h-[92vh] gap-0 p-0">
          <DialogHeader className="px-6 pt-6 pb-4 shrink-0">
            <DialogTitle>Mettre en vente / échange</DialogTitle>
          </DialogHeader>

          <div className="overflow-y-auto flex-1 px-6 pb-4 space-y-4">
            {(() => {
              const topkitPrice = item.estimated_price || null;
              const customPrice = parseFloat(listingForm.asking_price) || 0;
              const priceDiff = topkitPrice && customPrice > 0
                ? Math.round(((customPrice - topkitPrice) / topkitPrice) * 100)
                : null;
              const showPrice = listingForm.listing_type === "sale" || listingForm.listing_type === "both";
              return (
                <>
                  <p className="text-sm text-muted-foreground">{kit.club} — {kit.season}</p>
                  <div className="space-y-1">
                    <Label>Type d'annonce</Label>
                    <Select value={listingForm.listing_type} onValueChange={v => setListingForm(f => ({ ...f, listing_type: v }))}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sale">Vente</SelectItem>
                        <SelectItem value="trade">Échange</SelectItem>
                        <SelectItem value="both">Vente ou échange</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {showPrice && (
                    <div className="space-y-2">
                      <Label>Prix de vente</Label>
                      <div className="grid grid-cols-2 gap-2">
                        {topkitPrice ? (
                          <button
                            onClick={() => setListingForm(f => ({ ...f, use_topkit_price: true, asking_price: String(topkitPrice) }))}
                            className={`border p-3 text-left transition-colors ${listingForm.use_topkit_price ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"}`}
                          >
                            <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1" style={{ fontFamily: "Barlow Condensed" }}>Prix Topkit</div>
                            <div className="font-mono text-lg font-bold">{topkitPrice} €</div>
                            <div className="text-[10px] text-muted-foreground mt-0.5">Estimation automatique</div>
                          </button>
                        ) : (
                          <button
                            onClick={() => { resetListingDialog(); setEditForm(formFromItem(item)); setEditMode("advanced"); setEditOpen(true); }}
                            className="border border-dashed border-border p-3 text-left flex flex-col hover:border-primary/40 transition-colors"
                          >
                            <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1" style={{ fontFamily: "Barlow Condensed" }}>Prix Topkit</div>
                            <div className="text-xs text-primary font-medium mt-1">Estimez votre maillot →</div>
                            <div className="text-[10px] text-muted-foreground mt-0.5">Pour débloquer l'estimation</div>
                          </button>
                        )}
                        <button
                          onClick={() => setListingForm(f => ({ ...f, use_topkit_price: false, asking_price: "" }))}
                          className={`border p-3 text-left transition-colors ${!listingForm.use_topkit_price || !topkitPrice ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"}`}
                        >
                          <div className="text-[10px] text-muted-foreground uppercase font-semibold mb-1" style={{ fontFamily: "Barlow Condensed" }}>Prix personnalisé</div>
                          <div className="text-[11px] text-muted-foreground mt-1">Définir mon prix</div>
                        </button>
                      </div>
                      {(!listingForm.use_topkit_price || !topkitPrice) && (
                        <div className="space-y-1">
                          <Input
                            type="number" min={0} step={1} placeholder={topkitPrice ? `Ex: ${topkitPrice}` : "Ex: 80"}
                            value={listingForm.asking_price}
                            onChange={e => setListingForm(f => ({ ...f, asking_price: e.target.value }))}
                            className="font-mono"
                          />
                          {priceDiff !== null && (
                            <p className={`text-xs font-medium ${priceDiff < 0 ? "text-green-600" : priceDiff > 0 ? "text-orange-600" : "text-muted-foreground"}`}>
                              {priceDiff === 0 ? "Au prix Topkit" : priceDiff < 0 ? `${Math.abs(priceDiff)}% moins cher que Topkit` : `${priceDiff}% plus cher que Topkit`}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                  {(listingForm.listing_type === "trade" || listingForm.listing_type === "both") && (
                    <div className="space-y-1">
                      <Label>Cherche en échange (optionnel)</Label>
                      <Input placeholder="Ex: PSG 2012 domicile taille L"
                        value={listingForm.trade_for}
                        onChange={e => setListingForm(f => ({ ...f, trade_for: e.target.value }))} />
                    </div>
                  )}
                </>
              );
            })()}

            {/* Photos obligatoires */}
            <div className="space-y-2 pt-2 border-t border-border">
              <p className="text-xs font-medium uppercase tracking-wide" style={{ fontFamily: "Barlow Condensed" }}>
                Photos du maillot <span className="text-destructive">*</span>
              </p>
              <div className="grid grid-cols-2 gap-3">
                {[{ side: "front", label: "Face avant" }, { side: "back", label: "Face arrière" }].map(({ side, label }) => (
                  <label key={side} className={`relative flex flex-col items-center justify-center border-2 border-dashed cursor-pointer aspect-[3/4] overflow-hidden transition-colors ${
                    listingPhotos[side] ? "border-primary/40 bg-primary/5" : "border-border hover:border-primary/40"
                  }`}>
                    <input type="file" accept="image/*" className="sr-only"
                      onChange={e => e.target.files[0] && handleUploadListingPhoto(side, e.target.files[0])} />
                    {photoUploading[side] ? (
                      <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                    ) : listingPhotos[side] ? (
                      <>
                        <img src={listingPhotos[side]} alt={label} className="absolute inset-0 w-full h-full object-cover" />
                        <span className="absolute bottom-1 right-1 bg-primary text-primary-foreground text-[9px] px-1 py-0.5 rounded">✓</span>
                      </>
                    ) : (
                      <>
                        <Plus className="w-6 h-6 text-muted-foreground mb-1" />
                        <span className="text-[10px] text-muted-foreground" style={{ fontFamily: "DM Sans" }}>{label}</span>
                      </>
                    )}
                  </label>
                ))}
              </div>
              {(!listingPhotos.front || !listingPhotos.back) && (
                <p className="text-[10px] text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
                  Les deux photos sont obligatoires pour publier l'annonce.
                </p>
              )}
            </div>
          </div>

          <DialogFooter className="px-6 py-4 border-t border-border shrink-0">
            <Button variant="ghost" onClick={resetListingDialog}>Annuler</Button>
            <Button
              onClick={handleCreateListing}
              disabled={
                listingLoading ||
                !listingPhotos.front || !listingPhotos.back ||
                photoUploading.front || photoUploading.back ||
                ((listingForm.listing_type === "sale" || listingForm.listing_type === "both") && !listingForm.asking_price)
              }
            >
              {listingLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Tag className="w-4 h-4 mr-2" />}
              Publier l'annonce
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
