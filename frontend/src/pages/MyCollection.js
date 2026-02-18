import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMyCollection, getCollectionCategories, removeFromCollection, updateCollectionItem, getCollectionStats, getCategoryStats, proxyImageUrl } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { toast } from 'sonner';
import { Shirt, LayoutGrid, List, Trash2, FolderOpen, Edit2, Check, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';

const CONDITION_ORIGINS = ['Club Stock', 'Match Prepared', 'Match Worn', 'Training', 'Shop'];
const PHYSICAL_STATES = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_TYPES = ['Name+Number', 'Name', 'Number'];
const FLOCKING_ORIGINS = ['Official', 'Personalized'];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];

const fieldLabel = "text-xs uppercase tracking-wider";
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = "bg-card border-border rounded-none";

function parseSeasonYear(season) {
  if (!season) return 0;
  const match = season.match(/(\d{4})/);
  return match ? parseInt(match[1]) : 0;
}

export default function MyCollection() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [categoryStats, setCategoryStats] = useState([]);
  const [detailItem, setDetailItem] = useState(null);
  const [editForm, setEditForm] = useState({});

  const fetchCollection = async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      const [colRes, statsRes, catStatsRes] = await Promise.all([
        getMyCollection(params),
        getCollectionStats(),
        getCategoryStats()
      ]);
      setItems(colRes.data);
      setStats(statsRes.data);
      setCategoryStats(catStatsRes.data);
    } catch { /* ignore */ } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCollection();
    getCollectionCategories().then(r => setCategories(r.data)).catch(() => {});
  }, [selectedCategory]);

  const handleRemove = async (collectionId) => {
    try {
      await removeFromCollection(collectionId);
      toast.success('Removed from collection');
      setDetailItem(null);
      fetchCollection();
    } catch {
      toast.error('Failed to remove');
    }
  };

  const openDetail = (item) => {
    setDetailItem(item);
    setEditForm({
      flocking_type: item.flocking_type || '',
      flocking_origin: item.flocking_origin || '',
      flocking_detail: item.flocking_detail || item.printing || '',
      condition_origin: item.condition_origin || '',
      physical_state: item.physical_state || item.condition || '',
      size: item.size || '',
      purchase_cost: item.purchase_cost || '',
      signed: item.signed || false,
      signed_by: item.signed_by || '',
      signed_proof: item.signed_proof || false,
      notes: item.notes || '',
      category: item.category || 'General',
    });
  };

  const saveEdit = async () => {
    if (!detailItem) return;
    try {
      const mk = detailItem.master_kit;
      const seasonYear = parseSeasonYear(mk?.season);
      const est = calculateEstimation({
        modelType: detailItem.version?.model || 'Replica',
        competition: detailItem.version?.competition || '',
        conditionOrigin: editForm.condition_origin || '',
        physicalState: editForm.physical_state || '',
        flockingOrigin: editForm.flocking_origin || '',
        signed: editForm.signed || false,
        signedProof: editForm.signed_proof || false,
        seasonYear,
      });
      const data = {
        ...editForm,
        purchase_cost: editForm.purchase_cost ? parseFloat(editForm.purchase_cost) : null,
        estimated_price: est.estimatedPrice,
      };
      await updateCollectionItem(detailItem.collection_id, data);
      toast.success('Item updated');
      setDetailItem(null);
      fetchCollection();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update');
    }
  };

  const getFlockingLabel = (item) => {
    const detail = item.flocking_detail || item.printing;
    if (!detail) return null;
    const parts = [detail];
    if (item.flocking_origin) parts.push(`(${item.flocking_origin})`);
    return parts.join(' ');
  };

  const getConditionLabel = (item) => {
    const parts = [];
    if (item.condition_origin) parts.push(item.condition_origin);
    if (item.physical_state || item.condition) parts.push(item.physical_state || item.condition);
    return parts.join(' / ') || null;
  };

  const getEstimatedPrice = (item) => {
    if (item.estimated_price) return item.estimated_price;
    return null;
  };

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="collection-title">MY COLLECTION</h1>
          <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
            {items.length} jerseys in your locker room
          </p>

          {stats && stats.total_jerseys > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6" data-testid="collection-value-stats">
              <div className="border border-border p-4 text-center">
                <Shirt className="w-4 h-4 text-primary mx-auto mb-1" />
                <div className="font-mono text-2xl">{stats.total_jerseys}</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>Total Jerseys</div>
              </div>
              <div className="border border-destructive/20 p-4 text-center">
                <TrendingDown className="w-4 h-4 text-destructive mx-auto mb-1" />
                <div className="font-mono text-2xl">{stats.estimated_value.low}&euro;</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>Low Est.</div>
              </div>
              <div className="border border-accent/20 p-4 text-center">
                <Minus className="w-4 h-4 text-accent mx-auto mb-1" />
                <div className="font-mono text-2xl">{stats.estimated_value.average}&euro;</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>Avg Est.</div>
              </div>
              <div className="border border-primary/20 p-4 text-center">
                <TrendingUp className="w-4 h-4 text-primary mx-auto mb-1" />
                <div className="font-mono text-2xl">{stats.estimated_value.high}&euro;</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={fieldStyle}>High Est.</div>
              </div>
            </div>
          )}

          {categoryStats.length > 0 && (
            <div className="mb-6" data-testid="category-stats">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={fieldStyle}>CATEGORY BREAKDOWN</h3>
              <div className="flex flex-wrap gap-2">
                {categoryStats.map(cs => (
                  <button key={cs.category} onClick={() => setSelectedCategory(selectedCategory === cs.category ? '' : cs.category)}
                    className={`border px-3 py-2 text-left ${selectedCategory === cs.category ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/30'}`}
                    style={{ transition: 'border-color 0.2s' }} data-testid={`category-stat-${cs.category}`}>
                    <div className="text-xs font-semibold" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{cs.category}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="font-mono text-xs">{cs.count} jerseys</span>
                      {cs.estimated_value.average > 0 && <span className="font-mono text-[10px] text-accent">~{cs.estimated_value.average}&euro;</span>}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-3">
            {categories.length > 0 && !categoryStats.length && (
              <Select value={selectedCategory || "all"} onValueChange={(v) => setSelectedCategory(v === "all" ? "" : v)}>
                <SelectTrigger className="bg-card border-border rounded-none w-48" data-testid="collection-category-filter"><SelectValue placeholder="All Categories" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            )}
            <div className="flex items-center border border-border ml-auto">
              <button onClick={() => setViewMode('grid')} className={`p-2 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-grid"><LayoutGrid className="w-4 h-4" /></button>
              <button onClick={() => setViewMode('list')} className={`p-2 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-list"><List className="w-4 h-4" /></button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />)}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20" data-testid="empty-collection">
            <FolderOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-2xl tracking-tight mb-2">LOCKER ROOM IS EMPTY</h3>
            <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Start building your collection by browsing the catalog</p>
            <Link to="/browse"><Button className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="browse-catalog-btn">Browse Catalog</Button></Link>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children" data-testid="collection-grid">
            {items.map(item => (
              <div key={item.collection_id} className="card-shimmer relative border border-border bg-card overflow-hidden group" data-testid={`collection-item-${item.collection_id}`}>
                <Link to={`/version/${item.version_id}`}>
                  <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
                    <img src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)} alt={item.master_kit?.club} className="w-full h-full object-cover group-hover:scale-105" style={{ transition: 'transform 0.5s ease' }} />
                    {getConditionLabel(item) && (
                      <div className="absolute bottom-2 left-2"><Badge variant="secondary" className="rounded-none text-[10px]">{getConditionLabel(item)}</Badge></div>
                    )}
                    {item.signed && (
                      <div className="absolute bottom-2 right-2"><Badge className="rounded-none text-[10px] bg-accent/90 text-accent-foreground border-none">Signed</Badge></div>
                    )}
                  </div>
                  <div className="p-3 space-y-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{item.master_kit?.club}</h3>
                    <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season} - {item.version?.model}</p>
                    {getFlockingLabel(item) && <p className="text-xs text-primary/80 truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getFlockingLabel(item)}</p>}
                    <div className="flex items-center justify-between">
                      {item.size && <span className="font-mono text-[10px] text-muted-foreground">{item.size}</span>}
                      {getEstimatedPrice(item) && <span className="font-mono text-xs text-accent">{getEstimatedPrice(item)}&euro;</span>}
                    </div>
                  </div>
                </Link>
                <div className="absolute top-2 left-2 flex gap-1 opacity-0 group-hover:opacity-100" style={{ transition: 'opacity 0.2s ease' }}>
                  <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); openDetail(item); }} className="p-1.5 bg-card/90 border border-border text-muted-foreground hover:text-foreground" data-testid={`edit-collection-${item.collection_id}`}><Edit2 className="w-3 h-3" /></button>
                  <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleRemove(item.collection_id); }} className="p-1.5 bg-destructive/90 text-destructive-foreground" data-testid={`remove-collection-${item.collection_id}`}><Trash2 className="w-3 h-3" /></button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2 stagger-children" data-testid="collection-list">
            {items.map(item => (
              <div key={item.collection_id} className="flex items-center gap-4 p-3 border border-border bg-card group" data-testid={`collection-list-item-${item.collection_id}`}>
                <Link to={`/version/${item.version_id}`} className="flex items-center gap-4 flex-1 min-w-0">
                  <img src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)} alt="" className="w-14 h-18 object-cover" />
                  <div className="min-w-0">
                    <h3 className="text-sm font-semibold truncate">{item.master_kit?.club}</h3>
                    <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season} - {item.version?.competition}</p>
                    {getFlockingLabel(item) && <p className="text-xs text-primary/80 truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getFlockingLabel(item)}</p>}
                  </div>
                </Link>
                <Badge variant="outline" className="rounded-none text-[10px] shrink-0">{item.version?.model}</Badge>
                {getConditionLabel(item) && <Badge variant="secondary" className="rounded-none text-[10px] shrink-0">{getConditionLabel(item)}</Badge>}
                {item.size && <span className="font-mono text-[10px] text-muted-foreground shrink-0">{item.size}</span>}
                {getEstimatedPrice(item) && <span className="font-mono text-xs text-accent shrink-0">{getEstimatedPrice(item)}&euro;</span>}
                {item.signed && <Badge className="rounded-none text-[10px] bg-accent/90 shrink-0">Signed</Badge>}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 shrink-0" style={{ transition: 'opacity 0.2s ease' }}>
                  <button onClick={() => openDetail(item)} className="p-1.5 text-muted-foreground hover:text-foreground" data-testid={`edit-list-${item.collection_id}`}><Edit2 className="w-4 h-4" /></button>
                  <button onClick={() => handleRemove(item.collection_id)} className="p-1.5 text-muted-foreground hover:text-destructive" style={{ transition: 'color 0.2s ease' }} data-testid={`remove-list-${item.collection_id}`}><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Edit Sheet */}
      <Sheet open={!!detailItem} onOpenChange={(open) => { if (!open) setDetailItem(null); }}>
        <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto" data-testid="item-detail-sheet">
          {detailItem && (
            <>
              <SheetHeader className="mb-6">
                <SheetTitle className="text-left tracking-tighter" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>EDIT ITEM</SheetTitle>
              </SheetHeader>

              <div className="mb-6">
                <div className="flex gap-4 mb-4">
                  <img src={proxyImageUrl(detailItem.version?.front_photo || detailItem.master_kit?.front_photo)} alt={detailItem.master_kit?.club} className="w-20 h-28 object-cover border border-border" />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{detailItem.master_kit?.club}</h3>
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{detailItem.master_kit?.season} - {detailItem.master_kit?.kit_type}</p>
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{detailItem.master_kit?.brand}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.model}</Badge>
                      <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.competition}</Badge>
                    </div>
                  </div>
                </div>
                <div className="h-px bg-border" />
              </div>

              <div className="space-y-4">
                <p className="text-xs uppercase tracking-wider text-muted-foreground" style={fieldStyle}>ITEM DETAILS</p>

                {/* Flocking */}
                <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>FLOCKING</p>
                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Type</Label>
                    <Select value={editForm.flocking_type || "none"} onValueChange={v => setEditForm(p => ({...p, flocking_type: v === "none" ? "" : v}))}>
                      <SelectTrigger className={inputClass} data-testid="detail-flocking-type"><SelectValue placeholder="None" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {FLOCKING_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Origin</Label>
                    <Select value={editForm.flocking_origin || "none"} onValueChange={v => setEditForm(p => ({...p, flocking_origin: v === "none" ? "" : v}))}>
                      <SelectTrigger className={inputClass} data-testid="detail-flocking-origin"><SelectValue placeholder="None" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Detail</Label>
                    <Input value={editForm.flocking_detail || ''} onChange={e => setEditForm(p => ({...p, flocking_detail: e.target.value}))} placeholder="e.g., Messi 10" className={inputClass} data-testid="detail-flocking-detail" />
                  </div>
                </div>

                {/* Condition & State */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label className={fieldLabel} style={fieldStyle}>Condition (Origin)</Label>
                    <Select value={editForm.condition_origin || "none"} onValueChange={v => setEditForm(p => ({...p, condition_origin: v === "none" ? "" : v}))}>
                      <SelectTrigger className={inputClass} data-testid="detail-condition-origin"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {CONDITION_ORIGINS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className={fieldLabel} style={fieldStyle}>Physical State</Label>
                    <Select value={editForm.physical_state || "none"} onValueChange={v => setEditForm(p => ({...p, physical_state: v === "none" ? "" : v}))}>
                      <SelectTrigger className={inputClass} data-testid="detail-physical-state"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Size & Purchase Cost */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label className={fieldLabel} style={fieldStyle}>Size</Label>
                    <Select value={editForm.size || "none"} onValueChange={v => setEditForm(p => ({...p, size: v === "none" ? "" : v}))}>
                      <SelectTrigger className={inputClass} data-testid="detail-size"><SelectValue placeholder="Select" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label className={fieldLabel} style={fieldStyle}>Purchase Cost (&euro;)</Label>
                    <Input type="number" value={editForm.purchase_cost || ''} onChange={e => setEditForm(p => ({...p, purchase_cost: e.target.value}))} placeholder="0" className={`${inputClass} font-mono`} data-testid="detail-purchase-cost" />
                  </div>
                </div>

                {/* Signed */}
                <div className="space-y-3">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Switch checked={editForm.signed || false} onCheckedChange={v => setEditForm(p => ({...p, signed: v}))} data-testid="detail-signed-switch" />
                      <Label className="text-xs" style={fieldStyle}>SIGNED</Label>
                    </div>
                    {editForm.signed && (
                      <div className="flex-1">
                        <Input value={editForm.signed_by || ''} onChange={e => setEditForm(p => ({...p, signed_by: e.target.value}))} placeholder="Player name" className={inputClass} data-testid="detail-signed-by" />
                      </div>
                    )}
                  </div>
                  {editForm.signed && (
                    <div className="flex items-center gap-2 ml-12">
                      <Switch checked={editForm.signed_proof || false} onCheckedChange={v => setEditForm(p => ({...p, signed_proof: v}))} data-testid="detail-signed-proof" />
                      <Label className="text-[10px] text-muted-foreground" style={fieldStyle}>PROOF / CERTIFICATE</Label>
                    </div>
                  )}
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <Label className={fieldLabel} style={fieldStyle}>Notes</Label>
                  <Textarea value={editForm.notes || ''} onChange={e => setEditForm(p => ({...p, notes: e.target.value}))} placeholder="Any notes..." className="bg-card border-border rounded-none min-h-[80px]" data-testid="detail-notes" />
                </div>

                {/* Real-time Estimation */}
                <EstimationBreakdown
                  modelType={detailItem.version?.model || 'Replica'}
                  conditionOrigin={editForm.condition_origin || ''}
                  physicalState={editForm.physical_state || ''}
                  flockingOrigin={editForm.flocking_origin || ''}
                  signed={editForm.signed || false}
                  signedProof={editForm.signed_proof || false}
                  seasonYear={parseSeasonYear(detailItem.master_kit?.season)}
                />
              </div>

              <div className="flex gap-2 mt-6">
                <Button onClick={saveEdit} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 flex-1" data-testid="detail-save-btn">
                  <Check className="w-4 h-4 mr-1" /> Save Changes
                </Button>
                <Button variant="outline" onClick={() => handleRemove(detailItem.collection_id)} className="rounded-none text-destructive hover:text-destructive" data-testid="detail-remove-btn">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
