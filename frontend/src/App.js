import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider } from "@/contexts/AuthContext";
import AuthCallback from "@/pages/AuthCallback";
import Landing from "@/pages/Landing";
import Browse from "@/pages/Browse";
import KitDetail from "@/pages/KitDetail";
import VersionDetail from "@/pages/VersionDetail";
import MyCollection from "@/pages/MyCollection";
import AddJersey from "@/pages/AddJersey";
import Profile from "@/pages/Profile";
import Contributions from "@/pages/Contributions";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";

function AppRouter() {
  const location = useLocation();

  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/browse" element={<Browse />} />
        <Route path="/kit/:kitId" element={<KitDetail />} />
        <Route path="/version/:versionId" element={<VersionDetail />} />
        <Route path="/collection" element={<ProtectedRoute><MyCollection /></ProtectedRoute>} />
        <Route path="/add-jersey" element={<ProtectedRoute><AddJersey /></ProtectedRoute>} />
        <Route path="/contributions" element={<ProtectedRoute><Contributions /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <div className="noise-overlay">
      <BrowserRouter>
        <AuthProvider>
          <AppRouter />
          <Toaster position="bottom-right" theme="dark" />
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;
