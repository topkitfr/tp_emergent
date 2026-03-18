// frontend/src/pages/Leagues.js
import React, { useState, useEffect, useCallback } from 'react';
import { getLeagues } from '@/lib/api';
import { Trophy, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';

export default function Leagues() {
  const [leagues, setLeagues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [level, setLevel] = useState('');
  const [region, setRegion] = useState('');

  const fetchLeagues = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (level) params.level = level;
      if (region) params.country_or_region = region;
      const res = await getLeagues(params);
      setLeagues((res.data || []).filter(l => l.status !== 'rejected'));
    } catch { } finally {
      setLoading(false);
    }
  }, [search, level, region]);

  useEffect(() => { fetchLeagues(); }, [fetchLeagues]);

  const regions = [...new Set(leagues.map(l => l.country_or_region).filter(Boolean))].sort();

  return (
    <EntityListPage
      title="LEAGUES"
      icon={Trophy}
      entities={leagues}
      loading={loading}
      search={search}
      onSearchChange={setSearch}
      totalLabel="leagues"
      testId="leagues-page"
      emptyMessage="Try a different search or filter"
      filters={[
        {
          key: 'level',
          label: 'All Levels',
          value: level,
          onChange: setLevel,
          options: [
            { value: 'domestic', label: 'Domestic' },
            { value: 'continental', label: 'Continental' },
            { value: 'international', label: 'International' },
            { value: 'cup', label: 'Cup' },
          ],
        },
        {
          key: 'region',
          label: 'All Regions',
          value: region,
          onChange: setRegion,
          options: regions,
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
            league.country_or_region ? { icon: Globe, text: league.country_or_region } : null,
            league.organizer ? { text: league.organizer } : null,
          ].filter(Boolean)}
          badges={[
            { label: `${league.kit_count ?? 0} kits`, variant: 'secondary' },
            league.level ? { label: league.level, variant: 'outline' } : null,
          ].filter(Boolean)}
          testId={`league-card-${league.league_id}`}
        />
      )}
    />
  );
}
