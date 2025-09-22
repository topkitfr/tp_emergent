// Unified field definitions for all entity types
// This consolidates fields from all creation forms into the Community DB

export const getUnifiedFieldsForEntityType = (type) => {
  switch (type) {
    case 'team':
      return [
        // Core required fields
        { key: 'name', label: 'Team Name', type: 'text', required: true },
        { key: 'short_name', label: 'Short Name', type: 'text' },
        { key: 'country', label: 'Country', type: 'text', required: true },
        { key: 'city', label: 'City', type: 'text' },
        { key: 'founded_year', label: 'Founded Year', type: 'number' },
        
        // Enhanced fields from existing team creation
        { key: 'colors', label: 'Team Colors', type: 'color_list', placeholder: 'Add team colors' },
        { key: 'common_names', label: 'Alternative Names', type: 'text_list', placeholder: 'Add alternative team names' },
        
        // Image fields
        { key: 'logo_url', label: 'Team Logo', type: 'image', required: false },
        { key: 'secondary_photos', label: 'Additional Photos', type: 'image_multiple' }
      ];

    case 'brand':
      return [
        // Core required fields
        { key: 'name', label: 'Brand Name', type: 'text', required: true },
        { key: 'official_name', label: 'Official Name', type: 'text' },
        { key: 'country', label: 'Country of Origin', type: 'text', required: true },
        { key: 'founded_year', label: 'Founded Year', type: 'number' },
        { key: 'website', label: 'Official Website', type: 'url' },
        
        // Enhanced fields from existing brand creation
        { key: 'common_names', label: 'Alternative Names', type: 'text_list', placeholder: 'Add alternative brand names' },
        
        // Image fields
        { key: 'logo_url', label: 'Brand Logo', type: 'image', required: false },
        { key: 'secondary_photos', label: 'Additional Photos', type: 'image_multiple' }
      ];

    case 'player':
      return [
        // Core required fields
        { key: 'name', label: 'Player Name', type: 'text', required: true },
        { key: 'full_name', label: 'Full Name', type: 'text' },
        { key: 'nationality', label: 'Nationality', type: 'text', required: true },
        { key: 'birth_date', label: 'Birth Date', type: 'date' },
        { key: 'position', label: 'Position', type: 'select', options: ['Goalkeeper', 'Defender', 'Midfielder', 'Forward'] },
        
        // Player Type with Coefficient (NEW FIELD)
        { 
          key: 'player_type', 
          label: 'Player Type', 
          type: 'select', 
          required: true,
          options: [
            { value: 'showdown_legend', label: 'Showdown Legend (3.00x)', coefficient: 3.00 },
            { value: 'superstar', label: 'Superstar (2.00x)', coefficient: 2.00 },
            { value: 'star', label: 'Star (1.00x)', coefficient: 1.00 },
            { value: 'good_player', label: 'Good Player (0.5x)', coefficient: 0.50 },
            { value: 'none', label: 'None (0.00x)', coefficient: 0.00 }
          ]
        },
        
        // Enhanced fields
        { key: 'current_team', label: 'Current Team', type: 'text' },
        { key: 'jersey_number', label: 'Jersey Number', type: 'number' },
        { key: 'common_names', label: 'Alternative Names', type: 'text_list', placeholder: 'Add nicknames or alternative names' },
        
        // Image fields
        { key: 'photo_url', label: 'Player Photo', type: 'image', required: false },
        { key: 'secondary_photos', label: 'Additional Photos', type: 'image_multiple' }
      ];

    case 'competition':
      return [
        // Core required fields
        { key: 'competition_name', label: 'Competition Name', type: 'text', required: true },
        { key: 'official_name', label: 'Official Name', type: 'text' },
        { key: 'type', label: 'Competition Type', type: 'select', options: ['National league', 'Continental competition', 'National cup', 'International competition', 'Intercontinental competition', 'Continental super cup'], required: true },
        { key: 'country', label: 'Country', type: 'text', required: true },
        { key: 'level', label: 'Level', type: 'select', options: ['pro', 'semi pro', 'amateur', 'special'] },
        { key: 'founded_year', label: 'Founded Year', type: 'number' },
        
        // Enhanced fields
        { key: 'confederations_federations', label: 'Federation/Confederation', type: 'text_list', placeholder: 'Add federations (e.g., UEFA, FIFA)' },
        { key: 'common_names', label: 'Alternative Names', type: 'text_list', placeholder: 'Add alternative competition names' },
        
        // Image fields
        { key: 'logo_url', label: 'Competition Logo', type: 'image', required: false },
        { key: 'secondary_photos', label: 'Additional Photos', type: 'image_multiple' }
      ];

    case 'master_kit':
    case 'master_jersey':
      return [
        // Master Kit form fields for contribution improvements
        { key: 'club_id', label: 'Team', type: 'team_select', required: false },
        { key: 'season', label: 'Season', type: 'text', required: false, placeholder: '2024-2025' },
        { key: 'brand_id', label: 'Brand', type: 'brand_select', required: false },
        { key: 'kit_type', label: 'Kit Type', type: 'select', options: ['home', 'away', 'third', 'fourth', 'gk', 'special'], required: false },
        { key: 'main_sponsor_id', label: 'Main Sponsor', type: 'brand_select', required: false },
        { key: 'model', label: 'Model', type: 'select', options: ['replica', 'authentic', 'player_issue'], required: false },
        { key: 'sku_code', label: 'SKU Code', type: 'text', required: false },
        { key: 'primary_color', label: 'Primary Color', type: 'text', required: false },
        { key: 'pattern_description', label: 'Pattern Description', type: 'textarea', required: false },
        { key: 'front_photo_url', label: 'Front Photo', type: 'image', required: false }
      ];

    case 'reference_kit':
      return [
        // B/ Reference Kit form as specified
        { key: 'master_kit_id', label: 'Master Kit', type: 'master_kit_select', required: true },
        { key: 'league_competition', label: 'League/Competition', type: 'competition_select', required: true },
        { key: 'model', label: 'Model', type: 'select', options: ['replica', 'authentic'], required: true },
        { key: 'long_sleeve', label: 'Long Sleeve', type: 'checkbox' },
        { key: 'limited', label: 'Limited', type: 'checkbox', reveals: 'limited_units' },
        { key: 'limited_units', label: 'Number of Units', type: 'number', dependsOn: 'limited' },
        { key: 'pic_1', label: 'Pic 1 (front/back)', type: 'image', required: true },
        { key: 'pic_2', label: 'Pic 2 (sleeve/tags/other)', type: 'image' },
        { key: 'description', label: 'Description', type: 'textarea' }
      ];

    case 'personal_kit':
      return [
        // C/ Personal Kit form - additional info when adding Reference Kit to collection
        { key: 'condition', label: 'Condition (state of the kit)', type: 'select', options: ['New', 'Excellent', 'Good', 'Fair', 'Poor'], required: false },
        { key: 'player_id', label: 'Player', type: 'player_select', required: false },
        { key: 'number', label: 'Number (player\'s jersey number)', type: 'number', required: false },
        { key: 'purchase_price', label: 'Purchase Price', type: 'number', required: false },
        { key: 'estimated_value', label: 'Estimated Value', type: 'number', required: false }
      ];

    default:
      return [];
  }
};

