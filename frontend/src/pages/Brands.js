// frontend/src/pages/Brands.js
import React, { useState, useEffect, useCallback } from 'react';
import { getBrands } from '@/lib/api';
import { Tag, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';

export default function Brands() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');

  const fetchBrands = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (country) params.country = country;
      const res = await getBrands(params);
      setBrands((res.data || []).filter(b => b.status !== 'rejected'));
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country]);

  useEffect(() => { fetchBrands(); }, [fetchBrands]);

  const countries = [...new Set(brands.map(b => b.country).filter(Boolean))].sort();

  return (
    <EntityListPage
      title="BRANDS"
      icon={Tag}
      entities={brands}
      loading={loading}
      search={search}
      onSearchChange={setSearch}
      totalLabel="brands"
      testId="brands-page"
      emptyMessage="Try a different search or filter"
      filters={[
        {
          key: 'country',
          label: 'All Countries',
          value: country,
          onChange: setCountry,
          options: countries,
        },
      ]}
      renderCard={brand => (
        <EntityCard
          key={brand.brand_id}
          to={`/brands/${brand.slug || brand.brand_id}`}
          image={brand.logo_url}
          icon={Tag}
          name={brand.name}
          meta={[
            brand.country ? { icon: Globe, text: brand.country } : null,
          ].filter(Boolean)}
          badges={[
            { label: `${brand.kit_count ?? 0} kits`, variant: 'secondary' },
            brand.founded ? { label: `Est. ${brand.founded}`, variant: 'outline' } : null,
          ].filter(Boolean)}
          testId={`brand-card-${brand.brand_id}`}
        />
      )}
    />
  );
}
