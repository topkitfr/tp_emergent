// frontend/src/pages/ResetPassword.js
import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { API_BASE } from '@/lib/api';

export default function ResetPassword() {
  const [searchParams]          = useSearchParams();
  const token                   = searchParams.get('token') || '';
  const navigate                = useNavigate();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm]   = useState('');
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');
  const [success, setSuccess]   = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!token) {
      setError('Lien invalide ou expiré.');
      return;
    }
    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères.');
      return;
    }
    if (password !== confirm) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: password }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Une erreur est survenue.');
      } else {
        setSuccess(true);
        setTimeout(() => navigate('/login'), 2500);
      }
    } catch {
      setError('Une erreur est survenue. Réessaie.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="w-full max-w-sm text-center space-y-4">
          <p className="text-red-500 text-sm">Lien invalide ou expiré.</p>
          <Link to="/forgot-password" className="text-xs text-primary underline">
            Demander un nouveau lien
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        <div className="mb-8 text-center">
          <Link to="/">
            <img src="/topkit-logo.png" alt="Topkit" className="h-8 object-contain mx-auto" />
          </Link>
        </div>

        <h1 className="text-lg font-semibold text-foreground mb-1">
          Nouveau mot de passe
        </h1>
        <p className="text-sm text-muted-foreground mb-6">
          Choisis un nouveau mot de passe pour ton compte.
        </p>

        {success ? (
          <div className="border border-green-600 p-4 text-sm text-green-400 text-center space-y-2">
            <p>✅ Mot de passe réinitialisé !</p>
            <p className="text-xs text-muted-foreground">Redirection vers la connexion...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="password"
              placeholder="Nouveau mot de passe (8 chars min)"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="rounded-none"
              required
              minLength={8}
            />
            <Input
              type="password"
              placeholder="Confirmer le mot de passe"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              className="rounded-none"
              required
            />

            {error && <p className="text-sm text-red-500">{error}</p>}

            <Button
              type="submit"
              className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={loading}
            >
              {loading ? 'Réinitialisation...' : 'Réinitialiser le mot de passe'}
            </Button>

            <p className="text-center text-xs text-muted-foreground">
              <Link to="/login" className="hover:text-foreground transition-colors">
                ← Retour à la connexion
              </Link>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
