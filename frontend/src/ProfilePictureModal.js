import React, { useState } from 'react';
import axios from 'axios';

const ProfilePictureModal = ({ user, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess('');

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
        if (onUpdate) onUpdate();
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors du téléchargement');
      }
    } catch (error) {
      console.error('Profile picture upload error:', error);
      setError('Erreur lors du téléchargement de la photo');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePicture = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer votre photo de profil ?')) {
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

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
        if (onUpdate) onUpdate();
        setTimeout(() => {
          onClose();
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la suppression');
      }
    } catch (error) {
      console.error('Profile picture delete error:', error);
      setError('Erreur lors de la suppression de la photo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-800">Photo de profil</h3>
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

        <div className="text-center space-y-6">
          {/* Current Profile Picture */}
          <div className="flex justify-center">
            <div className="w-32 h-32 bg-gray-100 rounded-full overflow-hidden flex items-center justify-center">
              {user.profile_picture_url ? (
                <img 
                  src={`${API}/api/uploads/${user.profile_picture_url}`}
                  alt="Profile"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : (
                <div className="text-6xl text-gray-400">👤</div>
              )}
              <div className="text-6xl text-gray-400" style={{display: user.profile_picture_url ? 'none' : 'flex'}}>👤</div>
            </div>
          </div>

          {/* Upload Button */}
          <div className="space-y-3">
            <input
              type="file"
              id="profile-picture-upload-modal"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              onChange={handleFileUpload}
              className="hidden"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => document.getElementById('profile-picture-upload-modal').click()}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors"
            >
              {loading ? 'Téléchargement...' : (user.profile_picture_url ? 'Changer la photo' : 'Ajouter une photo')}
            </button>

            {user.profile_picture_url && (
              <button
                type="button"
                onClick={handleDeletePicture}
                disabled={loading}
                className="w-full bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                {loading ? 'Suppression...' : 'Supprimer la photo'}
              </button>
            )}
          </div>

          <p className="text-sm text-gray-500">
            Formats acceptés : JPG, PNG, WebP<br />
            Taille maximale : 5MB
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePictureModal;