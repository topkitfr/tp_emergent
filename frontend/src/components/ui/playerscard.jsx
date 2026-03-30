// frontend/src/components/ui/playerscard.jsx
import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { User } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

export default function PlayerCard({ player, isFollowed, onFollowToggle }) {
  const [loading, setLoading] = useState(false);

  const handleFollowClick = useCallback(
    async (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (loading) return;

      setLoading(true);
      try {
        const id = player.player_id || player._id;
        await onFollowToggle(id, !isFollowed);
      } finally {
        setLoading(false);
      }
    },
    [loading, onFollowToggle, player, isFollowed]
  );

  const imageUrl = proxyImageUrl(player.photo_url);
  const displayName = player.name || 'Unknown player';
  const nationality = player.nationality;
  const auraScore = player.aura_score;

  return (
    <Link
      to={`/players/${player.slug || player.player_id || player._id}`}
      className="group relative block overflow-hidden rounded-lg bg-surface shadow-sm transition hover:shadow-md"
      data-testid={`player-card-${player.player_id || player._id}`}
    >
      {/* Follow button overlay */}
      <button
        type="button"
        onClick={handleFollowClick}
        className="absolute right-2 top-2 z-10 rounded-full bg-surface/90 px-3 py-1 text-xs font-medium text-primary shadow-sm opacity-0 transition group-hover:opacity-100 group-focus-within:opacity-100"
        aria-label={isFollowed ? 'Unfollow player' : 'Follow player'}
      >
        {loading ? '...' : isFollowed ? 'Following' : 'Follow'}
      </button>

      {/* Image / avatar */}
      <div className="aspect-[3/4] w-full bg-surface-offset flex items-center justify-center overflow-hidden">
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

      {/* Content */}
      <div className="flex flex-col gap-1 px-3 py-2">
        <div className="truncate text-sm font-semibold text-text">
          {displayName}
        </div>
        {nationality && (
          <div className="truncate text-xs text-text-muted">
            {nationality}
          </div>
        )}
        <div className="mt-1 flex items-center justify-between text-[11px] text-text-faint">
          <span>{player.kit_count ?? 0} kits</span>
          {typeof auraScore === 'number' && (
            <span>Aura {auraScore.toFixed(1)}</span>
          )}
        </div>
      </div>
    </Link>
  );
}