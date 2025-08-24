import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PasswordResetPage = () => {
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [tokenValid, setTokenValid] = useState(null);

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    // Get token from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');
    
    if (urlToken) {
      setToken(urlToken);
      // Optionally verify token validity here
    } else {
      setError('Token de réinitialisation manquant. Veuillez utiliser le lien reçu par email.');
    }
  }, []);

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    
    if (!newPassword || !confirmPassword) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (newPassword.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    // Basic password validation
    const hasUppercase = /[A-Z]/.test(newPassword);
    const hasLowercase = /[a-z]/.test(newPassword);
    const hasNumber = /\d/.test(newPassword);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(newPassword);

    if (!hasUppercase || !hasLowercase || !hasNumber || !hasSpecial) {
      setError('Le mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre et un caractère spécial');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/api/auth/reset-password`, {
        token: token,
        new_password: newPassword
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      setSuccess(true);
      setError('');
      
    } catch (error) {
      let errorMessage = 'Erreur lors de la réinitialisation du mot de passe';
      
      if (error.response && error.response.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.request) {
        errorMessage = 'Erreur réseau. Vérifiez votre connexion.';
      }
      
      setError(errorMessage);
      setTokenValid(false);
    } finally {
      setLoading(false);
    }
  };

  if (!token && !error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md text-center">
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Mot de passe réinitialisé !
          </h1>
          <p className="text-gray-600 mb-6">
            Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.
          </p>
          <a
            href="/"
            className="inline-block bg-black hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-lg transition-all"
          >
            Retour à la connexion
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">TopKit</h1>
          <h2 className="text-xl text-gray-700">Nouveau mot de passe</h2>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handlePasswordReset} className="space-y-4">
          <div>
            <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Nouveau mot de passe
            </label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              placeholder="Saisissez votre nouveau mot de passe"
              disabled={loading}
              required
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Confirmer le mot de passe
            </label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              placeholder="Confirmez votre nouveau mot de passe"
              disabled={loading}
              required
            />
          </div>

          <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded-lg">
            <p className="font-medium mb-1">Exigences du mot de passe :</p>
            <ul className="space-y-1">
              <li>• Au moins 8 caractères</li>
              <li>• Au moins 1 majuscule (A-Z)</li>
              <li>• Au moins 1 minuscule (a-z)</li>
              <li>• Au moins 1 chiffre (0-9)</li>
              <li>• Au moins 1 caractère spécial (!@#$%^&*)</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-all"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Réinitialisation...
              </span>
            ) : (
              'Réinitialiser le mot de passe'
            )}
          </button>
        </form>

        <div className="text-center mt-6">
          <a
            href="/"
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Retour à l'accueil
          </a>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetPage;