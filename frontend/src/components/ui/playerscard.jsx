// frontend/src/components/ui/playerscard.jsx
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

// ── Tiers visuels selon la note Aura ──────────────────────────────────────
const TIER = {
  0: { border: '#4b5563', glow: 'rgba(75,85,99,0)',    bg: '#1a1a1a' },
  1: { border: '#7B3F1A', glow: 'rgba(139,69,19,0.55)', bg: '#1c1008' },
  2: { border: '#C0392B', glow: 'rgba(192,57,43,0.6)',  bg: '#1e0c0a' },
  3: { border: '#2471A3', glow: 'rgba(36,113,163,0.6)', bg: '#081520' },
  4: { border: '#909497', glow: 'rgba(144,148,151,0.5)',bg: '#161819' },
  5: { border: '#D4AC0D', glow: 'rgba(212,172,13,0.7)', bg: '#181200' },
};

// ── Résolution robuste de la note Aura ────────────────────────────────────
function resolveAuraStars(player) {
  const candidates = [
    player.aura_stars,
    player.aura_rating,
    player.stars,
    player.star_rating,
    player.aura_level,
    player.aura_score,
    player.auraScore,
    player.community_rating,
    player.community_score,
    player.rating,
    player.score,
    player.note,
    player.grade,
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

// ── Résolution robuste de l'URL image ─────────────────────────────────────
function resolveImageUrl(player) {
  const raw =
    player.image_url       ??
    player.photo_url       ??
    player.photo           ??
    player.picture         ??
    player.img             ??
    player.img_url         ??
    player.avatar          ??
    player.avatar_url      ??
    player.headshot        ??
    player.headshot_url    ??
    player.thumbnail       ??
    player.profile_image   ??
    player.profile_picture ??
    '';
  if (!raw) return '';
  try {
    return proxyImageUrl(raw);
  } catch {
    return raw; // fallback: URL brute si proxyImageUrl plante
  }
}

// ── Rendu des étoiles ──────────────────────────────────────────────────────
function StarRow({ stars, color }) {
  return (
    <span style={{ fontSize: 13, letterSpacing: 1.5, lineHeight: 1, userSelect: 'none' }}>
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} style={{ color: i < stars ? color : '#9ca3af' }}>
          {i < stars ? '★' : '☆'}
        </span>
      ))}
    </span>
  );
}

// ── Composant principal ────────────────────────────────────────────────────
export default function PlayerCard({ player, isFollowed = false, onFollowToggle }) {
  const [loading, setLoading] = useState(false);

  const playerId   = player._id        ?? player.player_id ?? player.id ?? '';
  const playerSlug = player.slug       ?? player.player_slug ?? playerId;
  const playerName =
    player.name         ??
    player.player_name  ??
    player.full_name    ??
    player.display_name ??
    'Joueur inconnu';
  const nationality = player.nationality ?? player.country ?? '';
  const position    = player.position   ?? player.role    ?? player.poste ?? '';

  const imageUrl = resolveImageUrl(player);
  const stars    = resolveAuraStars(player);
  const tier     = TIER[stars] ?? TIER[0];

  const handleFollowClick = useCallback(async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!playerId || !onFollowToggle || loading) return;
    setLoading(true);
    try { await onFollowToggle(playerId, !isFollowed); }
    finally { setLoading(false); }
  }, [playerId, isFollowed, onFollowToggle, loading]);

  return (
    <Link
      to={`/players/${playerSlug}`}
      className="group block focus:outline-none"
      style={{ textDecoration: 'none' }}
    >
      {/* ── Enveloppe carte (ratio Panini 2/3) ────────────────────── */}
      <div
        style={{
          position: 'relative',
          aspectRatio: '2 / 3',
          borderRadius: 10,
          overflow: 'hidden',
          border: `4px solid ${tier.border}`,
          boxShadow: `0 0 16px ${tier.glow}, 0 4px 12px rgba(0,0,0,0.55)`,
          background: tier.bg,
          transition: 'transform 0.18s ease, box-shadow 0.2s ease',
          cursor: 'pointer',
        }}
        className="hover:scale-[1.04]"
      >
        {/* ── Photo full-bleed ──────────────────────────────────────── */}
        {imageUrl ? (
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
        ) : null}

        {/* ── Placeholder si pas d'image ────────────────────────────── */}
        {!imageUrl && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: tier.bg,
          }}>
            <User size={52} color="#4b5563" />
          </div>
        )}

        {/* ── Badge note (coin haut droit) ──────────────────────────── */}
        {stars > 0 && (
          <div style={{
            position: 'absolute',
            top: 7,
            right: 7,
            background: tier.border,
            color: stars === 4 ? '#111' : '#fff',
            fontSize: 9,
            fontWeight: 800,
            padding: '2px 6px',
            borderRadius: 4,
            letterSpacing: '1.5px',
            textTransform: 'uppercase',
            boxShadow: '0 1px 4px rgba(0,0,0,0.5)',
            zIndex: 3,
          }}>
            {'★'.repeat(stars)}
          </div>
        )}

        {/* ── Bouton Follow (overlay au hover) ─────────────────────── */}
        {onFollowToggle && (
          <button
            onClick={handleFollowClick}
            disabled={loading}
            aria-label={isFollowed ? 'Ne plus suivre' : 'Suivre'}
            className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
            style={{
              position: 'absolute',
              top: 7,
              left: 7,
              background: isFollowed ? 'rgba(255,255,255,0.92)' : 'rgba(0,0,0,0.72)',
              color: isFollowed ? '#111' : '#fff',
              border: 'none',
              borderRadius: 5,
              padding: '3px 8px',
              fontSize: 10,
              fontWeight: 700,
              cursor: loading ? 'wait' : 'pointer',
              opacity: loading ? 0.6 : undefined,
              zIndex: 4,
              transition: 'opacity 0.15s',
              letterSpacing: '0.3px',
            }}
          >
            {loading ? '…' : isFollowed ? '✓ Suivi' : '+ Suivre'}
          </button>
        )}

        {/* ── Bandeau blanc bas style Panini ─────────────────────────── */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          background: '#ffffff',
          borderTop: `3px solid ${tier.border}`,
          padding: '6px 8px 8px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 3,
          zIndex: 2,
        }}>
          {/* Nom */}
          <span style={{
            color: '#111111',
            fontWeight: 800,
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: '0.8px',
            lineHeight: 1.2,
            textAlign: 'center',
            width: '100%',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {playerName}
          </span>

          {/* Poste · Nationalité */}
          {(position || nationality) && (
            <span style={{
              color: '#555',
              fontSize: 9,
              textTransform: 'uppercase',
              letterSpacing: '0.6px',
              lineHeight: 1,
            }}>
              {[position, nationality].filter(Boolean).join(' · ')}
            </span>
          )}

          {/* Étoiles Aura */}
          <StarRow stars={stars} color={tier.border} />
        </div>
      </div>
    </Link>
  );
}