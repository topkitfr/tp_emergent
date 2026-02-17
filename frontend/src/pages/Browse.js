import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getMasterKits, getFilters } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, X, Shirt, Star, LayoutGrid, List, Filter } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import JerseyCard from '@/components/JerseyCard';

export default function Browse() {
  const [kits, setKits] = useState([]);
  const [filters, setFilters] = useState({ clubs: [], brands: [], seasons: [], years: [], kit_types: [], designs: [], leagues: [] });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedClub, setSelectedClub] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedDesign, setSelectedDesign] = useState('');
  const [selectedLeague, setSelectedLeague] = useState('');
  const [viewMode, setViewMode] = useState('grid');

  const fetchKits = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (selectedClub) params.club = selectedClub;
      if (selectedBrand) params.brand = selectedBrand;
      if (selectedType) params.kit_type = selectedType;
      if (selectedYear) params.year = parseInt(selectedYear);
      if (selectedDesign) params.design = selectedDesign;
      if (selectedLeague) params.league = selectedLeague;
      const res = await getMasterKits(params);
      setKits(res.data);
    } catch (err) {
      console.error('Failed to fetch kits:', err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedClub, selectedBrand, selectedType, selectedYear, selectedDesign, selectedLeague]);

  useEffect(() => {
    getFilters().then(r => setFilters(r.data)).catch(() => {});
    fetchKits();
  }, [fetchKits]);

  const clearFilters = () => {
    setSearch('');
    setSelectedClub('');
    setSelectedBrand('');
    setSelectedType('');
    setSelectedYear('');
    setSelectedDesign('');
    setSelectedLeague('');
  };

  const activeFilterCount = [selectedClub, selectedBrand, selectedType, selectedYear, selectedDesign, selectedLeague].filter(Boolean).length;

  const FilterPanel = () => (
    <div className="space-y-6">
      <div>
        <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Club</label>
        <Select value={selectedClub} onValueChange={setSelectedClub}>
          <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-club">
            <SelectValue placeholder="All Clubs" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {filters.clubs.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Brand</label>
        <Select value={selectedBrand} onValueChange={setSelectedBrand}>
          <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-brand">
            <SelectValue placeholder="All Brands" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {filters.brands.map(b => <SelectItem key={b} value={b}>{b}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Type</label>
        <Select value={selectedType} onValueChange={setSelectedType}>
          <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-type">
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {filters.kit_types.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Year</label>
        <Select value={selectedYear} onValueChange={setSelectedYear}>
          <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-year">
            <SelectValue placeholder="All Years" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {filters.years.map(y => <SelectItem key={y} value={String(y)}>{y}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      <div>
        <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Design</label>
        <Select value={selectedDesign} onValueChange={setSelectedDesign}>
          <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-design">
            <SelectValue placeholder="All Designs" />
          </SelectTrigger>
          <SelectContent className="bg-card border-border">
            {filters.designs?.map(d => <SelectItem key={d} value={d}>{d}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>
      {filters.leagues?.length > 0 && (
        <div>
          <label className="text-xs text-muted-foreground uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>League</label>
          <Select value={selectedLeague} onValueChange={setSelectedLeague}>
            <SelectTrigger className="bg-card border-border rounded-none" data-testid="filter-league">
              <SelectValue placeholder="All Leagues" />
            </SelectTrigger>
            <SelectContent className="bg-card border-border">
              {filters.leagues.map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
      )}
      {activeFilterCount > 0 && (
        <Button variant="outline" size="sm" onClick={clearFilters} className="w-full rounded-none border-border" data-testid="clear-filters-btn">
          <X className="w-3 h-3 mr-1" /> Clear Filters
        </Button>
      )}
    </div>
  );

  return (
    <div className="animate-fade-in-up">
      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="browse-title">
            BROWSE CATALOG
          </h1>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search clubs, brands, seasons..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9 bg-card border-border rounded-none h-10"
                data-testid="search-input"
              />
            </div>
            <div className="flex items-center gap-2">
              {/* Mobile filter */}
              <div className="md:hidden">
                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="outline" size="sm" className="rounded-none border-border relative" data-testid="mobile-filter-btn">
                      <Filter className="w-4 h-4 mr-1" /> Filters
                      {activeFilterCount > 0 && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary text-primary-foreground text-[10px] flex items-center justify-center rounded-full">
                          {activeFilterCount}
                        </span>
                      )}
                    </Button>
                  </SheetTrigger>
                  <SheetContent side="left" className="bg-background border-border">
                    <SheetHeader>
                      <SheetTitle className="text-left">Filters</SheetTitle>
                    </SheetHeader>
                    <div className="mt-6">
                      <FilterPanel />
                    </div>
                  </SheetContent>
                </Sheet>
              </div>
              <div className="flex items-center border border-border">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                  data-testid="view-grid-btn"
                >
                  <LayoutGrid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'}`}
                  data-testid="view-list-btn"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          {activeFilterCount > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {selectedClub && <Badge variant="secondary" className="rounded-none text-xs">{selectedClub} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedClub('')} /></Badge>}
              {selectedBrand && <Badge variant="secondary" className="rounded-none text-xs">{selectedBrand} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedBrand('')} /></Badge>}
              {selectedType && <Badge variant="secondary" className="rounded-none text-xs">{selectedType} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedType('')} /></Badge>}
              {selectedYear && <Badge variant="secondary" className="rounded-none text-xs">{selectedYear} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedYear('')} /></Badge>}
              {selectedDesign && <Badge variant="secondary" className="rounded-none text-xs">{selectedDesign} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedDesign('')} /></Badge>}
              {selectedLeague && <Badge variant="secondary" className="rounded-none text-xs">{selectedLeague} <X className="w-3 h-3 ml-1 cursor-pointer" onClick={() => setSelectedLeague('')} /></Badge>}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Desktop filter sidebar */}
          <aside className="hidden md:block w-56 shrink-0 sticky top-20 self-start" data-testid="filter-sidebar">
            <h3 className="text-xs text-muted-foreground uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>
              Filters
            </h3>
            <FilterPanel />
          </aside>

          {/* Results */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-6">
              <p className="text-sm text-muted-foreground">
                <span className="font-mono text-foreground">{kits.length}</span> kits found
              </p>
            </div>

            {loading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />
                ))}
              </div>
            ) : kits.length === 0 ? (
              <div className="text-center py-20">
                <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl tracking-tight mb-2">NO KITS FOUND</h3>
                <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                  Try adjusting your filters or search term
                </p>
              </div>
            ) : viewMode === 'grid' ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children" data-testid="kits-grid">
                {kits.map(kit => (
                  <JerseyCard key={kit.kit_id} kit={kit} />
                ))}
              </div>
            ) : (
              <div className="space-y-2 stagger-children" data-testid="kits-list">
                {kits.map(kit => (
                  <Link to={`/kit/${kit.kit_id}`} key={kit.kit_id}>
                    <div className="flex items-center gap-4 p-3 border border-border bg-card hover:border-primary/30 group" data-testid={`kit-list-item-${kit.kit_id}`} style={{ transition: 'border-color 0.2s ease' }}>
                      <img src={kit.front_photo} alt={kit.club} className="w-16 h-20 object-cover" />
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold tracking-tight truncate">{kit.club}</h3>
                        <p className="text-xs text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>{kit.season} - {kit.kit_type}</p>
                      </div>
                      <Badge variant="outline" className="rounded-none text-xs shrink-0">{kit.brand}</Badge>
                      {kit.avg_rating > 0 && (
                        <div className="flex items-center gap-1 text-xs text-accent">
                          <Star className="w-3 h-3 fill-current" />
                          {kit.avg_rating}
                        </div>
                      )}
                      <span className="font-mono text-xs text-muted-foreground">{kit.version_count}v</span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
