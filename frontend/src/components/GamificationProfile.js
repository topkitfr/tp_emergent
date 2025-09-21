import React, { useState, useEffect } from 'react';

const GamificationProfile = ({ user, API, isCompact = false }) => {
  const [gamificationData, setGamificationData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user && user.id) {
      fetchGamificationData();
    }
  }, [user]);

  const fetchGamificationData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/api/users/${user.id}/gamification`);
      
      if (response.ok) {
        const data = await response.json();
        setGamificationData(data);
      } else {
        console.error('Failed to fetch gamification data');
      }
    } catch (error) {
      console.error('Error fetching gamification data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user || loading) {
    return (
      <div className={`${isCompact ? 'p-2' : 'p-4'} animate-pulse`}>
        <div className="bg-gray-200 rounded h-4 w-24 mb-2"></div>
        <div className="bg-gray-200 rounded h-2 w-full"></div>
      </div>
    );
  }

  if (!gamificationData) {
    return null;
  }

  const { xp, level, level_emoji, xp_to_next_level, next_level, progress_percentage } = gamificationData;

  if (isCompact) {
    // Compact version for header/navbar
    return (
      <div className="flex items-center space-x-2">
        <div className="flex items-center space-x-1">
          <span className="text-lg">{level_emoji}</span>
          <span className="text-sm font-medium text-gray-700">{xp.toLocaleString()} XP</span>
        </div>
        <div className="text-xs text-gray-500">{level}</div>
      </div>
    );
  }

  // Full version for profile page
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-black">Progression</h3>
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{level_emoji}</span>
          <span className="text-lg font-bold text-black">{level}</span>
        </div>
      </div>
      
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">XP Total</span>
          <span className="text-lg font-bold text-green-600">{xp.toLocaleString()} XP</span>
        </div>
        
        {next_level && (
          <>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Prochain niveau: {next_level}</span>
              <span className="text-sm text-gray-600">{xp_to_next_level} XP restants</span>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress_percentage}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-500 text-center">
              {progress_percentage}% vers {next_level}
            </div>
          </>
        )}
        
        {!next_level && level === 'Ballon d\'Or' && (
          <div className="text-center py-2">
            <div className="text-yellow-600 font-medium">🎉 Niveau maximum atteint ! 🎉</div>
            <div className="text-sm text-gray-600 mt-1">
              Vous êtes au sommet de la hiérarchie TopKit
            </div>
          </div>
        )}
      </div>
      
      {/* Level Benefits */}
      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Niveaux</h4>
        <div className="space-y-2">
          <div className={`flex items-center justify-between p-2 rounded ${level === 'Remplaçant' ? 'bg-blue-50' : ''}`}>
            <div className="flex items-center space-x-2">
              <span>👕</span>
              <span className="text-sm">Remplaçant</span>
            </div>
            <span className="text-xs text-gray-500">0-99 XP</span>
          </div>
          <div className={`flex items-center justify-between p-2 rounded ${level === 'Titulaire' ? 'bg-blue-50' : ''}`}>
            <div className="flex items-center space-x-2">
              <span>⚽</span>
              <span className="text-sm">Titulaire</span>
            </div>
            <span className="text-xs text-gray-500">100-499 XP</span>
          </div>
          <div className={`flex items-center justify-between p-2 rounded ${level === 'Légende' ? 'bg-blue-50' : ''}`}>
            <div className="flex items-center space-x-2">
              <span>🏆</span>
              <span className="text-sm">Légende</span>
            </div>
            <span className="text-xs text-gray-500">500-1999 XP</span>
          </div>
          <div className={`flex items-center justify-between p-2 rounded ${level === 'Ballon d\'Or' ? 'bg-blue-50' : ''}`}>
            <div className="flex items-center space-x-2">
              <span>🔥</span>
              <span className="text-sm">Ballon d'Or</span>
            </div>
            <span className="text-xs text-gray-500">2000+ XP</span>
          </div>
        </div>
      </div>
      
      {/* XP Sources */}
      <div className="border-t border-gray-200 pt-4 mt-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Comment gagner des XP</h4>
        <div className="space-y-1 text-sm text-gray-600">
          <div className="flex justify-between">
            <span>Ajouter un maillot</span>
            <span className="font-medium text-green-600">+20 XP</span>
          </div>
          <div className="flex justify-between">
            <span>Ajouter équipe/marque/joueur/compétition</span>
            <span className="font-medium text-green-600">+10 XP</span>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          * XP attribués après validation par les modérateurs
        </div>
        <div className="text-xs text-gray-500">
          * Limite de 100 XP par jour
        </div>
      </div>
    </div>
  );
};

export default GamificationProfile;