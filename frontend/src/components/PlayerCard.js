// frontend/src/components/PlayerCard.js
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User, Heart } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

// ── Couleurs du cadre selon la note Aura ──────────────────────────────────
const TIER = {
  0: { border: '#3f3f46', glow: 'rgba(63,63,70,0)',     bg: '#18181b' },
  1: { border: '#7B3F1A', glow: 'rgba(139,69,19,0.5)',  bg: '#1c1008' },
  2: { border: '#C0392B', glow: 'rgba(192,57,43,0.55)', bg: '#1e0c0a' },
  3: { border: '#2471A3', glow: 'rgba(36,113,163,0.55)',bg: '#081520' },
  4: { border: '#909497', glow: 'rgba(144,148,151,0.5)',bg: '#161819' },
  5: { border: '#D4AC0D', glow: 'rgba(212,172,13,0.65)',bg: '#181200' },
};

function resolveAuraStars(player) {
  const candidates = [
    player.aura_stars, player.aura_rating, player.stars,
    player.star_rating, player.aura_level, player.aura_score,
    player.auraScore, player.community_rating, player.community_score,
    player.rating, player.score, player.note, player.grade,
  ];
  for (const val of candidates) {
    if (val !== undefined && val !== null && val !== '') {
      const n = Number(val);
      if (isNaN(n)) continue;
      if (n >= 0 && n <= 5)   return Math.round(n);
      if (n > 5  && n <= 10)  return Math.round(n / 2);
      if (n > 10 && n <= 100) return Math.round(n / 20);
    }
  }
  return 0;
}

export default function PlayerCard({ player, isFollowed = false, onFollowToggle }) {
  const [followLoading, setFollowLoading] = useState(false);

  const playerId   = player._id        ?? player.player_id ?? player.id ?? '';
  const playerSlug = player.slug       ?? player.player_slug ?? playerId;
  const playerName =
    player.name         ?? player.player_name  ??
    player.full_name    ?? player.display_name ?? 'Unknown';
  const nationality = player.nationality ?? player.country ?? '';
  const position    = player.position   ?? player.role    ?? player.poste ?? '';

  // Même logique que JerseyCard : proxyImageUrl direct sur le champ image
  const rawImage =
    player.image_url    ?? player.photo_url   ?? player.photo      ??
    player.picture      ?? player.img         ?? player.img_url    ??
    player.avatar       ?? player.avatar_url  ?? player.headshot   ??
    player.profile_image ?? '';
  const imageUrl = rawImage ? proxyImageUrl(rawImage) : '';

  const stars = resolveAuraStars(player);
  const tier  = TIER[stars] ?? TIER[0];

  const handleFollow = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!playerId || !onFollowToggle || followLoading) return;
    setFollowLoading(true);
    try { await onFollowToggle(playerId, !isFollowed); }
    finally { setFollowLoading(false); }
  }, [playerId, isFollowed, onFollowToggle, followLoading]);

  return (
    <Link to={`/players/${playerSlug}`} data-testid={`player-card-${playerId}`}>
      <div
        className="relative overflow-hidden group hover:-translate-y-1"
        style={{
          aspectRatio: '2 / 3',
          border: `3px solid ${tier.border}`,
          boxShadow: `0 0 12px ${tier.glow}, 0 3px 10px rgba(0,0,0,0.5)`,
          background: tier.bg,
          borderRadius: 8,
          transition: 'transform 0.3s ease, box-shadow 0.2s ease',
        }}
      >
        {/* ── Photo ───────────────────────────────────────────── */}
        <div className="absolute inset-0">
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={playerName}
              className="w-full h-full object-cover object-top group-hover:scale-105"
              style={{ transition: 'transform 0.5s ease' }}
              loading="lazy"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <User className="w-10 h-10 text-zinc-600" />
            </div>
          )}
        </div>

        {/* ── Bandeau haut : étoiles + follow ─────────────────── */}
        <div
          className="absolute top-0 left-0 right-0 flex items-center justify-between px-1.5 py-1"
          style={{
            background: 'linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, transparent 100%)',
            zIndex: 2,
          }}
        >
          {/* Étoiles Aura */}
          <span className="text-[11px] leading-none select-none" style={{ letterSpacing: 1 }}>
            {Array.from({ length: 5 }, (_, i) => (
              <span key={i} style={{ color: i < stars ? tier.border : 'rgba(255,255,255,0.2)' }}>
                {i < stars ? '★' : '☆'}
              </span>
            ))}
          </span>

          {/* Follow */}
          {onFollowToggle && (
            <button
              onClick={handleFollow}
              disabled={followLoading}
              aria-label={isFollowed ? 'Ne plus suivre' : 'Suivre'}
              className="p-0.5 transition-transform hover:scale-125"
              style={{ background: 'none', border: 'none', cursor: followLoading ? 'wait' : 'pointer' }}
            >
              <Heart
                size={13}
                fill={isFollowed ? '#ef4444' : 'none'}
                stroke={isFollowed ? '#ef4444' : 'rgba(255,255,255,0.75)'}
                strokeWidth={2}
              />
            </button>
          )}
        </div>

        {/* ── Bandeau blanc bas style Panini ──────────────────── */}
        <div
          className="absolute bottom-0 left-0 right-0 flex flex-col items-center"
          style={{
            background: '#ffffff',
            borderTop: `2px solid ${tier.border}`,
            padding: '4px 6px 5px',
            zIndex: 2,
          }}
        >
          <span
            className="w-full text-center truncate"
            style={{
              color: '#111',
              fontWeight: 800,
              fontSize: 10,
              textTransform: 'uppercase',
              letterSpacing: '0.7px',
              lineHeight: 1.2,
              fontFamily: 'Barlow Condensed, sans-serif',
            }}
          >
            {playerName}
          </span>
          {(position || nationality) && (
            <span
              style={{
                color: '#666',
                fontSize: 8,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                lineHeight: 1,
                fontFamily: 'DM Sans, sans-serif',
              }}
            >
              {[position, nationality].filter(Boolean).join(' · ')}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}