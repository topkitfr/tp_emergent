// src/pages/VersionDetail.js
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { User, Star, ArrowLeft, Shirt } from "lucide-react";
import { proxyImageUrl } from "@/lib/utils";

export default function VersionDetail() {
  const { versionId } = useParams();
  const [version, setVersion]   = useState(null);
  const [wornBy,  setWornBy]    = useState([]);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`/api/versions/${versionId}`).then((r) => r.json()),
      fetch(`/api/versions/${versionId}/worn-by`).then((r) => r.json()),
    ]).then(([versionData, wornByData]) => {
      setVersion(versionData);
      setWornBy(Array.isArray(wornByData) ? wornByData : []);
      setLoading(false);
    });
  }, [versionId]);

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-muted-foreground">
      Loading...
    </div>
  );
  if (!version) return (
    <div className="flex items-center justify-center h-64 text-muted-foreground">
      Version not found.
    </div>
  );

  const kit = version.master_kit || {};

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">

      {/* ── Back ── */}
      <Link to="/browse" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="w-4 h-4" /> Back to Browse
      </Link>

      {/* ── Header ── */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Club cliquable → /teams/:slug */}
          {kit.team_slug ? (
            <Link to={`/teams/${kit.team_slug}`} className="text-2xl font-bold hover:underline">
              {kit.club}
            </Link>
          ) : (
            <h1 className="text-2xl font-bold">{kit.club ?? "Unknown club"}</h1>
          )}
          <span className="text-muted-foreground text-xl">·</span>
          <span className="text-xl text-muted-foreground">{kit.season}</span>
        </div>

        <div className="flex items-center gap-2 flex-wrap text-sm text-muted-foreground">
          <span>{version.competition}</span>
          <span>·</span>
          <span>{version.model}</span>
          {kit.brand && <><span>·</span><span>{kit.brand}</span></>}
        </div>

        {version.avg_rating > 0 && (
          <div className="flex items-center gap-1 text-sm text-yellow-500">
            <Star className="w-4 h-4 fill-yellow-400" />
            {version.avg_rating.toFixed(1)}
            <span className="text-muted-foreground">({version.review_count} reviews)</span>
          </div>
        )}
      </div>

      {/* ── Photos ── */}
      <div className="flex gap-6 flex-wrap">
        {[version.front_photo, version.back_photo].map((photo, i) =>
          photo ? (
            <div key={i} className="flex flex-col items-center gap-1">
              <img
                src={proxyImageUrl(photo)}
                alt={i === 0 ? "Front" : "Back"}
                className="w-52 h-52 rounded-xl border object-contain bg-muted p-2"
              />
              <span className="text-xs text-muted-foreground">{i === 0 ? "Front" : "Back"}</span>
            </div>
          ) : null
        )}
      </div>

      {/* ── Métadonnées ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
        {[
          { label: "SKU",         value: version.sku_code },
          { label: "EAN",         value: version.ean_code },
          { label: "In collections", value: version.collection_count > 0 ? `${version.collection_count} collectors` : null },
        ].filter((f) => f.value).map(({ label, value }) => (
          <div key={label} className="bg-muted rounded-lg p-3">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="font-medium mt-0.5">{value}</p>
          </div>
        ))}
      </div>

      {/* ── Players who wore this kit ── */}
      {wornBy.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-4">Players who wore this kit</h2>
          <div className="flex flex-wrap gap-4">
            {wornBy.map((player) => (
              <Link
                key={player.player_id}
                to={`/players/${player.slug}`}
                className="flex flex-col items-center gap-2 group w-16"
              >
                <div className="w-14 h-14 rounded-full overflow-hidden bg-muted border-2 border-transparent group-hover:border-primary transition-colors">
                  {player.photo_url ? (
                    <img
                      src={proxyImageUrl(player.photo_url)}
                      alt={player.full_name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <User className="w-6 h-6 text-muted-foreground" />
                    </div>
                  )}
                </div>
                <span className="text-xs text-center leading-tight group-hover:underline line-clamp-2">
                  {player.full_name}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ── Reviews ── */}
      {version.reviews?.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-4">Reviews</h2>
          <div className="space-y-3">
            {version.reviews.map((review) => (
              <div key={review.review_id} className="border rounded-xl p-4 space-y-1">
                <div className="flex items-center gap-2">
                  {review.user_picture && (
                    <img src={proxyImageUrl(review.user_picture)} alt="" className="w-7 h-7 rounded-full" />
                  )}
                  <span className="font-medium text-sm">{review.user_name || "Anonymous"}</span>
                  <div className="flex items-center gap-0.5 ml-auto">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className={`w-3.5 h-3.5 ${i < review.rating ? "fill-yellow-400 text-yellow-400" : "text-muted-foreground"}`} />
                    ))}
                  </div>
                </div>
                {review.comment && <p className="text-sm text-muted-foreground">{review.comment}</p>}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
