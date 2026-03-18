// frontend/src/pages/LeagueDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Trophy, Globe, Layers } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getLeague } from '@/lib/api';
import api from '@/lib/api';

export default function LeagueDetail() {
  const { id } = useParams();
  const [league, setLeague]       = useState(null);
  const [loading, setLoading]     = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam,   setFilterTeam]   = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [leagueRes, kitsRes] = await Promise.all([
        getLeague(id),
        api.get(`/leagues/${id}/kits`),
      ]);
      setLeague({
        ...leagueRes.data,
        kits: (kitsRes.data || []).filter(k => k.status !== 'rejected'),
      });
    } catch {
      setLeague(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;
  if (!league) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">League not found</p>
    </div>
  );

  const kits    = league.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teams   = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  return (
    <EntityDetailPage
      entityType="league"
      entity={league}
      entityId={league.league_id}
      backTo={{ path: '/database/leagues', label: 'Leagues' }}
      image={league.logo_url}
      icon={Trophy}
      title={league.name}
      subtitle={
        <>
          {league.country_or_region && (
            <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{league.country_or_region}</span>
          )}
          {league.level && (
            <span className="flex items-center gap-1"><Layers className="w-3.5 h-3.5" />{league.level}</span>
          )}
        </>
      }
      metaItems={[
        league.organizer
          ? <span key="org" className="flex items-center gap-1"><Trophy className="w-3.5 h-3.5" />{league.organizer}</span>
          : null,
      ].filter(Boolean)}
      badges={[
        { label: `${league.kit_count ?? kits.length} kits`, variant: 'secondary' },
        { label: 'League', variant: 'outline' },
        league.status === 'approved'
          ? { label: 'Approved', variant: 'secondary' }
          : { label: league.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' },
      ]}
      kits={kits}
      filters={[
        { key: 'season', label: 'All Seasons', value: filterSeason, onChange: setFilterSeason, options: seasons },
        { key: 'club',   label: 'All Clubs',   value: filterTeam,   onChange: setFilterTeam,   options: teams   },
      ]}
      onEditSuccess={loadData}
      testId="league-detail-page"
    />
  );
}
