import JerseyCard from "../JerseyCard";
import React, { useEffect, useState } from "react";
import { getVersions } from "../../lib/api";


function LatestAdditionsSection() {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchLatest() {
      try {
        setLoading(true);
        setError(null);
        // Appel de l'API : /api/versions?limit=6
        const response = await getVersions({ limit: 6 });
        setVersions(response.data);
      } catch (e) {
        console.error("Erreur chargement latest versions", e);
        setError("Impossible de charger les derniers kits.");
      } finally {
        setLoading(false);
      }
    }

    fetchLatest();
  }, []);

  if (loading) {
    return (
      <section className="latest-additions">
        <h2>Latest additions</h2>
        <p>Chargement des derniers maillots…</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="latest-additions">
        <h2>Latest additions</h2>
        <p>{error}</p>
      </section>
    );
  }

  if (!versions.length) {
    return null;
  }

  return (
    <section className="latest-additions">
      <div className="latest-additions-header">
        <div>
          <h2>Latest additions</h2>
          <p>Les derniers kits version ajoutés au catalogue.</p>
        </div>
      </div>

      <div className="latest-additions-grid">
        {versions.map((version) => (
          <div
  key={version.version_id}
  className="latest-additions-card"
>
  <div className="latest-additions-badge">NEW</div>
  <JerseyCard kit={version.master_kit || version} />
</div>
        ))}
      </div>
    </section>
  );
}

export default LatestAdditionsSection;
