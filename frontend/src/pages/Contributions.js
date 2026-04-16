import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import {
  getSubmissions, getReports, voteOnSubmission, voteOnReport,
  createSubmission, getMasterKits, proxyImageUrl,
  createTeamPending, createBrandPending, createLeaguePending, createSponsorPending,
  getUserByUsername,
} from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  ThumbsUp, ThumbsDown, Shirt, FileCheck, AlertTriangle, Plus, Check, Clock, X,
  ChevronDown, ChevronUp, ArrowRight, ArrowLeft, CheckCircle2, Search,
  Trophy, Activity, Users, Package, Star, Zap,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';

// ===== CONSTANTES =====
const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const MODELS = ['Authentic', 'Replica', 'Other'];
const GENDERS = ['Man', 'Woman', 'Kid'];
const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];

const SEASONS = Array.from({ length: 41 }, (_, i) => {
  const y = 1985 + i;
  return `${y}/${y + 1}`;
}).reverse();

const FIELD_LABELS = {
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

const ENTITY_DISPLAY_FIELDS = {
  team: ['name', 'country', 'city', 'founded', 'primary_color', 'secondary_color'],
  league: ['name', 'country_or_region', 'level', 'organizer'],
  brand: ['name', 'country', 'founded'],
  player: ['full_name', 'nationality', 'birth_year', 'positions', 'preferred_number'],
  sponsor: ['name', 'country'],
};

const ENTITY_IMAGE_FIELDS = {
  team: 'crest_url',
  league: 'logo_url',
  brand: 'logo_url',
  player: 'photo_url',
  sponsor: 'logo_url',
};

const TYPE_LABELS = {
  master_kit: 'Master Kit', version: 'Version',
  team: 'Team', league: 'League', brand: 'Brand', player: 'Player', sponsor: 'Sponsor',
};

const TYPE_ICONS = {
  master_kit: Shirt,
  version: Package,
  team: Users,
  league: Trophy,
  brand: Star,
  player: Zap,
  sponsor: Activity,
};

const TYPE_COLORS = {
  master_kit: 'text-primary bg-primary/10 border-primary/20',
  version:    'text-blue-500 bg-blue-500/10 border-blue-500/20',
  team:       'text-orange-500 bg-orange-500/10 border-orange-500/20',
  league:     'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
  brand:      'text-purple-500 bg-purple-500/10 border-purple-500/20',
  player:     'text-green-500 bg-green-500/10 border-green-500/20',
  sponsor:    'text-pink-500 bg-pink-500/10 border-pink-500/20',
};

// ===== UTILS =====
function getDisplayName(item) {
  return item?.display_name || item?.name || item?.full_name || item?.data?.name || item?.data?.full_name || '—';
}

function emptyEntityBuckets() {
  return { team: [], league: [], brand: [], player: [], sponsor: [] };
}

function buildEntityBucketsFromSubmissions(items = []) {
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

function getSubmissionTitle(sub, existingKits = []) {
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

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
  return new Date(dateStr).toLocaleDateString();
}

// ===== COMPOSANT: USERNAME =====
function UserLink({ name, username, className = '' }) {
  if (username) {
    return (
      <Link to={`/profile/${username}`} className={`hover:text-primary transition-colors ${className}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
        {name || username}
      </Link>
    );
  }
  return <span className={className} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{name || 'Unknown'}</span>;
}

// ===== COMPOSANT: AVATAR =====
function UserAvatar({ username, name, photoUrl, size = 'md' }) {
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

// ===== COMPOSANT: FEED CARD (mini browser style) =====
function FeedCard({ sub }) {
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
      {/* Image zone */}
      <div className="relative bg-secondary aspect-[3/4] overflow-hidden flex items-center justify-center">
        {imageUrl ? (
          <img
            src={proxyImageUrl(imageUrl)}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className={`w-12 h-12 flex items-center justify-center border rounded-sm ${colorClass}`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
        {/* Type badge */}
        <div className={`absolute top-2 left-2 border text-[9px] px-1.5 py-0.5 font-semibold uppercase tracking-wider ${colorClass}`}
          style={{ fontFamily: 'Barlow Condensed' }}>
          {TYPE_LABELS[sub.submission_type] || sub.submission_type}
        </div>
      </div>
      {/* Info zone */}
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

// ===== COMPOSANT: TOP CONTRIBUTOR CARD =====
function ContributorCard({ contributor, rank }) {
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
      <UserAvatar
        username={contributor.username}
        name={contributor.name}
        photoUrl={contributor.photo_url}
        size="lg"
      />
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
        {contributor.score !== undefined && (
          <>
            <div className="w-px h-8 bg-border" />
            <div>
              <p className="text-lg font-bold text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>—</p>
              <p className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>score</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ===== COMPOSANT: SUBMISSION DETAIL =====
function SubmissionDetail({ sub, existingKits }) {
  const isEntity = ['team', 'league', 'brand', 'player', 'sponsor'].includes(sub.submission_type);
  const fields = isEntity
    ? (ENTITY_DISPLAY_FIELDS[sub.submission_type] || [])
    : sub.submission_type === 'master_kit'
      ? ['club', 'season', 'kit_type', 'brand', 'league', 'design', 'sponsor', 'gender']
      : ['competition', 'model', 'sku_code', 'ean_code'];
  const parentKit = sub.submission_type === 'version' && existingKits.find(k => k.kit_id === sub.data?.kit_id);

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

// ===== COMPOSANT: REPORT DETAIL =====
function ReportDetail({ rep }) {
  const skipFields = ['_id', 'kit_id', 'version_id', 'created_by', 'created_at', 'version_count', 'avg_rating', 'review_count'];
  const allFields = [...new Set([
    ...Object.keys(rep.original_data || {}).filter(f => !skipFields.includes(f)),
    ...Object.keys(rep.corrections || {}).filter(f => !skipFields.includes(f)),
  ])];
  return (
    <div className="mt-4 pt-4 border-t border-border">
      <div className="grid grid-cols-[1fr,1fr,1fr] gap-0 text-[10px] uppercase tracking-wider text-muted-foreground mb-2 px-2" style={{ fontFamily: 'Barlow Condensed' }}>
        <span>Field</span><span>Current</span><span>Proposed</span>
      </div>
      {allFields.map(field => {
        const original = rep.original_data?.[field];
        const proposed = rep.corrections?.[field];
        const changed = proposed !== undefined && String(proposed) !== String(original);
        const isMediaField = field.includes('photo') || field === 'logo_url' || field === 'crest_url';
        return (
          <div key={field} className={`grid grid-cols-[1fr,1fr,1fr] gap-0 py-2 px-2 border-t border-border/30 ${changed ? 'bg-primary/5' : ''}`}>
            <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{FIELD_LABELS[field] || field}</span>
            {isMediaField ? (
              <>
                <div>{original ? <img src={proxyImageUrl(original)} alt="" className="w-12 h-16 object-cover border border-border" /> : <span className="text-xs text-muted-foreground">—</span>}</div>
                <div>{changed && proposed ? <img src={proxyImageUrl(proposed)} alt="" className="w-12 h-16 object-cover border border-primary/30" /> : <span className="text-xs text-muted-foreground">—</span>}</div>
              </>
            ) : (
              <>
                <span className={`text-sm ${changed ? 'line-through text-muted-foreground/50' : ''}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{original !== undefined && original !== null ? String(original) : '—'}</span>
                <span className={`text-sm ${changed ? 'text-primary font-medium' : 'text-muted-foreground'}`} style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{changed ? String(proposed) : '—'}</span>
              </>
            )}
          </div>
        );
      })}
      {rep.notes && (
        <div className="mt-3 p-3 bg-secondary/30 border border-border">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Reporter Notes</p>
          <p className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{rep.notes}</p>
        </div>
      )}
    </div>
  );
}

