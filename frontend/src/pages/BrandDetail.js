// frontend/src/pages/BrandDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Zap, Globe, Calendar } from 'lucide-react';
import EntityDetailPage, { EntityDetailSkeleton } from '@/components/EntityDetailPage';
import { getBrand } from '@/lib/api';
import api from '@/lib/api';

export default function BrandDetail() {
  const { id } = useParams();
  const [brand, setBrand]         = useState(null);
  const [loading, setLoading]     = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam,   setFilterTeam]   = useState('');

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [brandRes, kitsRes] = await Promise.all([
        getBrand(id),
        api.get(`/brands/${id}/kits`),
      ]);
      if (!brandRes.data) { setBrand(null); return; }
      setBrand({
        ...brandRes.data,
        kits: (kitsRes.data || []).filter(k => k.status !== 'rejected'),
      });
    } catch {
      setBrand(null);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <EntityDetailSkeleton />;
  if (!brand)  return (
    <div className="px-4 lg:px-8 py-16 text-center">
      <p className="text-muted-foreground">Brand not found</p>
    </div>
  );

  const kits    = brand.kits || [];
  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teams   = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  return (
    <EntityDetailPage
      entityType="brand"
      entity={brand}
      entityId={brand.brand_id}
      backTo={{ path: '/database/brands', label: 'Brands' }}
      image={brand.logo_url}
      icon={Zap}
      title={brand.name}
      subtitle={
        <>
          {brand.country && (
            <span className="flex items-center gap-1"><Globe className="w-3.5 h-3.5" />{brand.country}</span>
          )}
        </>
      }
      metaItems={[
        brand.founded
          ? <span key="founded" className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />Founded {brand.founded}</span>
          : null,
      ].filter(Boolean)}
      badges={[
        { label: `${brand.kit_count ?? kits.length} kits`, variant: 'secondary' },
        { label: 'Brand', variant: 'outline' },
        brand.status === 'approved'
          ? { label: 'Approved', variant: 'secondary' }
          : { label: brand.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' },
      ]}
      kits={kits}
      filters={[
        { key: 'season', label: 'All Seasons', value: filterSeason, onChange: setFilterSeason, options: seasons },
        { key: 'club',   label: 'All Clubs',   value: filterTeam,   onChange: setFilterTeam,   options: teams   },
      ]}
      onEditSuccess={loadData}
      testId="brand-detail-page"
    />
  );
}
