import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getBrands } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Tag, Globe } from 'lucide-react';

export default function Brands() {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchBrands = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      const res = await getBrands(params);
      setBrands(res.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { fetchBrands(); }, [fetchBrands]);

  return (
    <div className="animate-fade-in-up" data-testid="brands-page">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-4" data-testid="brands-title">BRANDS</h1>
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search brands..." value={search} onChange={e => setSearch(e.target.value)} className="pl-9 bg-card border-border rounded-none h-10" data-testid="brands-search" />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        <p className="text-sm text-muted-foreground mb-6"><span className="font-mono text-foreground">{brands.length}</span> brands</p>
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <div key={i} className="h-24 bg-card animate-pulse border border-border" />)}
          </div>
        ) : brands.length === 0 ? (
          <div className="text-center py-20">
            <Tag className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl tracking-tight mb-2">NO BRANDS FOUND</h3>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="brands-grid">
            {brands.map(brand => (
              <Link to={`/brands/${brand.slug || brand.brand_id}`} key={brand.brand_id}>
                <div className="border border-border bg-card p-5 hover:border-primary/30 group flex items-start gap-4" style={{ transition: 'border-color 0.2s' }} data-testid={`brand-card-${brand.brand_id}`}>
                  <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0">
                    {brand.logo_url ? <img src={brand.logo_url} alt={brand.name} className="w-10 h-10 object-contain" /> : <Tag className="w-6 h-6 text-muted-foreground" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary" style={{ transition: 'color 0.2s' }}>{brand.name}</h3>
                    {brand.country && <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}><Globe className="w-3 h-3" /> {brand.country}</p>}
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="rounded-none text-[10px]">{brand.kit_count} kits</Badge>
                      {brand.founded && <span className="text-[10px] font-mono text-muted-foreground">Est. {brand.founded}</span>}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
