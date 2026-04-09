// frontend/src/components/TeamTypeTag.js
// Tag Club 🏟️ vs Équipe Nationale 🚩
// isNational: boolean
import React from 'react';
import { Badge } from '@/components/ui/badge';

export default function TeamTypeTag({ isNational, className = '' }) {
  const meta = isNational
    ? { icon: '🚩', label: 'Nationale',  color: '#a13544', bg: 'rgba(161,53,68,0.10)' }
    : { icon: '🏟️', label: 'Club',        color: '#01696f', bg: 'rgba(1,105,111,0.10)' };
  return (
    <Badge
      variant="outline"
      className={`rounded-none text-[10px] uppercase tracking-wider font-medium gap-1 ${className}`}
      style={{
        borderColor: meta.color,
        color: meta.color,
        backgroundColor: meta.bg,
        fontFamily: 'Barlow Condensed, sans-serif',
      }}
    >
      <span>{meta.icon}</span>
      <span>{meta.label}</span>
    </Badge>
  );
}
