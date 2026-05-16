import { useState, useEffect, useCallback } from "react";
import { getListings, getMarketplaceFilters } from "@/lib/api";
import ListingCard from "@/components/ListingCard";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Loader2, ShoppingBag, SlidersHorizontal, LayoutGrid, List, Search, X } from "lucide-react";
import Pagination from "@/components/Pagination";

const LIMIT = 48;
const EMPTY = "__all__";

const GENDER_LABELS = { man: "Men", woman: "Women", youth: "Youth" };
const PHYSICAL_STATES = ["New with tag", "Very good", "Used", "Damaged", "Needs restoration"];

function FiltersPanel({ filters, state, setState, activeFilterCount, clearFilters }) {
  const { search, setSearch, teamType, setTeamType, listingType, setListingType,
    minPrice, setMinPrice, maxPrice, setMaxPrice,
    club, setClub, brand, setBrand, season, setSeason,
    kitType, setKitType, league, setLeague, gender, setGender,
    physicalState, setPhysicalState, signed, setSigned } = state;

  const selectFilters = [
    { label: "Club",     value: club,     set: setClub,     options: filters.clubs     ?? [] },
    { label: "Brand",    value: brand,    set: setBrand,    options: filters.brands    ?? [] },
    { label: "Season",   value: season,   set: setSeason,   options: filters.seasons   ?? [] },
    { label: "Kit type", value: kitType,  set: setKitType,  options: filters.kit_types ?? [] },
    { label: "League",   value: league,   set: setLeague,   options: filters.leagues   ?? [] },
    { label: "Gender",   value: gender,   set: setGender,   options: filters.genders   ?? [], labelMap: GENDER_LABELS },
    { label: "État",     value: physicalState, set: setPhysicalState, options: PHYSICAL_STATES },
  ];

  return (
    <div className="space-y-4">
      {/* Type */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Type d'annonce</label>
        <Select value={listingType} onValueChange={setListingType}>
          <SelectTrigger><SelectValue /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tous</SelectItem>
            <SelectItem value="sale">Vente</SelectItem>
            <SelectItem value="trade">Échange</SelectItem>
            <SelectItem value="both">Vente ou échange</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Toggle Club / National */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Type</label>
        <div className="flex items-center gap-0 border border-border">
          {[{ id: "club", label: "Club" }, { id: "national", label: "National" }].map(({ id, label }, i) => (
            <button
              key={id}
              onClick={() => setTeamType(teamType === id ? "" : id)}
              className={`flex-1 px-3 py-2 text-sm font-semibold uppercase tracking-wide transition-colors ${
                i === 0 ? "" : "border-l border-border"
              } ${teamType === id
                ? "bg-primary text-primary-foreground"
                : "bg-transparent text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
              style={{ fontFamily: "Barlow Condensed, sans-serif" }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input placeholder="Rechercher..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9" />
      </div>

      {/* Prix */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Prix (€)</label>
        <div className="flex items-center gap-2">
          <Input type="number" placeholder="Min" value={minPrice} onChange={e => setMinPrice(e.target.value)} className="w-full" />
          <span className="text-muted-foreground shrink-0">–</span>
          <Input type="number" placeholder="Max" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} className="w-full" />
        </div>
      </div>

      {/* Dynamic selects */}
      {selectFilters.map(({ label, value, set, options, labelMap }) => (
        <div key={label} className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
          <Select value={value || EMPTY} onValueChange={v => set(v === EMPTY ? "" : v)}>
            <SelectTrigger>
              <SelectValue placeholder={`Tous`} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={EMPTY}>Tous</SelectItem>
              {options.map(o => (
                <SelectItem key={o} value={o}>{labelMap ? (labelMap[o] ?? o) : o}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ))}

      {/* Signé */}
      <div className="flex items-center justify-between">
        <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Signé</Label>
        <Switch
          checked={signed === true}
          onCheckedChange={v => setSigned(v ? true : null)}
        />
      </div>

      {activeFilterCount > 0 && (
        <Button variant="ghost" onClick={clearFilters} className="w-full text-muted-foreground">
          <X className="w-4 h-4 mr-2" /> Effacer les filtres
        </Button>
      )}
    </div>
  );
}

export default function Marketplace() {
  const [listings, setListings] = useState([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState("grid");
  const [filters, setFilters] = useState({ clubs: [], brands: [], seasons: [], kit_types: [], leagues: [], genders: [] });

  const [listingType, setListingType] = useState("all");
  const [teamType,    setTeamType]    = useState("");
  const [search,      setSearch]      = useState("");
  const [minPrice,    setMinPrice]    = useState("");
  const [maxPrice,    setMaxPrice]    = useState("");
  const [club,        setClub]        = useState("");
  const [brand,       setBrand]       = useState("");
  const [season,      setSeason]      = useState("");
  const [kitType,     setKitType]     = useState("");
  const [league,      setLeague]      = useState("");
  const [gender,      setGender]      = useState("");
  const [physicalState, setPhysicalState] = useState("");
  const [signed,      setSigned]      = useState(null);

  const activeFilterCount = [
    listingType !== "all" ? listingType : "",
    teamType, search, minPrice, maxPrice, club, brand,
    season, kitType, league, gender, physicalState,
    signed === true ? "signed" : "",
  ].filter(Boolean).length;

  const clearFilters = () => {
    setListingType("all"); setTeamType(""); setSearch(""); setMinPrice(""); setMaxPrice("");
    setClub(""); setBrand(""); setSeason(""); setKitType(""); setLeague("");
    setGender(""); setPhysicalState(""); setSigned(null);
  };

  useEffect(() => {
    getMarketplaceFilters()
      .then(r => setFilters(r.data))
      .catch(() => {});
  }, []);

  const fetchListings = useCallback(async (currentSkip = 0) => {
    setLoading(true);
    try {
      const params = { skip: currentSkip, limit: LIMIT };
      if (listingType && listingType !== "all") params.listing_type = listingType;
      if (teamType)      params.team_type      = teamType;
      if (search)        params.search         = search;
      if (minPrice)      params.min_price      = parseFloat(minPrice);
      if (maxPrice)      params.max_price      = parseFloat(maxPrice);
      if (club)          params.club           = club;
      if (brand)         params.brand          = brand;
      if (season)        params.season         = season;
      if (kitType)       params.kit_type       = kitType;
      if (league)        params.league         = league;
      if (gender)        params.gender         = gender;
      if (physicalState) params.physical_state = physicalState;
      if (signed === true) params.signed       = true;
      const res = await getListings(params);
      setListings(res.data.results);
      setTotal(res.data.total);
    } catch {
      setListings([]);
    } finally {
      setLoading(false);
    }
  }, [listingType, teamType, search, minPrice, maxPrice, club, brand, season, kitType, league, gender, physicalState, signed]);

  useEffect(() => {
    setSkip(0);
    fetchListings(0);
  }, [fetchListings]);

  const handlePage = (newSkip) => {
    setSkip(newSkip);
    fetchListings(newSkip);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const filterState = {
    search, setSearch, teamType, setTeamType,
    listingType, setListingType,
    minPrice, setMinPrice, maxPrice, setMaxPrice,
    club, setClub, brand, setBrand, season, setSeason,
    kitType, setKitType, league, setLeague, gender, setGender,
    physicalState, setPhysicalState, signed, setSigned,
  };

  const gridClass = viewMode === "grid"
    ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
    : "flex flex-col gap-3";

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">

      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <ShoppingBag className="w-6 h-6 text-accent-foreground" />
        <div>
          <h1 className="text-2xl font-bold">Marketplace</h1>
          <p className="text-sm text-muted-foreground">Achetez, vendez et échangez des maillots avec la communauté Topkit</p>
        </div>
      </div>

      <div className="flex gap-8">

        {/* Sidebar desktop */}
        <aside className="hidden lg:block w-56 shrink-0">
          <FiltersPanel filters={filters} state={filterState} activeFilterCount={activeFilterCount} clearFilters={clearFilters} />
        </aside>

        <div className="flex-1 min-w-0 space-y-5">

          {/* Top bar */}
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">
              {loading ? "Chargement..." : `${total} annonce${total !== 1 ? "s" : ""}`}
            </span>

            <div className="flex items-center gap-2">
              {/* Sheet mobile */}
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="lg:hidden relative">
                    <SlidersHorizontal className="w-4 h-4 mr-2" />
                    Filtres
                    {activeFilterCount > 0 && (
                      <Badge className="absolute -top-2 -right-2 w-5 h-5 flex items-center justify-center p-0 text-xs">
                        {activeFilterCount}
                      </Badge>
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-72">
                  <SheetHeader><SheetTitle>Filtres</SheetTitle></SheetHeader>
                  <div className="mt-4">
                    <FiltersPanel filters={filters} state={filterState} activeFilterCount={activeFilterCount} clearFilters={clearFilters} />
                  </div>
                </SheetContent>
              </Sheet>

              {/* View toggle */}
              <div className="flex items-center gap-1 border rounded-lg p-1">
                <button onClick={() => setViewMode("grid")} className={`p-1.5 rounded transition-colors ${viewMode === "grid" ? "bg-muted" : "hover:bg-muted"}`}>
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button onClick={() => setViewMode("list")} className={`p-1.5 rounded transition-colors ${viewMode === "list" ? "bg-muted" : "hover:bg-muted"}`}>
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          {loading ? (
            <div className="flex justify-center py-20"><Loader2 className="animate-spin w-6 h-6" /></div>
          ) : listings.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground">
              <ShoppingBag className="w-10 h-10 mx-auto mb-3 opacity-30" />
              <p>Aucune annonce pour le moment.</p>
              {activeFilterCount > 0 && (
                <Button variant="outline" size="sm" onClick={clearFilters} className="mt-3">Effacer les filtres</Button>
              )}
            </div>
          ) : (
            <div className={gridClass}>
              {listings.map(l => <ListingCard key={l.listing_id} listing={l} />)}
            </div>
          )}

          {total > LIMIT && (
            <Pagination total={total} skip={skip} limit={LIMIT} onPage={handlePage} />
          )}
        </div>
      </div>
    </div>
  );
}
