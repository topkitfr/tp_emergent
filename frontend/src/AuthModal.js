import React, { useState } from 'react';

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
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  const handleAuthFormSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🚀 AuthModal - Form submission started');
    console.log('📧 Email from state:', formData.email);
    console.log('🔑 Password provided:', !!formData.password);
    console.log('🔄 Is login mode:', isLogin);

    if (!formData.email || !formData.password) {
      console.error('❌ Missing required fields');
      setError('Email and password are required');
      return;
    }
    
    if (!isLogin && !formData.name) {
      console.error('❌ Missing name for registration');
      setError('Name is required for registration');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { 
            email: formData.email.trim(), 
            password: formData.password 
          }
        : { 
            email: formData.email.trim(), 
            password: formData.password, 
            name: formData.name.trim() 
          };

      console.log('📤 API URL:', `${API}/api${endpoint}`);
      console.log('📦 Payload:', { ...payload, password: '[HIDDEN]' });
      
      const response = await fetch(`${API}/api${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Response received:', response.status);

      if (isLogin) {
        console.log('🎉 Login successful, calling onLoginSuccess');
        
        // Call the parent's login success handler
        onLoginSuccess(data.token, data.user);
        onClose();
      } else {
        console.log('📝 Registration successful');
        alert('Registration successful! You can now sign in.');
        setIsLogin(true); // Switch to login mode
      }
      
    } catch (error) {
      console.error('❌ Authentication error:', error);
      
      let errorMessage = 'Connection error';
      
      // Handle fetch-specific errors
      if (error.message && error.message.includes('HTTP')) {
        const statusMatch = error.message.match(/HTTP (\d+):/);
        if (statusMatch) {
          const status = parseInt(statusMatch[1]);
          if (status === 400 || status === 401) {
            errorMessage = 'Invalid email or password';
          } else if (status === 422) {
            errorMessage = 'Invalid data format';
          } else {
            errorMessage = `Server error (${status})`;
          }
        }
      } else if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        console.error('📡 Network error - failed to reach server');
        errorMessage = 'Network error. Check your connection.';
      } else {
        console.error('⚠️ Request error:', error.message);
        errorMessage = 'Connection error';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      console.log('Sending password reset request for:', formData.resetEmail);
      
      const response = await axios.post(`${API}/api/auth/request-password-reset`, {
        email: formData.resetEmail
      });

      console.log('Password reset response:', response.data);
      setSuccessMessage('Reset link sent to your email if the account exists.');
      setFormData({ ...formData, resetEmail: '' });
      
    } catch (error) {
      console.error('Password reset error:', error);
      
      let errorMessage = 'Error sending reset email';
      
      if (error.response) {
        errorMessage = error.response.data.detail;
      } else if (error.request) {
        errorMessage = 'Network error. Check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await axios.post(`${API}/api/auth/reset-password`, {
        token: resetToken,
        new_password: formData.newPassword
      });

      setSuccessMessage('Password reset successfully. You can now sign in with your new password.');
      setShowResetForm(false);
      setIsLogin(true);
      setFormData({ ...formData, newPassword: '', confirmPassword: '' });
      
    } catch (error) {
      console.error('Password reset error:', error);
      
      let errorMessage = 'Error resetting password';
      
      if (error.response) {
        errorMessage = error.response.data.detail;
      } else if (error.request) {
        errorMessage = 'Network error. Check your connection.';
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
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    resetForm();
  };

  const handleInputChange = (field, value) => {
    console.log(`📝 Input change - ${field}:`, value ? 'VALUE_SET' : 'EMPTY');
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleModalClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={handleModalClick}
      style={{ zIndex: 9999 }}
    >
      <div 
        className="bg-white rounded-lg shadow-2xl w-full max-w-md border border-gray-200"
        style={{ position: 'relative', zIndex: 10000 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-black">
            {showForgotPassword ? 'Forgot Password' : 
             showResetForm ? 'New Password' :
             isLogin ? 'Sign In' : 'Sign Up'}
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
                Enter your email address and we'll send you a link to reset your password.
              </p>
              
              <input
                type="email"
                name="resetEmail"
                placeholder="Email address"
                value={formData.resetEmail}
                onChange={(e) => handleInputChange('resetEmail', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50"
                >
                  {loading ? 'Sending...' : 'Send Reset Link'}
                </button>
                
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(false);
                    resetForm();
                  }}
                  disabled={loading}
                >
                  Back to Sign In
                </button>
              </div>
            </form>

          /* Password Reset Form */
          ) : showResetForm ? (
            <form onSubmit={handlePasswordReset} noValidate className="space-y-4">
              <input
                type="password"
                name="newPassword"
                placeholder="New password"
                value={formData.newPassword}
                onChange={(e) => handleInputChange('newPassword', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm new password"
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50"
              >
                {loading ? 'Updating...' : 'Update Password'}
              </button>
            </form>

          /* Login/Register Form */
          ) : (
            <form onSubmit={handleAuthFormSubmit} noValidate className="space-y-4">
              
              {/* Name field (registration only) */}
              {!isLogin && (
                <input
                  id="auth-name-field"
                  type="text"
                  name="name"
                  placeholder="Full name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  onInput={(e) => handleInputChange('name', e.target.value)}
                  onBlur={(e) => handleInputChange('name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              )}
              
              {/* Email field */}
              <input
                id="auth-email-field"
                type="email"
                name="email"
                placeholder="Email address"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                onInput={(e) => handleInputChange('email', e.target.value)}
                onBlur={(e) => handleInputChange('email', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                autoComplete="email"
              />
              
              {/* Password field */}
              <input
                id="auth-password-field"
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                onInput={(e) => handleInputChange('password', e.target.value)}
                onBlur={(e) => handleInputChange('password', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                autoComplete={isLogin ? "current-password" : "new-password"}
              />

              {/* Password strength indicator (registration only) */}
              {!isLogin && formData.password && (
                <div className="space-y-2">
                  <div className="text-xs text-gray-600">Password strength:</div>
                  <div className="space-y-1">
                    <div className={`text-xs ${passwordValidation.minLength ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordValidation.minLength ? '✓' : '×'} At least 8 characters
                    </div>
                    <div className={`text-xs ${passwordValidation.hasUppercase ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordValidation.hasUppercase ? '✓' : '×'} Uppercase letter
                    </div>
                    <div className={`text-xs ${passwordValidation.hasLowercase ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordValidation.hasLowercase ? '✓' : '×'} Lowercase letter
                    </div>
                    <div className={`text-xs ${passwordValidation.hasNumber ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordValidation.hasNumber ? '✓' : '×'} Number
                    </div>
                    <div className={`text-xs ${passwordValidation.hasSpecial ? 'text-green-600' : 'text-red-600'}`}>
                      {passwordValidation.hasSpecial ? '✓' : '×'} Special character
                    </div>
                  </div>
                </div>
              )}
              
              {/* Forgot password link (login only) */}
              {isLogin && (
                <div className="text-right">
                  <button
                    type="button"
                    onClick={() => {
                      setShowForgotPassword(true);
                      resetForm();
                    }}
                    className="text-sm text-blue-600 hover:text-blue-800"
                  >
                    Forgot your password?
                  </button>
                </div>
              )}
              
              {/* Submit button */}
              <button
                type="submit"
                disabled={loading || (!isLogin && Object.values(passwordValidation).some(v => !v))}
                className="w-full bg-black hover:bg-gray-800 text-white py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {isLogin ? 'Signing In...' : 'Signing Up...'}
                  </span>
                ) : (
                  isLogin ? 'Sign In' : 'Sign Up'
                )}
              </button>
            </form>
          )}

          {/* Toggle between login/register */}
          {!showForgotPassword && !showResetForm && (
            <div className="mt-6 text-center">
              <span className="text-sm text-gray-600">
                {isLogin ? "Don't have an account? " : 'Already have an account? '}
              </span>
              <button
                onClick={toggleMode}
                className="text-sm text-blue-600 hover:text-blue-800 font-semibold"
              >
                {isLogin ? 'Sign up here' : 'Sign in here'}
              </button>
            </div>
          )}

          {/* Email verification notice */}
          {!isLogin && !showForgotPassword && !showResetForm && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-700">
                <strong>Note:</strong> After registration, you may need to verify your email address before accessing all features.
              </p>
              
              <div className="mt-3 space-y-1">
                <>
                  <p className="text-xs text-blue-700 font-semibold">Test credentials:</p>
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ...formData,
                        email: 'steinmetzlivio@gmail.com',
                        password: 'T0p_Mdp_1288*'
                      });
                    }}
                    disabled={loading}
                  >
                    Sign In
                  </button>
                </>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal;