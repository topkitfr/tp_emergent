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
  
  // Password validation helper
  const validatePassword = (password) => {
    return {
      minLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };
  };
  
  const passwordValidation = !isLogin ? validatePassword(formData.password || '') : {};

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://jersey-hub-2.preview.emergentagent.com';

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
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-md border border-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-black">
            {isLogin ? 'Connexion' : 'Inscription'}
          </h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-black text-2xl transition-colors"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
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
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={loading}
              />
            )}

            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              disabled={loading}
            />

            <input
              type="password"
              placeholder="Mot de passe"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              disabled={loading}
            />
        
            {/* Password Requirements */}
            {!isLogin && (
              <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="text-xs text-gray-700 mb-2 font-medium">
                  🔒 Exigences du mot de passe :
                </div>
                <div className="grid grid-cols-1 gap-1 text-xs">
                  <div className="flex items-center">
                    <span className={`mr-2 ${passwordValidation.minLength ? 'text-green-600' : 'text-gray-400'}`}>
                      {passwordValidation.minLength ? '✓' : '•'}
                    </span>
                    <span className={passwordValidation.minLength ? 'text-green-700' : 'text-gray-600'}>
                      Au moins <strong>8 caractères</strong>
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className={`mr-2 ${passwordValidation.hasUppercase ? 'text-green-600' : 'text-gray-400'}`}>
                      {passwordValidation.hasUppercase ? '✓' : '•'}
                    </span>
                    <span className={passwordValidation.hasUppercase ? 'text-green-700' : 'text-gray-600'}>
                      Au moins <strong>1 majuscule</strong> (A-Z)
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className={`mr-2 ${passwordValidation.hasLowercase ? 'text-green-600' : 'text-gray-400'}`}>
                      {passwordValidation.hasLowercase ? '✓' : '•'}
                    </span>
                    <span className={passwordValidation.hasLowercase ? 'text-green-700' : 'text-gray-600'}>
                      Au moins <strong>1 minuscule</strong> (a-z)
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className={`mr-2 ${passwordValidation.hasNumber ? 'text-green-600' : 'text-gray-400'}`}>
                      {passwordValidation.hasNumber ? '✓' : '•'}
                    </span>
                    <span className={passwordValidation.hasNumber ? 'text-green-700' : 'text-gray-600'}>
                      Au moins <strong>1 chiffre</strong> (0-9)
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className={`mr-2 ${passwordValidation.hasSpecial ? 'text-green-600' : 'text-gray-400'}`}>
                      {passwordValidation.hasSpecial ? '✓' : '•'}
                    </span>
                    <span className={passwordValidation.hasSpecial ? 'text-green-700' : 'text-gray-600'}>
                      Au moins <strong>1 caractère spécial</strong> (!@#$%^&*)
                    </span>
                  </div>
                </div>
              </div>
            )}
        
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-all"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {isLogin ? 'Connexion...' : 'Inscription...'}
                </span>
              ) : (
                isLogin ? 'Se connecter' : 'S\'inscrire'
              )}
            </button>
          </form>

          <p className="text-center text-gray-600 mt-4">
            {isLogin ? (
              <>
                Pas encore de compte ?
                <button
                  onClick={switchMode}
                  className="text-black hover:text-gray-700 ml-2 font-medium underline"
                  type="button"
                  disabled={loading}
                >
                  S'inscrire
                </button>
              </>
            ) : (
              <>
                Déjà un compte ?
                <button
                  onClick={switchMode}
                  className="text-black hover:text-gray-700 ml-2 font-medium underline"
                  type="button"
                  disabled={loading}
                >
                  Se connecter
                </button>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;