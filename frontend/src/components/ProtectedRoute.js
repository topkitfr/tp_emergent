import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ user, authLoading, setShowAuthModal, children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isNavigating, setIsNavigating] = useState(false);

  // Handle route changes - add small delay to prevent race conditions
  useEffect(() => {
    console.log('📍 ProtectedRoute: Route changed to', location.pathname);
    setIsNavigating(true);
    
    // Small delay to ensure auth state is synchronized after navigation
    const timer = setTimeout(() => {
      setIsNavigating(false);
      console.log('✅ ProtectedRoute: Navigation complete, auth state synchronized');
    }, 100);
    
    return () => clearTimeout(timer);
  }, [location.pathname]);

  useEffect(() => {
    // Only redirect if auth check is complete, navigation is complete, and no user found
    if (!authLoading && !isNavigating && !user) {
      console.log('🔒 ProtectedRoute: No user found after auth check, redirecting to home');
      // Redirect to home and show login modal
      navigate('/');
      if (setShowAuthModal) {
        setShowAuthModal(true);
      }
    } else if (!authLoading && !isNavigating && user) {
      console.log('✅ ProtectedRoute: User authenticated:', user.email || user.username);
    } else if (authLoading || isNavigating) {
      console.log('⏳ ProtectedRoute: Waiting...', { authLoading, isNavigating });
    }
  }, [user, authLoading, isNavigating, navigate, setShowAuthModal]);

  // Show loading spinner while checking authentication or during navigation
  if (authLoading || isNavigating) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-500">
            {authLoading ? 'Checking authentication...' : 'Loading...'}
          </div>
        </div>
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