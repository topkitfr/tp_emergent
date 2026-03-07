// src/pages/Browse.js
import { useState, useEffect } from "react";
import {
  Search, SlidersHorizontal, LayoutGrid, List, Shirt, X
} from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import JerseyCard from "@/components/JerseyCard";
import VersionCard from "@/components/VersionCard";

const EMPTY_FILTER = "__all__";

// ── Composant panneau filtres — défini HORS du composant principal ──
function FiltersPanel({
  browseMode, setBrowseMode,
  search, setSearch,
  filterItems, activeFilterCount, clearFilters,
}) {
  return (
    <div className="space-y-4">

{/* Toggle Kits / Versions */}
<div className="space-y-1.5">
  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
    View
  </label>
  <div className="flex items-center gap-2">
    {[
      { id: "master",  label: "Master" },
      { id: "version", label: "Version" },
    ].map(({ id, label }) => (
      <button
        key={id}
        onClick={() => setBrowseMode(id)}
        className={`flex-1 px-3 py-1.5 text-sm font-semibold uppercase tracking-wide transition-colors border ${
          browseMode === id
            ? "bg-primary text-primary-foreground border-primary"
            : "bg-transparent text-muted-foreground border-border hover:border-primary hover:text-foreground"
        }`}
        style={{ fontFamily: 'Barlow Condensed, sans-serif' }}
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

      {/* Dropdowns */}
      {filterItems.map(({ label, value, set, options }) => (
        <div key={label} className="space-y-1.5">
          <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {label}
          </label>
          <Select
            value={value || EMPTY_FILTER}
            onValueChange={(v) => set(v === EMPTY_FILTER ? "" : v)}
          >
            <SelectTrigger>
              <SelectValue placeholder={`All ${label.toLowerCase()}s`} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value={EMPTY_FILTER}>All {label.toLowerCase()}s</SelectItem>
              {options.map((o) => (
                <SelectItem key={o} value={o}>{o}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      ))}

      {/* Clear filters */}
      {activeFilterCount > 0 && (
        <Button variant="ghost" onClick={clearFilters} className="w-full text-muted-foreground">
          <X className="w-4 h-4 mr-2" /> Clear filters
        </Button>
      )}
    </div>
  );
}

// ── Composant principal ───────────────────────────────
export default function Browse() {

  const [browseMode,      setBrowseMode]      = useState("master");
  const [kits,            setKits]            = useState([]);
  const [versions,        setVersions]        = useState([]);
  const [filters,         setFilters]         = useState({
    clubs: [], brands: [], seasons: [], kit_types: [], designs: [], leagues: [],
  });
  const [loading,         setLoading]         = useState(true);
  const [viewMode,        setViewMode]        = useState("grid");
  const [search,          setSearch]          = useState("");
  const [selectedClub,    setSelectedClub]    = useState("");
  const [selectedBrand,   setSelectedBrand]   = useState("");
  const [selectedType,    setSelectedType]    = useState("");
  const [selectedSeason,  setSelectedSeason]  = useState("");
  const [selectedDesign,  setSelectedDesign]  = useState("");
  const [selectedLeague,  setSelectedLeague]  = useState("");
  const [quickAddVersion, setQuickAddVersion] = useState(null);

  const activeFilterCount = [
    search, selectedClub, selectedBrand, selectedType,
    selectedSeason, selectedDesign, selectedLeague,
  ].filter(Boolean).length;

  const clearFilters = () => {
    setSearch(""); setSelectedClub(""); setSelectedBrand("");
    setSelectedType(""); setSelectedSeason(""); setSelectedDesign(""); setSelectedLeague("");
  };

  // ── Fetch filtres ──────────────────────────────────────
  useEffect(() => {
    fetch("/api/master-kits/filters")
      .then((r) => { if (!r.ok) throw new Error(`filters: ${r.status}`); return r.json(); })
      .then(setFilters)
      .catch((e) => console.error("Filters error:", e));
  }, []);

  // ── Fetch master kits ──────────────────────────────────
  useEffect(() => {
    if (browseMode !== "master") return;
    setLoading(true);
    const params = new URLSearchParams();
    if (search)         params.set("search",   search);
    if (selectedClub)   params.set("club",     selectedClub);
    if (selectedBrand)  params.set("brand",    selectedBrand);
    if (selectedType)   params.set("kit_type", selectedType);
    if (selectedSeason) params.set("season",   selectedSeason);
    if (selectedDesign) params.set("design",   selectedDesign);
    if (selectedLeague) params.set("league",   selectedLeague);

    fetch(`/api/master-kits?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`master-kits: ${r.status}`); return r.json(); })
      .then((data) => { setKits(Array.isArray(data) ? data : []); setLoading(false); })
      .catch((e) => { console.error("Kits error:", e); setLoading(false); });
  }, [browseMode, search, selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague]);

  // ── Fetch versions ─────────────────────────────────────
  useEffect(() => {
    if (browseMode !== "version") return;
    setLoading(true);
    const params = new URLSearchParams();
    if (search)         params.set("search",   search);
    if (selectedClub)   params.set("club",     selectedClub);
    if (selectedBrand)  params.set("brand",    selectedBrand);
    if (selectedType)   params.set("kit_type", selectedType);
    if (selectedSeason) params.set("season",   selectedSeason);
    if (selectedLeague) params.set("league",   selectedLeague);

    fetch(`/api/versions?${params}`)
      .then((r) => { if (!r.ok) throw new Error(`versions: ${r.status}`); return r.json(); })
      .then((data) => { setVersions(Array.isArray(data) ? data : []); setLoading(false); })
      .catch((e) => { console.error("Versions error:", e); setLoading(false); });
  }, [browseMode, search, selectedClub, selectedBrand, selectedType, selectedSeason, selectedLeague]);

  // ── Props du panneau filtres ───────────────────────────
  const filterItems = [
    { label: "Club",     value: selectedClub,   set: setSelectedClub,   options: filters.clubs },
    { label: "Brand",    value: selectedBrand,  set: setSelectedBrand,  options: filters.brands },
    { label: "Season",   value: selectedSeason, set: setSelectedSeason, options: filters.seasons },
    { label: "Kit type", value: selectedType,   set: setSelectedType,   options: filters.kit_types },
    { label: "League",   value: selectedLeague, set: setSelectedLeague, options: filters.leagues },
    ...(browseMode === "master"
      ? [{ label: "Design", value: selectedDesign, set: setSelectedDesign, options: filters.designs }]
      : []),
  ];

  const filtersPanelProps = {
    browseMode, setBrowseMode,
    search, setSearch,
    filterItems, activeFilterCount, clearFilters,
  };

  // ── Rendu ──────────────────────────────────────────────
  const gridClass = viewMode === "grid"
    ? "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4"
    : "flex flex-col gap-3";

  const isEmpty = browseMode === "master" ? kits.length === 0 : versions.length === 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex gap-8">

        {/* Sidebar desktop */}
        <aside className="hidden lg:block w-56 shrink-0">
          <FiltersPanel {...filtersPanelProps} />
        </aside>

        {/* Contenu principal */}
        <div className="flex-1 min-w-0 space-y-5">

          {/* Topbar */}
          <div className="flex items-center justify-between gap-3">

            <span className="text-sm text-muted-foreground">
              {loading ? "Loading..." : (
                browseMode === "master"
                  ? `${kits.length} kits found`
                  : `${versions.length} versions found`
              )}
            </span>

            <div className="flex items-center gap-2">

              {/* Filtres mobile */}
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

              {/* Toggle Grid / List */}
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

          {/* Grille */}
          {loading ? (
            <div className={gridClass}>
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="rounded-xl border bg-muted animate-pulse aspect-[3/4]" />
              ))}
            </div>
          ) : isEmpty ? (
            <div className="flex flex-col items-center gap-3 py-24 text-muted-foreground">
              <Shirt className="w-10 h-10" />
              <p>Try adjusting your filters or search term.</p>
              {activeFilterCount > 0 && (
                <Button variant="outline" size="sm" onClick={clearFilters}>
                  Clear filters
                </Button>
              )}
            </div>
          ) : browseMode === "master" ? (
            <div className={gridClass}>
              {kits.map((kit) => (
                <JerseyCard key={kit.kit_id} kit={kit} />
              ))}
            </div>
          ) : (
            <div className={gridClass}>
              {versions.map((v) => (
                <VersionCard
                  key={v.version_id}
                  version={v}
                  onAddToCollection={setQuickAddVersion}
                />
              ))}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
