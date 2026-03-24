import JerseyCard from "../JerseyCard";
import React, { useEffect, useState } from "react";
import { getMasterKits } from "../../lib/api";

function LatestAdditionsSection() {
  const [kits, setKits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchLatest() {
      try {
        setLoading(true);
        setError(null);
        const response = await getMasterKits({
          limit: 4,
          sort_by: "created_at",
          order: "desc",
        });
        setKits(response.data?.items ?? response.data ?? []);
      } catch (e) {
        console.error("Erreur chargement latest kits", e);
        setError("Impossible de charger les derniers kits.");
      } finally {
        setLoading(false);
      }
    }
    fetchLatest();
  }, []);

  if (loading) {
    return (
      <div>
        <h2 className="text-lg md:text-xl mb-2 text-muted-foreground">LATEST ADDITIONS</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="aspect-[3/4] bg-card animate-pulse border border-border" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2 className="text-lg md:text-xl mb-2 text-muted-foreground">LATEST ADDITIONS</h2>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (!kits.length) {
    return (
      <div>
        <h2 className="text-lg md:text-xl mb-2 text-muted-foreground">LATEST ADDITIONS</h2>
        <p className="text-sm text-muted-foreground">Aucun kit disponible pour le moment.</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-lg md:text-xl mb-2 text-muted-foreground">LATEST ADDITIONS</h2>
      <p className="text-sm text-muted-foreground mb-8">Les derniers kits ajoutés au catalogue.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kits.map((kit) => (
          <JerseyCard key={kit._id} kit={kit} showNew={true} />
        ))}
      </div>
    </div>
  );
}

export default LatestAdditionsSection;
