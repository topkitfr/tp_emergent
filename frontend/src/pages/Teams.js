// frontend/src/pages/Teams.js
import React, { useState, useEffect, useCallback } from 'react';
import { getTeams } from '@/lib/api';
import { Shield, MapPin } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';

const PAGE_SIZE = 48;

export default function Teams() {
  const [teams, setTeams]         = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]       = useState('');
  const [country, setCountry]     = useState('');

  // Reset page quand les filtres changent
  useEffect(() => { setPage(1); }, [search, country]);

  const fetchTeams = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search)  params.search  = search;
      if (country) params.country = country;
      const res = await getTeams(params);
      const data = res.data;
      // Support both paginated {results, total} and legacy array
      if (Array.isArray(data)) {
        const filtered = data.filter(t => t.status !== 'rejected');
        setTeams(filtered);
        setTotal(filtered.length);
      } else {
        setTeams((data.results || []).filter(t => t.status !== 'rejected'));
        setTotal(data.total ?? 0);
      }
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country, page]);

  useEffect(() => { fetchTeams(); }, [fetchTeams]);

  const countries = [...new Set(teams.map(t => t.country).filter(Boolean))].sort();

  return (
    <>
      <EntityListPage
        title="TEAMS"
        icon={Shield}
        entities={teams}
        loading={loading}
        search={search}
        onSearchChange={setSearch}
        totalLabel="teams"
        onAddNew={() => setAddDialogOpen(true)}
        testId="teams-page"
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
        renderCard={team => (
          <EntityCard
            key={team.team_id}
            to={`/teams/${team.slug || team.team_id}`}
            image={team.crest_url}
            icon={Shield}
            name={team.name}
            meta={[
              team.country ? { icon: MapPin, text: team.country } : null,
              team.city ? { text: team.city } : null,
            ].filter(Boolean)}
            badges={[
              { label: `${team.kit_count ?? 0} kits`, variant: 'secondary' },
              team.founded ? { label: `Est. ${team.founded}`, variant: 'outline' } : null,
            ].filter(Boolean)}
            testId={`team-card-${team.team_id}`}
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
        entityType="team"
        onSuccess={fetchTeams}
      />
    </>
  );
}
