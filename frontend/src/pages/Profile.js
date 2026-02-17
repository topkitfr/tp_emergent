import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { getMyCollection } from '@/lib/api';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Shirt, FolderOpen, Star, Mail, Calendar } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();
  const [collection, setCollection] = useState([]);

  useEffect(() => {
    getMyCollection({}).then(r => setCollection(r.data)).catch(() => {});
  }, []);

  if (!user) return null;

  const categories = [...new Set(collection.map(c => c.category))];

  return (
    <div className="animate-fade-in-up">
      <div className="relative">
        <div className="absolute inset-0 stadium-glow pointer-events-none" />
        <div className="max-w-4xl mx-auto px-4 lg:px-8 py-12">
          {/* Profile Header */}
          <div className="flex items-start gap-6 mb-8" data-testid="profile-header">
            <Avatar className="w-20 h-20 border-2 border-border">
              <AvatarImage src={user.picture} alt={user.name} />
              <AvatarFallback className="text-2xl bg-secondary">{user.name?.[0]}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-3xl tracking-tighter mb-1" data-testid="profile-name">{user.name?.toUpperCase()}</h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Mail className="w-3 h-3" />
                <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>{user.email}</span>
              </div>
              {user.created_at && (
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                  <Calendar className="w-3 h-3" />
                  <span style={{ textTransform: 'none', fontFamily: 'DM Sans' }}>Joined {new Date(user.created_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 border border-border mb-8" data-testid="profile-stats">
            <div className="p-6 text-center border-r border-border">
              <FolderOpen className="w-5 h-5 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold font-mono">{collection.length}</div>
              <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>JERSEYS</div>
            </div>
            <div className="p-6 text-center border-r border-border">
              <Shirt className="w-5 h-5 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold font-mono">{categories.length}</div>
              <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>CATEGORIES</div>
            </div>
            <div className="p-6 text-center">
              <Star className="w-5 h-5 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold font-mono">0</div>
              <div className="text-xs text-muted-foreground" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>REVIEWS</div>
            </div>
          </div>

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
                        <p className="text-xs font-semibold truncate" style={{ fontFamily: 'Barlow Condensed, sans-serif', textTransform: 'uppercase' }}>{item.master_kit?.club}</p>
                        <p className="text-[10px] text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>{item.master_kit?.season}</p>
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
