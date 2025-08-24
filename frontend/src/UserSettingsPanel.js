import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserSettingsPanel = ({ user, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Teams data for favorite club dropdown
  const [teams, setTeams] = useState([]);
  
  // Profile picture states
  const [profilePictureLoading, setProfilePictureLoading] = useState(false);
  const [profilePictureError, setProfilePictureError] = useState('');
  const [profileData, setProfileData] = useState({
    // Basic profile
    name: user?.name || '',
    email: user?.email || '',
    profile_picture_url: null,
    
    // Public profile information
    bio: '',
    favorite_club: '',
    favorite_club_name: '',
    instagram_username: '',
    twitter_username: '',
    website: '',
    
    // Address settings
    address: {
      street: '',
      city: '',
      postal_code: '',
      country: 'France'
    },
    
    // Seller settings
    seller_settings: {
      business_name: '',
      phone: '',
      return_policy: '',
      shipping_info: ''
    },
    
    // Buyer settings
    buyer_settings: {
      preferred_payment: 'card',
      delivery_preferences: 'standard'
    },
    
    // Privacy settings
    privacy_settings: {
      profile_visibility: 'public',
      show_collection: true,
      show_activity: true,
      email_notifications: true
    }
  });

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchUserSettings();
    fetchTeams();
  }, []);

  const fetchUserSettings = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      // Fetch both profile settings and public profile info
      const [profileResponse, publicInfoResponse] = await Promise.all([
        axios.get(`${API}/api/users/${user.id}/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API}/api/users/profile/public-info`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      // Merge profile settings
      if (profileResponse.data) {
        setProfileData(prev => ({
          ...prev,
          ...profileResponse.data,
          name: user.name,
          email: user.email,
          profile_picture_url: profileResponse.data.profile_picture_url || null
        }));
      }
      
      // Merge public info
      if (publicInfoResponse.data) {
        setProfileData(prev => ({
          ...prev,
          bio: publicInfoResponse.data.bio || '',
          favorite_club: publicInfoResponse.data.favorite_club || '',
          favorite_club_name: publicInfoResponse.data.favorite_club_name || '',
          instagram_username: publicInfoResponse.data.instagram_username || '',
          twitter_username: publicInfoResponse.data.twitter_username || '',
          website: publicInfoResponse.data.website || '',
          profile_picture_url: publicInfoResponse.data.profile_picture_url || prev.profile_picture_url
        }));
      }
      
    } catch (error) {
      console.log('Settings not found, using defaults');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API}/api/teams/dropdown`);
      setTeams(response.data || []);
    } catch (error) {
      console.log('Could not fetch teams for dropdown');
      setTeams([]);
    }
  };

  const saveSettings = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const token = localStorage.getItem('token');
      
      // Save both profile settings and public info
      await Promise.all([
        axios.put(`${API}/api/users/profile/settings`, profileData, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.put(`${API}/api/users/profile/public-info`, {
          bio: profileData.bio,
          favorite_club: profileData.favorite_club,
          instagram_username: profileData.instagram_username,
          twitter_username: profileData.twitter_username,
          website: profileData.website
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setSuccess('Paramètres sauvegardés avec succès !');
      if (onUpdate) onUpdate();
      
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (error) {
      setError('Erreur lors de la sauvegarde: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const updateProfileData = (section, field, value) => {
    setProfileData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  // Profile picture handlers
  const handleProfilePictureUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setProfilePictureLoading(true);
    setProfilePictureError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/profile/picture`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess('Photo de profil mise à jour avec succès !');
        setProfileData(prev => ({
          ...prev,
          profile_picture_url: data.profile_picture_url
        }));
        if (onUpdate) onUpdate();
      } else {
        const errorData = await response.json();
        setProfilePictureError(errorData.detail || 'Erreur lors du téléchargement');
      }
    } catch (error) {
      console.error('Profile picture upload error:', error);
      setProfilePictureError('Erreur lors du téléchargement de la photo');
    } finally {
      setProfilePictureLoading(false);
    }
  };

  const handleDeleteProfilePicture = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
      return;
    }

    setProfilePictureLoading(true);
    setProfilePictureError('');

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/users/profile/picture`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Photo de profil supprimée avec succès !');
        setProfileData(prev => ({
          ...prev,
          profile_picture_url: null
        }));
        if (onUpdate) onUpdate();
      } else {
        const errorData = await response.json();
        setProfilePictureError(errorData.detail || 'Erreur lors de la suppression');
      }
    } catch (error) {
      console.error('Profile picture delete error:', error);
      setProfilePictureError('Erreur lors de la suppression de la photo');
    } finally {
      setProfilePictureLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: '👤 Profil', icon: '👤' },
    { id: 'public', label: '📋 Informations Publiques', icon: '📋' },
    { id: 'address', label: '📍 Adresse', icon: '📍' },
    { id: 'seller', label: '🏪 Vendeur', icon: '🏪' },
    { id: 'buyer', label: '🛒 Acheteur', icon: '🛒' },
    { id: 'privacy', label: '🔒 Confidentialité', icon: '🔒' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Paramètres du profil</h2>
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

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <div className="flex h-[70vh]">
          {/* Tabs */}
          <div className="w-1/4 border-r pr-4">
            <div className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeTab === tab.id 
                      ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label.split(' ')[1]}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="w-3/4 pl-6 overflow-y-auto">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Informations du profil</h3>
                
                {/* Profile Picture Section */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">Photo de profil</label>
                    <div className="flex items-center space-x-4">
                      <div className="w-20 h-20 bg-gray-100 rounded-full overflow-hidden flex items-center justify-center">
                        {profileData.profile_picture_url ? (
                          <img 
                            src={`${API}/${profileData.profile_picture_url}`}
                            alt="Profile"
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                        ) : (
                          <div className="text-2xl text-gray-400">👤</div>
                        )}
                        <div className="text-2xl text-gray-400" style={{display: profileData.profile_picture_url ? 'none' : 'flex'}}>👤</div>
                      </div>
                      <div className="flex flex-col space-y-2">
                        <input
                          type="file"
                          id="profile-picture-upload-settings"
                          accept="image/jpeg,image/jpg,image/png,image/webp"
                          onChange={handleProfilePictureUpload}
                          className="hidden"
                        />
                        <button
                          type="button"
                          onClick={() => document.getElementById('profile-picture-upload-settings').click()}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors"
                        >
                          {profileData.profile_picture_url ? 'Changer la photo' : 'Ajouter une photo'}
                        </button>
                        {profileData.profile_picture_url && (
                          <button
                            type="button"
                            onClick={handleDeleteProfilePicture}
                            className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition-colors"
                          >
                            Supprimer
                          </button>
                        )}
                      </div>
                    </div>
                    {profilePictureLoading && (
                      <div className="mt-2 text-sm text-gray-500">Téléchargement en cours...</div>
                    )}
                    {profilePictureError && (
                      <div className="mt-2 text-sm text-red-600">{profilePictureError}</div>
                    )}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom complet
                    </label>
                    <input
                      type="text"
                      value={profileData.name}
                      onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={profileData.email}
                      disabled
                      className="w-full p-3 border border-gray-300 rounded-lg bg-gray-100 cursor-not-allowed"
                    />
                    <p className="text-xs text-gray-500 mt-1">L'email ne peut pas être modifié</p>
                  </div>
                </div>
              </div>
            )}

            {/* Address Tab */}
            {activeTab === 'address' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Adresse de livraison</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Adresse
                    </label>
                    <input
                      type="text"
                      value={profileData.address.street}
                      onChange={(e) => updateProfileData('address', 'street', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="123 rue de la République"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ville
                      </label>
                      <input
                        type="text"
                        value={profileData.address.city}
                        onChange={(e) => updateProfileData('address', 'city', e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="Paris"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Code postal
                      </label>
                      <input
                        type="text"
                        value={profileData.address.postal_code}
                        onChange={(e) => updateProfileData('address', 'postal_code', e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="75001"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Pays
                    </label>
                    <select
                      value={profileData.address.country}
                      onChange={(e) => updateProfileData('address', 'country', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="France">France</option>
                      <option value="Belgique">Belgique</option>
                      <option value="Suisse">Suisse</option>
                      <option value="Canada">Canada</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Seller Tab */}
            {activeTab === 'seller' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Paramètres vendeur</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nom commercial (optionnel)
                    </label>
                    <input
                      type="text"
                      value={profileData.seller_settings.business_name}
                      onChange={(e) => updateProfileData('seller_settings', 'business_name', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Mon Shop de Maillots"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Téléphone de contact
                    </label>
                    <input
                      type="tel"
                      value={profileData.seller_settings.phone}
                      onChange={(e) => updateProfileData('seller_settings', 'phone', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="+33 1 23 45 67 89"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Politique de retour
                    </label>
                    <textarea
                      value={profileData.seller_settings.return_policy}
                      onChange={(e) => updateProfileData('seller_settings', 'return_policy', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-24"
                      placeholder="Retours acceptés sous 14 jours..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Informations d'expédition
                    </label>
                    <textarea
                      value={profileData.seller_settings.shipping_info}
                      onChange={(e) => updateProfileData('seller_settings', 'shipping_info', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-24"
                      placeholder="Expédition sous 2-3 jours ouvrés..."
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Buyer Tab */}
            {activeTab === 'buyer' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Préférences d'achat</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Mode de paiement préféré
                    </label>
                    <select
                      value={profileData.buyer_settings.preferred_payment}
                      onChange={(e) => updateProfileData('buyer_settings', 'preferred_payment', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="card">Carte bancaire</option>
                      <option value="paypal">PayPal</option>
                      <option value="bank_transfer">Virement bancaire</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Préférences de livraison
                    </label>
                    <select
                      value={profileData.buyer_settings.delivery_preferences}
                      onChange={(e) => updateProfileData('buyer_settings', 'delivery_preferences', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="standard">Livraison standard</option>
                      <option value="express">Livraison express</option>
                      <option value="pickup">Point relais</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Paramètres de confidentialité</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Visibilité du profil
                    </label>
                    <select
                      value={profileData.privacy_settings.profile_visibility}
                      onChange={(e) => updateProfileData('privacy_settings', 'profile_visibility', e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="public">Public</option>
                      <option value="friends">Amis uniquement</option>
                      <option value="private">Privé</option>
                    </select>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Afficher ma collection</span>
                      <input
                        type="checkbox"
                        checked={profileData.privacy_settings.show_collection}
                        onChange={(e) => updateProfileData('privacy_settings', 'show_collection', e.target.checked)}
                        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Afficher mon activité</span>
                      <input
                        type="checkbox"
                        checked={profileData.privacy_settings.show_activity}
                        onChange={(e) => updateProfileData('privacy_settings', 'show_activity', e.target.checked)}
                        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">Notifications par email</span>
                      <input
                        type="checkbox"
                        checked={profileData.privacy_settings.email_notifications}
                        onChange={(e) => updateProfileData('privacy_settings', 'email_notifications', e.target.checked)}
                        className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={saveSettings}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Sauvegarde...' : 'Sauvegarder'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserSettingsPanel;