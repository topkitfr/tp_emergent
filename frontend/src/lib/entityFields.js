// frontend/src/lib/entityFields.js
// Constantes + config par type d'entité partagées par AddEntityDialog,
// EntityEditDialog et EntityForm. Single source of truth pour les champs
// présentés à la saisie d'une entité (team/league/brand/sponsor/player).

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

// ─── Config par type d'entité ────────────────────────────────────────────────
//
// Chaque entité expose :
// - label, nameField, imageField, imageLabel, folder, searchPlaceholder
// - fields[] : la liste ordonnée des champs du formulaire
//
// Pour chaque field :
// - key       : nom du champ dans le state (et dans le payload)
// - label     : label affiché
// - type      : 'text' (défaut) | 'number' | 'select' | 'textarea' | 'image'
//               | 'positions' | 'team_type' | 'career' | 'individual_awards'
//               | 'divider' | 'flag_preview'
// - options   : pour 'select', liste des valeurs
// - required  : marque le champ obligatoire (étoile à l'affichage)
// - span      : 2 = pleine largeur de la grille (par défaut 1)
// - placeholder : optionnel
// - folder    : pour 'image', dossier de stockage (sinon hérite de config.folder)
//
// Champs commençant par `_` = pseudo-champs UI (divider, preview) sans
// valeur métier — nettoyés du payload par buildEntityPayload().

export const ENTITY_FIELD_CONFIGS = {
  team: {
    label: 'Team',
    nameField: 'name',
    imageField: 'crest_url',
    imageLabel: 'Crest / Badge',
    folder: 'team',
    searchPlaceholder: 'Nom du club...',
    fields: [
      { key: 'name',              label: 'Team Name',       placeholder: 'FC Barcelona', required: true, span: 2 },
      { key: 'country',           label: 'Country',         placeholder: 'Spain' },
      { key: 'city',              label: 'City',            placeholder: 'Barcelona' },
      { key: 'founded',           label: 'Founded (year)',  placeholder: '1899', type: 'number' },
      { key: 'gender',            label: 'Genre',           type: 'select', options: GENDER_OPTIONS, placeholder: 'Genre' },
      { key: 'is_national',       label: 'Type',            type: 'team_type', span: 2 },
      { key: '_stadium_divider',  label: 'Stadium',         type: 'divider', span: 2 },
      { key: 'stadium_name',      label: 'Stadium Name',    placeholder: 'Camp Nou', span: 2 },
      { key: 'stadium_capacity',  label: 'Capacity',        placeholder: '99354', type: 'number' },
      { key: 'stadium_surface',   label: 'Surface',         type: 'select', options: SURFACE_OPTIONS, placeholder: 'Surface' },
      { key: 'stadium_city',      label: 'Ville du stade',  placeholder: 'Barcelona' },
      { key: 'stadium_country',   label: 'Pays du stade',   placeholder: 'Spain' },
      { key: 'stadium_image_url', label: 'Stadium Image',   type: 'image', folder: 'team', span: 2 },
    ],
  },
  league: {
    label: 'League',
    nameField: 'name',
    imageField: 'logo_url',
    imageLabel: 'Logo',
    folder: 'league',
    searchPlaceholder: 'Nom de la compétition...',
    fields: [
      { key: 'name',              label: 'League Name',      placeholder: 'Premier League', required: true, span: 2 },
      { key: 'country_or_region', label: 'Country / Region', placeholder: 'England' },
      { key: 'country_code',      label: 'Country Code',     placeholder: 'GB' },
      { key: 'type',              label: 'Type',             type: 'select', options: LEAGUE_TYPE_OPTIONS, placeholder: 'League / Cup' },
      { key: 'entity_type',       label: 'Entity Type',      type: 'select', options: LEAGUE_ENTITY_TYPE_OPTIONS, placeholder: 'league / cup / confederation' },
      { key: 'scope',             label: 'Scope',            type: 'select', options: LEAGUE_SCOPE_OPTIONS, placeholder: 'domestic / international' },
      { key: 'level',             label: 'Level',            type: 'select', options: LEAGUE_LEVELS, placeholder: 'Select level' },
      { key: 'gender',            label: 'Genre',            type: 'select', options: GENDER_OPTIONS, placeholder: 'Genre' },
      { key: 'organizer',         label: 'Organizer',        placeholder: 'UEFA' },
      { key: '_flag_preview',     label: '', type: 'flag_preview', span: 2 },
    ],
  },
  brand: {
    label: 'Brand',
    nameField: 'name',
    imageField: 'logo_url',
    imageLabel: 'Logo',
    folder: 'brand',
    searchPlaceholder: 'Nom de la marque...',
    fields: [
      { key: 'name',    label: 'Brand Name',     placeholder: 'Adidas',  required: true, span: 2 },
      { key: 'country', label: 'Country',        placeholder: 'Germany' },
      { key: 'founded', label: 'Founded (year)', placeholder: '1949', type: 'number' },
    ],
  },
  sponsor: {
    label: 'Sponsor',
    nameField: 'name',
    imageField: 'logo_url',
    imageLabel: 'Logo',
    folder: 'sponsor',
    searchPlaceholder: 'Nom du sponsor...',
    fields: [
      { key: 'name',    label: 'Sponsor Name', placeholder: 'Emirates',  required: true, span: 2 },
      { key: 'country', label: 'Country',      placeholder: 'UAE' },
      { key: 'website', label: 'Website',      placeholder: 'https://...' },
    ],
  },
  player: {
    label: 'Player',
    nameField: 'full_name',
    imageField: 'photo_url',
    imageLabel: 'Photo',
    folder: 'player',
    searchPlaceholder: 'Nom du joueur...',
    fields: [
      { key: 'full_name',        label: 'Full Name',                  placeholder: 'Zinédine Zidane', required: true, span: 2 },
      { key: 'first_name',       label: 'Prénom',                     placeholder: 'Zinédine' },
      { key: 'last_name',        label: 'Nom de famille',             placeholder: 'Zidane' },
      { key: 'nationality',      label: 'Nationality',                placeholder: 'French' },
      { key: 'birth_date',       label: 'Date of Birth (DD/MM/YYYY)', placeholder: '23/06/1972' },
      { key: 'birth_place',      label: 'Lieu de naissance',          placeholder: 'Marseille' },
      { key: 'birth_country',    label: 'Pays de naissance',          placeholder: 'France' },
      { key: 'height',           label: 'Height (cm)',                placeholder: '185', type: 'number' },
      { key: 'weight',           label: 'Weight (kg)',                placeholder: '80',  type: 'number' },
      { key: 'preferred_foot',   label: 'Preferred Foot',             type: 'select', options: FOOT_OPTIONS, placeholder: 'Pied' },
      { key: 'preferred_number', label: 'Preferred Number',           placeholder: '10', type: 'number' },
      { key: 'positions',        label: 'Positions',                  type: 'positions',         span: 2 },
      { key: '_career_divider',  label: 'Carrière & Transferts',      type: 'divider',           span: 2 },
      { key: 'career',           label: 'Carrière',                   type: 'career',            span: 2 },
      { key: 'individual_awards',label: 'Distinctions individuelles', type: 'individual_awards', span: 2 },
      { key: 'bio',              label: 'Bio',                        type: 'textarea',          span: 2, placeholder: 'Brief biography...' },
    ],
  },
};

