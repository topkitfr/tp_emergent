import { useState } from 'react';
import { UserPlus, UserCheck } from 'lucide-react';

export function PlayerCard({ player, isFollowed: initialFollowed, onFollowToggle }) {
  const [followed, setFollowed] = useState(initialFollowed);
  const [loading, setLoading] = useState(false);

  const handleFollow = async (e) => {
    e.preventDefault(); // évite la navigation vers la page détail
    setLoading(true);
    await onFollowToggle(player._id, !followed);
    setFollowed(!followed);
    setLoading(false);
  };

  return (
    <a href={`/players/${player.slug}`} className="group relative block rounded-lg overflow-hidden border border-border bg-card hover:shadow-md transition-shadow">
      {/* Photo */}
      <div className="aspect-[3/4] bg-muted overflow-hidden">
        <img
          src={player.photo_url || '/placeholder-player.png'}
          alt={player.full_name}
          className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
      </div>

      {/* Info */}
      <div className="p-3 space-y-1">
        <p className="font-semibold text-sm truncate">{player.full_name}</p>
        <p className="text-xs text-muted-foreground">{player.position}</p>
        {player.aura_score != null && (
          <p className="text-xs font-mono font-bold text-primary">{player.aura_score}</p>
        )}
      </div>

      {/* Bouton follow — coin supérieur droit */}
      <button
        onClick={handleFollow}
        disabled={loading}
        aria-label={followed ? 'Ne plus suivre' : 'Suivre ce joueur'}
        className={`absolute top-2 right-2 p-1.5 rounded-full backdrop-blur-sm transition-colors
          ${followed
            ? 'bg-primary text-primary-foreground'
            : 'bg-background/80 text-muted-foreground hover:text-primary hover:bg-background'
          }`}
      >
        {followed ? <UserCheck size={14} /> : <UserPlus size={14} />}
      </button>
    </a>
  );
}