// ===== COMPOSANT: USE EXISTING KIT =====
const ANY_TYPE   = '__all__';
const ANY_SEASON = '__any__';

function UseExistingKitPanel({ onSelect }) {
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
    } catch (e) {
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

// ===== COMPOSANT VOTE ROW =====
function VoteRow({ item, onVoteUp, onVoteDown, hasVoted, expanded, onToggle, children, title, subtitle, badges }) {
  return (
    <div className="border border-border bg-card">
      <div
        className="flex items-start justify-between gap-4 p-4 cursor-pointer hover:bg-secondary/20 transition-colors"
        onClick={onToggle}
      >
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

// ===== COMPOSANT PRINCIPAL =====
export default function Contributions() {
  const { user } = useAuth();

  const [activeTab, setActiveTab]               = useState('pending');
  const [submissions, setSubmissions]           = useState([]);
  const [reports, setReports]                   = useState([]);
  const [loading, setLoading]                   = useState(true);
  const [existingKits, setExistingKits]         = useState([]);
  const [expandedSubmission, setExpandedSubmission] = useState(null);
  const [expandedReport, setExpandedReport]     = useState(null);
  const [pendingEntities, setPendingEntities]   = useState(emptyEntityBuckets());
  const [approvedEntities, setApprovedEntities] = useState(emptyEntityBuckets());
  const [loadingPending, setLoadingPending]     = useState(false);

  const [recentApproved, setRecentApproved]     = useState([]);
  const [loadingFeed, setLoadingFeed]           = useState(true);
  const [topContributors, setTopContributors]   = useState([]);

  const [showAddForm, setShowAddForm]           = useState(false);
  const [addStep, setAddStep]                   = useState(1);
  const [subType, setSubType]                   = useState('master_kit');
  const [submitting, setSubmitting]             = useState(false);

  const [club, setClub]           = useState('');
  const [teamId, setTeamId]       = useState('');
  const [season, setSeason]       = useState('');
  const [kitType, setKitType]     = useState('');
  const [brand, setBrand]         = useState('');
  const [brandId, setBrandId]     = useState('');
  const [frontPhoto, setFrontPhoto] = useState('');
  const [design, setDesign]       = useState('');
  const [sponsor, setSponsor]     = useState('');
  const [sponsorId, setSponsorId] = useState('');
  const [leagueId, setLeagueId]   = useState('');
  const [league, setLeague]       = useState('');
  const [gender, setGender]       = useState('');

  const [selectedKit, setSelectedKit]           = useState('');
  const [selectedKitLabel, setSelectedKitLabel] = useState('');
  const [competition, setCompetition]           = useState('');
  const [model, setModel]                       = useState('');
  const [skuCode, setSkuCode]                   = useState('');
  const [eanCode, setEanCode]                   = useState('');
  const [verFrontPhoto, setVerFrontPhoto]       = useState('');
  const [verBackPhoto, setVerBackPhoto]         = useState('');

  // ===== FETCH FEED + CONTRIBUTORS =====
  useEffect(() => {
    async function fetchFeedData() {
      setLoadingFeed(true);
      try {
        const res = await getSubmissions({ status: 'approved', limit: 30 });
        const approved = res.data || [];
        setRecentApproved(approved);

        // Agréger les top contributeurs
        const counts = {};
        approved.forEach(sub => {
          const key = sub.submitter_username || sub.submitter_name || 'anonymous';
          if (!counts[key]) {
            counts[key] = {
              username: sub.submitter_username,
              name: sub.submitter_name,
              count: 0,
              photo_url: null,
            };
          }
          counts[key].count++;
        });

        const sorted = Object.values(counts).sort((a, b) => b.count - a.count).slice(0, 9);

        // Fetch photo_url pour chaque contributeur qui a un username
        const enriched = await Promise.all(
          sorted.map(async (c) => {
            if (!c.username) return c;
            try {
              const profileRes = await getUserByUsername(c.username);
              const profile = profileRes?.data;
              return { ...c, photo_url: profile?.photo_url || null, name: profile?.name || c.name };
            } catch {
              return c;
            }
          })
        );

        setTopContributors(enriched);
      } catch (e) {
        console.error('Failed to fetch feed:', e);
      } finally {
        setLoadingFeed(false);
      }
    }
    fetchFeedData();
  }, []);

  // ===== FETCH QUEUE =====
  const fetchData = useCallback(async () => {
    setLoading(true);
    setLoadingPending(true);
    try {
      const status = activeTab === 'approved' ? 'approved' : activeTab === 'rejected' ? 'rejected' : 'pending';
      const [subsRes, repsRes] = await Promise.all([
        getSubmissions({ status }),
        getReports({ status }),
      ]);
      const nextSubs = subsRes.data || [];
      setSubmissions(nextSubs);
      setReports(repsRes.data || []);
      const entityBuckets = buildEntityBucketsFromSubmissions(nextSubs);
      if (status === 'approved') {
        setApprovedEntities(entityBuckets);
        setPendingEntities(emptyEntityBuckets());
      } else {
        setPendingEntities(entityBuckets);
        setApprovedEntities(emptyEntityBuckets());
      }
    } catch (e) {
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
      setLoadingPending(false);
    }
  }, [activeTab]);

  useEffect(() => { fetchData(); }, [activeTab, fetchData]);

  useEffect(() => {
    getMasterKits({ limit: 500 }).then(res => setExistingKits(res.data?.results ?? [])).catch(console.error);
  }, []);

  // ===== SUBMIT =====
  const handleSubmitKit = async () => {
    if (!club.trim() || !season.trim() || !kitType || !brand.trim() || !frontPhoto) {
      toast.error('Please fill all required fields (Club, Season, Type, Brand, Photo)'); return;
    }
    setSubmitting(true);
    try {
      const data = { club, team_id: teamId, season, kit_type: kitType, brand, brand_id: brandId, league, league_id: leagueId, sponsor, sponsor_id: sponsorId, design, gender, front_photo: frontPhoto };
      const submissionRes = await createSubmission({ submission_type: 'master_kit', data });
      const masterKitSubmissionId = submissionRes?.data?.submission_id;
      if (masterKitSubmissionId) {
        const pendingJobs = [];
        if (!teamId    && club.trim())    pendingJobs.push(createTeamPending(   { name: club.trim()    }, masterKitSubmissionId));
        if (!brandId   && brand.trim())   pendingJobs.push(createBrandPending(  { name: brand.trim()   }, masterKitSubmissionId));
        if (!leagueId  && league.trim())  pendingJobs.push(createLeaguePending( { name: league.trim()  }, masterKitSubmissionId));
        if (!sponsorId && sponsor.trim()) pendingJobs.push(createSponsorPending({ name: sponsor.trim() }, masterKitSubmissionId));
        await Promise.allSettled(pendingJobs);
      }
      toast.success('Master kit submitted for community review!');
      closeAddForm();
      await fetchData();
      const kitsRes = await getMasterKits();
      setExistingKits(kitsRes.data?.results ?? []);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmitVersion = async () => {
    if (!selectedKit || !competition || !model) {
      toast.error('Please fill all required fields (Parent Kit, Competition, Model)'); return;
    }
    setSubmitting(true);
    try {
      await createSubmission({ submission_type: 'version', data: { kit_id: selectedKit, competition, model, sku_code: skuCode, ean_code: eanCode, front_photo: verFrontPhoto, back_photo: verBackPhoto } });
      toast.success('Version submitted for community review!');
      closeAddForm();
      await fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  const closeAddForm = () => {
    setShowAddForm(false); setAddStep(1); setSubType('master_kit');
    setClub(''); setTeamId(''); setSponsorId(''); setSeason(''); setKitType(''); setBrand(''); setBrandId('');
    setFrontPhoto(''); setDesign(''); setSponsor(''); setLeague(''); setLeagueId(''); setGender('');
    setSelectedKit(''); setSelectedKitLabel(''); setCompetition(''); setModel('');
    setSkuCode(''); setEanCode(''); setVerFrontPhoto(''); setVerBackPhoto('');
  };

  const handleSelectExistingKit = (kit) => {
    setSelectedKit(kit.kit_id);
    setSelectedKitLabel(`${kit.club} — ${kit.season} (${kit.kit_type})`);
    setAddStep(2); setSubType('version');
  };

  const hasVoted = (item) => item.voters?.includes(user?.user_id);
  const isModerator = user?.role === 'moderator' || user?.role === 'admin';

  const handleVoteSubmission = async (submissionId, isUpvote) => {
    try {
      await voteOnSubmission(submissionId, isUpvote ? 'up' : 'down');
      await fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to register vote');
    }
  };

  const handleVoteReport = async (reportId, vote) => {
    try {
      await voteOnReport(reportId, vote);
      await fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to register vote');
    }
  };

  const entityEditSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    ['edit', 'removal'].includes(s.data?.mode)
  );
  const entityCreateSubs = submissions.filter(s =>
    ['team', 'league', 'brand', 'player', 'sponsor'].includes(s.submission_type) &&
    s.data?.mode === 'create'
  );
  const standaloneEntitySubs = entityCreateSubs.filter(s => !s.data?.parent_submission_id);
  const jerseyAndCreateSubs = submissions.filter(s =>
    !entityEditSubs.includes(s) &&
    !entityCreateSubs.includes(s) &&
    (s.submission_type === 'master_kit' || s.submission_type === 'version')
  );

  const totalApproved = recentApproved.length;
  const pendingCount = submissions.filter(s => s.status === 'pending').length + reports.filter(r => r.status === 'pending').length;

  return (
    <div className="animate-fade-in-up">

      {/* ===== HEADER ===== */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2">CONTRIBUTIONS</h1>
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                Suivez les ajouts de la communauté, votez sur les soumissions en attente, et découvrez les meilleurs contributeurs.
                {isModerator ? ' En tant que modérateur, votre vote valide instantanément.' : ' 5 votes requis pour validation.'}
              </p>
              {isModerator && <Badge className="mt-2 rounded-none bg-primary/20 text-primary border-primary/30">Moderator</Badge>}
            </div>
            <Button onClick={() => setShowAddForm(!showAddForm)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 shrink-0">
              <Plus className="w-4 h-4 mr-1" /> Add Jersey
            </Button>
          </div>

          <div className="flex items-center gap-6 mt-6 pt-6 border-t border-border">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{totalApproved}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>ajouts récents</span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-orange-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{pendingCount}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>en attente de vote</span>
            </div>
            <div className="w-px h-4 bg-border" />
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-500" />
              <span className="text-sm font-semibold" style={{ fontFamily: 'Barlow Condensed' }}>{topContributors.length}</span>
              <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>contributeurs actifs</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 lg:px-8 py-8 space-y-12">

        {/* ===== FORMULAIRE ADD ===== */}
        {showAddForm && (
          <div className="border border-primary/30 p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className={`flex items-center gap-2 ${addStep === 1 ? 'text-primary' : 'text-muted-foreground'}`}>
                <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 1 ? 'bg-primary text-primary-foreground' : addStep > 1 ? 'bg-primary/20 text-primary' : 'bg-secondary text-muted-foreground'}`}>
                  {addStep > 1 ? <Check className="w-3 h-3" /> : '1'}
                </div>
                <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>MASTER KIT</span>
              </div>
              <div className="w-8 h-px bg-border" />
              <div className={`flex items-center gap-2 ${addStep === 2 ? 'text-primary' : 'text-muted-foreground'}`}>
                <div className={`w-6 h-6 flex items-center justify-center text-xs font-mono ${addStep === 2 ? 'bg-primary text-primary-foreground' : 'bg-secondary text-muted-foreground'}`}>2</div>
                <span className="text-xs tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>VERSION</span>
              </div>
            </div>

            {addStep === 1 && (
              <div>
                <UseExistingKitPanel onSelect={handleSelectExistingKit} />
                <div className="text-center text-xs text-muted-foreground tracking-wider my-4" style={{ fontFamily: 'Barlow Condensed' }}>OR CREATE NEW</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Team *</Label>
                    <EntityAutocomplete entityType="team" value={club}
                      onChange={(val) => { setClub(val); setTeamId(''); }}
                      onSelect={(item) => { setClub(item.label); setTeamId(item.id); }}
                      placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" testId="add-club" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Season *</Label>
                    <Input value={season} onChange={(e) => setSeason(e.target.value)} placeholder="e.g., 2024/2025" className="bg-card border-border rounded-none" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>League</Label>
                    <EntityAutocomplete entityType="league" value={league}
                      onChange={(val) => { setLeague(val); setLeagueId(''); }}
                      onSelect={(item) => { setLeague(item.label); setLeagueId(item.id); }}
                      placeholder="e.g., Ligue 1" className="bg-card border-border rounded-none" testId="add-league" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Type *</Label>
                    <Select value={kitType} onValueChange={setKitType}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select type" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">{KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Brand *</Label>
                    <EntityAutocomplete entityType="brand" value={brand}
                      onChange={(val) => { setBrand(val); setBrandId(''); }}
                      onSelect={(item) => { setBrand(item.label); setBrandId(item.id); }}
                      placeholder="e.g., Nike" className="bg-card border-border rounded-none" testId="add-brand" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Design</Label>
                    <Input value={design} onChange={(e) => setDesign(e.target.value)} placeholder="e.g., Single stripe" className="bg-card border-border rounded-none" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Sponsor</Label>
                    <EntityAutocomplete entityType="sponsor" value={sponsor}
                      onChange={(val) => { setSponsor(val); setSponsorId(''); }}
                      onSelect={(item) => { setSponsor(item.label); setSponsorId(item.id); }}
                      placeholder="e.g., Qatar Airways" className="bg-card border-border rounded-none" testId="add-sponsor" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Gender</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select gender" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">{GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo *</Label>
                    <ImageUpload value={frontPhoto} onChange={setFrontPhoto} testId="add-front-photo" />
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <Button onClick={handleSubmitKit} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
                    {submitting ? 'Submitting...' : 'Submit Master Kit'} <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none">Cancel</Button>
                </div>
              </div>
            )}

            {addStep === 2 && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <button onClick={() => { setAddStep(1); setSelectedKit(''); setSelectedKitLabel(''); }} className="text-muted-foreground hover:text-foreground">
                    <ArrowLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>
                    ADDING VERSION TO{' '}
                    <span className="text-foreground">{selectedKitLabel || 'NEW KIT (PENDING)'}</span>
                  </span>
                </div>
                {!selectedKit && (
                  <div className="mb-4">
                    <Label className="text-xs uppercase tracking-wider mb-2 block" style={{ fontFamily: 'Barlow Condensed' }}>Select Parent Kit *</Label>
                    <Select value={selectedKit} onValueChange={setSelectedKit}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select a Master Kit" /></SelectTrigger>
                      <SelectContent className="bg-card border-border max-h-60">
                        {existingKits.map(k => <SelectItem key={k.kit_id} value={k.kit_id}>{k.club} - {k.season} ({k.kit_type})</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                )}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Competition *</Label>
                    <Select value={competition} onValueChange={setCompetition}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select competition" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">{COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Model *</Label>
                    <Select value={model} onValueChange={setModel}>
                      <SelectTrigger className="bg-card border-border rounded-none"><SelectValue placeholder="Select model" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">{MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                    <Input value={skuCode} onChange={e => setSkuCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EAN Code</Label>
                    <Input value={eanCode} onChange={e => setEanCode(e.target.value)} placeholder="Optional" className="bg-card border-border rounded-none font-mono" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                    <ImageUpload value={verFrontPhoto} onChange={setVerFrontPhoto} folder="version" side="front" testId="add-ver-front-photo" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Back Photo</Label>
                    <ImageUpload value={verBackPhoto} onChange={setVerBackPhoto} folder="version" side="back" testId="add-ver-back-photo" />
                  </div>
                </div>
                <div className="flex gap-2 mt-6">
                  <Button onClick={handleSubmitVersion} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
                    {submitting ? 'Submitting...' : 'Submit Version for Review'} <Check className="w-4 h-4 ml-1" />
                  </Button>
                  <Button variant="outline" onClick={closeAddForm} className="rounded-none">Cancel</Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===== SECTION 1 : DERNIERS AJOUTS (image cards) ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <Activity className="w-5 h-5 text-primary" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Derniers ajouts à la base</h2>
          </div>

          {loadingFeed ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {[1,2,3,4,5,6].map(i => (
                <div key={i} className="border border-border bg-card overflow-hidden">
                  <div className="aspect-[3/4] bg-secondary animate-pulse" />
                  <div className="p-2 space-y-1">
                    <div className="h-2.5 bg-secondary animate-pulse rounded w-3/4" />
                    <div className="h-2 bg-secondary animate-pulse rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : recentApproved.length === 0 ? (
            <div className="text-center py-10 border border-dashed border-border">
              <Package className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun ajout récent</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
              {recentApproved.slice(0, 18).map(sub => (
                <FeedCard key={sub.submission_id} sub={sub} />
              ))}
            </div>
          )}
        </section>

        {/* ===== SECTION 2 : TOP CONTRIBUTEURS ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <Trophy className="w-5 h-5 text-yellow-500" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Meilleurs contributeurs</h2>
          </div>

          {loadingFeed ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {[1,2,3,4,5,6].map(i => (
                <div key={i} className="border border-border bg-card p-4 flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-full bg-secondary animate-pulse" />
                  <div className="space-y-2 w-full">
                    <div className="h-3 bg-secondary animate-pulse rounded w-2/3 mx-auto" />
                    <div className="h-2 bg-secondary animate-pulse rounded w-1/3 mx-auto" />
                  </div>
                </div>
              ))}
            </div>
          ) : topContributors.length === 0 ? (
            <div className="text-center py-10 border border-dashed border-border">
              <Users className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun contributeur pour le moment</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {topContributors.map((contributor, index) => (
                <ContributorCard key={contributor.username || contributor.name || index} contributor={contributor} rank={index + 1} />
              ))}
            </div>
          )}
        </section>

        {/* ===== SECTION 3 : COMMUNITY QUEUE ===== */}
        <section>
          <div className="flex items-center gap-3 mb-5">
            <ThumbsUp className="w-5 h-5 text-primary" />
            <h2 className="text-sm uppercase tracking-widest" style={{ fontFamily: 'Barlow Condensed' }}>Community Queue — Votes</h2>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="bg-card border border-border rounded-none mb-6">
              <TabsTrigger value="pending" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Clock className="w-3 h-3 mr-1" /> Pending
              </TabsTrigger>
              <TabsTrigger value="approved" className="rounded-none data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                <Check className="w-3 h-3 mr-1" /> Approved
              </TabsTrigger>
              <TabsTrigger value="rejected" className="rounded-none data-[state=active]:bg-destructive data-[state=active]:text-destructive-foreground">
                <X className="w-3 h-3 mr-1" /> Rejected
              </TabsTrigger>
            </TabsList>

            <TabsContent value={activeTab}>
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                <Shirt className="w-4 h-4" /> Jersey Submissions
              </h3>
              {loading ? (
                <div className="space-y-3 mb-8">{[1,2,3].map(i => <div key={i} className="h-20 bg-card animate-pulse border border-border" />)}</div>
              ) : jerseyAndCreateSubs.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border mb-8">
                  <FileCheck className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No {activeTab} submissions</p>
                </div>
              ) : (
                <div className="space-y-3 mb-8">
                  {jerseyAndCreateSubs.map(sub => (
                    <VoteRow
                      key={sub.submission_id}
                      item={sub}
                      onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                      onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                      hasVoted={hasVoted(sub)}
                      expanded={expandedSubmission === sub.submission_id}
                      onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                      title={getSubmissionTitle(sub, existingKits)}
                      subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                        {sub.data?.mode === 'removal' && <Badge variant="outline" className="rounded-none text-[10px] border-destructive/50 text-destructive">Removal</Badge>}
                        <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                      </>}
                    >
                      <SubmissionDetail sub={sub} existingKits={existingKits} />
                    </VoteRow>
                  ))}
                </div>
              )}

              {standaloneEntitySubs.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <Package className="w-4 h-4" /> Database References
                  </h3>
                  <div className="space-y-3">
                    {standaloneEntitySubs.map(sub => (
                      <VoteRow
                        key={sub.submission_id}
                        item={sub}
                        onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                        onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                        hasVoted={hasVoted(sub)}
                        expanded={expandedSubmission === sub.submission_id}
                        onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                        title={sub.submission_type === 'player' ? (sub.data?.full_name || '?') : (sub.data?.name || '?')}
                        subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                        badges={<>
                          <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                          <Badge variant="outline" className="rounded-none text-[10px] border-primary/30 text-primary">New</Badge>
                          <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                        </>}
                      >
                        <SubmissionDetail sub={sub} existingKits={existingKits} />
                      </VoteRow>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'pending' && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <AlertTriangle className="w-4 h-4" /> Références en attente de validation
                  </h3>
                  {loadingPending ? (
                    <div className="h-16 bg-card animate-pulse border border-border" />
                  ) : Object.values(pendingEntities).every(arr => arr.length === 0) ? (
                    <div className="text-center py-8 border border-dashed border-border">
                      <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucune référence en attente</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {[{ key: 'team', label: 'Équipes' }, { key: 'league', label: 'Compétitions' }, { key: 'brand', label: 'Marques' }, { key: 'player', label: 'Joueurs' }, { key: 'sponsor', label: 'Sponsors' }].map(({ key, label }) => {
                        const list = pendingEntities[key] || [];
                        if (!list.length) return null;
                        return (
                          <div key={key} className="border border-border bg-card p-4">
                            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{label} ({list.length})</p>
                            <div className="space-y-2">
                              {list.map(item => (
                                <div key={item._id} className="flex items-center justify-between px-3 py-2 bg-secondary/30 border border-border/50">
                                  <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getDisplayName(item)}</span>
                                  <Badge variant="outline" className="rounded-none text-[10px] border-accent/40 text-accent">for review</Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'approved' && (
                <div className="mb-8">
                  <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                    <CheckCircle2 className="w-4 h-4" /> Références validées
                  </h3>
                  {Object.values(approvedEntities).every(arr => arr.length === 0) ? (
                    <div className="text-center py-8 border border-dashed border-border">
                      <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No approved references yet</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {[{ key: 'team', label: 'Équipes' }, { key: 'league', label: 'Compétitions' }, { key: 'brand', label: 'Marques' }, { key: 'player', label: 'Joueurs' }, { key: 'sponsor', label: 'Sponsors' }].map(({ key, label }) => {
                        const list = approvedEntities[key] || [];
                        if (!list.length) return null;
                        return (
                          <div key={key} className="border border-border bg-card p-4">
                            <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>{label} ({list.length})</p>
                            <div className="space-y-2">
                              {list.map(item => (
                                <div key={item._id} className="flex items-center justify-between px-3 py-2 bg-secondary/30 border border-border/50">
                                  <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getDisplayName(item)}</span>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline" className="rounded-none text-[10px] border-primary/40 text-primary">approved</Badge>
                                    <Link to={`/${key}/${item.slug || item._id}`} className="text-xs text-primary hover:underline">View</Link>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                <AlertTriangle className="w-4 h-4" /> Correction Reports
              </h3>
              {reports.length === 0 && entityEditSubs.length === 0 ? (
                <div className="text-center py-10 border border-dashed border-border">
                  <AlertTriangle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No {activeTab} reports</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {reports.map(rep => (
                    <VoteRow
                      key={rep.report_id}
                      item={rep}
                      onVoteUp={() => handleVoteReport(rep.report_id, 'up')}
                      onVoteDown={() => handleVoteReport(rep.report_id, 'down')}
                      hasVoted={hasVoted(rep)}
                      expanded={expandedReport === rep.report_id}
                      onToggle={() => setExpandedReport(expandedReport === rep.report_id ? null : rep.report_id)}
                      title={rep.notes || 'Correction submitted'}
                      subtitle={<>by <UserLink name={rep.reporter_name} username={rep.reporter_username} /> — {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">
                          {rep.report_type === 'removal' ? 'Removal Request' : rep.target_type === 'master_kit' ? 'Kit Correction' : 'Version Correction'}
                        </Badge>
                        <Badge className={`rounded-none text-[10px] ${rep.status === 'approved' ? 'bg-primary/20 text-primary' : rep.status === 'rejected' ? 'bg-destructive/20 text-destructive' : 'bg-accent/20 text-accent'}`}>{rep.status}</Badge>
                      </>}
                    >
                      <ReportDetail rep={rep} />
                    </VoteRow>
                  ))}
                  {entityEditSubs.map(sub => (
                    <VoteRow
                      key={sub.submission_id}
                      item={sub}
                      onVoteUp={() => handleVoteSubmission(sub.submission_id, true)}
                      onVoteDown={() => handleVoteSubmission(sub.submission_id, false)}
                      hasVoted={hasVoted(sub)}
                      expanded={expandedSubmission === sub.submission_id}
                      onToggle={() => setExpandedSubmission(expandedSubmission === sub.submission_id ? null : sub.submission_id)}
                      title={sub.submission_type === 'player' ? (sub.data?.full_name || '?') : (sub.data?.name || '?')}
                      subtitle={<>by <UserLink name={sub.submitter_name} username={sub.submitter_username} /> — {sub.created_at ? new Date(sub.created_at).toLocaleDateString() : ''}</>}
                      badges={<>
                        <Badge variant="outline" className="rounded-none text-[10px]">{TYPE_LABELS[sub.submission_type] || sub.submission_type}</Badge>
                        <Badge variant="outline" className="rounded-none text-[10px] border-orange-500/40 text-orange-500">
                          {sub.data?.mode === 'removal' ? 'Removal' : 'Edit'}
                        </Badge>
                        <Badge className={`rounded-none text-[10px] ${sub.status === 'approved' ? 'bg-primary/20 text-primary' : sub.status === 'pending' ? 'bg-accent/20 text-accent' : 'bg-destructive/20 text-destructive'}`}>{sub.status}</Badge>
                      </>}
                    >
                      <SubmissionDetail sub={sub} existingKits={existingKits} />
                    </VoteRow>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </section>
      </div>
    </div>
  );
}
