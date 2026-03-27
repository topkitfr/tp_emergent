// src/pages/VersionDetail.js
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  getVersion, getMasterKit, getVersionEstimates, getVersionWornBy, getReviews,
  createReport, proxyImageUrl, addToWishlist, checkWishlist,
  removeFromWishlist, createReview,
} from '@/lib/api';
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
import AddToCollectionDialog from '@/components/AddToCollectionDialog';

const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];
const MODELS       = ['Authentic', 'Replica', 'Other'];

// ── Slider ──────────────────────────────────────────────────────────────────
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
        <img src={proxyImageUrl(photos[current])} alt={`Photo ${current + 1}`} className="w-full h-full object-cover transition-opacity duration-300" />
        {photos.length > 1 && (
          <>
            <button onClick={prev} className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-background/80 border border-border flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-background">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button onClick={next} className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-background/80 border border-border flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-background">
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

// ── VALUE ESTIMATION bloc ──────────────────────────────────────────────────
function ValueEstimation({ estimates }) {
  if (!estimates) return null;
  const { low, average, high, count } = estimates;
  if (!count || count === 0) return null;

  // Position du curseur average sur la barre (0-100%)
  const range = (high ?? 0) - (low ?? 0);
  const avgPct = range > 0
    ? Math.round(((average ?? low ?? 0) - (low ?? 0)) / range * 100)
    : 50;

  return (
    <div className="border border-border bg-card p-4 space-y-3" data-testid="value-estimation">

      {/* Header */}
      <div className="flex items-center justify-between">
        <h4 className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>
          VALUE ESTIMATION
        </h4>
        <span className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          {count} estimate{count !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Prix moyen en grand */}
      <div className="text-center py-1">
        <span className="text-3xl font-mono font-bold text-foreground">
          {average != null ? `${average}€` : '—'}
        </span>
        <p className="text-[10px] uppercase tracking-wider text-muted-foreground mt-0.5" style={{ fontFamily: 'Barlow Condensed' }}>
          Average
        </p>
      </div>

      {/* Barre de gradient Low → High */}
      <div className="space-y-2">
        <div className="relative h-2 w-full rounded-none" style={{
          background: 'linear-gradient(to right, #ef4444, #eab308, #22c55e)',
        }}>
          {/* Curseur average */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-3 h-4 bg-white border-2 border-background shadow"
            style={{ left: `calc(${avgPct}% - 6px)`, transition: 'left 0.4s ease' }}
          />
        </div>

        {/* Labels Low / High */}
        <div className="flex justify-between">
          <div className="text-left">
            <p className="text-[10px] uppercase tracking-wider text-red-400" style={{ fontFamily: 'Barlow Condensed' }}>Low</p>
            <p className="text-xs font-mono text-red-400">{low != null ? `${low}€` : '—'}</p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-wider text-green-400" style={{ fontFamily: 'Barlow Condensed' }}>High</p>
            <p className="text-xs font-mono text-green-400">{high != null ? `${high}€` : '—'}</p>
          </div>
        </div>
      </div>

    </div>
  );
}

// ── Page ────────────────────────────────────────────────────────────────────
export default function VersionDetail() {
  const { versionId } = useParams();
  const { user }      = useAuth();

  const [version,           setVersion]           = useState(null);
  const [masterKit,         setMasterKit]         = useState(null);
  const [estimates,         setEstimates]         = useState(null);
  const [reviews,           setReviews]           = useState([]);
  const [loading,           setLoading]           = useState(true);
  const [addStatus,         setAddStatus]         = useState('idle');
  const [showAddDialog,     setShowAddDialog]     = useState(false);
  const [wishStatus,        setWishStatus]        = useState('idle');
  const [wishlistId,        setWishlistId]        = useState(null);
  const [showReport,        setShowReport]        = useState(false);
  const [showRemoval,       setShowRemoval]       = useState(false);
  const [removalNotes,      setRemovalNotes]      = useState('');
  const [reviewRating,      setReviewRating]      = useState(0);
  const [reviewHover,       setReviewHover]       = useState(0);
  const [reviewComment,     setReviewComment]     = useState('');
  const [submitting,        setSubmitting]        = useState(false);

  const [reportCorrections, setReportCorrections] = useState({
    competition: '', model: '', sku_code: '', ean_code: '', front_photo: '', back_photo: '',
  });
  const [reportNotes, setReportNotes] = useState('');
  const setField = (key) => (val) => setReportCorrections(p => ({ ...p, [key]: val }));

  const fetchReviews = useCallback(async () => {
    try { const res = await getReviews(versionId); setReviews(Array.isArray(res.data) ? res.data : []); }
    catch { setReviews([]); }
  }, [versionId]);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      getVersion(versionId),
      getVersionEstimates(versionId).catch(() => null),
    ]).then(async ([versionRes, estimatesRes]) => {
      const v = versionRes.data;
      setVersion(v);
      setEstimates(estimatesRes?.data || null);
      setReportCorrections({
        competition: v.competition || '', model: v.model || '',
        sku_code: v.sku_code || '', ean_code: v.ean_code || '',
        front_photo: v.front_photo || '', back_photo: v.back_photo || '',
      });

      const kitId = v.kit_id || v.master_kit?.kit_id;
      if (kitId) {
        getMasterKit(kitId).then(r => setMasterKit(r.data)).catch(() => {});
      } else if (v.master_kit) {
        setMasterKit(v.master_kit);
      }

      await fetchReviews();
      try {
        const wRes = await checkWishlist(v.version_id);
        if (wRes.data?.in_wishlist) { setWishStatus('done'); setWishlistId(wRes.data.wishlist_id); }
      } catch {}
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [versionId, fetchReviews]);

  const handleAdd = () => { if (addStatus !== 'idle') return; setShowAddDialog(true); };
  const handleAddSuccess = () => { setShowAddDialog(false); setAddStatus('done'); toast.success('Added to your collection 🎽'); };

  const handleSubmitReport = async () => {
    try {
      await createReport({ target_type: 'version', target_id: versionId, corrections: reportCorrections, notes: reportNotes, report_type: 'error' });
      toast.success('Report submitted for community review');
      setShowReport(false); setReportNotes('');
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed to submit report'); }
  };

  const handleRequestRemoval = async () => {
    try {
      await createReport({ target_type: 'version', target_id: versionId, corrections: {}, notes: removalNotes, report_type: 'removal' });
      toast.success('Removal request submitted');
      setShowRemoval(false); setRemovalNotes('');
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
  };

  const handleSubmitReview = async () => {
    if (!reviewRating) return toast.error('Please select a rating');
    setSubmitting(true);
    try {
      await createReview({ version_id: versionId, rating: reviewRating, comment: reviewComment });
      toast.success('Review submitted!');
      setReviewRating(0); setReviewComment('');
      await fetchReviews();
    } catch (err) { toast.error(err?.response?.data?.detail || 'Failed to submit review'); }
    finally { setSubmitting(false); }
  };

  const handleWishlist = async () => {
    if (wishStatus === 'loading') return;
    setWishStatus('loading');
    try {
      if (wishStatus === 'done' && wishlistId) {
        await removeFromWishlist(wishlistId);
        setWishStatus('idle'); setWishlistId(null);
        toast.success('Removed from wishlist');
      } else {
        const res = await addToWishlist({ version_id: versionId });
        setWishStatus('done'); setWishlistId(res.data?.wishlist_id || null);
        toast.success('Added to wishlist ❤️');
      }
    } catch (err) {
      if (err?.response?.status === 400) { setWishStatus('done'); toast.info('Already in your wishlist'); }
      else { setWishStatus('idle'); toast.error('Failed to update wishlist'); }
    }
  };

  if (loading) return (
    <div className="animate-pulse px-4 lg:px-8 py-8 max-w-7xl mx-auto">
      <div className="h-8 w-32 bg-card mb-8" />
      <div className="grid md:grid-cols-2 gap-8"><div className="aspect-[3/4] bg-card" /><div className="space-y-4"><div className="h-10 w-3/4 bg-card" /></div></div>
    </div>
  );

  if (!version) return (
    <div className="px-4 lg:px-8 py-20 text-center">
      <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
      <h2 className="text-2xl tracking-tight mb-2">VERSION NOT FOUND</h2>
      <Link to="/browse"><Button variant="outline" className="rounded-none mt-4">Back to Browse</Button></Link>
    </div>
  );

  const kit      = masterKit || version.master_kit || {};
  const photos   = [version.front_photo, version.back_photo].filter(Boolean);
  const teamPath  = kit.team_id  ? `/teams/${kit.team_id}`   : null;
  const brandPath = kit.brand_id ? `/brands/${kit.brand_id}` : null;
  const kitPath   = kit.kit_id   ? `/kit/${kit.kit_id}`      : null;
  const kitType   = kit.kit_type || '';

  return (
    <div className="animate-fade-in-up">

      {showAddDialog && version && (
        <AddToCollectionDialog
          version={version}
          onClose={() => setShowAddDialog(false)}
          onSuccess={handleAddSuccess}
        />
      )}

      {/* Breadcrumb */}
      <div className="border-b border-border px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
          <Link to="/browse" className="hover:text-foreground transition-colors">Browse</Link>
          <ChevronRight className="w-3 h-3" />
          {teamPath
            ? <Link to={teamPath} className="hover:text-foreground transition-colors">{kit.club || '—'}</Link>
            : <span>{kit.club || '—'}</span>}
          <ChevronRight className="w-3 h-3" />
          {kitPath
            ? <Link to={kitPath} className="hover:text-foreground transition-colors">{kit.season || '—'}{kitType ? ` (${kitType})` : ''}</Link>
            : <span>{kit.season || '—'}{kitType ? ` (${kitType})` : ''}</span>}
          <ChevronRight className="w-3 h-3" />
          <span>{version.competition || '—'}</span>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground">{version.model || '—'}</span>
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
                  {kitType && <Badge variant="outline" className="rounded-none text-xs">{kitType}</Badge>}
                  {version.model && <Badge variant="outline" className="rounded-none text-xs">{version.model}</Badge>}
                </div>
                <h1 className="text-4xl sm:text-5xl tracking-tighter leading-none mb-2">
                  {teamPath
                    ? <Link to={teamPath} className="hover:text-primary transition-colors">{kit.club}</Link>
                    : <span>{kit.club}</span>}
                </h1>
                <p className="text-lg text-muted-foreground" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                  {kit.season} Season
                </p>
              </div>

              {version.avg_rating > 0 && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    {[1,2,3,4,5].map(i => (
                      <Star key={i} className={`w-4 h-4 ${
                        i <= Math.round(version.avg_rating) ? 'fill-primary text-primary' : 'text-muted-foreground'
                      }`} />
                    ))}
                  </div>
                  <span className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {version.avg_rating.toFixed(1)} ({version.review_count} review{version.review_count !== 1 ? 's' : ''})
                  </span>
                </div>
              )}

              {/* Info grid */}
              <div className="grid grid-cols-2 gap-4">
                {kit.club && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Team</p>
                    {teamPath
                      ? <Link to={teamPath} className="text-sm hover:text-primary transition-colors">{kit.club}</Link>
                      : <p className="text-sm">{kit.club}</p>}
                  </div>
                )}
                {kit.season && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Season</p>
                    <p className="text-sm">{kit.season}</p>
                  </div>
                )}
                {version.competition && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Competition</p>
                    <p className="text-sm">{version.competition}</p>
                  </div>
                )}
                {kit.brand && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>Brand</p>
                    {brandPath
                      ? <Link to={brandPath} className="text-sm hover:text-primary transition-colors">{kit.brand}</Link>
                      : <p className="text-sm">{kit.brand}</p>}
                  </div>
                )}
                {version.sku_code && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>SKU</p>
                    <p className="text-sm font-mono">{version.sku_code}</p>
                  </div>
                )}
                {version.ean_code && (
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1" style={{ fontFamily: 'Barlow Condensed' }}>EAN</p>
                    <p className="text-sm font-mono">{version.ean_code}</p>
                  </div>
                )}
              </div>

              {/* VALUE ESTIMATION */}
              <ValueEstimation estimates={estimates} />

              {/* Action buttons */}
              <div className="flex flex-wrap gap-3">
                {user && (
                  <>
                    <Button onClick={handleAdd} disabled={addStatus === 'done'} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
                      {addStatus === 'done' ? <Check className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
                      {addStatus === 'done' ? 'In Collection' : 'Add to Collection'}
                    </Button>
                    <Button onClick={handleWishlist} variant="outline" disabled={wishStatus === 'loading'}
                      className={`rounded-none ${
                        wishStatus === 'done'
                          ? 'border-rose-500 text-rose-500 hover:bg-rose-500/10'
                          : 'border-border hover:border-primary hover:text-primary'
                      }`}>
                      {wishStatus === 'loading'
                        ? <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        : <Heart className={`w-4 h-4 mr-2 ${wishStatus === 'done' ? 'fill-rose-500 text-rose-500' : ''}`} />}
                      {wishStatus === 'done' ? 'Wishlisted' : 'Add to Wishlist'}
                    </Button>
                  </>
                )}
              </div>

              {/* Report / Removal */}
              {user && (
                <div className="flex gap-2 pt-2">
                  <button onClick={() => { setShowReport(!showReport); setShowRemoval(false); }} className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    <AlertTriangle className="w-3 h-3" /> Report an error
                  </button>
                  <span className="text-muted-foreground">·</span>
                  <button onClick={() => { setShowRemoval(!showRemoval); setShowReport(false); }} className="text-xs text-muted-foreground hover:text-destructive flex items-center gap-1" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    <Trash2 className="w-3 h-3" /> Request removal
                  </button>
                </div>
              )}

              {/* Report form */}
              {showReport && (
                <div className="border border-border p-4 space-y-4 mt-2">
                  <p className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Report an Error</p>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Competition</Label>
                      <Select value={reportCorrections.competition} onValueChange={setField('competition')}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{COMPETITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Model</Label>
                      <Select value={reportCorrections.model} onValueChange={setField('model')}>
                        <SelectTrigger className="bg-card border-border rounded-none"><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">{MODELS.map(m => <SelectItem key={m} value={m}>{m}</SelectItem>)}</SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>SKU Code</Label>
                      <Input value={reportCorrections.sku_code} onChange={e => setField('sku_code')(e.target.value)} className="bg-card border-border rounded-none font-mono" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EAN Code</Label>
                      <Input value={reportCorrections.ean_code} onChange={e => setField('ean_code')(e.target.value)} className="bg-card border-border rounded-none font-mono" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Front Photo</Label>
                      <ImageUpload value={reportCorrections.front_photo} onChange={setField('front_photo')} folder="version" side="front" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Back Photo</Label>
                      <ImageUpload value={reportCorrections.back_photo} onChange={setField('back_photo')} folder="version" side="back" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-[10px] uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Notes</Label>
                    <Textarea value={reportNotes} onChange={e => setReportNotes(e.target.value)} className="bg-card border-border rounded-none resize-none" rows={3} />
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleSubmitReport} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">Submit Report</Button>
                    <Button variant="outline" onClick={() => setShowReport(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}

              {/* Removal form */}
              {showRemoval && (
                <div className="border border-destructive/30 p-4 space-y-3 mt-2">
                  <p className="text-xs uppercase tracking-wider text-destructive" style={{ fontFamily: 'Barlow Condensed' }}>Request Removal</p>
                  <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>This will create a community vote to remove this version.</p>
                  <Textarea placeholder="Reason for removal..." value={removalNotes} onChange={e => setRemovalNotes(e.target.value)} className="bg-card border-border rounded-none resize-none" rows={3} />
                  <div className="flex gap-2">
                    <Button onClick={handleRequestRemoval} variant="destructive" className="rounded-none">Submit Removal Request</Button>
                    <Button variant="outline" onClick={() => setShowRemoval(false)} className="rounded-none">Cancel</Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Separator />

      {/* Reviews */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-10">
        <h2 className="text-2xl tracking-tighter mb-6">COMMUNITY REVIEWS</h2>
        {user && (
          <div className="border border-border p-6 mb-8 space-y-4">
            <p className="text-xs uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>Leave a Review</p>
            <div className="flex items-center gap-1">
              {[1,2,3,4,5].map(i => (
                <button key={i} onMouseEnter={() => setReviewHover(i)} onMouseLeave={() => setReviewHover(0)} onClick={() => setReviewRating(i)} className="p-1">
                  <Star className={`w-6 h-6 transition-colors ${
                    i <= (reviewHover || reviewRating) ? 'fill-primary text-primary' : 'text-muted-foreground'
                  }`} />
                </button>
              ))}
            </div>
            <Textarea placeholder="Share your thoughts about this jersey..." value={reviewComment} onChange={e => setReviewComment(e.target.value)} className="bg-card border-border rounded-none resize-none" rows={3} />
            <Button onClick={handleSubmitReview} disabled={submitting} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90">
              {submitting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null} Submit Review
            </Button>
          </div>
        )}
        {reviews.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-border">
            <Star className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No reviews yet. Be the first!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map(review => (
              <div key={review.review_id} className="border border-border p-5 space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    {review.user_picture
                      ? <img src={proxyImageUrl(review.user_picture)} alt="" className="w-8 h-8 rounded-full object-cover" />
                      : <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center"><User className="w-4 h-4 text-muted-foreground" /></div>}
                    <div>
                      {review.user_username
                        ? <Link to={`/profile/${review.user_username}`} className="text-sm font-semibold hover:text-primary transition-colors" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{review.user_name || review.user_username}</Link>
                        : <p className="text-sm font-semibold" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{review.user_name || 'Anonymous'}</p>}
                      <p className="text-[10px] text-muted-foreground">{review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-0.5 shrink-0">
                    {[1,2,3,4,5].map(i => <Star key={i} className={`w-3.5 h-3.5 ${i <= review.rating ? 'fill-primary text-primary' : 'text-muted-foreground'}`} />)}
                  </div>
                </div>
                {review.comment && <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{review.comment}</p>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
