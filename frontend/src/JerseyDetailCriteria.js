// Jersey Detail Criteria for Collection Management
export const JERSEY_DETAIL_CRITERIA = {
  model_type: {
    label: "Model Type",
    options: [
      { value: "authentic", label: "Authentic (Stadium version)" },
      { value: "player_issue", label: "Player Issue" },
      { value: "match_worn", label: "Match Worn" },
      { value: "pro", label: "Pro (Professional cut)" },
      { value: "replica", label: "Replica (Fan version)" },
      { value: "retro", label: "Retro/Vintage" }
    ]
  },
  
  condition: {
    label: "Condition",
    options: [
      { value: "mint", label: "Mint - Perfect condition" },
      { value: "near_mint", label: "Near Mint - Excellent with minor flaws" },
      { value: "very_good", label: "Very Good - Good condition with some wear" },
      { value: "good", label: "Good - Acceptable condition with visible wear" },
      { value: "fair", label: "Fair - Poor condition but complete" },
      { value: "poor", label: "Poor - Significant damage or wear" }
    ]
  },
  
  size: {
    label: "Size",
    options: [
      { value: "xs", label: "XS" },
      { value: "s", label: "S" },
      { value: "m", label: "M" },
      { value: "l", label: "L" },
      { value: "xl", label: "XL" },
      { value: "xxl", label: "XXL" },
      { value: "xxxl", label: "XXXL" }
    ]
  },
  
  special_features: {
    label: "Special Features",
    options: [
      { value: "signed", label: "Signed/Autographed" },
      { value: "champions_league", label: "Champions League badges" },
      { value: "europa_league", label: "Europa League badges" },
      { value: "cup_final", label: "Cup Final badges" },
      { value: "league_badges", label: "League winner badges" },
      { value: "memorial", label: "Memorial/Tribute edition" },
      { value: "limited_edition", label: "Limited Edition" },
      { value: "debut", label: "Player debut jersey" },
      { value: "farewell", label: "Player farewell jersey" }
    ]
  },
  
  material_details: {
    label: "Material & Cut",
    options: [
      { value: "climacool", label: "Climacool Technology" },
      { value: "dri_fit", label: "Dri-FIT Technology" },
      { value: "aeroready", label: "AEROREADY" },
      { value: "vapor", label: "Vapor Technology" },
      { value: "recycled", label: "Recycled Materials" },
      { value: "performance", label: "Performance Cut" },
      { value: "slim_fit", label: "Slim Fit" },
      { value: "regular_fit", label: "Regular Fit" }
    ]
  },
  
  tags: {
    label: "Tags (removable)",
    options: [
      { value: "tags_on", label: "Original tags attached" },
      { value: "tags_removed", label: "Tags removed" }
    ]
  },
  
  packaging: {
    label: "Original Packaging",
    options: [
      { value: "original_box", label: "Original box included" },
      { value: "original_bag", label: "Original bag included" },
      { value: "no_packaging", label: "No original packaging" }
    ]
  },
  
  customization: {
    label: "Customization",
    options: [
      { value: "name_number", label: "Player name & number" },
      { value: "number_only", label: "Number only" },
      { value: "name_only", label: "Name only" },
      { value: "blank", label: "Blank (no customization)" },
      { value: "custom_text", label: "Custom text/personalization" }
    ]
  },
  
  competition_badges: {
    label: "Competition Badges",
    options: [
      { value: "ucl", label: "UEFA Champions League" },
      { value: "uel", label: "UEFA Europa League" },
      { value: "uecl", label: "UEFA Conference League" },
      { value: "world_cup", label: "FIFA World Cup" },
      { value: "euros", label: "UEFA European Championship" },
      { value: "copa_america", label: "Copa América" },
      { value: "nations_league", label: "UEFA Nations League" },
      { value: "domestic_cup", label: "Domestic Cup (FA Cup, Copa del Rey, etc.)" }
    ]
  },
  
  rarity: {
    label: "Rarity Level",
    options: [
      { value: "common", label: "Common - Widely available" },
      { value: "uncommon", label: "Uncommon - Somewhat rare" },
      { value: "rare", label: "Rare - Hard to find" },
      { value: "very_rare", label: "Very Rare - Extremely difficult to find" },
      { value: "legendary", label: "Legendary - Museum quality/Historic significance" }
    ]
  },
  
  purchase_details: {
    label: "Purchase Information",
    fields: [
      { key: "purchase_price", label: "Purchase Price (€)", type: "number" },
      { key: "purchase_date", label: "Purchase Date", type: "date" },
      { key: "purchase_location", label: "Purchase Location", type: "text" },
      { key: "certificate_authenticity", label: "Certificate of Authenticity", type: "checkbox" }
    ]
  },
  
  storage_notes: {
    label: "Storage & Care Notes",
    type: "textarea",
    placeholder: "Any specific storage conditions, care instructions, or additional notes about this jersey..."
  }
};

// Price estimation factors based on criteria
export const PRICE_FACTORS = {
  model_type: {
    authentic: 1.0,
    player_issue: 2.5,
    match_worn: 5.0,
    pro: 1.8,
    replica: 0.6,
    retro: 1.5
  },
  
  condition: {
    mint: 1.0,
    near_mint: 0.9,
    very_good: 0.75,
    good: 0.6,
    fair: 0.4,
    poor: 0.2
  },
  
  special_features: {
    signed: 2.0,
    champions_league: 1.4,
    europa_league: 1.2,
    cup_final: 1.6,
    league_badges: 1.3,
    memorial: 1.8,
    limited_edition: 1.5,
    debut: 2.2,
    farewell: 2.5
  },
  
  rarity: {
    common: 1.0,
    uncommon: 1.3,
    rare: 1.8,
    very_rare: 2.8,
    legendary: 5.0
  }
};

// Default base prices by league/competition (in EUR)
export const BASE_PRICES = {
  'Premier League': 80,
  'La Liga': 75,
  'Serie A': 70,
  'Bundesliga': 70,
  'Ligue 1': 65,
  'Champions League': 90,
  'Europa League': 75,
  'World Cup': 100,
  'European Championship': 85,
  'Nation': 70
};