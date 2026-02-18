import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getLeagues } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Trophy, Globe } from 'lucide-react';

export default function Leagues() {
  const [leagues, setLeagues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState('');

  const fetchLeagues = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (level) params.level = level;
      const res = await getLeagues(params);
      setLeagues(res.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  }, [search, level]);

  useEffect(() => { fetchLeagues(); }, [fetchLeagues]);

  return (
    <div className="animate-fade-in-up" data-testid="leagues-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="leagues-title">LEAGUES</h1>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search leagues..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9 bg-card border-border rounded-none h-10" data-testid="leagues-search" />
            </div>
            <select value={level} onChange={e => setLevel(e.target.value)} className="h-10 px-3 bg-card border border-border rounded-none text-sm" data-testid="leagues-level-filter">
              <option value="">All Levels</option>
              <option value="domestic">Domestic</option>
              <option value="continental">Continental</option>
              <option value="international">International</option>
              <option value="cup">Cup</option>
            </select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6"><span className="font-mono text-foreground">{leagues.length}</span> leagues</p>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-24 bg-card animate-pulse border border-border" />)}
          </div>
        ) : leagues.length === 0 ? (
          <div className="text-center py-20">
            <Trophy className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl tracking-tight mb-2">NO LEAGUES FOUND</h3>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="leagues-grid">
            {leagues.map(league => (
              <Link to={`/leagues/${league.slug || league.league_id}`} key={league.league_id}>
                <div className="border border-border bg-card p-5 hover:border-primary/30 group flex items-start gap-4" style={{ transition: 'border-color 0.2s' }} data-testid={`league-card-${league.league_id}`}>
                  <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0">
                    {league.logo_url ? <img src={league.logo_url} alt={league.name} className="w-10 h-10 object-contain" /> : <Trophy className="w-6 h-6 text-muted-foreground" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary" style={{ transition: 'color 0.2s' }}>{league.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {league.country_or_region && <span className="text-xs text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Globe className="w-3 h-3" /> {league.country_or_region}</span>}
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="rounded-none text-[10px]">{league.kit_count} kits</Badge>
                      <Badge variant="outline" className="rounded-none text-[10px]">{league.level}</Badge>
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
