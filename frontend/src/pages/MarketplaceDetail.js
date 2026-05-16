import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getListing, updateOffer, cancelListing } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ArrowLeft, Loader2, ShoppingBag, RefreshCw, Check, X } from "lucide-react";
import OfferDialog from "@/components/OfferDialog";
import { proxyImageUrl as getImageUrl } from "@/lib/api";

const TYPE_LABEL = { sale: "Vente", trade: "Échange", both: "Vente ou échange" };
const STATUS_BADGE = {
  active:    { label: "Actif",     className: "bg-green-100 text-green-800" },
  reserved:  { label: "Réservé",   className: "bg-yellow-100 text-yellow-800" },
  completed: { label: "Terminé",   className: "bg-gray-100 text-gray-600" },
  cancelled: { label: "Annulé",    className: "bg-red-100 text-red-700" },
};
const OFFER_STATUS = {
  pending:   { label: "En attente", className: "bg-yellow-100 text-yellow-800" },
  accepted:  { label: "Acceptée",  className: "bg-green-100 text-green-800" },
  refused:   { label: "Refusée",   className: "bg-red-100 text-red-700" },
  withdrawn: { label: "Retirée",   className: "bg-gray-100 text-gray-600" },
};

export default function MarketplaceDetail() {
  const { listingId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const [listing, setListing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [offerOpen, setOfferOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState(null);

  const fetchListing = async () => {
    setLoading(true);
    try {
      const res = await getListing(listingId);
      setListing(res.data);
    } catch {
      navigate("/marketplace");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchListing(); }, [listingId]);

  const isSeller = user && listing && user.user_id === listing.user_id;
  const isActive = listing?.status === "active";

  const handleOfferAction = async (offerId, status) => {
    setActionLoading(offerId + status);
    try {
      await updateOffer(offerId, { status });
      toast({ title: status === "accepted" ? "Offre acceptée !" : "Offre refusée." });
      fetchListing();
    } catch (e) {
      toast({ title: "Erreur", description: e.response?.data?.detail, variant: "destructive" });
    } finally {
      setActionLoading(null);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm("Annuler cette annonce ?")) return;
    try {
      await cancelListing(listingId);
      toast({ title: "Annonce annulée." });
      navigate("/marketplace");
    } catch (e) {
      toast({ title: "Erreur", description: e.response?.data?.detail, variant: "destructive" });
    }
  };

  if (loading) return <div className="flex justify-center py-20"><Loader2 className="animate-spin w-6 h-6" /></div>;
  if (!listing) return null;

  const kit = listing.version || {};
  const col = listing.collection_item || {};
  const listingPhotos = listing.listing_photos || [];
  const fallbackPhoto = col.front_photo ? getImageUrl(col.front_photo) : kit.front_photo ? getImageUrl(kit.front_photo) : null;
  const [activePhoto, setActivePhoto] = useState(0);
  const photos = listingPhotos.length > 0 ? listingPhotos : (fallbackPhoto ? [fallbackPhoto] : []);
  const sb = STATUS_BADGE[listing.status] || STATUS_BADGE.active;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Button variant="ghost" size="sm" onClick={() => navigate("/marketplace")} className="mb-6 -ml-2">
        <ArrowLeft className="w-4 h-4 mr-1" /> Marketplace
      </Button>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Photos */}
        <div className="space-y-2">
          <div className="aspect-[3/4] bg-muted overflow-hidden flex items-center justify-center border border-border">
            {photos.length > 0
              ? <img src={photos[activePhoto]} alt="kit" className="object-cover w-full h-full" />
              : <ShoppingBag className="w-16 h-16 opacity-20" />
            }
          </div>
          {photos.length > 1 && (
            <div className="flex gap-2">
              {photos.map((url, i) => (
                <button key={i} onClick={() => setActivePhoto(i)}
                  className={`w-16 h-20 border-2 overflow-hidden shrink-0 transition-colors ${i === activePhoto ? 'border-primary' : 'border-border'}`}>
                  <img src={url} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Infos */}
        <div className="space-y-5">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className={sb.className}>{sb.label}</Badge>
            <Badge variant="outline">{TYPE_LABEL[listing.listing_type]}</Badge>
          </div>

          {/* Prix */}
          {listing.asking_price != null && (
            <div>
              <p className="text-3xl font-bold">{listing.asking_price} €</p>
              {listing.estimated_price && (
                <p className="text-xs text-muted-foreground mt-1">Estimation Topkit : {listing.estimated_price} €</p>
              )}
            </div>
          )}

          {/* État */}
          {listing.condition_summary && (
            <div>
              <p className="text-sm font-medium">État</p>
              <p className="text-sm text-muted-foreground">{listing.condition_summary}</p>
            </div>
          )}

          {/* Échange recherché */}
          {listing.trade_for && (
            <div>
              <p className="text-sm font-medium">Cherche en échange</p>
              <p className="text-sm text-muted-foreground">{listing.trade_for}</p>
            </div>
          )}

          <Separator />

          {/* Vendeur */}
          <div className="flex items-center gap-3">
            <Avatar className="w-9 h-9">
              <AvatarFallback>{(listing.seller?.name || "?")[0].toUpperCase()}</AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{listing.seller?.name || listing.seller?.username || "Vendeur"}</p>
              <p className="text-xs text-muted-foreground">Vendeur</p>
            </div>
          </div>

          {/* Actions */}
          {!isSeller && isActive && user && (
            <Button className="w-full" onClick={() => setOfferOpen(true)}>
              <ShoppingBag className="w-4 h-4 mr-2" />
              Faire une offre
            </Button>
          )}
          {!user && isActive && (
            <Button className="w-full" variant="outline" onClick={() => navigate("/login")}>
              Connectez-vous pour faire une offre
            </Button>
          )}
          {isSeller && isActive && (
            <Button variant="destructive" size="sm" onClick={handleCancel}>
              Annuler l'annonce
            </Button>
          )}
        </div>
      </div>

      {/* Offres reçues (vendeur uniquement) */}
      {isSeller && listing.offers && listing.offers.length > 0 && (
        <div className="mt-10">
          <h2 className="text-lg font-semibold mb-4">Offres reçues ({listing.offers.length})</h2>
          <div className="space-y-3">
            {listing.offers.map(offer => {
              const os = OFFER_STATUS[offer.status] || OFFER_STATUS.pending;
              return (
                <Card key={offer.offer_id}>
                  <CardContent className="pt-4 flex items-center justify-between gap-4 flex-wrap">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-sm">{offer.offerer?.name || offer.offerer?.username || "Utilisateur"}</p>
                        <Badge className={os.className + " text-xs"}>{os.label}</Badge>
                      </div>
                      {offer.offered_price != null && <p className="text-sm">Offre : <strong>{offer.offered_price} €</strong></p>}
                      {offer.offered_collection_id && <p className="text-xs text-muted-foreground">+ échange de maillot</p>}
                      {offer.message && <p className="text-xs text-muted-foreground italic">"{offer.message}"</p>}
                    </div>
                    {offer.status === "pending" && isActive && (
                      <div className="flex gap-2">
                        <Button
                          size="sm" variant="outline"
                          className="border-green-500 text-green-700 hover:bg-green-50"
                          disabled={actionLoading === offer.offer_id + "accepted"}
                          onClick={() => handleOfferAction(offer.offer_id, "accepted")}
                        >
                          <Check className="w-4 h-4 mr-1" /> Accepter
                        </Button>
                        <Button
                          size="sm" variant="outline"
                          className="border-red-400 text-red-600 hover:bg-red-50"
                          disabled={actionLoading === offer.offer_id + "refused"}
                          onClick={() => handleOfferAction(offer.offer_id, "refused")}
                        >
                          <X className="w-4 h-4 mr-1" /> Refuser
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      <OfferDialog
        listing={listing}
        open={offerOpen}
        onClose={() => setOfferOpen(false)}
        onSuccess={fetchListing}
      />
    </div>
  );
}
