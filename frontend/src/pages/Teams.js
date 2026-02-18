import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getTeams } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Shield, MapPin } from 'lucide-react';

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');

  const fetchTeams = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (country) params.country = country;
      const res = await getTeams(params);
      setTeams(res.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  }, [search, country]);

  useEffect(() => { fetchTeams(); }, [fetchTeams]);

  const countries = [...new Set(teams.map(t => t.country).filter(Boolean))].sort();

  return (
    <div className="animate-fade-in-up" data-testid="teams-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="teams-title">TEAMS</h1>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search teams..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="pl-9 bg-card border-border rounded-none h-10"
                data-testid="teams-search"
              />
            </div>
            {countries.length > 0 && (
              <select
                value={country}
                onChange={e => setCountry(e.target.value)}
                className="h-10 px-3 bg-card border border-border rounded-none text-sm"
                data-testid="teams-country-filter"
              >
                <option value="">All Countries</option>
                {countries.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6">
          <span className="font-mono text-foreground">{teams.length}</span> teams
        </p>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-24 bg-card animate-pulse border border-border" />)}
          </div>
        ) : teams.length === 0 ? (
          <div className="text-center py-20">
            <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl tracking-tight mb-2">NO TEAMS FOUND</h3>
            <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Try a different search</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="teams-grid">
            {teams.map(team => (
              <Link to={`/teams/${team.slug || team.team_id}`} key={team.team_id}>
                <div className="border border-border bg-card p-5 hover:border-primary/30 group flex items-start gap-4" style={{ transition: 'border-color 0.2s' }} data-testid={`team-card-${team.team_id}`}>
                  <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0">
                    {team.crest_url ? (
                      <img src={team.crest_url} alt={team.name} className="w-10 h-10 object-contain" />
                    ) : (
                      <Shield className="w-6 h-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary" style={{ transition: 'color 0.2s' }}>{team.name}</h3>
                    {team.country && (
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                        <MapPin className="w-3 h-3" /> {team.country}
                      </p>
                    )}
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="rounded-none text-[10px]">{team.kit_count} kits</Badge>
                      {team.founded && <span className="text-[10px] font-mono text-muted-foreground">Est. {team.founded}</span>}
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
