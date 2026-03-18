// frontend/src/pages/Teams.js
import React, { useState, useEffect, useCallback } from 'react';
import { getTeams } from '@/lib/api';
import { Shield, MapPin } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';

export default function Teams() {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');

  const fetchTeams = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (country) params.country = country;
      const res = await getTeams(params);
      setTeams((res.data || []).filter(t => t.status !== 'rejected'));
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country]);

  useEffect(() => { fetchTeams(); }, [fetchTeams]);

  const countries = [...new Set(teams.map(t => t.country).filter(Boolean))].sort();

  return (
    <EntityListPage
      title="TEAMS"
      icon={Shield}
      entities={teams}
      loading={loading}
      search={search}
      onSearchChange={setSearch}
      totalLabel="teams"
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
    />
  );
}
