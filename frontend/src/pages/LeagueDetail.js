// src/pages/LeagueDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getLeague, proxyImageUrl } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Trophy, Globe, ArrowLeft, Shirt, Pencil } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';

export default function LeagueDetail() {
  const { id } = useParams(); // "ligue-1"
  const { user } = useAuth();

  const [league, setLeague] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam, setFilterTeam] = useState('');
  const [showEdit, setShowEdit] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        // 1) league
        const leagueRes = await getLeague(id);

        // 2) kits de la league
        const kitsRes = await fetch(`/api/leagues/${id}/kits`);
        const kitsData = await kitsRes.json();

        const leagueWithKits = {
          ...leagueRes.data,
          kits: kitsData || [],
        };
        setLeague(leagueWithKits);
      } catch (e) {
        console.error(e);
        setLeague(null);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!league) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <p>League not found</p>
        </div>
      </div>
    );
  }

  const isPending = league.status === 'pending';
  const isAdminOrModerator = user && (user.role === 'admin' || user.role === 'moderator');

  const seasons = Array.from(
    new Set((league.kits || []).map(k => k.season).filter(Boolean))
  )
    .sort()
    .reverse();

  const teams = Array.from(
    new Set((league.kits || []).map(k => k.club).filter(Boolean))
  ).sort();

  const filteredKits = (league.kits || []).filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterTeam && k.club !== filterTeam) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-6">
          <Link
            to="/database/leagues"
            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to leagues
          </Link>

          {isAdminOrModerator && !isPending && (
            <Button
              size="sm"
              variant="outline"
              className="rounded-none"
              onClick={() => setShowEdit(true)}
            >
              <Pencil className="w-4 h-4 mr-2" />
              Suggest edit
            </Button>
          )}
        </div>

        {/* League header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1
              className="text-2xl font-black uppercase mb-1"
              style={{ fontFamily: 'Barlow Condensed, sans-serif' }}
            >
              {league.name}
            </h1>
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className="rounded-none text-[10px] uppercase tracking-wider"
              >
                League
              </Badge>
              <Badge
                variant={isPending ? 'outline' : 'secondary'}
                className="rounded-none text-[10px] uppercase tracking-wider"
              >
                {isPending ? 'Pending' : 'Approved'}
              </Badge>
              {league.country_or_region && (
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Globe className="w-3 h-3" />
                  {league.country_or_region}
                </span>
              )}
              {league.level && (
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Trophy className="w-3 h-3" />
                  {league.level}
                </span>
              )}
            </div>
          </div>

          {league.logo && (
            <div className="w-16 h-16 bg-card border border-border flex items-center justify-center">
              <img
                src={proxyImageUrl(league.logo)}
                alt={league.name}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}
        </div>

        {/* Message si pending */}
        {isPending && (
          <div className="mb-8 border border-border bg-card p-4">
            <p className="text-sm text-muted-foreground">
              This league reference is pending approval with its jersey submission
              and cannot be edited yet. Once the related jersey is approved,
              you will be able to submit correction reports from this page.
            </p>
          </div>
        )}

        {/* Filtres + kits */}
        <div className="mb-4 flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-muted-foreground">
              Filter by season
            </span>
            <select
              className="bg-card border border-border text-xs px-2 py-1 rounded-none"
              value={filterSeason}
              onChange={e => setFilterSeason(e.target.value)}
            >
              <option value="">All</option>
              {seasons.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-muted-foreground">
              Filter by club
            </span>
            <select
              className="bg-card border border-border text-xs px-2 py-1 rounded-none"
              value={filterTeam}
              onChange={e => setFilterTeam(e.target.value)}
            >
              <option value="">All</option>
              {teams.map(t => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-8">
          <h2
            className="text-sm uppercase tracking-wider text-muted-foreground mb-2"
            style={{ fontFamily: 'Barlow Condensed, sans-serif' }}
          >
            <Shirt className="w-4 h-4 inline mr-1" /> Kits
          </h2>
          {filteredKits.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No kits found for this league with current filters.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <JerseyCard key={kit.kit_id} kit={kit} />
              ))}
            </div>
          )}
        </div>

        {/* Dialog d'édition uniquement si league approuvée */}
        {showEdit && !isPending && (
          <EntityEditDialog
            entityType="league"
            entity={league}
            open={showEdit}
            onOpenChange={setShowEdit}
          />
        )}
      </div>
    </div>
  );
}
