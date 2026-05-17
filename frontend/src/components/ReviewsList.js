import { useState, useEffect } from "react";
import { Star } from "lucide-react";
import { getUserReviews, getUserReviewsSummary } from "@/lib/api";

function StarRow({ score, size = "w-4 h-4" }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(s => (
        <Star
          key={s}
          className={`${size} ${s <= score ? "text-yellow-400 fill-yellow-400" : "text-muted-foreground"}`}
        />
      ))}
    </div>
  );
}

export default function ReviewsList({ userId, compact = false }) {
  const [reviews, setReviews] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;
    setLoading(true);
    Promise.all([
      getUserReviews(userId),
      getUserReviewsSummary(userId),
    ])
      .then(([revRes, sumRes]) => {
        setReviews(revRes.data || []);
        setSummary(sumRes.data || { avg_score: 0.0, count: 0 });
      })
      .catch(() => {
        setReviews([]);
        setSummary({ avg_score: 0.0, count: 0 });
      })
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground py-1">
        <div className="w-16 h-3 bg-muted animate-pulse rounded" />
      </div>
    );
  }

  const count = summary?.count ?? 0;
  const avg = summary?.avg_score ?? 0;

  // Summary line (used in compact mode and as header in full mode)
  const summaryLine = (
    <div className="flex items-center gap-2">
      {count > 0 ? (
        <>
          <StarRow score={Math.round(avg)} size="w-4 h-4" />
          <span className="text-sm font-semibold" style={{ fontFamily: "Barlow Condensed" }}>
            {avg.toFixed(1)}
          </span>
          <span className="text-xs text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
            ({count} avis)
          </span>
        </>
      ) : (
        <span className="text-xs text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
          Aucun avis pour l'instant
        </span>
      )}
    </div>
  );

  if (compact) {
    return summaryLine;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm uppercase tracking-wider" style={{ fontFamily: "Barlow Condensed" }}>
          Réputation
        </h3>
        {summaryLine}
      </div>

      {reviews.length === 0 ? (
        <p className="text-xs text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
          Aucun avis pour l'instant
        </p>
      ) : (
        <div className="space-y-3">
          {reviews.map(review => (
            <div key={review.review_id} className="border border-border bg-card p-3 space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <StarRow score={review.score} size="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold" style={{ fontFamily: "Barlow Condensed" }}>
                    {review.score}/5
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted-foreground font-mono">
                    {new Date(review.created_at).toLocaleDateString("fr-FR")}
                  </p>
                  <p className="text-[10px] text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
                    par @{review.reviewer_username} ·{" "}
                    <span className="capitalize">
                      {review.role === "buyer" ? "Acheteur" : "Vendeur"}
                    </span>
                  </p>
                </div>
              </div>
              {review.comment && (
                <p className="text-xs text-muted-foreground" style={{ fontFamily: "DM Sans" }}>
                  {review.comment}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
