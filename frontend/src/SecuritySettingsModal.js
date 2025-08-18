import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TwoFactorAuthSetup from './TwoFactorAuthSetup';
import PasswordChangeModal from './PasswordChangeModal';

const SecuritySettingsModal = ({ user, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('security');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [securityInfo, setSecurityInfo] = useState({
    has_2fa: false,
    password_last_changed: null,
    login_history: [],
    security_alerts: true,
    email_notifications: true
  });

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (isOpen && user) {
      fetchSecurityInfo();
    }
  }, [isOpen, user]);

  const fetchSecurityInfo = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/api/users/security-info`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSecurityInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch security info:', error);
      setError('Failed to load security information');
    } finally {
      setLoading(false);
    }
  };

  const updateSecuritySettings = async (setting, value) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/api/users/security-settings`, {
        [setting]: value
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSecurityInfo(prev => ({ ...prev, [setting]: value }));
      setSuccess('Security settings updated successfully');
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      setError('Failed to update security settings');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg max-w-4xl w-full mx-4 p-6 max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Security & Privacy Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl font-bold"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-600 text-white px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-600 text-white px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <div className="space-y-6">
          
          {/* Two-Factor Authentication Section */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Two-Factor Authentication</h3>
                <p className="text-gray-400 text-sm">
                  Add an extra layer of security to your account with 2FA
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  securityInfo.has_2fa 
                    ? 'bg-green-800 text-green-200' 
                    : 'bg-red-800 text-red-200'
                }`}>
                  {securityInfo.has_2fa ? '🔒 Enabled' : '🔓 Disabled'}
                </span>
                <button
                  onClick={() => setShow2FASetup(true)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    securityInfo.has_2fa
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {securityInfo.has_2fa ? 'Disable 2FA' : 'Enable 2FA'}
                </button>
              </div>
            </div>
          </div>

          {/* Password Security Section */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">Password Security</h3>
                <p className="text-gray-400 text-sm">
                  Keep your account secure with a strong password
                </p>
                {securityInfo.password_last_changed && (
                  <p className="text-gray-500 text-xs mt-1">
                    Last changed: {new Date(securityInfo.password_last_changed).toLocaleDateString()}
                  </p>
                )}
              </div>
              <button
                onClick={() => setShowPasswordModal(true)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Change Password
              </button>
            </div>
          </div>

          {/* Security Alerts Section */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Security Notifications</h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-white font-medium">Security Alerts</label>
                  <p className="text-gray-400 text-sm">
                    Get notified about suspicious account activity
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={securityInfo.security_alerts}
                  onChange={(e) => updateSecuritySettings('security_alerts', e.target.checked)}
                  className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-white font-medium">Email Notifications</label>
                  <p className="text-gray-400 text-sm">
                    Receive email alerts for password changes and login attempts
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={securityInfo.email_notifications}
                  onChange={(e) => updateSecuritySettings('email_notifications', e.target.checked)}
                  className="w-5 h-5 text-blue-600 bg-gray-800 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Login History Section */}
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">Recent Login Activity</h3>
            
            {loading ? (
              <div className="text-gray-400">Loading login history...</div>
            ) : securityInfo.login_history?.length > 0 ? (
              <div className="space-y-3 max-h-48 overflow-y-auto">
                {securityInfo.login_history.slice(0, 10).map((login, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                    <div>
                      <div className="text-white font-medium">
                        {login.location || 'Unknown location'}
                      </div>
                      <div className="text-gray-400 text-sm">
                        {login.ip_address} • {login.user_agent?.split(' ')[0] || 'Unknown browser'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-gray-300 text-sm">
                        {new Date(login.timestamp).toLocaleDateString()}
                      </div>
                      <div className="text-gray-500 text-xs">
                        {new Date(login.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-400">No recent login activity</div>
            )}
          </div>
        </div>

        {/* Close Button */}
        <div className="flex justify-end mt-6 pt-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </div>

      {/* 2FA Setup Modal */}
      {show2FASetup && (
        <TwoFactorAuthSetup
          user={user}
          onClose={() => setShow2FASetup(false)}
          onSuccess={() => {
            setShow2FASetup(false);
            fetchSecurityInfo(); // Refresh security info
          }}
        />
      )}

      {/* Password Change Modal */}
      {showPasswordModal && (
        <PasswordChangeModal
          isOpen={showPasswordModal}
          onClose={() => setShowPasswordModal(false)}
          onSuccess={() => {
            setShowPasswordModal(false);
            fetchSecurityInfo(); // Refresh security info
          }}
        />
      )}
    </div>
  );
};

export default SecuritySettingsModal;