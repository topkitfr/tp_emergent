import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getPlayers } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, User, Globe } from 'lucide-react';

export default function Players() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [nationality, setNationality] = useState('');

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (nationality) params.nationality = nationality;
      const res = await getPlayers(params);
      setPlayers(res.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  }, [search, nationality]);

  useEffect(() => { fetchPlayers(); }, [fetchPlayers]);

  const nationalities = [...new Set(players.map(p => p.nationality).filter(Boolean))].sort();

  return (
    <div className="animate-fade-in-up" data-testid="players-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="players-title">PLAYERS</h1>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search players..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9 bg-card border-border rounded-none h-10" data-testid="players-search" />
            </div>
            {nationalities.length > 0 && (
              <select value={nationality} onChange={e => setNationality(e.target.value)} className="h-10 px-3 bg-card border border-border rounded-none text-sm" data-testid="players-nationality-filter">
                <option value="">All Nationalities</option>
                {nationalities.map(n => <option key={n} value={n}>{n}</option>)}
              </select>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6"><span className="font-mono text-foreground">{players.length}</span> players</p>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-24 bg-card animate-pulse border border-border" />)}
          </div>
        ) : players.length === 0 ? (
          <div className="text-center py-20">
            <User className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl tracking-tight mb-2">NO PLAYERS FOUND</h3>
            <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Players are added when linked to jersey versions</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="players-grid">
            {players.map(player => (
              <Link to={`/players/${player.slug || player.player_id}`} key={player.player_id}>
                <div className="border border-border bg-card p-5 hover:border-primary/30 group flex items-start gap-4" style={{ transition: 'border-color 0.2s' }} data-testid={`player-card-${player.player_id}`}>
                  <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0 rounded-full overflow-hidden">
                    {player.photo_url ? <img src={player.photo_url} alt={player.full_name} className="w-12 h-12 object-cover" /> : <User className="w-6 h-6 text-muted-foreground" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary" style={{ transition: 'color 0.2s' }}>{player.full_name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      {player.nationality && <span className="text-xs text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Globe className="w-3 h-3" /> {player.nationality}</span>}
                      {player.preferred_number && <span className="text-xs font-mono text-primary">#{player.preferred_number}</span>}
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      {player.positions?.length > 0 && player.positions.map(p => <Badge key={p} variant="outline" className="rounded-none text-[10px]">{p}</Badge>)}
                      <Badge variant="secondary" className="rounded-none text-[10px]">{player.kit_count} versions</Badge>
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
