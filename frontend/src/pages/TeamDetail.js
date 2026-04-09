// frontend/src/pages/TeamDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Shield, Globe, MapPin, Calendar, UserPlus, UserMinus,
  Pencil, Shirt, ArrowLeft, Building2
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { getTeam, followEntity, unfollowEntity, isFollowing, proxyImageUrl } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

const BC = { fontFamily: 'Barlow Condensed, sans-serif' };
const DM = { fontFamily: 'DM Sans, sans-serif', textTransform: 'none' };

// ─── Skeleton ───────────────────────────────────────────────────────────────────
function TeamDetailSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="w-full bg-card" style={{ minHeight: '280px' }} />
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
          <div className="h-40 bg-card border border-border" />
          <div className="h-40 bg-card border border-border" />
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1,2,3,4,5,6].map(i => <div key={i} className="aspect-[3/4] bg-card border border-border" />)}
        </div>
      </div>
    </div>
  );
}

// ─── VenueCard ────────────────────────────────────────────────────────────────
function VenueCard({ team }) {
  const hasVenue = team.stadium_name || team.stadium_capacity || team.stadium_city;
  if (!hasVenue) return null;

  return (
    <div className="border border-border bg-card overflow-hidden">
      {team.stadium_image_url && (
        <div className="aspect-video w-full overflow-hidden bg-secondary">
          <img
            src={proxyImageUrl(team.stadium_image_url)}
            alt={team.stadium_name || 'Stadium'}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        </div>
      )}
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2">
          <Building2 className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground" style={BC}>Stadium</p>
        </div>
        {team.stadium_name && (
          <p className="text-lg tracking-tight" style={BC}>{team.stadium_name}</p>
        )}
        <div className="grid grid-cols-2 gap-x-4 gap-y-2">
          {team.stadium_capacity && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5" style={BC}>Capacity</p>
              <p className="text-sm font-mono">{team.stadium_capacity.toLocaleString()}</p>
            </div>
          )}
          {team.stadium_surface && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5" style={BC}>Surface</p>
              <p className="text-sm" style={DM}>{team.stadium_surface}</p>
            </div>
          )}
          {team.stadium_city && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5" style={BC}>City</p>
              <p className="text-sm" style={DM}>{team.stadium_city}</p>
            </div>
          )}
          {team.stadium_country && (
            <div>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5" style={BC}>Country</p>
              <p className="text-sm" style={DM}>{team.stadium_country}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── TeamInfoCard ─────────────────────────────────────────────────────────────
function TeamInfoCard({ team }) {
  const items = [
    team.country      && { label: 'Country', value: team.country },
    team.city         && { label: 'City',    value: team.city },
    team.founded      && { label: 'Founded', value: team.founded },
    team.gender       && { label: 'Genre',   value: team.gender.charAt(0).toUpperCase() + team.gender.slice(1) },
    team.is_national != null && {
      label: 'Type',
      value: team.is_national ? '🚩 National' : '🏟️ Club',
    },
  ].filter(Boolean);

  if (items.length === 0) return null;

  return (
    <div className="border border-border bg-card p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Shield className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
        <p className="text-[10px] uppercase tracking-widest text-muted-foreground" style={BC}>Team Info</p>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-2">
        {items.map(({ label, value }) => (
          <div key={label}>
            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-0.5" style={BC}>{label}</p>
            <p className="text-sm" style={DM}>{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────
export default function TeamDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [team, setTeam]                 = useState(null);
  const [loading, setLoading]           = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterBrand, setFilterBrand]   = useState('');
  const [following, setFollowing]       = useState(false);
  const [followLoading, setFollowLoading] = useState(false);
  const [showEdit, setShowEdit]         = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getTeam(id);
      setTeam({
        ...res.data,
        kits: (res.data?.kits || []).filter(k => k.status !== 'rejected'),
      });
    } catch {
      setTeam(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    if (!user || !id) return;
    isFollowing('team', id)
      .then(r => setFollowing(r.data?.following || false))
      .catch(() => {});
  }, [user, id]);

  const handleFollow = async () => {
    if (!user) return;
    setFollowLoading(true);
    try {
      if (following) {
        await unfollowEntity({ target_type: 'team', target_id: id });
        setFollowing(false);
      } else {
        await followEntity({ target_type: 'team', target_id: id });
        setFollowing(true);
      }
    } catch (e) {
      console.error('Follow error:', e);
    } finally {
      setFollowLoading(false);
    }
  };

  if (loading) return <TeamDetailSkeleton />;
  if (!team) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Team not found</p>
    </div>
  );

  const kits    = team.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const brands  = [...new Set(kits.map(k => k.brand).filter(Boolean))].sort();

  const filteredKits = kits.filter(kit => {
    const okSeason = !filterSeason || kit.season === filterSeason;
    const okBrand  = !filterBrand  || (kit.brand || '').toLowerCase().includes(filterBrand.toLowerCase());
    return okSeason && okBrand;
  });

  const isPending = team.status === 'pending' || team.status === 'for_review';

  return (
    <div className="animate-fade-in-up" data-testid="team-detail-page">

      {/* ── HERO BANNER ──────────────────────────────────────────────────── */}
      <div className="relative w-full overflow-hidden" style={{ minHeight: '280px' }}>
        {team.stadium_image_url ? (
          <img
            src={proxyImageUrl(team.stadium_image_url)}
            alt={team.stadium_name || team.name}
            className="absolute inset-0 w-full h-full object-cover"
            loading="eager"
          />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-card to-secondary" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/10" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 lg:px-8 pt-6 pb-8 flex flex-col" style={{ minHeight: '280px' }}>
          <Link
            to="/teams"
            className="inline-flex items-center gap-1.5 text-xs text-white/60 hover:text-white/90 transition-colors mb-auto"
          >
            <ArrowLeft className="w-3 h-3" />
            Teams
          </Link>

          <div className="flex items-end gap-5 mt-8">
            {/* Crest */}
            <div className="shrink-0 w-20 h-20 bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center overflow-hidden">
              {team.crest_url
                ? <img src={proxyImageUrl(team.crest_url)} alt={team.name} className="w-16 h-16 object-contain p-1" />
                : <Shield className="w-8 h-8 text-white/40" />
              }
            </div>

            <div className="flex-1 min-w-0">
              {isPending && (
                <Badge variant="outline" className="rounded-none text-[10px] border-white/30 text-white/70 mb-2">
                  PENDING APPROVAL
                </Badge>
              )}
              <h1 className="text-3xl sm:text-4xl tracking-tighter text-white break-words" style={BC}>
                {team.name}
              </h1>
              <div className="flex flex-wrap items-center gap-3 mt-1.5 text-sm text-white/60" style={DM}>
                {team.country && (
                  <span className="flex items-center gap-1">
                    <Globe className="w-3.5 h-3.5" />{team.country}
                  </span>
                )}
                {team.city && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" />{team.city}
                  </span>
                )}
                {team.founded && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />Est. {team.founded}
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {user && (
                <button
                  onClick={handleFollow}
                  disabled={followLoading}
                  className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border rounded-none transition-colors ${
                    following
                      ? 'bg-white text-black border-white hover:bg-white/80'
                      : 'bg-transparent text-white border-white/40 hover:border-white'
                  }`}
                  style={BC}
                  data-testid="follow-btn"
                >
                  {following
                    ? <><UserMinus className="w-3.5 h-3.5" /> Unfollow</>
                    : <><UserPlus  className="w-3.5 h-3.5" /> Follow</>}
                </button>
              )}
              {user && (
                <button
                  onClick={() => setShowEdit(true)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-white/40 text-white hover:border-white rounded-none transition-colors"
                  style={BC}
                  data-testid="team-detail-page-suggest-edit-btn"
                >
                  <Pencil className="w-3 h-3" /> Suggest Edit
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── INFOS + VENUE ────────────────────────────────────────────────── */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
          <TeamInfoCard team={team} />
          <VenueCard team={team} />
        </div>

        {/* ── KITS ─────────────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 mb-5">
          <Shirt className="w-4 h-4 text-muted-foreground" />
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground" style={BC}>Kits</p>
          <div className="flex-1 border-t border-border ml-1" />
          <span className="font-mono text-xs text-muted-foreground">
            {filteredKits.length}{filteredKits.length !== kits.length && `/${kits.length}`}
          </span>
        </div>

        {kits.length > 0 && (
          <div className="flex flex-wrap gap-3 mb-6">
            <select
              value={filterSeason}
              onChange={e => setFilterSeason(e.target.value)}
              className="h-9 px-3 bg-card border border-border rounded-none text-sm text-foreground"
              data-testid="team-detail-page-filter-season"
            >
              <option value="">All Seasons</option>
              {seasons.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <select
              value={filterBrand}
              onChange={e => setFilterBrand(e.target.value)}
              className="h-9 px-3 bg-card border border-border rounded-none text-sm text-foreground"
              data-testid="team-detail-page-filter-brand"
            >
              <option value="">All Brands</option>
              {brands.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
        )}

        {kits.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-border">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
            <p className="text-sm text-muted-foreground" style={DM}>No kits found for this team</p>
          </div>
        ) : filteredKits.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm text-muted-foreground" style={DM}>No kits match the selected filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
            {filteredKits.map(kit => (
              <JerseyCard key={kit.kit_id} kit={kit} />
            ))}
          </div>
        )}
      </div>

      {/* ── Suggest Edit Dialog ───────────────────────────────────────── */}
      {showEdit && (
        <EntityEditDialog
          open={showEdit}
          onOpenChange={setShowEdit}
          entityType="team"
          mode="edit"
          initialData={team}
          entityId={team.team_id}
          onSuccess={loadData}
        />
      )}
    </div>
  );
}
