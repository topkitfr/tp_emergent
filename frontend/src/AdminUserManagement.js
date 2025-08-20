import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminUserManagement = ({ isOpen, onClose }) => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetails, setUserDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmAction, setConfirmAction] = useState(null);
  const [banReason, setBanReason] = useState('');

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://jersey-vault-3.preview.emergentagent.com';

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUsers(response.data.users || []);
      setError('');
    } catch (error) {
      setError('Erreur lors du chargement des utilisateurs: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchUserDetails = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/admin/users/${userId}/security`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setUserDetails(response.data);
      setSelectedUser(userId);
    } catch (error) {
      setError('Erreur lors du chargement des détails utilisateur: ' + (error.response?.data?.detail || error.message));
    }
  };

  const banUser = async (userId, reason) => {
    try {
      setActionLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/users/${userId}/ban`, {
        reason: reason || 'Violation des conditions d\'utilisation'
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchUsers();
      if (selectedUser === userId) {
        await fetchUserDetails(userId);
      }
      
      setConfirmAction(null);
      setBanReason('');
      setError('');
    } catch (error) {
      setError('Erreur lors du bannissement: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(false);
    }
  };

  const unbanUser = async (userId) => {
    try {
      setActionLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/admin/users/${userId}/unban`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchUsers();
      if (selectedUser === userId) {
        await fetchUserDetails(userId);
      }
      
      setConfirmAction(null);
      setError('');
    } catch (error) {
      setError('Erreur lors du débannissement: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(false);
    }
  };

  const deleteUser = async (userId) => {
    try {
      setActionLoading(true);
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchUsers();
      setSelectedUser(null);
      setUserDetails(null);
      setConfirmAction(null);
      setError('');
    } catch (error) {
      setError('Erreur lors de la suppression: ' + (error.response?.data?.detail || error.message));
    } finally {
      setActionLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full mx-4 p-6 max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Gestion des utilisateurs</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl font-bold"
            type="button"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="flex h-[70vh]">
          {/* Users List */}
          <div className="w-1/3 border-r pr-4">
            <h3 className="text-lg font-semibold mb-4">Utilisateurs ({users.length})</h3>
            
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-2 overflow-y-auto max-h-full">
                {users.map((user) => (
                  <div
                    key={user.id}
                    onClick={() => fetchUserDetails(user.id)}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedUser === user.id ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{user.name}</p>
                        <p className="text-sm text-gray-600">{user.email}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`inline-block w-2 h-2 rounded-full ${
                            user.is_banned ? 'bg-red-500' : 'bg-green-500'
                          }`}></span>
                          <span className="text-xs text-gray-500">
                            {user.is_banned ? 'Banni' : 'Actif'}
                          </span>
                          {user.role === 'admin' && (
                            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                              Admin
                            </span>
                          )}
                          {user.role === 'moderator' && (
                            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                              Mod
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* User Details */}
          <div className="w-2/3 pl-4">
            {selectedUser && userDetails ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Détails de l'utilisateur</h3>
                  
                  <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-600">Nom</label>
                        <p className="text-gray-900">{userDetails.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Email</label>
                        <p className="text-gray-900">{userDetails.email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Rôle</label>
                        <p className="text-gray-900 capitalize">{userDetails.role}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Statut</label>
                        <p className={`font-medium ${userDetails.is_banned ? 'text-red-600' : 'text-green-600'}`}>
                          {userDetails.is_banned ? 'Banni' : 'Actif'}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">2FA</label>
                        <p className={`font-medium ${userDetails.has_2fa ? 'text-green-600' : 'text-gray-500'}`}>
                          {userDetails.has_2fa ? 'Activé' : 'Désactivé'}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-600">Dernière connexion</label>
                        <p className="text-gray-900">
                          {userDetails.last_login ? new Date(userDetails.last_login).toLocaleDateString('fr-FR') : 'Jamais'}
                        </p>
                      </div>
                    </div>

                    {userDetails.ban_reason && (
                      <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                        <label className="text-sm font-medium text-red-600">Raison du bannissement</label>
                        <p className="text-red-800">{userDetails.ban_reason}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Statistics */}
                <div>
                  <h4 className="text-md font-semibold mb-3">Statistiques</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-blue-50 p-3 rounded-lg text-center">
                      <p className="text-2xl font-bold text-blue-600">{userDetails.jerseys_count || 0}</p>
                      <p className="text-sm text-blue-600">Maillots soumis</p>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg text-center">
                      <p className="text-2xl font-bold text-green-600">{userDetails.listings_count || 0}</p>
                      <p className="text-sm text-green-600">Annonces actives</p>
                    </div>
                    <div className="bg-purple-50 p-3 rounded-lg text-center">
                      <p className="text-2xl font-bold text-purple-600">{userDetails.collection_count || 0}</p>
                      <p className="text-sm text-purple-600">Collection</p>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                {userDetails.role !== 'admin' && (
                  <div>
                    <h4 className="text-md font-semibold mb-3">Actions</h4>
                    <div className="flex space-x-3">
                      {!userDetails.is_banned ? (
                        <button
                          onClick={() => setConfirmAction({ type: 'ban', userId: selectedUser })}
                          className="bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700 transition-colors"
                        >
                          🚫 Bannir l'utilisateur
                        </button>
                      ) : (
                        <button
                          onClick={() => setConfirmAction({ type: 'unban', userId: selectedUser })}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                        >
                          ✅ Débannir l'utilisateur
                        </button>
                      )}
                      
                      <button
                        onClick={() => setConfirmAction({ type: 'delete', userId: selectedUser })}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                      >
                        🗑️ Supprimer le compte
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>Sélectionnez un utilisateur pour voir les détails</p>
              </div>
            )}
          </div>
        </div>

        {/* Confirmation Modal */}
        {confirmAction && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
              <h3 className="text-lg font-semibold mb-4">
                {confirmAction.type === 'ban' && 'Confirmer le bannissement'}
                {confirmAction.type === 'unban' && 'Confirmer le débannissement'}
                {confirmAction.type === 'delete' && 'Confirmer la suppression'}
              </h3>
              
              <p className="text-gray-600 mb-4">
                {confirmAction.type === 'ban' && 'Êtes-vous sûr de vouloir bannir cet utilisateur ?'}
                {confirmAction.type === 'unban' && 'Êtes-vous sûr de vouloir débannir cet utilisateur ?'}
                {confirmAction.type === 'delete' && 'Êtes-vous sûr de vouloir supprimer définitivement ce compte ? Cette action est irréversible.'}
              </p>

              {confirmAction.type === 'ban' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Raison du bannissement (optionnel)
                  </label>
                  <textarea
                    value={banReason}
                    onChange={(e) => setBanReason(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    placeholder="Violation des conditions d'utilisation, comportement inapproprié, etc."
                  />
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setConfirmAction(null);
                    setBanReason('');
                  }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={() => {
                    if (confirmAction.type === 'ban') {
                      banUser(confirmAction.userId, banReason);
                    } else if (confirmAction.type === 'unban') {
                      unbanUser(confirmAction.userId);
                    } else if (confirmAction.type === 'delete') {
                      deleteUser(confirmAction.userId);
                    }
                  }}
                  disabled={actionLoading}
                  className={`flex-1 text-white py-2 rounded-lg transition-colors ${
                    confirmAction.type === 'delete' 
                      ? 'bg-red-600 hover:bg-red-700' 
                      : confirmAction.type === 'ban'
                      ? 'bg-yellow-600 hover:bg-yellow-700'
                      : 'bg-green-600 hover:bg-green-700'
                  } disabled:opacity-50`}
                >
                  {actionLoading ? 'Traitement...' : 'Confirmer'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUserManagement;