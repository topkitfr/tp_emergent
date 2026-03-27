// src/pages/KitDetail.js
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getMasterKit, createReport, proxyImageUrl, getKitPlayers } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Star, Shirt, Tag, Package, ChevronRight,
  AlertTriangle, Check, Trash2, User, Plus,
} from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';
import EntityAutocomplete from '@/components/EntityAutocomplete';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const GENDERS   = ['Man', 'Woman', 'Kid'];

export default function KitDetail() {
  const { kitId } = useParams();
  const { user }  = useAuth();
  const navigate  = useNavigate();

  const [kit,               setKit]               = useState(null);
  const [loading,           setLoading]           = useState(true);
  const [players,           setPlayers]           = useState([]);
  const [showReport,        setShowReport]        = useState(false);
  const [reportCorrections, setReportCorrections] = useState({});
  const [reportNotes,       setReportNotes]       = useState('');
  const [showRemovalForm,   setShowRemovalForm]   = useState(false);
  const [removalNotes,      setRemovalNotes]      = useState('');

  useEffect(() => {
    setLoading(true);
    getMasterKit(kitId)
      .then(async r => {
        setKit(r.data);
        setReportCorrections({
          club:        r.data.club        || '',
          season:      r.data.season      || '',
          kit_type:    r.data.kit_type    || '',
          brand:       r.data.brand       || '',
          design:      r.data.design      || '',
          sponsor:     r.data.sponsor     || '',
          league:      r.data.league      || '',
          gender:      r.data.gender      || '',
          front_photo: r.data.front_photo || '',
        });
        try {
          const res = await getKitPlayers(r.data.kit_id);
          setPlayers(res.data || []);
        } catch { setPlayers([]); }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [kitId]);

  const handleSubmitReport = async () => {
    try {
      await createReport({
        target_type: 'master_kit',
        target_id:   kitId,
        corrections: reportCorrections,
        notes:       reportNotes,
        report_type: 'error',
      });
      toast.success('Report submitted for community review');
      setShowReport(false);
      setReportNotes('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit report');
    }
  };

  const handleRequestRemoval = async () => {
    try {
      await createReport({
        target_type: 'master_kit',
        target_id:   kitId,
        corrections: {},
        notes:       removalNotes,
        report_type: 'removal',
      });
      toast.success('Removal request submitted for community vote');
      setShowRemovalForm(false);
      setRemovalNotes('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit removal request');
    }
  };

  const set = (key) => (val) => setReportCorrections(p => ({ ...p, [key]: val }));

  if (loading) return (
    <div className="animate-pulse px-4 lg:px-8 py-8 max-w-7xl mx-auto">
      <div className="h-8 w-32 bg-card mb-8" />
      <div className="grid md:grid-cols-2 gap-8">
        <div className="aspect-[3/4] bg-card" />
        <div className="space-y-4">
          <div className="h-10 w-3/4 bg-card" />
          <div className="h-6 w-1/2 bg-card" />
        </div>
      </div>
    </div>
  );

  if (!kit) return (
    <div className="px-4 lg:px-8 py-20 text-center">
      <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
      <h2 className="text-2xl tracking-tight mb-2">KIT NOT FOUND</h2>
      <Link to="/browse">
        <Button variant="outline" className="rounded-none mt-4">Back to Browse</Button>
      </Link>
    </div>
  );

  const teamPath   = kit.team_id   ? `/teams/${kit.team_id}`   : kit.club_slug ? `/teams/${kit.club_slug}`   : null;
  const brandPath  = kit.brand_id  ? `/brands/${kit.brand_id}` : kit.brand_slug ? `/brands/${kit.brand_slug}` : null;
  const leaguePath = kit.league_id ? `/leagues/${kit.league_id}` : kit.league_slug ? `/leagues/${kit.league_slug}` : null;
  const sponsorPath = kit.sponsor_id ? `/database/sponsors/${kit.sponsor_id}` : null;

  return (
    <div className="animate-fade-in-up">

      {/* Breadcrumb */}
      <div className="border-b border-border px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-muted-foreground">
          <Link to="/browse" className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>Browse</Link>
          <ChevronRight className="w-3 h-3" />
          {teamPath ? (
            <Link to={teamPath} className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>{kit.club}</Link>
          ) : (
            <span>{kit.club}</span>
          )}
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground truncate">{kit.season}</span>
        </div>
      </div>

      {/* Hero */}
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
          <div className="grid md:grid-cols-[1fr_1.2fr] gap-8 lg:gap-16">

            {/* Left — Image */}
            <div className="relative">
              <div className="aspect-[3/4] border border-border bg-card overflow-hidden" data-testid="kit-main-image">
                <img
                  src={proxyImageUrl(kit.front_photo)}
                  alt={`${kit.club} ${kit.season}`}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Right — Info */}
            <div className="space-y-6">

              <div>
                <Badge variant="outline" className="rounded-none text-xs mb-3">{kit.kit_type}</Badge>
                <h1 className="text-4xl sm:text-5xl tracking-tighter leading-none mb-2" data-testid="kit-title">
                  {teamPath ? (
                    <Link to={teamPath} className="hover:text-primary transition-colors">{kit.club}</Link>
                  ) : (
                    <span>{kit.club}</span>
                  )}
                </h1>
                <p className="text-lg text-muted-foreground"
                  style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                  {kit.season} Season
                </p>
                {(kit.review_count ?? 0) > 0 ? (
                  <div className="flex items-center gap-2 mt-2">
                    <div className="flex items-center gap-0.5">
                      {[1,2,3,4,5].map(s => (
                        <Star key={s} className={`w-4 h-4 ${
                          s <= Math.round(kit.avg_rating ?? 0) ? 'text-accent fill-accent' : 'text-muted-foreground'
                        }`} />
                      ))}
                    </div>
                    <span className="text-sm font-mono text-accent">{(kit.avg_rating ?? 0).toFixed(1)}</span>
                    <span className="text-xs text-muted-foreground">({kit.review_count} review{kit.review_count > 1 ? 's' : ''})</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 mt-2">
                    {[1,2,3,4,5].map(s => <Star key={s} className="w-4 h-4 text-muted-foreground/30" />)}
                    <span className="text-xs text-muted-foreground ml-1">No reviews yet</span>
                  </div>
                )}
              </div>

              <Separator className="bg-border" />

              {/* Data Grid */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Brand</div>
                  <div className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-primary" />
                    {brandPath ? (
                      <Link to={brandPath} className="text-sm hover:text-primary transition-colors">{kit.brand || 'None'}</Link>
                    ) : (
                      <span className="text-sm">{kit.brand || 'None'}</span>
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Type</div>
                  <div className="flex items-center gap-2"><Shirt className="w-4 h-4 text-primary" /><span className="text-sm">{kit.kit_type || 'None'}</span></div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>League</div>
                  {leaguePath ? (
                    <Link to={leaguePath} className="text-sm hover:text-primary transition-colors">{kit.league || 'None'}</Link>
                  ) : (
                    <span className="text-sm">{kit.league || 'None'}</span>
                  )}
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Design</div>
                  <span className="text-sm">{kit.design || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Sponsor</div>
                  {sponsorPath ? (
                    <Link to={sponsorPath} className="text-sm hover:text-primary transition-colors">{kit.sponsor || 'None'}</Link>
                  ) : (
                    <span className="text-sm">{kit.sponsor || 'None'}</span>
                  )}
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Gender</div>
                  <span className="text-sm">{kit.gender || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Versions</div>
                  <div className="flex items-center gap-2"><Package className="w-4 h-4 text-primary" /><span className="text-sm font-mono">{kit.versions?.length || 0}</span></div>
                </div>
              </div>

              {/* Players */}
              {players.length > 0 && (
                <div className="space-y-3">
                  <h5 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Players who wore this kit</h5>
                  <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                    {players.slice(0, 6).map(player => (
                      <Link
                        key={player.player_id ?? player.id}
                        to={`/players/${player.slug ?? player.player_id ?? player.id}`}
                        className="flex-shrink-0 w-16 hover:scale-105 transition-transform"
                      >
                        <div className="w-16 h-20 bg-secondary rounded overflow-hidden">
                          {player.photo_url ?? player.photo ? (
                            <img
                              src={proxyImageUrl(player.photo_url ?? player.photo)}
                              alt={player.full_name ?? player.name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center">
                              <User className="w-6 h-6 text-muted-foreground" />
                            </div>
                          )}
                        </div>
                        <p className="text-[11px] text-center mt-1 font-mono truncate">
                          {player.full_name ?? player.name}
                        </p>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              {user && (
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm" onClick={() => setShowReport(!showReport)}
                    className="rounded-none border-border" data-testid="kit-report-btn">
                    <AlertTriangle className="w-4 h-4 mr-1" /> Report Error
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setShowRemovalForm(!showRemovalForm)}
                    className="rounded-none border-destructive/50 text-destructive hover:bg-destructive/10"
                    data-testid="kit-request-removal-btn">
                    <Trash2 className="w-4 h-4 mr-1" /> Request Removal
                  </Button>
                </div>
              )}

              {/* Report Form */}
              {showReport && user && (
                <div className="border border-destructive/30 p-4 space-y-4" data-testid="kit-report-form">
                  <h4 className="text-sm uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>REPORT ERROR</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Team</Label>
                      <EntityAutocomplete entityType="team" value={reportCorrections.club || ''} onChange={set('club')} onSelect={(item) => set('club')(item.label)} placeholder="e.g., FC Barcelona" className="bg-card border-border rounded-none" testId="report-club" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Season</Label>
                      <Input value={reportCorrections.season || ''} onChange={e => set('season')(e.target.value)} className="bg-card border-border rounded-none h-9 text-sm" data-testid="report-season" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Type</Label>
                      <Select value={reportCorrections.kit_type || ''} onValueChange={set('kit_type')}>
                        <SelectTrigger className="bg-card border-border rounded-none h-9 text-sm" data-testid="report-kit-type"><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Brand</Label>
                      <EntityAutocomplete entityType="brand" value={reportCorrections.brand || ''} onChange={set('brand')} onSelect={(item) => set('brand')(item.label)} placeholder="e.g., Nike" className="bg-card border-border rounded-none" testId="report-brand" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>League</Label>
                      <EntityAutocomplete entityType="league" value={reportCorrections.league || ''} onChange={set('league')} onSelect={(item) => set('league')(item.label)} placeholder="e.g., Ligue 1" className="bg-card border-border rounded-none" testId="report-league" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Gender</Label>
                      <Select value={reportCorrections.gender || ''} onValueChange={set('gender')}>
                        <SelectTrigger className="bg-card border-border rounded-none h-9 text-sm" data-testid="report-gender"><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{GENDERS.map(g => <SelectItem key={g} value={g}>{g}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Design</Label>
                      <Input value={reportCorrections.design || ''} onChange={e => set('design')(e.target.value)} className="bg-card border-border rounded-none h-9 text-sm" data-testid="report-design" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Sponsor</Label>
                      <Input value={reportCorrections.sponsor || ''} onChange={e => set('sponsor')(e.target.value)} className="bg-card border-border rounded-none h-9 text-sm" data-testid="report-sponsor" />
                    </div>
                    <div className="space-y-1 col-span-full">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                      <ImageUpload value={reportCorrections.front_photo || ''} onChange={set('front_photo')} folder="master_kit" testId="kit-report-front-photo" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Notes</Label>
                    <Textarea value={reportNotes} onChange={e => setReportNotes(e.target.value)} placeholder="Describe the error..." className="bg-card border-border rounded-none min-h-[60px] text-sm" data-testid="kit-report-notes" />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSubmitReport} className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="kit-submit-report-btn">
                      <Check className="w-3 h-3 mr-1" /> Submit Report
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowReport(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}

              {/* Removal Form */}
              {showRemovalForm && user && (
                <div className="border border-destructive/50 p-4 space-y-3" data-testid="kit-removal-form">
                  <h4 className="text-sm uppercase tracking-wider text-destructive" style={{ fontFamily: 'Barlow Condensed' }}>REQUEST REMOVAL</h4>
                  <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Request removal of this master kit and all its versions. The community will vote on the request.</p>
                  <div className="space-y-1">
                    <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Reason for removal</Label>
                    <Textarea value={removalNotes} onChange={e => setRemovalNotes(e.target.value)} placeholder="Explain why this kit should be removed..." className="bg-card border-border rounded-none min-h-[80px] text-sm" data-testid="kit-removal-notes" />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleRequestRemoval} disabled={!removalNotes.trim()} className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="kit-submit-removal-btn">
                      <Trash2 className="w-3 h-3 mr-1" /> Submit Removal Request
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowRemovalForm(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Versions */}
      <div className="border-t border-border" id="versions-section">
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
          <h2 className="text-xl tracking-tight mb-6" data-testid="versions-section-title">
            VERSIONS{' '}
            <span className="font-mono text-sm text-muted-foreground ml-2">{kit.versions?.length || 0}</span>
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="versions-grid">
            {(kit.versions || []).map(v => (
              <Link to={`/version/${v.version_id}`} key={v.version_id}>
                <div className="border border-border bg-card p-4 hover:border-primary/30 group"
                  data-testid={`version-card-${v.version_id}`}
                  style={{ transition: 'border-color 0.2s ease' }}>
                  <div className="flex gap-4">
                    <div className="w-20 h-24 bg-secondary overflow-hidden shrink-0">
                      <img src={proxyImageUrl(v.front_photo || kit.front_photo)} alt="" className="w-full h-full object-cover" />
                    </div>
                    <div className="min-w-0 space-y-1.5">
                      <Badge variant="outline" className="rounded-none text-[10px]">{v.model}</Badge>
                      <h4 className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>{v.competition}</h4>
                      {v.sku_code && <p className="font-mono text-[10px] text-muted-foreground">{v.sku_code}</p>}
                      {v.ean_code && <p className="font-mono text-[10px] text-muted-foreground">EAN: {v.ean_code}</p>}
                      {(v.review_count ?? 0) > 0 ? (
                        <div className="flex items-center gap-1">
                          <div className="flex gap-0.5">
                            {[1,2,3,4,5].map(s => (
                              <Star key={s} className={`w-3 h-3 ${s <= Math.round(v.avg_rating ?? 0) ? 'text-accent fill-accent' : 'text-muted-foreground'}`} />
                            ))}
                          </div>
                          <span className="text-xs font-mono text-accent">{(v.avg_rating ?? 0).toFixed(1)}</span>
                          <span className="text-[10px] text-muted-foreground">({v.review_count})</span>
                        </div>
                      ) : (
                        <div className="flex gap-0.5">
                          {[1,2,3,4,5].map(s => <Star key={s} className="w-3 h-3 text-muted-foreground/30" />)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}

            {/* Add Version — redirige vers /contributions avec kit_id pré-rempli */}
            {user && (
              <button
                onClick={() => navigate(`/contributions?kit_id=${kitId}`)}
                className="border border-dashed border-border bg-card p-4 hover:border-primary/50 group flex flex-col items-center justify-center gap-3 min-h-[112px] w-full transition-colors"
                data-testid="add-version-card"
              >
                <div className="w-10 h-10 border border-dashed border-border group-hover:border-primary flex items-center justify-center transition-colors">
                  <Plus className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <span className="text-xs uppercase tracking-wider text-muted-foreground group-hover:text-primary transition-colors" style={{ fontFamily: 'Barlow Condensed' }}>
                  Add Version
                </span>
              </button>
            )}

            {(!kit.versions || kit.versions.length === 0) && !user && (
              <div className="col-span-full text-center py-12 border border-dashed border-border">
                <Package className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No versions added yet</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Ratings agrégées */}
      {(kit.review_count ?? 0) > 0 && (
        <div className="border-t border-border">
          <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
            <h2 className="text-xl tracking-tight mb-6">
              RATINGS{' '}
              <span className="font-mono text-sm text-muted-foreground ml-2">{kit.review_count} review{kit.review_count > 1 ? 's' : ''} across all versions</span>
            </h2>
            <div className="flex items-center gap-6">
              <div className="border border-border bg-card p-6 text-center min-w-[120px]">
                <p className="text-4xl font-mono font-bold text-accent">{(kit.avg_rating ?? 0).toFixed(1)}</p>
                <div className="flex items-center justify-center gap-0.5 mt-2">
                  {[1,2,3,4,5].map(s => (
                    <Star key={s} className={`w-4 h-4 ${s <= Math.round(kit.avg_rating ?? 0) ? 'fill-accent text-accent' : 'text-muted-foreground'}`} />
                  ))}
                </div>
                <p className="text-[10px] text-muted-foreground uppercase tracking-wider mt-2" style={{ fontFamily: 'Barlow Condensed' }}>Global average</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  Ratings are based on individual version reviews.<br />
                  Select a version above to read or leave a review.
                </p>
                <button
                  onClick={() => document.getElementById('versions-section')?.scrollIntoView({ behavior: 'smooth' })}
                  className="text-xs text-primary underline underline-offset-2 hover:text-primary/80 transition-colors"
                  style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  See versions ↑
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
