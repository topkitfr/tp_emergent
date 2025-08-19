import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TwoFactorAuthSetup = ({ user, onClose, onSuccess }) => {
  const [step, setStep] = useState('setup'); // setup, verify, success
  const [qrCode, setQrCode] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationToken, setVerificationToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Get API URL from environment
  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'https://kit-beta.preview.emergentagent.com';

  useEffect(() => {
    setupTwoFactor();
  }, []);

  const setupTwoFactor = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/api/auth/2fa/setup`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setQrCode(response.data.qr_code);
      setSecret(response.data.secret);
      setBackupCodes(response.data.backup_codes);
      setError('');
    } catch (error) {
      setError('Erreur lors de la configuration 2FA: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const enableTwoFactor = async () => {
    if (!verificationToken) {
      setError('Veuillez entrer le code de vérification');
      return;
    }

    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      await axios.post(`${API}/api/auth/2fa/enable`, {
        token: verificationToken
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setStep('success');
      setError('');
      if (onSuccess) onSuccess();
    } catch (error) {
      setError('Code de vérification invalide. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const downloadBackupCodes = () => {
    const element = document.createElement('a');
    const file = new Blob([backupCodes.join('\n')], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = 'topkit-backup-codes.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  if (loading && step === 'setup') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Configuration de l'authentification à deux facteurs...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-lg w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {step === 'setup' && 'Configuration 2FA'}
            {step === 'verify' && 'Vérification 2FA'}
            {step === 'success' && '2FA Activé'}
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

        {step === 'setup' && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-3">Étape 1: Scanner le QR Code</h3>
              <p className="text-gray-600 mb-4">
                Utilisez Google Authenticator ou une autre app 2FA pour scanner ce code QR :
              </p>
              <div className="bg-white p-4 border rounded-lg inline-block">
                <img src={`data:image/png;base64,${qrCode}`} alt="QR Code 2FA" className="w-48 h-48" />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Clé secrète (si scanner impossible) : <code className="bg-gray-100 px-2 py-1 rounded">{secret}</code>
              </p>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-3">Étape 2: Codes de sauvegarde</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 mb-3">
                  ⚠️ Sauvegardez ces codes de récupération dans un endroit sûr :
                </p>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {backupCodes.map((code, index) => (
                    <code key={index} className="bg-white px-2 py-1 rounded text-sm font-mono">
                      {code}
                    </code>
                  ))}
                </div>
                <button
                  onClick={downloadBackupCodes}
                  className="text-blue-600 hover:text-blue-700 text-sm underline"
                >
                  📥 Télécharger les codes
                </button>
              </div>
            </div>

            <button
              onClick={() => setStep('verify')}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Continuer vers la vérification
            </button>
          </div>
        )}

        {step === 'verify' && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-3">Vérification</h3>
              <p className="text-gray-600 mb-4">
                Entrez le code à 6 chiffres généré par votre app d'authentification :
              </p>
            </div>

            <div>
              <input
                type="text"
                placeholder="123456"
                value={verificationToken}
                onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-center text-2xl font-mono tracking-widest"
                maxLength="6"
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setStep('setup')}
                className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Retour
              </button>
              <button
                onClick={enableTwoFactor}
                disabled={loading || verificationToken.length !== 6}
                className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Vérification...' : 'Activer 2FA'}
              </button>
            </div>
          </div>
        )}

        {step === 'success' && (
          <div className="text-center space-y-6">
            <div className="text-green-600 text-6xl">✅</div>
            <div>
              <h3 className="text-lg font-semibold text-green-600 mb-2">
                Authentification à deux facteurs activée !
              </h3>
              <p className="text-gray-600">
                Votre compte est maintenant protégé par l'authentification à deux facteurs.
              </p>
            </div>
            <button
              onClick={onClose}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Fermer
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TwoFactorAuthSetup;