import { useState, useEffect, useCallback } from "react";
import { getListings } from "@/lib/api";
import ListingCard from "@/components/ListingCard";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Loader2, ShoppingBag } from "lucide-react";
import Pagination from "@/components/Pagination";

const LIMIT = 48;

export default function Marketplace() {
  const [listings, setListings] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);

  const [listingType, setListingType] = useState("all");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const fetchListings = useCallback(async (currentSkip = 0) => {
    setLoading(true);
    try {
      const params = { skip: currentSkip, limit: LIMIT };
      if (listingType && listingType !== "all") params.listing_type = listingType;
      if (minPrice)    params.min_price = parseFloat(minPrice);
      if (maxPrice)    params.max_price = parseFloat(maxPrice);
      const res = await getListings(params);
      setListings(res.data.results);
      setTotal(res.data.total);
    } catch {
      setListings([]);
    } finally {
      setLoading(false);
    }
  }, [listingType, minPrice, maxPrice]);

  useEffect(() => {
    setSkip(0);
    fetchListings(0);
  }, [fetchListings]);

  const handlePage = (newSkip) => {
    setSkip(newSkip);
    fetchListings(newSkip);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <ShoppingBag className="w-6 h-6 text-accent-foreground" />
        <div>
          <h1 className="text-2xl font-bold">Marketplace</h1>
          <p className="text-sm text-muted-foreground">Achetez, vendez et échangez des maillots avec la communauté Topkit</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex flex-wrap gap-3 items-end">
        <div className="w-44">
          <Select value={listingType} onValueChange={setListingType}>
            <SelectTrigger><SelectValue placeholder="Tous les types" /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous</SelectItem>
              <SelectItem value="sale">Vente</SelectItem>
              <SelectItem value="trade">Échange</SelectItem>
              <SelectItem value="both">Vente ou échange</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <Input
            type="number"
            placeholder="Prix min €"
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
            className="w-28"
          />
          <span className="text-muted-foreground">–</span>
          <Input
            type="number"
            placeholder="Prix max €"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
            className="w-28"
          />
        </div>
        {(listingType !== "all" || minPrice || maxPrice) && (
          <Button variant="ghost" size="sm" onClick={() => { setListingType("all"); setMinPrice(""); setMaxPrice(""); }}>
            Réinitialiser
          </Button>
        )}
        <span className="text-sm text-muted-foreground ml-auto">{total} annonce{total !== 1 ? "s" : ""}</span>
      </div>

      {/* Grille */}
      {loading ? (
        <div className="flex justify-center py-20"><Loader2 className="animate-spin w-6 h-6" /></div>
      ) : listings.length === 0 ? (
        <div className="text-center py-20 text-muted-foreground">
          <ShoppingBag className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>Aucune annonce pour le moment.</p>
          <p className="text-xs mt-1">Mettez un maillot en vente depuis votre collection !</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {listings.map(l => <ListingCard key={l.listing_id} listing={l} />)}
        </div>
      )}

      {total > LIMIT && (
        <Pagination total={total} skip={skip} limit={LIMIT} onPage={handlePage} />
      )}
    </div>
  );
}
