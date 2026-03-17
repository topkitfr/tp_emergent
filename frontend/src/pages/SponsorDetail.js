import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMasterKits, proxyImageUrl } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tag, ArrowLeft, Shirt, Pencil } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

export default function SponsorDetail() {
  const { name } = useParams();
  const decodedName = decodeURIComponent(name || '');
const { user } = useAuth();

  const [sponsor, setSponsor]           = useState(null);
  const [kits, setKits]                 = useState([]);
  const [loading, setLoading]           = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam, setFilterTeam]     = useState('');
  const [showEdit, setShowEdit]         = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const slug = decodedName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
        const sRes = await fetch(`/api/sponsors/${slug}`);
        const sData = sRes.ok ? await sRes.json() : null;
        setSponsor(sData);

        const kRes = await getMasterKits({ limit: 2000 });
        const allKits = kRes.data || [];
        setKits(allKits.filter(
          k => (k.sponsor || '').trim().toLowerCase() === decodedName.trim().toLowerCase()
        ));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [decodedName]);

  if (loading) return (
    <div className="animate-fade-in-up px-4 lg:px-8 py-16">
      <div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" />
    </div>
  );

  if (!sponsor && !kits.length) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <Link to="/database/sponsors" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4">
        <ArrowLeft className="w-3 h-3" /> Sponsors
      </Link>
      <p className="text-muted-foreground">Sponsor not found.</p>
    </div>
  );

  const isPending    = sponsor?.status === 'pending' || sponsor?.status === 'for_review';
  const isAdminOrMod = user && (user.role === 'admin' || user.role === 'moderator');
  const seasons      = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teamNames    = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();
  const filteredKits = kits.filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterTeam   && k.club   !== filterTeam)   return false;
    return true;
  });

  return (
    <div className="animate-fade-in-up" data-testid="sponsor-detail-page">

      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link to="/database/sponsors"
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4"
            data-testid="back-to-sponsors">
            <ArrowLeft className="w-3 h-3" /> Sponsors
          </Link>

          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-secondary flex items-center justify-center shrink-0">
              {sponsor?.logo_url
                ? <img src={proxyImageUrl(sponsor.logo_url)} alt={decodedName} className="w-16 h-16 object-contain" />
                : <Tag className="w-10 h-10 text-muted-foreground" />
              }
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter" data-testid="sponsor-name">
                {sponsor?.name || decodedName}
              </h1>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                {sponsor?.country && (
                  <span className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {sponsor.country}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2 mt-3">
                <Badge variant="secondary" className="rounded-none">
                  {kits.length} kit{kits.length !== 1 ? 's' : ''}
                </Badge>
                {sponsor?.status && (
                  <Badge
                    variant={sponsor.status === 'approved' ? 'secondary' : 'outline'}
                    className={`rounded-none text-[10px] uppercase tracking-wider ml-2 ${isPending ? 'border-accent/40 text-accent' : ''}`}
                  >
                    {sponsor.status === 'for_review' ? 'For Review' : sponsor.status}
                  </Badge>
                )}

                {/* Bouton Suggest Edit */}
                {isAdminOrMod && !isPending && (
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button
                          variant="outline" size="sm"
                          className="rounded-none border-border ml-2"
                          onClick={() => setShowEdit(true)}
                          data-testid="suggest-edit-sponsor-btn"
                        >
                          <Pencil className="w-3 h-3 mr-1" /> Suggest Edit
                        </Button>
                      </TooltipTrigger>
                    </Tooltip>
                  </TooltipProvider>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Message pending */}
      {isPending && (
        <div className="max-w-7xl mx-auto px-4 lg:px-8 pt-6">
          <div className="border border-border bg-card p-4 mb-4">
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              This sponsor reference is pending approval with its jersey submission and cannot be edited yet.
            </p>
          </div>
        </div>
      )}

      {/* Filtres + grille */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="flex flex-wrap gap-3 mb-6">
          <select value={filterSeason} onChange={e => setFilterSeason(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="sponsor-filter-season">
            <option value="">All Seasons</option>
            {seasons.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select value={filterTeam} onChange={e => setFilterTeam(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="sponsor-filter-team">
            <option value="">All Teams</option>
            {teamNames.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {filteredKits.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              No kits match these filters
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children"
            data-testid="sponsor-kits-grid">
            {filteredKits.map(kit => <JerseyCard key={kit.kit_id} kit={kit} />)}
          </div>
        )}
      </div>

      {/* Dialog Edit */}
      {showEdit && !isPending && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType="sponsor"
          mode="edit"
          entityId={sponsor?.sponsor_id || null}
          initialData={{
            name:    sponsor?.name    || decodedName,
            country: sponsor?.country || '',
          }}
          onSuccess={async () => {
            const slug = decodedName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
            const res = await fetch(`/api/sponsors/${slug}`);
            if (res.ok) setSponsor(await res.json());
          }}
        />
      )}
    </div>
  );
}
