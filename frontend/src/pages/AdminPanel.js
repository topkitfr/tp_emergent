import React, { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Navigate } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const LABELS = {
  team: { id: "team_id", name: "name" },
  league: { id: "league_id", name: "name" },
  brand: { id: "brand_id", name: "name" },
  player: { id: "player_id", name: "full_name" },
};

export default function AdminPanel() {
  const { user } = useAuth();

  // TEMPORAIRE : accès forcé pour debug, tu remettras la condition plus tard
  const isAdmin = true;
  // Si tu veux la vraie condition ensuite :
  // const isAdmin = user && (user.role === "admin" || user.role === "moderator");

  console.log("ADMIN USER =", user);
  console.log("IS_ADMIN =", isAdmin);

  const [pending, setPending] = useState({
    team: [],
    league: [],
    brand: [],
    player: [],
  });
  const [loading, setLoading] = useState(true);

  const fetchPending = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/entities/pending`, {
        credentials: "include",
      });

      if (!res.ok) {
        console.error("Failed to fetch pending entities", res.status);
        setPending({ team: [], league: [], brand: [], player: [] });
        return;
      }

      const data = await res.json();

      setPending({
        team: data.team || [],
        league: data.league || [],
        brand: data.brand || [],
        player: data.player || [],
      });
    } catch (err) {
      console.error("Error fetching pending entities", err);
      setPending({ team: [], league: [], brand: [], player: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAdmin) {
      fetchPending();
    }
  }, [isAdmin]);

  if (!isAdmin) {
    return <Navigate to="/" />;
  }

  const totalCount = Object.values(pending).reduce(
    (acc, arr) => acc + arr.length,
    0
  );

  const handleAction = async (entityType, entityId, action) => {
    try {
      const res = await fetch(
        `${API}/entities/${entityType}/${entityId}/${action}`,
        {
          method: "PATCH",
          credentials: "include",
        }
      );

      if (!res.ok) {
        console.error("Failed to update entity", res.status);
        return;
      }

      await fetchPending();
    } catch (err) {
      console.error("Error updating entity", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-2">Admin — Entités en attente</h1>
      <p className="text-gray-500 mb-8">{totalCount} entité(s) à valider</p>

      {loading ? (
        <p>Chargement...</p>
      ) : totalCount === 0 ? (
        <p className="text-green-600">✅ Aucune entité en attente.</p>
      ) : (
        Object.entries(LABELS).map(([type, config]) =>
          pending[type].length > 0 ? (
            <div key={type} className="mb-8">
              <h2 className="text-lg font-semibold capitalize mb-3 border-b pb-1">
                {type}s ({pending[type].length})
              </h2>
              <div className="space-y-2">
                {pending[type].map((entity) => (
                  <div
                    key={entity[config.id]}
                    className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-3 border"
                  >
                    <div>
                      <p className="font-medium">{entity[config.name]}</p>
                      <p className="text-xs text-gray-400">
                        {entity[config.id]}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() =>
                          handleAction(type, entity[config.id], "approve")
                        }
                        className="bg-green-500 hover:bg-green-600 text-white text-sm px-3 py-1 rounded"
                      >
                        Approuver
                      </button>
                      <button
                        onClick={() =>
                          handleAction(type, entity[config.id], "reject")
                        }
                        className="bg-red-500 hover:bg-red-600 text-white text-sm px-3 py-1 rounded"
                      >
                        Rejeter
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null
        )
      )}
    </div>
  );
}
