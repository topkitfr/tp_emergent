// frontend/src/components/ProtectedRoute.js
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

/**
 * ProtectedRoute — Protège une route contre les accès non authentifiés.
 *
 * Props:
 * - requireRole: "moderator" | "admin" — restreint aux rôles spécifiés
 *   (les admins ont toujours accès aux routes moderator)
 */
export default function ProtectedRoute({ children, requireRole }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Vérification de rôle (hiérarchie: admin > moderator > user)
  if (requireRole) {
    const ROLE_HIERARCHY = { admin: 3, moderator: 2, user: 1 };
    const userLevel = ROLE_HIERARCHY[user.role] || 1;
    const requiredLevel = ROLE_HIERARCHY[requireRole] || 1;

    if (userLevel < requiredLevel) {
      // Redirection simple — pas de JSX wrapper autour de Navigate
      return <Navigate to="/" replace />;
    }
  }

  return children;
}
