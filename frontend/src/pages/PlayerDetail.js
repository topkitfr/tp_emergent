// frontend/src/pages/PlayerDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Globe, Calendar, Shirt, Trophy, RefreshCw, Ruler, Weight, MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Pencil } from 'lucide-react';
import {
  getPlayer, proxyImageUrl, followEntity, unfollowEntity,
  isFollowing, votePlayerAura, getPlayerAura,
  getPlayerScoring, getPlayerCareer, enrichPlayer,
} from '@/lib/api';
import EntityEditDialog from '@/components/EntityEditDialog';
import { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { useAuth } from '@/contexts/AuthContext';

// ── Helpers ──────────────────────────────────────────────────────────────────
const isTitle = (t) => {
  const p = (t.place || '').toLowerCase();
  return p === '1st' || p === 'winner';
};

const SCORE_TIER = (s) => {
  if (s >= 800) return { label: 'Légende', color: '#f59e0b' };
  if (s >= 500) return { label: 'Elite',   color: '#a855f7' };
  if (s >= 200) return { label: 'Confirmé', color: '#3b82f6' };
  if (s >= 50)  return { label: 'Pro',      color: '#22c55e' };
  return              { label: 'Émergent',  color: '#6b7280' };
};

// ── Component ─────────────────────────────────────────────────────────────────
export default function PlayerDetail() {
  const { id } = useParams();
  const { user: authUser } = useAuth();
  const [player, setPlayer]     = useState(null);
  const [loading, setLoading]   = useState(true);
  const [showEdit, setShowEdit] = useState(false);
  const [following, setFollowing]   = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [aura, setAura]             = useState(null);

  // Scoring / palmarès
  const [scoring, setScoring]           = useState(null);
  const [scoringLoading, setScoringLoading] = useState(false);
  const [enrichLoading, setEnrichLoading]   = useState(false);
  const [enrichError, setEnrichError]       = useState(null);

  // Carrière clubs
  const [career, setCareer]           = useState(null);
  const [careerLoading, setCareerLoading] = useState(false);

  const loadData = useCallback(() => {
    setLoading(true);
    getPlayer(id)
      .then(r => setPlayer(r.data))
      .catch(() => setPlayer(null))
      .finally(() => setLoading(false));
  }, [id]);

  const loadScoring = useCallback((pid) => {
    setScoringLoading(true);
    getPlayerScoring(pid)
      .then(r => setScoring(r.data))
      .catch(() => setScoring(null))
      .finally(() => setScoringLoading(false));
  }, []);

  const loadCareer = useCallback((pid) => {
    setCareerLoading(true);
    getPlayerCareer(pid)
      .then(r => setCareer(r.data))
      .catch(() => setCareer(null))
      .finally(() => setCareerLoading(false));
  }, []);

  useEffect(() => {
    if (!player) return;
    const pid = player.player_id;
    if (authUser) {
      isFollowing('player', pid).then(r => setFollowing(r.data?.following || false)).catch(() => {});
    }
    getPlayerAura(pid).then(r => setAura(r.data)).catch(() => {});
    loadScoring(pid);
    loadCareer(pid);
  }, [player, authUser, loadScoring, loadCareer]);

  const handleFollow = async () => {
    if (!authUser || !player) return;
    setFollowLoading(true);
    try {
      if (following) {
        await unfollowEntity({ target_type: 'player', target_id: player.player_id });
        setFollowing(false);
      } else {
        await followEntity({ target_type: 'player', target_id: player.player_id });
        setFollowing(true);
      }
    } catch (e) { console.error(e); }
    finally { setFollowLoading(false); }
  };

  const handleAuraVote = async (score) => {
    if (!authUser || !player) return;
    try {
      const res = await votePlayerAura(player.player_id, score);
      setAura(res.data);
      setPlayer(p => ({ ...p, aura_level: res.data.aura_level }));
    } catch (e) { console.error(e); }
  };

  const handleEnrich = async () => {
    if (!player) return;
    setEnrichLoading(true);
    setEnrichError(null);
    try {
      await enrichPlayer(player.player_id, player.apifootball_id, aura?.aura_avg || 0);
      loadScoring(player.player_id);
    } catch (e) {
      setEnrichError(e?.response?.data?.detail || "Erreur lors de l'enrichissement");
    } finally {
      setEnrichLoading(false);
    }
  };

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;
  if (!player) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Player not found</p>
    </div>
  );

  const isPending = player.status === 'pending' || player.status === 'for_review';
  const canEdit   = !!authUser;

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

  // Palmarès — titres uniquement (place === '1st' ou 'winner')
  const allTrophies = scoring?.trophies || player.honours || [];
  const titles = allTrophies.filter(isTitle);
  const byComp = {};
  for (const t of titles) {
    const key = t.league || t.honour || t.strHonour || 'Unknown';
    if (!byComp[key]) byComp[key] = [];
    byComp[key].push(t);
  }
  const scorePalmares = scoring?.score_palmares ?? player.score_palmares ?? null;
  const tier = scorePalmares !== null ? SCORE_TIER(scorePalmares) : null;

  const careerEntries = career?.career || [];

  return (
    <div className="animate-fade-in-up" data-testid="player-detail-page">

      {/* ── Header ── */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link
            to="/players"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground mb-5 transition-colors"
          >
            <ArrowLeft className="w-3 h-3" />Players
          </Link>

          <div className="flex flex-col sm:flex-row items-start gap-6">
            <div className="shrink-0 rounded-full bg-secondary flex items-center justify-center overflow-hidden border border-border w-24 h-24">
              {player.photo_url
                ? <img src={proxyImageUrl(player.photo_url)} alt={player.full_name} className="w-24 h-24 object-cover rounded-full" />
                : <User className="w-10 h-10 text-muted-foreground" />
              }
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  {isPending && (
                    <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent mb-2">PENDING APPROVAL</Badge>
                  )}
                  <h1 className="text-3xl sm:text-4xl tracking-tighter break-words">{player.full_name}</h1>
                  <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {player.nationality && <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{player.nationality}</span>}
                    {(player.birth_date || player.birth_year) && (
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {player.birth_date || `Born ${player.birth_year}`}
                      </span>
                    )}
                    {player.birth_place && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{player.birth_place}</span>}
                    {player.height && <span className="flex items-center gap-1"><Ruler className="w-3.5 h-3.5" />{player.height}</span>}
                    {player.weight && <span className="flex items-center gap-1"><Weight className="w-3.5 h-3.5" />{player.weight}</span>}
                    {player.preferred_number && <span className="font-mono text-primary">#{player.preferred_number}</span>}
                  </div>
                  {player.bio && (
                    <p className="mt-2 text-sm text-muted-foreground max-w-lg" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{player.bio}</p>
                  )}
                </div>

                <div className="flex gap-2 shrink-0">
                  {authUser && (
                    <Button variant={following ? 'secondary' : 'outline'} size="sm" onClick={handleFollow} disabled={followLoading} className="rounded-none border-border hover:border-primary/50">
                      {following ? 'Following' : '+ Follow'}
                    </Button>
                  )}
                  {canEdit && (
                    <Button variant="outline" size="sm" onClick={() => setShowEdit(true)} className="rounded-none border-border hover:border-primary/50">
                      <Pencil className="w-3 h-3 mr-1.5" />Suggest Edit
                    </Button>
                  )}
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mt-3">
                {player.positions?.map(p => <Badge key={p} variant="outline" className="rounded-none">{p}</Badge>)}
                <Badge variant="secondary" className="rounded-none">{kitCount} kit{kitCount !== 1 ? 's' : ''}</Badge>
                <Badge
                  variant={player.status === 'approved' ? 'secondary' : 'outline'}
                  className={`rounded-none text-[10px] uppercase tracking-wider ${player.status === 'for_review' ? 'border-accent/40 text-accent' : ''}`}
                >
                  {player.status === 'approved' ? 'Approved' : player.status === 'for_review' ? 'For Review' : 'Pending'}
                </Badge>
                {tier && (
                  <Badge variant="outline" className="rounded-none text-[10px] uppercase tracking-wider" style={{ borderColor: tier.color, color: tier.color }}>
                    {tier.label} · {scorePalmares.toFixed(0)} pts
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Aura ── */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>AURA — NOTE COMMUNAUTAIRE</h3>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(level => (
                <button key={level} type="button" onClick={() => handleAuraVote(level)} disabled={!authUser}
                  className={`p-0.5 transition-transform hover:scale-110 focus:outline-none ${!authUser ? 'cursor-default' : 'cursor-pointer'}`}>
                  <svg className={`w-6 h-6 ${level <= (aura?.aura_level || player?.aura_level || 1) ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30 fill-transparent'}`} viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                  </svg>
                </button>
              ))}
            </div>
            <div className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              {aura ? (
                <><span className="font-mono text-foreground">{aura.aura_avg?.toFixed(1) || '—'}</span><span className="ml-1">/ 5</span><span className="ml-2 text-xs">({aura.aura_votes} vote{aura.aura_votes !== 1 ? 's' : ''})</span>{aura.your_vote && <span className="ml-2 text-xs text-primary">Your vote: {aura.your_vote}★</span>}</>
              ) : <span className="text-xs">No votes yet</span>}
            </div>
          </div>
        </div>
      </div>

      {/* ── Palmarès ── */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>PALMARÈS — TITRES REMPORTÉS</h3>
              {tier && <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 border" style={{ borderColor: tier.color, color: tier.color, fontFamily: 'Barlow Condensed' }}>{tier.label}</span>}
              {player.apifootball_id && <span className="text-xs text-muted-foreground font-mono">#{player.apifootball_id}</span>}
            </div>
            {player.apifootball_id && (
              <Button variant="outline" size="sm" onClick={handleEnrich} disabled={enrichLoading} className="rounded-none border-border hover:border-primary/50 text-xs gap-1.5">
                <RefreshCw className={`w-3 h-3 ${enrichLoading ? 'animate-spin' : ''}`} />
                {enrichLoading ? 'Enrichissement...' : 'Enrich'}
              </Button>
            )}
          </div>
          {enrichError && <p className="text-xs text-destructive mb-3">{enrichError}</p>}

          {scoringLoading ? (
            <div className="flex gap-6 animate-pulse">{[80,60,100].map((w,i) => <div key={i} className="h-8 bg-muted rounded" style={{ width: w }} />)}</div>
          ) : scorePalmares !== null ? (
            <>
              <div className="flex flex-wrap gap-6 mb-5">
                <div>
                  <p className="text-2xl font-bold font-mono" style={{ color: tier?.color }}>{scorePalmares.toFixed(0)}</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Score Palmarès</p>
                </div>
                <div>
                  <p className="text-2xl font-bold font-mono">{titles.length}</p>
                  <p className="text-xs text-muted-foreground uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Titres</p>
                </div>
                {scoring?.updated_at && (
                  <div className="ml-auto self-end">
                    <p className="text-xs text-muted-foreground">Mis à jour le {new Date(scoring.updated_at).toLocaleDateString('fr-FR')}</p>
                  </div>
                )}
              </div>
              {titles.length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(byComp).map(([comp, entries]) => (
                    <div key={comp}>
                      <p className="text-xs uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>{comp}</p>
                      <div className="space-y-1">
                        {entries.map((t, i) => (
                          <div key={i} className="flex items-center justify-between px-3 py-2 border border-border bg-card text-sm">
                            <span className="flex items-center gap-2" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                              <Trophy className="w-3.5 h-3.5 text-yellow-500" />
                              Vainqueur
                            </span>
                            <span className="font-mono text-xs text-muted-foreground">{t.season || t.strSeason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun titre remporté pour ce joueur.</p>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 border border-dashed border-border text-center gap-3">
              <Trophy className="w-8 h-8 text-muted-foreground opacity-30" />
              <p className="text-sm text-muted-foreground">{player.apifootball_id ? 'Palmarès non encore chargé — cliquez sur Enrich' : 'Aucun ID API-Football lié à ce joueur'}</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Carrière Clubs ── */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed' }}>CARRIÈRE — CLUBS</h3>

          {careerLoading ? (
            <div className="space-y-3 animate-pulse">
              {[1,2,3].map(i => <div key={i} className="h-14 bg-muted rounded" />)}
            </div>
          ) : !career?.has_apifootball_id ? (
            <div className="flex flex-col items-center justify-center py-8 border border-dashed border-border text-center gap-3">
              <p className="text-sm text-muted-foreground">Aucun ID API-Football lié à ce joueur</p>
            </div>
          ) : careerEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucune donnée de carrière disponible.</p>
          ) : (
            <div className="space-y-2">
              {careerEntries.map((entry, i) => (
                <div key={i} className="border border-border bg-card">
                  {/* Club row */}
                  <div className="flex items-center gap-4 px-4 py-3">
                    {entry.team_logo ? (
                      <img src={entry.team_logo} alt={entry.club} className="w-8 h-8 object-contain" loading="lazy" />
                    ) : (
                      <div className="w-8 h-8 bg-muted-foreground/10 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-muted-foreground" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{entry.club}</p>
                      <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>
                        {entry.year_start && entry.year_end
                          ? `${entry.year_start} – ${entry.year_end}`
                          : entry.year_start || entry.date_start || ''}
                        {entry.from_club && <span className="ml-2 opacity-60">← {entry.from_club}</span>}
                      </p>
                    </div>
                    {entry.topkit_kits?.length > 0 && (
                      <Badge variant="outline" className="rounded-none text-[10px] shrink-0" style={{ borderColor: '#22c55e', color: '#22c55e' }}>
                        {entry.topkit_kits.length} maillot{entry.topkit_kits.length > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </div>

                  {/* Maillots Topkit liés */}
                  {entry.topkit_kits?.length > 0 && (
                    <div className="border-t border-border px-4 py-2 flex flex-wrap gap-2 bg-muted/30">
                      {entry.topkit_kits.map(kit => (
                        <Link key={kit.kit_id} to={`/kit/${kit.kit_id}`} className="flex items-center gap-2 px-2 py-1 border border-border hover:border-primary/40 transition-colors bg-card">
                          {kit.front_photo && (
                            <img src={proxyImageUrl(kit.front_photo)} alt="" className="w-8 h-10 object-cover" loading="lazy" />
                          )}
                          <div>
                            <p className="text-xs font-medium" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.season}</p>
                            <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.kit_type} · {kit.brand}</p>
                          </div>
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Career in Shirts ── */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <h2 className="text-lg tracking-tighter mb-6">CAREER IN SHIRTS</h2>
        {kitCount === 0 ? (
          <div className="text-center py-16 border border-dashed border-border">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No jersey linked to this player yet</p>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(byTeam).map(([teamName, kits]) => (
              <div key={teamName}>
                <h3 className="text-sm uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{teamName}</h3>
                <div className="space-y-2">
                  {kits.map(kit => (
                    <Link to={`/kit/${kit.kit_id}`} key={kit.kit_id}>
                      <div className="flex items-center gap-4 p-3 border border-border bg-card hover:border-primary/30 transition-colors duration-200">
                        <img src={proxyImageUrl(kit.front_photo)} alt="" className="w-12 h-16 object-cover border border-border" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.season} — {kit.kit_type}</p>
                          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.league || ''}</p>
                        </div>
                        <Badge variant="outline" className="rounded-none text-[10px] shrink-0">{kit.brand}</Badge>
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
            apifootball_id:   player.apifootball_id || '',
          }}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}
