import React, { useState, useCallback, useEffect } from "react";
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
  getUserLists,
  createList,
  updateList,
  deleteList,
  addItemToList,
  removeItemFromList,
  createListing,
  getMyListings,
  cancelListing,
  estimatePrice,
} from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { toast } from 'sonner';
import {
  Shirt, LayoutGrid, List, Trash2, FolderOpen, Edit2,
  Check, TrendingUp, TrendingDown, Minus, Plus,
  BookMarked, X, Pencil, Loader2, Tag,
} from 'lucide-react';
import { calculateEstimation } from '@/utils/estimation';
import CollectionItemForm, {
  INITIAL_FORM_STATE,
  formFromItem,
  formToPayload,
} from '@/components/CollectionItemForm';

// ─── helpers ────────────────────────────────────────────────────────────────
const fieldStyle = { fontFamily: 'Barlow Condensed' };

function parseSeasonYear(season) {
  if (!season) return 0;
  const m = season.match(/(\d{4})/);
  return m ? parseInt(m[1]) : 0;
}

function getFlockingLabel(item) {
  const detail = item.flocking_detail || item.printing;
  if (!detail) return null;
  return item.flocking_origin ? `${detail} (${item.flocking_origin})` : detail;
}

function getConditionLabel(item) {
  const parts = [];
  if (item.condition_origin) parts.push(item.condition_origin);
  if (item.physical_state || item.condition) parts.push(item.physical_state || item.condition);
  return parts.join(' / ') || null;
}

/** Normalise un detail FastAPI/Pydantic en string lisible */
function normalizeDetail(detail) {
  if (!detail) return null;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map(d => d?.msg || d?.message || JSON.stringify(d)).join(' · ');
  }
  if (typeof detail === 'object') return detail.msg || detail.message || JSON.stringify(detail);
  return String(detail);
}

