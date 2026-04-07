// frontend/src/pages/PlayerDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { User, Globe, Calendar, Shirt, Trophy, RefreshCw, Ruler, Weight, MapPin, ArrowRight } from 'lucide-react';
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

// ── Helpers ───────────────────────────────────────────────────────────────────
const SCORE_TIER = (s) => {
  if (s >= 800) return { label: 'Légende', color: '#f59e0b' };
  if (s >= 500) return { label: 'Elite',   color: '#a855f7' };
  if (s >= 200) return { label: 'Confirmé', color: '#3b82f6' };
  if (s >= 50)  return { label: 'Pro',      color: '#22c55e' };
  return              { label: 'Émergent',  color: '#6b7280' };
};

const PLACE_META = (place) => {
  const p = (place || '').toLowerCase();
  if (p === '1st' || p === 'winner') return { icon: '🥇', label: 'Vainqueur', order: 1 };
  if (p === '2nd' || p === 'runner-up') return { icon: '🥈', label: '2e place', order: 2 };
  if (p === '3rd' || p === 'third') return { icon: '🥉', label: '3e place', order: 3 };
  return { icon: '🏅', label: place, order: 4 };
};

const formatTransfer = (amount) => {
  if (!amount || amount === 0) return null;
  if (amount >= 1_000_000) return `${(amount / 1_000_000).toFixed(1)}M€`;
  if (amount >= 1_000) return `${Math.round(amount / 1_000)}K€`;
  return `${amount}€`;
};

