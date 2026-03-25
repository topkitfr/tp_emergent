// frontend/src/components/Pagination.js
import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * Pagination — composant réutilisable
 * Props:
 *   page      : numéro de page actuel (1-based)
 *   total     : nombre total d'items
 *   pageSize  : items par page
 *   onChange  : (newPage) => void
 */
export default function Pagination({ page, total, pageSize, onChange }) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const pages = [];
  const delta = 2;
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - delta && i <= page + delta)) {
      pages.push(i);
    }
  }

  // Inject ellipsis markers
  const items = [];
  let prev = null;
  for (const p of pages) {
    if (prev !== null && p - prev > 1) items.push('...');
    items.push(p);
    prev = p;
  }

  return (
    <div className="flex items-center justify-center gap-1 pt-6">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="rounded-none px-2"
      >
        <ChevronLeft className="w-4 h-4" />
      </Button>

      {items.map((item, idx) =>
        item === '...' ? (
          <span key={`ellipsis-${idx}`} className="px-2 text-muted-foreground text-sm">…</span>
        ) : (
          <Button
            key={item}
            variant={item === page ? 'default' : 'outline'}
            size="sm"
            onClick={() => onChange(item)}
            className="rounded-none w-8 h-8 p-0 text-xs"
          >
            {item}
          </Button>
        )
      )}

      <Button
        variant="outline"
        size="sm"
        onClick={() => onChange(page + 1)}
        disabled={page >= totalPages}
        className="rounded-none px-2"
      >
        <ChevronRight className="w-4 h-4" />
      </Button>
    </div>
  );
}
