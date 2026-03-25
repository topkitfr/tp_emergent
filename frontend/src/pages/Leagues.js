// frontend/src/pages/Leagues.js
import React, { useState, useEffect, useCallback } from 'react';
import { getLeagues } from '@/lib/api';
import { Trophy, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';

const PAGE_SIZE = 48;

export default function Leagues() {
  const [leagues, setLeagues]     = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]       = useState('');
  const [country, setCountry]     = useState('');

  useEffect(() => { setPage(1); }, [search, country]);

  const fetchLeagues = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search)  params.search  = search;
      if (country) params.country = country;
      const res = await getLeagues(params);
      const data = res.data;
      if (Array.isArray(data)) {
        const filtered = data.filter(l => l.status !== 'rejected');
        setLeagues(filtered);
        setTotal(filtered.length);
      } else {
        setLeagues((data.results || []).filter(l => l.status !== 'rejected'));
        setTotal(data.total ?? 0);
      }
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country, page]);

  useEffect(() => { fetchLeagues(); }, [fetchLeagues]);

  const countries = [...new Set(leagues.map(l => l.country).filter(Boolean))].sort();

  return (
    <>
      <EntityListPage
        title="LEAGUES"
        icon={Trophy}
        entities={leagues}
        loading={loading}
        search={search}
        onSearchChange={setSearch}
        totalLabel="leagues"
        onAddNew={() => setAddDialogOpen(true)}
        testId="leagues-page"
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
        renderCard={league => (
          <EntityCard
            key={league.league_id}
            to={`/leagues/${league.slug || league.league_id}`}
            image={league.logo_url}
            icon={Trophy}
            name={league.name}
            meta={[
              league.country ? { icon: Globe, text: league.country } : null,
            ].filter(Boolean)}
            badges={[
              { label: `${league.kit_count ?? 0} kits`, variant: 'secondary' },
            ]}
            testId={`league-card-${league.league_id}`}
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
        entityType="league"
        onSuccess={fetchLeagues}
      />
    </>
  );
}
