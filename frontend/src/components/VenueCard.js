// frontend/src/components/VenueCard.js
// Carte stade pour TeamDetail
// Props:
//   name: string
//   city: string
//   capacity: number
//   surface: string   — "Grass" | "Artificial Turf" | "Hybrid"
//   imageUrl: string
//   country: string
import React from 'react';
import { MapPin, Users, Layers } from 'lucide-react';

const SURFACE_META = {
  grass:          { label: 'Gazon naturel',    color: '#437a22', bg: 'rgba(67,122,34,0.10)'  },
  'artificial turf': { label: 'Gazon artificiel', color: '#006494', bg: 'rgba(0,100,148,0.10)' },
  hybrid:         { label: 'Gazon hybride',    color: '#01696f', bg: 'rgba(1,105,111,0.10)'  },
};

function getSurfaceMeta(surface) {
  if (!surface) return null;
  return SURFACE_META[surface.toLowerCase()] ?? { label: surface, color: '#7a7974', bg: 'transparent' };
}

export default function VenueCard({ name, city, capacity, surface, imageUrl, country }) {
  if (!name && !imageUrl) return null;
  const surfaceMeta = getSurfaceMeta(surface);

  return (
    <div className="border border-border bg-card overflow-hidden">
      {/* Photo stade */}
      {imageUrl ? (
        <div className="relative w-full" style={{ aspectRatio: '16/7' }}>
          <img
            src={imageUrl}
            alt={name || 'Stade'}
            className="w-full h-full object-cover"
            loading="lazy"
          />
          {/* Gradient overlay bas */}
          <div
            className="absolute inset-0"
            style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.55) 0%, transparent 50%)' }}
          />
          {name && (
            <p
              className="absolute bottom-3 left-4 text-white font-semibold text-sm"
              style={{ fontFamily: 'Barlow Condensed, sans-serif', letterSpacing: '0.03em', textTransform: 'uppercase' }}
            >
              {name}
            </p>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center bg-muted" style={{ aspectRatio: '16/7' }}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2" className="text-muted-foreground opacity-40">
            <rect x="2" y="7" width="20" height="13" rx="0" />
            <path d="M2 10h20M7 7V4h10v3" />
          </svg>
        </div>
      )}

      {/* Infos stade */}
      <div className="px-4 py-3 flex flex-wrap gap-x-6 gap-y-2">
        {(city || country) && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <MapPin className="w-3.5 h-3.5 shrink-0" />
            <span style={{ fontFamily: 'DM Sans, sans-serif' }}>
              {[city, country].filter(Boolean).join(', ')}
            </span>
          </div>
        )}
        {capacity && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Users className="w-3.5 h-3.5 shrink-0" />
            <span style={{ fontFamily: 'DM Sans, sans-serif' }}>
              {capacity.toLocaleString('fr-FR')} places
            </span>
          </div>
        )}
        {surfaceMeta && (
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 shrink-0" style={{ color: surfaceMeta.color }} />
            <span
              className="text-xs font-medium"
              style={{
                color: surfaceMeta.color,
                fontFamily: 'DM Sans, sans-serif',
              }}
            >
              {surfaceMeta.label}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
