// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback } from 'react';
import { getPlayers, togglePlayerFollow } from '@/lib/api';
import { User } from 'lucide-react';
import EntityListPage from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';
import PlayerCard from '@/components/ui/playerscard';

const PAGE_SIZE = 48;

export default function Players() {
  const [players, setPlayers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    setPage(1);
  }, [search]);

  const fetchPlayers = useCallback(async () => {
    setLoading(true);

    try {
      const params = {
        skip: (page - 1) * PAGE_SIZE,
        limit: PAGE_SIZE,
      };

      if (search) {
        params.search = search;
      }

      const res = await getPlayers(params);
      const data = res.data;

      if (Array.isArray(data)) {
        const filtered = data.filter((p) => p.status !== 'rejected');
        setPlayers(filtered);
        setTotal(filtered.length);
      } else {
        const filtered = (data.results || []).filter(
          (p) => p.status !== 'rejected'
        );
        setPlayers(filtered);
        setTotal(data.total ?? filtered.length);
      }
    } catch (error) {
      console.error('Failed to load players:', error);
      setPlayers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const handleFollowToggle = useCallback(async (playerId, nextFollowed) => {
    let previousPlayer = null;

    setPlayers((prev) =>
      prev.map((player) => {
        const currentId = player.player_id || player._id;

        if (currentId === playerId) {
          previousPlayer = player;
          return {
            ...player,
            is_followed: nextFollowed,
            followed: nextFollowed,
          };
        }

        return player;
      })
    );

    try {
      await togglePlayerFollow(playerId, nextFollowed);
    } catch (error) {
      console.error('Failed to update player follow state:', error);

      setPlayers((prev) =>
        prev.map((player) => {
          const currentId = player.player_id || player._id;

          if (currentId === playerId && previousPlayer) {
            return previousPlayer;
          }

          return player;
        })
      );
    }
  }, []);

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
        renderCard={(player) => (
          <PlayerCard
            key={player.player_id || player._id}
            player={player}
            isFollowed={!!(player.is_followed ?? player.followed)}
            onFollowToggle={handleFollowToggle}
          />
        )}
        footer={
          <Pagination
            page={page}
            total={total}
            pageSize={PAGE_SIZE}
            onChange={(p) => {
              setPage(p);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
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