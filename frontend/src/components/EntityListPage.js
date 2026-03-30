// frontend/src/components/EntityListPage.js
import React from 'react';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Plus } from 'lucide-react';
import { proxyImageUrl } from '@/lib/api';

export default function EntityListPage({
  title,
  icon: Icon,
  entities = [],
  loading = false,
  search = '',
  onSearchChange,
  filters = [],
  renderCard,
  emptyMessage = 'No results found',
  totalLabel = 'items',
  testId,
  onAddNew,
  footer,
  gridClassName, // ← nouvelle prop
}) {
  return (
    <div className="animate-fade-in-up" data-testid={testId}>
      {/* ── Header ── */}
      <div className="border-b border-border px-4 lg:px-8 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between gap-3 mb-5">
            <div className="flex items-center gap-3">
              {Icon && <Icon className="w-7 h-7 text-primary" />}
              <h1 className="text-3xl sm:text-4xl tracking-tighter">{title}</h1>
            </div>
            {onAddNew && (
              <button
                onClick={onAddNew}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-border bg-card hover:border-primary/60 hover:bg-primary/5 text-xs tracking-wider transition-colors"
                style={{ fontFamily: 'Barlow Condensed' }}
                data-testid={`${testId}-add-btn`}
              >
                <Plus className="w-3.5 h-3.5" />
                ADD NEW
              </button>
            )}
          </div>

          {/* Barre de recherche + filtres */}
          <div className="flex flex-col sm:flex-row gap-3 flex-wrap">
            <div className="relative flex-1 min-w-[200px] max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
              <Input
                placeholder={`Search ${totalLabel}...`}
                value={search}
                onChange={e => onSearchChange(e.target.value)}
                className="pl-9 bg-card border-border rounded-none h-10"
                data-testid={`${testId}-search`}
              />
            </div>

            {filters.map(filter => (
              <select
                key={filter.key}
                value={filter.value}
                onChange={e => filter.onChange(e.target.value)}
                className="h-10 px-3 bg-card border border-border rounded-none text-sm text-foreground min-w-[140px]"
                data-testid={`${testId}-filter-${filter.key}`}
              >
                <option value="">{filter.label}</option>
                {filter.options.map(opt => {
                  const val = typeof opt === 'string' ? opt : opt.value;
                  const lbl = typeof opt === 'string' ? opt : opt.label;
                  return <option key={val} value={val}>{lbl}</option>;
                })}
              </select>
            ))}
          </div>
        </div>
      </div>

      {/* ── Contenu ── */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
        {/* Compteur */}
        <p className="text-sm text-muted-foreground mb-6" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
          <span className="font-mono text-foreground">{entities.length}</span> {totalLabel}
        </p>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-20 bg-card animate-pulse border border-border" />
            ))}
          </div>
        ) : entities.length === 0 ? (
          <div className="text-center py-24">
            {Icon && <Icon className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />}
            <h3 className="text-xl tracking-tight mb-2">NO {title} FOUND</h3>
            <p className="text-sm text-muted-foreground" style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              {emptyMessage}
            </p>
          </div>
        ) : (
          <div
            className={
              gridClassName ||
              "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-children"
            }
            data-testid={`${testId}-grid`}
          >
            {entities.map(renderCard)}
          </div>
        )}

        {/* ── Footer (ex: Pagination) ── */}
        {footer && <div className="mt-6">{footer}</div>}
      </div>
    </div>
  );
}

/**
 * EntityCard — carte standardisée pour toutes les entités.
 */
export function EntityCard({ to, image, icon: CardIcon, name, meta = [], badges = [], testId }) {
  return (
    <Link to={to} data-testid={testId}>
      <div className="border border-border bg-card p-4 hover:border-primary/50 group flex items-center gap-4 transition-colors duration-200 cursor-pointer h-full">
        <div className="w-12 h-12 bg-secondary flex items-center justify-center shrink-0 overflow-hidden rounded-sm">
          {image
            ? <img src={proxyImageUrl(image)} alt={name} className="w-12 h-12 object-contain p-1" />
            : CardIcon && <CardIcon className="w-5 h-5 text-muted-foreground" />
          }
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold tracking-tight truncate group-hover:text-primary transition-colors duration-200">
            {name}
          </h3>
          {meta.map((m, i) => m && (
            <p key={i} className="text-xs text-muted-foreground truncate mt-0.5 flex items-center gap-1"
              style={{ fontFamily: 'DM Sans', textTransform: 'none' }}>
              {m.icon && <m.icon className="w-3 h-3 shrink-0" />}
              {m.text}
            </p>
          ))}
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {badges.map((b, i) => (
                <Badge key={i} variant={b.variant || 'secondary'} className="rounded-none text-[10px] px-1.5 py-0">
                  {b.label}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}