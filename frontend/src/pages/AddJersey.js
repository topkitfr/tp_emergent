// AddJersey.js — redirected to /contributions
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function AddJersey() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const kitId = searchParams.get('kit_id');

  useEffect(() => {
    navigate(kitId ? `/contributions?kit_id=${kitId}` : '/contributions', { replace: true });
  }, [navigate, kitId]);

  return null;
}
