// frontend/src/components/ui/playerscard.jsx
import React, { useState, useCallback, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

// ── Config couleurs par note (1–5 étoiles) ─────────────────────────────────
const TIER = {
  0: { border: '#4b5563', glow: 'rgba(75,85,99,0)',   bg: '#1f2937', label: 'NO RATING' },
  1: { border: '#7B3F1A', glow: 'rgba(139,69,19,0.6)',bg: '#2a1810', label: '★' },
  2: { border: '#C0392B', glow: 'rgba(192,57,43,0.7)',bg: '#2d0f0c', label: '★★' },
  3: { border: '#2471A3', glow: 'rgba(36,113,163,0.7)',bg:'#0a1c2e', label: '★★★' },
  4: { border: '#909497', glow: 'rgba(144,148,151,0.6)',bg:'#1a1d1f', label: '★★★★' },
  5: { border: '#D4AC0D', glow: 'rgba(212,172,13,0.8)',bg: '#1c1500', label: '★★★★★' },
};

// Diagnostic activé une seule fois par session pour trouver le bon champ
let _diagDone = false;

function resolveAuraStars(player) {
  // Log de diagnostic pour trouver le bon champ (une seule fois)
  if (!_diagDone) {
    _diagDone = true;
    const auraFields = Object.entries(player)
      .filter(([k]) =>
        k.toLowerCase().includes('aura') ||
        k.toLowerCase().includes('star') ||
        k.toLowerCase().includes('rating') ||
        k.toLowerCase().includes('score') ||
        k.toLowerCase().includes('note') ||
        k.toLowerCase().includes('grade')
      );
    console.group('🔍 [PlayerCard] Diagnostic champs Aura');
    console.log('Tous les champs du player:', Object.keys(player));
    console.log('Champs suspects pour la note:', auraFields);
    console.groupEnd();
  }

  // Tentative sur tous les noms de champs connus
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
      const n = Math.round(Number(val));
      if (!isNaN(n) && n >= 0 && n <= 5) return n;
      // Si la valeur est sur 10 ou 100, on ramène sur 5
      if (!isNaN(n) && n > 5 && n <= 10) return Math.round(n / 2);
      if (!isNaN(n) && n > 10 && n <= 100) return Math.round(n / 20);
    }
  }

  return 0;
}

// Render des étoiles colorées
function StarRating({ stars, borderColor }) {
  const filled = '★'.repeat(stars);
  const empty  = '☆'.repeat(5 - stars);
  return (
    <span style={{ fontSize: 14, letterSpacing: 1, lineHeight: 1 }}>
      <span style={{ color: stars > 0 ? borderColor : '#9ca3af' }}>{filled}</span>
      <span style={{ color: '#9ca3af' }}>{empty}</span>
    </span>
  );
}

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
  const imageUrl    = proxyImageUrl(
    player.image_url ?? player.photo ?? player.img ?? player.avatar ?? ''
  );

  const stars = resolveAuraStars(player);
  const tier  = TIER[stars] ?? TIER[0];

  const handleFollowClick = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (!playerId || !onFollowToggle || loading) return;
      setLoading(true);
      try {
        await onFollowToggle(playerId, !isFollowed);
      } finally {
        setLoading(false);
      }
    },
    [playerId, isFollowed, onFollowToggle, loading]
  );

  return (
    <Link
      to={`/players/${playerSlug}`}
      className="group block focus:outline-none"
      style={{ textDecoration: 'none', display: 'block' }}
    >
      {/* ── Enveloppe principale (ratio Panini 2/3) ─────────────────── */}
      <div
        style={{
          position: 'relative',
          aspectRatio: '2 / 3',
          borderRadius: 10,
          overflow: 'hidden',
          border: `4px solid ${tier.border}`,
          boxShadow: `0 0 14px ${tier.glow}, 0 3px 10px rgba(0,0,0,0.5)`,
          background: tier.bg,
          transition: 'transform 0.18s ease, box-shadow 0.2s ease',
          cursor: 'pointer',
        }}
        className="hover:scale-[1.04]"
      >
        {/* ── Photo full-bleed ─────────────────────────────────────── */}
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={playerName}
            style={{
              position: 'absolute',
              inset: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'top center',
            }}
          />
        ) : (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <User size={48} color="#6b7280" />
          </div>
        )}

        {/* ── Badge tier (coin haut droit) ─────────────────────────── */}
        {stars > 0 && (
          <div
            style={{
              position: 'absolute',
              top: 6,
              right: 6,
              background: tier.border,
              color: stars === 4 ? '#111' : '#fff',
              fontSize: 9,
              fontWeight: 800,
              padding: '2px 6px',
              borderRadius: 4,
              letterSpacing: '1.5px',
              textTransform: 'uppercase',
              boxShadow: '0 1px 4px rgba(0,0,0,0.5)',
              zIndex: 2,
            }}
          >
            {tier.label}
          </div>
        )}

        {/* ── Bouton Follow (overlay, visible au hover/focus) ────────── */}
        {onFollowToggle && (
          <button
            onClick={handleFollowClick}
            disabled={loading}
            aria-label={isFollowed ? 'Ne plus suivre' : 'Suivre'}
            style={{
              position: 'absolute',
              top: 6,
              left: 6,
              background: isFollowed ? 'rgba(255,255,255,0.92)' : 'rgba(0,0,0,0.7)',
              color: isFollowed ? '#111' : '#fff',
              border: 'none',
              borderRadius: 5,
              padding: '3px 8px',
              fontSize: 10,
              fontWeight: 700,
              cursor: loading ? 'wait' : 'pointer',
              opacity: loading ? 0.6 : 1,
              zIndex: 3,
              transition: 'opacity 0.15s',
              letterSpacing: '0.3px',
            }}
            className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
          >
            {loading ? '…' : isFollowed ? '✓ Suivi' : '+ Suivre'}
          </button>
        )}

        {/* ── Bandeau blanc bas style Panini ───────────────────────── */}
        <div
          style={{
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
            gap: 2,
            zIndex: 2,
          }}
        >
          {/* Nom en majuscules */}
          <span
            style={{
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
            }}
          >
            {playerName}
          </span>

          {/* Poste · Nationalité */}
          {(position || nationality) && (
            <span
              style={{
                color: '#555555',
                fontSize: 9,
                textTransform: 'uppercase',
                letterSpacing: '0.6px',
                lineHeight: 1,
              }}
            >
              {[position, nationality].filter(Boolean).join(' · ')}
            </span>
          )}

          {/* Étoiles */}
          <StarRating stars={stars} borderColor={tier.border} />
        </div>
      </div>
    </Link>
  );
}