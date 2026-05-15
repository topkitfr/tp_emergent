import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createOffer, getMyCollection as getCollections } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { useEffect } from "react";

export default function OfferDialog({ listing, open, onClose, onSuccess }) {
  const { toast } = useToast();
  const [offerType, setOfferType] = useState("buy");
  const [offeredPrice, setOfferedPrice] = useState("");
  const [offeredCollectionId, setOfferedCollectionId] = useState("");
  const [message, setMessage] = useState("");
  const [myCollection, setMyCollection] = useState([]);
  const [loading, setLoading] = useState(false);

  const canBuy  = listing?.listing_type === "sale" || listing?.listing_type === "both";
  const canTrade = listing?.listing_type === "trade" || listing?.listing_type === "both";

  useEffect(() => {
    if (open && canTrade) {
      getCollections().then(r => setMyCollection(r.data?.items || r.data || [])).catch(() => {});
    }
  }, [open, canTrade]);

  // Initialise le type d'offre selon ce qui est disponible
  useEffect(() => {
    if (canBuy) setOfferType("buy");
    else if (canTrade) setOfferType("trade");
  }, [canBuy, canTrade]);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const payload = {
        offer_type: offerType,
        message: message || undefined,
      };
      if (offerType === "buy" || offerType === "buy_and_trade") {
        payload.offered_price = parseFloat(offeredPrice);
      }
      if (offerType === "trade" || offerType === "buy_and_trade") {
        payload.offered_collection_id = offeredCollectionId;
      }
      await createOffer(listing.listing_id, payload);
      toast({ title: "Offre envoyée !", description: "Le vendeur va recevoir une notification." });
      onSuccess?.();
      onClose();
    } catch (e) {
      toast({ title: "Erreur", description: e.response?.data?.detail || "Une erreur est survenue.", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Faire une offre</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type d'offre */}
          {canBuy && canTrade && (
            <div className="space-y-1">
              <Label>Type d'offre</Label>
              <Select value={offerType} onValueChange={setOfferType}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {canBuy  && <SelectItem value="buy">Achat</SelectItem>}
                  {canTrade && <SelectItem value="trade">Échange</SelectItem>}
                  {canBuy && canTrade && <SelectItem value="buy_and_trade">Achat + Échange</SelectItem>}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Prix */}
          {(offerType === "buy" || offerType === "buy_and_trade") && (
            <div className="space-y-1">
              <Label>
                Votre offre (€)
                {listing?.asking_price && (
                  <span className="text-muted-foreground font-normal ml-2 text-xs">
                    Prix demandé : {listing.asking_price} €
                  </span>
                )}
              </Label>
              <Input
                type="number"
                min={0}
                step={0.01}
                value={offeredPrice}
                onChange={e => setOfferedPrice(e.target.value)}
                placeholder="Ex: 80"
              />
            </div>
          )}

          {/* Maillot proposé en échange */}
          {(offerType === "trade" || offerType === "buy_and_trade") && (
            <div className="space-y-1">
              <Label>Maillot à échanger (depuis votre collection)</Label>
              <Select value={offeredCollectionId} onValueChange={setOfferedCollectionId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choisir un maillot…" />
                </SelectTrigger>
                <SelectContent>
                  {myCollection.length === 0 && (
                    <SelectItem value="" disabled>Aucun maillot dans votre collection</SelectItem>
                  )}
                  {myCollection.map(item => (
                    <SelectItem key={item.collection_id} value={item.collection_id}>
                      {item.club || item.version_id} — {item.size || ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Message */}
          <div className="space-y-1">
            <Label>Message (optionnel)</Label>
            <Textarea
              value={message}
              onChange={e => setMessage(e.target.value)}
              placeholder="Précisez vos conditions, disponibilités…"
              rows={3}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>Annuler</Button>
          <Button
            onClick={handleSubmit}
            disabled={loading || (offerType === "buy" && !offeredPrice) || (offerType === "trade" && !offeredCollectionId)}
          >
            {loading ? "Envoi…" : "Envoyer l'offre"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
