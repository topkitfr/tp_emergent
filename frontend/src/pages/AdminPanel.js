import React, { useEffect, useState, useRef } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Navigate } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const LABELS = {
  team:   { id: "team_id",   name: "name" },
  league: { id: "league_id", name: "name" },
  brand:  { id: "brand_id",  name: "name" },
  player: { id: "player_id", name: "full_name" },
};

// ─── Onglet Import CSV ────────────────────────────────────────────────────────
function CsvImportTab() {
  const [dragging, setDragging]   = useState(false);
  const [file, setFile]           = useState(null);
  const [mode, setMode]           = useState("reset"); // "reset" | "append"
  const [uploading, setUploading] = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.name.endsWith(".csv")) {
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

    // Confirmation obligatoire pour le reset
    if (mode === "reset") {
      const ok = window.confirm(
        "⚠️ ATTENTION : cette opération va supprimer TOUS les kits, versions, teams, leagues et brands existants avant d'importer le nouveau CSV.\n\nContinuer ?"
      );
      if (!ok) return;
    }

    setUploading(true);
    setResult(null);
    setError(null);

    try {
      const endpoint =
        mode === "reset"
          ? `${API}/admin/reset-and-import-csv`
          : `${API}/admin/import-csv`;

      const formData = new FormData();
      formData.append("file", file);

      const res  = await fetch(endpoint, {
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
      </p>

      {/* Mode selector */}
      <div className="flex gap-3 mb-5">
        <label className={`flex items-start gap-2.5 cursor-pointer rounded-xl border p-4 flex-1 transition-colors
          ${mode === "reset"
            ? "border-red-400 bg-red-50 dark:bg-red-950/30"
            : "border-gray-200 dark:border-gray-700 hover:border-gray-300"}`}>
          <input
            type="radio"
            name="mode"
            value="reset"
            checked={mode === "reset"}
            onChange={() => setMode("reset")}
            className="mt-0.5"
          />
          <div>
            <p className="text-sm font-semibold text-red-600">Reset + Import</p>
            <p className="text-xs text-gray-500 mt-0.5">
              Supprime toute la base (kits, versions, teams, leagues, brands) puis importe le CSV.
              Les comptes utilisateurs et collections sont préservés.
            </p>
          </div>
        </label>

        <label className={`flex items-start gap-2.5 cursor-pointer rounded-xl border p-4 flex-1 transition-colors
          ${mode === "append"
            ? "border-blue-400 bg-blue-50 dark:bg-blue-950/30"
            : "border-gray-200 dark:border-gray-700 hover:border-gray-300"}`}>
          <input
            type="radio"
            name="mode"
            value="append"
            checked={mode === "append"}
            onChange={() => setMode("append")}
            className="mt-0.5"
          />
          <div>
            <p className="text-sm font-semibold text-blue-600">Ajout uniquement</p>
            <p className="text-xs text-gray-500 mt-0.5">
              Importe sans toucher à la base existante. Les doublons sont ignorés.
            </p>
          </div>
        </label>
      </div>

      {/* Zone drag & drop */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
          ${dragging
            ? "border-blue-500 bg-blue-50 dark:bg-blue-950/30"
            : "border-gray-300 dark:border-gray-600 hover:border-gray-400"}`}
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
            <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            Glissez-déposez votre CSV ici, ou{" "}
            <span className="text-blue-500 underline">cliquez pour sélectionner</span>
          </p>
        )}
      </div>

      {/* Bouton */}
      {file && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className={`mt-4 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50
            ${mode === "reset"
              ? "bg-red-600 hover:bg-red-700"
              : "bg-blue-600 hover:bg-blue-700"}`}
        >
          {uploading
            ? "Import en cours…"
            : mode === "reset"
            ? "⚠️ Reset + Importer"
            : "Importer (ajout)"}
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
          <p className="text-sm font-semibold text-green-700 mb-3">✅ {result.message}</p>

          {/* Stats kits */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center bg-white dark:bg-gray-900 rounded-lg p-3">
              <p className="text-2xl font-bold text-green-600">{result.kits_created ?? result.created}</p>
              <p className="text-xs text-gray-500">kits créés</p>
            </div>
            <div className="text-center bg-white dark:bg-gray-900 rounded-lg p-3">
              <p className="text-2xl font-bold text-yellow-500">{result.rows_skipped ?? result.skipped}</p>
              <p className="text-xs text-gray-500">lignes ignorées</p>
            </div>
            <div className="text-center bg-white dark:bg-gray-900 rounded-lg p-3">
              <p className="text-2xl font-bold text-gray-500">{result.rows_total ?? result.total_rows}</p>
              <p className="text-xs text-gray-500">lignes total</p>
            </div>
          </div>

          {/* Stats entités (mode reset) */}
          {result.teams_created !== undefined && (
            <div className="grid grid-cols-4 gap-2 mb-4">
              {[
                { label: "teams",   value: result.teams_created },
                { label: "ligues",  value: result.leagues_created },
                { label: "marques", value: result.brands_created },
                { label: "versions",value: result.versions_created },
              ].map(({ label, value }) => (
                <div key={label} className="text-center bg-white dark:bg-gray-900 rounded-lg p-2">
                  <p className="text-lg font-bold text-blue-500">{value}</p>
                  <p className="text-xs text-gray-500">{label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Erreurs */}
          {result.errors?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-red-600 mb-1">
                {result.errors.length} erreur(s) :
              </p>
              <ul className="text-xs text-red-500 space-y-0.5 max-h-40 overflow-y-auto font-mono">
                {result.errors.map((e, i) => <li key={i}>{e}</li>)}
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
  const [pending, setPending] = useState({ team: [], league: [], brand: [], player: [] });
  const [loading, setLoading] = useState(true);

  const fetchPending = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API}/entities/pending`, { credentials: "include" });
      if (!res.ok) { setPending({ team: [], league: [], brand: [], player: [] }); return; }
      const data = await res.json();
      setPending({
        team:   data.team   || [],
        league: data.league || [],
        brand:  data.brand  || [],
        player: data.player || [],
      });
    } catch (err) {
      console.error("Error fetching pending entities", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPending(); }, []);

  const totalCount = Object.values(pending).reduce((acc, arr) => acc + arr.length, 0);

  const handleAction = async (entityType, entityId, action) => {
    try {
      const res = await fetch(`${API}/entities/${entityType}/${entityId}/${action}`, {
        method: "PATCH",
        credentials: "include",
      });
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
    { id: "csv",     label: "Import CSV" },
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

      {activeTab === "pending" && <PendingEntitiesTab />}
      {activeTab === "csv"     && <CsvImportTab />}
    </div>
  );
}
