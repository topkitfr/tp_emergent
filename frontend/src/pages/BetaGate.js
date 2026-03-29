import React, { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

// Codes d'accès beta valides — à modifier selon tes besoins
const VALID_CODES = [
  'TOPKIT2025',
  'BETA-KIT',
  'TK-TESTER',
  'TOPKIT-BETA',
  'KITBETA01',
];

export default function BetaGate({ onAccess }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [shake, setShake] = useState(false);
  const inputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (loading || success) return;
    setError('');
    setLoading(true);

    setTimeout(() => {
      const trimmed = code.trim().toUpperCase();
      if (VALID_CODES.includes(trimmed)) {
        setSuccess(true);
        setTimeout(() => onAccess(), 900);
      } else {
        setError('Code invalide. Vérifie ton invitation.');
        setShake(true);
        setTimeout(() => {
          setShake(false);
          inputRef.current?.focus();
          inputRef.current?.select();
        }, 600);
      }
      setLoading(false);
    }, 500);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="mb-10 text-center">
          <Link to="/">
            <img
              src="/topkit-logo.png"
              alt="Topkit"
              className="h-8 object-contain mx-auto"
            />
          </Link>
        </div>

        {/* Badge beta */}
        <div className="flex items-center gap-2 mb-5">
          <span className="inline-flex items-center gap-1.5 text-xs font-medium tracking-wider uppercase px-2 py-1 border border-border text-muted-foreground">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block animate-pulse" />
            Bêta privée
          </span>
        </div>

        {/* Header */}
        <div className="mb-6">
          <h1 className="text-lg font-semibold text-foreground leading-snug">
            Accès sur invitation
          </h1>
          <p className="text-sm text-muted-foreground mt-1.5 leading-relaxed">
            Topkit est en période de test fermé. Entre ton code d'invitation pour accéder à la plateforme.
          </p>
        </div>

        {/* Divider */}
        <div className="border-t border-border mb-6" />

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className={`space-y-4 transition-all ${shake ? 'animate-shake' : ''}`}
        >
          <div className="space-y-1.5">
            <label
              htmlFor="beta-code"
              className="text-xs text-muted-foreground uppercase tracking-wider"
            >
              Code d'accès
            </label>
            <Input
              ref={inputRef}
              id="beta-code"
              type="text"
              placeholder="ex : TOPKIT2025"
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
              }`}
              autoFocus
              autoComplete="off"
              spellCheck={false}
              required
              disabled={success}
            />
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-red-500 mt-0.5 shrink-0">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <p className="text-sm text-red-500">{error}</p>
            </div>
          )}

          {/* Success */}
          {success && (
            <div className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-green-500 shrink-0">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              <p className="text-sm text-green-600 font-medium">Code valide — accès en cours...</p>
            </div>
          )}

          <Button
            type="submit"
            className={`w-full rounded-none transition-all ${
              success
                ? 'bg-green-600 hover:bg-green-600 text-white cursor-default'
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
            }`}
            disabled={loading || !code.trim() || success}
          >
            {success
              ? 'Accès accordé ✓'
              : loading
              ? 'Vérification...'
              : 'Accéder au site'}
          </Button>
        </form>

        {/* Footer */}
        <div className="mt-8 space-y-3 text-center">
          <p className="text-xs text-muted-foreground">
            Tu n'as pas de code ?{' '}
            <a
              href="mailto:contact@topkit.app"
              className="hover:text-foreground transition-colors underline underline-offset-2"
            >
              Demande une invitation
            </a>
          </p>
          <p className="text-xs text-muted-foreground/60">
            topkit.app · bêta privée · {new Date().getFullYear()}
          </p>
        </div>

      </div>
    </div>
  );
}
