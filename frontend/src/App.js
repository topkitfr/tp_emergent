// frontend/src/App.js
import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import Landing from "@/pages/Landing";
import Login from "@/pages/login";
import Browse from "@/pages/Browse";
import KitDetail from "@/pages/KitDetail";
import VersionDetail from "@/pages/VersionDetail";
import MyCollection from "@/pages/MyCollection";
import AddJersey from "@/pages/AddJersey";
import Profile from "@/pages/Profile";
import Contributions from "@/pages/Contributions";
import Wishlist from "@/pages/Wishlist";
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
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

function App() {
  return (
    <div className="noise-overlay">
      <BrowserRouter>
        <AuthProvider>
          <NotificationProvider>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />

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
                {/* Redirects pour compatibilité avec anciens liens /database/leagues */}
                <Route path="/database/leagues" element={<Navigate to="/leagues" replace />} />
                <Route path="/database/leagues/:id" element={<Navigate to="/leagues/:id" replace />} />

                {/* ── Database — Brands ── */}
                <Route path="/brands" element={<Brands />} />
                <Route path="/brands/:id" element={<BrandDetail />} />
                {/* Redirects pour compatibilité */}
                <Route path="/database/brands" element={<Navigate to="/brands" replace />} />
                <Route path="/database/brands/:id" element={<Navigate to="/brands/:id" replace />} />

                {/* ── Database — Players ── */}
                <Route path="/players" element={<Players />} />
                <Route path="/players/:id" element={<PlayerDetail />} />

                {/* ── Database — Sponsors ── */}
                <Route path="/database/sponsors" element={<Sponsors />} />
                <Route path="/database/sponsors/:name" element={<SponsorDetail />} />

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
          </NotificationProvider>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
