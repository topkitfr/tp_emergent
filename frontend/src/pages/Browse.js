// src/pages/Browse.js
import { getMasterKits, getFilters } from '../lib/api';
import { useState, useEffect } from "react";
import { Search, SlidersHorizontal, LayoutGrid, List, Shirt, X } from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import JerseyCard from "@/components/JerseyCard";

const EMPTY_FILTER = "__all__";
const LIMIT = 50;

// Labels affichés pour les valeurs entity_type
const ENTITY_TYPE_LABELS = {
  club: "Club",
  nation: "National",
};

// Labels affichés pour les valeurs gender
const GENDER_LABELS = {
  man: "Men",
  woman: "Women",
  youth: "Youth",
};

function FiltersPanel({ entityType, setEntityType, search, setSearch, filterItems, activeFilterCount, clearFilters }) {
  return (
    <div className="space-y-4">
      {/* Toggle Club / National */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Type</label>
        <div className="flex items-center gap-2">
          {[
            { id: "", label: "All" },
            { id: "club", label: "Club" },
            { id: "nation", label: "National" },
          ].map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setEntityType(id)}
              className={`flex-1 px-3 py-1.5 text-sm font-semibold uppercase tracking-wide transition-colors border ${
                entityType === id
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-transparent text-muted-foreground border-border hover:border-primary hover:text-foreground"
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
        <Input
          placeholder="Search kits..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Dynamic filter selects */}
      {filterItems.map(({ label, value, set, options, labelMap }) => (
        <div key={label} className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
          <Select value={value || EMPTY_FILTER} onValueChange={(v) => set(v === EMPTY_FILTER ? "" : v)}>
            <SelectTrigger>
              <SelectValue placeholder={`All ${label.toLowerCase()}s`} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={EMPTY_FILTER}>All {label.toLowerCase()}s</SelectItem>
              {options.map((o) => (
                <SelectItem key={o} value={o}>
                  {labelMap ? (labelMap[o] ?? o) : o}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ))}

      {activeFilterCount > 0 && (
        <Button variant="ghost" onClick={clearFilters} className="w-full text-muted-foreground">
          <X className="w-4 h-4 mr-2" /> Clear filters
        </Button>
      )}
    </div>
  );
}

export default function Browse() {
  const [kits,             setKits]            = useState([]);
  const [total,            setTotal]           = useState(0);
  const [skip,             setSkip]            = useState(0);
  const [filters,          setFilters]         = useState({
    clubs: [], brands: [], seasons: [], kit_types: [], designs: [], leagues: [], genders: [],
  });
  const [loading,          setLoading]         = useState(true);
  const [loadingMore,      setLoadingMore]     = useState(false);
  const [viewMode,         setViewMode]        = useState("grid");
  const [search,           setSearch]          = useState("");
  const [entityType,       setEntityType]      = useState("");   // "" | "club" | "nation"
  const [selectedClub,     setSelectedClub]    = useState("");
  const [selectedBrand,    setSelectedBrand]   = useState("");
  const [selectedType,     setSelectedType]    = useState("");
  const [selectedSeason,   setSelectedSeason]  = useState("");
  const [selectedDesign,   setSelectedDesign]  = useState("");
  const [selectedLeague,   setSelectedLeague]  = useState("");
  const [selectedGender,   setSelectedGender]  = useState("");

  const activeFilterCount = [
    search, entityType, selectedClub, selectedBrand, selectedType,
    selectedSeason, selectedDesign, selectedLeague, selectedGender,
  ].filter(Boolean).length;

  const clearFilters = () => {
    setSearch(""); setEntityType(""); setSelectedClub(""); setSelectedBrand("");
    setSelectedType(""); setSelectedSeason(""); setSelectedDesign("");
    setSelectedLeague(""); setSelectedGender("");
  };

  // Reset pagination on filter change
  useEffect(() => {
    setSkip(0);
  }, [search, entityType, selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague, selectedGender]);

  // Load filter options once
  useEffect(() => {
    getFilters()
      .then((r) => setFilters(r.data))
      .catch((e) => console.error("Filters error:", e));
  }, []);

  // Fetch master kits
  useEffect(() => {
    const isLoadMore = skip > 0;
    if (isLoadMore) setLoadingMore(true);
    else setLoading(true);

    const params = { skip, limit: LIMIT };
    if (search)          params.search      = search;
    if (entityType)      params.entity_type = entityType;
    if (selectedClub)    params.club        = selectedClub;
    if (selectedBrand)   params.brand       = selectedBrand;
    if (selectedType)    params.kit_type    = selectedType;
    if (selectedSeason)  params.season      = selectedSeason;
    if (selectedDesign)  params.design      = selectedDesign;
    if (selectedLeague)  params.league      = selectedLeague;
    if (selectedGender)  params.gender      = selectedGender;

    getMasterKits(params)
      .then((r) => {
        const newKits = r.data?.results ?? [];
        setKits((prev) => skip === 0 ? newKits : [...prev, ...newKits]);
        setTotal(r.data?.total ?? 0);
        setLoading(false);
        setLoadingMore(false);
      })
      .catch((e) => { console.error("Kits error:", e); setLoading(false); setLoadingMore(false); });
  }, [skip, search, entityType, selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague, selectedGender]);

  const filterItems = [
    { label: "Club",     value: selectedClub,    set: setSelectedClub,    options: filters.clubs     ?? [] },
    { label: "Brand",    value: selectedBrand,   set: setSelectedBrand,   options: filters.brands    ?? [] },
    { label: "Season",   value: selectedSeason,  set: setSelectedSeason,  options: filters.seasons   ?? [] },
    { label: "Kit type", value: selectedType,    set: setSelectedType,    options: filters.kit_types ?? [] },
    { label: "League",   value: selectedLeague,  set: setSelectedLeague,  options: filters.leagues   ?? [] },
    { label: "Design",   value: selectedDesign,  set: setSelectedDesign,  options: filters.designs   ?? [] },
    { label: "Gender",   value: selectedGender,  set: setSelectedGender,  options: filters.genders   ?? [], labelMap: GENDER_LABELS },
  ];

  const filtersPanelProps = { entityType, setEntityType, search, setSearch, filterItems, activeFilterCount, clearFilters };
  const gridClass = viewMode === "grid" ? "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4" : "flex flex-col gap-3";

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex gap-8">

        <aside className="hidden lg:block w-56 shrink-0">
          <FiltersPanel {...filtersPanelProps} />
        </aside>

        <div className="flex-1 min-w-0 space-y-5">

          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">
              {loading ? "Loading..." : `${total} kits found`}
            </span>

            <div className="flex items-center gap-2">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="lg:hidden relative">
                    <SlidersHorizontal className="w-4 h-4 mr-2" />
                    Filters
                    {activeFilterCount > 0 && (
                      <Badge className="absolute -top-2 -right-2 w-5 h-5 flex items-center justify-center p-0 text-xs">
                        {activeFilterCount}
                      </Badge>
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-72">
                  <SheetHeader><SheetTitle>Filters</SheetTitle></SheetHeader>
                  <div className="mt-4">
                    <FiltersPanel {...filtersPanelProps} />
                  </div>
                </SheetContent>
              </Sheet>

              <div className="flex items-center gap-1 border rounded-lg p-1">
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-1.5 rounded transition-colors ${viewMode === "grid" ? "bg-muted" : "hover:bg-muted"}`}
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-1.5 rounded transition-colors ${viewMode === "list" ? "bg-muted" : "hover:bg-muted"}`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {loading ? (
            <div className={gridClass}>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="rounded-xl border bg-muted animate-pulse aspect-[3/4]" />
              ))}
            </div>
          ) : kits.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-24 text-muted-foreground">
              <Shirt className="w-10 h-10" />
              <p>Try adjusting your filters or search term.</p>
              {activeFilterCount > 0 && (
                <Button variant="outline" size="sm" onClick={clearFilters}>Clear filters</Button>
              )}
            </div>
          ) : (
            <div className={gridClass}>
              {kits.map((kit) => (
                <JerseyCard key={kit.kit_id} kit={kit} />
              ))}
            </div>
          )}

          {/* Load more */}
          {!loading && kits.length < total && (
            <div className="flex justify-center pt-4">
              <Button
                variant="outline"
                onClick={() => setSkip((s) => s + LIMIT)}
                disabled={loadingMore}
              >
                {loadingMore ? "Loading..." : `Load more (${total - kits.length} remaining)`}
              </Button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