// ─── Helpers payload ─────────────────────────────────────────────────────────

const PSEUDO_FIELD_PREFIX = '_';

/**
 * Construit le payload à envoyer au backend depuis le state form.
 *
 * Normalisations :
 * - Player : height/weight → Optional[str] (PlayerCreate côté backend
 *   attend des strings), preferred_number → int|null, et alias
 *   first_name/last_name → firstname/lastname (champs Pydantic).
 * - Tous types : suppression des pseudo-champs UI (`_stadium_divider`,
 *   `_flag_preview`, `_career_divider`).
 * - Mode 'edit' : on omet les champs image qui n'ont pas changé, pour ne
 *   pas réécrire l'URL existante avec elle-même (et déclencher la
 *   suppression du fichier orphelin côté Freebox).
 */
export function buildEntityPayload(entityType, form, initialData = {}, mode = 'create') {
  const payload = { ...form };

  // Nettoyer les pseudo-champs UI
  for (const k of Object.keys(payload)) {
    if (k.startsWith(PSEUDO_FIELD_PREFIX)) delete payload[k];
  }

  if (entityType === 'player') {
    payload.firstname = form.first_name || form.firstname || '';
    payload.lastname  = form.last_name  || form.lastname  || '';
    delete payload.first_name;
    delete payload.last_name;
    payload.height = (form.height != null && form.height !== '')
      ? String(form.height)
      : null;
    payload.weight = (form.weight != null && form.weight !== '')
      ? String(form.weight)
      : null;
    payload.preferred_number = (form.preferred_number != null && form.preferred_number !== '')
      ? parseInt(form.preferred_number, 10)
      : null;
  }

  if (mode === 'edit') {
    for (const imgField of IMAGE_FIELDS) {
      if (imgField in payload && payload[imgField] === (initialData[imgField] || '')) {
        delete payload[imgField];
      }
    }
  }

  return payload;
}
