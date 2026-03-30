// frontend/src/components/PlayerCard.js
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User, Heart } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

// ── Config couleurs par note ───────────────────────────────────────────────
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

function resolveImageUrl(player) {
  const raw =
    player.image_url    ?? player.photo_url   ?? player.photo      ??
    player.picture      ?? player.img         ?? player.img_url    ??
    player.avatar       ?? player.avatar_url  ?? player.headshot   ??
    player.headshot_url ?? player.thumbnail   ?? player.profile_image ??
    player.profile_picture ?? '';
  if (!raw) return '';
  try { return proxyImageUrl(raw); } catch { return raw; }
}

export default function PlayerCard({ player, isFollowed = false, onFollowToggle }) {
  const [followLoading, setFollowLoading] = useState(false);

  const playerId   = player._id        ?? player.player_id ?? player.id ?? '';
  const playerSlug = player.slug       ?? player.player_slug ?? playerId;
  const playerName =
    player.name         ?? player.player_name  ??
    player.full_name    ?? player.display_name ?? 'Joueur inconnu';
  const nationality = player.nationality ?? player.country ?? '';
  const position    = player.position   ?? player.role    ?? player.poste ?? '';
  const imageUrl    = resolveImageUrl(player);
  const stars       = resolveAuraStars(player);
  const tier        = TIER[stars] ?? TIER[0];

  const handleFollow = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!playerId || !onFollowToggle || followLoading) return;
    setFollowLoading(true);
    try { await onFollowToggle(playerId, !isFollowed); }
    finally { setFollowLoading(false); }
  }, [playerId, isFollowed, onFollowToggle, followLoading]);

  return (
    <Link
      to={`/players/${playerSlug}`}
      className="group block focus:outline-none"
      style={{ textDecoration: 'none' }}
    >
      <div
        style={{
          position: 'relative',
          aspectRatio: '2 / 3',
          borderRadius: 8,
          overflow: 'hidden',
          border: `3px solid ${tier.border}`,
          boxShadow: `0 0 12px ${tier.glow}, 0 3px 10px rgba(0,0,0,0.5)`,
          background: tier.bg,
          transition: 'transform 0.16s ease, box-shadow 0.18s ease',
        }}
        className="hover:scale-[1.03]"
      >
        {imageUrl && (
          <img
            src={imageUrl}
            alt={playerName}
            onError={(e) => { e.currentTarget.style.display = 'none'; }}
            style={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'top center',
              display: 'block',
            }}
          />
        )}
        {!imageUrl && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: tier.bg,
          }}>
            <User size={40} color="#52525b" />
          </div>
        )}

        {/* Bandeau haut : étoiles + cœur */}
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '5px 6px',
          background: 'linear-gradient(to bottom, rgba(0,0,0,0.72) 0%, transparent 100%)',
          zIndex: 3,
        }}>
          <span style={{ fontSize: 11, letterSpacing: 1, lineHeight: 1, userSelect: 'none' }}>
            {Array.from({ length: 5 }, (_, i) => (
              <span key={i} style={{ color: i < stars ? tier.border : 'rgba(255,255,255,0.25)' }}>
                {i < stars ? '★' : '☆'}
              </span>
            ))}
          </span>

          {onFollowToggle && (
            <button
              onClick={handleFollow}
              disabled={followLoading}
              aria-label={isFollowed ? 'Ne plus suivre' : 'Suivre'}
              style={{
                background: 'none',
                border: 'none',
                padding: '2px',
                cursor: followLoading ? 'wait' : 'pointer',
                lineHeight: 1,
                opacity: followLoading ? 0.5 : 1,
                transition: 'transform 0.15s ease',
              }}
              onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.2)'}
              onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
            >
              <Heart
                size={14}
                fill={isFollowed ? '#ef4444' : 'none'}
                stroke={isFollowed ? '#ef4444' : 'rgba(255,255,255,0.8)'}
                strokeWidth={2}
              />
            </button>
          )}
        </div>

        {/* Bandeau blanc bas style Panini */}
        <div style={{
          position: 'absolute',
          bottom: 0, left: 0, right: 0,
          background: '#ffffff',
          borderTop: `2px solid ${tier.border}`,
          padding: '4px 6px 5px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          zIndex: 2,
        }}>
          <span style={{
            color: '#111',
            fontWeight: 800,
            fontSize: 10,
            textTransform: 'uppercase',
            letterSpacing: '0.7px',
            lineHeight: 1.2,
            textAlign: 'center',
            width: '100%',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {playerName}
          </span>
          {(position || nationality) && (
            <span style={{
              color: '#555',
              fontSize: 8,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              lineHeight: 1,
            }}>
              {[position, nationality].filter(Boolean).join(' · ')}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}