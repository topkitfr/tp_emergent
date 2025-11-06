import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ProtectedRoute = ({ user, authLoading, setShowAuthModal, children }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Only redirect if auth check is complete and no user found
    if (!authLoading && !user) {
      console.log('🔒 ProtectedRoute: No user found after auth check, redirecting to home');
      // Redirect to home and show login modal
      navigate('/');
      if (setShowAuthModal) {
        setShowAuthModal(true);
      }
    } else if (!authLoading && user) {
      console.log('✅ ProtectedRoute: User authenticated:', user.email);
    }
  }, [user, authLoading, navigate, setShowAuthModal]);

  // Show loading spinner while checking authentication
  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Checking authentication...</div>
      </div>
    );
  }

  // If auth check is complete but no user, don't render children (redirect is happening)
  if (!user) {
    return null;
  }

  return children;
};

export default ProtectedRoute;