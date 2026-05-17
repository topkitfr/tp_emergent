import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { proxyImageUrl, getMasterKits } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  ThumbsUp, ThumbsDown, Shirt, Package, Users, Trophy,
  Star, Zap, Activity, Search, ArrowRight, ChevronDown, ChevronUp,
} from 'lucide-react';
import EntityAutocomplete from '@/components/EntityAutocomplete';

// ─── Constantes ──────────────────────────────────────────────────────────────

export const KIT_TYPES  = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
export const MODELS     = ['Authentic', 'Replica', 'Other'];
export const GENDERS    = ['Man', 'Woman', 'Kid'];
export const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];

export const SEASONS = Array.from({ length: 41 }, (_, i) => {
  const y = 1985 + i;
  return `${y}/${y + 1}`;
}).reverse();

export const FIELD_LABELS = {
  club: 'Club / Team', season: 'Season', kit_type: 'Type', brand: 'Brand',
  design: 'Design', sponsor: 'Sponsor', league: 'League', gender: 'Gender',
  front_photo: 'Front Photo', back_photo: 'Back Photo', competition: 'Competition',
  model: 'Model', sku_code: 'SKU Code', ean_code: 'EAN Code', kit_id: 'Parent Kit',
  version_id: 'Version ID', created_by: 'Created By', created_at: 'Created At',
  name: 'Name', full_name: 'Full Name', country: 'Country', city: 'City',
  founded: 'Founded', primary_color: 'Primary Color', secondary_color: 'Secondary Color',
  crest_url: 'Crest / Badge', logo_url: 'Logo', photo_url: 'Photo',
  country_or_region: 'Country / Region', level: 'Level', organizer: 'Organizer',
  nationality: 'Nationality', birth_year: 'Birth Year', positions: 'Positions',
  preferred_number: 'Preferred Number',
};

export const ENTITY_DISPLAY_FIELDS = {
  team: ['name', 'country', 'city', 'founded', 'primary_color', 'secondary_color'],
  league: ['name', 'country_or_region', 'level', 'organizer'],
  brand: ['name', 'country', 'founded'],
  player: ['full_name', 'nationality', 'birth_year', 'positions', 'preferred_number'],
  sponsor: ['name', 'country'],
};

export const ENTITY_IMAGE_FIELDS = {
  team: 'crest_url', league: 'logo_url', brand: 'logo_url',
  player: 'photo_url', sponsor: 'logo_url',
};

export const TYPE_LABELS = {
  master_kit: 'Master Kit', version: 'Version',
  team: 'Team', league: 'League', brand: 'Brand', player: 'Player', sponsor: 'Sponsor',
};

export const TYPE_ICONS = {
  master_kit: Shirt, version: Package, team: Users, league: Trophy,
  brand: Star, player: Zap, sponsor: Activity,
};

export const TYPE_COLORS = {
  master_kit: 'text-primary bg-primary/10 border-primary/20',
  version:    'text-blue-500 bg-blue-500/10 border-blue-500/20',
  team:       'text-orange-500 bg-orange-500/10 border-orange-500/20',
  league:     'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
  brand:      'text-purple-500 bg-purple-500/10 border-purple-500/20',
  player:     'text-green-500 bg-green-500/10 border-green-500/20',
  sponsor:    'text-pink-500 bg-pink-500/10 border-pink-500/20',
};

export const VOTE_THRESHOLD = 5;

// ─── Utils ────────────────────────────────────────────────────────────────────

export function getDisplayName(item) {
  return item?.display_name || item?.name || item?.full_name || item?.data?.name || item?.data?.full_name || '—';
}

export function emptyEntityBuckets() {
  return { team: [], league: [], brand: [], player: [], sponsor: [] };
}

export function buildEntityBucketsFromSubmissions(items = []) {
  const buckets = emptyEntityBuckets();
  items.forEach((sub) => {
    const ENTITY_TYPES = ['team', 'league', 'brand', 'player', 'sponsor'];
    if (!ENTITY_TYPES.includes(sub.submission_type)) return;
    if ((sub.data?.mode || 'create') !== 'create') return;
    const entityId = sub.data?.entity_id || sub.submission_id;
    const display_name = sub.data?.full_name || sub.data?.name || '—';
    const item = { ...sub.data, submission_id: sub.submission_id, display_name, status: sub.status, _id: entityId };
    if (sub.submission_type === 'team')    item.team_id    = entityId;
    if (sub.submission_type === 'league')  item.league_id  = entityId;
    if (sub.submission_type === 'brand')   item.brand_id   = entityId;
    if (sub.submission_type === 'player')  item.player_id  = entityId;
    if (sub.submission_type === 'sponsor') item.sponsor_id = entityId;
    buckets[sub.submission_type].push(item);
  });
  return buckets;
}

