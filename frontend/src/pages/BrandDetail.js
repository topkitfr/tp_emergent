// src/pages/BrandDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Shirt, Pencil } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';
import { proxyImageUrl } from '@/lib/api';

export default function BrandDetail() {
  const { id } = useParams(); // slug de la brand
  const { user } = useAuth();

  const [brand, setBrand] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam, setFilterTeam] = useState('');
  const [showEdit, setShowEdit] = useState(false);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        // Infos de la brand
        const brandRes = await fetch(`/api/brands/${id}`);
        if (!brandRes.ok) {
          setBrand(null);
          return;
        }
        const brandData = await brandRes.json();

        // Kits de la brand
        const kitsRes = await fetch(`/api/brands/${id}/kits`);
        const kitsData = await kitsRes.json();

        setBrand({
          ...brandData,
          kits: kitsData || [],
        });
      } catch (e) {
        console.error(e);
        setBrand(null);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  if (loading) {
    return (
      <div className="animate-fade-in-up px-4 lg:px-8 py-16">
        <div className="h-48 bg-card animate-pulse max-w-4xl mx-auto" />
      </div>
    );
  }

  if (!brand) {
    return (
      <div className="px-4 lg:px-8 py-16 text-center">
        <p className="text-muted-foreground">Brand not found</p>
      </div>
    );
  }

  const kits = brand.kits || [];

  const seasons = [...new Set(kits.map(k => k.season).filter(Boolean))].sort().reverse();
  const teamNames = [...new Set(kits.map(k => k.club).filter(Boolean))].sort();

  const filteredKits = kits.filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterTeam && k.club !== filterTeam) return false;
    return true;
  });

  return (
    <div className="animate-fade-in-up" data-testid="brand-detail-page">
      {/* Header */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <Link
            to="/brands"
            className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground mb-4"
            data-testid="back-to-brands"
          >
            <ArrowLeft className="w-3 h-3" />
            Brands
          </Link>

          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-secondary flex items-center justify-center shrink-0">
              {brand.logo_url ? (
                <img
                  src={proxyImageUrl(brand.logo_url)}
                  alt={brand.name}
                  className="w-16 h-16 object-contain"
                />
              ) : (
                <span className="text-xl font-semibold">{brand.name[0]}</span>
              )}
            </div>

            <div>
              <h1
                className="text-3xl sm:text-4xl tracking-tighter"
                data-testid="brand-name"
              >
                {brand.name}
              </h1>

              <div className="flex flex-wrap items-center gap-3 mt-2">
                {brand.country && (
                  <span
                    className="text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                  >
                    {brand.country}
                  </span>
                )}
                {brand.founded && (
                  <span
                    className="text-sm text-muted-foreground"
                    style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                  >
                    Since {brand.founded}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 mt-3">
                <Badge variant="secondary" className="rounded-none">
                  {brand.kit_count || kits.length} kits
                </Badge>

                {user && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-none border-border ml-2"
                    onClick={() => setShowEdit(true)}
                    data-testid="suggest-edit-brand-btn"
                  >
                    <Pencil className="w-3 h-3 mr-1" />
                    Suggest Edit
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {/* Filtres */}
        <div className="flex flex-wrap gap-3 mb-6">
          <select
            value={filterSeason}
            onChange={e => setFilterSeason(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="brand-filter-season"
          >
            <option value="">All Seasons</option>
            {seasons.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <select
            value={filterTeam}
            onChange={e => setFilterTeam(e.target.value)}
            className="h-9 px-3 bg-card border border-border rounded-none text-sm"
            data-testid="brand-filter-team"
          >
            <option value="">All Teams</option>
            {teamNames.map(t => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>

        {/* Grid de kits */}
        {filteredKits.length === 0 ? (
          <div className="text-center py-16">
            <Shirt className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p
              className="text-sm text-muted-foreground"
              style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
            >
              No kits found for this brand
            </p>
          </div>
        ) : (
          <div
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children"
            data-testid="brand-kits-grid"
          >
            {filteredKits.map(kit => (
              <JerseyCard
                key={kit.kit_id}
                kit={kit}
              />
            ))}
          </div>
        )}
      </div>

      {/* Dialog édition entité */}
      <EntityEditDialog
        open={showEdit}
        onOpenChange={setShowEdit}
        entityType="brand"
        mode="edit"
        entityId={brand.brand_id}
        initialData={{
          name: brand.name,
          country: brand.country,
          founded: brand.founded,
          logo_url: brand.logo_url,
        }}
        onSuccess={async () => {
          const res = await fetch(`/api/brands/${id}`);
          if (res.ok) {
            const data = await res.json();
            setBrand(prev => ({ ...(prev || {}), ...data }));
          }
        }}
      />
    </div>
  );
}
