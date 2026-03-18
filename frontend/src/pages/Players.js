// frontend/src/pages/Players.js
import React, { useState, useEffect, useCallback } from 'react';
import { getPlayers } from '@/lib/api';
import { User, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';

const POSITIONS = ['GK', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'CDM', 'CM', 'CAM', 'LM', 'RM', 'LW', 'RW', 'SS', 'CF', 'ST'];

export default function Players() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [nationality, setNationality] = useState('');
  const [position, setPosition] = useState('');

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (nationality) params.nationality = nationality;
      const res = await getPlayers(params);
      let data = (res.data || []).filter(p => p.status !== 'rejected');
      if (position) data = data.filter(p => p.positions?.includes(position));
      setPlayers(data);
    } catch { } finally {
      setLoading(false);
    }
  }, [search, nationality, position]);

  useEffect(() => { fetchPlayers(); }, [fetchPlayers]);

  const nationalities = [...new Set(players.map(p => p.nationality).filter(Boolean))].sort();

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
      emptyMessage="Players are linked to jersey versions"
      filters={[
        {
          key: 'nationality',
          label: 'All Nationalities',
          value: nationality,
          onChange: setNationality,
          options: nationalities,
        },
        {
          key: 'position',
          label: 'All Positions',
          value: position,
          onChange: setPosition,
          options: POSITIONS,
        },
      ]}
      renderCard={player => (
        <EntityCard
          key={player.player_id}
          to={`/players/${player.slug || player.player_id}`}
          image={player.photo_url}
          icon={User}
          name={player.full_name}
          meta={[
            player.nationality ? { icon: Globe, text: player.nationality } : null,
            player.birth_year ? { text: `Born ${player.birth_year}` } : null,
          ].filter(Boolean)}
          badges={[
            ...(player.positions?.slice(0, 2).map(p => ({ label: p, variant: 'outline' })) || []),
            player.preferred_number ? { label: `#${player.preferred_number}`, variant: 'secondary' } : null,
            { label: `${player.kit_count ?? 0} versions`, variant: 'secondary' },
          ].filter(Boolean)}
          testId={`player-card-${player.player_id}`}
        />
      )}
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
