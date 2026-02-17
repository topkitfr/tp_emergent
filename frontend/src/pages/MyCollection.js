import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMyCollection, getCollectionCategories, removeFromCollection, updateCollectionItem, getCollectionStats, getCategoryStats } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import { Shirt, LayoutGrid, List, Trash2, FolderOpen, Edit2, X, Check, TrendingUp, TrendingDown, Minus, DollarSign } from 'lucide-react';

const CONDITIONS = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];

export default function MyCollection() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [categoryStats, setCategoryStats] = useState([]);
  const [editingId, setEditingId] = useState(null);
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
      fetchCollection();
    } catch {
      toast.error('Failed to remove');
    }
  };

  const startEdit = (item) => {
    setEditingId(item.collection_id);
    setEditForm({
      condition: item.condition || '',
      size: item.size || '',
      value_estimate: item.value_estimate || '',
      notes: item.notes || '',
      category: item.category || 'General'
    });
  };

  const saveEdit = async (collectionId) => {
    try {
      const data = {
        ...editForm,
        value_estimate: editForm.value_estimate ? parseFloat(editForm.value_estimate) : null
      };
      await updateCollectionItem(collectionId, data);
      toast.success('Updated');
      setEditingId(null);
      fetchCollection();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update');
    }
  };

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="collection-title">
            MY COLLECTION
          </h1>
          <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
            {items.length} jerseys in your locker room
          </p>

          {/* Overall Value Stats */}
          {stats && stats.total_jerseys > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6" data-testid="collection-value-stats">
              <div className="border border-border p-4 text-center">
                <Shirt className="w-4 h-4 text-primary mx-auto mb-1" />
                <div className="font-mono text-2xl">{stats.total_jerseys}</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>Total Jerseys</div>
              </div>
              <div className="border border-destructive/20 p-4 text-center">
                <TrendingDown className="w-4 h-4 text-destructive mx-auto mb-1" />
                <div className="font-mono text-2xl">${stats.estimated_value.low}</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>Low Est.</div>
              </div>
              <div className="border border-accent/20 p-4 text-center">
                <Minus className="w-4 h-4 text-accent mx-auto mb-1" />
                <div className="font-mono text-2xl">${stats.estimated_value.average}</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>Avg Est.</div>
              </div>
              <div className="border border-primary/20 p-4 text-center">
                <TrendingUp className="w-4 h-4 text-primary mx-auto mb-1" />
                <div className="font-mono text-2xl">${stats.estimated_value.high}</div>
                <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>High Est.</div>
              </div>
            </div>
          )}

          {/* Category Stats */}
          {categoryStats.length > 0 && (
            <div className="mb-6" data-testid="category-stats">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={{ fontFamily: 'Barlow Condensed' }}>
                CATEGORY BREAKDOWN
              </h3>
              <div className="flex flex-wrap gap-2">
                {categoryStats.map(cs => (
                  <button
                    key={cs.category}
                    onClick={() => setSelectedCategory(selectedCategory === cs.category ? '' : cs.category)}
                    className={`border px-3 py-2 text-left ${selectedCategory === cs.category ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/30'}`}
                    style={{ transition: 'border-color 0.2s' }}
                    data-testid={`category-stat-${cs.category}`}
                  >
                    <div className="text-xs font-semibold" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{cs.category}</div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="font-mono text-xs">{cs.count} jerseys</span>
                      {cs.estimated_value.average > 0 && (
                        <span className="font-mono text-[10px] text-accent">~${cs.estimated_value.average}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-wrap items-center gap-3">
            {categories.length > 0 && !categoryStats.length && (
              <Select value={selectedCategory || "all"} onValueChange={(v) => setSelectedCategory(v === "all" ? "" : v)}>
                <SelectTrigger className="bg-card border-border rounded-none w-48" data-testid="collection-category-filter">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                </SelectContent>
              </Select>
            )}
            <div className="flex items-center border border-border ml-auto">
              <button onClick={() => setViewMode('grid')} className={`p-2 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-grid">
                <LayoutGrid className="w-4 h-4" />
              </button>
              <button onClick={() => setViewMode('list')} className={`p-2 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-list">
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20" data-testid="empty-collection">
            <FolderOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-2xl tracking-tight mb-2">LOCKER ROOM IS EMPTY</h3>
            <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
              Start building your collection by browsing the catalog
            </p>
            <Link to="/browse">
              <Button className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="browse-catalog-btn">
                Browse Catalog
              </Button>
            </Link>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children" data-testid="collection-grid">
            {items.map(item => (
              <div key={item.collection_id} className="card-shimmer relative border border-border bg-card overflow-hidden group" data-testid={`collection-item-${item.collection_id}`}>
                <Link to={`/version/${item.version_id}`}>
                  <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
                    <img src={item.version?.front_photo || item.master_kit?.front_photo} alt={item.master_kit?.club} className="w-full h-full object-cover group-hover:scale-105" style={{ transition: 'transform 0.5s ease' }} />
                    <div className="absolute top-2 right-2">
                      <Badge className="rounded-none text-[10px] bg-primary/90 text-primary-foreground border-none">{item.category}</Badge>
                    </div>
                    {item.condition && (
                      <div className="absolute bottom-2 left-2">
                        <Badge variant="secondary" className="rounded-none text-[10px]">{item.condition}</Badge>
                      </div>
                    )}
                  </div>
                  <div className="p-3 space-y-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{item.master_kit?.club}</h3>
                    <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                      {item.master_kit?.season} - {item.version?.model}
                    </p>
                    <div className="flex items-center justify-between">
                      {item.size && <span className="font-mono text-[10px] text-muted-foreground">{item.size}</span>}
                      {item.value_estimate > 0 && <span className="font-mono text-xs text-accent">${item.value_estimate}</span>}
                    </div>
                  </div>
                </Link>
                <div className="absolute top-2 left-2 flex gap-1 opacity-0 group-hover:opacity-100" style={{ transition: 'opacity 0.2s ease' }}>
                  <button onClick={() => startEdit(item)} className="p-1.5 bg-card/90 border border-border text-muted-foreground hover:text-foreground" data-testid={`edit-collection-${item.collection_id}`}>
                    <Edit2 className="w-3 h-3" />
                  </button>
                  <button onClick={() => handleRemove(item.collection_id)} className="p-1.5 bg-destructive/90 text-destructive-foreground" data-testid={`remove-collection-${item.collection_id}`}>
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2 stagger-children" data-testid="collection-list">
            {items.map(item => (
              <div key={item.collection_id} data-testid={`collection-list-item-${item.collection_id}`}>
                {editingId === item.collection_id ? (
                  <div className="border border-primary/30 p-4 bg-card space-y-3" data-testid={`edit-form-${item.collection_id}`}>
                    <div className="flex items-center gap-3 mb-2">
                      <img src={item.version?.front_photo || item.master_kit?.front_photo} alt="" className="w-12 h-16 object-cover" />
                      <div>
                        <h4 className="text-sm font-semibold">{item.master_kit?.club}</h4>
                        <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season}</p>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="space-y-1">
                        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Condition</Label>
                        <Select value={editForm.condition || "none"} onValueChange={v => setEditForm(p => ({...p, condition: v === "none" ? "" : v}))}>
                          <SelectTrigger className="bg-card border-border rounded-none h-8 text-xs"><SelectValue placeholder="Select" /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            <SelectItem value="none">None</SelectItem>
                            {CONDITIONS.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Size</Label>
                        <Select value={editForm.size || "none"} onValueChange={v => setEditForm(p => ({...p, size: v === "none" ? "" : v}))}>
                          <SelectTrigger className="bg-card border-border rounded-none h-8 text-xs"><SelectValue placeholder="Select" /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            <SelectItem value="none">None</SelectItem>
                            {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Value ($)</Label>
                        <Input type="number" value={editForm.value_estimate} onChange={e => setEditForm(p => ({...p, value_estimate: e.target.value}))} className="bg-card border-border rounded-none h-8 text-xs font-mono" />
                      </div>
                      <div className="space-y-1">
                        <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Category</Label>
                        <Input value={editForm.category} onChange={e => setEditForm(p => ({...p, category: e.target.value}))} className="bg-card border-border rounded-none h-8 text-xs" />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <Label className="text-[10px] uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Notes</Label>
                      <Textarea value={editForm.notes} onChange={e => setEditForm(p => ({...p, notes: e.target.value}))} className="bg-card border-border rounded-none min-h-[50px] text-xs" />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => saveEdit(item.collection_id)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 h-7 text-xs">
                        <Check className="w-3 h-3 mr-1" /> Save
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setEditingId(null)} className="rounded-none h-7 text-xs">
                        <X className="w-3 h-3 mr-1" /> Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-4 p-3 border border-border bg-card group">
                    <Link to={`/version/${item.version_id}`} className="flex items-center gap-4 flex-1 min-w-0">
                      <img src={item.version?.front_photo || item.master_kit?.front_photo} alt="" className="w-14 h-18 object-cover" />
                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold truncate">{item.master_kit?.club}</h3>
                        <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          {item.master_kit?.season} - {item.version?.competition}
                        </p>
                        {item.notes && <p className="text-[10px] text-muted-foreground mt-0.5 truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.notes}</p>}
                      </div>
                    </Link>
                    <Badge variant="outline" className="rounded-none text-[10px] shrink-0">{item.version?.model}</Badge>
                    {item.condition && <Badge variant="secondary" className="rounded-none text-[10px] shrink-0">{item.condition}</Badge>}
                    {item.size && <span className="font-mono text-[10px] text-muted-foreground shrink-0">{item.size}</span>}
                    {item.value_estimate > 0 && <span className="font-mono text-xs text-accent shrink-0">${item.value_estimate}</span>}
                    <Badge variant="secondary" className="rounded-none text-[10px] shrink-0">{item.category}</Badge>
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 shrink-0" style={{ transition: 'opacity 0.2s ease' }}>
                      <button onClick={() => startEdit(item)} className="p-1.5 text-muted-foreground hover:text-foreground" data-testid={`edit-list-${item.collection_id}`}>
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button onClick={() => handleRemove(item.collection_id)} className="p-1.5 text-muted-foreground hover:text-destructive" style={{ transition: 'color 0.2s ease' }} data-testid={`remove-list-${item.collection_id}`}>
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
