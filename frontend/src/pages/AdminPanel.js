import React, { useEffect, useState, useRef, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Navigate } from "react-router-dom";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const LABELS = {
  team:   { id: "team_id",   name: "name" },
  league: { id: "league_id", name: "name" },
  brand:  { id: "brand_id",  name: "name" },
  player: { id: "player_id", name: "full_name" },
};

// ─── helpers ──────────────────────────────────────────────────────────────────
const apiFetch = (path, opts = {}) =>
  fetch(`${API}${path}`, { credentials: "include", ...opts });

// ─── Onglet Stats ─────────────────────────────────────────────────────────────
function StatsTab() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiFetch("/admin/stats")
      .then((r) => r.ok ? r.json() : Promise.reject(r.status))
      .then(setStats)
      .catch(() => setError("Impossible de charger les stats"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-sm text-gray-400">Chargement…</p>;
  if (error)   return <p className="text-sm text-red-500">{error}</p>;

  const cards = [
    { label: "Utilisateurs",   value: stats.users_total,          sub: `${stats.users_banned} bannis` },
    { label: "Kits",           value: stats.kits_total,           sub: null },
    { label: "Soumissions",    value: stats.submissions_total,    sub: `${stats.submissions_pending} en attente` },
    { label: "Signalements",   value: stats.reports_total,        sub: `${stats.reports_pending} en attente` },
    { label: "Admins",         value: stats.admins_count,         sub: null },
    { label: "Modérateurs",    value: stats.moderators_count,     sub: null },
  ];

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Vue d'ensemble</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {cards.map(({ label, value, sub }) => (
          <div key={label} className="bg-gray-50 dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-2xl font-bold">{value ?? "—"}</p>
            <p className="text-sm text-gray-500">{label}</p>
            {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Onglet Users ─────────────────────────────────────────────────────────────
function UsersTab() {
  const [users, setUsers]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [page, setPage]         = useState(1);
  const [total, setTotal]       = useState(0);
  const [search, setSearch]     = useState("");
  const [roleFilter, setRole]   = useState("");
  const [bannedFilter, setBanned] = useState("");
  const [actionMsg, setMsg]     = useState(null);
  const PER_PAGE = 20;

  const load = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({ page, per_page: PER_PAGE });
    if (search)      params.set("search", search);
    if (roleFilter)  params.set("role", roleFilter);
    if (bannedFilter !== "") params.set("banned", bannedFilter);
    apiFetch(`/admin/users?${params}`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => { setUsers(d.users); setTotal(d.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search, roleFilter, bannedFilter]);

  useEffect(() => { load(); }, [load]);

  const action = async (userId, act) => {
    setMsg(null);
    const r = await apiFetch(`/admin/users/${userId}/${act}`, { method: "POST" });
    const d = await r.json();
    setMsg(r.ok ? { ok: true, text: d.message } : { ok: false, text: d.detail });
    load();
  };

  const totalPages = Math.ceil(total / PER_PAGE);
  const ROLE_BADGE = { admin: "bg-red-100 text-red-700", moderator: "bg-yellow-100 text-yellow-700", user: "bg-gray-100 text-gray-600" };

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Utilisateurs ({total})</h2>

      {/* Filtres */}
      <div className="flex flex-wrap gap-2 mb-4">
        <input
          className="border dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm bg-white dark:bg-gray-800 flex-1 min-w-[160px]"
          placeholder="Rechercher (nom, email…)"
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        <select
          className="border dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm bg-white dark:bg-gray-800"
          value={roleFilter}
          onChange={(e) => { setRole(e.target.value); setPage(1); }}
        >
          <option value="">Tous les rôles</option>
          <option value="admin">Admin</option>
          <option value="moderator">Modérateur</option>
          <option value="user">User</option>
        </select>
        <select
          className="border dark:border-gray-600 rounded-lg px-3 py-1.5 text-sm bg-white dark:bg-gray-800"
          value={bannedFilter}
          onChange={(e) => { setBanned(e.target.value); setPage(1); }}
        >
          <option value="">Tous</option>
          <option value="true">Bannis</option>
          <option value="false">Actifs</option>
        </select>
      </div>

      {actionMsg && (
        <div className={`mb-3 px-3 py-2 rounded-lg text-sm ${
          actionMsg.ok ? "bg-green-50 text-green-700 dark:bg-green-950/30" : "bg-red-50 text-red-700 dark:bg-red-950/30"
        }`}>
          {actionMsg.ok ? "✅" : "❌"} {actionMsg.text}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-gray-400">Chargement…</p>
      ) : (
        <div className="space-y-2">
          {users.map((u) => (
            <div key={u._id} className="flex flex-wrap items-center justify-between gap-2 bg-gray-50 dark:bg-gray-800 rounded-xl px-4 py-3 border border-gray-200 dark:border-gray-700">
              <div className="min-w-0">
                <p className="font-medium text-sm truncate">{u.username} {u.is_banned && <span className="text-xs text-red-500">🚫 banni</span>}</p>
                <p className="text-xs text-gray-400 truncate">{u.email}</p>
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_BADGE[u.role] || ROLE_BADGE.user}`}>
                  {u.role}
                </span>
                {!u.is_banned
                  ? <button onClick={() => action(u._id, "ban")}   className="text-xs bg-red-500 hover:bg-red-600 text-white px-2.5 py-1 rounded-md">Bannir</button>
                  : <button onClick={() => action(u._id, "unban")} className="text-xs bg-green-500 hover:bg-green-600 text-white px-2.5 py-1 rounded-md">Débannir</button>
                }
                {u.role === "user" &&
                  <button onClick={() => action(u._id, "promote")} className="text-xs bg-yellow-500 hover:bg-yellow-600 text-white px-2.5 py-1 rounded-md">Promouvoir</button>
                }
                {u.role === "moderator" &&
                  <button onClick={() => action(u._id, "demote")}  className="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2.5 py-1 rounded-md">Rétrograder</button>
                }
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex gap-2 mt-4 justify-center">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 text-sm border rounded-lg disabled:opacity-40 dark:border-gray-600">
            ← Préc
          </button>
          <span className="text-sm text-gray-500 self-center">{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 text-sm border rounded-lg disabled:opacity-40 dark:border-gray-600">
            Suiv →
          </button>
        </div>
      )}
    </div>
  );
}

// ─── Onglet Soumissions ───────────────────────────────────────────────────────
function SubmissionsTab() {
  const [subs, setSubs]       = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage]       = useState(1);
  const [total, setTotal]     = useState(0);
  const [msg, setMsg]         = useState(null);
  const PER_PAGE = 20;

  const load = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({ page, per_page: PER_PAGE, status: "pending" });
    apiFetch(`/submissions?${params}`)
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => {
        setSubs(Array.isArray(d) ? d : d.submissions || []);
        setTotal(d.total ?? (Array.isArray(d) ? d.length : 0));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  useEffect(() => { load(); }, [load]);

  const action = async (subId, act) => {
    setMsg(null);
    const r = await apiFetch(`/admin/submissions/${subId}/${act}`, { method: "POST" });
    const d = await r.json();
    setMsg(r.ok ? { ok: true, text: d.message } : { ok: false, text: d.detail });
    load();
  };

  const TYPE_COLORS = {
    master_kit: "bg-blue-100 text-blue-700",
    version:    "bg-purple-100 text-purple-700",
    team:       "bg-green-100 text-green-700",
    league:     "bg-yellow-100 text-yellow-700",
    brand:      "bg-orange-100 text-orange-700",
    player:     "bg-pink-100 text-pink-700",
  };

  const totalPages = Math.ceil(total / PER_PAGE);

  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">Soumissions en attente ({total})</h2>

      {msg && (
        <div className={`mb-3 px-3 py-2 rounded-lg text-sm ${
          msg.ok ? "bg-green-50 text-green-700 dark:bg-green-950/30" : "bg-red-50 text-red-700 dark:bg-red-950/30"
        }`}>
          {msg.ok ? "✅" : "❌"} {msg.text}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-gray-400">Chargement…</p>
      ) : subs.length === 0 ? (
        <p className="text-sm text-green-600">✅ Aucune soumission en attente.</p>
      ) : (
        <div className="space-y-2">
          {subs.map((s) => (
            <div key={s._id} className="flex flex-wrap items-center justify-between gap-2 bg-gray-50 dark:bg-gray-800 rounded-xl px-4 py-3 border border-gray-200 dark:border-gray-700">
              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TYPE_COLORS[s.submission_type] || "bg-gray-100 text-gray-600"}`}>
                    {s.submission_type}
                  </span>
                  <p className="text-sm font-medium truncate">{s.data?.name || s.data?.full_name || s._id}</p>
                </div>
                <p className="text-xs text-gray-400">par {s.submitted_by} · {new Date(s.created_at).toLocaleDateString("fr-FR")}</p>
              </div>
              <div className="flex gap-2">
                <button onClick={() => action(s._id, "approve")} className="text-xs bg-green-500 hover:bg-green-600 text-white px-2.5 py-1 rounded-md">Approuver</button>
                <button onClick={() => action(s._id, "reject")}  className="text-xs bg-red-500 hover:bg-red-600 text-white px-2.5 py-1 rounded-md">Rejeter</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex gap-2 mt-4 justify-center">
          <button disabled={page <= 1} onClick={() => setPage(p => p - 1)}
            className="px-3 py-1 text-sm border rounded-lg disabled:opacity-40 dark:border-gray-600">← Préc</button>
          <span className="text-sm text-gray-500 self-center">{page} / {totalPages}</span>
          <button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}
            className="px-3 py-1 text-sm border rounded-lg disabled:opacity-40 dark:border-gray-600">Suiv →</button>
        </div>
      )}
    </div>
  );
}

// ─── Onglet Maintenance ───────────────────────────────────────────────────────
function MaintenanceTab() {
  const [status, setStatus]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [toggling, setToggle] = useState(false);
  const [msg, setMsg]         = useState(null);

  const load = () => {
    setLoading(true);
    apiFetch("/admin/maintenance")
      .then((r) => r.ok ? r.json() : Promise.reject())
      .then((d) => setStatus(d.maintenance_mode))
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const toggle = async () => {
    const next = !status;
    if (!window.confirm(`Passer le site en mode ${next ? "MAINTENANCE" : "NORMAL"} ?`)) return;
    setToggle(true);
    setMsg(null);
    const r = await apiFetch("/admin/maintenance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: next }),
    });
    const d = await r.json();
    if (r.ok) { setStatus(d.maintenance_mode); setMsg({ ok: true, text: d.message }); }
    else      { setMsg({ ok: false, text: d.detail }); }
    setToggle(false);
  };

  return (
    <div className="max-w-lg">
      <h2 className="text-lg font-semibold mb-4">Mode maintenance</h2>
      <p className="text-sm text-gray-500 mb-6">
        Quand activé, toutes les routes API renvoient 503 sauf <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">/api/admin/*</code> et les routes d'auth.
        Le front affiche une page de maintenance.
      </p>

      {loading ? (
        <p className="text-sm text-gray-400">Chargement…</p>
      ) : (
        <div className="flex items-center gap-4">
          <div className={`w-3 h-3 rounded-full ${status ? "bg-red-500" : "bg-green-500"}`} />
          <span className="text-sm font-medium">
            Statut actuel : <strong>{status ? "🔴 Maintenance" : "🟢 Normal"}</strong>
          </span>
          <button
            onClick={toggle}
            disabled={toggling}
            className={`text-sm font-medium px-4 py-2 rounded-lg text-white transition-colors disabled:opacity-50 ${
              status ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"
            }`}
          >
            {toggling ? "…" : status ? "Désactiver" : "Activer la maintenance"}
          </button>
        </div>
      )}

      {msg && (
        <div className={`mt-4 px-3 py-2 rounded-lg text-sm ${
          msg.ok ? "bg-green-50 text-green-700 dark:bg-green-950/30" : "bg-red-50 text-red-700 dark:bg-red-950/30"
        }`}>
          {msg.ok ? "✅" : "❌"} {msg.text}
        </div>
      )}
    </div>
  );
}

// ─── Onglet Import CSV ────────────────────────────────────────────────────────
function CsvImportTab() {
  const [dragging, setDragging]   = useState(false);
  const [file, setFile]           = useState(null);
  const [mode, setMode]           = useState("reset");
  const [uploading, setUploading] = useState(false);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const inputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault(); setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.name.endsWith(".csv")) { setFile(dropped); setResult(null); setError(null); }
    else setError("Veuillez déposer un fichier .csv");
  };

  const handleUpload = async () => {
    if (!file) return;
    if (mode === "reset") {
      const ok = window.confirm("⚠️ Cette opération supprime TOUS les kits, versions, teams, leagues et brands. Continuer ?");
      if (!ok) return;
    }
    setUploading(true); setResult(null); setError(null);
    try {
      const endpoint = mode === "reset" ? `${API}/admin/reset-and-import-csv` : `${API}/admin/import-csv`;
      const formData = new FormData();
      formData.append("file", file);
      const res  = await fetch(endpoint, { method: "POST", credentials: "include", body: formData });
      const data = await res.json();
      if (!res.ok) setError(data.detail || "Erreur lors de l'import");
      else setResult(data);
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
        Colonnes : <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded text-xs">team, season, type, design, colors, brand, sponsor, league, gender, img_url, source_url</code>
      </p>

      <div className="flex gap-3 mb-5">
        {[["reset",  "Reset + Import",    "Supprime toute la base puis importe.",          "red"],
          ["append", "Ajout uniquement",   "Importe sans toucher à la base existante.",    "blue"]
        ].map(([val, title, desc, color]) => (
          <label key={val} className={`flex items-start gap-2.5 cursor-pointer rounded-xl border p-4 flex-1 transition-colors
            ${mode === val ? `border-${color}-400 bg-${color}-50 dark:bg-${color}-950/30` : "border-gray-200 dark:border-gray-700 hover:border-gray-300"}`}>
            <input type="radio" name="mode" value={val} checked={mode === val} onChange={() => setMode(val)} className="mt-0.5" />
            <div>
              <p className={`text-sm font-semibold text-${color}-600`}>{title}</p>
              <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
            </div>
          </label>
        ))}
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors
          ${dragging ? "border-blue-500 bg-blue-50 dark:bg-blue-950/30" : "border-gray-300 dark:border-gray-600 hover:border-gray-400"}`}
      >
        <input ref={inputRef} type="file" accept=".csv" className="hidden" onChange={(e) => { setFile(e.target.files[0]); setResult(null); setError(null); }} />
        {file
          ? <div><p className="text-sm font-medium text-green-600">📄 {file.name}</p><p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p></div>
          : <p className="text-sm text-gray-500">Glissez-déposez votre CSV ici, ou <span className="text-blue-500 underline">cliquez pour sélectionner</span></p>
        }
      </div>

      {file && (
        <button onClick={handleUpload} disabled={uploading}
          className={`mt-4 text-white text-sm font-medium px-6 py-2.5 rounded-lg transition-colors disabled:opacity-50
            ${mode === "reset" ? "bg-red-600 hover:bg-red-700" : "bg-blue-600 hover:bg-blue-700"}`}>
          {uploading ? "Import en cours…" : mode === "reset" ? "⚠️ Reset + Importer" : "Importer (ajout)"}
        </button>
      )}

      {error && <div className="mt-4 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg"><p className="text-sm text-red-600">❌ {error}</p></div>}

      {result && (
        <div className="mt-4 p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
          <p className="text-sm font-semibold text-green-700 mb-3">✅ {result.message}</p>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[[result.kits_created ?? result.created, "kits créés"], [result.rows_skipped ?? result.skipped, "ignorées"], [result.rows_total ?? result.total_rows, "total"]]
              .map(([val, lbl]) => (
                <div key={lbl} className="text-center bg-white dark:bg-gray-900 rounded-lg p-3">
                  <p className="text-2xl font-bold text-green-600">{val}</p><p className="text-xs text-gray-500">{lbl}</p>
                </div>
              ))}
          </div>
          {result.errors?.length > 0 && (
            <><p className="text-xs font-semibold text-red-600 mb-1">{result.errors.length} erreur(s) :</p>
            <ul className="text-xs text-red-500 space-y-0.5 max-h-40 overflow-y-auto font-mono">{result.errors.map((e, i) => <li key={i}>{e}</li>)}</ul></>
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
      const res = await apiFetch("/entities/pending");
      if (!res.ok) { setPending({ team: [], league: [], brand: [], player: [] }); return; }
      const data = await res.json();
      setPending({ team: data.team || [], league: data.league || [], brand: data.brand || [], player: data.player || [] });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPending(); }, []);

  const totalCount = Object.values(pending).reduce((acc, arr) => acc + arr.length, 0);

  const handleAction = async (entityType, entityId, action) => {
    const res = await apiFetch(`/entities/${entityType}/${entityId}/${action}`, { method: "PATCH" });
    if (res.ok) fetchPending();
  };

  if (loading) return <p className="text-sm text-gray-400">Chargement…</p>;
  if (totalCount === 0) return <p className="text-sm text-green-600">✅ Aucune entité en attente.</p>;

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
                <div key={entity[config.id]}
                  className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-3 border border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="font-medium text-sm">{entity[config.name]}</p>
                    <p className="text-xs text-gray-400">{entity[config.id]}</p>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => handleAction(type, entity[config.id], "approve")}
                      className="bg-green-500 hover:bg-green-600 text-white text-xs px-3 py-1.5 rounded-md">Approuver</button>
                    <button onClick={() => handleAction(type, entity[config.id], "reject")}
                      className="bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1.5 rounded-md">Rejeter</button>
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
  const [activeTab, setActiveTab] = useState("stats");

  const isAdmin = user && ["admin", "moderator"].includes(user.role);
  if (!isAdmin) return <Navigate to="/" />;

  const tabs = [
    { id: "stats",       label: "📊 Stats" },
    { id: "users",       label: "👥 Users" },
    { id: "submissions", label: "📬 Soumissions" },
    { id: "maintenance", label: "🔧 Maintenance" },
    { id: "pending",     label: "⏳ Entités" },
    { id: "csv",         label: "📥 Import CSV" },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Administration</h1>

      <div className="flex flex-wrap gap-1 mb-8 border-b border-gray-200 dark:border-gray-700">
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

      {activeTab === "stats"       && <StatsTab />}
      {activeTab === "users"       && <UsersTab />}
      {activeTab === "submissions" && <SubmissionsTab />}
      {activeTab === "maintenance" && <MaintenanceTab />}
      {activeTab === "pending"     && <PendingEntitiesTab />}
      {activeTab === "csv"         && <CsvImportTab />}
    </div>
  );
}
