// frontend/src/components/entity-form/FlagPreview.js
// Mini-preview drapeau + code pays, affiché en lecture seule quand un
// préremplissage DB a renseigné `country_flag` sur une league.
import React from 'react';

const fieldStyle = { fontFamily: 'Barlow Condensed' };

export default function FlagPreview({ flagUrl, code }) {
  if (!flagUrl) return null;
  return (
    <div className="flex items-center gap-2">
      <img src={flagUrl} alt="flag" className="h-4 w-auto rounded-sm border border-border" />
      <span className="text-xs text-muted-foreground" style={fieldStyle}>
        {code || ''}
      </span>
    </div>
  );
}
