import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getMasterKits, getFilters, getVersions, addToCollection } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, X, Shirt, LayoutGrid, List, Filter, Plus } from 'lucide-react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import JerseyCard from '@/components/JerseyCard';
import { proxyImageUrl } from '@/lib/api';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

export default function Browse() {
  const { user } = useAuth();
  const [viewMode, setViewMode]       = useState('grid');
  const [browseMode, setBrowseMode]   = useState('master'); // ← toggle master/version
  const [kits, setKits]               = useState([]);
  const [versions, setVersions]       = useState([]);
  const [filters, setFilters]         = useState({ clubs: [], brands: [], seasons: [], kit_types: [], designs: [], leagues: [] });
  const [loading, setLoading]         = useState(true);
  const [addingId, setAddingId]       = useState(null); // version_id en cours d'ajout

  const [search, setSearch]               = useState('');
  const [selectedClub, setSelectedClub]   = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedType, setSelectedType]   = useState('');
  const [selectedSeason, setSelectedSeason] = useState('');
  const [selectedDesign, setSelectedDesign] = useState('');
  const [selectedLeague, setSelectedLeague] = useState('');

  // ── Fetch master kits ──
  const fetchKits = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search)         params.search   = search;
      if (selectedClub)   params.club     = selectedClub;
      if (selectedBrand)  params.brand    = selectedBrand;
      if (selectedType)   params.kit_type = selectedType;
      if (selectedSeason) params.season   = selectedSeason;
      if (selectedDesign) params.design   = selectedDesign;
      if (selectedLeague) params.league   = selectedLeague;
      const res = await getMasterKits(params);
      setKits(res.data);
    } catch (err) {
      console.error('Failed to fetch kits:', err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague]);

  // ── Fetch versions ──
  const fetchVersions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search)         params.search   = search;
      if (selectedClub)   params.club     = selectedClub;
      if (selectedBrand)  params.brand    = selectedBrand;
      if (selectedType)   params.kit_type = selectedType;
      if (selectedSeason) params.season   = selectedSeason;
      if (selectedLeague) params.league   = selectedLeague;
      const res = await getVersions(params);
      setVersions(res.data);
    } catch (err) {
      console.error('Failed to fetch versions:', err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague]);

  useEffect(() => {
    getFilters().then(r => setFilters(r.data)).catch(() => {});
  }, []);

  useEffect(() => {
    if (browseMode === 'master') fetchKits();
    else fetchVersions();
  }, [browseMode, fetchKits, fetchVersions]);

  const clearFilters = () => {
    setSearch(''); setSelectedClub(''); setSelectedBrand('');
    setSelectedType(''); setSelectedSeason(''); setSelectedDesign(''); setSelectedLeague('');
  };

  const activeFilterCount = [selectedClub, selectedBrand, selectedType, selectedSeason, selectedDesign, selectedLeague].filter(Boolean).length;

  // ── Ajouter une version à la collection ──
  const handleAddToCollection = async (version) => {
    if (!user) { toast.error('You must be logged in'); return; }
    setAddingId(version.version_id);
    try {
      await addToCollection({
        version_id:  version.version_id,
        kit_id:      version.kit_id,
        condition:   'Unknown',
        size:        '',
        notes:       '',
      });
      toast.success('New jersey added! 🎽', {
        description: `${version.master_kit?.club || ''} ${version.master_kit?.season || ''} — ${version.competition || ''}`,
        duration: 3000,
      });
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to add jersey');
    } finally {
      setAddingId(null);
    }
  };

  const FilterPanel = () => (
    <div className="space-y-6">
      {/* Toggle Master / Version */}
      <div>
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>
          View
        </p>
        <div className="flex border border-border">
          <button
            onClick={() => setBrowseMode('master')}
            className={`flex-1 py-2 text-xs tracking-wider transition-colors ${browseMode === 'master' ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground hover:text-foreground'}`}
            style={{ fontFamily: 'Barlow Condensed' }}
          >
            MASTER
          </button>
          <button
            onClick={() => setBrowseMode('version')}
            className={`flex-1 py-2 text-xs tracking-wider transition-colors ${browseMode === 'version' ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground hover:text-foreground'}`}
            style={{ fontFamily: 'Barlow Condensed' }}
          >
            VERSION
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="space-y-4">
        {filters.clubs.length > 0 && (
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Club</label>
            <Select value={selectedClub} onValueChange={setSelectedClub}>
              <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="All clubs" /></SelectTrigger>
              <SelectContent className="bg-card border-border max-h-60">
                {filters.clubs.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        )}
        {filters.brands.length > 0 && (
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Brand</label>
            <Select value={selectedBrand} onValueChange={setSelectedBrand}>
              <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="All brands" /></SelectTrigger>
              <SelectContent className="bg-card border-border max-h-60">
                {filters.brands.map(b => <SelectItem key={b} value={b}>{b}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        )}
        {filters.seasons.length > 0 && (
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Season</label>
            <Select value={selectedSeason} onValueChange={setSelectedSeason}>
              <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="All seasons" /></SelectTrigger>
              <SelectContent className="bg-card border-border max-h-60">
                {filters.seasons.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        )}
        {filters.kit_types.length > 0 && (
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Type</label>
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="All types" /></SelectTrigger>
              <SelectContent className="bg-card border-border">
                {filters.kit_types.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        )}
        {filters.leagues?.length > 0 && (
          <div className="space-y-2">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>League</label>
            <Select value={selectedLeague} onValueChange={setSelectedLeague}>
              <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="All leagues" /></SelectTrigger>
              <SelectContent className="bg-card border-border max-h-60">
                {filters.leagues.map(l => <SelectItem key={l} value={l}>{l}</SelectItem>)}
              </SelectContent>
            </Select>
          </div>
        )}
        {activeFilterCount > 0 && (
          <Button variant="outline" onClick={clearFilters} className="w-full rounded-none text-xs">
            <X className="w-3 h-3 mr-1" /> Clear filters ({activeFilterCount})
          </Button>
        )}
      </div>
    </div>
  );

  return (
    <div className="animate-fade-in-up">
      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4">BROWSE</h1>
          <div className="flex gap-2">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search jerseys..."
                className="pl-9 bg-card border-border rounded-none"
              />
              {search && (
                <button onClick={() => setSearch('')} className="absolute right-3 top-1/2 -translate-y-1/2">
                  <X className="w-4 h-4 text-muted-foreground" />
                </button>
              )}
            </div>
            <div className="flex border border-border">
              <button onClick={() => setViewMode('grid')} className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground'}`}>
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button onClick={() => setViewMode('list')} className={`px-3 py-2 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground'}`}>
                <List className="w-4 h-4" />
              </button>
            </div>
            {/* Mobile filter */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" className="lg:hidden rounded-none relative">
                  <Filter className="w-4 h-4" />
                  {activeFilterCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary text-primary-foreground text-[10px] flex items-center justify-center">
                      {activeFilterCount}
                    </span>
                  )}
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="bg-card border-border w-72">
                <SheetHeader><SheetTitle>Filters</SheetTitle></SheetHeader>
                <div className="mt-6"><FilterPanel /></div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 flex gap-8">
        {/* Sidebar desktop */}
        <aside className="hidden lg:block w-56 shrink-0">
          <FilterPanel />
        </aside>

        {/* Main content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-6">
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              {browseMode === 'master' ? kits.length : versions.length} {browseMode === 'master' ? 'master kits' : 'versions'} found
            </p>
            <Badge variant="outline" className="rounded-none text-[10px]">
              {browseMode === 'master' ? 'MASTER VIEW' : 'VERSION VIEW'}
            </Badge>
          </div>

          {loading ? (
            <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2 sm:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
              {[...Array(8)].map((_, i) => <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />)}
            </div>
          ) : browseMode === 'master' ? (
            /* ── MASTER VIEW ── */
            kits.length === 0 ? (
              <div className="text-center py-20 border border-dashed border-border">
                <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No kits found</p>
              </div>
            ) : (
              <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2 sm:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
                {kits.map(kit => (
                  <JerseyCard key={kit.kit_id} kit={kit} viewMode={viewMode} />
                ))}
              </div>
            )
          ) : (
            /* ── VERSION VIEW ── */
            versions.length === 0 ? (
              <div className="text-center py-20 border border-dashed border-border">
                <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No versions found</p>
              </div>
            ) : (
              <div className={`grid gap-4 ${viewMode === 'grid' ? 'grid-cols-2 sm:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}>
                {versions.map(version => (
                  <div key={version.version_id} className="relative group border border-border bg-card hover:border-primary/50 transition-colors">
                    <Link to={`/version/${version.version_id}`}>
                      <div className="aspect-[3/4] overflow-hidden bg-secondary/20">
                        {version.front_photo || version.master_kit?.front_photo ? (
                          <img
                            src={proxyImageUrl(version.front_photo || version.master_kit?.front_photo)}
                            alt={version.master_kit?.club}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Shirt className="w-12 h-12 text-muted-foreground/30" />
                          </div>
                        )}
                      </div>
                      <div className="p-3">
                        <p className="text-xs font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {version.master_kit?.club || '—'}
                        </p>
                        <p className="text-[10px] text-muted-foreground truncate" style={{ fontFamily: 'Barlow Condensed' }}>
                          {version.master_kit?.season} · {version.master_kit?.kit_type}
                        </p>
                        <div className="flex gap-1 mt-1 flex-wrap">
                          {version.competition && (
                            <Badge variant="outline" className="rounded-none text-[9px] px-1">{version.competition}</Badge>
                          )}
                          {version.model && (
                            <Badge variant="outline" className="rounded-none text-[9px] px-1">{version.model}</Badge>
                          )}
                        </div>
                      </div>
                    </Link>

                    {/* ── BOUTON + ── */}
                    <button
                      onClick={() => handleAddToCollection(version)}
                      disabled={addingId === version.version_id}
                      className="absolute top-2 right-2 w-8 h-8 bg-primary text-primary-foreground flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-primary/80 disabled:opacity-50"
                      data-testid={`add-to-collection-${version.version_id}`}
                      title="Add to my collection"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
