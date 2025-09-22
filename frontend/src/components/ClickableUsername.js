import React from 'react';
import { useNavigate } from 'react-router-dom';

const ClickableUsername = ({ 
  userId, 
  username, 
  currentUser, 
  setShowAuthModal, 
  className = "text-blue-600 hover:text-blue-800 hover:underline transition-colors cursor-pointer",
  children 
}) => {
  const navigate = useNavigate();

  const handleUserClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (currentUser) {
      // If it's the current user, redirect to their own profile page
      if (username === currentUser.name || userId === currentUser.id) {
        navigate('/profile');
      } else {
        // Navigate to public profile
        navigate(`/profile/${userId}`);
      }
    } else {
      // Store the intended action and trigger login modal
      localStorage.setItem('pendingAction', JSON.stringify({
        action: 'viewProfile',
        userId: userId
      }));
      if (setShowAuthModal) {
        setShowAuthModal(true);
      }
    }
  };

  return (
    <button
      onClick={handleUserClick}
      className={className}
      type="button"
    >
      {children || username}
    </button>
  );
};

export default ClickableUsername;