// ─── composant ──────────────────────────────────────────────────────────────
export default function MyCollection() {
  const { user } = useAuth();

  // collection
  const [items,          setItems]          = useState([]);
  const [categories,     setCategories]     = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode,       setViewMode]       = useState('grid');
  const [loading,        setLoading]        = useState(true);
  const [stats,          setStats]          = useState(null);
  const [categoryStats,  setCategoryStats]  = useState([]);

  // listes
  const [lists,          setLists]          = useState([]);
  const [activeListId,   setActiveListId]   = useState(null);
  const [showCreateList, setShowCreateList] = useState(false);
  const [newListName,    setNewListName]    = useState('');
  const [newListColor,   setNewListColor]   = useState('#6366f1');
  const [creatingList,   setCreatingList]   = useState(false);
  const [editingListId,  setEditingListId]  = useState(null);
  const [editingListName,setEditingListName]= useState('');
  const [addToListItem,  setAddToListItem]  = useState(null);

  // listing
  const [listingItem,    setListingItem]    = useState(null);
  const [listingForm,    setListingForm]    = useState({ listing_type: 'sale', asking_price: '', trade_for: '' });
  const [listingLoading, setListingLoading] = useState(false);
  const [myListedIds,    setMyListedIds]    = useState(new Set());
  const [myListings,     setMyListings]     = useState([]);

  // edit sheet ─ UNIFIÉ
  const [detailItem, setDetailItem] = useState(null);
  const [editForm,   setEditForm]   = useState(INITIAL_FORM_STATE);
  const [editMode,   setEditMode]   = useState('basic');   // 'basic' | 'advanced'
  const [saving,     setSaving]     = useState(false);

  // ─── fetch ────────────────────────────────────────────────────────────────
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
    } catch {}
    finally { setLoading(false); }
  }, [selectedCategory]);

  const fetchLists = useCallback(async () => {
    try { const r = await getUserLists(); setLists(r.data ?? []); } catch {}
  }, []);

  useEffect(() => {
    fetchCollection();
    fetchLists();
    getCollectionCategories().then(r => setCategories(r.data)).catch(() => {});
    getMyListings()
      .then(r => {
        const all = r.data || [];
        const active = all.filter(l => l.status === 'active');
        setMyListings(active);
        setMyListedIds(new Set(active.map(l => l.collection_id)));
      })
      .catch(() => {});
  }, [fetchCollection, fetchLists]);

  // ─── listes handlers ──────────────────────────────────────────────────────
  const handleCreateList = async () => {
    if (!newListName.trim()) return;
    setCreatingList(true);
    try {
      const r = await createList({ name: newListName.trim(), color: newListColor });
      setLists(prev => [...prev, r.data]);
      setNewListName('');
      setShowCreateList(false);
      toast.success(`Liste "${r.data.name}" créée`);
    } catch (e) { toast.error(normalizeDetail(e.response?.data?.detail) || 'Erreur'); }
    finally { setCreatingList(false); }
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
    } catch (e) { toast.error(normalizeDetail(e.response?.data?.detail) || 'Erreur'); }
  };

  const handleAddToList = async (listId) => {
    if (!addToListItem) return;
    try {
      await addItemToList(listId, addToListItem);
      await fetchLists();
      setAddToListItem(null);
      toast.success('Ajouté à la liste');
    } catch (e) { toast.error(normalizeDetail(e.response?.data?.detail) || 'Déjà dans la liste'); }
  };

  const handleRemoveFromList = async (listId, collectionId) => {
    try {
      await removeItemFromList(listId, collectionId);
      await fetchLists();
      toast.success('Retiré de la liste');
    } catch { toast.error('Erreur'); }
  };

  // ─── collection handlers ──────────────────────────────────────────────────
  const handleRemove = async (collectionId) => {
    try {
      await removeFromCollection(collectionId);
      toast.success('Removed from collection');
      setDetailItem(null);
      fetchCollection();
    } catch { toast.error('Failed to remove'); }
  };

  // ─── openDetail — hydrate le form depuis l'item existant ──────────────────
  const openDetail = (item) => {
    setDetailItem(item);
    setEditForm(formFromItem(item));
    // Si l'item a des champs avancés renseignés → ouvrir en mode advanced
    const hasAdvanced = item.condition_origin ||
      (Array.isArray(item.patches) && item.patches.length > 0) ||
      item.has_patch || item.signed || item.is_rare;
    setEditMode(hasAdvanced ? 'advanced' : 'basic');
  };

  // ─── saveEdit — identique à AddToCollectionDialog ─────────────────────────
  const saveEdit = async () => {
    if (!detailItem) return;
    setSaving(true);
    try {
      // Résoudre joueur flocqué
      let resolvedFlockingPlayerId = editForm.flocking_player_id;
      if (editForm.flocking_origin === 'Official' && editForm.flocking_detail && !resolvedFlockingPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: editForm.flocking_detail });
          resolvedFlockingPlayerId = r.data?.player_id;
        } catch {}
      }

      // Résoudre joueur signataire (type 'other')
      let resolvedSignedPlayerId = editForm.signed_player_id;
      if (editForm.signed && editForm.signed_type === 'other' && editForm.signed_other_text && !resolvedSignedPlayerId) {
        try {
          const r = await createPlayerPending({ full_name: editForm.signed_other_text });
          resolvedSignedPlayerId = r.data?.player_id;
        } catch {}
      }

      const seasonYear = parseSeasonYear(detailItem.master_kit?.season);
      const localEst = calculateEstimation({
        mode:             editMode,
        modelType:        detailItem.version?.model       || 'Replica',
        competition:      detailItem.version?.competition || '',
        conditionOrigin:  editForm.condition_origin,
        physicalState:    editForm.physical_state,
        flockingOrigin:   editForm.flocking_origin === 'none' ? 'None' : editForm.flocking_origin,
        patches:          editForm.patches,
        patchOtherText:   editForm.patch_other_text,
        signed:           editForm.signed,
        signedType:       editForm.signed_type,
        signedOtherText:  editForm.signed_other_text,
        playerProfile:    editForm.player_profile,
        signedProofLevel: editForm.signed_proof_level,
        isRare:           editForm.is_rare,
        rareReason:       editForm.rare_reason,
        seasonYear,
      });
      const estRes = await estimatePrice({
        model_type:          detailItem.version?.model || 'Replica',
        competition:         detailItem.version?.competition || '',
        condition_origin:    editForm.condition_origin || '',
        physical_state:      editForm.physical_state || '',
        flocking_origin:     editForm.flocking_origin === 'none' ? 'None' : (editForm.flocking_origin || ''),
        flocking_player_id:  resolvedFlockingPlayerId || '',
        signed:              editForm.signed || false,
        signed_type:         editForm.signed_type || '',
        signed_other_detail: editForm.signed_other_text || '',
        signed_proof:        editForm.signed_proof_level || 'none',
        season_year:         seasonYear,
        patch:               (editForm.patches?.length > 0) || !!editForm.patch_other_text,
        is_rare:             editForm.is_rare || false,
        rare_reason:         editForm.rare_reason || '',
        mode:                editMode,
      }).catch(() => ({ data: localEst }));
      const estimation = estRes.data || localEst;

      const payload = formToPayload(
        { ...editForm, flocking_player_id: resolvedFlockingPlayerId, signed_player_id: resolvedSignedPlayerId },
        estimation,
      );

      await updateCollectionItem(detailItem.collection_id, payload);
      toast.success('Item updated');
      setDetailItem(null);
      fetchCollection();
    } catch (err) {
      const detail = normalizeDetail(err?.response?.data?.detail);
      toast.error(detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  // ─── listing handler ─────────────────────────────────────────────────────
  const handleCreateListing = async () => {
    if (!listingItem) return;
    setListingLoading(true);
    try {
      const payload = {
        collection_id: listingItem.collection_id,
        listing_type: listingForm.listing_type,
      };
      if ((listingForm.listing_type === 'sale' || listingForm.listing_type === 'both') && listingForm.asking_price) {
        payload.asking_price = parseFloat(listingForm.asking_price);
      }
      if ((listingForm.listing_type === 'trade' || listingForm.listing_type === 'both') && listingForm.trade_for) {
        payload.trade_for = listingForm.trade_for;
      }
      const res = await createListing(payload);
      setMyListings(prev => [...prev, res.data]);
      setMyListedIds(prev => new Set([...prev, listingItem.collection_id]));
      toast.success('Annonce publiée !');
      setListingItem(null);
      setListingForm({ listing_type: 'sale', asking_price: '', trade_for: '' });
    } catch (e) {
      toast.error(normalizeDetail(e.response?.data?.detail) || 'Erreur lors de la publication');
    } finally {
      setListingLoading(false);
    }
  };

  const handleCancelListing = async (listingId, collectionId) => {
    if (!window.confirm('Annuler cette annonce ?')) return;
    try {
      await cancelListing(listingId);
      setMyListings(prev => prev.filter(l => l.listing_id !== listingId));
      setMyListedIds(prev => { const s = new Set(prev); s.delete(collectionId); return s; });
      toast.success('Annonce annulée.');
    } catch (e) {
      toast.error(normalizeDetail(e.response?.data?.detail) || 'Erreur');
    }
  };

  // ─── computed ─────────────────────────────────────────────────────────────
  const activeList     = lists.find(l => l.list_id === activeListId);
  const displayedItems = activeListId && activeList
    ? items.filter(it => (activeList.collection_ids || []).includes(it.collection_id))
    : items;

  // ─── render ───────────────────────────────────────────────────────────────
  return (
    <div className="animate-fade-in-up">
      {/* ── Header / Stats ── */}
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

          {/* ── Mes annonces actives ── */}
          {myListings.length > 0 && (
            <div className="mb-6" data-testid="my-listings">
              <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-3" style={fieldStyle}>
                <Tag className="w-3.5 h-3.5 inline mr-1" /> MES ANNONCES ({myListings.length})
              </h3>
              <div className="space-y-2">
                {myListings.map(l => {
                  const snap = l.kit_snapshot || {};
                  const typeLabel = { sale: 'Vente', trade: 'Échange', both: 'Vente/Échange' }[l.listing_type] || l.listing_type;
                  const typeCls   = { sale: 'bg-green-600', trade: 'bg-blue-600', both: 'bg-purple-600' }[l.listing_type] || 'bg-gray-500';
                  return (
                    <div key={l.listing_id} className="flex items-center gap-3 border border-border bg-card px-3 py-2 text-sm">
                      <span className={`text-[10px] text-white px-1.5 py-0.5 rounded font-semibold shrink-0 ${typeCls}`}>{typeLabel}</span>
                      <span className="flex-1 truncate text-xs">{snap.club || '—'} {snap.season ? `— ${snap.season}` : ''}</span>
                      {l.asking_price != null && <span className="font-mono text-xs text-accent shrink-0">{l.asking_price} €</span>}
                      {l.offer_count > 0 && (
                        <Badge className="text-[10px] bg-yellow-100 text-yellow-800 shrink-0">{l.offer_count} offre{l.offer_count > 1 ? 's' : ''}</Badge>
                      )}
                      <Link to={`/marketplace/${l.listing_id}`} className="text-xs text-muted-foreground hover:text-foreground shrink-0">Voir</Link>
                      <button onClick={() => handleCancelListing(l.listing_id, l.collection_id)} className="text-xs text-muted-foreground hover:text-destructive shrink-0" title="Annuler l'annonce"><X className="w-3.5 h-3.5" /></button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Listes ── */}
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
                <Input value={newListName} onChange={e => setNewListName(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleCreateList()} placeholder="Nom de la liste" className="bg-card border-border rounded-none flex-1 h-8 text-xs" autoFocus data-testid="new-list-name-input" />
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
                    <button
                      onClick={() => setActiveListId(activeListId === lst.list_id ? null : lst.list_id)}
                      className={`flex items-center gap-1.5 border px-3 py-1.5 text-xs transition-colors ${activeListId === lst.list_id ? 'text-white' : 'border-border text-muted-foreground hover:border-primary/40'}`}
                      style={{ ...fieldStyle, borderColor: activeListId === lst.list_id ? (lst.color || '#6366f1') : undefined, backgroundColor: activeListId === lst.list_id ? (lst.color || '#6366f1') + '22' : undefined, color: activeListId === lst.list_id ? (lst.color || '#6366f1') : undefined }}
                      data-testid={`list-chip-${lst.list_id}`}
                    >
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

          <div className="flex items-center gap-3">
            <div className="flex items-center border border-border ml-auto">
              <button onClick={() => setViewMode('grid')} className={`p-2 ${viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-grid"><LayoutGrid className="w-4 h-4" /></button>
              <button onClick={() => setViewMode('list')} className={`p-2 ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'}`} data-testid="collection-view-list"><List className="w-4 h-4" /></button>
            </div>
          </div>
        </div>
      </div>

      {/* ── Items grid / list ── */}
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
                <Link to={`/collection/${item.collection_id}`}>
                  <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
                    <img src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)} alt={item.master_kit?.club} className="w-full h-full object-cover group-hover:scale-105" style={{ transition: 'transform 0.5s ease' }} />
                    {getConditionLabel(item) && <div className="absolute bottom-2 left-2"><Badge variant="secondary" className="rounded-none text-[10px]">{getConditionLabel(item)}</Badge></div>}
                    {item.signed && <div className="absolute bottom-2 right-2"><Badge className="rounded-none text-[10px] bg-accent/90 text-accent-foreground border-none">Signed</Badge></div>}
                    {myListedIds.has(item.collection_id) && (
                      <span className="absolute top-2 right-2 text-[10px] bg-green-600 text-white px-1.5 py-0.5 rounded font-semibold z-10">EN VENTE</span>
                    )}
                  </div>
                  <div className="p-3 space-y-1">
                    <h3 className="text-sm font-semibold tracking-tight truncate" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{item.master_kit?.club}</h3>
                    <p className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season} - {item.version?.model}</p>
                    {getFlockingLabel(item) && <p className="text-xs text-primary/80 truncate" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{getFlockingLabel(item)}</p>}
                    <div className="flex items-center justify-between">
                      {item.size && <span className="font-mono text-[10px] text-muted-foreground">{item.size}</span>}
                      {item.estimated_price && <span className="font-mono text-xs text-accent">{item.estimated_price}&euro;</span>}
                    </div>
                  </div>
                </Link>
                <div className="absolute top-2 left-2 flex gap-1 opacity-0 group-hover:opacity-100" style={{ transition: 'opacity 0.2s ease' }}>
                  <button onClick={e => { e.preventDefault(); e.stopPropagation(); openDetail(item); }} className="p-1.5 bg-card/90 border border-border text-muted-foreground hover:text-foreground" data-testid={`edit-collection-${item.collection_id}`}><Edit2 className="w-3 h-3" /></button>
                  {activeListId ? (
                    <button onClick={e => { e.preventDefault(); e.stopPropagation(); handleRemoveFromList(activeListId, item.collection_id); }} className="p-1.5 bg-card/90 border border-primary/40 text-primary hover:text-destructive" title="Retirer de la liste" data-testid={`remove-from-list-${item.collection_id}`}><X className="w-3 h-3" /></button>
                  ) : (
                    <button onClick={e => { e.preventDefault(); e.stopPropagation(); setAddToListItem(item.collection_id); }} className="p-1.5 bg-card/90 border border-border text-muted-foreground hover:text-primary" title="Ajouter à une liste" data-testid={`add-to-list-${item.collection_id}`}><BookMarked className="w-3 h-3" /></button>
                  )}
                  {!myListedIds.has(item.collection_id) && (
                    <button onClick={e => { e.preventDefault(); e.stopPropagation(); setListingItem(item); }} className="p-1.5 bg-black/60 text-white hover:bg-primary/80 rounded" title="Mettre en vente" data-testid={`list-item-${item.collection_id}`}><Tag className="w-3 h-3" /></button>
                  )}
                  <button onClick={e => { e.preventDefault(); e.stopPropagation(); handleRemove(item.collection_id); }} className="p-1.5 bg-destructive/90 text-destructive-foreground" data-testid={`remove-collection-${item.collection_id}`}><Trash2 className="w-3 h-3" /></button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-2 stagger-children" data-testid="collection-list">
            {displayedItems.map((item) => (
              <div key={item.collection_id} className="flex items-center gap-4 p-3 border border-border bg-card group" data-testid={`collection-list-item-${item.collection_id}`}>
                <Link to={`/collection/${item.collection_id}`} className="flex items-center gap-4 flex-1 min-w-0">
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
                {item.estimated_price && <span className="font-mono text-xs text-accent shrink-0">{item.estimated_price}&euro;</span>}
                {item.signed && <Badge className="rounded-none text-[10px] bg-accent/90 shrink-0">Signed</Badge>}
                {myListedIds.has(item.collection_id) && (
                  <span className="text-[10px] bg-green-600 text-white px-1.5 py-0.5 rounded font-semibold shrink-0">EN VENTE</span>
                )}
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 shrink-0" style={{ transition: 'opacity 0.2s ease' }}>
                  <button onClick={() => openDetail(item)} className="p-1.5 text-muted-foreground hover:text-foreground" data-testid={`edit-list-${item.collection_id}`}><Edit2 className="w-4 h-4" /></button>
                  {!myListedIds.has(item.collection_id) && (
                    <button onClick={() => setListingItem(item)} className="p-1.5 text-muted-foreground hover:text-primary" title="Mettre en vente" data-testid={`list-item-list-${item.collection_id}`}><Tag className="w-4 h-4" /></button>
                  )}
                  <button onClick={() => handleRemove(item.collection_id)} className="p-1.5 text-muted-foreground hover:text-destructive" style={{ transition: 'color 0.2s ease' }} data-testid={`remove-list-${item.collection_id}`}><Trash2 className="w-4 h-4" /></button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ══ EDIT ITEM SHEET — formulaire unifié ══ */}
      <Sheet open={!!detailItem} onOpenChange={open => { if (!open) setDetailItem(null); }}>
        <SheetContent side="right" className="bg-background border-border w-full sm:max-w-lg overflow-y-auto" data-testid="item-detail-sheet">
          {detailItem && (
            <>
              <SheetHeader className="mb-4">
                <SheetTitle className="text-left tracking-tighter" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>
                  EDIT ITEM
                </SheetTitle>
              </SheetHeader>

              {/* Aperçu version */}
              <div className="flex gap-4 mb-4">
                <img
                  src={proxyImageUrl(detailItem.version?.front_photo || detailItem.master_kit?.front_photo)}
                  alt={detailItem.master_kit?.club}
                  className="w-20 h-28 object-cover border border-border shrink-0"
                />
                <div className="flex-1">
                  <h3 className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>
                    {detailItem.master_kit?.club}
                  </h3>
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {detailItem.master_kit?.season} — {detailItem.master_kit?.kit_type}
                  </p>
                  <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                    {detailItem.master_kit?.brand}
                  </p>
                  <div className="flex gap-2 mt-2">
                    <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.model || '—'}</Badge>
                    <Badge variant="outline" className="rounded-none text-[10px]">{detailItem.version?.competition || '—'}</Badge>
                  </div>
                </div>
              </div>

              {/* ══ Formulaire unifié ══ */}
              <CollectionItemForm
                form={editForm}
                onChange={(field, value) => setEditForm(f => ({ ...f, [field]: value }))}
                mode={editMode}
                onModeChange={setEditMode}
                version={detailItem.version}
                seasonYear={parseSeasonYear(detailItem.master_kit?.season)}
                showEstimation
              />

              {/* Actions */}
              <div className="flex gap-2 mt-6">
                <Button
                  onClick={saveEdit}
                  disabled={saving}
                  className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90 flex-1"
                >
                  {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-1" />}
                  {saving ? 'Saving…' : 'Save'}
                </Button>
                <Button variant="outline" onClick={() => setDetailItem(null)} disabled={saving} className="rounded-none">Cancel</Button>
                <Button variant="ghost" onClick={() => handleRemove(detailItem.collection_id)} disabled={saving} className="rounded-none text-destructive hover:text-destructive px-3">
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      {/* ══ LISTING DIALOG ══ */}
      <Dialog open={!!listingItem} onOpenChange={open => { if (!open) { setListingItem(null); setListingForm({ listing_type: 'sale', asking_price: '', trade_for: '' }); } }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Mettre en vente / échange</DialogTitle>
          </DialogHeader>
          {listingItem && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                {listingItem.master_kit?.club} — {listingItem.master_kit?.season}
              </p>
              <div className="space-y-1">
                <Label>Type d'annonce</Label>
                <Select value={listingForm.listing_type} onValueChange={v => setListingForm(f => ({ ...f, listing_type: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sale">Vente</SelectItem>
                    <SelectItem value="trade">Échange</SelectItem>
                    <SelectItem value="both">Vente ou échange</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {(listingForm.listing_type === 'sale' || listingForm.listing_type === 'both') && (
                <div className="space-y-1">
                  <Label>Prix demandé (€)</Label>
                  <Input
                    type="number"
                    min={0}
                    step={0.01}
                    placeholder="Ex: 80"
                    value={listingForm.asking_price}
                    onChange={e => setListingForm(f => ({ ...f, asking_price: e.target.value }))}
                  />
                </div>
              )}
              {(listingForm.listing_type === 'trade' || listingForm.listing_type === 'both') && (
                <div className="space-y-1">
                  <Label>Cherche en échange (optionnel)</Label>
                  <Input
                    placeholder="Ex: PSG 2012 domicile taille L"
                    value={listingForm.trade_for}
                    onChange={e => setListingForm(f => ({ ...f, trade_for: e.target.value }))}
                  />
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" onClick={() => { setListingItem(null); setListingForm({ listing_type: 'sale', asking_price: '', trade_for: '' }); }}>Annuler</Button>
            <Button onClick={handleCreateListing} disabled={listingLoading || ((listingForm.listing_type === 'sale' || listingForm.listing_type === 'both') && !listingForm.asking_price)}>
              {listingLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Tag className="w-4 h-4 mr-2" />}
              Publier l'annonce
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

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
