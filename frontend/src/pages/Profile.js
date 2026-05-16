import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import {
  getMyCollection, getCollectionStats, updateProfile, updateCredentials,
  getUserBadges, getUserByUsername, getFollows, proxyImageUrl,
  getUserPublicCollection, getUserPublicSubmissions, getUserPublicFollows,
  getUserListings, deleteAccount, getMyTransactions,
} from '@/lib/api';
import TransactionCard from '@/components/TransactionCard';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import {
  Shirt, FolderOpen, Star, Mail, Calendar, Edit2, Check, X,
  Lock, Globe, DollarSign, TrendingUp, TrendingDown, Minus,
  FileCheck, Shield, KeyRound, Users, User, Tag,
} from 'lucide-react';
import ImageUpload from '@/components/ImageUpload';

export default function Profile() {
  const { username: urlUsername } = useParams();
  const { user, checkAuth } = useAuth();
  const [profileUser, setProfileUser]       = useState(null);
  const [collection, setCollection]         = useState([]);
  const [stats, setStats]                   = useState(null);
  const [editing, setEditing]               = useState(false);
  const [saving, setSaving]                 = useState(false);
  const [loadingProfile, setLoadingProfile] = useState(!!urlUsername);
  const [badges, setBadges]                 = useState([]);
  const [follows, setFollows]               = useState([]);
  const [credForm, setCredForm]             = useState({ current_password: '', new_email: '', new_password: '' });
  const [savingCreds, setSavingCreds]       = useState(false);
  const [showDelete, setShowDelete]         = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting]             = useState(false);

  const [publicCollection, setPublicCollection]   = useState([]);
  const [publicCollectionPrivate, setPublicCollectionPrivate] = useState(false);
  const [publicSubmissions, setPublicSubmissions] = useState([]);
  const [publicFollows, setPublicFollows]         = useState([]);
  const [publicListings, setPublicListings]       = useState([]);
  const [transactions, setTransactions]           = useState([]);
  const [txnTab, setTxnTab]                       = useState("active"); // "active" | "completed"

  const [formData, setFormData] = useState({
    username: '',
    description: '',
    collection_privacy: 'public',
    profile_picture: ''
  });

  const isOwnProfile = !urlUsername || (user && profileUser && user.user_id === profileUser.user_id);

  useEffect(() => {
    if (urlUsername) {
      setLoadingProfile(true);
      getUserByUsername(urlUsername)
        .then(r => { setProfileUser(r.data); setLoadingProfile(false); })
        .catch(() => { setProfileUser(null); setLoadingProfile(false); });
    } else if (user) {
      setProfileUser(user);
    }
  }, [urlUsername, user]);

  useEffect(() => {
    if (profileUser && isOwnProfile) {
      setFormData({
        username: profileUser.username || '',
        description: profileUser.description || '',
        collection_privacy: profileUser.collection_privacy || 'public',
        profile_picture: profileUser.profile_picture || ''
      });
      getMyCollection({}).then(r => setCollection(r.data)).catch(() => {});
      getCollectionStats().then(r => setStats(r.data)).catch(() => {});
      getUserBadges().then(r => setBadges(r.data?.badges || [])).catch(() => {});
      getFollows().then(r => setFollows(r.data?.follows || [])).catch(() => {});
      getMyTransactions().then(r => setTransactions(r.data || [])).catch(() => {});
    }
  }, [profileUser, isOwnProfile]);

  useEffect(() => {
    if (profileUser && !isOwnProfile) {
      const uid = profileUser.user_id;
      getUserPublicCollection(uid)
        .then(r => setPublicCollection(r.data?.collection || []))
        .catch(err => {
          if (err.response?.status === 403) setPublicCollectionPrivate(true);
        });
      getUserPublicSubmissions(uid)
        .then(r => setPublicSubmissions(r.data?.submissions || []))
        .catch(() => {});
      getUserPublicFollows(uid)
        .then(r => setPublicFollows(r.data?.follows || []))
        .catch(() => {});
      getUserListings(uid)
        .then(r => setPublicListings(r.data || []))
        .catch(() => {});
    }
  }, [profileUser, isOwnProfile]);

  if (loadingProfile) {
    return (
      <div className="animate-pulse max-w-4xl mx-auto px-4 lg:px-8 py-12">
        <div className="flex items-start gap-6 mb-8">
          <div className="w-20 h-20 rounded-full bg-card" />
          <div className="flex-1 space-y-3">
            <div className="h-8 w-48 bg-card" />
            <div className="h-4 w-32 bg-card" />
          </div>
        </div>
      </div>
    );
  }

  const displayUser = profileUser || user;
  if (!displayUser) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(formData);
      toast.success('Profile updated');
      setEditing(false);
      setProfileUser(prev => ({ ...prev, ...formData }));
      checkAuth();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveCreds = async () => {
    if (!credForm.current_password) { toast.error('Current password required'); return; }
    if (!credForm.new_email && !credForm.new_password) { toast.error('Enter a new email or new password'); return; }
    setSavingCreds(true);
    try {
      await updateCredentials({
        current_password: credForm.current_password,
        new_email:        credForm.new_email    || undefined,
        new_password:     credForm.new_password || undefined,
      });
      toast.success('Credentials updated');
      setCredForm({ current_password: '', new_email: '', new_password: '' });
      checkAuth();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update credentials');
    } finally {
      setSavingCreds(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) { toast.error('Mot de passe requis'); return; }
    setDeleting(true);
    try {
      await deleteAccount(deletePassword);
      toast.success('Compte supprimé. À bientôt !');
      setTimeout(() => window.location.href = '/', 1500);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Erreur lors de la suppression');
    } finally {
      setDeleting(false);
    }
  };

  const togglePrivacy = async () => {
    const newVal = formData.collection_privacy === 'public' ? 'private' : 'public';
    setFormData(p => ({ ...p, collection_privacy: newVal }));
    try {
      await updateProfile({ collection_privacy: newVal });
      toast.success(`Collection set to ${newVal}`);
      checkAuth();
    } catch {
      toast.error('Failed to update privacy');
    }
  };

  const categories = [...new Set(collection.map(c => c.category))];
  const profileUrl = displayUser.username ? `${window.location.origin}/profile/${displayUser.username}` : null;

  return (
    <div className="animate-fade-in-up">
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-4xl mx-auto px-4 lg:px-8 py-12">

          {/* Profile Header */}
          <div className="flex items-start gap-6 mb-8" data-testid="profile-header">
            <Avatar className="w-20 h-20 border-2 border-border">
              <AvatarImage src={proxyImageUrl(displayUser.profile_picture)} alt={displayUser.name} />
              <AvatarFallback className="text-2xl bg-secondary">{displayUser.name?.[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-3xl tracking-tighter mb-1" data-testid="profile-name">
                    {(displayUser.username || displayUser.name)?.toUpperCase()}
                  </h1>
                  {displayUser.username && displayUser.name && displayUser.username.toLowerCase() !== displayUser.name.toLowerCase().replace(/\s/g, '') && (
                    <p className="text-sm text-muted-foreground font-normal" data-testid="profile-fullname" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{displayUser.name}</p>
                  )}
                  {displayUser.username && (
                    <p className="text-sm text-primary font-mono" data-testid="profile-username">@{displayUser.username}</p>
                  )}
                </div>
                {isOwnProfile && user && (
                  <Button variant="outline" size="sm" onClick={() => setEditing(!editing)} className="rounded-none border-border" data-testid="edit-profile-btn">
                    <Edit2 className="w-3 h-3 mr-1" /> {editing ? 'Cancel' : 'Edit'}
                  </Button>
                )}
              </div>
              <div className="flex items-center gap-4 mt-2">
                {isOwnProfile && (
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Mail className="w-3 h-3" />
                    <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>{displayUser.email}</span>
                  </div>
                )}
                {displayUser.created_at && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Joined {new Date(displayUser.created_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
              {displayUser.description && !editing && (
                <p className="text-sm text-muted-foreground mt-3 max-w-lg" style={{ textTransform: 'none', fontFamily: 'DM Sans' }} data-testid="profile-description">
                  {displayUser.description}
                </p>
              )}
              {profileUrl && !editing && (
                <p className="text-xs text-muted-foreground mt-2 font-mono" data-testid="profile-url">
                  {profileUrl}
                </p>
              )}
            </div>
          </div>

          {/* Edit Form */}
          {editing && isOwnProfile && (
            <div className="space-y-6 mb-8">
              <div className="border border-primary/30 p-6 space-y-4" data-testid="profile-edit-form">
                <h3 className="text-sm uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EDIT PROFILE</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Username</Label>
                    <Input value={formData.username} onChange={e => setFormData(p => ({...p, username: e.target.value}))} placeholder="username" className="bg-card border-border rounded-none" data-testid="input-username" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Profile Picture</Label>
                    <ImageUpload
                      value={formData.profile_picture}
                      onChange={(url) => setFormData(p => ({...p, profile_picture: url}))}
                      folder="profile"
                      label="Profile Picture"
                      testId="profile-picture-upload"
                    />
                  </div>
                  <div className="space-y-2 sm:col-span-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Bio</Label>
                    <Textarea value={formData.description} onChange={e => setFormData(p => ({...p, description: e.target.value}))} placeholder="Tell others about yourself..." className="bg-card border-border rounded-none min-h-[80px]" data-testid="input-description" />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSave} disabled={saving} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="save-profile-btn">
                    <Check className="w-4 h-4 mr-1" /> {saving ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button variant="outline" onClick={() => setEditing(false)} className="rounded-none">
                    <X className="w-4 h-4 mr-1" /> Cancel
                  </Button>
                </div>
              </div>

              <div className="border border-border p-6 space-y-4" data-testid="credentials-form">
                <h3 className="text-sm uppercase tracking-wider flex items-center gap-2" style={{ fontFamily: 'Barlow Condensed' }}>
                  <KeyRound className="w-4 h-4" /> CHANGE EMAIL / PASSWORD
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2 sm:col-span-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Current Password *</Label>
                    <Input type="password" value={credForm.current_password} onChange={e => setCredForm(p => ({...p, current_password: e.target.value}))} placeholder="Required to change credentials" className="bg-card border-border rounded-none" data-testid="input-current-password" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>New Email</Label>
                    <Input type="email" value={credForm.new_email} onChange={e => setCredForm(p => ({...p, new_email: e.target.value}))} placeholder="Leave blank to keep current" className="bg-card border-border rounded-none" data-testid="input-new-email" />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>New Password</Label>
                    <Input type="password" value={credForm.new_password} onChange={e => setCredForm(p => ({...p, new_password: e.target.value}))} placeholder="Min. 8 characters" className="bg-card border-border rounded-none" data-testid="input-new-password" />
                  </div>
                </div>
                <Button onClick={handleSaveCreds} disabled={savingCreds} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="save-credentials-btn">
                  <Check className="w-4 h-4 mr-1" /> {savingCreds ? 'Saving...' : 'Update Credentials'}
                </Button>
              </div>
            </div>
          )}

          {/* Privacy Toggle */}
          {isOwnProfile && user && (
            <div className="flex items-center justify-between border border-border p-4 mb-8" data-testid="privacy-toggle">
              <div className="flex items-center gap-3">
                {formData.collection_privacy === 'public' ? (
                  <Globe className="w-5 h-5 text-primary" />
                ) : (
                  <Lock className="w-5 h-5 text-muted-foreground" />
                )}
                <div>
                  <p className="text-sm font-medium">Collection Privacy</p>
                  <p className="text-xs text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>
                    {formData.collection_privacy === 'public' ? 'Your collection is visible to everyone' : 'Your collection is private'}
                  </p>
                </div>
              </div>
              <Switch
                checked={formData.collection_privacy === 'public'}
                onCheckedChange={togglePrivacy}
                data-testid="privacy-switch"
              />
            </div>
          )}

          {/* Danger Zone — suppression compte */}
          {isOwnProfile && user && (
            <div className="border border-red-900/40 p-4 mb-8">
              <p className="text-xs font-semibold text-red-500 mb-3 uppercase tracking-widest">Zone dangereuse</p>
              {!showDelete ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-none border-red-800 text-red-500 hover:bg-red-950 hover:text-red-400"
                  onClick={() => setShowDelete(true)}
                >
                  Supprimer mon compte
                </Button>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs text-muted-foreground">
                    Cette action est <strong className="text-red-400">irréversible</strong>. Toutes tes données seront supprimées (collection, annonces, offres).
                  </p>
                  <Input
                    type="password"
                    placeholder="Confirme ton mot de passe"
                    value={deletePassword}
                    onChange={e => setDeletePassword(e.target.value)}
                    className="rounded-none border-red-900/40 bg-card"
                  />
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      className="rounded-none bg-red-700 hover:bg-red-600 text-white"
                      onClick={handleDeleteAccount}
                      disabled={deleting}
                    >
                      {deleting ? 'Suppression...' : 'Confirmer la suppression'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="rounded-none"
                      onClick={() => { setShowDelete(false); setDeletePassword(''); }}
                    >
                      Annuler
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Stats — propre profil */}
          {isOwnProfile && (
            <div className="grid grid-cols-2 sm:grid-cols-4 border border-border mb-8" data-testid="profile-stats">
              <div className="p-5 text-center border-r border-border">
                <FolderOpen className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{collection.length}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>JERSEYS</div>
              </div>
              <div className="p-5 text-center border-r border-border">
                <Shirt className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{categories.length}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>CATEGORIES</div>
              </div>
              <div className="p-5 text-center border-r border-border">
                <Star className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{displayUser.review_count || 0}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>REVIEWS</div>
              </div>
              <div className="p-5 text-center">
                <FileCheck className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{displayUser.submission_count || 0}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>SUBMISSIONS</div>
              </div>
            </div>
          )}

          {/* Stats — profil tiers */}
          {!isOwnProfile && profileUser && (
            <div className="grid grid-cols-3 border border-border mb-8" data-testid="public-profile-stats">
              <div className="p-5 text-center border-r border-border">
                <FolderOpen className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{profileUser.collection_count || 0}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>JERSEYS</div>
              </div>
              <div className="p-5 text-center border-r border-border">
                <Star className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{profileUser.review_count || 0}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>REVIEWS</div>
              </div>
              <div className="p-5 text-center">
                <FileCheck className="w-5 h-5 text-primary mx-auto mb-2" />
                <div className="text-2xl font-bold font-mono">{profileUser.submission_count || 0}</div>
                <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>SUBMISSIONS</div>
              </div>
            </div>
          )}

          {/* Collection Value */}
          {isOwnProfile && stats && stats.items_with_estimates > 0 && (
            <div className="border border-border p-6 mb-8" data-testid="collection-total-value">
              <h3 className="text-sm uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
                <DollarSign className="w-4 h-4 inline mr-1" /> COLLECTION VALUE
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-destructive/5 border border-destructive/20">
                  <TrendingDown className="w-4 h-4 text-destructive mx-auto mb-1" />
                  <div className="font-mono text-xl">${stats.estimated_value.low}</div>
                  <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>Low</div>
                </div>
                <div className="text-center p-3 bg-accent/5 border border-accent/20">
                  <Minus className="w-4 h-4 text-accent mx-auto mb-1" />
                  <div className="font-mono text-xl">${stats.estimated_value.average}</div>
                  <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>Average</div>
                </div>
                <div className="text-center p-3 bg-primary/5 border border-primary/20">
                  <TrendingUp className="w-4 h-4 text-primary mx-auto mb-1" />
                  <div className="font-mono text-xl">${stats.estimated_value.high}</div>
                  <div className="text-[10px] text-muted-foreground uppercase" style={{ fontFamily: 'Barlow Condensed' }}>High</div>
                </div>
              </div>
            </div>
          )}

          {/* Badges ClubID */}
          {isOwnProfile && badges.length > 0 && (
            <div className="mb-8" data-testid="clubid-badges">
              <h3 className="text-sm uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
                <Shield className="w-4 h-4 inline mr-1" /> CLUBID BADGES
              </h3>
              <div className="flex flex-wrap gap-3">
                {badges.map(b => (
                  <div
                    key={b.team_id}
                    className="flex items-center gap-2 px-3 py-2 border text-xs font-bold uppercase tracking-wider"
                    style={{
                      borderColor: b.primary_color || '#6366f1',
                      color: b.primary_color || '#6366f1',
                      background: `${b.primary_color || '#6366f1'}15`,
                      fontFamily: 'Barlow Condensed',
                    }}
                    data-testid={`badge-${b.team_id}`}
                  >
                    <Shield className="w-3.5 h-3.5" style={{ color: b.primary_color }} />
                    {b.club} CLUBID FAN
                    <span className="ml-1 opacity-60 font-mono text-[10px]">{b.kit_count} kits</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Following */}
          {isOwnProfile && follows.length > 0 && (
            <div className="mb-8" data-testid="following-section">
              <h3 className="text-sm uppercase tracking-wider mb-4" style={{ fontFamily: 'Barlow Condensed' }}>
                <Users className="w-4 h-4 inline mr-1" /> FOLLOWING ({follows.length})
              </h3>
              <div className="flex flex-wrap gap-2">
                {follows.map(f => (
                  <Link
                    key={f.follow_id}
                    to={f.target_type === 'team' ? `/teams/${f.target_id}` : `/players/${f.target_id}`}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-border hover:border-primary/50 transition-colors"
                    style={{ fontFamily: 'Barlow Condensed' }}
                    data-testid={`follow-item-${f.follow_id}`}
                  >
                    {f.target_type === 'team' ? <Shield className="w-3 h-3 text-primary" /> : <User className="w-3 h-3 text-accent" />}
                    <span className="uppercase">{f.target_name || f.target_id}</span>
                    <span className="text-muted-foreground/50 text-[10px] lowercase">{f.target_type}</span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          <Separator className="bg-border mb-8" />

          {/* Transactions */}
          {isOwnProfile && (() => {
            const activeTxns    = transactions.filter(t => !["completed"].includes(t.status));
            const completedTxns = transactions.filter(t => t.status === "completed");
            const pendingCount  = activeTxns.filter(t => {
              const isSeller = t.seller_id === user?.user_id;
              const isTrade  = t.transaction_type === "trade";
              return (
                (isSeller  && t.status === "awaiting_shipment" && !t.seller_shipped) ||
                (!isSeller && t.status === "shipped"           && !t.buyer_received)  ||
                (!isSeller && t.status === "delivered"         && !t.buyer_approved)  ||
                (isTrade && isSeller  && t.status === "delivered" && !t.seller_approved) ||
                (isTrade && !isSeller && t.status === "awaiting_shipment" && !t.buyer_shipped)
              );
            }).length;
            return (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl tracking-tight">MES TRANSACTIONS</h2>
                    {pendingCount > 0 && (
                      <span className="bg-destructive text-destructive-foreground text-[10px] font-bold px-2 py-0.5 rounded-full">
                        {pendingCount} action{pendingCount > 1 ? "s" : ""}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-1">
                    {["active", "completed"].map(tab => (
                      <button key={tab} onClick={() => setTxnTab(tab)}
                        className={`text-xs px-3 py-1 border font-medium uppercase tracking-wide ${txnTab === tab ? "bg-primary text-primary-foreground border-primary" : "border-border text-muted-foreground hover:text-foreground"}`}
                        style={{ fontFamily: "Barlow Condensed" }}>
                        {tab === "active" ? `En cours (${activeTxns.length})` : `Terminées (${completedTxns.length})`}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-3">
                  {(txnTab === "active" ? activeTxns : completedTxns).map(txn => (
                    <TransactionCard
                      key={txn.transaction_id}
                      txn={txn}
                      currentUserId={user?.user_id}
                      onRefresh={() => getMyTransactions().then(r => setTransactions(r.data || [])).catch(() => {})}
                    />
                  ))}
                  {(txnTab === "active" ? activeTxns : completedTxns).length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-8 border border-dashed border-border" style={{ fontFamily: "DM Sans" }}>
                      {txnTab === "active" ? "Aucune transaction en cours" : "Aucune transaction terminée"}
                    </p>
                  )}
                </div>
              </div>
            );
          })()}

          {/* Collection propre profil */}
          {isOwnProfile && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl tracking-tight">RECENT COLLECTION</h2>
                <Link to="/collection">
                  <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground rounded-none" data-testid="view-all-collection-btn">
                    View All
                  </Button>
                </Link>
              </div>
              {collection.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 stagger-children">
                  {collection.slice(0, 8).map(item => (
                    <Link to={`/version/${item.version_id}`} key={item.collection_id}>
                      <div className="border border-border bg-card overflow-hidden hover:border-primary/30" style={{ transition: 'border-color 0.2s ease' }} data-testid={`profile-collection-${item.collection_id}`}>
                        <div className="aspect-[3/4] bg-secondary overflow-hidden">
                          <img src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)} alt="" className="w-full h-full object-cover" />
                        </div>
                        <div className="p-2">
                          <p className="text-xs font-semibold truncate" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{item.master_kit?.club}</p>
                          <div className="flex items-center justify-between">
                            <p className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season}</p>
                            {item.value_estimate > 0 && <span className="font-mono text-[10px] text-accent">${item.value_estimate}</span>}
                          </div>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 border border-dashed border-border">
                  <FolderOpen className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground" style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>No jerseys in collection yet</p>
                  <Link to="/browse">
                    <Button variant="outline" size="sm" className="rounded-none mt-3" data-testid="profile-browse-btn">Browse Catalog</Button>
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Section profil tiers */}
          {!isOwnProfile && (
            <div className="space-y-10">

              <div>
                <h2 className="text-xl tracking-tight mb-6">COLLECTION</h2>
                {publicCollectionPrivate ? (
                  <div className="flex items-center gap-3 py-8 border border-dashed border-border text-muted-foreground justify-center">
                    <Lock className="w-5 h-5" />
                    <span className="text-sm" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Cette collection est privée</span>
                  </div>
                ) : publicCollection.length > 0 ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                    {publicCollection.slice(0, 8).map(item => (
                      <Link to={`/version/${item.version_id}`} key={item.collection_id}>
                        <div className="border border-border bg-card overflow-hidden hover:border-primary/30" style={{ transition: 'border-color 0.2s ease' }}>
                          <div className="aspect-[3/4] bg-secondary overflow-hidden">
                            <img src={proxyImageUrl(item.version?.front_photo || item.master_kit?.front_photo)} alt="" className="w-full h-full object-cover" />
                          </div>
                          <div className="p-2">
                            <p className="text-xs font-semibold truncate" style={{ fontFamily: 'Barlow Condensed', textTransform: 'uppercase' }}>{item.master_kit?.club}</p>
                            <p className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season}</p>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 border border-dashed border-border">
                    <FolderOpen className="w-6 h-6 text-muted-foreground mx-auto mb-2" />
                    <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>Aucun maillot pour l'instant</p>
                  </div>
                )}
              </div>

              {publicListings.length > 0 && (
                <div>
                  <h2 className="text-xl tracking-tight mb-6">MARKETPLACE ({publicListings.length})</h2>
                  <div className="space-y-2">
                    {publicListings.map(l => {
                      const snap = l.kit_snapshot || {};
                      const typeLabel = { sale: 'Vente', trade: 'Échange', both: 'Vente/Échange' }[l.listing_type] || l.listing_type;
                      const typeCls   = { sale: 'bg-green-600', trade: 'bg-blue-600', both: 'bg-purple-600' }[l.listing_type] || 'bg-gray-500';
                      return (
                        <Link to={`/marketplace/${l.listing_id}`} key={l.listing_id} className="flex items-center gap-3 border border-border bg-card px-3 py-2 hover:border-primary/30 transition-colors">
                          <Tag className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                          <span className={`text-[10px] text-white px-1.5 py-0.5 rounded font-semibold shrink-0 ${typeCls}`}>{typeLabel}</span>
                          <span className="flex-1 truncate text-xs">{snap.club || '—'}{snap.season ? ` — ${snap.season}` : ''}</span>
                          {l.asking_price != null && <span className="font-mono text-xs text-accent shrink-0">{l.asking_price} €</span>}
                          <span className="text-xs text-muted-foreground shrink-0">Voir →</span>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              )}

              {publicSubmissions.length > 0 && (
                <div>
                  <h2 className="text-xl tracking-tight mb-6">CONTRIBUTIONS ({publicSubmissions.length})</h2>
                  <div className="space-y-2">
                    {publicSubmissions.slice(0, 10).map(s => (
                      <div key={s.submission_id} className="flex items-center justify-between border border-border p-3 text-sm">
                        <div style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
                          <span className="font-medium">{s.submission_type}</span>
                          {s.data?.club && <span className="text-muted-foreground ml-2">{s.data.club}</span>}
                          {s.data?.season && <span className="text-muted-foreground ml-1">— {s.data.season}</span>}
                        </div>
                        <span className="text-[10px] text-muted-foreground font-mono">{new Date(s.created_at).toLocaleDateString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {publicFollows.length > 0 && (
                <div>
                  <h2 className="text-xl tracking-tight mb-6">FOLLOWING ({publicFollows.length})</h2>
                  <div className="flex flex-wrap gap-2">
                    {publicFollows.map(f => (
                      <Link
                        key={f.follow_id}
                        to={f.target_type === 'team' ? `/teams/${f.target_id}` : `/players/${f.target_id}`}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs border border-border hover:border-primary/50 transition-colors"
                        style={{ fontFamily: 'Barlow Condensed' }}
                      >
                        {f.target_type === 'team' ? <Shield className="w-3 h-3 text-primary" /> : <User className="w-3 h-3 text-accent" />}
                        <span className="uppercase">{f.target_name || f.target_id}</span>
                        <span className="text-muted-foreground/50 text-[10px] lowercase">{f.target_type}</span>
                      </Link>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}

        </div>
      </div>
    </div>
  );
}
