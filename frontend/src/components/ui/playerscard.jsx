// frontend/src/components/ui/playerscard.jsx
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

// ── Couleur du cadre selon la note Aura (1 à 5 étoiles) ─────────────────────
const AURA_BORDER = {
  0: { border: '#6b7280', glow: 'rgba(107,114,128,0.4)',  label: '' },
  1: { border: '#8B4513', glow: 'rgba(139, 69, 19, 0.5)', label: '★' },
  2: { border: '#C0392B', glow: 'rgba(192, 57, 43, 0.5)', label: '★★' },
  3: { border: '#2980B9', glow: 'rgba(41,128,185,0.5)',   label: '★★★' },
  4: { border: '#A8A9AD', glow: 'rgba(168,169,173,0.5)',  label: '★★★★' },
  5: { border: '#FFD700', glow: 'rgba(255,215,0,0.6)',    label: '★★★★★' },
};

// Renvoie un entier 0-5 depuis n'importe quel champ de l'objet player
function resolveAuraStars(player) {
  const raw =
    player.aura_stars    ??
    player.aura_rating   ??
    player.stars         ??
    null;

  if (raw !== null) {
    const n = Math.round(Number(raw));
    return Math.min(5, Math.max(0, n));
  }

  // Sinon on déduit depuis le score flottant (0-5 scale)
  const score =
    player.aura_score    ??
    player.auraScore     ??
    player.rating        ??
    player.community_rating ??
    null;

  if (score !== null) {
    const n = Math.round(Number(score));
    return Math.min(5, Math.max(0, n));
  }

  return 0;
}

export default function PlayerCard({ player, isFollowed = false, onFollowToggle }) {
  const [loading, setLoading] = useState(false);

  const playerId   = player._id         ?? player.player_id ?? player.id ?? '';
  const playerSlug = player.slug        ?? player.player_slug ?? playerId;
  const playerName =
    player.name         ??
    player.player_name  ??
    player.full_name    ??
    player.display_name ??
    'Joueur inconnu';

  const nationality = player.nationality ?? player.country ?? '';
  const position    = player.position    ?? player.role    ?? player.poste ?? '';
  const imageUrl    = proxyImageUrl(
    player.image_url ?? player.photo ?? player.img ?? player.avatar ?? ''
  );

  const stars = resolveAuraStars(player);
  const aura  = AURA_BORDER[stars] ?? AURA_BORDER[0];

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
      style={{ textDecoration: 'none' }}
    >
      {/* ── Wrapper carte ─────────────────────────────────────────────── */}
      <div
        style={{
          position: 'relative',
          borderRadius: '10px',
          overflow: 'hidden',
          border: `3px solid ${aura.border}`,
          boxShadow: `0 0 10px ${aura.glow}, 0 2px 8px rgba(0,0,0,0.35)`,
          aspectRatio: '2/3',
          background: '#1a1a1a',
          transition: 'transform 0.18s ease, box-shadow 0.18s ease',
        }}
        className="hover:scale-[1.03]"
      >
        {/* ── Photo joueur ─────────────────────────────────────────────── */}
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={playerName}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'top center',
              display: 'block',
            }}
          />
        ) : (
          <div
            style={{
              width: '100%',
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: '#2a2a2a',
            }}
          >
            <User size={48} color="#555" />
          </div>
        )}

        {/* ── Bandeau étoile (coin haut droit) ─────────────────────────── */}
        {stars > 0 && (
          <div
            style={{
              position: 'absolute',
              top: 6,
              right: 6,
              background: aura.border,
              color: stars === 4 ? '#333' : '#fff',
              fontSize: '10px',
              fontWeight: 700,
              padding: '2px 5px',
              borderRadius: '4px',
              letterSpacing: '1px',
              lineHeight: 1,
              boxShadow: '0 1px 4px rgba(0,0,0,0.4)',
            }}
          >
            {aura.label}
          </div>
        )}

        {/* ── Bandeau blanc bas style Panini ──────────────────────────── */}
        <div
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            background: '#ffffff',
            borderTop: `2px solid ${aura.border}`,
            padding: '5px 7px 6px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '2px',
          }}
        >
          {/* Nom */}
          <span
            style={{
              color: '#111',
              fontWeight: 700,
              fontSize: '11px',
              textTransform: 'uppercase',
              letterSpacing: '0.6px',
              lineHeight: 1.2,
              textAlign: 'center',
              maxWidth: '100%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {playerName}
          </span>

          {/* Poste + nationalité */}
          {(position || nationality) && (
            <span
              style={{
                color: '#555',
                fontSize: '9px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                lineHeight: 1,
              }}
            >
              {[position, nationality].filter(Boolean).join(' · ')}
            </span>
          )}

          {/* Étoiles Aura */}
          <span
            style={{
              color: stars === 0 ? '#aaa' : aura.border,
              fontSize: '12px',
              lineHeight: 1,
              filter: stars === 4 ? 'drop-shadow(0 0 1px #888)' : 'none',
            }}
          >
            {stars === 0
              ? '☆☆☆☆☆'
              : '★'.repeat(stars) + '☆'.repeat(5 - stars)}
          </span>
        </div>

        {/* ── Bouton Follow (overlay hover) ────────────────────────────── */}
        {onFollowToggle && (
          <button
            onClick={handleFollowClick}
            disabled={loading}
            aria-label={isFollowed ? 'Ne plus suivre' : 'Suivre'}
            style={{
              position: 'absolute',
              top: 6,
              left: 6,
              background: isFollowed
                ? 'rgba(255,255,255,0.9)'
                : 'rgba(0,0,0,0.65)',
              color: isFollowed ? '#111' : '#fff',
              border: 'none',
              borderRadius: '5px',
              padding: '3px 7px',
              fontSize: '10px',
              fontWeight: 600,
              cursor: loading ? 'wait' : 'pointer',
              opacity: loading ? 0.6 : 1,
              transition: 'opacity 0.15s',
            }}
            className="opacity-0 group-hover:opacity-100 group-focus-within:opacity-100"
          >
            {loading ? '…' : isFollowed ? 'Suivi ✓' : '+ Suivre'}
          </button>
        )}
      </div>
    </Link>
  );
}