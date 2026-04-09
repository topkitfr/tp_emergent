// frontend/src/components/GenderBadge.js
// Badge genre pour joueur / ligue
// gender: "male" | "female"
import React from 'react';
import { Badge } from '@/components/ui/badge';

const GENDER_META = {
  male:   { label: '♂ Masculin',  color: '#006494', bg: 'rgba(0,100,148,0.10)' },
  female: { label: '♀ Féminin',   color: '#a12c7b', bg: 'rgba(161,44,123,0.10)' },
};

export default function GenderBadge({ gender, className = '' }) {
  if (!gender) return null;
  const meta = GENDER_META[gender.toLowerCase()] ?? { label: gender, color: '#7a7974', bg: 'transparent' };
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
