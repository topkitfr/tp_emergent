// src/pages/BrandDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Shirt, Pencil } from 'lucide-react';
import JerseyCard from '@/components/JerseyCard';
import EntityEditDialog from '@/components/EntityEditDialog';
import { useAuth } from '@/contexts/AuthContext';
import { proxyImageUrl } from '@/lib/api';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export default function BrandDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [brand, setBrand] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeason, setFilterSeason] = useState('');
  const [filterTeam, setFilterTeam] = useState('');
  const [showEdit, setShowEdit] = useState(false);


  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const brandRes = await fetch(`/api/brands/${id}`);
        if (!brandRes.ok) {
          setBrand(null);
          return;
        }
        const brandData = await brandRes.json();

        const kitsRes = await fetch(`/api/brands/${id}/kits`);
        const kitsData = await kitsRes.json();

        setBrand({
          ...brandData,
          kits: kitsData || [],
        });
      } catch (e) {
        console.error(e);
        setBrand(null);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);


  if (loading) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!brand) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <p>Brand not found</p>
        </div>
      </div>
    );
  }

  const isPending = brand.status === 'pending' || brand.status === 'for_review';
  const isAdminOrModerator = user && (user.role === 'admin' || user.role === 'moderator');

  const seasons = Array.from(
    new Set((brand.kits || []).map(k => k.season).filter(Boolean))
  ).sort().reverse();

  const teams = Array.from(
    new Set((brand.kits || []).map(k => k.club).filter(Boolean))
  ).sort();

  const filteredKits = (brand.kits || []).filter(k => {
    if (filterSeason && k.season !== filterSeason) return false;
    if (filterTeam && k.club !== filterTeam) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Header top bar */}
        <div className="flex items-center justify-between mb-6">
          <Link
            to="/database/brands"
            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to brands
          </Link>

          {isAdminOrModerator && !isPending && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="sm"
                    variant="outline"
                    className="rounded-none"
                    onClick={() => setShowEdit(true)}
                    disabled={brand?.status !== 'approved'}
                  >
                    <Pencil className="w-4 h-4 mr-2" />
                    Suggest edit
                  </Button>
                </TooltipTrigger>
                {brand?.status !== 'approved' && (
                  <TooltipContent>
                    <p>Waiting for approval</p>
                  </TooltipContent>
                )}
              </Tooltip>
            </TooltipProvider>
          )}
        </div>

        {/* Brand header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1
              className="text-2xl font-black uppercase mb-1"
              style={{ fontFamily: 'Barlow Condensed, sans-serif' }}
            >
              {brand.name}
            </h1>
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className="rounded-none text-[10px] uppercase tracking-wider"
              >
                Brand
              </Badge>
              <Badge
                variant={brand.status === 'approved' ? 'secondary' : 'outline'}
                className={`rounded-none text-[10px] uppercase tracking-wider ${
                  brand.status === 'for_review' ? 'border-accent/40 text-accent' : ''
                }`}
              >
                {brand.status === 'approved' ? 'Approved' : brand.status === 'for_review' ? 'For Review' : 'Pending'}
              </Badge>
              {brand.country && (
                <span className="text-xs text-muted-foreground">
                  {brand.country}
                </span>
              )}
            </div>
          </div>

          {brand.logo && (
            <div className="w-16 h-16 bg-card border border-border flex items-center justify-center">
              <img
                src={proxyImageUrl(brand.logo)}
                alt={brand.name}
                className="max-w-full max-h-full object-contain"
              />
            </div>
          )}
        </div>

        {/* Message de verrouillage si pending */}
        {isPending && (
          <div className="mb-8 border border-border bg-card p-4">
            <p className="text-sm text-muted-foreground">
              This brand reference is pending approval with its jersey submission
              and cannot be edited yet. Once the related jersey is approved,
              you will be able to submit correction reports from this page.
            </p>
          </div>
        )}

        {/* Filtres et liste de kits */}
        <div className="mb-4 flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-muted-foreground">
              Filter by season
            </span>
            <select
              className="bg-card border border-border text-xs px-2 py-1 rounded-none"
              value={filterSeason}
              onChange={e => setFilterSeason(e.target.value)}
            >
              <option value="">All</option>
              {seasons.map(s => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-muted-foreground">
              Filter by club
            </span>
            <select
              className="bg-card border border-border text-xs px-2 py-1 rounded-none"
              value={filterTeam}
              onChange={e => setFilterTeam(e.target.value)}
            >
              <option value="">All</option>
              {teams.map(t => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-8">
          <h2
            className="text-sm uppercase tracking-wider text-muted-foreground mb-2"
            style={{ fontFamily: 'Barlow Condensed, sans-serif' }}
          >
            <Shirt className="w-4 h-4 inline mr-1" /> Kits
          </h2>
          {filteredKits.length === 0 ? (
            <p className="text-xs text-muted-foreground">
              No kits found for this brand with current filters.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {filteredKits.map(kit => (
                <JerseyCard key={kit.kit_id} kit={kit} />
              ))}
            </div>
          )}
        </div>

        {/* Dialog d'édition uniquement si brand approuvée */}
        {showEdit && !isPending && (
          <EntityEditDialog
            entityType="brand"
            entity={brand}
            open={showEdit}
            onOpenChange={setShowEdit}
          />
        )}
      </div>
    </div>
  );
}