// ── Transfer Bar Chart ─────────────────────────────────────────────────────────
function TransferChart({ entries }) {
  const withFees = entries.filter(e => e.transfer_fee && e.transfer_fee > 0);
  if (withFees.length === 0) return null;
  const max = Math.max(...withFees.map(e => e.transfer_fee));
  return (
    <div className="mt-4 border border-border bg-card p-4">
      <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>MONTANTS DE TRANSFERT</p>
      <div className="space-y-2">
        {withFees.map((e, i) => (
          <div key={i} className="flex items-center gap-3">
            <div className="w-24 shrink-0 text-xs text-muted-foreground truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{e.club}</div>
            <div className="flex-1 bg-muted h-5 relative overflow-hidden">
              <div
                className="h-full bg-primary/70 transition-all duration-700"
                style={{ width: `${Math.round((e.transfer_fee / max) * 100)}%` }}
              />
            </div>
            <div className="w-16 text-right text-xs font-mono text-primary shrink-0">{formatTransfer(e.transfer_fee)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function PlayerDetail() {
  const { id } = useParams();
  const { user: authUser } = useAuth();
  const [player, setPlayer]         = useState(null);
  const [loading, setLoading]       = useState(true);
  const [showEdit, setShowEdit]     = useState(false);
  const [following, setFollowing]   = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [aura, setAura]             = useState(null);
  const [showAllKits, setShowAllKits] = useState(false);

  // Scoring / palmarès
  const [scoring, setScoring]             = useState(null);
  const [scoringLoading, setScoringLoading] = useState(false);
  const [enrichLoading, setEnrichLoading]   = useState(false);
  const [enrichError, setEnrichError]       = useState(null);

  // Carrière clubs
  const [career, setCareer]             = useState(null);
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

  useEffect(() => { loadData(); }, [loadData]);

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

  if (loading) return <EntityDetailSkeleton />;
  if (!player) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Player not found</p>
    </div>
  );

  const isPending = player.status === 'pending' || player.status === 'for_review';
  const canEdit   = !!authUser;

  // ── Kits par équipe ──
  const versions = player.versions || [];
  const kitsSeen = new Set();
  const allKitsList = [];
  for (const v of versions) {
    const kit = v.master_kit;
    if (!kit || kitsSeen.has(kit.kit_id)) continue;
    kitsSeen.add(kit.kit_id);
    allKitsList.push({ ...kit, version_id: v.version_id });
  }
  allKitsList.sort((a, b) => (b.season || '').localeCompare(a.season || ''));
  const kitCount = allKitsList.length;
  const visibleKits = showAllKits ? allKitsList : allKitsList.slice(0, 5);

  // ── Palmarès ──
  const allTrophies = scoring?.trophies || player.honours || [];
  const byComp = {};
  for (const t of allTrophies) {
    const meta = PLACE_META(t.place);
    // Afficher winner + runner-up seulement
    if (meta.order > 2) continue;
    const key = t.league || t.honour || t.strHonour || 'Unknown';
    if (!byComp[key]) byComp[key] = [];
    byComp[key].push({ ...t, _meta: meta });
  }
  // Tri interne par ordre médaille
  for (const key of Object.keys(byComp)) {
    byComp[key].sort((a, b) => a._meta.order - b._meta.order || (b.season || '').localeCompare(a.season || ''));
  }
  const titlesCount    = allTrophies.filter(t => PLACE_META(t.place).order === 1).length;
  const scorePalmares  = scoring?.score_palmares ?? player.score_palmares ?? null;
  const tier           = scorePalmares !== null ? SCORE_TIER(scorePalmares) : null;

  const careerEntries = career?.career || [];

  return (
    <div className="animate-fade-in-up" data-testid="player-detail-page">

      {/* ════════════════════════════════════════════════════
           HEADER — Identité + Aura intégrée
      ════════════════════════════════════════════════════ */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link
            to="/players"
            className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground mb-5 transition-colors"
          >
            <ArrowLeft className="w-3 h-3" />Players
          </Link>

          <div className="flex flex-col sm:flex-row items-start gap-6">
            {/* Photo */}
            <div className="shrink-0 rounded-full bg-secondary flex items-center justify-center overflow-hidden border border-border w-24 h-24">
              {player.photo_url
                ? <img src={proxyImageUrl(player.photo_url)} alt={player.full_name} className="w-24 h-24 object-cover rounded-full" />
                : <User className="w-10 h-10 text-muted-foreground" />
              }
            </div>

            <div className="flex-1 min-w-0">
              {/* Nom + actions */}
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

              {/* Badges positions / statut / tier */}
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

              {/* ── Aura intégrée dans le header ── */}
              <div className="flex items-center gap-3 mt-4 pt-4 border-t border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>AURA</span>
                <div className="flex items-center gap-0.5">
                  {[1,2,3,4,5].map(level => (
                    <button key={level} type="button" onClick={() => handleAuraVote(level)} disabled={!authUser}
                      className={`p-0.5 transition-transform hover:scale-110 focus:outline-none ${!authUser ? 'cursor-default' : 'cursor-pointer'}`}>
                      <svg className={`w-5 h-5 ${level <= (aura?.aura_level || player?.aura_level || 1) ? 'text-yellow-400 fill-yellow-400' : 'text-muted-foreground/30 fill-transparent'}`} viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                      </svg>
                    </button>
                  ))}
                </div>
                <span className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  {aura
                    ? <><span className="font-mono text-foreground">{aura.aura_avg?.toFixed(1) || '—'}</span><span className="ml-1 text-xs">/ 5</span><span className="ml-2 text-xs">({aura.aura_votes} vote{aura.aura_votes !== 1 ? 's' : ''})</span>{aura.your_vote && <span className="ml-2 text-xs text-primary">· ton vote : {aura.your_vote}★</span>}</>
                    : <span className="text-xs">Aucun vote</span>
                  }
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
           SECTION 1 — CARRIÈRE CLUBS + TRANSFERTS
      ════════════════════════════════════════════════════ */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xs uppercase tracking-wider text-muted-foreground mb-5" style={{ fontFamily: 'Barlow Condensed' }}>CARRIÈRE — CLUBS</h2>

          {careerLoading ? (
            <div className="space-y-3 animate-pulse">
              {[1,2,3].map(i => <div key={i} className="h-14 bg-muted rounded" />)}
            </div>
          ) : !career?.has_apifootball_id ? (
            <div className="flex flex-col items-center justify-center py-8 border border-dashed border-border text-center gap-2">
              <p className="text-sm text-muted-foreground">Aucun ID API-Football lié à ce joueur</p>
            </div>
          ) : careerEntries.length === 0 ? (
            <p className="text-sm text-muted-foreground">Aucune donnée de carrière disponible.</p>
          ) : (
            <>
              {/* Timeline */}
              <div className="relative">
                {/* Ligne verticale */}
                <div className="absolute left-[19px] top-0 bottom-0 w-px bg-border" />

                <div className="space-y-0">
                  {careerEntries.map((entry, i) => (
                    <div key={i} className="relative flex gap-4 pb-4">
                      {/* Dot timeline */}
                      <div className="shrink-0 relative z-10 flex items-start pt-3">
                        {entry.team_logo ? (
                          <img src={entry.team_logo} alt={entry.club} className="w-10 h-10 object-contain bg-card border border-border p-0.5" loading="lazy" />
                        ) : (
                          <div className="w-10 h-10 bg-muted border border-border flex items-center justify-center">
                            <User className="w-4 h-4 text-muted-foreground" />
                          </div>
                        )}
                      </div>

                      {/* Contenu */}
                      <div className="flex-1 border border-border bg-card px-4 py-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{entry.club}</p>
                            <p className="text-xs text-muted-foreground mt-0.5" style={{ fontFamily: 'DM Sans' }}>
                              {entry.year_start && entry.year_end
                                ? `${entry.year_start} – ${entry.year_end}`
                                : entry.year_start || entry.date_start || '—'}
                              {entry.from_club && <span className="ml-2 opacity-50">← {entry.from_club}</span>}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            {entry.transfer_fee > 0 && (
                              <span className="text-xs font-mono text-primary border border-primary/30 px-1.5 py-0.5">
                                {formatTransfer(entry.transfer_fee)}
                              </span>
                            )}
                            {entry.topkit_kits?.length > 0 && (
                              <Badge variant="outline" className="rounded-none text-[10px]" style={{ borderColor: '#22c55e', color: '#22c55e' }}>
                                {entry.topkit_kits.length} kit{entry.topkit_kits.length > 1 ? 's' : ''}
                              </Badge>
                            )}
                          </div>
                        </div>

                        {/* Mini kits liés dans la carrière */}
                        {entry.topkit_kits?.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {entry.topkit_kits.map(kit => (
                              <Link key={kit.kit_id} to={`/kit/${kit.kit_id}`}
                                className="flex items-center gap-1.5 px-2 py-1 border border-border hover:border-primary/40 transition-colors bg-background text-xs"
                                style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                              >
                                {kit.front_photo && (
                                  <img src={proxyImageUrl(kit.front_photo)} alt="" className="w-6 h-8 object-cover" loading="lazy" />
                                )}
                                <span className="text-muted-foreground">{kit.season}</span>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bar chart transferts */}
              <TransferChart entries={careerEntries} />
            </>
          )}
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
           SECTION 2 — MAILLOTS TOPKIT (5 max)
      ════════════════════════════════════════════════════ */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
              MAILLOTS TOPKIT
              {kitCount > 0 && <span className="ml-2 font-mono text-muted-foreground/50">{kitCount}</span>}
            </h2>
            {kitCount > 5 && !showAllKits && (
              <button
                onClick={() => setShowAllKits(true)}
                className="text-xs text-primary hover:underline flex items-center gap-1"
                style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
              >
                Voir les {kitCount} maillots <ArrowRight className="w-3 h-3" />
              </button>
            )}
          </div>

          {kitCount === 0 ? (
            <div className="text-center py-12 border border-dashed border-border">
              <Shirt className="w-8 h-8 text-muted-foreground mx-auto mb-3 opacity-30" />
              <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun maillot lié à ce joueur</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
                {visibleKits.map(kit => (
                  <Link to={`/kit/${kit.kit_id}`} key={kit.kit_id}
                    className="border border-border bg-card hover:border-primary/40 transition-colors duration-200 group"
                  >
                    <div className="aspect-[3/4] overflow-hidden bg-muted">
                      {kit.front_photo
                        ? <img src={proxyImageUrl(kit.front_photo)} alt="" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" loading="lazy" />
                        : <div className="w-full h-full flex items-center justify-center"><Shirt className="w-8 h-8 text-muted-foreground opacity-30" /></div>
                      }
                    </div>
                    <div className="p-2">
                      <p className="text-xs font-medium truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.club}</p>
                      <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{kit.season} · {kit.kit_type}</p>
                    </div>
                  </Link>
                ))}
              </div>
              {kitCount > 5 && showAllKits && (
                <button
                  onClick={() => setShowAllKits(false)}
                  className="mt-3 text-xs text-muted-foreground hover:text-foreground transition-colors"
                  style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                >
                  Réduire
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
           SECTION 3 — PALMARÈS COLLECTIF (🥇 + 🥈)
      ════════════════════════════════════════════════════ */}
      <div className="px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <h2 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>PALMARÈS COLLECTIF</h2>
              {tier && (
                <span className="text-xs font-bold uppercase tracking-wider px-2 py-0.5 border" style={{ borderColor: tier.color, color: tier.color, fontFamily: 'Barlow Condensed' }}>
                  {tier.label}
                </span>
              )}
              {scorePalmares !== null && (
                <span className="text-xs font-mono text-muted-foreground">{scorePalmares.toFixed(0)} pts</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {scoring?.updated_at && (
                <span className="text-xs text-muted-foreground hidden sm:inline">
                  MàJ {new Date(scoring.updated_at).toLocaleDateString('fr-FR')}
                </span>
              )}
              {player.apifootball_id && (
                <Button variant="outline" size="sm" onClick={handleEnrich} disabled={enrichLoading} className="rounded-none border-border hover:border-primary/50 text-xs gap-1.5">
                  <RefreshCw className={`w-3 h-3 ${enrichLoading ? 'animate-spin' : ''}`} />
                  {enrichLoading ? 'Chargement...' : 'Enrich'}
                </Button>
              )}
            </div>
          </div>

          {enrichError && <p className="text-xs text-destructive mb-3">{enrichError}</p>}

          {scoringLoading ? (
            <div className="flex gap-6 animate-pulse">{[80,60,100].map((w,i) => <div key={i} className="h-8 bg-muted rounded" style={{ width: w }} />)}</div>
          ) : scorePalmares !== null ? (
            <>
              {/* Stats chiffres */}
              {titlesCount > 0 && (
                <div className="flex gap-6 mb-5">
                  <div>
                    <p className="text-2xl font-bold font-mono" style={{ color: tier?.color }}>{titlesCount}</p>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Titres 🥇</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold font-mono text-muted-foreground">
                      {allTrophies.filter(t => PLACE_META(t.place).order === 2).length}
                    </p>
                    <p className="text-xs text-muted-foreground uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Finales 🥈</p>
                  </div>
                </div>
              )}

              {/* Liste par compétition */}
              {Object.keys(byComp).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(byComp).map(([comp, entries]) => (
                    <div key={comp}>
                      <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1.5" style={{ fontFamily: 'Barlow Condensed' }}>{comp}</p>
                      <div className="space-y-1">
                        {entries.map((t, i) => (
                          <div key={i} className="flex items-center justify-between px-3 py-2 border border-border bg-card text-sm">
                            <span className="flex items-center gap-2" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                              <span>{t._meta.icon}</span>
                              <span>{t._meta.label}</span>
                            </span>
                            <span className="font-mono text-xs text-muted-foreground">{t.season || t.strSeason}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Aucun palmarès enregistré pour ce joueur.</p>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 border border-dashed border-border text-center gap-3">
              <Trophy className="w-8 h-8 text-muted-foreground opacity-30" />
              <p className="text-sm text-muted-foreground">
                {player.apifootball_id ? 'Palmarès non encore chargé — cliquez sur Enrich' : 'Aucun ID API-Football lié à ce joueur'}
              </p>
            </div>
          )}
        </div>
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
