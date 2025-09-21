import React, { useState, useEffect } from 'react';

const XPNotification = ({ 
  isVisible, 
  onClose, 
  xpAwarded, 
  newLevel, 
  levelChanged, 
  levelEmoji 
}) => {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (isVisible) {
      setShow(true);
      // Auto-hide after 5 seconds
      const timer = setTimeout(() => {
        handleClose();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [isVisible]);

  const handleClose = () => {
    setShow(false);
    setTimeout(() => {
      onClose();
    }, 300); // Wait for animation to complete
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
      {/* Backdrop */}
      <div className={`absolute inset-0 bg-black transition-opacity duration-300 ${
        show ? 'bg-opacity-30' : 'bg-opacity-0'
      }`} />
      
      {/* Notification */}
      <div className={`
        relative bg-white rounded-lg shadow-2xl max-w-sm mx-4 p-6 pointer-events-auto
        transform transition-all duration-300 ${
        show 
          ? 'scale-100 opacity-100 translate-y-0' 
          : 'scale-95 opacity-0 translate-y-4'
      }`}>
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="text-center">
          {/* Success Icon & Animation */}
          <div className="mb-4 relative">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            {/* Floating XP Animation */}
            <div className="absolute -top-2 -right-2 animate-bounce">
              <div className="bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full text-xs font-bold">
                +{xpAwarded} XP
              </div>
            </div>
          </div>

          {/* Main Message */}
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              Contribution approuvée ! ✅
            </h3>
            <p className="text-gray-600">
              Vous avez gagné <span className="font-bold text-green-600">{xpAwarded} XP</span>
            </p>
          </div>

          {/* Level Info */}
          {levelChanged ? (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-center space-x-2 mb-2">
                <span className="text-3xl animate-pulse">{levelEmoji}</span>
                <div className="text-center">
                  <div className="text-sm font-medium text-purple-600">Nouveau niveau !</div>
                  <div className="text-lg font-bold text-purple-800">{newLevel}</div>
                </div>
              </div>
              <div className="text-sm text-purple-600">
                🎉 Félicitations ! Vous avez atteint un nouveau niveau !
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <div className="flex items-center justify-center space-x-2">
                <span className="text-xl">{levelEmoji}</span>
                <div className="text-sm">
                  <span className="font-medium text-gray-700">Niveau actuel: </span>
                  <span className="font-bold text-gray-900">{newLevel}</span>
                </div>
              </div>
            </div>
          )}

          {/* Action Button */}
          <button
            onClick={handleClose}
            className="w-full px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors font-medium"
          >
            Super !
          </button>
        </div>
      </div>
    </div>
  );
};

// Hook for managing XP notifications
export const useXPNotification = () => {
  const [notification, setNotification] = useState({
    isVisible: false,
    xpAwarded: 0,
    newLevel: '',
    levelChanged: false,
    levelEmoji: ''
  });

  const showNotification = ({ xpAwarded, newLevel, levelChanged, levelEmoji }) => {
    setNotification({
      isVisible: true,
      xpAwarded,
      newLevel,
      levelChanged,
      levelEmoji
    });
  };

  const hideNotification = () => {
    setNotification(prev => ({
      ...prev,
      isVisible: false
    }));
  };

  const NotificationComponent = () => (
    <XPNotification
      {...notification}
      onClose={hideNotification}
    />
  );

  return {
    showNotification,
    NotificationComponent
  };
};

export default XPNotification;