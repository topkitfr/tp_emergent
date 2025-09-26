import React, { useState, useEffect } from 'react';

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
  const [googleLoading, setGoogleLoading] = useState(false);
  
  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Handle Google OAuth session on component mount
  useEffect(() => {
    const handleGoogleSession = async () => {
      // Check for session_id in URL fragment
      const hash = window.location.hash;
      const sessionMatch = hash.match(/session_id=([^&]+)/);
      
      if (sessionMatch) {
        const sessionId = sessionMatch[1];
        setGoogleLoading(true);
        
        try {
          console.log('🔑 Processing Google OAuth session:', sessionId);
          
          const response = await fetch(`${API}/api/auth/google/session`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId })
          });
          
          if (response.ok) {
            const data = await response.json();
            console.log('✅ Google OAuth successful');
            
            // Clean URL fragment
            window.history.replaceState(null, null, window.location.pathname + window.location.search);
            
            // Store user data and token
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Close modal and trigger success callback
            onClose();
            if (onLoginSuccess) {
              onLoginSuccess(data);
            }
          } else {
            console.error('❌ Google OAuth failed:', response.status);
            setError('Google authentication failed. Please try again.');
          }
        } catch (error) {
          console.error('❌ Google OAuth error:', error);
          setError('Google authentication error. Please try again.');
        } finally {
          setGoogleLoading(false);
        }
      }
    };

    if (isOpen) {
      handleGoogleSession();
    }
  }, [isOpen, API, onClose, onLoginSuccess]);

  // Google OAuth login function
  const handleGoogleLogin = () => {
    console.log('🔍 Starting Google OAuth...');
    const redirectUrl = encodeURIComponent(window.location.origin + '/');
    const googleAuthUrl = `https://auth.emergentagent.com/?redirect=${redirectUrl}`;
    
    console.log('🌐 Redirecting to:', googleAuthUrl);
    window.location.href = googleAuthUrl;
  };
  
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

  const handleAuthFormSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    console.log('🚀 AuthModal - Form submission started');
    console.log('📊 Current formData state:', formData);
    console.log('📧 Email from state:', formData.email || 'UNDEFINED');
    console.log('🔑 Password from state:', formData.password || 'UNDEFINED');
    console.log('🔑 Password provided:', !!formData.password);
    console.log('🔄 Is login mode:', isLogin);

    // Also check DOM values for debugging
    const emailField = document.getElementById('auth-email-field');
    const passwordField = document.getElementById('auth-password-field');
    
    if (emailField && passwordField) {
      console.log('📧 Email from DOM:', emailField.value || 'EMPTY');
      console.log('🔑 Password from DOM:', passwordField.value || 'EMPTY');
    }

    if (!formData.email || !formData.password) {
      console.error('❌ Missing required fields in formData state');
      console.error('❌ formData.email:', formData.email);
      console.error('❌ formData.password:', formData.password);
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
        setSuccessMessage('Registration successful! You are now signed in.');
        
        // Auto-login the user after successful registration
        if (data.token && data.user) {
          console.log('🎉 Auto-login after registration successful');
          onLoginSuccess(data.token, data.user);
          onClose();
        } else {
          // Fallback: show success message and switch to login mode
          setTimeout(() => {
            setSuccessMessage('');
            setIsLogin(true); // Switch to login mode
          }, 2000);
        }
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
            // Different error messages based on login vs signup context
            if (isLogin) {
              errorMessage = 'Invalid email or password';
            } else {
              errorMessage = 'Email already exists or invalid data. Please try a different email or sign in instead.';
            }
          } else if (status === 422) {
            errorMessage = isLogin ? 'Invalid login data' : 'Please check your registration details';
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
      
      const response = await fetch(`${API}/api/auth/request-password-reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.resetEmail
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('Password reset response:', data);
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
      const response = await fetch(`${API}/api/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: resetToken,
          new_password: formData.newPassword
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

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
    console.log(`📝 Input change - ${field}:`, value || 'EMPTY_VALUE');
    console.log('📊 Previous formData:', formData);
    
    const newFormData = {
      ...formData,
      [field]: value
    };
    
    console.log('📊 New formData:', newFormData);
    setFormData(newFormData);
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

          {/* Google OAuth Section */}
          {!showForgotPassword && !showResetForm && (
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">Or continue with</span>
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={handleGoogleLogin}
                  disabled={loading || googleLoading}
                  className="w-full flex justify-center items-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 transition-colors"
                >
                  {googleLoading ? (
                    <span className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 mr-2"></div>
                      Connecting to Google...
                    </span>
                  ) : (
                    <span className="flex items-center">
                      <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                      </svg>
                      Google
                    </span>
                  )}
                </button>
              </div>
            </div>
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