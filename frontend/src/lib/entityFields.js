// frontend/src/lib/entityFields.js
// Constantes partagées par AddEntityDialog, EntityEditDialog et leur futur
// composant commun EntityForm. Single source of truth pour les options de
// dropdown / toggle utilisés à la saisie d'une entité (team/league/brand/
// sponsor/player).

export const POSITIONS = [
  'GK', 'CB', 'LB', 'RB', 'LWB', 'RWB',
  'CDM', 'CM', 'CAM', 'LM', 'RM',
  'LW', 'RW', 'SS', 'CF', 'ST',
];

export const FOOT_OPTIONS = ['right', 'left', 'both'];

export const GENDER_OPTIONS = ['male', 'female'];

export const SURFACE_OPTIONS = ['Grass', 'Artificial Turf', 'Hybrid'];

export const LEAGUE_LEVELS = ['domestic', 'continental', 'international', 'cup'];

export const LEAGUE_TYPE_OPTIONS = ['League', 'Cup'];

export const LEAGUE_ENTITY_TYPE_OPTIONS = ['league', 'cup', 'confederation'];

export const LEAGUE_SCOPE_OPTIONS = ['domestic', 'international'];

// Champs image gérés au niveau soumission — utilisés pour éviter de renvoyer
// l'URL existante en mode 'edit' quand l'user n'a rien re-uploadé.
export const IMAGE_FIELDS = new Set([
  'crest_url',
  'logo_url',
  'photo_url',
  'stadium_image_url',
]);
