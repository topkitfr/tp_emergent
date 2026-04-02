import React, { useState, useEffect, useRef, useCallback } from "react";
import { Link } from 'react-router-dom';
import {
  getMyCollection,
  getCollectionCategories,
  removeFromCollection,
  updateCollectionItem,
  getCollectionStats,
  getCategoryStats,
  proxyImageUrl,
  createPlayerPending,
  getPlayerAura,
  getUserLists,
  createList,
  updateList,
  deleteList,
  addItemToList,
  removeItemFromList,
} from '@/lib/api';
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
import {
  Shirt,
  LayoutGrid,
  List,
  Trash2,
  FolderOpen,
  Edit2,
  Check,
  TrendingUp,
  TrendingDown,
  Minus,
  Star,
  Plus,
  BookMarked,
  X,
  ChevronRight,
  ArrowLeft,
  MoreHorizontal,
  Pencil,
} from 'lucide-react';
import EstimationBreakdown from '@/components/EstimationBreakdown';
import { calculateEstimation } from '@/utils/estimation';
import EntityAutocomplete from '@/components/EntityAutocomplete';

const CONDITION_ORIGINS = ['Club Stock', 'Match Prepared', 'Match Worn', 'Training', 'Shop'];
const PHYSICAL_STATES = ['New with tag', 'Very good', 'Used', 'Damaged', 'Needs restoration'];
const FLOCKING_TYPES = ['Name+Number', 'Name', 'Number'];
const FLOCKING_ORIGINS = ['Official', 'Personalized'];
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '3XL'];
const SIGNED_TYPES = [
  { value: 'player_flocked', label: 'Signed by flocked player' },
  { value: 'team',           label: 'Signed by the team' },
  { value: 'other',          label: 'Other (specify)' },
];
const PROOF_LEVELS = [
  { value: 'none',   label: 'No proof' },
  { value: 'light',  label: 'Light certificate' },
  { value: 'strong', label: 'Solid proof (COA)' },
];
const PLAYER_PROFILES = [
  { value: 'legend', label: 'Football Legend' },
  { value: 'star',   label: 'Club Star' },
  { value: 'none',   label: 'Standard player' },
];

