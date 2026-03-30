// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { getPlayers, togglePlayerFollow } from '@/lib/api';
import { User } from 'lucide-react';
import EntityListPage from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';
import PlayerCard from '@/components/ui/playerscard';

const PAGE_SIZE = 48;

// ── Diagnostic une seule fois pour trouver les bons champs ────────────────
let _diagDone = false;
function diagPlayer(player) {
  if (_diagDone) return;
  _diagDone = true;

  const imageFields = Object.entries(player).filter(([k, v]) =>
    k.toLowerCase().includes('image') ||
    k.toLowerCase().includes('photo') ||
    k.toLowerCase().includes('img') ||
    k.toLowerCase().includes('avatar') ||
    k.toLowerCase().includes('picture') ||
    k.toLowerCase().includes('headshot') ||
    k.toLowerCase().includes('thumbnail') ||
    (typeof v === 'string' && (v.startsWith('http') || v.startsWith('/')))
  );

  const auraFields = Object.entries(player).filter(([k]) =>
    k.toLowerCase().includes('aura') ||
    k.toLowerCase().includes('star') ||
    k.toLowerCase().includes('rating') ||
    k.toLowerCase().includes('score') ||
    k.toLowerCase().includes('note') ||
    k.toLowerCase().includes('grade') ||
    k.toLowerCase().includes('community')
  );

  console.group('🔍 [Players] Diagnostic shape joueur');
  console.log('Tous les champs:', Object.keys(player));
  console.log('');
  console.log('📸 Champs image suspects:');
  imageFields.forEach(([k, v]) => console.log(`  ${k}:`, v));
  console.log('');
  console.log('⭐ Champs note/aura suspects:');
  auraFields.forEach(([k, v]) => console.log(`  ${k}:`, v));
  console.groupEnd();
}

export default function Players() {
  const [players, setPlayers]       = useState([]);
  const [total, setTotal]           = useState(0);
  const [page, setPage]             = useState(1);
  const [loading, setLoading]       = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]         = useState('');

  // Reset page à 1 quand la recherche change
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

      // ── Normalisation de la réponse (plusieurs shapes possibles) ──
      let rawList = [];
      let rawTotal = 0;

      if (Array.isArray(res.data)) {
        rawList  = res.data;
        rawTotal = res.data.length;
      } else if (res.data && Array.isArray(res.data.results)) {
        rawList  = res.data.results;
        rawTotal = res.data.total ?? res.data.count ?? rawList.length;
      } else if (res.data && Array.isArray(res.data.players)) {
        rawList  = res.data.players;
        rawTotal = res.data.total ?? res.data.count ?? rawList.length;
      } else if (res.data && Array.isArray(res.data.items)) {
        rawList  = res.data.items;
        rawTotal = res.data.total ?? res.data.count ?? rawList.length;
      } else {
        console.warn('[Players] Shape de réponse inattendu:', res.data);
      }

      // Filtrer les rejected
      const filtered = rawList.filter((p) => p.status !== 'rejected');

      // Diagnostic sur le premier joueur
      if (filtered.length > 0) diagPlayer(filtered[0]);

      setPlayers(filtered);
      setTotal(rawTotal);
    } catch (error) {
      console.error('[Players] Erreur fetchPlayers:', error);
      setPlayers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  // ── Follow/unfollow optimiste avec rollback ────────────────────────────
  const handleFollowToggle = useCallback(async (playerId, nextFollowed) => {
    let previousPlayer = null;

    setPlayers((prev) =>
      prev.map((player) => {
        const id = player._id ?? player.player_id ?? player.id;
        if (id === playerId) {
          previousPlayer = player;
          return { ...player, is_followed: nextFollowed, followed: nextFollowed };
        }
        return player;
      })
    );

    try {
      await togglePlayerFollow(playerId, nextFollowed);
    } catch (error) {
      console.error('[Players] Erreur follow toggle:', error);
      // Rollback
      setPlayers((prev) =>
        prev.map((player) => {
          const id = player._id ?? player.player_id ?? player.id;
          return id === playerId && previousPlayer ? previousPlayer : player;
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
            key={player._id ?? player.player_id ?? player.id}
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