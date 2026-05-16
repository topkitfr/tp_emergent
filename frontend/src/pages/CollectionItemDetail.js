import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  getCollectionItem,
  removeFromCollection,
  updateCollectionItem,
  createListing,
  cancelListing,
  proxyImageUrl,
  createPlayerPending,
  estimatePrice,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import {
  ArrowLeft, Edit2, Trash2, Tag, ExternalLink,
  ShoppingBag, Loader2, Check, Shield, Star, Package,
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

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);

  // edit sheet
  const [editOpen, setEditOpen] = useState(false);
  const [editForm, setEditForm] = useState(INITIAL_FORM_STATE);
  const [editMode, setEditMode] = useState("basic");
  const [saving, setSaving] = useState(false);

  // listing dialog
  const [listingOpen, setListingOpen] = useState(false);
  const [listingForm, setListingForm] = useState({ listing_type: "sale", asking_price: "", trade_for: "" });
  const [listingLoading, setListingLoading] = useState(false);

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

  const openEdit = () => {
    if (!item) return;
    setEditForm(formFromItem(item));
    setEditOpen(true);
  };

  const saveEdit = async () => {
    setSaving(true);
    try {
      const estimation = calculateEstimation(editForm, item.version, parseSeasonYear(item.master_kit?.season));
      let payload = formToPayload(editForm, estimation);

      // resolve pending players
      if (editForm.flocking_origin !== "none" && editForm.flocking_detail && !editForm.flocking_player_id) {
        const parts = editForm.flocking_detail.split(" ");
        const number = parts[parts.length - 1];
        const name = parts.slice(0, -1).join(" ");
        if (name) {
          const r = await createPlayerPending({ full_name: name, jersey_number: number || "" });
          payload.flocking_player_id = r.data.player_id;
        }
      }
      if (editForm.signed && editForm.signed_type === "handsigned" && editForm.signed_player_id === "" && editForm.signed_other_text === "") {
        if (editForm.flocking_player_id || payload.flocking_player_id) {
          payload.signed_by_player_id = editForm.flocking_player_id || payload.flocking_player_id;
        }
      }

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

  const handleCreateListing = async () => {
    setListingLoading(true);
    try {
      const payload = { collection_id, listing_type: listingForm.listing_type };
      if ((listingForm.listing_type === "sale" || listingForm.listing_type === "both") && listingForm.asking_price) {
        payload.asking_price = parseFloat(listingForm.asking_price);
      }
      if ((listingForm.listing_type === "trade" || listingForm.listing_type === "both") && listingForm.trade_for) {
        payload.trade_for = listingForm.trade_for;
      }
      await createListing(payload);
      toast.success("Annonce publiée !");
      setListingOpen(false);
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
      <Dialog open={listingOpen} onOpenChange={open => { if (!open) setListingOpen(false); }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Mettre en vente / échange</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
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
            {(listingForm.listing_type === "sale" || listingForm.listing_type === "both") && (
              <div className="space-y-1">
                <Label>Prix demandé (€)</Label>
                <Input type="number" min={0} step={0.01} placeholder="Ex: 80"
                  value={listingForm.asking_price} onChange={e => setListingForm(f => ({ ...f, asking_price: e.target.value }))} />
              </div>
            )}
            {(listingForm.listing_type === "trade" || listingForm.listing_type === "both") && (
              <div className="space-y-1">
                <Label>Cherche en échange (optionnel)</Label>
                <Input placeholder="Ex: PSG 2012 domicile taille L"
                  value={listingForm.trade_for} onChange={e => setListingForm(f => ({ ...f, trade_for: e.target.value }))} />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setListingOpen(false)}>Annuler</Button>
            <Button onClick={handleCreateListing}
              disabled={listingLoading || ((listingForm.listing_type === "sale" || listingForm.listing_type === "both") && !listingForm.asking_price)}>
              {listingLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Tag className="w-4 h-4 mr-2" />}
              Publier l'annonce
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
