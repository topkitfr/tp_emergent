import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTeam } from '@/lib/api';
import { proxyImageUrl } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Shield, MapPin, Calendar, ArrowLeft, Shirt } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';

export default function TeamDetail() {
  const { id } = useParams();
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterBrand, setFilterBrand] = useState('');

  useEffect(() => {
    setLoading(true);
    getTeam(id).then(r => setTeam(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-fade-in-up px-4 lg:px-8 py-16"><div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" /></div>;
  if (!team) return <div className="px-4 lg:px-8 py-16 text-center"><p className="text-muted-foreground">Team not found</p></div>;

  const kits = team.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const types = [...new Set(kits.map(k => k.kit_type).filter(Boolean))].sort();
  const brands = [...new Set(kits.map(k => k.brand).filter(Boolean))].sort();

  const filteredKits = kits.filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterType && k.kit_type !== filterType) return false;
    if (filterBrand && k.brand !== filterBrand) return false;
    return true;
  });

  return (
    <div className="animate-fade-in-up" data-testid="team-detail-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link to="/teams" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4" data-testid="back-to-teams">
            <ArrowLeft className="w-3 h-3" /> Teams
          </Link>
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-secondary flex items-center justify-center shrink-0">
              {team.crest_url ? <img src={team.crest_url} alt={team.name} className="w-16 h-16 object-contain" /> : <Shield className="w-10 h-10 text-muted-foreground" />}
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter" data-testid="team-name">{team.name}</h1>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                {team.country && <span className="text-sm text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><MapPin className="w-3 h-3" /> {team.country}{team.city ? `, ${team.city}` : ''}</span>}
                {team.founded && <span className="text-sm text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Calendar className="w-3 h-3" /> Founded {team.founded}</span>}
              </div>
              <div className="flex items-center gap-2 mt-3">
                <Badge variant="secondary" className="rounded-none">{team.kit_count} kits</Badge>
                {team.primary_color && <div className="w-4 h-4 border border-border" style={{ backgroundColor: team.primary_color }} />}
                {team.secondary_color && <div className="w-4 h-4 border border-border" style={{ backgroundColor: team.secondary_color }} />}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="flex flex-wrap gap-3 mb-6">
          <select value={filterSeason} onChange={e => setFilterSeason(e.target.value)} className="h-9 px-3 bg-card border border-border rounded-none text-sm" data-testid="team-filter-season">
            <option value="">All Seasons</option>
            {seasons.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={filterType} onChange={e => setFilterType(e.target.value)} className="h-9 px-3 bg-card border border-border rounded-none text-sm" data-testid="team-filter-type">
            <option value="">All Types</option>
            {types.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={filterBrand} onChange={e => setFilterBrand(e.target.value)} className="h-9 px-3 bg-card border border-border rounded-none text-sm" data-testid="team-filter-brand">
            <option value="">All Brands</option>
            {brands.map(b => <option key={b} value={b}>{b}</option>)}
          </select>
        </div>

        {filteredKits.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No kits found for this team</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children" data-testid="team-kits-grid">
            {filteredKits.map(kit => <JerseyCard key={kit.kit_id} kit={kit} />)}
          </div>
        )}
      </div>
    </div>
  );
}
