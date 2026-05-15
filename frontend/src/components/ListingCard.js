import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { proxyImageUrl as getImageUrl } from "@/lib/api";

const TYPE_BADGE = {
  sale:  { label: "VENTE",          className: "bg-green-600 text-white" },
  trade: { label: "ÉCHANGE",        className: "bg-blue-600 text-white" },
  both:  { label: "VENTE / ÉCHANGE", className: "bg-purple-600 text-white" },
};

export default function ListingCard({ listing }) {
  const navigate = useNavigate();
  const badge = TYPE_BADGE[listing.listing_type] || TYPE_BADGE.sale;
  const kit = listing.kit_snapshot || {};
  const photo = kit.front_photo ? getImageUrl(kit.front_photo) : null;

  return (
    <div
      className="group relative bg-card border rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => navigate(`/marketplace/${listing.listing_id}`)}
    >
      {/* Image */}
      <div className="aspect-[3/4] bg-muted flex items-center justify-center overflow-hidden">
        {photo ? (
          <img src={photo} alt="kit" className="object-cover w-full h-full" />
        ) : (
          <span className="text-muted-foreground text-xs">Pas d'image</span>
        )}
      </div>

      {/* Badge type */}
      <div className="absolute top-2 left-2">
        <Badge className={badge.className}>{badge.label}</Badge>
      </div>

      {/* Infos */}
      <div className="p-3 space-y-1">
        <p className="font-semibold text-sm leading-tight truncate">
          {listing.seller?.name || listing.seller?.username || "Vendeur"}
        </p>
        <p className="text-xs text-muted-foreground truncate">
          {listing.condition_summary || "—"}
        </p>
        <div className="flex items-center justify-between pt-1">
          {listing.asking_price != null ? (
            <span className="font-bold text-accent-foreground">{listing.asking_price} €</span>
          ) : (
            <span className="text-xs text-muted-foreground italic">Échange uniquement</span>
          )}
          <Button size="sm" variant="outline" className="text-xs h-7 px-2">
            Voir
          </Button>
        </div>
      </div>
    </div>
  );
}
