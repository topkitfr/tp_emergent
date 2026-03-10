// frontend/src/pages/Leagues.js
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getLeagues, proxyImageUrl } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Globe } from 'lucide-react';

export default function Leagues() {
  const [leagues, setLeagues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchLeagues = useCallback(async () => {
    setLoading(true);
    try {
      const params = { status: 'approved' }; // Filtre par défaut
      if (search) params.search = search;
      const res = await getLeagues(params);
      setLeagues(res.data);
    } catch (err) {
      console.error("Failed to fetch leagues:", err);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchLeagues(); }, [fetchLeagues]);

  return (
    <div className="animate-fade-in-up" data-testid="leagues-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="leagues-title">LEAGUES</h1>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search leagues..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-card border-border rounded-none h-10"
              data-testid="leagues-search"
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6">
          <span className="font-mono text-foreground">{leagues.length}</span> leagues
        </p>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-24 bg-card animate-pulse border border-border" />)}
          </div>
        ) : leagues.length === 0 ? (
          <div className="text-center py-20">
            <Globe className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl tracking-tight mb-2">NO LEAGUES FOUND</h3>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="leagues-grid">
            {leagues.map(league => (
              <Link to={`/leagues/${league.slug || league.league_id}`} key={league.league_id}>
                <div className="border border-border bg-card p-5 hover:border-primary/30 group flex items-start gap-4" style={{ transition: 'border-color 0.2s' }} data-testid={`league-card-${league.league_id}`}>
                  <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0">
                    {league.logo_url ? (
                      <img src={proxyImageUrl(league.logo_url)} alt={league.name} className="w-10 h-10 object-contain" />
                    ) : (
                      <Globe className="w-6 h-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary" style={{ transition: 'color 0.2s' }}>{league.name}</h3>
                    {league.country_or_region && (
                      <p className="text-xs text-muted-foreground mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                        {league.country_or_region}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="rounded-none text-[10px]">{league.kit_count || 0} kits</Badge>
                      {league.level && <span className="text-[10px] font-mono text-muted-foreground">{league.level}</span>}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
