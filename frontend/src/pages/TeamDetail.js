// src/pages/TeamDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Shirt, Pencil } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';
import { proxyImageUrl } from '@/lib/api';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export default function TeamDetail() {
  const { id } = useParams(); // slug de la team
  const { user } = useAuth();

  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterBrand, setFilterBrand] = useState('');
  const [showEdit, setShowEdit] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        // Infos de la team
        const teamRes = await fetch(`/api/teams/${id}`);
        if (!teamRes.ok) {
          setTeam(null);
          return;
        }
        const teamData = await teamRes.json();

        // Kits de la team
        const kitsRes = await fetch(`/api/teams/${id}/kits`);
        const kitsData = await kitsRes.json();

        setTeam({
          ...teamData,
          kits: kitsData || [],
        });
      } catch (e) {
        console.error(e);
        setTeam(null);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="animate-fade-in-up px-4 lg:px-8 py-16">
        <div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" />
      </div>
    );
  }

  if (!team) {
    return (
      <div className="px-4 lg:px-8 py-16 text-center">
        <p className="text-muted-foreground">Team not found</p>
      </div>
    );
  }

  const isPending = team.status === 'pending' || team.status === 'for_review';

  const isAdminOrModerator = user && (user.role === 'admin' || user.role === 'moderator');

  const kits = team.kits || [];

  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))]
    .sort()
    .reverse();
  const brands = [...new Set(kits.map(k => k.brand).filter(Boolean))].sort();

  const filteredKits = kits.filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterBrand && k.brand !== filterBrand) return false;
    return true;
  });

  return (
    <div className="animate-fade-in-up" data-testid="team-detail-page">
      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link
            to="/teams"
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4"
            data-testid="back-to-teams"
          >
            <ArrowLeft className="w-3 h-3" />
            Teams
          </Link>

          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-secondary flex items-center justify-center shrink-0">
              {team.crest_url ? (
                <img
                  src={proxyImageUrl(team.crest_url)}
                  alt={team.name}
                  className="w-16 h-16 object-contain"
                />
              ) : (
                <span className="text-xl font-semibold">{team.name[0]}</span>
              )}
            </div>

            <div>
              <h1
                className="text-3xl sm:text-4xl tracking-tighter"
                data-testid="team-name"
              >
                {team.name}
              </h1>

              <div className="flex flex-wrap items-center gap-3 mt-2">
                {team.country && (
                  <span
                    className="text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                  >
                    {team.country}
                  </span>
                )}
                {team.city && (
                  <span
                    className="text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                  >
                    {team.city}
                  </span>
                )}
                {team.founded && (
                  <span
                    className="text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                  >
                    Founded {team.founded}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 mt-3">
                <Badge variant="secondary" className="rounded-none">
                  {team.kit_count || kits.length} kits
                </Badge>

                <Badge
  variant={team.status === 'approved' ? 'secondary' : 'outline'}
  className={`rounded-none text-[10px] uppercase tracking-wider ml-2 ${
    team.status === 'for_review' ? 'border-accent/40 text-accent' : ''
  }`}
>
  {team.status === 'approved' ? 'Approved' : team.status === 'for_review' ? 'For Review' : 'Pending'}
</Badge>


 {isAdminOrModerator && !isPending && (
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="rounded-none border-border ml-2"
          onClick={() => setShowEdit(true)}
          disabled={team?.status !== 'approved'}
          data-testid="suggest-edit-team-btn"
        >
          <Pencil className="w-3 h-3 mr-1" />
          Suggest Edit
        </Button>
      </TooltipTrigger>
      {team?.status !== 'approved' && (
        <TooltipContent>
          <p>Waiting for approval</p>
        </TooltipContent>
      )}
    </Tooltip>
  </TooltipProvider>
)}

                
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Message si pending */}
      {isPending && (
        <div className="max-w-7xl mx-auto px-4 lg:px-8 pt-6">
          <div className="border border-border bg-card p-4 mb-4">
            <p className="text-sm text-muted-foreground">
              This team reference is pending approval with its jersey submission
              and cannot be edited yet. Once the related jersey is approved,
              you will be able to submit correction reports from this page.
            </p>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {/* Filtres */}
        <div className="flex flex-wrap gap-3 mb-6">
          <select
            value={filterSeason}
            onChange={e => setFilterSeason(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="team-filter-season"
          >
            <option value="">All Seasons</option>
            {seasons.map(s => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <select
            value={filterBrand}
            onChange={e => setFilterBrand(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="team-filter-brand"
          >
            <option value="">All Brands</option>
            {brands.map(b => (
              <option key={b} value={b}>
                {b}
              </option>
            ))}
          </select>
        </div>

        {/* Grid de kits */}
        {filteredKits.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p
              className="text-sm text-muted-foreground"
              style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
            >
              No kits found for this team
            </p>
          </div>
        ) : (
          <div
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children"
            data-testid="team-kits-grid"
          >
            {filteredKits.map(kit => (
              <JerseyCard key={kit.kit_id} kit={kit} />
            ))}
          </div>
        )}
      </div>

      {/* Dialog édition entité : seulement si approved */}
      {showEdit && !isPending && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType="team"
          mode="edit"
          entityId={team.team_id}
          initialData={{
            name: team.name,
            country: team.country,
            city: team.city,
            founded: team.founded,
            primary_color: team.primary_color,
            secondary_color: team.secondary_color,
            crest_url: team.crest_url,
          }}
          onSuccess={async () => {
            const res = await fetch(`/api/teams/${id}`);
            if (res.ok) {
              const data = await res.json();
              setTeam(prev => ({ ...(prev || {}), ...data }));
            }
          }}
        />
      )}
    </div>
  );
}
