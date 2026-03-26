import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { loginUser, registerUser } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      let res;
      if (mode === 'login') {
        res = await loginUser(form.email, form.password);
      } else {
        res = await registerUser(form.email, form.password, form.name);
      }
      login(res.data);
      navigate('/browse');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
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

        <div className="flex mb-6 border border-border">
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              mode === 'login' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => { setMode('login'); setError(''); }}
          >
            Sign in
          </button>
          <button
            className={`flex-1 py-2 text-sm font-medium transition-colors ${
              mode === 'register' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
            onClick={() => { setMode('register'); setError(''); }}
          >
            Create account
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <Input
              type="text"
              placeholder="Your name"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="rounded-none"
              required
            />
          )}
          <Input
            type="email"
            placeholder="Email address"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
            className="rounded-none"
            required
          />
          <div className="space-y-1">
            <Input
              type="password"
              placeholder="Password (8 chars min)"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="rounded-none"
              required
              minLength={8}
            />
            {mode === 'login' && (
              <div className="text-right">
                <Link
                  to="/forgot-password"
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Mot de passe oublié ?
                </Link>
              </div>
            )}
          </div>

          {error && <p className="text-sm text-red-500">{error}</p>}

          <Button
            type="submit"
            className="w-full rounded-none bg-primary text-primary-foreground hover:bg-primary/90"
            disabled={loading}
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          <Link to="/" className="hover:text-foreground transition-colors">← Back to home</Link>
        </p>
      </div>
    </div>
  );
}
