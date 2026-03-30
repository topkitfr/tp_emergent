// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback } from 'react';
import { getPlayers, followEntity, unfollowEntity } from '@/lib/api';
import { User } from 'lucide-react';
import { toast } from 'react-hot-toast';
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

      if (search) params.search = search;

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
        setTotal(data.total ?? 0);
      }
    } catch (error) {
      toast.error('Impossible de charger les joueurs');
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const handleFollowToggle = useCallback(async (playerId, nextFollowed) => {
    let rollbackPlayer = null;

    // Optimistic UI
    setPlayers((prev) =>
      prev.map((player) => {
        const currentId = player.player_id || player._id;
        if (currentId === playerId) {
          rollbackPlayer = player;
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
      const payload = { type: 'player', id: playerId };

      if (nextFollowed) {
        await followEntity(payload);
        toast.success('Joueur ajouté aux suivis');
      } else {
        await unfollowEntity(payload);
        toast.success('Joueur retiré des suivis');
      }
    } catch (error) {
      // rollback
      setPlayers((prev) =>
        prev.map((player) => {
          const currentId = player.player_id || player._id;
          if (currentId === playerId && rollbackPlayer) {
            return rollbackPlayer;
          }
          return player;
        })
      );

      toast.error('Impossible de mettre à jour le suivi');
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