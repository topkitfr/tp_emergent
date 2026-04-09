// frontend/src/components/LevelBadge.js
// Badge coloré pour le niveau d'un joueur ou d'une ligue
// level: "Professional" | "Semi-Pro" | "Amateur" | "Youth"
import React from 'react';
import { Badge } from '@/components/ui/badge';

const LEVEL_META = {
  Professional: { label: 'Professional', color: '#01696f', bg: 'rgba(1,105,111,0.12)' },
  'Semi-Pro':   { label: 'Semi-Pro',     color: '#006494', bg: 'rgba(0,100,148,0.12)' },
  Amateur:      { label: 'Amateur',      color: '#da7101', bg: 'rgba(218,113,1,0.12)'  },
  Youth:        { label: 'Youth',        color: '#7a7974', bg: 'rgba(122,121,116,0.12)'},
};

export default function LevelBadge({ level, className = '' }) {
  if (!level) return null;
  const meta = LEVEL_META[level] ?? { label: level, color: '#7a7974', bg: 'rgba(122,121,116,0.12)' };
  return (
    <Badge
      variant="outline"
      className={`rounded-none text-[10px] uppercase tracking-wider font-medium ${className}`}
      style={{
        borderColor: meta.color,
        color: meta.color,
        backgroundColor: meta.bg,
        fontFamily: 'Barlow Condensed, sans-serif',
      }}
    >
      {meta.label}
    </Badge>
  );
}
