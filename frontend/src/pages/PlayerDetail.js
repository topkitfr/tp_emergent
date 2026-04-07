// frontend/src/pages/PlayerDetail.js
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  User, Globe, Calendar, Shirt, Trophy, RefreshCw,
  Ruler, Weight, MapPin, ArrowRight, Star, Award,
} from 'lucide-react';
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

// ── SECTION 2 : Combined Career + Transfer Chart ──────────────────────────────
function CareerTransferSection({ entries, loading, hasApiId }) {
  const canvasRef = useRef(null);

  const withFees = entries.filter(e => e.transfer_fee && e.transfer_fee > 0);
  const maxFee = withFees.length > 0 ? Math.max(...withFees.map(e => e.transfer_fee)) : 0;

  // Draw bar chart on canvas
  useEffect(() => {
    if (!canvasRef.current || withFees.length === 0) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.offsetWidth;
    const H = 160;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    ctx.scale(dpr, dpr);

    // Clear
    ctx.clearRect(0, 0, W, H);

    const padL = 10, padR = 16, padT = 16, padB = 28;
    const chartW = W - padL - padR;
    const chartH = H - padT - padB;
    const barCount = withFees.length;
    const barGap = 6;
    const barW = Math.max(8, (chartW - (barCount - 1) * barGap) / barCount);

    // Grid lines (2)
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    [0.33, 0.66, 1].forEach(ratio => {
      const y = padT + chartH * (1 - ratio);
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(W - padR, y);
      ctx.stroke();
    });

    withFees.forEach((e, i) => {
      const ratio = e.transfer_fee / maxFee;
      const barH = Math.max(4, ratio * chartH);
      const x = padL + i * (barW + barGap);
      const y = padT + chartH - barH;

      // Bar gradient
      const grad = ctx.createLinearGradient(0, y, 0, y + barH);
      grad.addColorStop(0, 'hsl(174 70% 42%)');
      grad.addColorStop(1, 'hsl(174 70% 28%)');
      ctx.fillStyle = grad;
      ctx.fillRect(x, y, barW, barH);

      // Amount label on top
      const label = formatTransfer(e.transfer_fee);
      ctx.fillStyle = 'hsl(174 70% 65%)';
      ctx.font = `bold ${Math.min(10, barW * 0.9)}px "DM Sans", sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(label, x + barW / 2, y - 4);

      // Club label below
      const clubLabel = (e.club || '').slice(0, 8);
      ctx.fillStyle = 'rgba(160,160,155,0.7)';
      ctx.font = `9px "DM Sans", sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(clubLabel, x + barW / 2, H - padB + 14);
    });
  }, [withFees, maxFee]);

  if (loading) {
    return (
      <div className="space-y-3 animate-pulse">
        {[1,2,3].map(i => <div key={i} className="h-14 bg-muted rounded" />)}
      </div>
    );
  }
  if (!hasApiId) {
    return (
      <div className="flex flex-col items-center justify-center py-8 border border-dashed border-border text-center gap-2">
        <p className="text-sm text-muted-foreground">Aucun ID API-Football lié à ce joueur</p>
      </div>
    );
  }
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">Aucune donnée de carrière disponible.</p>;
  }

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* LEFT: Timeline clubs */}
      <div className="flex-1 min-w-0">
        <div className="relative">
          <div className="absolute left-[19px] top-0 bottom-0 w-px bg-border" />
          <div className="space-y-0">
            {entries.map((entry, i) => (
              <div key={i} className="relative flex gap-4 pb-4">
                <div className="shrink-0 relative z-10 flex items-start pt-3">
                  {entry.team_logo ? (
                    <img src={entry.team_logo} alt={entry.club} className="w-10 h-10 object-contain bg-card border border-border p-0.5" loading="lazy" />
                  ) : (
                    <div className="w-10 h-10 bg-muted border border-border flex items-center justify-center">
                      <User className="w-4 h-4 text-muted-foreground" />
                    </div>
                  )}
                </div>
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
      </div>

      {/* RIGHT: Transfer bar chart (only shown if there are fees) */}
      {withFees.length > 0 && (
        <div className="lg:w-64 shrink-0">
          <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>
            MONTANTS DE TRANSFERT
          </p>
          <div className="border border-border bg-card p-3">
            <canvas ref={canvasRef} className="w-full" style={{ height: 160 }} />
          </div>
          {/* Legend list */}
          <div className="mt-2 space-y-1">
            {withFees.map((e, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground truncate mr-2">{e.club}</span>
                <span className="font-mono text-primary shrink-0">{formatTransfer(e.transfer_fee)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── SECTION 3 : Trophées + Awards perso ───────────────────────────────────────
function TrophiesSection({ scoring, player, tier, scorePalmares, enrichLoading, enrichError, onEnrich, scoringLoading }) {
  const allTrophies = scoring?.trophies || player.honours || [];

  // Group titles by competition name, count wins only
  const titlesByComp = {};
  const finalesByComp = {};

  for (const t of allTrophies) {
    const meta = PLACE_META(t.place);
    if (meta.order > 2) continue;
    const key = t.league || t.honour || t.strHonour || 'Unknown';
    if (meta.order === 1) {
      titlesByComp[key] = (titlesByComp[key] || 0) + 1;
    } else {
      finalesByComp[key] = (finalesByComp[key] || 0) + 1;
    }
  }

  const titlesCount = allTrophies.filter(t => PLACE_META(t.place).order === 1).length;
  const finalesCount = allTrophies.filter(t => PLACE_META(t.place).order === 2).length;

  const individualAwards = player.individual_awards || [];
  const hasAwards = individualAwards.length > 0;
  const hasTrophies = Object.keys(titlesByComp).length > 0 || Object.keys(finalesByComp).length > 0;

  if (scoringLoading) {
    return (
      <div className="flex gap-6 animate-pulse">
        {[80, 60, 100].map((w, i) => <div key={i} className="h-8 bg-muted rounded" style={{ width: w }} />)}
      </div>
    );
  }

  return (
    <div>
      {/* Header bar */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
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
            <Button variant="outline" size="sm" onClick={onEnrich} disabled={enrichLoading} className="rounded-none border-border hover:border-primary/50 text-xs gap-1.5">
              <RefreshCw className={`w-3 h-3 ${enrichLoading ? 'animate-spin' : ''}`} />
              {enrichLoading ? 'Chargement...' : 'Enrich'}
            </Button>
          )}
        </div>
      </div>

      {enrichError && <p className="text-xs text-destructive mb-3">{enrichError}</p>}

      {scorePalmares === null && !hasTrophies ? (
        <div className="flex flex-col items-center justify-center py-10 border border-dashed border-border text-center gap-3">
          <Trophy className="w-8 h-8 text-muted-foreground opacity-30" />
          <p className="text-sm text-muted-foreground">
            {player.apifootball_id ? 'Palmarès non encore chargé — cliquez sur Enrich' : 'Aucun ID API-Football lié à ce joueur'}
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* ── Trophées collectifs — style "FIFA WORLD CUP ×2" ── */}
          {hasTrophies && (
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>
                PALMARÈS COLLECTIF
                {titlesCount > 0 && <span className="ml-2 font-mono text-muted-foreground/50">{titlesCount} titre{titlesCount > 1 ? 's' : ''}</span>}
              </p>
              {/* Wins */}
              {Object.keys(titlesByComp).length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {Object.entries(titlesByComp).map(([comp, count]) => (
                    <div key={comp} className="flex items-center gap-1.5 border border-border bg-card px-3 py-1.5">
                      <span className="text-base">🥇</span>
                      <span className="text-xs font-semibold uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>{comp}</span>
                      {count > 1 && (
                        <span className="text-xs font-mono text-primary border border-primary/30 px-1 ml-1">×{count}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {/* Runner-ups */}
              {Object.keys(finalesByComp).length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {Object.entries(finalesByComp).map(([comp, count]) => (
                    <div key={comp} className="flex items-center gap-1.5 border border-border bg-card px-3 py-1.5 opacity-60">
                      <span className="text-base">🥈</span>
                      <span className="text-xs font-semibold uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>{comp}</span>
                      {count > 1 && (
                        <span className="text-xs font-mono px-1 ml-1 border border-border">×{count}</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── Awards individuels (masqués si vide) ── */}
          {hasAwards && (
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>
                DISTINCTIONS INDIVIDUELLES
              </p>
              <div className="flex flex-wrap gap-2">
                {individualAwards.map((award, i) => (
                  <div key={i} className="flex items-center gap-1.5 border border-border bg-card px-3 py-1.5" style={{ borderColor: 'rgba(168,85,247,0.3)' }}>
                    <Award className="w-3.5 h-3.5" style={{ color: '#a855f7' }} />
                    <span className="text-xs font-semibold uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed', color: '#a855f7' }}>
                      {typeof award === 'string' ? award : award.name}
                    </span>
                    {(award.count > 1 || award.year) && (
                      <span className="text-xs font-mono px-1 ml-1 border" style={{ borderColor: 'rgba(168,85,247,0.3)', color: '#a855f7' }}>
                        {award.count > 1 ? `×${award.count}` : award.year}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────
export default function PlayerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: authUser } = useAuth();
  const [player, setPlayer]         = useState(null);
  const [loading, setLoading]       = useState(true);
  const [showEdit, setShowEdit]     = useState(false);
  const [following, setFollowing]   = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [aura, setAura]             = useState(null);

  const [scoring, setScoring]               = useState(null);
  const [scoringLoading, setScoringLoading] = useState(false);
  const [enrichLoading, setEnrichLoading]   = useState(false);
  const [enrichError, setEnrichError]       = useState(null);

  const [career, setCareer]               = useState(null);
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
      loadCareer(player.player_id);
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

  // Kits pour Section 4
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
  const visibleKits = allKitsList.slice(0, 5);

  const careerEntries = career?.career || [];

  const scorePalmares = scoring?.score_palmares ?? player.score_palmares ?? null;
  const tier = scorePalmares !== null ? SCORE_TIER(scorePalmares) : null;

  // Browse URL with player filter
  const browseUrl = `/browse?player=${encodeURIComponent(player.full_name)}`;

  return (
    <div className="animate-fade-in-up" data-testid="player-detail-page">

      {/* ════════════════════════════════════════════════════
           SECTION 1 — IDENTITÉ JOUEUR
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

              {/* Aura */}
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
           SECTION 2 — HISTORIQUE CLUB + TRANSFERTS
      ════════════════════════════════════════════════════ */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xs uppercase tracking-wider text-muted-foreground mb-5" style={{ fontFamily: 'Barlow Condensed' }}>
            CARRIÈRE &amp; TRANSFERTS
          </h2>
          <CareerTransferSection
            entries={careerEntries}
            loading={careerLoading}
            hasApiId={career?.has_apifootball_id ?? !!player.apifootball_id}
          />
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
           SECTION 3 — TROPHÉES + AWARDS INDIVIDUELS
      ════════════════════════════════════════════════════ */}
      <div className="border-b border-border px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-xs uppercase tracking-wider text-muted-foreground mb-5" style={{ fontFamily: 'Barlow Condensed' }}>
            PALMARÈS &amp; DISTINCTIONS
          </h2>
          <TrophiesSection
            scoring={scoring}
            player={player}
            tier={tier}
            scorePalmares={scorePalmares}
            enrichLoading={enrichLoading}
            enrichError={enrichError}
            onEnrich={handleEnrich}
            scoringLoading={scoringLoading}
          />
        </div>
      </div>

      {/* ════════════════════════════════════════════════════
           SECTION 4 — CAREER IN SHIRTS (5 max + See More)
      ════════════════════════════════════════════════════ */}
      <div className="px-4 lg:px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
              CAREER IN SHIRTS
              {kitCount > 0 && <span className="ml-2 font-mono text-muted-foreground/50">{kitCount}</span>}
            </h2>
            {kitCount > 5 && (
              <Link
                to={browseUrl}
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
                style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
              >
                See all {kitCount} shirts <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </div>

          {kitCount === 0 ? (
            <div className="text-center py-12 border border-dashed border-border">
              <Shirt className="w-8 h-8 text-muted-foreground mx-auto mb-3 opacity-30" />
              <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun maillot lié à ce joueur</p>
            </div>
          ) : (
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
              {/* "See More" card tile si > 5 */}
              {kitCount > 5 && (
                <Link
                  to={browseUrl}
                  className="border border-dashed border-border bg-card hover:border-primary/40 transition-colors duration-200 flex flex-col items-center justify-center aspect-[3/4] gap-2 text-muted-foreground hover:text-primary"
                >
                  <ArrowRight className="w-5 h-5" />
                  <span className="text-xs text-center px-2" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    +{kitCount - 5} de plus
                  </span>
                </Link>
              )}
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
            full_name:          player.full_name,
            nationality:        player.nationality,
            birth_date:         player.birth_date || '',
            birth_year:         player.birth_year,
            bio:                player.bio || '',
            positions:          player.positions?.join(', ') || '',
            preferred_number:   player.preferred_number,
            photo_url:          player.photo_url,
            apifootball_id:     player.apifootball_id || '',
            individual_awards:  player.individual_awards || [],
          }}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}
