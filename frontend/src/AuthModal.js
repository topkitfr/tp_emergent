import React, { useState } from 'react';
import axios from 'axios';

const AuthModal = ({ isOpen, onClose, onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [formData, setFormData] = useState({ 
    email: '', 
    password: '', 
    name: '',
    resetEmail: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
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
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://topkit-admin-1.preview.emergentagent.com';

  const handleAuthFormSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 AuthModal - handleAuthFormSubmit called successfully!');
    
    // Get actual DOM values to handle autofill issues
    const emailInput = e.target.querySelector('input[type="email"]');
    const passwordInput = e.target.querySelector('input[type="password"]');
    const nameInput = e.target.querySelector('input[placeholder="Nom complet"]');
    
    const actualEmail = emailInput?.value || formData.email;
    const actualPassword = passwordInput?.value || formData.password;
    const actualName = nameInput?.value || formData.name;
    
    console.log('📧 Form data:', { 
      email: actualEmail, 
      password: actualPassword ? '***HIDDEN***' : 'EMPTY', 
      name: actualName 
    });
    console.log('🔄 isLogin mode:', isLogin);
    console.log('🌐 API URL:', API);
    
    // Update formData with actual values if they differ
    if (actualEmail !== formData.email || actualPassword !== formData.password || actualName !== formData.name) {
      setFormData({
        ...formData,
        email: actualEmail,
        password: actualPassword,
        name: actualName
      });
    }
    
    // Validation using actual values
    if (!actualEmail || !actualPassword) {
      console.error('❌ Missing required fields');
      setError('Veuillez remplir tous les champs requis');
      return;
    }

    if (!isLogin && !actualName) {
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
        email: actualEmail,
        password: '[HIDDEN]',
        ...(actualName && { name: actualName })
      });
      
      const response = await axios.post(fullUrl, {
        email: actualEmail,
        password: actualPassword,
        ...(actualName && { name: actualName })
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
          
          // Call success callback FIRST
          if (onLoginSuccess) {
            onLoginSuccess(response.data.token, response.data.user);
          }
          
          // Show success message
          console.log('✅ Login completed successfully');
          
          // Close modal AFTER callback
          setTimeout(() => {
            if (onClose) onClose();
          }, 100);
          
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
    setFormData({ 
      email: '', 
      password: '', 
      name: '',
      resetEmail: '',
      newPassword: '',
      confirmPassword: ''
    });
    setError('');
    setSuccessMessage('');
    setLoading(false);
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setShowForgotPassword(false);
    setShowResetForm(false);
    resetForm();
  };

  // Handle forgot password request
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    
    if (!formData.resetEmail) {
      setError('Veuillez saisir votre adresse email');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await axios.post(`${API}/api/auth/forgot-password`, {
        email: formData.resetEmail
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      setSuccessMessage(response.data.message || 'Un email de réinitialisation a été envoyé si cette adresse existe dans notre système.');
      setFormData({ ...formData, resetEmail: '' });
      
    } catch (error) {
      let errorMessage = 'Erreur lors de la demande de réinitialisation';
      
      if (error.response && error.response.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.request) {
        errorMessage = 'Erreur réseau. Vérifiez votre connexion.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle password reset with token
  const handleResetPassword = async (e) => {
    e.preventDefault();
    
    if (!formData.newPassword || !formData.confirmPassword) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.newPassword.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await axios.post(`${API}/api/auth/reset-password`, {
        token: resetToken,
        new_password: formData.newPassword
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json',
        }
      });

      setSuccessMessage(response.data.message || 'Mot de passe réinitialisé avec succès !');
      
      // Reset form and go back to login after successful reset
      setTimeout(() => {
        setShowResetForm(false);
        setShowForgotPassword(false);
        setIsLogin(true);
        resetForm();
      }, 2000);
      
    } catch (error) {
      let errorMessage = 'Erreur lors de la réinitialisation';
      
      if (error.response && error.response.data?.detail) {
        errorMessage = error.response.data.detail;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const handleModalClick = (e) => {
    // Close modal only if clicking on the backdrop (not the modal content)
    if (e.target === e.currentTarget) {
      setShowForgotPassword(false);
      setShowResetForm(false);
      resetForm();
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4" 
      style={{ zIndex: 9999, pointerEvents: 'auto' }}
      onClick={handleModalClick}
    >
      <div 
        className="bg-white rounded-lg shadow-2xl w-full max-w-md border border-gray-200"
        style={{ pointerEvents: 'auto' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-black">
            {showForgotPassword ? 'Mot de passe oublié' : 
             showResetForm ? 'Nouveau mot de passe' :
             isLogin ? 'Connexion' : 'Inscription'}
          </h2>
          <button 
            onClick={(e) => {
              e.stopPropagation();
              setShowForgotPassword(false);
              setShowResetForm(false);
              resetForm();
              onClose();
            }}
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

          {successMessage && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
              {successMessage}
            </div>
          )}

          {/* Forgot Password Form */}
          {showForgotPassword ? (
            <form onSubmit={handleForgotPassword} noValidate className="space-y-4">
              <p className="text-sm text-gray-600 mb-4">
                Saisissez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
              </p>
              
              <input
                type="email"
                placeholder="Adresse email"
                value={formData.resetEmail}
                onChange={(e) => setFormData({ ...formData, resetEmail: e.target.value })}
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={loading}
              />

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Envoi en cours...
                  </span>
                ) : (
                  'Envoyer le lien de réinitialisation'
                )}
              </button>

              <div className="text-center">
                <button
                  onClick={() => {
                    setShowForgotPassword(false);
                    resetForm();
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                  type="button"
                  disabled={loading}
                >
                  Retour à la connexion
                </button>
              </div>
            </form>
          ) : showResetForm ? (
            /* Reset Password Form */
            <form onSubmit={handleResetPassword} noValidate className="space-y-4">
              <p className="text-sm text-gray-600 mb-4">
                Saisissez votre nouveau mot de passe.
              </p>
              
              <input
                type="password"
                placeholder="Nouveau mot de passe"
                value={formData.newPassword}
                onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={loading}
              />

              <input
                type="password"
                placeholder="Confirmer le nouveau mot de passe"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={loading}
              />

              <div className="text-xs text-gray-600">
                Le mot de passe doit contenir au moins 8 caractères, incluant une majuscule, une minuscule, un chiffre et un caractère spécial.
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
          ) : (
            /* Regular Login/Register Form */
            <form onSubmit={handleAuthFormSubmit} noValidate className="space-y-4">
            {!isLogin && (
              <input
                type="text"
                placeholder="Nom complet"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                onBlur={(e) => setFormData({ ...formData, name: e.target.value })} // Handle autofill
                autoComplete="name"
                className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
                disabled={loading}
              />
            )}

            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              onBlur={(e) => setFormData({ ...formData, email: e.target.value })} // Handle autofill
              autoComplete="email"
              className="w-full p-3 bg-gray-50 border border-gray-300 rounded-lg text-black placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
              disabled={loading}
            />

            <input
              type="password"
              placeholder="Mot de passe"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              onBlur={(e) => setFormData({ ...formData, password: e.target.value })} // Handle autofill
              autoComplete="current-password"
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
          )}

          {/* Forgot Password Link - Only show in login mode and not in forgot password mode */}
          {isLogin && !showForgotPassword && !showResetForm && (
            <div className="text-center mt-3">
              <button
                onClick={() => {
                  setShowForgotPassword(true);
                  setError('');
                  setSuccessMessage('');
                }}
                className="text-sm text-blue-600 hover:text-blue-800 underline"
                type="button"
                disabled={loading}
              >
                Mot de passe oublié ?
              </button>
            </div>
          )}

          {/* Switch between login/register - Only show in regular mode */}
          {!showForgotPassword && !showResetForm && (
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
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;