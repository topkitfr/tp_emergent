// frontend/src/pages/Brands.js
import React, { useState, useEffect, useCallback } from 'react';
import { getBrands } from '@/lib/api';
import { Tag, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';

const PAGE_SIZE = 48;

export default function Brands() {
  const [brands, setBrands]       = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]       = useState('');
  const [country, setCountry]     = useState('');

  useEffect(() => { setPage(1); }, [search, country]);

  const fetchBrands = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search)  params.search  = search;
      if (country) params.country = country;
      const res = await getBrands(params);
      const data = res.data;
      if (Array.isArray(data)) {
        const filtered = data.filter(b => b.status !== 'rejected');
        setBrands(filtered);
        setTotal(filtered.length);
      } else {
        setBrands((data.results || []).filter(b => b.status !== 'rejected'));
        setTotal(data.total ?? 0);
      }
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country, page]);

  useEffect(() => { fetchBrands(); }, [fetchBrands]);

  const countries = [...new Set(brands.map(b => b.country).filter(Boolean))].sort();

  return (
    <>
      <EntityListPage
        title="BRANDS"
        icon={Tag}
        entities={brands}
        loading={loading}
        search={search}
        onSearchChange={setSearch}
        totalLabel="brands"
        onAddNew={() => setAddDialogOpen(true)}
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
        footer={
          <Pagination
            page={page}
            total={total}
            pageSize={PAGE_SIZE}
            onChange={p => { setPage(p); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          />
        }
      />
      <AddEntityDialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        entityType="brand"
        onSuccess={fetchBrands}
      />
    </>
  );
}
