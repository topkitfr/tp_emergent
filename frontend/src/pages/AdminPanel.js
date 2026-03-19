import React, { useEffect, useState, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Navigate } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const LABELS = {
  team: { id: "team_id", name: "name" },
  league: { id: "league_id", name: "name" },
  brand: { id: "brand_id", name: "name" },
  player: { id: "player_id", name: "full_name" },
};

// ─── Onglet Import CSV ────────────────────────────────────────────────────────
function CsvImportTab() {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.name.endsWith(".csv")) {
      setFile(dropped);
      setResult(null);
      setError(null);
    } else {
      setError("Veuillez déposer un fichier .csv");
    }
  };

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setResult(null);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API}/admin/import-csv`, {
        method: "POST",
        credentials: "include",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Erreur lors de l'import");
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Erreur réseau : " + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-lg font-semibold mb-1">Import CSV</h2>
      <p className="text-sm text-gray-400 mb-5">
        Colonnes attendues :{" "}
        <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded text-xs">
          team, season, type, design, colors, brand, sponsor, league, gender, img_url, source_url
        </code>
        <br />
        Les doublons (même team + season + type) sont automatiquement ignorés.
      </p>

      {/* Zone drag & drop */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
          ${dragging ? "border-blue-500 bg-blue-50 dark:bg-blue-950/30" : "border-gray-300 dark:border-gray-600 hover:border-gray-400"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleFileChange}
        />
        {file ? (
          <div>
            <p className="text-sm font-medium text-green-600">📄 {file.name}</p>
            <p className="text-xs text-gray-400 mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-500">
              Glissez-déposez votre fichier CSV ici, ou{" "}
              <span className="text-blue-500 underline">cliquez pour sélectionner</span>
            </p>
          </div>
        )}
      </div>

      {/* Bouton import */}
      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors"
        >
          {uploading ? "Import en cours…" : "Lancer l'import"}
        </button>
      )}

      {/* Erreur */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 font-medium">❌ {error}</p>
        </div>
      )}

      {/* Résultat */}
      {result && (
        <div className="mt-4 p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm font-semibold text-green-700 mb-2">✅ Import terminé</p>
          <div className="grid grid-cols-3 gap-3 mb-3">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{result.created}</p>
              <p className="text-xs text-gray-500">créés</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-500">{result.skipped}</p>
              <p className="text-xs text-gray-500">ignorés</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-500">{result.total_rows}</p>
              <p className="text-xs text-gray-500">lignes total</p>
            </div>
          </div>
          {result.errors && result.errors.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-red-600 mb-1">
                {result.errors.length} erreur(s) :
              </p>
              <ul className="text-xs text-red-500 space-y-0.5 max-h-40 overflow-y-auto">
                {result.errors.map((e, i) => (
                  <li key={i} className="font-mono">{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Onglet Entités en attente ────────────────────────────────────────────────
function PendingEntitiesTab() {
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

  useEffect(() => { fetchPending(); }, []);

  const totalCount = Object.values(pending).reduce((acc, arr) => acc + arr.length, 0);

  const handleAction = async (entityType, entityId, action) => {
    try {
      const res = await fetch(
        `${API}/entities/${entityType}/${entityId}/${action}`,
        { method: "PATCH", credentials: "include" }
      );
      if (!res.ok) return;
      await fetchPending();
    } catch (err) {
      console.error("Error updating entity", err);
    }
  };

  if (loading) return <p className="text-sm text-gray-400">Chargement…</p>;
  if (totalCount === 0)
    return <p className="text-sm text-green-600">✅ Aucune entité en attente.</p>;

  return (
    <>
      <p className="text-sm text-gray-400 mb-6">{totalCount} entité(s) à valider</p>
      {Object.entries(LABELS).map(([type, config]) =>
        pending[type].length > 0 ? (
          <div key={type} className="mb-8">
            <h2 className="text-base font-semibold capitalize mb-3 border-b border-gray-200 dark:border-gray-700 pb-1">
              {type}s ({pending[type].length})
            </h2>
            <div className="space-y-2">
              {pending[type].map((entity) => (
                <div
                  key={entity[config.id]}
                  className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3 border border-gray-200 dark:border-gray-700"
                >
                  <div>
                    <p className="font-medium text-sm">{entity[config.name]}</p>
                    <p className="text-xs text-gray-400">{entity[config.id]}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleAction(type, entity[config.id], "approve")}
                      className="bg-green-500 hover:bg-green-600 text-white text-xs px-3 py-1.5 rounded-md"
                    >
                      Approuver
                    </button>
                    <button
                      onClick={() => handleAction(type, entity[config.id], "reject")}
                      className="bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1.5 rounded-md"
                    >
                      Rejeter
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null
      )}
    </>
  );
}

// ─── Composant principal ──────────────────────────────────────────────────────
export default function AdminPanel() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("pending");

  // TEMPORAIRE : accès forcé pour debug, tu remettras la condition plus tard
  const isAdmin = true;
  // const isAdmin = user && (user.role === "admin" || user.role === "moderator");

  if (!isAdmin) return <Navigate to="/" />;

  const tabs = [
    { id: "pending", label: "Entités en attente" },
    { id: "csv", label: "Import CSV" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Administration</h1>

      {/* Onglets */}
      <div className="flex gap-1 mb-8 border-b border-gray-200 dark:border-gray-700">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px
              ${activeTab === tab.id
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Contenu */}
      {activeTab === "pending" && <PendingEntitiesTab />}
      {activeTab === "csv" && <CsvImportTab />}
    </div>
  );
}
