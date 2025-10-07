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
  const [estimatedPrice, setEstimatedPrice] = useState(0);
  const [coefficients, setCoefficients] = useState({});

  // Load form data when modal opens
  useEffect(() => {
    if (isOpen) {
      loadFormData();
      // Initialize form with existing item data
      if (editingItem) {
        // Map existing data to form fields
        const initialFormData = {
          kit_type: editingItem.kit_type || 'replica',
          condition: editingItem.condition || '',
          gender: editingItem.gender || '',
          size: editingItem.size || '',
          number: editingItem.number || '',
          printing_style: editingItem.printing_style || '',
          competition_patch: editingItem.competition_patch || '',
          associated_player: editingItem.associated_player_id || '',
          origin_type: editingItem.origin_type || '',
          competition: editingItem.competition || '',
          match_date: editingItem.match_date || '',
          opponent: editingItem.opponent_id || '',
          special_match_type: editingItem.special_match_type || '',
          match_result: editingItem.match_result || '',
          performance: editingItem.performance || [],
          match_proof: editingItem.match_proof || '',
          signed: editingItem.signed || false,
          signature_proof: editingItem.signature_proof || '',
          user_estimate: editingItem.user_estimate || '',
          notes: editingItem.personal_notes || ''
        };
        
        // Update form data with existing values
        Object.keys(initialFormData).forEach(key => {
          if (initialFormData[key] !== '' && initialFormData[key] !== null && initialFormData[key] !== undefined) {
            onFormDataChange(key, initialFormData[key]);
          }
        });
      }
      calculatePrice();
    }
  }, [isOpen, editingItem]);

  // Calculate price when form data changes
  useEffect(() => {
    if (isOpen && Object.keys(formData).length > 0) {
      calculatePrice();
    }
  }, [formData, isOpen]);

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
    // Trigger price calculation after data change
    setTimeout(() => calculatePrice(), 100);
  };

  const calculatePrice = async () => {
    try {
      // Include master_kit_id in the calculation data
      const calculationData = {
        ...formData,
        master_kit_id: editingItem?.master_kit_id || editingItem?.master_kit?.id
      };
      
      const response = await fetch(`${API}/api/calculate-price`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(calculationData)
      });
      
      if (response.ok) {
        const result = await response.json();
        setEstimatedPrice(result.estimated_price || 0);
        setCoefficients(result.coefficients || {});
      }
    } catch (error) {
      console.error('Error calculating price:', error);
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
                  <option value="club_stock">Home (0)</option>
                  <option value="match_prepared">Away (0)</option>
                  <option value="match_worn">Third (+0.1)</option>
                  <option value="training">Fourth (+0.2)</option>
                  <option value="other">GK (+0.1)</option>
                  <option value="other">Special (+0.3)</option>
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
                      {player.name} {(player.coefficient || player.influence_coefficient) && `(${player.coefficient || player.influence_coefficient})`}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">Player aura coefficient automatically applied to price estimation</p>
              </div>

              {/* Number */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Number (+0.1)</label>
                <input
                  type="number"
                  min="0"
                  max="99"
                  value={formData.number || ''}
                  onChange={(e) => handleInputChange('number', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  placeholder="0-99"
                />
              </div>

              {/* Style */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Printing Style</label>
                <select
                  value={formData.printing_style || ''}
                  onChange={(e) => handleInputChange('printing_style', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">No printing (0)</option>
                  <option value="league">League (+0.05)</option>
                  <option value="cup">Cup (+0.05)</option>
                  <option value="special">Special (+0.1)</option>
                </select>
              </div>

              {/* Competition Patch */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Competition Patch</label>
                <select
                  value={formData.competition_patch || ''}
                  onChange={(e) => handleInputChange('competition_patch', e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">No patch (0)</option>
                  <option value="ucl">UEFA Champions League (+1.0)</option>
                  <option value="uel">UEFA Europa League (+0.5)</option>
                  <option value="uecl">UEFA Europa Conference League (+0.2)</option>
                  <option value="laliga">La Liga (+0.1)</option>
                  <option value="premier_league">Premier League (+0.1)</option>
                  <option value="bundesliga">Bundesliga (+0.1)</option>
                  <option value="serie_a">Serie A (+0.1)</option>
                  <option value="ligue_1">Ligue 1 (+0.1)</option>
                  <option value="world_cup">FIFA World Cup (+1.0)</option>
                  <option value="euro">UEFA Euro (+1.0)</option>
                  <option value="copa_america">Copa América (+1.0)</option>
                  <option value="other">Other (+0.1)</option>
                </select>
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
                      <option value="ucl">UEFA Champions League</option>
                      <option value="uel">UEFA Europa League</option>
                      <option value="uecl">UEFA Europa Conference League</option>
                      <option value="laliga">La Liga</option>
                      <option value="premier_league">Premier League</option>
                      <option value="bundesliga">Bundesliga</option>
                      <option value="serie_a">Serie A</option>
                      <option value="ligue_1">Ligue 1</option>
                      <option value="world_cup">FIFA World Cup</option>
                      <option value="euro">UEFA Euro</option>
                      <option value="copa_america">Copa América</option>
                      <option value="national_cup">National Cup</option>
                    </select>
                    {errors.competition && (
                      <p className="text-red-500 text-sm mt-1 flex items-center">
                        <AlertCircle className="w-4 h-4 mr-1" />
                        {errors.competition}
                      </p>
                    )}
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

                  {/* Special fields for match-worn kits */}
                  {formData.origin_type === 'match_worn' && (
                    <>
                      {/* Special Match Type */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Special Match Type</label>
                        <select
                          value={formData.special_match_type || ''}
                          onChange={(e) => handleInputChange('special_match_type', e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Regular match</option>
                          <option value="classico">Clásico (+0.7)</option>
                          <option value="derby">Derby (+0.7)</option>
                          <option value="final">Final (+1.0)</option>
                          <option value="title_decider">Title Decider (+0.8)</option>
                          <option value="historical">Historical Match (+0.8)</option>
                        </select>
                      </div>

                      {/* Match Result */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Match Result</label>
                        <select
                          value={formData.match_result || ''}
                          onChange={(e) => handleInputChange('match_result', e.target.value)}
                          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Not specified</option>
                          <option value="win">Win (+0.3)</option>
                          <option value="draw">Draw (0)</option>
                          <option value="loss">Loss (-0.2)</option>
                        </select>
                      </div>

                      {/* Performance */}
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">Performance (multiple selections allowed)</label>
                        <div className="space-y-2">
                          {[
                            { value: 'scored_goal', label: 'Scored Goal (+0.5)' },
                            { value: 'decisive_assist', label: 'Decisive Assist (+0.3)' },
                            { value: 'man_of_the_match', label: 'Man of the Match (+0.4)' },
                            { value: 'title_winning_goal', label: 'Title Winning Goal (+1.0)' },
                            { value: 'clean_sheet', label: 'Clean Sheet (+0.5)' }
                          ].map(perf => (
                            <label key={perf.value} className="flex items-center">
                              <input
                                type="checkbox"
                                checked={formData.performance?.includes(perf.value) || false}
                                onChange={(e) => {
                                  const currentPerf = formData.performance || [];
                                  if (e.target.checked) {
                                    handleInputChange('performance', [...currentPerf, perf.value]);
                                  } else {
                                    handleInputChange('performance', currentPerf.filter(p => p !== perf.value));
                                  }
                                }}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                              />
                              <span className="ml-2 text-sm text-gray-700">{perf.label}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    </>
                  )}

                  {/* Match Proof (for both match-issued and match-worn) */}
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Match Proof</label>
                    <select
                      value={formData.match_proof || ''}
                      onChange={(e) => handleInputChange('match_proof', e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="none">No proof (-0.5)</option>
                      <option value="photo">Photo (+0.5)</option>
                      <option value="certificate">Certificate (+0.4)</option>
                    </select>
                  </div>
                </>
              )}

              {/* Signature */}
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.signed || false}
                    onChange={(e) => handleInputChange('signed', e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Signed (+2.5)</span>
                </label>
                
                {formData.signed && (
                  <div className="mt-3 space-y-3">
                    {/* Signature Proof */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Signature Proof</label>
                      <select
                        value={formData.signature_proof || ''}
                        onChange={(e) => handleInputChange('signature_proof', e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="none">No proof (-0.5)</option>
                        <option value="photo">Photo (+0.5)</option>
                        <option value="certificate">Certificate (+0.4)</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* D. Photos */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">D. Photos</h3>
              
              {/* Front Photo */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Front Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      handleInputChange('front_photo', e.target.files[0]);
                    }
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {formData.front_photo && (
                  <p className="text-xs text-green-600 mt-1">✓ Photo selected</p>
                )}
              </div>

              {/* Back Photo */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Back Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    if (e.target.files[0]) {
                      handleInputChange('back_photo', e.target.files[0]);
                    }
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {formData.back_photo && (
                  <p className="text-xs text-green-600 mt-1">✓ Photo selected</p>
                )}
              </div>

              {/* Other Photos */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Other Photos (max 3)</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => {
                    if (e.target.files.length > 0) {
                      handleInputChange('other_photos', Array.from(e.target.files));
                    }
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
                {formData.other_photos && formData.other_photos.length > 0 && (
                  <p className="text-xs text-green-600 mt-1">✓ {formData.other_photos.length} photo(s) selected</p>
                )}
              </div>
            </section>

            {/* E. User Estimate */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">E. User Estimate</h3>
              
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

            {/* F. Comments */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-4 border-b pb-2">F. Comments</h3>
              
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

          {/* Price Calculation Display */}
          {estimatedPrice > 0 && (
            <section className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200 mt-6">
              <h3 className="text-lg font-semibold mb-4 text-blue-800">TopKit Estimated Price</h3>
              <div className="text-3xl font-bold text-blue-600 mb-4">€{estimatedPrice.toFixed(2)}</div>
              
              {Object.keys(coefficients).length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium text-blue-700">Calculation Breakdown:</h4>
                  {Object.entries(coefficients).map(([key, value]) => (
                    <div key={key} className="text-sm text-blue-600">
                      <span className="capitalize">{key.replace('_', ' ')}:</span> {value}
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

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