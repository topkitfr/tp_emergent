// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback } from 'react';
import { getPlayers } from '@/lib/api';
import { User } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';

const PAGE_SIZE = 48;

export default function Players() {
  const [players, setPlayers]     = useState([]);
  const [total, setTotal]         = useState(0);
  const [page, setPage]           = useState(1);
  const [loading, setLoading]     = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]       = useState('');

  useEffect(() => { setPage(1); }, [search]);

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search) params.search = search;
      const res = await getPlayers(params);
      const data = res.data;
      if (Array.isArray(data)) {
        const filtered = data.filter(p => p.status !== 'rejected');
        setPlayers(filtered);
        setTotal(filtered.length);
      } else {
        setPlayers((data.results || []).filter(p => p.status !== 'rejected'));
        setTotal(data.total ?? 0);
      }
    } catch { } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => { fetchPlayers(); }, [fetchPlayers]);

  return (
    <>
      <EntityListPage
        title="PLAYERS"
        icon={User}
        entities={players}
        loading={loading}
        search={search}
        onSearchChange={setSearch}
        totalLabel="players"
        onAddNew={() => setAddDialogOpen(true)}
        testId="players-page"
        emptyMessage="Try a different search or filter"
        filters={[]}
        renderCard={player => (
          <EntityCard
            key={player.player_id}
            to={`/players/${player.slug || player.player_id}`}
            image={player.photo_url}
            icon={User}
            name={player.name}
            meta={[
              player.nationality ? { text: player.nationality } : null,
            ].filter(Boolean)}
            badges={[
              { label: `${player.kit_count ?? 0} kits`, variant: 'secondary' },
            ]}
            testId={`player-card-${player.player_id}`}
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
        entityType="player"
        onSuccess={fetchPlayers}
      />
    </>
  );
}
