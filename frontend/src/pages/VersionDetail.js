// src/pages/VersionDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVersion, getVersionEstimates, addToCollection, createReport, proxyImageUrl, addToWishlist, checkWishlist, removeFromWishlist, createReview } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import {
  Star, Shirt, ChevronRight, ChevronLeft, AlertTriangle,
  Check, Trash2, User, Plus, Loader2, Heart,
} from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';

const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];
const MODELS       = ['Authentic', 'Replica', 'Other'];

// ── Slider ────────────────────────────────────────────────────────────────────
function KitSlider({ photos }) {
  const [current, setCurrent] = useState(0);

  if (!photos.length) return (
    <div className="aspect-[3/4] border border-border bg-card flex items-center justify-center">
      <Shirt className="w-16 h-16 text-muted-foreground" />
    </div>
  );

  const prev = () => setCurrent(i => (i - 1 + photos.length) % photos.length);
  const next = () => setCurrent(i => (i + 1) % photos.length);

  return (
    <div className="space-y-3">
      <div className="relative aspect-[3/4] border border-border bg-card overflow-hidden group">
        <img
          src={proxyImageUrl(photos[current])}
          alt={`Photo ${current + 1}`}
          className="w-full h-full object-cover transition-opacity duration-300"
        />
        {photos.length > 1 && (
          <>
            <button onClick={prev}
              className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-background/80 border border-border flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-background">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button onClick={next}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-background/80 border border-border flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-background">
              <ChevronRight className="w-4 h-4" />
            </button>
            <div className="absolute bottom-2 right-2 bg-background/80 border border-border px-2 py-0.5">
              <span className="text-[10px] font-mono text-muted-foreground">{current + 1}/{photos.length}</span>
            </div>
          </>
        )}
      </div>
      {photos.length > 1 && (
        <div className="flex gap-2">
          {photos.map((photo, i) => (
            <button key={i} onClick={() => setCurrent(i)}
              className={`w-16 h-20 border overflow-hidden shrink-0 transition-colors ${
                i === current ? 'border-primary' : 'border-border hover:border-primary/50'
              }`}>
              <img src={proxyImageUrl(photo)} alt={i === 0 ? 'Front' : 'Back'} className="w-full h-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function VersionDetail() {
  const { versionId } = useParams();
  const { user }      = useAuth();

  const [version,       setVersion]       = useState(null);
  const [wornBy,        setWornBy]        = useState([]);
  const [estimates,     setEstimates]     = useState(null);
  const [reviews,       setReviews]       = useState([]);
  const [loading,       setLoading]       = useState(true);
  const [addStatus,     setAddStatus]     = useState('idle');
  const [wishStatus,    setWishStatus]    = useState('idle'); // 'idle' | 'loading' | 'done'
  const [wishlistId,    setWishlistId]    = useState(null);
  const [showReport,    setShowReport]    = useState(false);
  const [showRemoval,   setShowRemoval]   = useState(false);
  const [removalNotes,  setRemovalNotes]  = useState('');
  const [reviewRating,  setReviewRating]  = useState(0);
  const [reviewHover,   setReviewHover]   = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submitting,    setSubmitting]    = useState(false);

  // ── Report state — uniquement les champs d'une VERSION
  const [reportCorrections, setReportCorrections] = useState({
    competition: '',
    model:       '',
    sku_code:    '',
    ean_code:    '',
    front_photo: '',
    back_photo:  '',
  });
  const [reportNotes, setReportNotes] = useState('');

  const setField = (key) => (val) => setReportCorrections(p => ({ ...p, [key]: val }));

  const fetchReviews = useCallback(async () => {
    try {
      const res  = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reviews?version_id=${versionId}`, { credentials: 'include' });
      const data = res.ok ? await res.json() : [];
      setReviews(Array.isArray(data) ? data : []);
    } catch { setReviews([]); }
  }, [versionId]);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getVersion(versionId),
      fetch(`/api/versions/${versionId}/worn-by`).then(r => r.ok ? r.json() : []),
      getVersionEstimates(versionId).catch(() => null),
    ]).then(async ([versionRes, wornByData, estimatesRes]) => {
      const v = versionRes.data;
      setVersion(v);
      setWornBy(Array.isArray(wornByData) ? wornByData : []);
      setEstimates(estimatesRes?.data || null);
      // Pré-remplir le form de report avec les valeurs actuelles de la version
      setReportCorrections({
        competition: v.competition || '',
        model:       v.model       || '',
        sku_code:    v.sku_code    || '',
        ean_code:    v.ean_code    || '',
        front_photo: v.front_photo || '',
        back_photo:  v.back_photo  || '',
      });
      await fetchReviews();
      // Charger statut wishlist
      try {
        const wRes = await checkWishlist(v.version_id);
        if (wRes.data?.in_wishlist) {
          setWishStatus('done');
          setWishlistId(wRes.data.wishlist_id);
        }
      } catch {}
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [versionId, fetchReviews]);

  const handleAdd = async () => {
    if (addStatus !== 'idle') return;
    setAddStatus('loading');
    try {
      await addToCollection({ version_id: versionId });
      setAddStatus('done');
      toast.success('Added to your collection 🎽');
    } catch (err) {
      if (err?.response?.status === 400) {
        setAddStatus('done');
        toast.info('Already in your collection');
      } else {
        setAddStatus('error');
        setTimeout(() => setAddStatus('idle'), 2000);
      }
    }
  };

  const handleSubmitReport = async () => {
    try {
      await createReport({
        target_type: 'version',
        target_id:   versionId,
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
        target_type: 'version',
        target_id:   versionId,
        corrections: {},
        notes:       removalNotes,
        report_type: 'removal',
      });
      toast.success('Removal request submitted for community vote');
      setShowRemoval(false);
      setRemovalNotes('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit removal request');
    }
  };

  const handleSubmitReview = async () => {
    if (!reviewRating) return toast.error('Please select a rating');
    setSubmitting(true);
    try {
      await createReview({ version_id: versionId, rating: reviewRating, comment: reviewComment });
      toast.success('Review submitted!');
      setReviewRating(0);
      setReviewComment('');
      await fetchReviews();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWishlist = async () => {
    if (wishStatus === 'loading') return;
    setWishStatus('loading');
    try {
      if (wishStatus === 'done' && wishlistId) {
        await removeFromWishlist(wishlistId);
        setWishStatus('idle');
        setWishlistId(null);
        toast.success('Removed from wishlist');
      } else {
        const res = await addToWishlist({ version_id: versionId });
        setWishStatus('done');
        setWishlistId(res.data?.wishlist_id || null);
        toast.success('Added to wishlist ❤️');
      }
    } catch (err) {
      if (err?.response?.status === 400) {
        setWishStatus('done');
        toast.info('Already in your wishlist');
      } else {
        setWishStatus('idle');
        toast.error('Failed to update wishlist');
      }
    }
  };

  if (loading) return (
    <div className="animate-pulse px-4 lg:px-8 py-8 max-w-7xl mx-auto">
      <div className="h-8 w-32 bg-card mb-8" />
      <div className="grid md:grid-cols-2 gap-8">
        <div className="aspect-[3/4] bg-card" />
        <div className="space-y-4"><div className="h-10 w-3/4 bg-card" /><div className="h-6 w-1/2 bg-card" /></div>
      </div>
    </div>
  );

  if (!version) return (
    <div className="px-4 lg:px-8 py-20 text-center">
      <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
      <h2 className="text-2xl tracking-tight mb-2">VERSION NOT FOUND</h2>
      <Link to="/browse"><Button variant="outline" className="rounded-none mt-4">Back to Browse</Button></Link>
    </div>
  );

  const kit    = version.master_kit || {};
  const photos = [version.front_photo, version.back_photo].filter(Boolean);

  return (
    <div className="animate-fade-in-up">

      {/* Breadcrumb */}
      <div className="border-b border-border px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-muted-foreground">
          <Link to="/browse" className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>Browse</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to={`/kit/${kit.kit_id}`} className="hover:text-foreground truncate" style={{ transition: 'color 0.2s ease' }}>
            {kit.club} {kit.season}
          </Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground truncate">{version.model} · {version.competition}</span>
        </div>
      </div>

      {/* Hero */}
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
          <div className="grid md:grid-cols-[1fr_1.2fr] gap-8 lg:gap-16">

            <div className="relative"><KitSlider photos={photos} /></div>

            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  {kit.kit_type && <Badge variant="outline" className="rounded-none text-xs">{kit.kit_type}</Badge>}
                  {version.model && <Badge variant="outline" className="rounded-none text-xs">{version.model}</Badge>}
                </div>
                <h1 className="text-4xl sm:text-5xl tracking-tighter leading-none mb-2">
                  <Link to={`/teams/${kit.team_slug ?? kit.club}`} className="hover:text-primary transition-colors">
                    {kit.club}
                  </Link>
                </h1>
                <p className="text-lg text-muted-foreground" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                  {kit.season} Season
                </p>
              </div>

              {version.avg_rating > 0 && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    {[1,2,3,4,5].map(s => (
                      <Star key={s} className={`w-4 h-4 ${s <= Math.round(version.avg_rating) ? 'text-accent fill-accent' : 'text-muted'}`} />
                    ))}
                  </div>
                  <span className="text-sm font-mono text-accent">{version.avg_rating}</span>
                  <span className="text-xs text-muted-foreground">({version.review_count} reviews)</span>
                </div>
              )}

              <Separator className="bg-border" />

              {/* Data Grid */}
              <div className="grid grid-cols-2 gap-6">
                {[
                  { label: 'Brand',          value: kit.brand },
                  { label: 'Type',           value: kit.kit_type },
                  { label: 'Competition',    value: version.competition },
                  { label: 'Model',          value: version.model },
                  { label: 'SKU',            value: version.sku_code },
                  { label: 'EAN',            value: version.ean_code },
                  { label: 'In collections', value: version.collection_count > 0 ? `${version.collection_count} collectors` : null },
                ].filter(f => f.value).map(({ label, value }) => (
                  <div key={label}>
                    <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>{label}</div>
                    <span className="text-sm font-mono">{value}</span>
                  </div>
                ))}
              </div>

              {/* Estimated Value */}
              {estimates && (
                <div className="space-y-3">
                  <h5 className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Estimated Value</h5>
                  <div className="grid grid-cols-3 gap-3">
                    {[{ label: 'Low', value: estimates.low }, { label: 'Average', value: estimates.average }, { label: 'High', value: estimates.high }].map(({ label, value }) => (
                      <div key={label} className="border border-border bg-card p-3 text-center">
                        <p className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>{label}</p>
                        <p className="font-semibold font-mono text-primary">{value != null ? `€${value}` : '—'}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Buttons */}
              <div className="flex flex-wrap gap-2">
                {user && (
                  <Button onClick={handleAdd} size="sm"
                    className={`rounded-none ${addStatus === 'done' ? 'bg-green-500 hover:bg-green-500' : ''}`}>
                    {addStatus === 'loading' && <Loader2 className="w-4 h-4 mr-1 animate-spin" />}
                    {addStatus === 'done'    && <Check   className="w-4 h-4 mr-1" />}
                    {addStatus === 'idle'    && <Plus    className="w-4 h-4 mr-1" />}
                    {addStatus === 'done' ? 'In collection' : 'Add to collection'}
                  </Button>
                )}
                {user && (
                  <Button
                    variant="outline" size="sm"
                    onClick={handleWishlist}
                    className={`rounded-none border-border transition-colors ${wishStatus === 'done' ? 'border-red-400/60 text-red-400 hover:bg-red-400/10' : 'hover:border-red-400/40 hover:text-red-400'}`}
                  >
                    {wishStatus === 'loading'
                      ? <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                      : <Heart className={`w-4 h-4 mr-1 transition-all ${wishStatus === 'done' ? 'fill-red-400 text-red-400' : ''}`} />
                    }
                    {wishStatus === 'done' ? 'In wishlist' : 'Add to wishlist'}
                  </Button>
                )}
                {user && (
                  <>
                    <Button variant="outline" size="sm" onClick={() => setShowReport(!showReport)}
                      className="rounded-none border-border">
                      <AlertTriangle className="w-4 h-4 mr-1" /> Report Error
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setShowRemoval(!showRemoval)}
                      className="rounded-none border-destructive/50 text-destructive hover:bg-destructive/10">
                      <Trash2 className="w-4 h-4 mr-1" /> Request Removal
                    </Button>
                  </>
                )}
              </div>

              {/* ── Report Form (Version uniquement) ── */}
              {showReport && user && (
                <div className="border border-destructive/30 p-4 space-y-4">
                  <h4 className="text-sm uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>REPORT ERROR</h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">

                    {/* Competition — Select */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Competition *</Label>
                      <Select value={reportCorrections.competition} onValueChange={setField('competition')}>
                        <SelectTrigger className="bg-card border-border rounded-none text-sm" data-testid="report-competition">
                          <SelectValue placeholder="Select competition" />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Model — Select */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Model *</Label>
                      <Select value={reportCorrections.model} onValueChange={setField('model')}>
                        <SelectTrigger className="bg-card border-border rounded-none text-sm" data-testid="report-model">
                          <SelectValue placeholder="Select model" />
                        </SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* SKU Code */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                      <Input
                        value={reportCorrections.sku_code}
                        onChange={e => setField('sku_code')(e.target.value)}
                        placeholder="Optional"
                        className="bg-card border-border rounded-none text-sm font-mono"
                        data-testid="report-sku"
                      />
                    </div>

                    {/* EAN Code */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>EAN Code</Label>
                      <Input
                        value={reportCorrections.ean_code}
                        onChange={e => setField('ean_code')(e.target.value)}
                        placeholder="Optional"
                        className="bg-card border-border rounded-none text-sm font-mono"
                        data-testid="report-ean"
                      />
                    </div>

                    {/* Front Photo */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                      <ImageUpload
                        value={reportCorrections.front_photo}
                        onChange={setField('front_photo')}
                        testId="report-ver-front-photo"
                      />
                    </div>

                    {/* Back Photo */}
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Back Photo</Label>
                      <ImageUpload
                        value={reportCorrections.back_photo}
                        onChange={setField('back_photo')}
                        testId="report-ver-back-photo"
                      />
                    </div>
                  </div>

                  {/* Notes */}
                  <div className="space-y-1">
                    <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Notes</Label>
                    <Textarea
                      value={reportNotes}
                      onChange={e => setReportNotes(e.target.value)}
                      placeholder="Describe the error..."
                      className="bg-card border-border rounded-none min-h-[80px] text-sm"
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleSubmitReport}
                      className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      <Check className="w-3 h-3 mr-1" /> Submit Report
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowReport(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}

              {/* ── Removal Form ── */}
              {showRemoval && user && (
                <div className="border border-destructive/50 p-4 space-y-3">
                  <h4 className="text-sm uppercase tracking-wider text-destructive" style={{ fontFamily: 'Barlow Condensed' }}>REQUEST REMOVAL</h4>
                  <div className="space-y-1">
                    <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Reason</Label>
                    <Textarea
                      value={removalNotes}
                      onChange={e => setRemovalNotes(e.target.value)}
                      placeholder="Explain why this version should be removed..."
                      className="bg-card border-border rounded-none min-h-[80px] text-sm"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleRequestRemoval} disabled={!removalNotes.trim()}
                      className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      <Trash2 className="w-3 h-3 mr-1" /> Submit Removal Request
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setShowRemoval(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Players who wore this kit ── */}
      {wornBy.length > 0 && (
        <div className="border-t border-border">
          <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
            <h2 className="text-xl tracking-tight mb-6">
              PLAYERS WHO WORE THIS KIT{' '}
              <span className="font-mono text-sm text-muted-foreground ml-2">{wornBy.length}</span>
            </h2>
            <div className="flex flex-wrap gap-4">
              {wornBy.map(player => (
                <Link key={player.player_id} to={`/players/${player.slug ?? player.player_id}`}
                  className="flex-shrink-0 w-20 hover:scale-105 transition-transform">
                  <div className="w-20 h-24 bg-secondary overflow-hidden border border-border">
                    {player.photo_url ? (
                      <img src={proxyImageUrl(player.photo_url)} alt={player.full_name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <User className="w-8 h-8 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                  <p className="text-[11px] text-center mt-1 font-mono truncate leading-tight">{player.full_name}</p>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Reviews ── */}
      <div className="border-t border-border">
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
          <h2 className="text-xl tracking-tight mb-6">
            REVIEWS{' '}
            <span className="font-mono text-sm text-muted-foreground ml-2">{reviews.length}</span>
          </h2>

          {user ? (
            <div className="border border-border bg-card p-5 mb-6">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-4" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Leave a Review</h3>
              <div className="flex flex-col sm:flex-row gap-4 items-start">
                <div className="flex items-center gap-1 shrink-0 pt-1">
                  {[1,2,3,4,5].map(s => (
                    <button key={s}
                      onClick={() => setReviewRating(s)}
                      onMouseEnter={() => setReviewHover(s)}
                      onMouseLeave={() => setReviewHover(0)}
                      className="transition-transform hover:scale-110">
                      <Star className={`w-6 h-6 transition-colors ${s <= (reviewHover || reviewRating) ? 'fill-accent text-accent' : 'text-muted-foreground'}`} />
                    </button>
                  ))}
                  {reviewRating > 0 && <span className="text-xs font-mono text-accent ml-1">{reviewRating}/5</span>}
                </div>
                <Textarea
                  value={reviewComment}
                  onChange={e => setReviewComment(e.target.value)}
                  placeholder="Authentic? Replica? Match worn? Share your thoughts..."
                  className="bg-background border-border rounded-none min-h-[60px] text-sm resize-none flex-1"
                  style={{ fontFamily: 'DM Sans', textTransform: 'none' }}
                />
                <Button size="sm" onClick={handleSubmitReview} disabled={!reviewRating || submitting} className="rounded-none shrink-0 self-end">
                  {submitting
                    ? <><Loader2 className="w-3 h-3 mr-1 animate-spin" /> Submitting...</>
                    : <><Check   className="w-3 h-3 mr-1" /> Submit</>
                  }
                </Button>
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-border p-4 flex items-center gap-3 mb-6">
              <Star className="w-5 h-5 text-muted-foreground shrink-0" />
              <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Sign in to leave a review</p>
            </div>
          )}

          <div className="space-y-3">
            {reviews.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-border">
                <Star className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>No reviews yet — be the first!</p>
              </div>
            ) : reviews.map(review => (
              <div key={review.review_id} className="border border-border bg-card p-4">
                <div className="flex items-center gap-3 mb-2">
                  {review.user_picture ? (
                    <img src={proxyImageUrl(review.user_picture)} alt="" className="w-8 h-8 rounded-full object-cover shrink-0" />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                      <User className="w-4 h-4 text-muted-foreground" />
                    </div>
                  )}
                  <span className="font-medium text-sm">{review.user_name || 'Anonymous'}</span>
                  <div className="flex items-center gap-0.5 ml-auto">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className={`w-3.5 h-3.5 ${i < review.rating ? 'fill-accent text-accent' : 'text-muted-foreground'}`} />
                    ))}
                    <span className="text-xs font-mono text-accent ml-1">{review.rating}/5</span>
                  </div>
                </div>
                {review.comment && (
                  <p className="text-sm text-muted-foreground pl-11" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{review.comment}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

    </div>
  );
}
