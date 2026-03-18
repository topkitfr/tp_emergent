// frontend/src/pages/PlayerDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Globe, Calendar, Shirt } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Pencil } from 'lucide-react';
import { getPlayer, proxyImageUrl } from '@/lib/api';
import EntityEditDialog from '@/components/EntityEditDialog';
import { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { useAuth } from '@/contexts/AuthContext';

export default function PlayerDetail() {
  const { id } = useParams();
  const { user: authUser } = useAuth();
  const [player, setPlayer]     = useState(null);
  const [loading, setLoading]   = useState(true);
  const [showEdit, setShowEdit] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    getPlayer(id)
      .then(r => setPlayer(r.data))
      .catch(() => setPlayer(null))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;
  if (!player) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Player not found</p>
    </div>
  );

  const isPending = player.status === 'pending' || player.status === 'for_review';
  const canEdit   = !!authUser;

  // Déduplique les MasterKits depuis les versions floquées, groupés par équipe
  const versions = player.versions || [];
  const kitsSeen = new Set();
  const byTeam   = {};
  for (const v of versions) {
    const kit = v.master_kit;
    if (!kit || kitsSeen.has(kit.kit_id)) continue;
    kitsSeen.add(kit.kit_id);
    const teamName = kit.club || 'Unknown';
    if (!byTeam[teamName]) byTeam[teamName] = [];
    byTeam[teamName].push({ ...kit, version_id: v.version_id });
  }
  for (const team of Object.keys(byTeam)) {
    byTeam[team].sort((a, b) => (b.season || '').localeCompare(a.season || ''));
  }

  const kitCount = kitsSeen.size;

  return (
    <div className="animate-fade-in-up" data-testid="player-detail-page">

      {/* ── Header ── */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">

          <Link
            to="/players"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground mb-5 transition-colors"
            data-testid="back-to-players"
          >
            <ArrowLeft className="w-3 h-3" />
            Players
          </Link>

          <div className="flex flex-col sm:flex-row items-start gap-6">
            {/* Photo */}
            <div className="shrink-0 rounded-full bg-secondary flex items-center justify-center overflow-hidden border border-border w-24 h-24">
              {player.photo_url
                ? <img src={proxyImageUrl(player.photo_url)} alt={player.full_name} className="w-24 h-24 object-cover rounded-full" />
                : <User className="w-10 h-10 text-muted-foreground" />
              }
            </div>

            {/* Infos */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  {isPending && (
                    <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent mb-2">
                      PENDING APPROVAL
                    </Badge>
                  )}
                  <h1 className="text-3xl sm:text-4xl tracking-tighter break-words" data-testid="player-name">
                    {player.full_name}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {player.nationality && (
                      <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{player.nationality}</span>
                    )}
                    {(player.birth_date || player.birth_year) && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {player.birth_date || `Born ${player.birth_year}`}
                      </span>
                    )}
                    {player.preferred_number && (
                      <span className="font-mono text-primary">#{player.preferred_number}</span>
                    )}
                  </div>
                  {player.bio && (
                    <p className="mt-2 text-sm text-muted-foreground max-w-lg" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                      {player.bio}
                    </p>
                  )}
                </div>

                {canEdit && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowEdit(true)}
                    className="rounded-none border-border hover:border-primary/50 shrink-0"
                    data-testid="suggest-edit-player-btn"
                  >
                    <Pencil className="w-3 h-3 mr-1.5" />
                    Suggest Edit
                  </Button>
                )}
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mt-3">
                {player.positions?.map(p => (
                  <Badge key={p} variant="outline" className="rounded-none">{p}</Badge>
                ))}
                <Badge variant="secondary" className="rounded-none">
                  {kitCount} kit{kitCount !== 1 ? 's' : ''}
                </Badge>
                <Badge
                  variant={player.status === 'approved' ? 'secondary' : 'outline'}
                  className={`rounded-none text-[10px] uppercase tracking-wider ${
                    player.status === 'for_review' ? 'border-accent/40 text-accent' : ''
                  }`}
                >
                  {player.status === 'approved' ? 'Approved' : player.status === 'for_review' ? 'For Review' : 'Pending'}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Career in shirts ── */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <h2 className="text-lg tracking-tighter mb-6">CAREER IN SHIRTS</h2>

        {kitCount === 0 ? (
          <div className="text-center py-16 border border-dashed border-border">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              No jersey linked to this player yet
            </p>
          </div>
        ) : (
          <div className="space-y-8" data-testid="player-career">
            {Object.entries(byTeam).map(([teamName, kits]) => (
              <div key={teamName}>
                <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-3"
                  style={{ fontFamily: 'Barlow Condensed' }}>
                  {teamName}
                </h3>
                <div className="space-y-2">
                  {kits.map(kit => (
                    <Link to={`/kit/${kit.kit_id}`} key={kit.kit_id}>
                      <div
                        className="flex items-center gap-4 p-3 border border-border bg-card hover:border-primary/30 transition-colors duration-200"
                        data-testid={`career-kit-${kit.kit_id}`}
                      >
                        <img
                          src={proxyImageUrl(kit.front_photo)}
                          alt=""
                          className="w-12 h-16 object-cover border border-border"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {kit.season} — {kit.kit_type}
                          </p>
                          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {kit.league || ''}
                          </p>
                        </div>
                        <Badge variant="outline" className="rounded-none text-[10px] shrink-0">
                          {kit.brand}
                        </Badge>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dialog Edit */}
      {showEdit && !isPending && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType="player"
          mode="edit"
          entityId={player.player_id}
          initialData={{
            full_name:        player.full_name,
            nationality:      player.nationality,
            birth_date:       player.birth_date || '',
            birth_year:       player.birth_year,
            bio:              player.bio || '',
            positions:        player.positions?.join(', ') || '',
            preferred_number: player.preferred_number,
            photo_url:        player.photo_url,
          }}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}
