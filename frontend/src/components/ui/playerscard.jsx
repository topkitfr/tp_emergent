// frontend/src/components/ui/playerscard.jsx
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

export default function PlayerCard({ player, isFollowed = false, onFollowToggle }) {
  const [loading, setLoading] = useState(false);

  const playerId = player.player_id || player._id || player.id;
  const playerSlug = player.slug || player.player_id || player._id || player.id;

  const handleFollowClick = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();

      if (loading || !playerId || typeof onFollowToggle !== 'function') return;

      setLoading(true);
      try {
        await onFollowToggle(playerId, !isFollowed);
      } finally {
        setLoading(false);
      }
    },
    [loading, playerId, onFollowToggle, isFollowed]
  );

  const imageUrl = proxyImageUrl(
    player.photo_url ||
      player.photo ||
      player.image_url ||
      player.image ||
      ''
  );

  const displayName =
    player.name ||
    player.player_name ||
    player.full_name ||
    player.display_name ||
    'Unknown player';

  const nationality =
    player.nationality ||
    player.country ||
    player.nation ||
    null;

  const position =
    player.position ||
    player.role ||
    player.poste ||
    player.player_position ||
    null;

  const auraScore =
    player.aura_score ??
    player.auraScore ??
    player.community_aura ??
    player.community_rating ??
    null;

  return (
    <Link
      to={`/players/${playerSlug}`}
      className="group relative block overflow-hidden rounded-lg bg-surface shadow-sm transition hover:shadow-md focus:outline-none focus:ring-2 focus:ring-primary/30"
      data-testid={`player-card-${playerId}`}
    >
      <button
        type="button"
        onClick={handleFollowClick}
        disabled={loading || !playerId || typeof onFollowToggle !== 'function'}
        className="absolute right-2 top-2 z-10 rounded-full bg-surface/90 px-3 py-1 text-xs font-medium text-primary shadow-sm transition opacity-100 sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100 disabled:cursor-not-allowed disabled:opacity-70"
        aria-label={isFollowed ? 'Unfollow player' : 'Follow player'}
      >
        {loading ? '...' : isFollowed ? 'Following' : 'Follow'}
      </button>

      <div className="flex aspect-[3/4] w-full items-center justify-center overflow-hidden bg-surface-offset">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={displayName}
            className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-[1.03]"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-text-muted">
            <User className="h-10 w-10" />
          </div>
        )}
      </div>

      <div className="flex flex-col gap-1 px-3 py-2">
        <div className="truncate text-sm font-semibold text-text">
          {displayName}
        </div>

        {nationality && (
          <div className="truncate text-xs text-text-muted">
            {nationality}
          </div>
        )}

        {position && (
          <div className="truncate text-xs text-text-muted">
            {position}
          </div>
        )}

        <div className="mt-1 flex items-center justify-between text-[11px] text-text-faint">
          <span>Aura communautaire</span>
          {typeof auraScore === 'number' ? (
            <span>{auraScore.toFixed(1)}</span>
          ) : (
            <span>—</span>
          )}
        </div>
      </div>
    </Link>
  );
}