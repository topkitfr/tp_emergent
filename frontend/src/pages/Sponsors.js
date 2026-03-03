import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getMasterKits } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Tag } from 'lucide-react';

export default function Sponsors() {
  const [sponsors, setSponsors] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState('');

  const fetchSponsors = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMasterKits({ limit: 2000 });
      const kits = res.data;

      // Grouper les kits par sponsor
      const map = {};
      for (const kit of kits) {
        const name = kit.sponsor?.trim();
        if (!name) continue;
        if (!map[name]) map[name] = { name, kit_count: 0, clubs: new Set(), seasons: new Set() };
        map[name].kit_count++;
        if (kit.club)   map[name].clubs.add(kit.club);
        if (kit.season) map[name].seasons.add(kit.season);
      }

      let list = Object.values(map).map(s => ({
        ...s,
        clubs:   [...s.clubs].slice(0, 3),
        seasons: [...s.seasons].sort().reverse(),
      })).sort((a, b) => b.kit_count - a.kit_count);

      if (search) {
        list = list.filter(s => s.name.toLowerCase().includes(search.toLowerCase()));
      }

      setSponsors(list);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    fetchSponsors();
  }, [fetchSponsors]);

  return (
    <div className="animate-fade-in-up">
      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4">SPONSORS</h1>
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search sponsors..."
              className="pl-9 bg-card border-border rounded-none"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          {sponsors.length} sponsor{sponsors.length !== 1 ? 's' : ''} found
        </p>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-28 bg-card animate-pulse border border-border" />
            ))}
          </div>
        ) : sponsors.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-border">
            <Tag className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
              No sponsors found
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {sponsors.map(sponsor => (
              <Link
                key={sponsor.name}
                to={`/database/sponsors/${encodeURIComponent(sponsor.name)}`}
                className="border border-border bg-card hover:border-primary/50 transition-colors p-4 block"
                data-testid={`sponsor-card-${sponsor.name}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <Tag className="w-5 h-5 text-muted-foreground mt-0.5 shrink-0" />
                  <Badge variant="outline" className="rounded-none text-[10px]">
                    {sponsor.kit_count} kit{sponsor.kit_count !== 1 ? 's' : ''}
                  </Badge>
                </div>
                <p
                  className="text-sm font-semibold mb-2 leading-tight"
                  style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                >
                  {sponsor.name}
                </p>
                <div className="flex flex-wrap gap-1">
                  {sponsor.clubs.map(club => (
                    <span
                      key={club}
                      className="text-[10px] text-muted-foreground truncate"
                      style={{ fontFamily: 'Barlow Condensed' }}
                    >
                      {club}
                    </span>
                  ))}
                  {sponsor.clubs.length === 3 && (
                    <span className="text-[10px] text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                      ...
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
