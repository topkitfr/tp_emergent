// frontend/src/pages/Sponsors.js
import React, { useState, useEffect, useCallback } from 'react';
import { getMasterKits } from '@/lib/api';
import { Tag } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';

export default function Sponsors() {
  const [sponsors, setSponsors] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState('');
  const [country, setCountry]   = useState('');

  const fetchSponsors = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getMasterKits({ limit: 2000 });
      const kits = res.data || [];

      // Agrégation par sponsor
      const map = {};
      for (const kit of kits) {
        const name = kit.sponsor?.trim();
        if (!name) continue;
        if (!map[name]) map[name] = { name, kit_count: 0, clubs: new Set(), seasons: new Set() };
        map[name].kit_count++;
        if (kit.club)   map[name].clubs.add(kit.club);
        if (kit.season) map[name].seasons.add(kit.season);
      }

      let list = Object.values(map).map(s => ({
        ...s,
        clubs:   [...s.clubs].slice(0, 3),
        seasons: [...s.seasons].sort().reverse(),
        // slug pour le lien
        slug: s.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''),
      })).sort((a, b) => b.kit_count - a.kit_count);

      if (search)  list = list.filter(s => s.name.toLowerCase().includes(search.toLowerCase()));
      if (country) list = list.filter(s => (s.country || '').toLowerCase().includes(country.toLowerCase()));

      setSponsors(list);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [search, country]);

  useEffect(() => { fetchSponsors(); }, [fetchSponsors]);

  return (
    <>
    <EntityListPage
      title="SPONSORS"
      icon={Tag}
      entities={sponsors}
      loading={loading}
      search={search}
      onSearchChange={setSearch}
      totalLabel="sponsors"
      onAddNew={() => setAddDialogOpen(true)}
      testId="sponsors-page"
      emptyMessage="Sponsors are extracted from jersey submissions"
      filters={[]}
      renderCard={sponsor => (
        <EntityCard
          key={sponsor.name}
          to={`/database/sponsors/${encodeURIComponent(sponsor.name)}`}
          icon={Tag}
          name={sponsor.name}
          meta={[
            sponsor.clubs.length > 0
              ? { text: sponsor.clubs.join(' · ') + (sponsor.clubs.length >= 3 ? ' …' : '') }
              : null,
            sponsor.seasons.length > 0
              ? { text: `${sponsor.seasons[sponsor.seasons.length - 1]}–${sponsor.seasons[0]}` }
              : null,
          ].filter(Boolean)}
          badges={[
            { label: `${sponsor.kit_count} kit${sponsor.kit_count !== 1 ? 's' : ''}`, variant: 'secondary' },
          ]}
          testId={`sponsor-card-${sponsor.name}`}
        />
      )}
    />
  <AddEntityDialog
    open={addDialogOpen}
    onClose={() => setAddDialogOpen(false)}
    entityType="sponsor"
    onSuccess={fetchSponsors}
  />
    </>
  );
}
