import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMasterKits, proxyImageUrl } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tag, ArrowLeft, Shirt } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';

export default function SponsorDetail() {
  const { name } = useParams(); // encodé dans l’URL
  const decodedName = decodeURIComponent(name || '');
  const [kits, setKits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam, setFilterTeam] = useState('');

  useEffect(() => {
    const fetch = async () => {
      setLoading(true);
      try {
        // on récupère tous les kits puis on filtre par sponsor côté front
        const res = await getMasterKits({ limit: 2000 });
        const allKits = res.data || [];
        const sponsorKits = allKits.filter(
          k => (k.sponsor || '').trim().toLowerCase() === decodedName.trim().toLowerCase()
        );
        setKits(sponsorKits);
      } catch (e) {
        console.error(e);
        setKits([]);
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [decodedName]);

  if (loading) {
    return (
      <div className="animate-fade-in-up px-4 lg:px-8 py-16">
        <div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" />
      </div>
    );
  }

  if (!kits.length) {
    return (
      <div className="px-4 lg:px-8 py-16 text-center">
        <Link
          to="/database/sponsors"
          className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4"
        >
          <ArrowLeft className="w-3 h-3" /> Sponsors
        </Link>
        <p className="text-muted-foreground">No kits found for this sponsor.</p>
      </div>
    );
  }

  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teamNames = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  const filteredKits = kits.filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterTeam && k.club !== filterTeam) return false;
    return true;
  });

  return (
    <div className="animate-fade-in-up" data-testid="sponsor-detail-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link
            to="/database/sponsors"
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4"
            data-testid="back-to-sponsors"
          >
            <ArrowLeft className="w-3 h-3" /> Sponsors
          </Link>
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-secondary flex items-center justify-center shrink-0">
              <Tag className="w-10 h-10 text-muted-foreground" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter" data-testid="sponsor-name">
                {decodedName}
              </h1>
              <div className="flex items-center gap-2 mt-3">
                <Badge variant="secondary" className="rounded-none">
                  {kits.length} kit{kits.length !== 1 ? 's' : ''}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="flex flex-wrap gap-3 mb-6">
          <select
            value={filterSeason}
            onChange={e => setFilterSeason(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="sponsor-filter-season"
          >
            <option value="">All Seasons</option>
            {seasons.map(s => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <select
            value={filterTeam}
            onChange={e => setFilterTeam(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="sponsor-filter-team"
          >
            <option value="">All Teams</option>
            {teamNames.map(t => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {filteredKits.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p
              className="text-sm text-muted-foreground"
              style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
            >
              No kits match these filters
            </p>
          </div>
        ) : (
          <div
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children"
            data-testid="sponsor-kits-grid"
          >
            {filteredKits.map(kit => (
              <JerseyCard key={kit.kit_id} kit={kit} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
