import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ProtectedRoute = ({ user, setShowAuthModal, children }) => {
  const navigate = useNavigate();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check authentication immediately, but allow a brief moment for state to settle
    const timer = setTimeout(() => {
      setIsChecking(false);
      
      if (!user) {
        console.log('🔒 ProtectedRoute: No user found, redirecting to home');
        // Redirect to home and show login modal
        navigate('/');
        if (setShowAuthModal) {
          setShowAuthModal(true);
        }
      } else {
        console.log('✅ ProtectedRoute: User authenticated:', user.email);
      }
    }, 100); // Reduced delay to minimize timing issues

    return () => clearTimeout(timer);
  }, [user, navigate, setShowAuthModal]);

  // Show loading state while checking authentication
  if (isChecking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // If user is not logged in, show login required message
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="mb-6">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-6">You need to log in to access this page.</p>
          <button
            onClick={() => {navigate('/'); setShowAuthModal && setShowAuthModal(true);}}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Log In
          </button>
        </div>
      </div>
    );
  }

  return children;
};

export default ProtectedRoute;