export function getSubmissionTitle(sub, existingKits = []) {
  if (sub.submission_type === 'master_kit') {
    if (sub.data?.mode === 'removal') return `Removal — ${sub.data?.club || '?'} ${sub.data?.season || ''} (${sub.data?.kit_type || '?'})`.trim();
    return `${sub.data?.club || '?'} - ${sub.data?.season || '?'} (${sub.data?.kit_type || '?'})`;
  }
  if (sub.submission_type === 'version') {
    if (sub.data?.mode === 'removal') {
      const kitId = sub.data?.kit_id;
      const parentKit = kitId ? existingKits.find(k => k.kit_id === kitId) : null;
      if (parentKit) return `Removal — ${parentKit.club} ${parentKit.season} (${parentKit.kit_type})`;
      return `Removal — Version ${sub.data?.version_id || sub.data?.entity_id || '?'}`;
    }
    return `${sub.data?.competition || '?'} - ${sub.data?.model || '?'}`;
  }
  if (sub.submission_type === 'player') return sub.data?.full_name || '?';
  return sub.data?.name || '?';
}

export function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

// ─── Composants ───────────────────────────────────────────────────────────────

export function UserLink({ name, username, className = '' }) {
  if (username) {
    return (
      <Link to={`/profile/${username}`} className={`hover:text-primary transition-colors ${className}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
        {name || username}
      </Link>
    );
  }
  return <span className={className} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{name || 'Unknown'}</span>;
}

export function UserAvatar({ username, name, photoUrl, size = 'md' }) {
  const sizes = { sm: 'w-8 h-8 text-xs', md: 'w-12 h-12 text-sm', lg: 'w-16 h-16 text-base' };
  const initials = (name || username || '?').slice(0, 2).toUpperCase();
  if (photoUrl) {
    return (
      <img
        src={proxyImageUrl(photoUrl)}
        alt={name || username}
        className={`${sizes[size]} rounded-full object-cover border border-border shrink-0`}
      />
    );
  }
  return (
    <div className={`${sizes[size]} rounded-full bg-primary/15 border border-primary/30 flex items-center justify-center shrink-0`}>
      <span className="font-bold text-primary" style={{ fontFamily: 'Barlow Condensed' }}>{initials}</span>
    </div>
  );
}

export function FeedCard({ sub }) {
  const Icon = TYPE_ICONS[sub.submission_type] || Package;
  const colorClass = TYPE_COLORS[sub.submission_type] || 'text-muted-foreground bg-secondary border-border';
  const title = sub.submission_type === 'player'
    ? (sub.data?.full_name || '?')
    : sub.submission_type === 'master_kit'
      ? `${sub.data?.club || '?'}`
      : (sub.data?.name || sub.data?.full_name || '?');
  const subtitle = sub.submission_type === 'master_kit'
    ? `${sub.data?.season || ''} · ${sub.data?.kit_type || ''}`
    : null;
  const imageField = ENTITY_IMAGE_FIELDS[sub.submission_type];
  const imageUrl = sub.data?.front_photo || (imageField && sub.data?.[imageField]);

  return (
    <div className="border border-border bg-card flex flex-col overflow-hidden hover:border-primary/40 transition-colors group">
      <div className="relative bg-secondary aspect-[3/4] overflow-hidden flex items-center justify-center">
        {imageUrl ? (
          <img src={proxyImageUrl(imageUrl)} alt={title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className={`w-12 h-12 flex items-center justify-center border rounded-sm ${colorClass}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
        <div className={`absolute top-2 left-2 border text-[9px] px-1.5 py-0.5 font-semibold uppercase tracking-wider ${colorClass}`}
          style={{ fontFamily: 'Barlow Condensed' }}>
          {TYPE_LABELS[sub.submission_type] || sub.submission_type}
        </div>
      </div>
      <div className="p-2 flex flex-col gap-0.5 min-w-0">
        <p className="text-xs font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{title}</p>
        {subtitle && <p className="text-[10px] text-muted-foreground truncate" style={{ fontFamily: 'DM Sans' }}>{subtitle}</p>}
        <div className="flex items-center justify-between mt-1">
          <span className="text-[10px] text-muted-foreground truncate" style={{ fontFamily: 'DM Sans' }}>
            <UserLink name={sub.submitter_name} username={sub.submitter_username} className="text-foreground/60 hover:text-primary" />
          </span>
          <span className="text-[10px] text-muted-foreground shrink-0 ml-1">{timeAgo(sub.created_at)}</span>
        </div>
      </div>
    </div>
  );
}

export function ContributorCard({ contributor, rank }) {
  const rankColors = ['text-yellow-500', 'text-slate-400', 'text-amber-600'];
  const rankBg = ['bg-yellow-500/10 border-yellow-500/30', 'bg-slate-400/10 border-slate-400/30', 'bg-amber-600/10 border-amber-600/30'];
  return (
    <div className="border border-border bg-card p-4 flex flex-col items-center text-center gap-3 relative hover:border-primary/40 transition-colors">
      {rank <= 3 && (
        <div className={`absolute top-2 right-2 w-5 h-5 flex items-center justify-center text-[10px] font-bold border rounded-full ${rankBg[rank - 1]} ${rankColors[rank - 1]}`}
          style={{ fontFamily: 'Barlow Condensed' }}>
          {rank}
        </div>
      )}
      <UserAvatar username={contributor.username} name={contributor.name} photoUrl={contributor.photo_url} size="lg" />
      <div>
        {contributor.username ? (
          <Link to={`/profile/${contributor.username}`} className="text-sm font-semibold hover:text-primary transition-colors block" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            {contributor.name || contributor.username}
          </Link>
        ) : (
          <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{contributor.name || 'Anonymous'}</p>
        )}
        {contributor.username && (
          <p className="text-[11px] text-muted-foreground" style={{ fontFamily: 'DM Sans' }}>@{contributor.username}</p>
        )}
      </div>
      <div className="flex items-center gap-3 text-center">
        <div>
          <p className="text-lg font-bold text-primary" style={{ fontFamily: 'Barlow Condensed' }}>{contributor.count}</p>
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>contributions</p>
        </div>
      </div>
    </div>
  );
}

export function SubmissionDetail({ sub, existingKits }) {
  const isEntity = ['team', 'league', 'brand', 'player', 'sponsor'].includes(sub.submission_type);
  const fields = isEntity
    ? (ENTITY_DISPLAY_FIELDS[sub.submission_type] || [])
    : sub.submission_type === 'master_kit'
      ? ['club', 'season', 'kit_type', 'brand', 'league', 'design', 'sponsor', 'gender']
      : ['competition', 'model', 'sku_code', 'ean_code'];
  const parentKit = sub.submission_type === 'version' && existingKits && existingKits.find(k => k.kit_id === sub.data?.kit_id);

  return (
    <div className="mt-4 pt-4 border-t border-border">
      {isEntity && sub.data?.mode && (
        <div className="mb-3">
          <Badge variant="outline" className="rounded-none text-[10px]">
            {sub.data.mode === 'create' ? 'New Entity' : 'Edit Suggestion'}
          </Badge>
          {sub.data.mode === 'edit' && sub.data.entity_id && (
            <span className="text-[10px] font-mono text-muted-foreground ml-2">{sub.data.entity_id}</span>
          )}
        </div>
      )}
      {parentKit && (
        <div className="mb-3 p-3 bg-secondary/30 border border-border">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Parent Master Kit</p>
          <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
            {parentKit.club} - {parentKit.season} ({parentKit.kit_type})
          </p>
        </div>
      )}
      {sub.data?.mode === 'removal' && sub.data?.notes && (
        <div className="mb-3 p-3 bg-destructive/10 border border-destructive/30">
          <p className="text-[10px] uppercase tracking-wider text-destructive mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Reason for Removal</p>
          <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{sub.data.notes}</p>
        </div>
      )}
      {sub.data?.mode !== 'removal' && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          {fields.map(field => (
            <div key={field} className="space-y-1">
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>{FIELD_LABELS[field] || field}</p>
              <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{sub.data?.[field] || '—'}</p>
            </div>
          ))}
        </div>
      )}
      {sub.data?.front_photo && sub.data?.mode !== 'removal' && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>Photo</p>
          <img src={proxyImageUrl(sub.data.front_photo)} alt="Jersey" className="w-24 h-32 object-cover border border-border" />
        </div>
      )}
      {isEntity && ENTITY_IMAGE_FIELDS[sub.submission_type] && sub.data?.[ENTITY_IMAGE_FIELDS[sub.submission_type]] && (
        <div className="mt-3">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-2" style={{ fontFamily: 'Barlow Condensed' }}>
            {FIELD_LABELS[ENTITY_IMAGE_FIELDS[sub.submission_type]] || 'Image'}
          </p>
          <img src={proxyImageUrl(sub.data[ENTITY_IMAGE_FIELDS[sub.submission_type]])} alt="" className="w-20 h-20 object-contain border border-border bg-secondary" />
        </div>
      )}
    </div>
  );
}

