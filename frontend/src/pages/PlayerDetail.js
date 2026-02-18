import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPlayer } from '@/lib/api';
import { proxyImageUrl } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { User, Globe, ArrowLeft, Shirt, Calendar, Pencil } from 'lucide-react';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';

export default function PlayerDetail() {
  const { id } = useParams();
  const { user: authUser } = useAuth();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEdit, setShowEdit] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPlayer(id).then(r => setPlayer(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="animate-fade-in-up px-4 lg:px-8 py-16"><div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" /></div>;
  if (!player) return <div className="px-4 lg:px-8 py-16 text-center"><p className="text-muted-foreground">Player not found</p></div>;

  const versions = player.versions || [];

  // Group versions by team
  const byTeam = {};
  for (const v of versions) {
    const teamName = v.master_kit?.club || 'Unknown';
    if (!byTeam[teamName]) byTeam[teamName] = [];
    byTeam[teamName].push(v);
  }
  // Sort each team's versions by season
  for (const team of Object.keys(byTeam)) {
    byTeam[team].sort((a, b) => (b.master_kit?.season || '').localeCompare(a.master_kit?.season || ''));
  }

  return (
    <div className="animate-fade-in-up" data-testid="player-detail-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link to="/players" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4" data-testid="back-to-players">
            <ArrowLeft className="w-3 h-3" /> Players
          </Link>
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 bg-secondary flex items-center justify-center shrink-0 rounded-full overflow-hidden">
              {player.photo_url ? <img src={player.photo_url} alt={player.full_name} className="w-24 h-24 object-cover" /> : <User className="w-12 h-12 text-muted-foreground" />}
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter" data-testid="player-name">{player.full_name}</h1>
              <div className="flex flex-wrap items-center gap-3 mt-2">
                {player.nationality && <span className="text-sm text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Globe className="w-3 h-3" /> {player.nationality}</span>}
                {player.birth_year && <span className="text-sm text-muted-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Calendar className="w-3 h-3" /> Born {player.birth_year}</span>}
                {player.preferred_number && <span className="text-sm font-mono text-primary">#{player.preferred_number}</span>}
              </div>
              <div className="flex items-center gap-2 mt-3">
                {player.positions?.length > 0 && player.positions.map(p => <Badge key={p} variant="outline" className="rounded-none">{p}</Badge>)}
                <Badge variant="secondary" className="rounded-none">{player.kit_count} versions</Badge>
                {authUser && (
                  <Button variant="outline" size="sm" className="rounded-none border-border ml-2" onClick={() => setShowEdit(true)} data-testid="suggest-edit-btn">
                    <Pencil className="w-3 h-3 mr-1" /> Suggest Edit
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <h2 className="text-lg tracking-tighter mb-6">CAREER IN SHIRTS</h2>

        {versions.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No jersey versions linked to this player yet</p>
          </div>
        ) : (
          <div className="space-y-8" data-testid="player-career">
            {Object.entries(byTeam).map(([teamName, teamVersions]) => (
              <div key={teamName}>
                <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{teamName}</h3>
                <div className="space-y-2">
                  {teamVersions.map(v => (
                    <Link to={`/version/${v.version_id}`} key={v.version_id}>
                      <div className="flex items-center gap-4 p-3 border border-border bg-card hover:border-primary/30" style={{ transition: 'border-color 0.2s' }} data-testid={`career-version-${v.version_id}`}>
                        <img src={proxyImageUrl(v.front_photo || v.master_kit?.front_photo)} alt="" className="w-12 h-16 object-cover border border-border" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {v.master_kit?.season || ''} — {v.master_kit?.kit_type || ''}
                          </p>
                          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                            {v.competition} / {v.model}
                          </p>
                        </div>
                        <Badge variant="outline" className="rounded-none text-[10px] shrink-0">{v.master_kit?.brand}</Badge>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {player && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType="player"
          mode="edit"
          entityId={player.player_id}
          initialData={{ full_name: player.full_name, nationality: player.nationality, birth_year: player.birth_year, positions: player.positions?.join(', ') || '', preferred_number: player.preferred_number, photo_url: player.photo_url }}
          onSuccess={() => getPlayer(id).then(r => setPlayer(r.data))}
        />
      )}
    </div>
  );
}