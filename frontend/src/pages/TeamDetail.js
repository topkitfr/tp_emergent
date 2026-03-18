// frontend/src/pages/TeamDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Shield, Globe, MapPin, Calendar } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getTeam } from '@/lib/api';
import api from '@/lib/api';

export default function TeamDetail() {
  const { id } = useParams();
  const [team, setTeam]         = useState(null);
  const [loading, setLoading]   = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterBrand,  setFilterBrand]  = useState('');

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
    />
  );
}