// ─── VoteProgressBar ─────────────────────────────────────────────────────────

export function VoteProgressBar({ upvotes = 0, threshold = VOTE_THRESHOLD }) {
  const filled = Math.min(upvotes, threshold);
  const blocks = Array.from({ length: threshold }, (_, i) => i < filled);
  return (
    <div className="flex items-center gap-1.5 mt-1.5">
      <div className="flex items-center gap-0.5">
        {blocks.map((isFilled, i) => (
          <div
            key={i}
            className={`w-4 h-2 ${isFilled ? 'bg-primary' : 'border border-border bg-transparent'}`}
          />
        ))}
      </div>
      <span className="font-mono text-[10px] text-muted-foreground">{filled}/{threshold} votes</span>
    </div>
  );
}

// ─── BeforeAfterDiff ─────────────────────────────────────────────────────────

const SKIP_DIFF_FIELDS = ['_id', 'kit_id', 'version_id', 'created_by', 'created_at', 'version_count', 'avg_rating', 'review_count'];

export function BeforeAfterDiff({ original = {}, corrections = {} }) {
  const [showUnchanged, setShowUnchanged] = useState(false);

  const allFields = [...new Set([
    ...Object.keys(original).filter(f => !SKIP_DIFF_FIELDS.includes(f)),
    ...Object.keys(corrections).filter(f => !SKIP_DIFF_FIELDS.includes(f)),
  ])];

  const changedFields = allFields.filter(f => {
    const proposed = corrections[f];
    return proposed !== undefined && String(proposed) !== String(original[f] ?? '');
  });
  const unchangedFields = allFields.filter(f => !changedFields.includes(f));

  if (allFields.length === 0) {
    return (
      <p className="text-xs text-muted-foreground italic" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
        Aucun changement détecté.
      </p>
    );
  }

  const renderField = (field) => {
    const orig = original[field];
    const proposed = corrections[field];
    const changed = proposed !== undefined && String(proposed) !== String(orig ?? '');
    const isMedia = field.includes('photo') || field === 'logo_url' || field === 'crest_url';

    return (
      <div key={field} className={`py-2 px-3 border-b border-border/30 last:border-b-0 ${changed ? 'bg-primary/5' : ''}`}>
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5" style={{ fontFamily: 'Barlow Condensed' }}>
          {FIELD_LABELS[field] || field}
        </p>
        {isMedia ? (
          <div className="flex items-start gap-4">
            <div className="flex flex-col items-start gap-1">
              <span className="text-[9px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Actuel</span>
              {orig ? (
                <img src={proxyImageUrl(orig)} alt="actuel" className="w-14 h-18 object-cover border border-border" />
              ) : (
                <span className="text-xs text-muted-foreground">—</span>
              )}
            </div>
            {changed && (
              <div className="flex flex-col items-start gap-1">
                <span className="text-[9px] uppercase tracking-wider text-primary" style={{ fontFamily: 'Barlow Condensed' }}>Proposé</span>
                {proposed ? (
                  <img src={proxyImageUrl(proposed)} alt="proposé" className="w-14 h-18 object-cover border border-primary/40" />
                ) : (
                  <span className="text-xs text-muted-foreground">—</span>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-0.5">
            <div className="flex items-start gap-2">
              <span className="text-[9px] uppercase tracking-wider text-muted-foreground shrink-0 mt-0.5 w-8" style={{ fontFamily: 'Barlow Condensed' }}>
                {changed ? 'Avant' : 'Val.'}
              </span>
              <span
                className={`text-sm ${changed ? 'line-through text-muted-foreground/50' : 'text-foreground'}`}
                style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
              >
                {orig !== undefined && orig !== null ? String(orig) : '—'}
              </span>
            </div>
            {changed && (
              <div className="flex items-start gap-2">
                <span className="text-[9px] uppercase tracking-wider text-primary shrink-0 mt-0.5 w-8" style={{ fontFamily: 'Barlow Condensed' }}>Après</span>
                <span className="text-sm text-primary font-medium" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  {String(proposed)}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="border border-border">
      {changedFields.map(renderField)}
      {unchangedFields.length > 0 && (
        <>
          <button
            onClick={() => setShowUnchanged(v => !v)}
            className="w-full text-left px-3 py-2 text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
            style={{ fontFamily: 'Barlow Condensed' }}
          >
            {showUnchanged
              ? <><ChevronUp className="w-3 h-3" /> Masquer</>
              : <><ChevronDown className="w-3 h-3" /> Voir les {unchangedFields.length} champs inchangés</>
            }
          </button>
          {showUnchanged && unchangedFields.map(renderField)}
        </>
      )}
    </div>
  );
}

// ─── VoteCard ────────────────────────────────────────────────────────────────

export function VoteCard({
  item,
  onVoteUp,
  onVoteDown,
  hasVoted,
  canVote = true,
  expanded,
  onToggle,
  children,
  title,
  subtitle,
  badges,
  isModerator = false,
}) {
  const isPending = item?.status === 'pending';

  return (
    <div className="border border-border bg-card">
      <div
        className="flex items-start justify-between gap-4 p-4 cursor-pointer hover:bg-secondary/20 transition-colors"
        onClick={onToggle}
      >
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">{badges}</div>
          <h4 className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{title}</h4>
          <p className="text-xs text-muted-foreground mt-0.5" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{subtitle}</p>
          {isPending && (
            <VoteProgressBar upvotes={item.votes_up || 0} threshold={isModerator ? 1 : VOTE_THRESHOLD} />
          )}
          {isPending && isModerator && (
            <p className="text-[10px] text-primary mt-1" style={{ fontFamily: 'Barlow Condensed' }}>
              VOTRE VOTE VALIDE INSTANTANÉMENT
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0" onClick={e => e.stopPropagation()}>
          {isPending && !hasVoted && canVote && (
            <div className="flex gap-1">
              <button
                onClick={onVoteUp}
                className="p-2 border border-border hover:border-primary hover:text-primary transition-colors"
                title="Voter pour"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button
                onClick={onVoteDown}
                className="p-2 border border-border hover:border-destructive hover:text-destructive transition-colors"
                title="Voter contre"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          )}
          {hasVoted && (
            <Badge variant="secondary" className="rounded-none text-[10px]">Voté</Badge>
          )}
          {!canVote && isPending && !hasVoted && (
            <span className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Pas éligible</span>
          )}
          <button onClick={onToggle} className="p-1 text-muted-foreground hover:text-foreground transition-colors">
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>
      {expanded && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// ─── VoteRow (alias for backward compat) ─────────────────────────────────────

export function VoteRow({ item, onVoteUp, onVoteDown, hasVoted, expanded, onToggle, children, title, subtitle, badges }) {
  return (
    <div className="border border-border bg-card">
      <div className="flex items-start justify-between gap-4 p-4 cursor-pointer hover:bg-secondary/20 transition-colors" onClick={onToggle}>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">{badges}</div>
          <h4 className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{title}</h4>
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <div className="text-center">
            <div className="flex items-center gap-1">
              <span className="font-mono text-sm text-primary">{item.votes_up}</span>
              <span className="text-muted-foreground">/</span>
              <span className="font-mono text-sm text-destructive">{item.votes_down}</span>
            </div>
            <span className="text-[10px] text-muted-foreground">votes</span>
          </div>
          {item.status === 'pending' && !hasVoted && (
            <div className="flex gap-1" onClick={e => e.stopPropagation()}>
              <button onClick={onVoteUp} className="p-2 border border-border hover:border-primary hover:text-primary transition-colors">
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button onClick={onVoteDown} className="p-2 border border-border hover:border-destructive hover:text-destructive transition-colors">
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          )}
          {hasVoted && <Badge variant="secondary" className="rounded-none text-[10px]">Voted</Badge>}
          {expanded ? <ChevronUp className="w-4 h-4 text-muted-foreground" /> : <ChevronDown className="w-4 h-4 text-muted-foreground" />}
        </div>
      </div>
      {expanded && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

// ─── ReportDetail ─────────────────────────────────────────────────────────────

export function ReportDetail({ rep }) {
  return (
    <div>
      <BeforeAfterDiff original={rep.original_data || {}} corrections={rep.corrections || {}} />
      {rep.notes && (
        <div className="mt-3 p-3 bg-secondary/30 border border-border">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Notes</p>
          <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{rep.notes}</p>
        </div>
      )}
    </div>
  );
}

// ─── UseExistingKitPanel ──────────────────────────────────────────────────────

const ANY_TYPE   = '__all__';
const ANY_SEASON = '__any__';

export function UseExistingKitPanel({ onSelect }) {
  const [filterTeamLabel, setFilterTeamLabel] = useState('');
  const [filterSeason, setFilterSeason]       = useState(ANY_SEASON);
  const [filterType,   setFilterType]         = useState(ANY_TYPE);
  const [results,  setResults]                = useState([]);
  const [searched, setSearched]               = useState(false);
  const [loading,  setLoading]                = useState(false);

  const handleSearch = async () => {
    setLoading(true); setSearched(true);
    try {
      const params = { limit: 100 };
      if (filterTeamLabel.trim())                      params.club     = filterTeamLabel.trim();
      if (filterSeason && filterSeason !== ANY_SEASON) params.season   = filterSeason;
      if (filterType   && filterType   !== ANY_TYPE)   params.kit_type = filterType;
      const res = await getMasterKits(params);
      setResults(res.data?.results ?? []);
    } catch {
      toast.error('Failed to search kits');
    } finally {
      setLoading(false);
    }
  };

  const canSearch = filterTeamLabel.trim() !== '' && filterSeason !== ANY_SEASON && filterType !== ANY_TYPE;

  return (
    <div className="border border-border p-4 mb-4">
      <h4 className="text-xs uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed' }}>Use Existing Kit</h4>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
        <div className="space-y-1">
          <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Team *</Label>
          <EntityAutocomplete entityType="team" value={filterTeamLabel}
            onChange={(val) => setFilterTeamLabel(val)}
            onSelect={(item) => setFilterTeamLabel(item.label)}
            placeholder="e.g. AC Milan" className="bg-card border-border rounded-none text-xs" testId="filter-team" />
        </div>
        <div className="space-y-1">
          <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
          <Select value={filterSeason} onValueChange={setFilterSeason}>
            <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="Select season" /></SelectTrigger>
            <SelectContent className="bg-card border-border max-h-56">{SEASONS.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <div className="space-y-1">
          <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Type *</Label>
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="bg-card border-border rounded-none text-xs"><SelectValue placeholder="Select type" /></SelectTrigger>
            <SelectContent className="bg-card border-border">{KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
          </Select>
        </div>
      </div>
      <Button onClick={handleSearch} disabled={!canSearch || loading} size="sm" variant="outline" className="rounded-none mb-4">
        <Search className="w-3 h-3 mr-1" />{loading ? 'Searching...' : 'Search'}
      </Button>
      {!canSearch && <p className="text-[10px] text-muted-foreground mb-3" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Please fill in Team, Season and Type to search.</p>}
      {searched && !loading && (
        results.length === 0 ? (
          <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No matching kits found. You can create a new one below.</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {results.map(k => (
              <button key={k.kit_id} onClick={() => onSelect(k)}
                className="w-full flex items-center gap-3 border border-border bg-background hover:border-primary hover:bg-primary/5 p-3 transition-colors text-left">
                {k.front_photo ? (
                  <img src={proxyImageUrl(k.front_photo)} alt="" className="w-10 h-14 object-cover border border-border shrink-0" />
                ) : (
                  <div className="w-10 h-14 bg-secondary border border-border flex items-center justify-center shrink-0">
                    <Shirt className="w-5 h-5 text-muted-foreground" />
                  </div>
                )}
                <div className="min-w-0">
                  <p className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{k.club}</p>
                  <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{k.season} · {k.kit_type}{k.brand ? ` · ${k.brand}` : ''}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground ml-auto shrink-0" />
              </button>
            ))}
          </div>
        )
      )}
    </div>
  );
}
