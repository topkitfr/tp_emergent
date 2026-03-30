// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback } from 'react';
import { getPlayers, togglePlayerFollow } from '@/lib/api';
import { User } from 'lucide-react';
import EntityListPage from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';
import Pagination from '@/components/Pagination';
import PlayerCard from '@/components/ui/playerscard';
import './Players.css';

const PAGE_SIZE = 48;

let _diagDone = false;
function diagPlayer(player) {
  if (_diagDone) return;
  _diagDone = true;
  const imageFields = Object.entries(player).filter(([k, v]) =>
    k.toLowerCase().includes('image') || k.toLowerCase().includes('photo') ||
    k.toLowerCase().includes('img')   || k.toLowerCase().includes('avatar') ||
    k.toLowerCase().includes('picture') || k.toLowerCase().includes('headshot') ||
    (typeof v === 'string' && (v.startsWith('http') || v.startsWith('/')))
  );
  const auraFields = Object.entries(player).filter(([k]) =>
    k.toLowerCase().includes('aura') || k.toLowerCase().includes('star') ||
    k.toLowerCase().includes('rating') || k.toLowerCase().includes('score') ||
    k.toLowerCase().includes('note')   || k.toLowerCase().includes('grade') ||
    k.toLowerCase().includes('community')
  );
  console.group('🔍 [Players] Diagnostic shape joueur');
  console.log('Tous les champs :', Object.keys(player));
  console.log('📸 Champs image :', imageFields.map(([k,v]) => `${k}: ${v}`));
  console.log('⭐ Champs note  :', auraFields.map(([k,v]) => `${k}: ${v}`));
  console.groupEnd();
}

export default function Players() {
  const [players, setPlayers]           = useState([]);
  const [total, setTotal]               = useState(0);
  const [page, setPage]                 = useState(1);
  const [loading, setLoading]           = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]             = useState('');

  useEffect(() => { setPage(1); }, [search]);

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE };
      if (search) params.search = search;

      const res = await getPlayers(params);
      let rawList = [], rawTotal = 0;

      if (Array.isArray(res.data)) {
        rawList = res.data; rawTotal = res.data.length;
      } else if (res.data?.results) {
        rawList = res.data.results; rawTotal = res.data.total ?? rawList.length;
      } else if (res.data?.players) {
        rawList = res.data.players; rawTotal = res.data.total ?? rawList.length;
      } else if (res.data?.items) {
        rawList = res.data.items; rawTotal = res.data.total ?? rawList.length;
      }

      const filtered = rawList.filter(p => p.status !== 'rejected');
      if (filtered.length > 0) diagPlayer(filtered[0]);
      setPlayers(filtered);
      setTotal(rawTotal);
    } catch (err) {
      console.error('[Players] fetchPlayers error:', err);
      setPlayers([]); setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [search, page]);

  useEffect(() => { fetchPlayers(); }, [fetchPlayers]);

  const handleFollowToggle = useCallback(async (playerId, nextFollowed) => {
    let prev = null;
    setPlayers(list => list.map(p => {
      const id = p._id ?? p.player_id ?? p.id;
      if (id === playerId) { prev = p; return { ...p, is_followed: nextFollowed, followed: nextFollowed }; }
      return p;
    }));
    try { await togglePlayerFollow(playerId, nextFollowed); }
    catch (err) {
      console.error('[Players] follow error:', err);
      setPlayers(list => list.map(p => {
        const id = p._id ?? p.player_id ?? p.id;
        return id === playerId && prev ? prev : p;
      }));
    }
  }, []);

  // ── Grille 5 colonnes (injectée par-dessus EntityListPage) ───────────────
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(5, 1fr)',
    gap: '12px',
  };

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
        gridStyle={gridStyle}          // ← si EntityListPage le supporte
        gridClassName="players-grid"   // ← sinon on utilise la classe CSS ci-dessous
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
            onChange={(p) => { setPage(p); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
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