// src/components/VersionCard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Shirt, Plus } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { proxyImageUrl } from "@/lib/api";
import { useAuth } from '@/contexts/AuthContext';

export default function VersionCard({ version, onAddToCollection }) {
  const { user } = useAuth();
  const kit   = version.master_kit || {};
  const photo = version.front_photo || kit.front_photo;

  return (
    <div className="relative group">
      <Link to={`/versions/${version.version_id}`}>
        <div
          className="card-shimmer relative border border-border bg-card overflow-hidden group hover:-translate-y-1 hover:border-primary/30"
          style={{ transition: 'transform 0.3s ease, border-color 0.3s ease' }}
        >
          {/* Image */}
          <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
            {photo ? (
              <img
                src={proxyImageUrl(photo)}
                alt={`${kit.club} ${kit.season}`}
                className="w-full h-full object-cover group-hover:scale-105"
                style={{ transition: 'transform 0.5s ease' }}
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Shirt className="w-12 h-12 text-muted-foreground" />
              </div>
            )}

            {/* Badge type kit — top right */}
            <div className="absolute top-2 right-2">
              <Badge className="rounded-none text-[10px] bg-background/80 text-foreground backdrop-blur-sm border-none">
                {kit.kit_type}
              </Badge>
            </div>

            {/* Badge model (Replica/Authentic) — top left */}
            {version.model && (
              <div className="absolute top-2 left-2">
                <span className="font-mono text-[10px] px-1.5 py-0.5 bg-primary/90 text-primary-foreground">
                  {version.model === "Authentic" ? "AUTH" : version.model === "Replica" ? "REP" : version.model}
                </span>
              </div>
            )}
          </div>

          {/* Info */}
          <div className="p-3 space-y-1.5">
            <h3
              className="text-sm font-semibold tracking-tight truncate"
              style={{ fontFamily: 'Barlow Condensed, sans-serif', textTransform: 'uppercase' }}
            >
              {kit.club}
            </h3>
            <div className="flex items-center justify-between">
              <span
                className="text-xs text-muted-foreground"
                style={{ fontFamily: 'DM Sans, sans-serif' }}
              >
                {kit.season}
              </span>
              <span className="font-mono text-[10px] text-muted-foreground">{kit.brand}</span>
            </div>
            <p
              className="text-[10px] text-muted-foreground truncate"
              style={{ fontFamily: 'DM Sans, sans-serif' }}
            >
              {version.competition}
            </p>
            {version.avg_rating > 0 && (
              <div className="flex items-center gap-1">
                <Star className="w-3 h-3 text-accent fill-accent" />
                <span className="text-xs text-accent font-mono">{version.avg_rating}</span>
              </div>
            )}
          </div>
        </div>
      </Link>

      {/* Bouton + ajout rapide — visible au hover */}
      {user && (
        <button
          onClick={(e) => { e.preventDefault(); onAddToCollection(version); }}
          className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1.5
                     opacity-0 group-hover:opacity-100 transition-opacity shadow-md z-10"
          title="Add to collection"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
