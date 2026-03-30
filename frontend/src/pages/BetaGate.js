import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const BETA_STORAGE_KEY = 'topkit_beta_validated';

export default function BetaGate({ onAccess }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [shake, setShake] = useState(false);
  const inputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading || success) return;
    setError('');
    setLoading(true);

    try {
      const res = await fetch('/api/beta/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code.trim() }),
      });

      if (res.ok) {
        localStorage.setItem(BETA_STORAGE_KEY, 'true'); // ← Sauvegarde
        setSuccess(true);
        setTimeout(() => onAccess(), 800);
      } else {
        setError('Code invalide. Verifie ton invitation.');
        setShake(true);
        setTimeout(() => {
          setShake(false);
          inputRef.current?.focus();
          inputRef.current?.select();
        }, 600);
      }
    } catch {
      setError('Erreur reseau. Reessaie.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-sm space-y-6">
        {/* Logo */}
        <div className="flex justify-center">
          <span className="text-2xl font-bold tracking-tight">Topkit</span>
        </div>

        {/* Badge beta */}
        <div className="flex justify-center">
          <span className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border border-border bg-muted text-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
            Beta privee
          </span>
        </div>

        {/* Header */}
        <div className="text-center space-y-1 border-t border-border pt-6">
          <h1 className="text-xl font-semibold">Acces sur invitation</h1>
          <p className="text-sm text-muted-foreground">
            Topkit est en periode de test ferme. Entre ton code d&apos;invitation pour acceder a la plateforme.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label htmlFor="beta-code" className="text-sm font-medium">
              Code d&apos;acces
            </label>
            <Input
              ref={inputRef}
              id="beta-code"
              type="text"
              placeholder=""
              value={code}
              onChange={(e) => {
                setCode(e.target.value);
                if (error) setError('');
              }}
              className={`rounded-none font-mono uppercase tracking-widest transition-all ${
                success
                  ? 'border-green-500 bg-green-500/5 text-green-600'
                  : error
                  ? 'border-red-400'
                  : ''
              } ${shake ? 'animate-shake' : ''}`}
              autoFocus
              autoComplete="off"
              spellCheck={false}
              required
              disabled={success}
            />
          </div>

          {/* Error */}
          {error && (
            <p className="text-sm text-red-500 flex items-center gap-1.5">
              <span>&#x26A0;</span>
              {error}
            </p>
          )}

          {/* Success */}
          {success && (
            <p className="text-sm text-green-600 flex items-center gap-1.5">
              <span>&#x2713;</span>
              Code valide - acces en cours...
            </p>
          )}

          <Button
            type="submit"
            className={`w-full rounded-none ${
              success ? 'bg-green-600 hover:bg-green-700' : ''
            }`}
            disabled={loading || success}
          >
            {success ? 'Acces accorde \u2713' : loading ? 'Verification...' : 'Acceder au site'}
          </Button>
        </form>

        {/* Footer */}
        <div className="text-center space-y-1 border-t border-border pt-4">
          <p className="text-xs text-muted-foreground">
            Tu n&apos;as pas de code ?{' '}
            <Link to="mailto:contact@topkit.app" className="underline underline-offset-2">
              Demande une invitation
            </Link>
          </p>
          <p className="text-xs text-muted-foreground">
            topkit.app &middot; beta privee &middot; {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </div>
  );
}