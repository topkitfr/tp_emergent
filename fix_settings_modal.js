const fs = require('fs');

// Read the App.js file
let content = fs.readFileSync('/app/frontend/src/App.js', 'utf8');

// Find the UserSettingsPanel component
const componentStart = content.indexOf('const UserSettingsPanel = ({ user, profileData, onProfileUpdated, onClose }) => {');
const componentEnd = content.indexOf('// User Profile Page Component', componentStart);

if (componentStart === -1 || componentEnd === -1) {
    console.error('Could not find UserSettingsPanel component boundaries');
    process.exit(1);
}

// Extract the part before the component
const beforeComponent = content.substring(0, componentStart);

// Extract the part after the component
const afterComponent = content.substring(componentEnd);

// Create a properly structured UserSettingsPanel component
const newComponent = `const UserSettingsPanel = ({ user, profileData, onProfileUpdated, onClose }) => {
  const [activeSettingsTab, setActiveSettingsTab] = useState('security');
  const [show2FASetup, setShow2FASetup] = useState(false);
  const [showPasswordChange, setShowPasswordChange] = useState(false);
  const [settingsData, setSettingsData] = useState({
    seller_settings: {
      address_settings: {
        full_name: '',
        address_line_1: '',
        address_line_2: '',
        city: '',
        postal_code: '',
        country: '',
        phone_number: ''
      }
    },
    buyer_settings: {
      address_settings: {
        full_name: '',
        address_line_1: '',
        address_line_2: '',
        city: '',
        postal_code: '',
        country: '',
        phone_number: ''
      }
    }
  });
  const [loading, setLoading] = useState(false);

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (profileData) {
      setSettingsData({
        seller_settings: profileData.seller_settings || {
          address_settings: {
            full_name: '',
            address_line_1: '',
            address_line_2: '',
            city: '',
            postal_code: '',
            country: '',
            phone_number: ''
          }
        },
        buyer_settings: profileData.buyer_settings || {
          address_settings: {
            full_name: '',
            address_line_1: '',
            address_line_2: '',
            city: '',
            postal_code: '',
            country: '',
            phone_number: ''
          }
        }
      });
    }
  }, [profileData]);

  const updateSettings = async (section, data) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      await axios.put(\`\${API}/api/users/profile/settings\`, {
        [section]: data
      }, {
        headers: { Authorization: \`Bearer \${token}\` }
      });

      window.dispatchEvent(new CustomEvent('show-toast', {
        detail: { message: 'Paramètres mis à jour avec succès!', type: 'success' }
      }));

      if (onProfileUpdated) onProfileUpdated();

    } catch (error) {
      console.error('Settings update error:', error);
      window.dispatchEvent(new CustomEvent('show-toast', {
        detail: { 
          message: error.response?.data?.detail || 'Erreur lors de la mise à jour', 
          type: 'error' 
        }
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleAddressChange = (section, field, value) => {
    setSettingsData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        address_settings: {
          ...prev[section].address_settings,
          [field]: value
        }
      }
    }));
  };

  const saveAddressSettings = (section) => {
    updateSettings(section, settingsData[section]);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl p-8 max-w-4xl w-full mx-4 max-h-screen overflow-y-auto border border-gray-800">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">⚙️ Paramètres du compte</h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        <div className="space-y-6">
          {/* Settings Tabs */}
          <div className="border-b border-gray-700">
            <nav className="flex space-x-8">
              {[
                { id: 'security', label: '🔒 Sécurité' },
                { id: 'seller', label: '💼 Paramètres vendeur' },
                { id: 'buyer', label: '🛒 Paramètres acheteur' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveSettingsTab(tab.id)}
                  className={\`py-2 px-1 border-b-2 font-medium text-sm \${
                    activeSettingsTab === tab.id
                      ? 'border-blue-500 text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-300'
                  }\`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Security Settings */}
          {activeSettingsTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-gray-800 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Sécurité du compte</h3>
                
                <div className="space-y-4">
                  {/* Password Change */}
                  <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                    <div>
                      <h4 className="font-medium text-white">Mot de passe</h4>
                      <p className="text-sm text-gray-400">Modifiez votre mot de passe de connexion</p>
                    </div>
                    <button
                      onClick={() => setShowPasswordChange(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Modifier
                    </button>
                  </div>

                  {/* Two-Factor Authentication */}
                  <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                    <div>
                      <h4 className="font-medium text-white">Authentification à deux facteurs (2FA)</h4>
                      <p className="text-sm text-gray-400">
                        {user.two_factor_enabled 
                          ? 'Protection supplémentaire activée avec Google Authenticator'
                          : 'Ajoutez une couche de sécurité supplémentaire à votre compte'
                        }
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={\`px-2 py-1 rounded-full text-xs \${
                        user.two_factor_enabled ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                      }\`}>
                        {user.two_factor_enabled ? 'Activé' : 'Désactivé'}
                      </span>
                      <button
                        onClick={() => setShow2FASetup(true)}
                        disabled={user.two_factor_enabled}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {user.two_factor_enabled ? 'Configuré' : 'Configurer'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Other tabs content would go here */}
          {activeSettingsTab === 'seller' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Paramètres vendeur</h3>
              <p className="text-gray-400">Configuration des paramètres de vente...</p>
            </div>
          )}

          {activeSettingsTab === 'buyer' && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Paramètres acheteur</h3>
              <p className="text-gray-400">Configuration des paramètres d'achat...</p>
            </div>
          )}
        </div>

        {/* Modals */}
        {show2FASetup && (
          <TwoFactorAuthSetup
            isOpen={show2FASetup}
            onClose={() => setShow2FASetup(false)}
            onSuccess={() => {
              setShow2FASetup(false);
              if (onProfileUpdated) onProfileUpdated();
            }}
          />
        )}

        {showPasswordChange && (
          <PasswordChangeModal
            isOpen={showPasswordChange}
            onClose={() => setShowPasswordChange(false)}
            onSuccess={() => {
              setShowPasswordChange(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

`;

// Combine the parts
const newContent = beforeComponent + newComponent + afterComponent;

// Write the fixed file
fs.writeFileSync('/app/frontend/src/App.js', newContent);

console.log('UserSettingsPanel component has been fixed and converted to a modal!');