import React, { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createSession } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthCallback() {
  const hasProcessed = useRef(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash;
    const params = new URLSearchParams(hash.substring(1));
    const sessionId = params.get('session_id');

    if (!sessionId) {
      navigate('/', { replace: true });
      return;
    }

    const processSession = async () => {
      try {
        const res = await createSession(sessionId);
        login(res.data);
        navigate('/browse', { replace: true, state: { user: res.data } });
      } catch (err) {
        console.error('Auth failed:', err);
        navigate('/', { replace: true });
      }
    };
    processSession();
  }, [navigate, login]);

  return null;
}
