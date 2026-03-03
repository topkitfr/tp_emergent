// src/components/PlayerStrip.js
import React from 'react';
import { Link } from 'react-router-dom';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';

export default function PlayerStrip({ title = "Players who wore this kit", players }) {
  if (!players || players.length === 0) return null;

  const limited = players.slice(0, 6);

  return (
    <div className="mt-8">
      <h3
        className="text-sm uppercase tracking-wider mb-3"
        style={{ fontFamily: 'Barlow Condensed' }}
      >
        {title}
      </h3>

      <div className="flex gap-3 overflow-x-auto pb-2">
        {limited.map((p) => (
          <Link
            key={p.player_id}
            to={`/players/${p.player_id}`}
            className="min-w-[160px] border border-border bg-card p-3 flex items-center gap-3 hover:border-primary/40"
            style={{ transition: 'border-color 0.2s ease' }}
          >
            <Avatar className="w-10 h-10 border border-border">
              <AvatarImage src={p.photo} />
              <AvatarFallback className="text-[10px] bg-secondary">
                {p.name?.[0] || '?'}
              </AvatarFallback>
            </Avatar>
            <div className="min-w-0">
              <p
                className="text-sm font-medium truncate"
                style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
              >
                {p.name}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
