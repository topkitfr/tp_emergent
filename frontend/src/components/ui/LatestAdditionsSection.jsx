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
        const response = await getMasterKits({ limit: 4 });
        setKits(response.data);
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
        <p className="text-sm text-muted-foreground mb-8">Chargement des derniers maillots…</p>
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

  if (!kits.length) return null;

  return (
    <div>
      <h2 className="text-lg md:text-xl mb-2 text-muted-foreground">LATEST ADDITIONS</h2>
      <p className="text-sm text-muted-foreground mb-8">Les derniers kits version ajoutés au catalogue.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kits.map((kit) => (
  <JerseyCard key={kit._id} kit={kit} showNew={true} />
))}

      </div>
    </div>
  );
}

export default LatestAdditionsSection;
