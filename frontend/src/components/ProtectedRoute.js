// frontend/src/components/ProtectedRoute.js
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { ShieldAlert } from 'lucide-react';

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
      return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 text-center px-4">
          <ShieldAlert className="w-12 h-12 text-destructive opacity-60" />
          <h2 className="text-xl font-bold text-foreground">Accès refusé</h2>
          <p className="text-sm text-muted-foreground max-w-xs">
            Vous n'avez pas les permissions nécessaires pour accéder à cette page.
          </p>
          <Navigate to="/" replace />
        </div>
      );
    }
  }

  return children;
}
