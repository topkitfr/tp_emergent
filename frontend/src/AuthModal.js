import React, { useState } from 'react';
import axios from 'axios';

const AuthModal = ({ isOpen, onClose, onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ 
    email: '', 
    password: '', 
    name: '' 
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://topkit-email.preview.emergentagent.com';

  const handleAuthFormSubmit = async (e) => {
    e.preventDefault();
    
    console.log('🚀 AuthModal - handleAuthFormSubmit called successfully!');
    console.log('📧 Form data:', { 
      email: formData.email, 
      password: formData.password ? '***HIDDEN***' : 'EMPTY', 
      name: formData.name 
    });
    console.log('🔄 isLogin mode:', isLogin);
    console.log('🌐 API URL:', API);
    
    // Validation
    if (!formData.email || !formData.password) {
      console.error('❌ Missing required fields');
      setError('Veuillez remplir tous les champs requis');
      return;
    }

    if (!isLogin && !formData.name) {
      console.error('❌ Missing name for registration');
      setError('Le nom est requis pour l\'inscription');
      return;
    }
    
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register';
      const fullUrl = `${API}${endpoint}`;
      
      console.log('🔄 Making request to:', fullUrl);
      console.log('📤 Request payload:', {
        email: formData.email,
        password: '[HIDDEN]',
        ...(formData.name && { name: formData.name })
      });
      
      const response = await axios.post(fullUrl, {
        email: formData.email,
        password: formData.password,
        ...(formData.name && { name: formData.name })
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log('✅ Response received:', response.status);
      console.log('📥 Response data:', response.data);
      
      if (isLogin) {
        // Login successful
        if (response.data?.token && response.data?.user) {
          console.log('🔑 Login successful - storing token and user data');
          
          // Store authentication data
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          
          console.log('💾 Token stored:', response.data.token.substring(0, 20) + '...');
          console.log('👤 User stored:', response.data.user);
          
          // Close modal
          if (onClose) onClose();
          
          // Call success callback
          if (onLoginSuccess) {
            onLoginSuccess(response.data.token, response.data.user);
          }
          
          // Show success message
          console.log('✅ Login completed successfully');
          
        } else {
          console.error('❌ Invalid login response structure');
          setError('Réponse d\'authentification invalide');
        }
      } else {
        // Registration successful
        console.log('✅ Registration successful');
        setError('');
        
        // Switch to login mode
        setIsLogin(true);
        setFormData({ ...formData, password: '', name: '' });
        
        // Show success message
        alert('Inscription réussie ! Vous pouvez maintenant vous connecter.');
      }
      
    } catch (error) {
      console.error('❌ Authentication error:', error);
      
      let errorMessage = 'Erreur de connexion';
      
      if (error.response) {
        console.error('📥 Error response:', error.response.status, error.response.data);
        
        if (error.response.status === 401) {
          errorMessage = 'Email ou mot de passe incorrect';
        } else if (error.response.status === 400) {
          errorMessage = error.response.data?.detail || 'Données invalides';
        } else if (error.response.data?.detail) {
          errorMessage = error.response.data.detail;
        }
      } else if (error.request) {
        console.error('📡 Network error:', error.request);
        errorMessage = 'Erreur réseau. Vérifiez votre connexion.';
      } else {
        console.error('⚠️ Request setup error:', error.message);
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ email: '', password: '', name: '' });
    setError('');
    setLoading(false);
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {isLogin ? 'Connexion' : 'Inscription'}
          </h2>
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

        <form onSubmit={handleAuthFormSubmit} noValidate className="space-y-4">
          {!isLogin && (
            <input
              type="text"
              placeholder="Nom complet"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder-gray-500"
              disabled={loading}
              style={{ backgroundColor: '#ffffff', color: '#111827' }}
            />
          )}
          
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder-gray-500"
            disabled={loading}
            required
            style={{ backgroundColor: '#ffffff', color: '#111827' }}
          />
          
          <input
            type="password"
            placeholder="Mot de passe"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900 placeholder-gray-500"
            disabled={loading}
            required
            style={{ backgroundColor: '#ffffff', color: '#111827' }}
          />
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : 'S\'inscrire')}
          </button>
        </form>

        <p className="text-center text-gray-600 mt-4">
          {isLogin ? 'Pas de compte ?' : 'Déjà un compte ?'}
          <button
            onClick={switchMode}
            className="text-blue-600 hover:text-blue-700 ml-2 font-medium"
            type="button"
            disabled={loading}
          >
            {isLogin ? 'Créer un compte' : 'Se connecter'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default AuthModal;