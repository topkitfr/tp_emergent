import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ClickableUsername from '../components/ClickableUsername';

const LeaderboardPage = ({ user, API, setShowAuthModal }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUserRank, setCurrentUserRank] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API}/api/leaderboard?limit=100`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch leaderboard');
      }
      
      const data = await response.json();
      setLeaderboard(data);
      
      // Find current user's rank
      if (user) {
        const userEntry = data.find(entry => entry.username === user.name);
        if (userEntry) {
          setCurrentUserRank(userEntry.rank);
        }
      }
      
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      setError('Impossible de charger le classement');
    } finally {
      setLoading(false);
    }
  };

  const getRankDisplay = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  const getLevelColor = (level) => {
    switch (level) {
      case 'Remplaçant': return 'text-gray-600';
      case 'Titulaire': return 'text-blue-600';
      case 'Légende': return 'text-purple-600';
      case 'Ballon d\'Or': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du classement...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">❌</div>
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={fetchLeaderboard}
            className="mt-4 px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-black mb-2">Le Classement 🏆</h1>
          <p className="text-gray-600">
            Découvrez les contributeurs les plus actifs de la communauté TopKit
          </p>
          {currentUserRank && (
            <div className="mt-4 inline-block bg-blue-100 text-blue-800 px-4 py-2 rounded-full">
              Votre position: #{currentUserRank}
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 text-black">Niveaux de la communauté</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl mb-2">👕</div>
              <div className="font-medium text-gray-700">Remplaçant</div>
              <div className="text-sm text-gray-500">0-99 XP</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">⚽</div>
              <div className="font-medium text-blue-600">Titulaire</div>
              <div className="text-sm text-gray-500">100-499 XP</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">🏆</div>
              <div className="font-medium text-purple-600">Légende</div>
              <div className="text-sm text-gray-500">500-1999 XP</div>
            </div>
            <div className="text-center">
              <div className="text-2xl mb-2">🔥</div>
              <div className="font-medium text-yellow-600">Ballon d'Or</div>
              <div className="text-sm text-gray-500">2000+ XP</div>
            </div>
          </div>
        </div>

        {/* Leaderboard Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-black">Classement des contributeurs</h2>
          </div>
          
          {leaderboard.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              Aucun contributeur trouvé
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rang
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contributeur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      XP
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Niveau
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leaderboard.map((entry, index) => (
                    <tr 
                      key={entry.username}
                      className={`
                        ${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                        ${user && entry.username === user.name ? 'ring-2 ring-blue-500 bg-blue-50' : ''}
                        hover:bg-gray-100 transition-colors
                      `}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-2xl mr-2">
                            {getRankDisplay(entry.rank)}
                          </span>
                          <span className="text-sm font-medium text-gray-900">
                            #{entry.rank}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-semibold">
                              {entry.username.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium">
                              <ClickableUsername
                                userId={entry.user_id}
                                username={entry.username}
                                currentUser={user}
                                setShowAuthModal={setShowAuthModal}
                                className="text-gray-900 hover:text-blue-600 hover:underline transition-colors cursor-pointer"
                              />
                              {user && entry.username === user.name && (
                                <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                  Vous
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-bold text-green-600">
                          {entry.xp.toLocaleString()} XP
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-xl mr-2">{entry.level_emoji}</span>
                          <span className={`text-sm font-medium ${getLevelColor(entry.level)}`}>
                            {entry.level}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2 text-blue-900">
            Comment gagner des XP ?
          </h3>
          <div className="text-blue-800 space-y-2">
            <div className="flex items-center">
              <span className="mr-2">👕</span>
              <span>Ajouter un maillot: <strong>+20 XP</strong></span>
            </div>
            <div className="flex items-center">
              <span className="mr-2">⚽</span>
              <span>Ajouter une équipe/marque/joueur/compétition: <strong>+10 XP</strong></span>
            </div>
            <div className="text-sm mt-4 text-blue-700">
              * Les XP sont attribués uniquement après validation par les modérateurs
            </div>
            <div className="text-sm text-blue-700">
              * Limite de 100 XP par jour pour éviter les abus
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeaderboardPage;