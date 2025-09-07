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
        { key: 'level', label: 'Level', type: 'number' },
        { key: 'founded_year', label: 'Founded Year', type: 'number' },
        
        // Enhanced fields
        { key: 'confederations_federations', label: 'Federation/Confederation', type: 'text_list', placeholder: 'Add federations (e.g., UEFA, FIFA)' },
        { key: 'common_names', label: 'Alternative Names', type: 'text_list', placeholder: 'Add alternative competition names' },
        
        // Image fields
        { key: 'logo', label: 'Competition Logo', type: 'image', required: false },
        { key: 'secondary_photos', label: 'Additional Photos', type: 'image_multiple' }
      ];

    case 'master_kit':
      return [
        // Core required fields - Enhanced from existing forms
        { key: 'team_id', label: 'Team', type: 'team_select', required: true },
        { key: 'brand_id', label: 'Brand', type: 'brand_select', required: true },
        { key: 'season', label: 'Season', type: 'text', required: true, placeholder: 'e.g., 2024-25' },
        { key: 'jersey_type', label: 'Kit Type', type: 'select', options: ['Home', 'Away', 'Third', 'Goalkeeper', 'Training'], required: true },
        { key: 'model', label: 'Model', type: 'text', required: true },
        { key: 'primary_color', label: 'Primary Color', type: 'text', required: true },
        
        // Enhanced fields from existing master jersey creation
        { key: 'secondary_colors', label: 'Secondary Colors', type: 'color_list', placeholder: 'Add secondary colors' },
        { key: 'main_sponsor', label: 'Main Sponsor', type: 'text' },
        { key: 'special_edition', label: 'Special Edition', type: 'checkbox' },
        { key: 'design_name', label: 'Design Name', type: 'text' },
        { key: 'pattern', label: 'Pattern Description', type: 'textarea' },
        
        // Image fields
        { key: 'main_image_url', label: 'Kit Photo (Front)', type: 'image', required: true },
        { key: 'secondary_photos', label: 'Additional Photos (Back, Sleeves)', type: 'image_multiple' }
      ];

    case 'reference_kit':
      return [
        // Core required fields - Enhanced from Kit Store creation
        { key: 'master_kit_id', label: 'Master Kit', type: 'master_kit_select', required: true },
        { key: 'model_name', label: 'Model Name', type: 'text', required: true },
        { key: 'release_type', label: 'Release Type', type: 'select', options: ['Replica', 'Authentic', 'Player Issue'], required: true },
        { key: 'original_retail_price', label: 'Original Retail Price (€)', type: 'number' },
        { key: 'release_date', label: 'Release Date', type: 'date' },
        
        // Enhanced fields from existing reference kit creation
        { key: 'sku_code', label: 'SKU Code', type: 'text', placeholder: 'e.g., FN2345-413' },
        { key: 'barcode', label: 'Barcode', type: 'text', placeholder: 'e.g., 1234567890123' },
        { key: 'is_limited_edition', label: 'Limited Edition', type: 'checkbox' },
        { key: 'production_run', label: 'Number of Units (if limited)', type: 'number' },
        { key: 'league_competition', label: 'League/Competition', type: 'competition_select' },
        
        // Image fields
        { key: 'product_images', label: 'Product Photos', type: 'image_multiple', required: true },
        { key: 'main_photo', label: 'Main Photo (Front View)', type: 'image', required: true }
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
  }
};

// Helper function to validate required fields
export const validateEntityData = (entityType, data) => {
  const fields = getUnifiedFieldsForEntityType(entityType);
  const requiredFields = fields.filter(field => field.required);
  
  const errors = [];
  
  for (const field of requiredFields) {
    if (!data[field.key] || (typeof data[field.key] === 'string' && data[field.key].trim() === '')) {
      errors.push(`${field.label} is required`);
    }
  }
  
  return errors;
};

// Helper function to get field configuration by key
export const getFieldConfig = (entityType, fieldKey) => {
  const fields = getUnifiedFieldsForEntityType(entityType);
  return fields.find(field => field.key === fieldKey);
};