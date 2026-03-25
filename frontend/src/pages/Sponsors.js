// frontend/src/pages/Sponsors.js
import React, { useState, useEffect, useCallback } from 'react';
import { getSponsors } from '@/lib/api';
import { Briefcase } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';

const PAGE_SIZE = 48;

export default function Sponsors() {
  const [sponsors, setSponsors]   = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]       = useState('');

  useEffect(() => { setPage(1); }, [search]);

  const fetchSponsors = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search) params.search = search;
      const res = await getSponsors(params);
      const data = res.data;
      if (Array.isArray(data)) {
        const filtered = data.filter(s => s.status !== 'rejected');
        setSponsors(filtered);
        setTotal(filtered.length);
      } else {
        setSponsors((data.results || []).filter(s => s.status !== 'rejected'));
        setTotal(data.total ?? 0);
      }
    } catch { } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => { fetchSponsors(); }, [fetchSponsors]);

  return (
    <>
      <EntityListPage
        title="SPONSORS"
        icon={Briefcase}
        entities={sponsors}
        loading={loading}
        search={search}
        onSearchChange={setSearch}
        totalLabel="sponsors"
        onAddNew={() => setAddDialogOpen(true)}
        testId="sponsors-page"
        emptyMessage="Try a different search or filter"
        filters={[]}
        renderCard={sponsor => (
          <EntityCard
            key={sponsor.sponsor_id}
            to={`/sponsors/${sponsor.slug || sponsor.sponsor_id}`}
            image={sponsor.logo_url}
            icon={Briefcase}
            name={sponsor.name}
            meta={[]}
            badges={[
              { label: `${sponsor.kit_count ?? 0} kits`, variant: 'secondary' },
            ]}
            testId={`sponsor-card-${sponsor.sponsor_id}`}
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
        entityType="sponsor"
        onSuccess={fetchSponsors}
      />
    </>
  );
}
