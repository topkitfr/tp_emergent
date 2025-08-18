import React, { useState, useEffect } from 'react';
import axios from 'axios';
import tokenManager from './utils/tokenManager';

const SmartJerseySubmissionForm = ({ isOpen, onClose, onSuccess, csvData = null }) => {
  const [formData, setFormData] = useState({
    team: '',
    league: '',
    season: '24/25',
    jersey_type: 'home',
    player: '',
    manufacturer: '',
    description: ''
  });
  
  const [suggestions, setSuggestions] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

  // Predefined options that remain fixed
  const SEASONS = [
    '25/26', '24/25', '23/24', '22/23', '21/22', '20/21', '19/20', '18/19', '17/18', '16/17'
  ];

  const JERSEY_TYPES = [
    { value: 'home', label: 'Home' },
    { value: 'away', label: 'Away' },
    { value: 'third', label: 'Third' },
    { value: 'goalkeeper', label: 'Goalkeeper' },
    { value: 'special', label: 'Special Edition' }
  ];

  // Smart correction function using CSV data
  const getSmartSuggestions = (field, value) => {
    if (!csvData || !value || value.length < 2) return [];

    const searchValue = value.toLowerCase().trim();
    let matches = [];

    switch (field) {
      case 'team':
        matches = csvData.filter(row => 
          row.team_name?.toLowerCase().includes(searchValue) ||
          row.team_short?.toLowerCase().includes(searchValue) ||
          row.team_alias?.toLowerCase().includes(searchValue)
        ).map(row => ({
          value: row.team_name,
          label: row.team_name,
          league: row.league,
          country: row.country,
          short: row.team_short
        }));
        break;

      case 'league':
        matches = csvData.filter(row => 
          row.league?.toLowerCase().includes(searchValue) ||
          row.league_alias?.toLowerCase().includes(searchValue)
        ).map(row => ({
          value: row.league,
          label: row.league,
          country: row.country
        }));
        break;

      case 'manufacturer':
        matches = csvData.filter(row => 
          row.manufacturer?.toLowerCase().includes(searchValue) ||
          row.manufacturer_alias?.toLowerCase().includes(searchValue)
        ).map(row => ({
          value: row.manufacturer,
          label: row.manufacturer
        }));
        break;

      default:
        return [];
    }

    // Remove duplicates and limit results
    const uniqueMatches = matches.filter((match, index, self) => 
      index === self.findIndex(m => m.value === match.value)
    );

    return uniqueMatches.slice(0, 8);
  };

  // Handle input changes with smart suggestions
  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Generate suggestions for this field
    const fieldSuggestions = getSmartSuggestions(field, value);
    setSuggestions(prev => ({ ...prev, [field]: fieldSuggestions }));

    // Auto-populate related fields when selecting a team
    if (field === 'team' && csvData) {
      const teamData = csvData.find(row => 
        row.team_name?.toLowerCase() === value.toLowerCase()
      );
      
      if (teamData) {
        setFormData(prev => ({
          ...prev,
          league: teamData.league || prev.league,
          manufacturer: teamData.manufacturer || prev.manufacturer
        }));
        
        // Clear suggestions for filled fields
        setSuggestions(prev => ({
          ...prev,
          team: [],
          league: [],
          manufacturer: []
        }));
      }
    }
  };

  // Handle suggestion selection
  const selectSuggestion = (field, suggestion) => {
    setFormData(prev => ({ ...prev, [field]: suggestion.value }));
    
    // Auto-populate related fields
    if (field === 'team' && suggestion.league) {
      setFormData(prev => ({ ...prev, league: suggestion.league }));
    }
    
    // Clear suggestions
    setSuggestions(prev => ({ ...prev, [field]: [] }));
  };

  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.team || !formData.league) {
      setError('Team and League are required fields');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      // Use tokenManager for authenticated request with automatic refresh
      const response = await tokenManager.makeAuthenticatedRequest(
        'post',
        '/api/jerseys',
        formData
      );

      if (onSuccess) {
        onSuccess(response.data);
      }
      
      // Reset form
      setFormData({
        team: '',
        league: '',
        season: '24/25',
        jersey_type: 'home',
        player: '',
        manufacturer: '',
        description: ''
      });
      
      onClose();
      
    } catch (error) {
      console.error('Jersey submission error:', error);
      setError(error.response?.data?.detail || 'Erreur lors de la soumission du maillot');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg max-w-2xl w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">Submit New Jersey Reference</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl font-bold"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="bg-red-600 text-white px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Team Field with Smart Suggestions */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Team Name *
            </label>
            <input
              type="text"
              value={formData.team}
              onChange={(e) => handleInputChange('team', e.target.value)}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="e.g., Real Madrid, Manchester United..."
              required
            />
            
            {/* Team Suggestions */}
            {suggestions.team?.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {suggestions.team.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => selectSuggestion('team', suggestion)}
                    className="w-full text-left p-3 hover:bg-gray-700 text-white border-b border-gray-700 last:border-b-0"
                  >
                    <div className="font-medium">{suggestion.label}</div>
                    <div className="text-sm text-gray-400">
                      {suggestion.league} • {suggestion.country}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* League Field with Smart Suggestions */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              League/Competition *
            </label>
            <input
              type="text"
              value={formData.league}
              onChange={(e) => handleInputChange('league', e.target.value)}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="e.g., Premier League, La Liga..."
              required
            />
            
            {/* League Suggestions */}
            {suggestions.league?.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {suggestions.league.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => selectSuggestion('league', suggestion)}
                    className="w-full text-left p-3 hover:bg-gray-700 text-white border-b border-gray-700 last:border-b-0"
                  >
                    <div className="font-medium">{suggestion.label}</div>
                    <div className="text-sm text-gray-400">{suggestion.country}</div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Season - Predefined Options */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Season *
            </label>
            <select
              value={formData.season}
              onChange={(e) => setFormData(prev => ({ ...prev, season: e.target.value }))}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              required
            >
              {SEASONS.map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </select>
          </div>

          {/* Jersey Type - Predefined Options */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Jersey Type *
            </label>
            <select
              value={formData.jersey_type}
              onChange={(e) => setFormData(prev => ({ ...prev, jersey_type: e.target.value }))}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              required
            >
              {JERSEY_TYPES.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          {/* Player Field - Free Text */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Player Name (Optional)
            </label>
            <input
              type="text"
              value={formData.player}
              onChange={(e) => setFormData(prev => ({ ...prev, player: e.target.value }))}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="e.g., Messi, Ronaldo... (leave blank for team jersey)"
            />
          </div>

          {/* Manufacturer Field with Smart Suggestions */}
          <div className="relative">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Manufacturer
            </label>
            <input
              type="text"
              value={formData.manufacturer}
              onChange={(e) => handleInputChange('manufacturer', e.target.value)}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="e.g., Nike, Adidas, Puma..."
            />
            
            {/* Manufacturer Suggestions */}
            {suggestions.manufacturer?.length > 0 && (
              <div className="absolute z-10 w-full mt-1 bg-gray-800 border border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                {suggestions.manufacturer.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => selectSuggestion('manufacturer', suggestion)}
                    className="w-full text-left p-3 hover:bg-gray-700 text-white border-b border-gray-700 last:border-b-0"
                  >
                    {suggestion.label}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Description Field */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Additional Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full p-3 bg-gray-800 text-white border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 h-24"
              placeholder="Any additional details about this jersey..."
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-700">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg transition-colors"
            >
              {loading ? 'Submitting...' : 'Submit Jersey'}
            </button>
          </div>
        </form>

        {csvData && (
          <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <div className="text-blue-400 text-sm">
              💡 Smart corrections enabled - {csvData.length} teams and leagues loaded for auto-suggestions
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SmartJerseySubmissionForm;