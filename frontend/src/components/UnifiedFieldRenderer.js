import React, { useState, useEffect } from 'react';
import { fieldTypeConfig } from './UnifiedFieldDefinitions';

const UnifiedFieldRenderer = ({ 
  field, 
  value, 
  onChange, 
  teams = [], 
  brands = [], 
  competitions = [], 
  masterKits = [],
  referenceKits = [],
  players = [],
  onImageUpload,
  API,
  formData = {} // Add formData to check field dependencies
}) => {
  const [listItems, setListItems] = useState(Array.isArray(value) ? value : []);
  const [newItem, setNewItem] = useState('');

  // Update listItems when value changes externally
  useEffect(() => {
    if (field.type === 'color_list' || field.type === 'text_list') {
      setListItems(Array.isArray(value) ? value : []);
    }
  }, [value, field.type]);

  // Check if field should be rendered based on dependencies
  const shouldRenderField = () => {
    if (field.dependsOn) {
      const dependsOnValue = formData[field.dependsOn];
      return !!dependsOnValue; // Only render if the field it depends on is truthy
    }
    return true; // Render by default
  };

  // Don't render field if it shouldn't be shown
  if (!shouldRenderField()) {
    return null;
  }

  const handleListAdd = () => {
    if (newItem.trim() && !listItems.includes(newItem.trim())) {
      const updatedList = [...listItems, newItem.trim()];
      setListItems(updatedList);
      onChange(field.key, updatedList);
      setNewItem('');
    }
  };

  const handleListRemove = (itemToRemove) => {
    const updatedList = listItems.filter(item => item !== itemToRemove);
    setListItems(updatedList);
    onChange(field.key, updatedList);
  };

  const handleImageChange = async (event) => {
    if (!event.target || !event.target.files) {
      console.error('No files in event target');
      return;
    }
    
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    if (onImageUpload) {
      // Call onImageUpload with the event and field key as expected by DynamicContributionForm
      await onImageUpload(event, field.key);
    } else {
      // Fallback to base64 conversion for preview
      const file = files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        onChange(field.key, e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const renderField = () => {
    switch (field.type) {
      case 'text':
      case 'number':
      case 'date':
      case 'url':
        return (
          <input
            type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : field.type === 'url' ? 'url' : 'text'}
            value={value || ''}
            onChange={(e) => onChange(field.key, field.type === 'number' ? (e.target.value ? parseInt(e.target.value) : '') : e.target.value)}
            placeholder={field.placeholder || ''}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          />
        );

      case 'textarea':
        return (
          <textarea
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            placeholder={field.placeholder || ''}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          />
        );

      case 'team_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Team</option>
            {teams.map(team => (
              <option key={team.id} value={team.id}>{team.name}</option>
            ))}
          </select>
        );

      case 'brand_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Brand</option>
            {brands.map(brand => (
              <option key={brand.id} value={brand.id}>{brand.name}</option>
            ))}
          </select>
        );

      case 'competition_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Competition</option>
            {competitions.map(competition => (
              <option key={competition.id} value={competition.id}>{competition.competition_name || competition.name}</option>
            ))}
          </select>
        );

      case 'master_kit_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Master Kit</option>
            {masterKits.map(kit => (
              <option key={kit.id} value={kit.id}>
                {kit.team_info?.name || 'Unknown Team'} - {kit.season} - {kit.type}
              </option>
            ))}
          </select>
        );

      case 'reference_kit_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Reference Kit</option>
            {referenceKits.map(kit => (
              <option key={kit.id} value={kit.id}>
                {kit.master_kit_info?.team_info?.name || 'Unknown Team'} - {kit.model} - {kit.topkit_reference}
              </option>
            ))}
          </select>
        );

      case 'player_select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select Player</option>
            {players.map(player => (
              <option key={player.id} value={player.id}>{player.name}</option>
            ))}
          </select>
        );

      case 'season_select': {
        const currentYear = new Date().getFullYear();
        const seasons = [];
        // Generate seasons from 1980-1981 to current+5 years for suggestions
        for (let year = 1980; year <= currentYear + 5; year++) {
          seasons.push(`${year}-${year + 1}`);
        }
        
        return (
          <div className="relative">
            <input
              type="text"
              value={value || ''}
              onChange={(e) => onChange(field.key, e.target.value)}
              placeholder={field.placeholder || 'Enter season (e.g., 1986-1987, 2024-2025)'}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required={field.required}
              list={`seasons-${field.key}`}
            />
            <datalist id={`seasons-${field.key}`}>
              {seasons.reverse().map(season => (
                <option key={season} value={season}>{season}</option>
              ))}
            </datalist>
          </div>
        );
      }

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required={field.required}
          >
            <option value="">Select {field.label}</option>
            {field.options?.map(option => (
              <option key={option} value={option.toLowerCase()}>{option}</option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={!!value}
              onChange={(e) => onChange(field.key, e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <label className="ml-2 text-sm text-gray-700">
              {field.label}
            </label>
          </div>
        );

      case 'image':
      case 'image_multiple':
        return (
          <div className="space-y-2">
            <input
              type="file"
              accept="image/*"
              multiple={field.type === 'image_multiple'}
              onChange={handleImageChange}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
              required={field.required && !value}
            />
            <p className="text-xs text-gray-500">
              Max 5MB per image. {field.required ? 'Required.' : 'Optional.'}
            </p>
          </div>
        );

      case 'color_list':
      case 'text_list':
        return (
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={newItem}
                onChange={(e) => setNewItem(e.target.value)}
                placeholder={field.placeholder || `Add ${field.type === 'color_list' ? 'color' : 'item'}`}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleListAdd())}
              />
              <button
                type="button"
                onClick={handleListAdd}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
              >
                +
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {listItems.map((item, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm flex items-center gap-2"
                >
                  {field.type === 'color_list' && (
                    <div
                      className="w-3 h-3 rounded-full border border-gray-300"
                      style={{ backgroundColor: item.toLowerCase() }}
                    />
                  )}
                  {item}
                  <button
                    type="button"
                    onClick={() => handleListRemove(item)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => onChange(field.key, e.target.value)}
            placeholder={field.placeholder || ''}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
            required={field.required}
          />
        );
    }
  };

  return (
    <div className={field.type === 'image' || field.type === 'image_multiple' ? 'md:col-span-2' : ''}>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {field.label} {field.required && '*'}
      </label>
      {renderField()}
    </div>
  );
};

export default UnifiedFieldRenderer;