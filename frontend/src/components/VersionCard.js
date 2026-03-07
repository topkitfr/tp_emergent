// src/components/VersionCard.js
import { toast } from 'sonner';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, Shirt, Plus, Check, Loader2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { proxyImageUrl, addToCollection } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function VersionCard({ version, onAddToCollection }) {
  const { user }   = useAuth();
  const navigate   = useNavigate();
  const kit        = version.master_kit || {};
  const photo      = version.front_photo || kit.front_photo;
  const [status, setStatus] = useState("idle");

  const handleAdd = async (e) => {
    e.stopPropagation();
    if (status !== "idle") return;
    setStatus("loading");
    try {
      await addToCollection({ version_id: version.version_id });
      setStatus("done");
      toast.success("Added to your collection 🎽");
    } catch (err) {
      if (err?.response?.status === 400) {
        setStatus("done");
        toast.info("Already in your collection");
      } else {
        console.error("addToCollection error:", err?.response?.data || err);
        setStatus("error");
        setTimeout(() => setStatus("idle"), 2000);
      }
    }
  };  // ← accolade + point-virgule manquants dans ton fichier

  return (
    <div
      data-testid={`version-card-${version.version_id}`}
      onClick={() => navigate(`/version/${version.version_id}`)}
      className="card-shimmer relative border border-border bg-card overflow-hidden group
                 hover:-translate-y-1 hover:border-primary/30 cursor-pointer"
      style={{ transition: 'transform 0.3s ease, border-color 0.3s ease' }}
    >
      <div className="aspect-[3/4] relative overflow-hidden bg-secondary">
        {photo ? (
          <img
            src={proxyImageUrl(photo)}
            alt={`${kit.club} ${kit.season}`}
            className="w-full h-full object-cover group-hover:scale-105"
            style={{ transition: 'transform 0.5s ease' }}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Shirt className="w-12 h-12 text-muted-foreground" />
          </div>
        )}

        {/* Badge kit_type — top right */}
        <div className="absolute top-2 right-2">
          <Badge className="rounded-none text-[10px] bg-background/80 text-foreground backdrop-blur-sm border-none">
            {kit.kit_type}
          </Badge>
        </div>

        {/* Badge model — top left */}
        {version.model && (
          <div className="absolute top-2 left-2">
            <span className="font-mono text-[10px] px-1.5 py-0.5 bg-primary/90 text-primary-foreground">
              {version.model === "Authentic" ? "AUTH" : version.model === "Replica" ? "REP" : version.model}
            </span>
          </div>
        )}

        {/* Bouton + ajout direct */}
        {user && (
          <button
            onClick={handleAdd}
            className={`absolute bottom-2 right-2 rounded-full p-1.5 shadow-md transition-all
              opacity-0 group-hover:opacity-100
              ${status === "done"  ? "bg-green-500 text-white" : ""}
              ${status === "error" ? "bg-destructive text-white" : ""}
              ${status === "idle" || status === "loading" ? "bg-primary text-primary-foreground" : ""}
            `}
            title="Add to collection"
          >
            {status === "loading" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            {status === "done"    && <Check   className="w-3.5 h-3.5" />}
            {status === "idle"    && <Plus    className="w-3.5 h-3.5" />}
            {status === "error"   && <Plus    className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {/* Info */}
      <div className="p-3 space-y-1.5">
        <h3
          className="text-sm font-semibold tracking-tight truncate"
          style={{ fontFamily: 'Barlow Condensed, sans-serif', textTransform: 'uppercase' }}
        >
          {kit.club}
        </h3>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground" style={{ fontFamily: 'DM Sans, sans-serif' }}>
            {kit.season}
          </span>
          <span className="font-mono text-[10px] text-muted-foreground">{kit.brand}</span>
        </div>
        <p className="text-[10px] text-muted-foreground truncate" style={{ fontFamily: 'DM Sans, sans-serif' }}>
          {version.competition}
        </p>
        {version.avg_rating > 0 && (
          <div className="flex items-center gap-1">
            <Star className="w-3 h-3 text-accent fill-accent" />
            <span className="text-xs text-accent font-mono">{version.avg_rating}</span>
          </div>
        )}
      </div>
    </div>
  );
}
