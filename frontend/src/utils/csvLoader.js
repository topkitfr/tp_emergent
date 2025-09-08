// CSV Loader Utility for Smart Jersey Submission
export class CSVLoader {
  constructor() {
    this.data = null;
    this.isLoaded = false;
  }

  // Parse CSV text into array of objects
  parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const values = this.parseCSVLine(lines[i]);
      if (values.length === headers.length) {
        const row = {};
        headers.forEach((header, index) => {
          row[header] = values[index] ? values[index].trim() : '';
        });
        data.push(row);
      }
    }

    return data;
  }

  // Parse a single CSV line handling quoted fields
  parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    
    result.push(current); // Add the last field
    return result;
  }

  // Load CSV from URL
  async loadFromURL(url) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const csvText = await response.text();
      this.data = this.parseCSV(csvText);
      this.isLoaded = true;
      return this.data;
    } catch (error) {
      console.error('Failed to load CSV from URL:', error);
      throw error;
    }
  }

  // Load CSV from file input
  async loadFromFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const csvText = e.target.result;
          this.data = this.parseCSV(csvText);
          this.isLoaded = true;
          resolve(this.data);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }

  // Get all unique teams
  getTeams() {
    if (!this.data) return [];
    return [...new Set(this.data.map(row => row.team_name).filter(Boolean))];
  }

  // Get all unique leagues
  getLeagues() {
    if (!this.data) return [];
    return [...new Set(this.data.map(row => row.league).filter(Boolean))];
  }

  // Get all unique manufacturers
  getManufacturers() {
    if (!this.data) return [];
    return [...new Set(this.data.map(row => row.manufacturer).filter(Boolean))];
  }

  // Search teams by query
  searchTeams(query) {
    if (!this.data || !query) return [];
    
    const searchTerm = query.toLowerCase();
    return this.data.filter(row => 
      row.team_name?.toLowerCase().includes(searchTerm) ||
      row.team_short?.toLowerCase().includes(searchTerm) ||
      row.team_alias?.toLowerCase().includes(searchTerm)
    );
  }

  // Search leagues by query
  searchLeagues(query) {
    if (!this.data || !query) return [];
    
    const searchTerm = query.toLowerCase();
    return this.data.filter(row => 
      row.league?.toLowerCase().includes(searchTerm) ||
      row.league_alias?.toLowerCase().includes(searchTerm)
    );
  }

  // Get team data by exact name
  getTeamData(teamName) {
    if (!this.data) return null;
    return this.data.find(row => 
      row.team_name?.toLowerCase() === teamName.toLowerCase()
    );
  }

  // Validate and correct team name
  correctTeamName(input) {
    if (!this.data || !input) return input;
    
    const searchTerm = input.toLowerCase();
    
    // Try exact match first
    let match = this.data.find(row => 
      row.team_name?.toLowerCase() === searchTerm
    );
    
    if (match) return match.team_name;
    
    // Try alias match
    match = this.data.find(row => 
      row.team_alias?.toLowerCase().includes(searchTerm) ||
      row.team_short?.toLowerCase() === searchTerm
    );
    
    if (match) return match.team_name;
    
    // Return original if no match
    return input;
  }

  // Get data summary
  getSummary() {
    if (!this.data) return null;
    
    return {
      totalRows: this.data.length,
      uniqueTeams: this.getTeams().length,
      uniqueLeagues: this.getLeagues().length,
      uniqueManufacturers: this.getManufacturers().length,
      countries: [...new Set(this.data.map(row => row.country).filter(Boolean))].length
    };
  }
}

// Singleton instance
export const csvLoader = new CSVLoader();

// Hook for React components
export const useCSVData = () => {
  return {
    csvData: csvLoader.data,
    data: csvLoader.data,
    loading: false, // Static for now since we're not implementing async loading
    error: null,    // Static for now since we're not implementing error handling
    isLoaded: csvLoader.isLoaded,
    loadFromURL: csvLoader.loadFromURL.bind(csvLoader),
    loadFromFile: csvLoader.loadFromFile.bind(csvLoader),
    searchTeams: csvLoader.searchTeams.bind(csvLoader),
    searchLeagues: csvLoader.searchLeagues.bind(csvLoader),
    getTeamData: csvLoader.getTeamData.bind(csvLoader),
    correctTeamName: csvLoader.correctTeamName.bind(csvLoader),
    getSummary: csvLoader.getSummary.bind(csvLoader)
  };
};