// frontend/src/pages/ForgotPassword.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { API_BASE } from '@/lib/api';

export default function ForgotPassword() {
  const [email, setEmail]     = useState('');
  const [loading, setLoading] = useState(false);
  const [sent, setSent]       = useState(false);
  const [error, setError]     = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      // Toujours afficher le message de succès (anti-enumeration)
      setSent(true);
    } catch {
      setError('Une erreur est survenue. Réessaie.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        <div className="mb-8 text-center">
          <Link to="/">
            <img src="/topkit-logo.png" alt="Topkit" className="h-8 object-contain mx-auto" />
          </Link>
        </div>

        <h1 className="text-lg font-semibold text-foreground mb-1">
          Mot de passe oublié
        </h1>
        <p className="text-sm text-muted-foreground mb-6">
          Saisis ton email et on t'envoie un lien de réinitialisation.
        </p>

        {sent ? (
          <div className="border border-border p-4 text-sm text-foreground space-y-3">
            <p>
              Si cette adresse est associée à un compte, tu recevras un email
              dans quelques minutes.
            </p>
            <p className="text-muted-foreground text-xs">
              Pense à vérifier tes spams.
            </p>
            <Link
              to="/login"
              className="block text-center text-xs text-primary underline mt-2"
            >
              Retour à la connexion
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="rounded-none"
              required
            />

            {error && <p className="text-sm text-red-500">{error}</p>}

            <Button
              type="submit"
              className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={loading}
            >
              {loading ? 'Envoi...' : 'Envoyer le lien'}
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
