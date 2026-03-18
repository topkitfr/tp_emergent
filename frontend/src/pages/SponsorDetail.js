// frontend/src/pages/SponsorDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Tag, Globe } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getMasterKits } from '@/lib/api';
import api from '@/lib/api';

export default function SponsorDetail() {
  const { name }    = useParams();
  const decodedName = decodeURIComponent(name || '');

  const [sponsor, setSponsor] = useState(null);
  const [kits, setKits]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam,   setFilterTeam]   = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const slug = decodedName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');

      const [sRes, kRes] = await Promise.all([
        api.get(`/sponsors/${slug}`).catch(() => ({ data: null })),
        getMasterKits({ limit: 2000 }),
      ]);

      setSponsor(sRes.data || null);
      const allKits = kRes.data || [];
      setKits(
        allKits.filter(
          k => (k.sponsor || '').trim().toLowerCase() === decodedName.trim().toLowerCase()
              && k.status !== 'rejected'
        )
      );
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [decodedName]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;

  if (!sponsor && !kits.length) return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Sponsor not found.</p>
    </div>
  );

  const seasons   = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teamNames = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  // entity peut être null si sponsor pas encore en DB
  const entity = sponsor || { name: decodedName, status: null };

  return (
    <EntityDetailPage
      entityType="sponsor"
      entity={entity}
      entityId={sponsor?.sponsor_id || null}
      backTo={{ path: '/database/sponsors', label: 'Sponsors' }}
      image={sponsor?.logo_url}
      icon={Tag}
      title={sponsor?.name || decodedName}
      subtitle={
        <>
          {sponsor?.country && (
            <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{sponsor.country}</span>
          )}
        </>
      }
      metaItems={[]}
      badges={[
        { label: `${kits.length} kit${kits.length !== 1 ? 's' : ''}`, variant: 'secondary' },
        sponsor?.status
          ? (sponsor.status === 'approved'
              ? { label: 'Approved', variant: 'secondary' }
              : { label: sponsor.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' })
          : null,
      ].filter(Boolean)}
      kits={kits}
      filters={[
        { key: 'season', label: 'All Seasons', value: filterSeason, onChange: setFilterSeason, options: seasons },
        { key: 'club',   label: 'All Teams',   value: filterTeam,   onChange: setFilterTeam,   options: teamNames },
      ]}
      onEditSuccess={loadData}
      testId="sponsor-detail-page"
    />
  );
}
