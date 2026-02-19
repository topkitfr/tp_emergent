import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVersion, createReview, addToCollection, getVersionEstimates, createReport, checkWishlist, addToWishlist, removeFromWishlist, proxyImageUrl } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { Star, Shirt, ChevronRight, Package, Users, FolderPlus, Check, Hash, TrendingUp, TrendingDown, Minus, AlertTriangle, Heart } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';

const CONDITION_ORIGINS = ['Club Stock', 'Match Prepared', 'Match Worn', 'Training', 'Shop'];
const PHYSICAL_STATES = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_TYPES = ['Name+Number', 'Name', 'Number'];
const FLOCKING_ORIGINS = ['Official', 'Personalized'];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];
const COMPETITIONS = ['National Championship', 'National Cup', 'Continental Cup', 'Intercontinental Cup', 'World Cup'];
const MODELS = ['Authentic', 'Replica', 'Other'];

const fieldLabel = "text-[10px] uppercase tracking-wider text-muted-foreground";
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = "bg-card border-border rounded-none h-9 text-sm";

function parseSeasonYear(season) {
  if (!season) return 0;
  const match = season.match(/(\d{4})/);
  return match ? parseInt(match[1]) : 0;
}

export default function VersionDetail() {
  const { versionId } = useParams();
  const { user } = useAuth();
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [estimates, setEstimates] = useState(null);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewHover, setReviewHover] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [addingToCollection, setAddingToCollection] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showReportForm, setShowReportForm] = useState(false);

  // Wishlist state
  const [inWishlist, setInWishlist] = useState(false);
  const [wishlistId, setWishlistId] = useState(null);
  const [togglingWishlist, setTogglingWishlist] = useState(false);

  // Collection form
  const [flockingType, setFlockingType] = useState('');
  const [flockingOrigin, setFlockingOrigin] = useState('');
  const [flockingDetail, setFlockingDetail] = useState('');
  const [conditionOrigin, setConditionOrigin] = useState('');
  const [physicalState, setPhysicalState] = useState('');
  const [collectionSize, setCollectionSize] = useState('');
  const [purchaseCost, setPurchaseCost] = useState('');
  const [signed, setSigned] = useState(false);
  const [signedBy, setSignedBy] = useState('');
  const [signedProof, setSignedProof] = useState(false);
  const [collectionNotes, setCollectionNotes] = useState('');

  // Report form
  const [reportNotes, setReportNotes] = useState('');
  const [reportCorrections, setReportCorrections] = useState({});
  const [showRemovalForm, setShowRemovalForm] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');

  const fetchVersion = () => {
    Promise.all([
      getVersion(versionId),
      getVersionEstimates(versionId)
    ]).then(([vRes, eRes]) => {
      setVersion(vRes.data);
      setEstimates(eRes.data);
      setLoading(false);
      if (vRes.data) {
        setReportCorrections({
          competition: vRes.data.competition,
          model: vRes.data.model,
          sku_code: vRes.data.sku_code || '',
          ean_code: vRes.data.ean_code || ''
        });
      }
    }).catch(() => setLoading(false));
  };

  const fetchWishlistStatus = () => {
    if (!user) return;
    checkWishlist(versionId).then(res => {
      setInWishlist(res.data.in_wishlist);
      setWishlistId(res.data.wishlist_id);
    }).catch(() => {});
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchVersion(); }, [versionId]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { fetchWishlistStatus(); }, [versionId, user]);

  const handleToggleWishlist = async () => {
    setTogglingWishlist(true);
    try {
      if (inWishlist && wishlistId) {
        await removeFromWishlist(wishlistId);
        setInWishlist(false);
        setWishlistId(null);
        toast.success('Removed from wishlist');
      } else {
        const res = await addToWishlist({ version_id: versionId });
        setInWishlist(true);
        setWishlistId(res.data.wishlist_id);
        toast.success('Added to wishlist');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update wishlist');
    } finally {
      setTogglingWishlist(false);
    }
  };

  const handleSubmitReview = async () => {
    if (!reviewRating) { toast.error('Please select a rating'); return; }
    setSubmittingReview(true);
    try {
      await createReview({ version_id: versionId, rating: reviewRating, comment: reviewComment });
      toast.success('Review submitted');
      setReviewRating(0);
      setReviewComment('');
      fetchVersion();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit review');
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleAddToCollection = async () => {
    setAddingToCollection(true);
    try {
      const mk = version?.master_kit;
      const seasonYear = parseSeasonYear(mk?.season);
      const est = calculateEstimation({
        modelType: version?.model || 'Replica',
        competition: version?.competition || '',
        conditionOrigin, physicalState, flockingOrigin,
        signed, signedProof, seasonYear,
      });
      await addToCollection({
        version_id: versionId,
        flocking_type: flockingType,
        flocking_origin: flockingOrigin,
        flocking_detail: flockingDetail,
        condition_origin: conditionOrigin,
        physical_state: physicalState,
        size: collectionSize,
        purchase_cost: purchaseCost ? parseFloat(purchaseCost) : null,
        estimated_price: est.estimatedPrice,
        signed,
        signed_by: signed ? signedBy : '',
        signed_proof: signed ? signedProof : false,
        notes: collectionNotes
      });
      toast.success('Added to collection');
      setShowAddForm(false);
      fetchVersion();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add');
    } finally {
      setAddingToCollection(false);
    }
  };

  const handleSubmitReport = async () => {
    try {
      await createReport({
        target_type: 'version',
        target_id: versionId,
        corrections: reportCorrections,
        notes: reportNotes
      });
      toast.success('Report submitted for community review');
      setShowReportForm(false);
      setReportNotes('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit report');
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse px-4 lg:px-8 py-8 max-w-7xl mx-auto">
        <div className="h-8 w-40 bg-card mb-8" />
        <div className="grid md:grid-cols-2 gap-8">
          <div className="aspect-[3/4] bg-card" />
          <div className="space-y-4"><div className="h-10 w-3/4 bg-card" /></div>
        </div>
      </div>
    );
  }

  if (!version) {
    return (
      <div className="px-4 lg:px-8 py-20 text-center">
        <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-2xl tracking-tight mb-2">VERSION NOT FOUND</h2>
        <Link to="/browse"><Button variant="outline" className="rounded-none mt-4">Back to Browse</Button></Link>
      </div>
    );
  }

  const mk = version.master_kit;
  const seasonYear = parseSeasonYear(mk?.season);
  const estimateChartData = estimates && estimates.count > 0 ? [
    { name: 'Low', value: estimates.low, color: '#ef4444' },
    { name: 'Average', value: estimates.average, color: '#facc15' },
    { name: 'High', value: estimates.high, color: '#22c55e' }
  ] : [];

  return (
    <div className="animate-fade-in-up">
      {/* Breadcrumb */}
      <div className="border-b border-border px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
          <Link to="/browse" className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>Browse</Link>
          <ChevronRight className="w-3 h-3" />
          {mk && <Link to={`/kit/${mk.kit_id}`} className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>{mk.club} {mk.season}</Link>}
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground truncate">{version.competition} - {version.model}</span>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
        <div className="grid md:grid-cols-[1fr_1.2fr] gap-8 lg:gap-16">
          {/* Left - Images */}
          <div className="space-y-4">
            <div className="aspect-[3/4] border border-border bg-card overflow-hidden" data-testid="version-front-image">
              <img src={proxyImageUrl(version.front_photo || mk?.front_photo)} alt="Front" className="w-full h-full object-cover" />
            </div>
            {version.back_photo && (
              <div className="aspect-[3/4] border border-border bg-card overflow-hidden" data-testid="version-back-image">
                <img src={proxyImageUrl(version.back_photo)} alt="Back" className="w-full h-full object-cover" />
              </div>
            )}
          </div>

          {/* Right - Info */}
          <div className="space-y-6">
            <div>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="outline" className="rounded-none text-xs">{version.model}</Badge>
                {mk?.gender && <Badge variant="outline" className="rounded-none text-xs">{mk.gender}</Badge>}
              </div>
              {mk && (
                <p className="text-sm text-muted-foreground mb-1" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                  {mk.club} - {mk.season} - {mk.kit_type}
                </p>
              )}
              <h1 className="text-3xl sm:text-4xl tracking-tighter leading-none mb-2" data-testid="version-title">
                {version.competition}
              </h1>
            </div>

            {version.avg_rating > 0 && (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-0.5">
                  {[1, 2, 3, 4, 5].map(s => (
                    <Star key={s} className={`w-5 h-5 ${s <= Math.round(version.avg_rating) ? 'text-accent fill-accent' : 'text-muted'}`} />
                  ))}
                </div>
                <span className="text-sm font-mono text-accent">{version.avg_rating}</span>
                <span className="text-xs text-muted-foreground">({version.review_count} reviews)</span>
              </div>
            )}

            <Separator className="bg-border" />

            {/* Data Grid - All Fields */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className={fieldLabel} style={fieldStyle}>Competition</div>
                <div className="flex items-center gap-2 mt-1"><Package className="w-4 h-4 text-primary" /><span className="text-sm">{version.competition || 'None'}</span></div>
              </div>
              <div>
                <div className={fieldLabel} style={fieldStyle}>Model</div>
                <div className="flex items-center gap-2 mt-1"><Package className="w-4 h-4 text-primary" /><span className="text-sm">{version.model || 'None'}</span></div>
              </div>
              <div>
                <div className={fieldLabel} style={fieldStyle}>SKU</div>
                <div className="flex items-center gap-2 mt-1"><Hash className="w-4 h-4 text-primary" /><span className="text-sm font-mono">{version.sku_code || 'None'}</span></div>
              </div>
              <div>
                <div className={fieldLabel} style={fieldStyle}>EAN</div>
                <div className="flex items-center gap-2 mt-1"><Hash className="w-4 h-4 text-primary" /><span className="text-sm font-mono">{version.ean_code || 'None'}</span></div>
              </div>
              <div>
                <div className={fieldLabel} style={fieldStyle}>In Collections</div>
                <div className="flex items-center gap-2 mt-1"><Users className="w-4 h-4 text-primary" /><span className="text-sm font-mono">{version.collection_count || 0}</span></div>
              </div>
            </div>

            {/* Estimation Stats */}
            {estimates && estimates.count > 0 && (
              <div className="border border-border p-4" data-testid="estimation-stats">
                <h3 className="text-sm uppercase tracking-wider mb-4" style={fieldStyle}>
                  VALUE ESTIMATION
                  <span className="font-mono text-xs text-muted-foreground ml-2 normal-case">({estimates.count} estimates)</span>
                </h3>
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-3 bg-destructive/5 border border-destructive/20">
                    <TrendingDown className="w-4 h-4 text-destructive mx-auto mb-1" />
                    <div className="font-mono text-lg">{estimates.low}&euro;</div>
                    <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>Low</div>
                  </div>
                  <div className="text-center p-3 bg-accent/5 border border-accent/20">
                    <Minus className="w-4 h-4 text-accent mx-auto mb-1" />
                    <div className="font-mono text-lg">{estimates.average}&euro;</div>
                    <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>Average</div>
                  </div>
                  <div className="text-center p-3 bg-primary/5 border border-primary/20">
                    <TrendingUp className="w-4 h-4 text-primary mx-auto mb-1" />
                    <div className="font-mono text-lg">{estimates.high}&euro;</div>
                    <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>High</div>
                  </div>
                </div>
                <div className="h-32">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={estimateChartData} barSize={40}>
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#a1a1aa', fontSize: 11 }} />
                      <YAxis hide />
                      <Tooltip contentStyle={{ background: '#18181b', border: '1px solid #27272a', borderRadius: 0, fontSize: 12 }} formatter={(value) => [`${value}€`, 'Value']} />
                      <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                        {estimateChartData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Actions */}
            {user && (
              <div className="flex flex-wrap gap-2">
                {!showAddForm && (
                  <Button onClick={() => setShowAddForm(true)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="add-to-collection-btn">
                    <FolderPlus className="w-4 h-4 mr-2" /> Add to Collection
                  </Button>
                )}
                <Button
                  variant={inWishlist ? "default" : "outline"}
                  onClick={handleToggleWishlist}
                  disabled={togglingWishlist}
                  className={`rounded-none ${inWishlist ? 'bg-red-600 hover:bg-red-700 text-white border-red-600' : 'border-border'}`}
                  data-testid="toggle-wishlist-btn"
                >
                  <Heart className={`w-4 h-4 mr-2 ${inWishlist ? 'fill-white' : ''}`} />
                  {inWishlist ? 'In Wishlist' : 'Add to Wishlist'}
                </Button>
                <Button variant="outline" onClick={() => setShowReportForm(!showReportForm)} className="rounded-none border-border" data-testid="report-btn">
                  <AlertTriangle className="w-4 h-4 mr-2" /> Report Error
                </Button>
              </div>
            )}

            {/* Add to Collection Form */}
            {showAddForm && user && (
              <div className="border border-primary/30 p-4 space-y-4" data-testid="add-collection-form">
                <h4 className="text-sm uppercase tracking-wider" style={fieldStyle}>ADD TO COLLECTION</h4>

                {/* Flocking Section */}
                <div className="space-y-3">
                  <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>FLOCKING</p>
                  <div className="grid grid-cols-3 gap-3">
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fieldStyle}>Type</Label>
                      <Select value={flockingType || "none"} onValueChange={v => setFlockingType(v === "none" ? "" : v)}>
                        <SelectTrigger className={inputClass} data-testid="collection-flocking-type"><SelectValue placeholder="None" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          <SelectItem value="none">None</SelectItem>
                          {FLOCKING_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fieldStyle}>Origin</Label>
                      <Select value={flockingOrigin || "none"} onValueChange={v => setFlockingOrigin(v === "none" ? "" : v)}>
                        <SelectTrigger className={inputClass} data-testid="collection-flocking-origin"><SelectValue placeholder="None" /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          <SelectItem value="none">None</SelectItem>
                          {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className={fieldLabel} style={fieldStyle}>Detail</Label>
                      <Input value={flockingDetail} onChange={e => setFlockingDetail(e.target.value)} placeholder="e.g., Messi 10" className={inputClass} data-testid="collection-flocking-detail" />
                    </div>
                  </div>
                </div>

                {/* Condition & State */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Condition (Origin)</Label>
                    <Select value={conditionOrigin || "none"} onValueChange={v => setConditionOrigin(v === "none" ? "" : v)}>
                      <SelectTrigger className={inputClass} data-testid="collection-condition-origin"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {CONDITION_ORIGINS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Physical State</Label>
                    <Select value={physicalState || "none"} onValueChange={v => setPhysicalState(v === "none" ? "" : v)}>
                      <SelectTrigger className={inputClass} data-testid="collection-physical-state"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Size & Purchase Cost */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Size</Label>
                    <Select value={collectionSize || "none"} onValueChange={v => setCollectionSize(v === "none" ? "" : v)}>
                      <SelectTrigger className={inputClass} data-testid="collection-size-select"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Purchase Cost (&euro;)</Label>
                    <Input type="number" value={purchaseCost} onChange={e => setPurchaseCost(e.target.value)} placeholder="0.00" className={`${inputClass} font-mono`} data-testid="collection-purchase-cost" />
                  </div>
                </div>

                {/* Signed */}
                <div className="space-y-3">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Switch checked={signed} onCheckedChange={setSigned} data-testid="collection-signed-switch" />
                      <Label className="text-xs" style={fieldStyle}>SIGNED</Label>
                    </div>
                    {signed && (
                      <div className="flex-1">
                        <Input value={signedBy} onChange={e => setSignedBy(e.target.value)} placeholder="Signed by (player name)" className={inputClass} data-testid="collection-signed-by" />
                      </div>
                    )}
                  </div>
                  {signed && (
                    <div className="flex items-center gap-2 ml-12">
                      <Switch checked={signedProof} onCheckedChange={setSignedProof} data-testid="collection-signed-proof" />
                      <Label className="text-[10px] text-muted-foreground" style={fieldStyle}>PROOF / CERTIFICATE</Label>
                    </div>
                  )}
                </div>

                <div className="space-y-1">
                  <Label className={fieldLabel} style={fieldStyle}>Notes</Label>
                  <Textarea value={collectionNotes} onChange={e => setCollectionNotes(e.target.value)} placeholder="Personal notes..." className="bg-card border-border rounded-none min-h-[60px] text-sm" data-testid="collection-notes-input" />
                </div>

                {/* Real-time Estimation */}
                <EstimationBreakdown
                  modelType={version?.model || 'Replica'}
                  competition={version?.competition || ''}
                  conditionOrigin={conditionOrigin}
                  physicalState={physicalState}
                  flockingOrigin={flockingOrigin}
                  signed={signed}
                  signedProof={signedProof}
                  seasonYear={seasonYear}
                />

                <div className="flex gap-2">
                  <Button onClick={handleAddToCollection} disabled={addingToCollection} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="confirm-add-collection-btn">
                    <Check className="w-4 h-4 mr-1" /> {addingToCollection ? 'Adding...' : 'Confirm'}
                  </Button>
                  <Button variant="outline" onClick={() => setShowAddForm(false)} className="rounded-none" data-testid="cancel-add-collection-btn">Cancel</Button>
                </div>
              </div>
            )}

            {/* Report Form */}
            {showReportForm && user && (
              <div className="border border-destructive/30 p-4 space-y-3" data-testid="report-form">
                <h4 className="text-sm uppercase tracking-wider" style={fieldStyle}>REPORT ERROR</h4>
                <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                  Suggest corrections for this version. Community will vote on changes.
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Competition</Label>
                    <Input value={reportCorrections.competition || ''} onChange={e => setReportCorrections(p => ({...p, competition: e.target.value}))} className={inputClass} data-testid="report-competition" />
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Model</Label>
                    <Input value={reportCorrections.model || ''} onChange={e => setReportCorrections(p => ({...p, model: e.target.value}))} className={inputClass} data-testid="report-model" />
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>SKU Code</Label>
                    <Input value={reportCorrections.sku_code || ''} onChange={e => setReportCorrections(p => ({...p, sku_code: e.target.value}))} className={`${inputClass} font-mono`} data-testid="report-sku" />
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>EAN Code</Label>
                    <Input value={reportCorrections.ean_code || ''} onChange={e => setReportCorrections(p => ({...p, ean_code: e.target.value}))} className={`${inputClass} font-mono`} data-testid="report-ean" />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fieldStyle}>Notes</Label>
                  <Textarea value={reportNotes} onChange={e => setReportNotes(e.target.value)} placeholder="Describe the error..." className="bg-card border-border rounded-none min-h-[60px] text-sm" data-testid="report-notes" />
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSubmitReport} className="rounded-none bg-destructive text-destructive-foreground hover:bg-destructive/90" data-testid="submit-report-btn">
                    Submit Report
                  </Button>
                  <Button variant="outline" onClick={() => setShowReportForm(false)} className="rounded-none">Cancel</Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Reviews Section */}
        <div className="mt-16 border-t border-border pt-8">
          <h2 className="text-xl tracking-tight mb-6" data-testid="reviews-section-title">
            REVIEWS <span className="font-mono text-sm text-muted-foreground ml-2">{version.review_count || 0}</span>
          </h2>

          {user && (
            <div className="border border-border p-6 mb-8" data-testid="review-form">
              <h3 className="text-sm font-semibold mb-4" style={fieldStyle}>WRITE A REVIEW</h3>
              <div className="flex items-center gap-1 mb-4">
                {[1, 2, 3, 4, 5].map(s => (
                  <button key={s} onClick={() => setReviewRating(s)} onMouseEnter={() => setReviewHover(s)} onMouseLeave={() => setReviewHover(0)} data-testid={`star-rating-${s}`}>
                    <Star className={`w-6 h-6 cursor-pointer ${s <= (reviewHover || reviewRating) ? 'text-accent fill-accent' : 'text-muted'}`} style={{ transition: 'color 0.15s ease' }} />
                  </button>
                ))}
                {reviewRating > 0 && <span className="text-sm font-mono text-accent ml-2">{reviewRating}/5</span>}
              </div>
              <Textarea value={reviewComment} onChange={e => setReviewComment(e.target.value)} placeholder="Share your thoughts..." className="bg-card border-border rounded-none mb-3 min-h-[80px]" data-testid="review-comment-input" />
              <Button onClick={handleSubmitReview} disabled={submittingReview} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="submit-review-btn">
                {submittingReview ? 'Submitting...' : 'Submit Review'}
              </Button>
            </div>
          )}

          {version.reviews && version.reviews.length > 0 ? (
            <div className="space-y-4 stagger-children" data-testid="reviews-list">
              {version.reviews.map(r => (
                <div key={r.review_id} className="border border-border p-4" data-testid={`review-${r.review_id}`}>
                  <div className="flex items-center gap-3 mb-3">
                    <Avatar className="w-7 h-7 border border-border">
                      <AvatarImage src={r.user_picture} />
                      <AvatarFallback className="text-[10px] bg-secondary">{r.user_name?.[0]}</AvatarFallback>
                    </Avatar>
                    <div>
                      <span className="text-sm font-medium">{r.user_name || 'Anonymous'}</span>
                      <div className="flex items-center gap-0.5">
                        {[1, 2, 3, 4, 5].map(s => (
                          <Star key={s} className={`w-3 h-3 ${s <= r.rating ? 'text-accent fill-accent' : 'text-muted'}`} />
                        ))}
                      </div>
                    </div>
                    <span className="text-[10px] text-muted-foreground font-mono ml-auto">
                      {r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  {r.comment && <p className="text-sm text-muted-foreground leading-relaxed" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{r.comment}</p>}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border border-dashed border-border">
              <Star className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No reviews yet. Be the first!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
