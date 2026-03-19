// frontend/src/pages/TeamDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Shield, Globe, MapPin, Calendar, UserPlus, UserMinus } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getTeam, followEntity, unfollowEntity, isFollowing } from '@/lib/api';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function TeamDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [team, setTeam]         = useState(null);
  const [loading, setLoading]   = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterBrand,  setFilterBrand]  = useState('');
  const [following, setFollowing]       = useState(false);
  const [followLoading, setFollowLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [teamRes, kitsRes] = await Promise.all([
        getTeam(id),
        api.get(`/teams/${id}/kits`),
      ]);
      setTeam({
        ...teamRes.data,
        kits: (kitsRes.data || []).filter(k => k.status !== 'rejected'),
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
    isFollowing('team', id).then(r => setFollowing(r.data?.following || false)).catch(() => {});
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

  if (loading) return <EntityDetailSkeleton />;
  if (!team)   return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Team not found</p>
    </div>
  );

  const kits    = team.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const brands  = [...new Set(kits.map(k => k.brand).filter(Boolean))].sort();

  return (
    <EntityDetailPage
      entityType="team"
      entity={team}
      entityId={team.team_id}
      backTo={{ path: '/teams', label: 'Teams' }}
      image={team.crest_url}
      icon={Shield}
      title={team.name}
      subtitle={
        <>
          {team.country && <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{team.country}</span>}
          {team.city    && <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{team.city}</span>}
        </>
      }
      metaItems={[
        team.founded
          ? <span key="founded" className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />Founded {team.founded}</span>
          : null,
      ].filter(Boolean)}
      badges={[
        { label: `${team.kit_count ?? kits.length} kits`, variant: 'secondary' },
        team.status === 'approved'
          ? { label: 'Approved', variant: 'secondary' }
          : { label: team.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' },
      ]}
      kits={kits}
      filters={[
        { key: 'season', label: 'All Seasons', value: filterSeason, onChange: setFilterSeason, options: seasons },
        { key: 'brand',  label: 'All Brands',  value: filterBrand,  onChange: setFilterBrand,  options: brands  },
      ]}
      onEditSuccess={loadData}
      testId="team-detail-page"
      extraActions={
        user ? (
          <button
            onClick={handleFollow}
            disabled={followLoading}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border rounded-none transition-colors ${
              following
                ? 'bg-primary text-primary-foreground border-primary hover:bg-primary/80'
                : 'bg-transparent text-muted-foreground border-border hover:text-foreground hover:border-foreground'
            }`}
            data-testid="follow-btn"
          >
            {following
              ? <><UserMinus className="w-3.5 h-3.5" /> Unfollow</>
              : <><UserPlus  className="w-3.5 h-3.5" /> Follow</>}
          </button>
        ) : null
      }
    />
  );
}
