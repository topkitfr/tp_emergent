import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getVersion, createReview, addToCollection } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { toast } from 'sonner';
import { Star, Shirt, ChevronRight, Package, Tag, Users, FolderPlus, Check, Hash, User } from 'lucide-react';

export default function VersionDetail() {
  const { versionId } = useParams();
  const { user } = useAuth();
  const [version, setVersion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reviewRating, setReviewRating] = useState(0);
  const [reviewHover, setReviewHover] = useState(0);
  const [reviewComment, setReviewComment] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [addingToCollection, setAddingToCollection] = useState(false);
  const [collectionCategory, setCollectionCategory] = useState('General');
  const [showAddForm, setShowAddForm] = useState(false);

  const fetchVersion = () => {
    getVersion(versionId).then(r => {
      setVersion(r.data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => { fetchVersion(); }, [versionId]);

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
      await addToCollection({ version_id: versionId, category: collectionCategory });
      toast.success('Added to collection');
      setShowAddForm(false);
      fetchVersion();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add');
    } finally {
      setAddingToCollection(false);
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
              <img src={version.front_photo || mk?.front_photo} alt="Front" className="w-full h-full object-cover" />
            </div>
            {version.back_photo && (
              <div className="aspect-[3/4] border border-border bg-card overflow-hidden" data-testid="version-back-image">
                <img src={version.back_photo} alt="Back" className="w-full h-full object-cover" />
              </div>
            )}
          </div>

          {/* Right - Info */}
          <div className="space-y-6">
            <div>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="outline" className="rounded-none text-xs">{version.model}</Badge>
                <Badge variant="outline" className="rounded-none text-xs">{version.gender}</Badge>
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

            {/* Rating */}
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

            {/* Data */}
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Model</div>
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4 text-primary" />
                  <span className="text-sm">{version.model}</span>
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>Gender</div>
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-primary" />
                  <span className="text-sm">{version.gender}</span>
                </div>
              </div>
              {version.sku_code && (
                <div>
                  <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>SKU</div>
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4 text-primary" />
                    <span className="text-sm font-mono">{version.sku_code}</span>
                  </div>
                </div>
              )}
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>In Collections</div>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary" />
                  <span className="text-sm font-mono">{version.collection_count || 0}</span>
                </div>
              </div>
            </div>

            {/* Add to Collection */}
            {user && (
              <div>
                {!showAddForm ? (
                  <Button onClick={() => setShowAddForm(true)} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="add-to-collection-btn">
                    <FolderPlus className="w-4 h-4 mr-2" /> Add to My Collection
                  </Button>
                ) : (
                  <div className="border border-border p-4 space-y-3">
                    <Input
                      placeholder="Category (e.g., Champions League, Vintage)"
                      value={collectionCategory}
                      onChange={e => setCollectionCategory(e.target.value)}
                      className="bg-card border-border rounded-none"
                      data-testid="collection-category-input"
                    />
                    <div className="flex gap-2">
                      <Button onClick={handleAddToCollection} disabled={addingToCollection} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="confirm-add-collection-btn">
                        <Check className="w-4 h-4 mr-1" /> {addingToCollection ? 'Adding...' : 'Confirm'}
                      </Button>
                      <Button variant="outline" onClick={() => setShowAddForm(false)} className="rounded-none" data-testid="cancel-add-collection-btn">Cancel</Button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Reviews Section */}
        <div className="mt-16 border-t border-border pt-8">
          <h2 className="text-xl tracking-tight mb-6" data-testid="reviews-section-title">
            REVIEWS <span className="font-mono text-sm text-muted-foreground ml-2">{version.review_count || 0}</span>
          </h2>

          {/* Write Review */}
          {user && (
            <div className="border border-border p-6 mb-8" data-testid="review-form">
              <h3 className="text-sm font-semibold mb-4" style={{ fontFamily: 'Barlow Condensed, sans-serif' }}>WRITE A REVIEW</h3>
              <div className="flex items-center gap-1 mb-4">
                {[1, 2, 3, 4, 5].map(s => (
                  <button
                    key={s}
                    onClick={() => setReviewRating(s)}
                    onMouseEnter={() => setReviewHover(s)}
                    onMouseLeave={() => setReviewHover(0)}
                    data-testid={`star-rating-${s}`}
                  >
                    <Star className={`w-6 h-6 cursor-pointer ${s <= (reviewHover || reviewRating) ? 'text-accent fill-accent' : 'text-muted'}`} style={{ transition: 'color 0.15s ease' }} />
                  </button>
                ))}
                {reviewRating > 0 && <span className="text-sm font-mono text-accent ml-2">{reviewRating}/5</span>}
              </div>
              <Textarea
                placeholder="Share your thoughts on this jersey..."
                value={reviewComment}
                onChange={e => setReviewComment(e.target.value)}
                className="bg-card border-border rounded-none mb-3 min-h-[80px]"
                data-testid="review-comment-input"
              />
              <Button onClick={handleSubmitReview} disabled={submittingReview} className="rounded-none bg-primary text-primary-foreground hover:bg-primary/90" data-testid="submit-review-btn">
                {submittingReview ? 'Submitting...' : 'Submit Review'}
              </Button>
            </div>
          )}

          {/* Reviews List */}
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
                  {r.comment && <p className="text-sm text-muted-foreground leading-relaxed" style={{ fontFamily: 'DM Sans, sans-serif', textTransform: 'none' }}>{r.comment}</p>}
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
