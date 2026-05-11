// frontend/src/components/entity-form/EntityForm.js
//
// Formulaire de saisie d'une entité de référence (team/league/brand/
// sponsor/player). Rendu config-driven depuis ENTITY_FIELD_CONFIGS, pour
// que le même formulaire serve à AddEntityDialog (création) et
// EntityEditDialog (édition).
//
// Props :
// - entityType  : 'team' | 'league' | 'brand' | 'sponsor' | 'player'
// - value       : objet form (state contrôlé par le parent)
// - onChange    : fn(newValue) — patch complet du form
// - onDbSelect  : fn(item) — appelé quand l'user choisit une fiche
//                 existante dans la barre de recherche anti-doublon
// - mode        : 'create' | 'edit' (réservé pour adaptations UI futures)

import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ImageUpload from '@/components/ImageUpload';
import UnifiedEntitySearch from '@/components/UnifiedEntitySearch';
import IndividualAwardsField from '@/components/IndividualAwardsField';
import CareerField from '@/components/CareerField';
import PositionsToggle from './PositionsToggle';
import TeamTypeToggle from './TeamTypeToggle';
import FlagPreview from './FlagPreview';
import { ENTITY_FIELD_CONFIGS } from '@/lib/entityFields';

const fieldStyle = { fontFamily: 'Barlow Condensed' };
const labelClass = 'text-xs uppercase tracking-wider';
const inputClass = 'bg-card border-border rounded-none';

function capitalize(s) {
  if (typeof s !== 'string' || !s.length) return s;
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export default function EntityForm({ entityType, value, onChange, onDbSelect, mode = 'create' }) {
  const config = ENTITY_FIELD_CONFIGS[entityType];
  if (!config) return null;

  const set = (key, val) => onChange({ ...value, [key]: val });

  const renderField = (f) => {
    if (f.type === 'divider') {
      return (
        <div className="col-span-2 flex items-center gap-2 pt-1">
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground whitespace-nowrap" style={fieldStyle}>
            {f.label}
          </p>
          <div className="flex-1 border-t border-border" />
        </div>
      );
    }

    if (f.type === 'flag_preview') {
      if (!value.country_flag) return null;
      return (
        <div className="col-span-2">
          <FlagPreview flagUrl={value.country_flag} code={value.country_code} />
        </div>
      );
    }

    if (f.type === 'team_type') {
      return (
        <TeamTypeToggle
          value={value.is_national}
          onChange={v => set('is_national', v)}
        />
      );
    }

    if (f.type === 'positions') {
      return (
        <PositionsToggle
          value={value.positions}
          onChange={v => set('positions', v)}
        />
      );
    }

    if (f.type === 'career') {
      return (
        <CareerField
          value={value.career || []}
          onChange={v => set('career', v)}
        />
      );
    }

    if (f.type === 'individual_awards') {
      return (
        <IndividualAwardsField
          value={value.individual_awards || []}
          onChange={v => set('individual_awards', v)}
        />
      );
    }

    if (f.type === 'image') {
      return (
        <ImageUpload
          value={value[f.key] || ''}
          onChange={v => set(f.key, v)}
          folder={f.folder || config.folder}
          testId={`entity-form-${f.key}`}
        />
      );
    }

    if (f.type === 'select') {
      return (
        <Select value={value[f.key] || ''} onValueChange={v => set(f.key, v)}>
          <SelectTrigger className={`${inputClass} h-9`} data-testid={`entity-form-${f.key}`}>
            <SelectValue placeholder={f.placeholder || 'Select...'} />
          </SelectTrigger>
          <SelectContent>
            {f.options.map(o => (
              <SelectItem key={o} value={o}>{capitalize(o)}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    }

    if (f.type === 'textarea') {
      return (
        <Textarea
          value={value[f.key] ?? ''}
          onChange={e => set(f.key, e.target.value)}
          placeholder={f.placeholder || ''}
          className={`${inputClass} min-h-[80px] text-sm`}
          data-testid={`entity-form-${f.key}`}
        />
      );
    }

    // Défaut : Input text ou number
    return (
      <Input
        type={f.type === 'number' ? 'number' : 'text'}
        value={value[f.key] ?? ''}
        onChange={e => {
          if (f.type === 'number') {
            const raw = e.target.value;
            set(f.key, raw === '' ? '' : parseInt(raw, 10));
          } else {
            set(f.key, e.target.value);
          }
        }}
        placeholder={f.placeholder || ''}
        className={inputClass}
        data-testid={`entity-form-${f.key}`}
      />
    );
  };

  return (
    <div className="space-y-4">
      {/* Recherche anti-doublon — disponible à la création ET à l'édition
          (utile en edit pour repérer une collision de renommage). */}
      <div className="pb-3 border-b border-border space-y-1">
        <Label className={labelClass} style={fieldStyle}>Recherche rapide</Label>
        <UnifiedEntitySearch
          entityType={entityType}
          onSelectDb={onDbSelect}
          placeholder={config.searchPlaceholder}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {config.fields.map(f => {
          // Pseudo-champs (divider, flag_preview) : pas de wrapper Label
          if (f.type === 'divider' || f.type === 'flag_preview') {
            return <React.Fragment key={f.key}>{renderField(f)}</React.Fragment>;
          }
          return (
            <div
              key={f.key}
              className={`space-y-1.5 ${f.span === 2 ? 'col-span-2' : ''}`}
            >
              <Label className={labelClass} style={fieldStyle}>
                {f.label}{f.required ? ' *' : ''}
              </Label>
              {renderField(f)}
            </div>
          );
        })}
      </div>

      {/* Image principale (crest_url / logo_url / photo_url) — toujours en bas */}
      <div className="space-y-1.5">
        <Label className={labelClass} style={fieldStyle}>{config.imageLabel}</Label>
        <ImageUpload
          value={value[config.imageField] || ''}
          onChange={v => set(config.imageField, v)}
          folder={config.folder}
          testId={`entity-form-${config.imageField}`}
        />
      </div>
    </div>
  );
}
