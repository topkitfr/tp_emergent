// frontend/src/pages/database/Sponsors.js
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getSponsors, proxyImageUrl } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Globe } from 'lucide-react';

export default function Sponsors() {
  const [sponsors, setSponsors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchSponsors = useCallback(async () => {
    setLoading(true);
    try {
      const params = { status: 'approved' };
      if (search) params.search = search;
      const res = await getSponsors(params);
      setSponsors(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchSponsors(); }, [fetchSponsors]);

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
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search sponsors..."
              className="pl-9 bg-card border-border rounded-none"
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6">
          {sponsors.length} sponsor{sponsors.length !== 1 ? 's' : ''}
        </p>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-28 bg-card animate-pulse border border-border" />
            ))}
          </div>
        ) : sponsors.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-border">
            <Globe className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No sponsors found</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {sponsors.map((sponsor) => (
              <Link
                key={sponsor.id}
                to={`/sponsors/${sponsor.slug}`}
                className="border border-border bg-card hover:border-primary/50 transition-colors p-4 block"
              >
                <div className="flex items-center gap-3 mb-2">
                  {sponsor.logo_url ? (
                    <img
                      src={proxyImageUrl(sponsor.logo_url)}
                      alt={sponsor.name}
                      className="w-10 h-10 object-contain"
                    />
                  ) : (
                    <div className="w-10 h-10 bg-secondary flex items-center justify-center border border-border">
                      <Globe className="w-5 h-5 text-muted-foreground" />
                    </div>
                  )}
                  <Badge variant="outline" className="rounded-none text-[10px] ml-auto">
                    {sponsor.kit_count || 0} kit{sponsor.kit_count !== 1 ? 's' : ''}
                  </Badge>
                </div>
                <p className="text-sm font-semibold mb-1">{sponsor.name}</p>
                {sponsor.country && (
                  <p className="text-[10px] text-muted-foreground truncate">
                    {sponsor.country}
                  </p>
                )}
                {sponsor.clubs?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {sponsor.clubs.map((club) => (
                      <span key={club} className="text-[10px] text-muted-foreground truncate">
                        {club}
                      </span>
                    ))}
                    {sponsor.clubs?.length > 3 && <span className="text-[10px] text-muted-foreground">...</span>}
                  </div>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
