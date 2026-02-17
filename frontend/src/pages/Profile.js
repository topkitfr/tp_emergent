import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getMyCollection, getCollectionStats, updateProfile } from '@/lib/api';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { Shirt, FolderOpen, Star, Mail, Calendar, Edit2, Check, X, Lock, Globe, DollarSign, TrendingUp, TrendingDown, Minus, FileCheck } from 'lucide-react';

export default function Profile() {
  const { user, checkAuth } = useAuth();
  const [collection, setCollection] = useState([]);
  const [stats, setStats] = useState(null);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    description: '',
    collection_privacy: 'public',
    profile_picture: ''
  });

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        description: user.description || '',
        collection_privacy: user.collection_privacy || 'public',
        profile_picture: user.profile_picture || user.picture || ''
      });
    }
    getMyCollection({}).then(r => setCollection(r.data)).catch(() => {});
    getCollectionStats().then(r => setStats(r.data)).catch(() => {});
  }, [user]);

  if (!user) return null;

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateProfile(formData);
      toast.success('Profile updated');
      setEditing(false);
      checkAuth();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
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

  return (
    <div className="animate-fade-in-up">
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-4xl mx-auto px-4 lg:px-8 py-12">
          {/* Profile Header */}
          <div className="flex items-start gap-6 mb-8" data-testid="profile-header">
            <Avatar className="w-20 h-20 border-2 border-border">
              <AvatarImage src={user.profile_picture || user.picture} alt={user.name} />
              <AvatarFallback className="text-2xl bg-secondary">{user.name?.[0]}</AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-3xl tracking-tighter mb-1" data-testid="profile-name">{user.name?.toUpperCase()}</h1>
                  {user.username && (
                    <p className="text-sm text-primary font-mono" data-testid="profile-username">@{user.username}</p>
                  )}
                </div>
                <Button variant="outline" size="sm" onClick={() => setEditing(!editing)} className="rounded-none border-border" data-testid="edit-profile-btn">
                  <Edit2 className="w-3 h-3 mr-1" /> {editing ? 'Cancel' : 'Edit'}
                </Button>
              </div>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <Mail className="w-3 h-3" />
                  <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>{user.email}</span>
                </div>
                {user.created_at && (
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Joined {new Date(user.created_at).toLocaleDateString()}</span>
                  </div>
                )}
              </div>
              {user.description && !editing && (
                <p className="text-sm text-muted-foreground mt-3 max-w-lg" style={{ textTransform: 'none', fontFamily: 'DM Sans' }} data-testid="profile-description">
                  {user.description}
                </p>
              )}
            </div>
          </div>

          {/* Edit Form */}
          {editing && (
            <div className="border border-primary/30 p-6 mb-8 space-y-4" data-testid="profile-edit-form">
              <h3 className="text-sm uppercase tracking-wider" style={{ fontFamily: 'Barlow Condensed' }}>EDIT PROFILE</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Username</Label>
                  <Input value={formData.username} onChange={e => setFormData(p => ({...p, username: e.target.value}))} placeholder="username" className="bg-card border-border rounded-none" data-testid="input-username" />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Profile Picture URL</Label>
                  <Input value={formData.profile_picture} onChange={e => setFormData(p => ({...p, profile_picture: e.target.value}))} placeholder="https://..." className="bg-card border-border rounded-none" data-testid="input-picture" />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label className="text-xs uppercase tracking-wider text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>Description</Label>
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
          )}

          {/* Privacy Toggle */}
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

          {/* Stats */}
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
              <div className="text-2xl font-bold font-mono">{user.review_count || 0}</div>
              <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>REVIEWS</div>
            </div>
            <div className="p-5 text-center">
              <FileCheck className="w-5 h-5 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold font-mono">{user.submission_count || 0}</div>
              <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed' }}>SUBMISSIONS</div>
            </div>
          </div>

          {/* Collection Value */}
          {stats && stats.items_with_estimates > 0 && (
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

          <Separator className="bg-border mb-8" />

          {/* Recent Collection */}
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
                        <img src={item.version?.front_photo || item.master_kit?.front_photo} alt="" className="w-full h-full object-cover" />
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
        </div>
      </div>
    </div>
  );
}
