// frontend/src/pages/Sponsors.js
import React, { useState, useEffect, useCallback } from 'react';
import { getSponsors } from '@/lib/api';
import { Tag, Globe } from 'lucide-react';
import EntityListPage, { EntityCard } from '@/components/EntityListPage';
import AddEntityDialog from '@/components/AddEntityDialog';

export default function Sponsors() {
  const [sponsors, setSponsors]         = useState([]);
  const [loading, setLoading]           = useState(true);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [search, setSearch]             = useState('');
  const [country, setCountry]           = useState('');

  const fetchSponsors = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search)  params.search  = search;
      if (country) params.country = country;
      const res = await getSponsors(params);
      setSponsors((res.data || []).filter(s => s.status !== 'rejected'));
    } catch { } finally {
      setLoading(false);
    }
  }, [search, country]);

  useEffect(() => { fetchSponsors(); }, [fetchSponsors]);

  const countries = [...new Set(sponsors.map(s => s.country).filter(Boolean))].sort();

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
      renderCard={sponsor => (
        <EntityCard
          key={sponsor.sponsor_id}
          to={`/database/sponsors/${sponsor.slug || sponsor.sponsor_id}`}
          image={sponsor.logo_url}
          icon={Tag}
          name={sponsor.name}
          meta={[
            sponsor.country ? { icon: Globe, text: sponsor.country } : null,
          ].filter(Boolean)}
          badges={[
            { label: `${sponsor.kit_count ?? 0} kit${(sponsor.kit_count ?? 0) !== 1 ? 's' : ''}`, variant: 'secondary' },
            sponsor.status !== 'approved'
              ? { label: sponsor.status === 'for_review' ? 'For Review' : 'Pending', variant: 'outline' }
              : null,
          ].filter(Boolean)}
          testId={`sponsor-card-${sponsor.sponsor_id}`}
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
