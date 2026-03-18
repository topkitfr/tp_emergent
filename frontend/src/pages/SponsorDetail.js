// frontend/src/pages/SponsorDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Tag, Globe } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getSponsor, getSponsorKits } from '@/lib/api';

export default function SponsorDetail() {
  const { id } = useParams();

  const [sponsor, setSponsor]           = useState(null);
  const [loading, setLoading]           = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam,   setFilterTeam]   = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [sponsorRes, kitsRes] = await Promise.all([
        getSponsor(id),
        getSponsorKits(id),
      ]);
      if (!sponsorRes.data) { setSponsor(null); return; }
      setSponsor({
        ...sponsorRes.data,
        kits: (kitsRes.data || []).filter(k => k.status !== 'rejected'),
      });
    } catch {
      setSponsor(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;
  if (!sponsor) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Sponsor not found.</p>
    </div>
  );

  const kits    = sponsor.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teams   = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  return (
    <EntityDetailPage
      entityType="sponsor"
      entity={sponsor}
      entityId={sponsor.sponsor_id}
      backTo={{ path: '/database/sponsors', label: 'Sponsors' }}
      image={sponsor.logo_url}
      icon={Tag}
      title={sponsor.name}
      subtitle={
        <>
          {sponsor.country && (
            <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{sponsor.country}</span>
          )}
        </>
      }
      metaItems={[]}
      badges={[
        { label: `${kits.length} kit${kits.length !== 1 ? 's' : ''}`, variant: 'secondary' },
        { label: 'Sponsor', variant: 'outline' },
        sponsor.status === 'approved'
          ? { label: 'Approved', variant: 'secondary' }
          : { label: sponsor.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' },
      ]}
      kits={kits}
      filters={[
        { key: 'season', label: 'All Seasons', value: filterSeason, onChange: setFilterSeason, options: seasons },
        { key: 'club',   label: 'All Teams',   value: filterTeam,   onChange: setFilterTeam,   options: teams   },
      ]}
      onEditSuccess={loadData}
      testId="sponsor-detail-page"
    />
  );
}
