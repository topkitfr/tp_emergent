// frontend/src/App.js
import React, { useEffect, useState, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

// Pages chargées immédiatement (chemin critique avant auth)
import BetaGate from "@/pages/BetaGate";
import MaintenancePage from "@/pages/MaintenancePage";

// Pages lazy-loadées (splitées en chunks séparés)
const Landing          = lazy(() => import("@/pages/Landing"));
const Login            = lazy(() => import("@/pages/Login"));
const ForgotPassword   = lazy(() => import("@/pages/ForgotPassword"));
const ResetPassword    = lazy(() => import("@/pages/ResetPassword"));
const VerifyEmail      = lazy(() => import("@/pages/VerifyEmail"));
const Browse           = lazy(() => import("@/pages/Browse"));
const KitDetail        = lazy(() => import("@/pages/KitDetail"));
const VersionDetail    = lazy(() => import("@/pages/VersionDetail"));
const MyCollection           = lazy(() => import("@/pages/MyCollection"));
const CollectionItemDetail   = lazy(() => import("@/pages/CollectionItemDetail"));
const AddJersey        = lazy(() => import("@/pages/AddJersey"));
const Profile          = lazy(() => import("@/pages/Profile"));
const Contributions    = lazy(() => import("@/pages/Contributions"));
const Wishlist         = lazy(() => import("@/pages/Wishlist"));
const Marketplace      = lazy(() => import("@/pages/Marketplace"));
const MarketplaceDetail= lazy(() => import("@/pages/MarketplaceDetail"));
const Teams            = lazy(() => import("@/pages/Teams"));
const TeamDetail       = lazy(() => import("@/pages/TeamDetail"));
const Leagues          = lazy(() => import("@/pages/Leagues"));
const LeagueDetail     = lazy(() => import("@/pages/LeagueDetail"));
const Brands           = lazy(() => import("@/pages/Brands"));
const BrandDetail      = lazy(() => import("@/pages/BrandDetail"));
const Players          = lazy(() => import("@/pages/Players"));
const PlayerDetail     = lazy(() => import("@/pages/PlayerDetail"));
const Sponsors         = lazy(() => import("@/pages/Sponsors"));
const SponsorDetail    = lazy(() => import("@/pages/SponsorDetail"));
const AdminPanel       = lazy(() => import("@/pages/AdminPanel"));

const API = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

// Activer ou désactiver la beta gate ici
const BETA_ENABLED = true;

const RedirectWithId = ({ to }) => {
  const { id } = useParams();
  return <Navigate to={`${to}/${id}`} replace />;
};

// Composant interne : rendu après BrowserRouter + providers
function AppContent() {
const [betaUnlocked, setBetaUnlocked] = useState(
  () => localStorage.getItem('topkit_beta_validated') === 'true'
);

  if (BETA_ENABLED && !betaUnlocked) {
    return <BetaGate onAccess={() => setBetaUnlocked(true)} />;
  }

  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" /></div>}>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />

        <Route element={<Layout />}>
          {/* ── Navigation principale ── */}
          <Route path="/browse" element={<Browse />} />
          <Route path="/kit/:kitId" element={<KitDetail />} />
          <Route path="/version/:versionId" element={<VersionDetail />} />

          {/* ── Database — Teams ── */}
          <Route path="/teams" element={<Teams />} />
          <Route path="/teams/:id" element={<TeamDetail />} />

          {/* ── Database — Leagues ── */}
          <Route path="/leagues" element={<Leagues />} />
          <Route path="/leagues/:id" element={<LeagueDetail />} />
          <Route path="/database/leagues" element={<Navigate to="/leagues" replace />} />
          <Route path="/database/leagues/:id" element={<RedirectWithId to="/leagues" />} />

          {/* ── Database — Brands ── */}
          <Route path="/brands" element={<Brands />} />
          <Route path="/brands/:id" element={<BrandDetail />} />
          <Route path="/database/brands" element={<Navigate to="/brands" replace />} />
          <Route path="/database/brands/:id" element={<RedirectWithId to="/brands" />} />

          {/* ── Database — Players ── */}
          <Route path="/players" element={<Players />} />
          <Route path="/players/:id" element={<PlayerDetail />} />

          {/* ── Database — Sponsors ── */}
          <Route path="/sponsors" element={<Sponsors />} />
          <Route path="/sponsors/:id" element={<SponsorDetail />} />
          <Route path="/database/sponsors" element={<Navigate to="/sponsors" replace />} />
          <Route path="/database/sponsors/:id" element={<RedirectWithId to="/sponsors" />} />

          {/* ── Marketplace ── */}
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/marketplace/:listingId" element={<MarketplaceDetail />} />

          {/* ── Pages protégées ── */}
          <Route path="/collection" element={<ProtectedRoute><MyCollection /></ProtectedRoute>} />
          <Route path="/collection/:collection_id" element={<ProtectedRoute><CollectionItemDetail /></ProtectedRoute>} />
          <Route path="/wishlist" element={<ProtectedRoute><Wishlist /></ProtectedRoute>} />
          <Route path="/add-jersey" element={<ProtectedRoute><AddJersey /></ProtectedRoute>} />
          <Route path="/contributions" element={<ProtectedRoute><Contributions /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/profile/:username" element={<Profile />} />
          <Route path="/admin" element={<ProtectedRoute requireRole="moderator"><AdminPanel /></ProtectedRoute>} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster position="bottom-right" theme="dark" />
    </Suspense>
  );
}

function App() {
  const [maintenance, setMaintenance] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    fetch(`${API}/admin/maintenance`, { credentials: "include" })
      .then((r) => r.ok ? r.json() : null)
      .then((d) => { if (d?.maintenance_mode) setMaintenance(true); })
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);

  if (checking) return null;
  if (maintenance) return <MaintenancePage />;

  // ✅ BetaGate est maintenant DANS BrowserRouter + providers
  return (
    <div className="noise-overlay">
      <BrowserRouter>
        <AuthProvider>
          <NotificationProvider>
            <AppContent />
          </NotificationProvider>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
