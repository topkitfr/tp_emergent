// frontend/src/App.js
import React, { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import BetaGate from "@/pages/BetaGate";
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";
import ForgotPassword from "@/pages/ForgotPassword";
import ResetPassword from "@/pages/ResetPassword";
import Browse from "@/pages/Browse";
import KitDetail from "@/pages/KitDetail";
import VersionDetail from "@/pages/VersionDetail";
import MyCollection from "@/pages/MyCollection";
import AddJersey from "@/pages/AddJersey";
import Profile from "@/pages/Profile";
import Contributions from "@/pages/Contributions";
import Wishlist from "@/pages/Wishlist";
import Marketplace from "@/pages/Marketplace";
import MarketplaceDetail from "@/pages/MarketplaceDetail";
import Teams from "@/pages/Teams";
import TeamDetail from "@/pages/TeamDetail";
import Leagues from "@/pages/Leagues";
import LeagueDetail from "@/pages/LeagueDetail";
import Brands from "@/pages/Brands";
import BrandDetail from "@/pages/BrandDetail";
import Players from "@/pages/Players";
import PlayerDetail from "@/pages/PlayerDetail";
import Sponsors from "@/pages/Sponsors";
import SponsorDetail from "@/pages/SponsorDetail";
import AdminPanel from "@/pages/AdminPanel";
import MaintenancePage from "@/pages/MaintenancePage";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

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
    <>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

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
    </>
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