// Field type renderers configuration
export const fieldTypeConfig = {
  text: {
    component: 'input',
    inputType: 'text'
  },
  number: {
    component: 'input',
    inputType: 'number'
  },
  date: {
    component: 'input',
    inputType: 'date'
  },
  url: {
    component: 'input',
    inputType: 'url'
  },
  textarea: {
    component: 'textarea'
  },
  select: {
    component: 'select'
  },
  checkbox: {
    component: 'checkbox'
  },
  image: {
    component: 'file',
    accept: 'image/*',
    multiple: false
  },
  image_multiple: {
    component: 'file',
    accept: 'image/*',
    multiple: true
  },
  color_list: {
    component: 'color_list'
  },
  text_list: {
    component: 'text_list'
  },
  team_select: {
    component: 'team_select'
  },
  brand_select: {
    component: 'brand_select'
  },
  competition_select: {
    component: 'competition_select'
  },
  master_kit_select: {
    component: 'master_kit_select'
  },
  season_select: {
    component: 'season_select'
  },
  reference_kit_select: {
    component: 'reference_kit_select'
  }
};

// Helper function to validate required fields
export const validateEntityData = (entityType, data) => {
  const fields = getUnifiedFieldsForEntityType(entityType);
  const requiredFields = fields.filter(field => field.required);
  
  const errors = [];
  
  for (const field of requiredFields) {
    const value = data[field.key];
    
    // Handle image fields differently - they can have placeholder values or be handled separately
    if (field.type === 'image' || field.type === 'image_multiple') {
      // For image fields, just check if there's any value (including placeholder values)
      if (!value) {
        errors.push(`${field.label} is required`);
      }
    } else {
      // Regular validation for non-image fields
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        errors.push(`${field.label} is required`);
      }
    }
  }
  
  return errors;
};

// Helper function to get field configuration by key
export const getFieldConfig = (entityType, fieldKey) => {
  const fields = getUnifiedFieldsForEntityType(entityType);
  return fields.find(field => field.key === fieldKey);
};