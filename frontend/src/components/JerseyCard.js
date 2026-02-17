import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Shirt } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function JerseyCard({ kit }) {
  return (
    <Link to={`/kit/${kit.kit_id}`} data-testid={`jersey-card-${kit.kit_id}`}>
      <div className="card-shimmer relative border border-border bg-card overflow-hidden group hover:-translate-y-1 hover:border-primary/30" style={{ transition: 'transform 0.3s ease, border-color 0.3s ease' }}>
        {/* Image */}
        <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
          {kit.front_photo ? (
            <img
              src={kit.front_photo}
              alt={`${kit.club} ${kit.season}`}
              className="w-full h-full object-cover group-hover:scale-105"
              style={{ transition: 'transform 0.5s ease' }}
              loading="lazy"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Shirt className="w-12 h-12 text-muted-foreground" />
            </div>
          )}

          {/* Type badge */}
          <div className="absolute top-2 right-2">
            <Badge className="rounded-none text-[10px] bg-background/80 text-foreground backdrop-blur-sm border-none">
              {kit.kit_type}
            </Badge>
          </div>

          {/* Version count */}
          {kit.version_count > 0 && (
            <div className="absolute top-2 left-2">
              <span className="font-mono text-[10px] px-1.5 py-0.5 bg-primary/90 text-primary-foreground">
                {kit.version_count}v
              </span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="p-3 space-y-1.5">
          <h3 className="text-sm font-semibold tracking-tight truncate" style={{ fontFamily: 'Barlow Condensed, sans-serif', textTransform: 'uppercase' }}>
            {kit.club}
          </h3>
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
              {kit.season}
            </span>
            <span className="font-mono text-[10px] text-muted-foreground">{kit.brand}</span>
          </div>
          {kit.colors && (
            <p className="text-[10px] text-muted-foreground truncate" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
              {kit.colors}
            </p>
          )}
          {kit.avg_rating > 0 && (
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3 text-accent fill-accent" />
              <span className="text-xs text-accent font-mono">{kit.avg_rating}</span>
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
