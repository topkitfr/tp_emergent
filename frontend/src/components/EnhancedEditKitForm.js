import React, { useState, useEffect } from 'react';
import { X, AlertCircle, Upload } from 'lucide-react';

const EnhancedEditKitForm = ({ isOpen, onClose, editingItem, formData, onFormDataChange, onSave, API, title = "Edit Kit Details" }) => {
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [fileUploads, setFileUploads] = useState({
    photos: []
  });

  // Load form data when modal opens
  useEffect(() => {
    if (isOpen) {
      loadFormData();
    }
  }, [isOpen]);

  const loadFormData = async () => {
    try {
      setLoading(true);
      const [playersRes, teamsRes] = await Promise.all([
        fetch(`${API}/api/form-data/players`),
        fetch(`${API}/api/form-data/clubs`)
      ]);

      if (playersRes.ok && teamsRes.ok) {
        const [playersData, teamsData] = await Promise.all([
          playersRes.json(),
          teamsRes.json()
        ]);

        setPlayers(playersData);
        setTeams(teamsData);
      }
    } catch (error) {
      console.error('Error loading form data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (key, value) => {
    onFormDataChange(key, value);
    // Clear error when field is updated
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
  };

  const handleFileUpload = (files) => {
    const fileArray = Array.from(files);
    
    setFileUploads(prev => ({
      ...prev,
      photos: [...prev.photos, ...fileArray]
    }));
  };

  const removePhoto = (index) => {
    setFileUploads(prev => ({
      ...prev,
      photos: prev.photos.filter((_, i) => i !== index)
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Note: Photos are optional, no validation required
    
    // Validate required conditional fields
    if ((formData.origin_type === 'match_issued' || formData.origin_type === 'match_worn') && !formData.competition) {
      newErrors.competition = 'Competition is required for match-issued or match-worn kits';
    }

    if ((formData.origin_type === 'match_issued' || formData.origin_type === 'match_worn') && !formData.match_date) {
      newErrors.match_date = 'Match date is required for match-issued or match-worn kits';
    }

    if ((formData.origin_type === 'match_issued' || formData.origin_type === 'match_worn') && !formData.opponent) {
      newErrors.opponent = 'Opponent is required for match-issued or match-worn kits';
    }

    if (formData.signature && !formData.signature_player) {
      newErrors.signature_player = 'Player is required when kit is signed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Upload photos first if any
    if (fileUploads.photos.length > 0) {
      // Handle photo uploads here
      console.log('Uploading photos...', fileUploads.photos);
    }

    onSave();
  };

  if (!isOpen || !editingItem) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900">
              {editingItem.master_kit?.club || 'Unknown Club'} - {editingItem.master_kit?.season || 'Unknown Season'}
            </h3>
            <p className="text-sm text-gray-600">
              Editing comprehensive details for your collection
            </p>
          </div>

          <div className="space-y-8">
            {/* A. Basic Information */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">A. Basic Information</h3>
              
              {/* Type */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Kit Type</label>
                <div className="flex flex-wrap gap-4">
                  {[
                    { value: 'replica', label: 'Replica (€90)' },
                    { value: 'authentic', label: 'Authentic (€140)' }
                  ].map(type => (
                    <label key={type.value} className="flex items-center">
                      <input
                        type="radio"
                        name="kit_type"
                        value={type.value}
                        checked={formData.kit_type === type.value}
                        onChange={(e) => handleInputChange('kit_type', e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="ml-2 text-sm text-gray-700">{type.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Gender */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                <div className="flex flex-wrap gap-4">
                  {['Men', 'Women', 'Kid'].map(gender => (
                    <label key={gender} className="flex items-center">
                      <input
                        type="radio"
                        name="gender"
                        value={gender.toLowerCase()}
                        checked={formData.gender === gender.toLowerCase()}
                        onChange={(e) => handleInputChange('gender', e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="ml-2 text-sm text-gray-700">{gender}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Size */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Size</label>
                <select
                  value={formData.size || ''}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select size</option>
                  {['XS', 'S', 'M', 'L', 'XL', 'XXL'].map(size => (
                    <option key={size} value={size}>{size}</option>
                  ))}
                </select>
              </div>

              {/* Condition */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Condition</label>
                <select
                  value={formData.condition || ''}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select condition</option>
                  <option value="nwt">New with tags (+0.3)</option>
                  <option value="very_good">Very good (+0.15)</option>
                  <option value="used">Used (0)</option>
                  <option value="damaged">Damaged (-0.25)</option>
                  <option value="needs_restore">Needs restore (-0.5)</option>
                </select>
              </div>
            </section>

            {/* B. Player & Printing */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">B. Player & Printing</h3>
              
              {/* Associated Player */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Associated Player</label>
                <select
                  value={formData.associated_player || ''}
                  onChange={(e) => handleInputChange('associated_player', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select player</option>
                  {players.map(player => (
                    <option key={player.id} value={player.id}>
                      {player.name} {(player.coefficient || player.influence_coefficient) && `(×${player.coefficient || player.influence_coefficient})`}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Player coefficient automatically applied to price estimation</p>
              </div>
            </section>

            {/* C. Origin & Authenticity */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">C. Origin & Authenticity</h3>
              
              {/* Origin Type */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Origin Type</label>
                <div className="space-y-2">
                  {[
                    { value: 'standard', label: 'Standard (0)', coefficient: 0 },
                    { value: 'match_issued', label: 'Match-issued (+0.8)', coefficient: 0.8 },
                    { value: 'match_worn', label: 'Match-worn (+1.5)', coefficient: 1.5 }
                  ].map(option => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="radio"
                        name="origin_type"
                        value={option.value}
                        checked={formData.origin_type === option.value}
                        onChange={(e) => handleInputChange('origin_type', e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Conditional fields for match-issued/match-worn */}
              {(formData.origin_type === 'match_issued' || formData.origin_type === 'match_worn') && (
                <>
                  {/* Competition */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Competition</label>
                    <select
                      value={formData.competition || ''}
                      onChange={(e) => handleInputChange('competition', e.target.value)}
                      className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                        errors.competition ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select competition</option>
                      <option value="national_league">National League (+0.2)</option>
                      <option value="national_cup">National Cup (+0.1)</option>
                      <option value="continental_competition">Continental Competition (+0.5)</option>
                      <option value="international_competition">International Competition (+1.0)</option>
                      <option value="continental_super_cup">Continental Super Cup (+0.2)</option>
                    </select>
                    {errors.competition && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.competition}
                      </p>
                    )}
                  </div>

                  {/* Authenticity Proof */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Authenticity Proof</label>
                    <div className="space-y-2">
                      {[
                        { value: 'match_photos', label: 'Match photos/videos (+0.3)', coefficient: 0.3 },
                        { value: 'certificate', label: 'Certificate of authenticity (+0.2)', coefficient: 0.2 },
                        { value: 'no_proof', label: 'No proof (-0.5)', coefficient: -0.5 }
                      ].map(option => (
                        <label key={option.value} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={formData.authenticity_proof?.includes(option.value) || false}
                            onChange={(e) => {
                              const currentProofs = formData.authenticity_proof || [];
                              if (e.target.checked) {
                                handleInputChange('authenticity_proof', [...currentProofs, option.value]);
                              } else {
                                handleInputChange('authenticity_proof', currentProofs.filter(p => p !== option.value));
                              }
                            }}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                          <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Match Date */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Match Date</label>
                    <input
                      type="date"
                      value={formData.match_date || ''}
                      onChange={(e) => handleInputChange('match_date', e.target.value)}
                      className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                        errors.match_date ? 'border-red-500' : 'border-gray-300'
                      }`}
                    />
                    {errors.match_date && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.match_date}
                      </p>
                    )}
                  </div>

                  {/* Opponent */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Opponent</label>
                    <select
                      value={formData.opponent || ''}
                      onChange={(e) => handleInputChange('opponent', e.target.value)}
                      className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                        errors.opponent ? 'border-red-500' : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select opponent</option>
                      {teams.map(team => (
                        <option key={team.id} value={team.id}>{team.name}</option>
                      ))}
                    </select>
                    {errors.opponent && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.opponent}
                      </p>
                    )}
                  </div>
                </>
              )}
            </section>

            {/* D. Physical Condition */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">D. Physical Condition</h3>
              
              {/* General Condition */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">General Condition</label>
                <select
                  value={formData.general_condition || ''}
                  onChange={(e) => handleInputChange('general_condition', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select condition</option>
                  <option value="new_with_tags">New with Condition tags (+0.3)</option>
                  <option value="very_good">Very Good (+0.15)</option>
                  <option value="used">Used (0)</option>
                  <option value="damaged">Damaged (-0.25)</option>
                  <option value="needs_restoration">Needs restoration (-0.5)</option>
                </select>
              </div>

              {/* Photos */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Photos (Optional - Recommended: front, back, details)
                </label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => handleFileUpload(e.target.files)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {fileUploads.photos.length > 0 && (
                  <div className="mt-2 grid grid-cols-3 gap-2">
                    {fileUploads.photos.map((file, index) => (
                      <div key={index} className="relative">
                        <img
                          src={URL.createObjectURL(file)}
                          alt={`Upload ${index + 1}`}
                          className="w-full h-24 object-cover rounded-lg border"
                        />
                        <button
                          type="button"
                          onClick={() => removePhoto(index)}
                          className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  {fileUploads.photos.length} photos uploaded (photos are optional but recommended for better documentation)
                </p>
                {errors.photos && (
                  <p className="text-red-500 text-sm mt-1 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.photos}
                  </p>
                )}
              </div>
            </section>

            {/* E. Technical Details */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">E. Technical Details</h3>
              
              {/* Patches */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Patches</label>
                <div className="space-y-2">
                  {[
                    { value: 'national_league', label: 'National League (+0.1)', coefficient: 0.1 },
                    { value: 'national_cup', label: 'National Cup (+0.1)', coefficient: 0.1 },
                    { value: 'continental_competition', label: 'Continental Competition (+0.5)', coefficient: 0.5 },
                    { value: 'international_competition', label: 'International Competition (+1.0)', coefficient: 1.0 },
                    { value: 'continental_super_cup', label: 'Continental Super Cup (+0.2)', coefficient: 0.2 },
                    { value: 'other', label: 'Other (specify)', coefficient: 0 }
                  ].map(option => (
                    <label key={option.value} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.patches?.includes(option.value) || false}
                        onChange={(e) => {
                          const currentPatches = formData.patches || [];
                          if (e.target.checked) {
                            handleInputChange('patches', [...currentPatches, option.value]);
                          } else {
                            handleInputChange('patches', currentPatches.filter(p => p !== option.value));
                          }
                        }}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                    </label>
                  ))}
                </div>
                {formData.patches?.includes('other') && (
                  <input
                    type="text"
                    placeholder="Specify other patches"
                    value={formData.other_patches || ''}
                    onChange={(e) => handleInputChange('other_patches', e.target.value)}
                    className="mt-2 w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  />
                )}
              </div>

              {/* Signature */}
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.signature || false}
                    onChange={(e) => handleInputChange('signature', e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Signed (+2.0)</span>
                </label>
                
                {formData.signature && (
                  <div className="mt-3 space-y-3">
                    {/* Player dropdown */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Player</label>
                      <select
                        value={formData.signature_player || ''}
                        onChange={(e) => handleInputChange('signature_player', e.target.value)}
                        className={`w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 ${
                          errors.signature_player ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        <option value="">Select player</option>
                        {players.map(player => (
                          <option key={player.id} value={player.id}>{player.name}</option>
                        ))}
                      </select>
                      {errors.signature_player && (
                        <p className="text-red-500 text-sm mt-1 flex items-center">
                          <AlertCircle className="w-4 h-4 mr-1" />
                          {errors.signature_player}
                        </p>
                      )}
                    </div>

                    {/* Signature Certificate */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Signature Certificate</label>
                      <select
                        value={formData.signature_certificate || ''}
                        onChange={(e) => handleInputChange('signature_certificate', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select certificate status</option>
                        <option value="yes">Yes (+0.3)</option>
                        <option value="no">No (0)</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* F. User Estimate */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">F. User Estimate</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Your Estimate (€)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.user_estimate || ''}
                  onChange={(e) => handleInputChange('user_estimate', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="0.00"
                />
              </div>
            </section>

            {/* G. Comments */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">G. Comments</h3>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Comments</label>
                <textarea
                  value={formData.comments || ''}
                  onChange={(e) => handleInputChange('comments', e.target.value)}
                  rows="4"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="Additional comments about this kit..."
                />
              </div>
            </section>
          </div>

          <div className="flex justify-between items-center space-x-3 pt-6 border-t border-gray-200 mt-8">
            <div className="text-xs text-gray-500">
              💡 All coefficients are automatically applied to price estimation
            </div>
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
              <button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2"
              >
                <span>💾</span>
                <span>Save Enhanced Details</span>
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EnhancedEditKitForm;