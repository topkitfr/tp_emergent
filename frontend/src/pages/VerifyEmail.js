// frontend/src/pages/VerifyEmail.js
import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { BACKEND_URL } from '@/lib/api';

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token          = searchParams.get('token') || '';
  const [status, setStatus] = useState('loading'); // loading | success | error
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Lien invalide ou manquant.');
      return;
    }
    fetch(`${BACKEND_URL}/api/auth/verify-email?token=${encodeURIComponent(token)}`)
      .then(r => r.json().then(d => ({ ok: r.ok, data: d })))
      .then(({ ok, data }) => {
        if (ok) {
          setStatus('success');
        } else {
          setStatus('error');
          setMessage(data.detail || 'Lien invalide ou expiré.');
        }
      })
      .catch(() => {
        setStatus('error');
        setMessage('Une erreur est survenue. Réessaie plus tard.');
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm text-center space-y-6">

        <Link to="/">
          <img src="/topkit-logo.png" alt="Topkit" className="h-8 object-contain mx-auto" />
        </Link>

        {status === 'loading' && (
          <div className="flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-muted-foreground">Vérification en cours…</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-4">
            <div className="border border-green-600 p-6 space-y-2">
              <p className="text-green-400 text-lg font-semibold">✅ Email confirmé !</p>
              <p className="text-sm text-muted-foreground">
                Ton adresse email a bien été vérifiée. Ton compte est maintenant complet.
              </p>
            </div>
            <Link to="/browse" className="text-xs text-primary underline">
              Accéder à Topkit →
            </Link>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <div className="border border-red-600 p-6 space-y-2">
              <p className="text-red-400 text-lg font-semibold">❌ Lien invalide</p>
              <p className="text-sm text-muted-foreground">{message}</p>
            </div>
            <Link to="/" className="text-xs text-primary underline">
              ← Retour à l'accueil
            </Link>
          </div>
        )}

      </div>
    </div>
  );
}
