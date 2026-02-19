import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMasterKit, createReport, proxyImageUrl } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Star, Shirt, ArrowLeft, Tag, Package, ChevronRight, AlertTriangle, Check, Trash2 } from 'lucide-react';

const KIT_TYPES = ['Home', 'Away', 'Third', 'Fourth', 'GK', 'Special', 'Other'];
const GENDERS = ['Men', 'Women', 'Youth', 'Unisex'];

export default function KitDetail() {
  const { kitId } = useParams();
  const { user } = useAuth();
  const [kit, setKit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showReport, setShowReport] = useState(false);
  const [reportCorrections, setReportCorrections] = useState({});
  const [reportNotes, setReportNotes] = useState('');
  const [showRemovalForm, setShowRemovalForm] = useState(false);
  const [removalNotes, setRemovalNotes] = useState('');

  useEffect(() => {
    getMasterKit(kitId).then(r => {
      setKit(r.data);
      setReportCorrections({
        club: r.data.club,
        season: r.data.season,
        kit_type: r.data.kit_type,
        brand: r.data.brand,
        design: r.data.design || '',
        sponsor: r.data.sponsor || '',
        league: r.data.league || '',
        gender: r.data.gender || '',
      });
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [kitId]);

  const handleSubmitReport = async () => {
    try {
      await createReport({
        target_type: 'master_kit',
        target_id: kitId,
        corrections: reportCorrections,
        notes: reportNotes,
        report_type: 'error'
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
        target_id: kitId,
        corrections: {},
        notes: removalNotes,
        report_type: 'removal'
      });
      toast.success('Removal request submitted for community vote');
      setShowRemovalForm(false);
      setRemovalNotes('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to submit removal request');
    }
  };

  if (loading) {
    return (
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
  }

  if (!kit) {
    return (
      <div className="px-4 lg:px-8 py-20 text-center">
        <Shirt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-2xl tracking-tight mb-2">KIT NOT FOUND</h2>
        <Link to="/browse"><Button variant="outline" className="rounded-none mt-4">Back to Browse</Button></Link>
      </div>
    );
  }

  return (
    <div className="animate-fade-in-up">
      {/* Breadcrumb */}
      <div className="border-b border-border px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-sm text-muted-foreground">
          <Link to="/browse" className="hover:text-foreground" style={{ transition: 'color 0.2s ease' }}>Browse</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground truncate">{kit.club} {kit.season}</span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
          <div className="grid md:grid-cols-[1fr_1.2fr] gap-8 lg:gap-16">
            {/* Left - Image */}
            <div className="relative">
              <div className="aspect-[3/4] border border-border bg-card overflow-hidden" data-testid="kit-main-image">
                <img
                  src={proxyImageUrl(kit.front_photo)}
                  alt={`${kit.club} ${kit.season}`}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Right - Info */}
            <div className="space-y-6">
              <div>
                <Badge variant="outline" className="rounded-none text-xs mb-3">{kit.kit_type}</Badge>
                <h1 className="text-4xl sm:text-5xl tracking-tighter leading-none mb-2" data-testid="kit-title">
                  {kit.club}
                </h1>
                <p className="text-lg text-muted-foreground" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                  {kit.season} Season
                </p>
              </div>

              {kit.avg_rating > 0 && (
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    {[1, 2, 3, 4, 5].map(s => (
                      <Star key={s} className={`w-4 h-4 ${s <= Math.round(kit.avg_rating) ? 'text-accent fill-accent' : 'text-muted'}`} />
                    ))}
                  </div>
                  <span className="text-sm font-mono text-accent">{kit.avg_rating}</span>
                </div>
              )}

              <Separator className="bg-border" />

              {/* Data Grid - All Fields */}
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Brand</div>
                  <div className="flex items-center gap-2">
                    <Tag className="w-4 h-4 text-primary" />
                    <span className="text-sm">{kit.brand || 'None'}</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Type</div>
                  <div className="flex items-center gap-2">
                    <Shirt className="w-4 h-4 text-primary" />
                    <span className="text-sm">{kit.kit_type || 'None'}</span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>League</div>
                  <span className="text-sm">{kit.league || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Design</div>
                  <span className="text-sm">{kit.design || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Sponsor</div>
                  <span className="text-sm">{kit.sponsor || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Gender</div>
                  <span className="text-sm">{kit.gender || 'None'}</span>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Versions</div>
                  <div className="flex items-center gap-2">
                    <Package className="w-4 h-4 text-primary" />
                    <span className="text-sm font-mono">{kit.version_count}</span>
                  </div>
                </div>
              </div>

              {/* Report Button */}
              {user && (
                <div>
                  <Button variant="outline" size="sm" onClick={() => setShowReport(!showReport)} className="rounded-none border-border" data-testid="kit-report-btn">
                    <AlertTriangle className="w-4 h-4 mr-1" /> Report Error
                  </Button>
                </div>
              )}

              {/* Report Form */}
              {showReport && user && (
                <div className="border border-destructive/30 p-4 space-y-3" data-testid="kit-report-form">
                  <h4 className="text-sm uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>REPORT ERROR</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Team</Label>
                      <Input value={reportCorrections.club || ''} onChange={e => setReportCorrections(p => ({...p, club: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-club" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Season</Label>
                      <Input value={reportCorrections.season || ''} onChange={e => setReportCorrections(p => ({...p, season: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-season" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Type</Label>
                      <Select value={reportCorrections.kit_type || ''} onValueChange={v => setReportCorrections(p => ({...p, kit_type: v}))}>
                        <SelectTrigger className="bg-card border-border rounded-none h-9 text-sm"><SelectValue /></SelectTrigger>
                        <SelectContent className="bg-card border-border">
                          {KIT_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Brand</Label>
                      <Input value={reportCorrections.brand || ''} onChange={e => setReportCorrections(p => ({...p, brand: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-brand" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Design</Label>
                      <Input value={reportCorrections.design || ''} onChange={e => setReportCorrections(p => ({...p, design: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-design" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Sponsor</Label>
                      <Input value={reportCorrections.sponsor || ''} onChange={e => setReportCorrections(p => ({...p, sponsor: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-sponsor" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>League</Label>
                      <Input value={reportCorrections.league || ''} onChange={e => setReportCorrections(p => ({...p, league: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-league" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Gender</Label>
                      <Input value={reportCorrections.gender || ''} onChange={e => setReportCorrections(p => ({...p, gender: e.target.value}))} className="bg-card border-border rounded-none h-9 text-sm" data-testid="kit-report-gender" />
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
            </div>
          </div>
        </div>
      </div>

      {/* Versions Section */}
      <div className="border-t border-border">
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
          <h2 className="text-xl tracking-tight mb-6" data-testid="versions-section-title">
            VERSIONS <span className="font-mono text-sm text-muted-foreground ml-2">{kit.versions?.length || 0}</span>
          </h2>
          {kit.versions && kit.versions.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children" data-testid="versions-grid">
              {kit.versions.map(v => (
                <Link to={`/version/${v.version_id}`} key={v.version_id}>
                  <div className="border border-border bg-card p-4 hover:border-primary/30 group" data-testid={`version-card-${v.version_id}`} style={{ transition: 'border-color 0.2s ease' }}>
                    <div className="flex gap-4">
                      <div className="w-20 h-24 bg-secondary overflow-hidden shrink-0">
                        <img src={proxyImageUrl(v.front_photo || kit.front_photo)} alt="" className="w-full h-full object-cover" />
                      </div>
                      <div className="min-w-0 space-y-1.5">
                        <Badge variant="outline" className="rounded-none text-[10px]">{v.model}</Badge>
                        <h4 className="text-sm font-semibold truncate" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>
                          {v.competition}
                        </h4>
                        {v.sku_code && <p className="font-mono text-[10px] text-muted-foreground">{v.sku_code}</p>}
                        {v.ean_code && <p className="font-mono text-[10px] text-muted-foreground">EAN: {v.ean_code}</p>}
                        {v.avg_rating > 0 && (
                          <div className="flex items-center gap-1">
                            <Star className="w-3 h-3 text-accent fill-accent" />
                            <span className="text-xs font-mono text-accent">{v.avg_rating}</span>
                            <span className="text-[10px] text-muted-foreground">({v.review_count})</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 border border-dashed border-border">
              <Package className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
              <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No versions added yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