const fieldLabel = 'text-xs uppercase tracking-wider';
const fieldStyle = { fontFamily: 'Barlow Condensed' };
const inputClass = 'bg-card border-border rounded-none';

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
  const [lists, setLists] = useState([]);
  const [activeListId, setActiveListId] = useState(null);
  const [showCreateList, setShowCreateList] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newListColor, setNewListColor] = useState('#6366f1');
  const [creatingList, setCreatingList] = useState(false);
  const [editingListId, setEditingListId] = useState(null);
  const [editingListName, setEditingListName] = useState('');
  const [addToListItem, setAddToListItem] = useState(null);
  const [detailItem, setDetailItem] = useState(null);
  const [editForm, setEditForm] = useState({});

  const fetchCollection = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      const [colRes, statsRes, catStatsRes] = await Promise.all([
        getMyCollection(params),
        getCollectionStats(),
        getCategoryStats(),
      ]);
      setItems(colRes.data);
      setStats(statsRes.data);
      setCategoryStats(catStatsRes.data);
    } catch {
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  const fetchLists = useCallback(async () => {
    try {
      const r = await getUserLists();
      setLists(r.data ?? []);
    } catch {}
  }, []);

  useEffect(() => {
    fetchCollection();
    fetchLists();
    getCollectionCategories().then(r => setCategories(r.data)).catch(() => {});
  }, [fetchCollection, fetchLists]);

  const handleCreateList = async () => {
    if (!newListName.trim()) return;
    setCreatingList(true);
    try {
      const r = await createList({ name: newListName.trim(), color: newListColor });
      setLists(prev => [...prev, r.data]);
      setNewListName('');
      setShowCreateList(false);
      toast.success(`Liste "${r.data.name}" créée`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erreur lors de la création');
    } finally {
      setCreatingList(false);
    }
  };

  const handleDeleteList = async (listId) => {
    try {
      await deleteList(listId);
      setLists(prev => prev.filter(l => l.list_id !== listId));
      if (activeListId === listId) setActiveListId(null);
      toast.success('Liste supprimée');
    } catch { toast.error('Erreur'); }
  };

  const handleRenameList = async (listId) => {
    if (!editingListName.trim()) return;
    try {
      const r = await updateList(listId, { name: editingListName.trim() });
      setLists(prev => prev.map(l => l.list_id === listId ? { ...l, name: r.data.name } : l));
      setEditingListId(null);
      toast.success('Liste renommée');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Erreur');
    }
  };

  const handleAddToList = async (listId) => {
    if (!addToListItem) return;
    try {
      await addItemToList(listId, addToListItem);
      await fetchLists();
      setAddToListItem(null);
      toast.success('Ajouté à la liste');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Déjà dans la liste');
    }
  };

  const handleRemoveFromList = async (listId, collectionId) => {
    try {
      await removeItemFromList(listId, collectionId);
      await fetchLists();
      toast.success('Retiré de la liste');
    } catch { toast.error('Erreur'); }
  };

  const activeList = lists.find(l => l.list_id === activeListId);
  const displayedItems = activeListId && activeList
    ? items.filter(it => (activeList.collection_ids || []).includes(it.collection_id))
    : items;

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

  // ─── openDetail ───────────────────────────────────────────────────────────
  const openDetail = (item) => {
    setDetailItem(item);
    setEditForm({
      flocking_type:       item.flocking_type      || '',
      flocking_origin:     item.flocking_origin    || '',
      flocking_detail:     item.flocking_detail    || item.printing || '',
      flocking_player_id:  item.flocking_player_id || '',
      condition_origin:    item.condition_origin   || '',
      physical_state:      item.physical_state     || item.condition || '',
      size:                item.size               || '',
      purchase_cost:       item.purchase_cost      || '',
      // Signed — full advanced fields
      signed:              item.signed             || false,
      signed_type:         item.signed_type        || '',
      player_profile:      item.player_profile     || 'none',
      signed_by:           item.signed_by          || '',
      signed_by_player_id: item.signed_by_player_id || '',
      signed_proof_level:  item.signed_proof_level
                             ? item.signed_proof_level
                             : item.signed_proof ? 'light' : 'none',
      // Advanced extras
      has_patch:           item.has_patch          || false,
      is_rare:             item.is_rare            || false,
      rare_reason:         item.rare_reason        || '',
      // Always
      notes:               item.notes              || '',
      category:            item.category           || 'General',
    });
  };

  // ─── saveEdit ───────────────────────────────────────────────────────────────
  const saveEdit = async () => {
    if (!detailItem) return;
    try {
      let resolvedFlockingPlayerId = editForm.flocking_player_id;
      let resolvedSignedByPlayerId = editForm.signed_by_player_id;

      if (editForm.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const res = await createPlayerPending({ full_name: editForm.flocking_detail });
          resolvedFlockingPlayerId = res.data?.player_id;
          toast.info(`Player "${editForm.flocking_detail}" created (for review)`);
        } catch (e) { console.warn('createPlayerPending (flocking) failed:', e); }
      }

      if (editForm.signed && editForm.signed_by && !resolvedSignedByPlayerId &&
          (editForm.signed_type === 'player_flocked' || editForm.signed_type === 'other')) {
        try {
          const res = await createPlayerPending({ full_name: editForm.signed_by });
          resolvedSignedByPlayerId = res.data?.player_id;
          toast.info(`Player "${editForm.signed_by}" created (for review)`);
        } catch (e) { console.warn('createPlayerPending (signed_by) failed:', e); }
      }

      const mk = detailItem.master_kit;
      const seasonYear = parseSeasonYear(mk?.season);
      const est = calculateEstimation({
        mode: 'advanced',
        modelType:        detailItem.version?.model       || 'Replica',
        competition:      detailItem.version?.competition || '',
        conditionOrigin:  editForm.condition_origin       || '',
        physicalState:    editForm.physical_state         || '',
        flockingOrigin:   editForm.flocking_origin        || 'None',
        hasPatch:         editForm.has_patch              || false,
        signed:           editForm.signed                 || false,
        signedType:       editForm.signed_type            || '',
        playerProfile:    editForm.player_profile         || 'none',
        signedProofLevel: editForm.signed_proof_level     || 'none',
        isRare:           editForm.is_rare                || false,
        seasonYear,
      });

      const data = {
        flocking_type:       editForm.flocking_type,
        flocking_origin:     editForm.flocking_origin,
        flocking_detail:     editForm.flocking_detail,
        flocking_player_id:  resolvedFlockingPlayerId || '',
        condition_origin:    editForm.condition_origin,
        physical_state:      editForm.physical_state,
        size:                editForm.size,
        purchase_cost:       editForm.purchase_cost ? parseFloat(editForm.purchase_cost) : null,
        signed:              editForm.signed,
        signed_type:         editForm.signed_type,
        player_profile:      editForm.player_profile,
        signed_by:           editForm.signed_by,
        signed_by_player_id: resolvedSignedByPlayerId || '',
        signed_proof:        editForm.signed_proof_level !== 'none',
        signed_proof_level:  editForm.signed_proof_level,
        has_patch:           editForm.has_patch,
        is_rare:             editForm.is_rare,
        rare_reason:         editForm.rare_reason,
        notes:               editForm.notes,
        category:            editForm.category,
        estimated_price:     est.estimatedPrice,
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

  const getEstimatedPrice = (item) => (item.estimated_price ? item.estimated_price : null);

  const setField = (field, value) => setEditForm(prev => ({ ...prev, [field]: value }));

  return (
    <div className="animate-fade-in-up">
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl sm:text-4xl tracking-tighter mb-2" data-testid="collection-title">MY COLLECTION</h1>
          <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
            {items.length} jerseys in your locker room{activeList ? ` — ${activeList.name}` : ''}
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

          <div className="mb-6" data-testid="my-lists">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground" style={fieldStyle}>
                <BookMarked className="w-3.5 h-3.5 inline mr-1" /> MES LISTES
              </h3>
              <button onClick={() => setShowCreateList(v => !v)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors" style={fieldStyle} data-testid="create-list-btn">
                <Plus className="w-3.5 h-3.5" /> Nouvelle liste
              </button>
            </div>

            {showCreateList && (
              <div className="flex items-center gap-2 mb-3 p-3 border border-primary/30 bg-primary/5">
                <input type="color" value={newListColor} onChange={e => setNewListColor(e.target.value)} className="w-7 h-7 rounded cursor-pointer border-0 bg-transparent" title="Couleur" />
                <Input value={newListName} onChange={e => setNewListName(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleCreateList()} placeholder="Nom de la liste (ex: Vintage 90, World Cup...)" className="bg-card border-border rounded-none flex-1 h-8 text-xs" autoFocus data-testid="new-list-name-input" />
                <Button onClick={handleCreateList} disabled={creatingList || !newListName.trim()} className="rounded-none h-8 px-3 text-xs bg-primary text-primary-foreground" data-testid="confirm-create-list-btn"><Check className="w-3.5 h-3.5" /></Button>
                <Button variant="outline" onClick={() => { setShowCreateList(false); setNewListName(''); }} className="rounded-none h-8 px-3 text-xs"><X className="w-3.5 h-3.5" /></Button>
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <button onClick={() => setActiveListId(null)} className={`flex items-center gap-1.5 border px-3 py-1.5 text-xs transition-colors ${!activeListId ? 'border-primary bg-primary/5 text-primary' : 'border-border text-muted-foreground hover:border-primary/40'}`} style={fieldStyle} data-testid="list-all-btn">
                <Shirt className="w-3 h-3" /> Toute la collection
                <span className="font-mono ml-1 opacity-60">{items.length}</span>
              </button>
              {lists.map(lst => (
                <div key={lst.list_id} className="relative group/chip">
                  {editingListId === lst.list_id ? (
                    <div className="flex items-center gap-1">
                      <Input value={editingListName} onChange={e => setEditingListName(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') handleRenameList(lst.list_id); if (e.key === 'Escape') setEditingListId(null); }} className="bg-card border-border rounded-none h-7 text-xs w-36" autoFocus />
                      <button onClick={() => handleRenameList(lst.list_id)} className="p-1 text-primary hover:text-primary/80"><Check className="w-3.5 h-3.5" /></button>
                      <button onClick={() => setEditingListId(null)} className="p-1 text-muted-foreground hover:text-foreground"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  ) : (
                    <button onClick={() => setActiveListId(activeListId === lst.list_id ? null : lst.list_id)}
                      className={`flex items-center gap-1.5 border px-3 py-1.5 text-xs transition-colors ${activeListId === lst.list_id ? 'text-white' : 'border-border text-muted-foreground hover:border-primary/40'}`}
                      style={{ ...fieldStyle, borderColor: activeListId === lst.list_id ? (lst.color || '#6366f1') : undefined, backgroundColor: activeListId === lst.list_id ? (lst.color || '#6366f1') + '22' : undefined, color: activeListId === lst.list_id ? (lst.color || '#6366f1') : undefined }}
                      data-testid={`list-chip-${lst.list_id}`}>
                      <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: lst.color || '#6366f1' }} />
                      {lst.name}
                      <span className="font-mono opacity-60">{lst.item_count}</span>
                      <span className="hidden group-hover/chip:flex items-center gap-0.5 ml-1">
                        <span onClick={e => { e.stopPropagation(); setEditingListId(lst.list_id); setEditingListName(lst.name); }} className="p-0.5 hover:text-foreground" title="Renommer"><Pencil className="w-3 h-3" /></span>
                        <span onClick={e => { e.stopPropagation(); handleDeleteList(lst.list_id); }} className="p-0.5 hover:text-destructive" title="Supprimer"><Trash2 className="w-3 h-3" /></span>
                      </span>
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {categories.length > 0 && !categoryStats.length && (
              <Select value={selectedCategory || 'all'} onValueChange={(v) => setSelectedCategory(v === 'all' ? '' : v)}>
                <SelectTrigger className="bg-card border-border rounded-none w-48" data-testid="collection-category-filter"><SelectValue placeholder="All Categories" /></SelectTrigger>
                <SelectContent className="bg-card border-border">
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}
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
        ) : displayedItems.length === 0 ? (
          <div className="text-center py-20" data-testid="empty-collection">
            <FolderOpen className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-2xl tracking-tight mb-2">LOCKER ROOM IS EMPTY</h3>
            <p className="text-sm text-muted-foreground mb-6" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Start building your collection by browsing the catalog</p>
            <Link to="/browse"><Button className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="browse-catalog-btn">Browse Catalog</Button></Link>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children" data-testid="collection-grid">
            {displayedItems.map((item) => (
              <div key={item.collection_id} className="card-shimmer relative border border-border bg-card overflow-hidden group" data-testid={`collection-item-${item.collection_id}`}>
                <Link to={`/version/${item.version_id}`}>
                  <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
                    <img
                      src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)}
                      alt={item.master_kit?.club}
                      className="w-full h-full object-cover group-hover:scale-105"
                      style={{ transition: 'transform 0.5s ease' }}
                    />
                    {getConditionLabel(item) && <div className="absolute bottom-2 left-2"><Badge variant="secondary" className="rounded-none text-[10px]">{getConditionLabel(item)}</Badge></div>}
                    {item.signed && <div className="absolute bottom-2 right-2"><Badge className="rounded-none text-[10px] bg-accent/90 text-accent-foreground border-none">Signed</Badge></div>}
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
                  {activeListId ? (
                    <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleRemoveFromList(activeListId, item.collection_id); }} className="p-1.5 bg-card/90 border border-primary/40 text-primary hover:text-destructive" title="Retirer de la liste" data-testid={`remove-from-list-${item.collection_id}`}><X className="w-3 h-3" /></button>
                  ) : (
                    <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); setAddToListItem(item.collection_id); }} className="p-1.5 bg-card/90 border border-border text-muted-foreground hover:text-primary" title="Ajouter à une liste" data-testid={`add-to-list-${item.collection_id}`}><BookMarked className="w-3 h-3" /></button>
                  )}
                  <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleRemove(item.collection_id); }} className="p-1.5 bg-destructive/90 text-destructive-foreground" data-testid={`remove-collection-${item.collection_id}`}><Trash2 className="w-3 h-3" /></button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2 stagger-children" data-testid="collection-list">
            {displayedItems.map((item) => (
              <div key={item.collection_id} className="flex items-center gap-4 p-3 border border-border bg-card group" data-testid={`collection-list-item-${item.collection_id}`}>
                <Link to={`/version/${item.version_id}`} className="flex items-center gap-4 flex-1 min-w-0">
                  <img
                    src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)}
                    alt=""
                    className="w-14 h-18 object-cover"
                  />
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

      {/* ══ EDIT ITEM SHEET ══ */}
      <Sheet open={!!detailItem} onOpenChange={(open) => { if (!open) setDetailItem(null); }}>
        <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto" data-testid="item-detail-sheet">
          {detailItem && (
            <>
              <SheetHeader className="mb-6">
                <SheetTitle className="text-left tracking-tighter" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>EDIT ITEM</SheetTitle>
              </SheetHeader>

              {/* Apercu */}
              <div className="mb-6">
                <div className="flex gap-4 mb-4">
                  <img
                    src={proxyImageUrl(detailItem.version?.front_photo || detailItem.master_kit?.front_photo)}
                    alt={detailItem.master_kit?.club}
                    className="w-20 h-28 object-cover border border-border"
                  />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{detailItem.master_kit?.club}</h3>
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{detailItem.master_kit?.season} - {detailItem.master_kit?.kit_type}</p>
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{detailItem.master_kit?.brand}</p>
                    <div className="flex gap-2 mt-2">
                      <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.model || 'None'}</Badge>
                      <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.competition || 'None'}</Badge>
                    </div>
                  </div>
                </div>
                <div className="h-px bg-border" />
              </div>

              {/* Form */}
              <div className="space-y-4">

                {/* Flocking */}
                <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>Flocking</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Origin</Label>
                    <Select value={editForm.flocking_origin || 'none'} onValueChange={v => {
                      setField('flocking_origin', v === 'none' ? '' : v);
                      if (v !== 'Official') { setField('flocking_detail', ''); setField('flocking_player_id', ''); }
                    }}>
                      <SelectTrigger className={inputClass}><SelectValue placeholder="None" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {FLOCKING_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Type</Label>
                    <Select value={editForm.flocking_type || 'none'} onValueChange={v => setField('flocking_type', v === 'none' ? '' : v)}>
                      <SelectTrigger className={inputClass}><SelectValue placeholder="None" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">None</SelectItem>
                        {FLOCKING_TYPES.map(t => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {editForm.flocking_origin === 'Official' && (
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Flocked Player</Label>
                    <EntityAutocomplete
                      entityType="player"
                      value={editForm.flocking_detail}
                      onChange={val => setField('flocking_detail', val)}
                      onSelect={item => { setField('flocking_detail', item.label); setField('flocking_player_id', item.id); }}
                      placeholder="e.g. Ronaldo 7"
                      className={inputClass}
                    />
                  </div>
                )}

                {/* Origin + State */}
                <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>Condition</p>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Origin</Label>
                    <Select value={editForm.condition_origin || 'none'} onValueChange={v => setField('condition_origin', v === 'none' ? '' : v)}>
                      <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">—</SelectItem>
                        {CONDITION_ORIGINS.map(o => <SelectItem key={o} value={o}>{o}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Physical State</Label>
                    <Select value={editForm.physical_state || 'none'} onValueChange={v => setField('physical_state', v === 'none' ? '' : v)}>
                      <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">—</SelectItem>
                        {PHYSICAL_STATES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Size + Purchase Cost */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Size</Label>
                    <Select value={editForm.size || 'none'} onValueChange={v => setField('size', v === 'none' ? '' : v)}>
                      <SelectTrigger className={inputClass}><SelectValue placeholder="—" /></SelectTrigger>
                      <SelectContent className="bg-card border-border">
                        <SelectItem value="none">—</SelectItem>
                        {SIZES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Purchase Cost (€)</Label>
                    <input
                      type="number"
                      value={editForm.purchase_cost}
                      onChange={e => setField('purchase_cost', e.target.value)}
                      placeholder="0"
                      className={`${inputClass} border px-3 py-2 text-sm w-full`}
                    />
                  </div>
                </div>

                {/* Patch + Rare */}
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <Switch checked={editForm.has_patch || false} onCheckedChange={v => setField('has_patch', v)} />
                    <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fieldStyle}>Official Patch</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch checked={editForm.is_rare || false} onCheckedChange={v => setField('is_rare', v)} />
                    <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fieldStyle}>Rare Jersey</Label>
                  </div>
                </div>

                {editForm.is_rare && (
                  <div className="space-y-1">
                    <Label className={fieldLabel} style={fieldStyle}>Why rare?</Label>
                    <input
                      type="text"
                      value={editForm.rare_reason || ''}
                      onChange={e => setField('rare_reason', e.target.value)}
                      placeholder="Ex: limited edition, printing error..."
                      className={`${inputClass} border px-3 py-2 text-xs w-full`}
                    />
                  </div>
                )}

                {/* Signed */}
                <p className="text-[10px] uppercase tracking-wider text-primary/60" style={fieldStyle}>Signature</p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Switch checked={editForm.signed || false} onCheckedChange={v => {
                      setField('signed', v);
                      if (!v) {
                        setField('signed_type', '');
                        setField('player_profile', 'none');
                        setField('signed_by', '');
                        setField('signed_by_player_id', '');
                        setField('signed_proof_level', 'none');
                      }
                    }} />
                    <Label className="text-[11px] uppercase tracking-wider cursor-pointer" style={fieldStyle}>Signed</Label>
                  </div>

                  {editForm.signed && (
                    <div className="space-y-3 pl-2 border-l-2 border-primary/30 ml-1">
                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fieldStyle}>Signed by</Label>
                        <Select value={editForm.signed_type || 'none'} onValueChange={v => {
                          setField('signed_type', v === 'none' ? '' : v);
                          setField('player_profile', 'none');
                          setField('signed_by', '');
                          setField('signed_by_player_id', '');
                        }}>
                          <SelectTrigger className={inputClass}><SelectValue placeholder="Select..." /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            <SelectItem value="none">—</SelectItem>
                            {SIGNED_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>

                      {(editForm.signed_type === 'player_flocked' || editForm.signed_type === 'other') && (
                        <div className="space-y-1">
                          <Label className={fieldLabel} style={fieldStyle}>
                            {editForm.signed_type === 'player_flocked' ? 'Flocked player (signed)' : 'Specify'}
                          </Label>
                          <EntityAutocomplete
                            entityType="player"
                            value={editForm.signed_by}
                            onChange={val => setField('signed_by', val)}
                            onSelect={item => { setField('signed_by', item.label); setField('signed_by_player_id', item.id || ''); }}
                            placeholder="e.g. Maldini"
                            className={inputClass}
                          />
                        </div>
                      )}

                      {editForm.signed_type === 'player_flocked' && (
                        <div className="space-y-1">
                          <Label className={fieldLabel} style={fieldStyle}>Player Profile</Label>
                          <Select value={editForm.player_profile || 'none'} onValueChange={v => setField('player_profile', v)}>
                            <SelectTrigger className={inputClass}><SelectValue /></SelectTrigger>
                            <SelectContent className="bg-card border-border">
                              {PLAYER_PROFILES.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      <div className="space-y-1">
                        <Label className={fieldLabel} style={fieldStyle}>Proof / Certificate</Label>
                        <Select value={editForm.signed_proof_level || 'none'} onValueChange={v => setField('signed_proof_level', v)}>
                          <SelectTrigger className={inputClass}><SelectValue /></SelectTrigger>
                          <SelectContent className="bg-card border-border">
                            {PROOF_LEVELS.map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}
                </div>

                {/* Notes */}
                <div className="space-y-1">
                  <Label className={fieldLabel} style={fieldStyle}>Notes</Label>
                  <Textarea
                    value={editForm.notes || ''}
                    onChange={e => setField('notes', e.target.value)}
                    placeholder="Any notes, details, context..."
                    className="bg-card border-border rounded-none min-h-[70px]"
                  />
                </div>

                {/* Estimation */}
                <EstimationBreakdown
                  mode="advanced"
                  modelType={detailItem.version?.model || 'Replica'}
                  competition={detailItem.version?.competition || ''}
                  conditionOrigin={editForm.condition_origin || ''}
                  physicalState={editForm.physical_state || ''}
                  flockingOrigin={editForm.flocking_origin || 'None'}
                  hasPatch={editForm.has_patch || false}
                  signed={editForm.signed || false}
                  signedType={editForm.signed_type || ''}
                  playerProfile={editForm.player_profile || 'none'}
                  signedProofLevel={editForm.signed_proof_level || 'none'}
                  isRare={editForm.is_rare || false}
                  seasonYear={parseSeasonYear(detailItem.master_kit?.season)}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2 mt-6">
                <Button onClick={saveEdit} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 flex-1">Save</Button>
                <Button variant="outline" onClick={() => setDetailItem(null)} className="rounded-none">Cancel</Button>
                <Button variant="ghost" onClick={() => handleRemove(detailItem.collection_id)} className="rounded-none text-destructive hover:text-destructive px-3"><Trash2 className="w-4 h-4" /></Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      {/* Add to list mini-panel */}
      {addToListItem && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={() => setAddToListItem(null)}>
          <div className="bg-card border border-border w-full max-w-sm p-4 mb-4 mx-4" onClick={e => e.stopPropagation()}>
            <p className="text-xs uppercase tracking-wider mb-3" style={fieldStyle}>Add to list</p>
            {lists.length === 0 ? (
              <p className="text-xs text-muted-foreground">No lists yet. Create one first.</p>
            ) : (
              <div className="space-y-2">
                {lists.map(lst => (
                  <button key={lst.list_id} onClick={() => handleAddToList(lst.list_id)} className="flex items-center gap-2 w-full text-left text-xs p-2 hover:bg-secondary transition-colors">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: lst.color || '#6366f1' }} />
                    {lst.name}
                  </button>
                ))}
              </div>
            )}
            <Button variant="outline" onClick={() => setAddToListItem(null)} className="rounded-none w-full mt-3 text-xs h-8">Cancel</Button>
          </div>
        </div>
      )}
    </div>
  );
}
