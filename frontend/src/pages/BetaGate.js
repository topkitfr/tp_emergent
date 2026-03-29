import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

// Codes d'accès beta valides — à modifier selon tes besoins
const VALID_CODES = ['TOPKIT2025', 'BETA-KIT', 'TK-TESTER'];

export default function BetaGate({ onAccess }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [shake, setShake] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    setTimeout(() => {
      const trimmed = code.trim().toUpperCase();
      if (VALID_CODES.includes(trimmed)) {
        onAccess();
      } else {
        setError('Code invalide. Vérifie ton invitation.');
        setShake(true);
        setTimeout(() => setShake(false), 600);
      }
      setLoading(false);
    }, 400);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="mb-8 text-center">
          <Link to="/">
            <img
              src="/topkit-logo.png"
              alt="Topkit"
              className="h-8 object-contain mx-auto"
            />
          </Link>
        </div>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-lg font-semibold text-foreground">Accès bêta privé</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Topkit est en période de test. Entre ton code d'invitation pour accéder au site.
          </p>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className={`space-y-4 ${shake ? 'animate-shake' : ''}`}
        >
          <div className="space-y-1">
            <label
              htmlFor="beta-code"
              className="text-xs text-muted-foreground uppercase tracking-wider"
            >
              Code d'accès
            </label>
            <Input
              id="beta-code"
              type="text"
              placeholder="ex: TOPKIT2025"
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                setError('');
              }}
              className="rounded-none font-mono uppercase tracking-widest"
              autoFocus
              autoComplete="off"
              spellCheck={false}
              required
            />
          </div>

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}

          <Button
            type="submit"
            className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
            disabled={loading || !code.trim()}
          >
            {loading ? 'Vérification...' : 'Accéder au site'}
          </Button>
        </form>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-muted-foreground">
          Tu n'as pas de code ?{' '}
          <a
            href="mailto:contact@topkit.app"
            className="hover:text-foreground transition-colors underline underline-offset-2"
          >
            Demande une invitation
          </a>
        </p>

      </div>
    </div>
  );
}
