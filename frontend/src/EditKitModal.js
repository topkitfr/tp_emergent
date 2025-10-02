import React, { useState, useEffect } from 'react';

const EditKitModal = ({ isOpen, onClose, masterKit, user, API }) => {
  // Form state
  const [formData, setFormData] = useState({
    // 1. BASE INFO
    type: 'replica',
    gender: 'men', 
    size: 'm',
    condition: 'used',
    
    // 2. PLAYER & PRINTING
    player_id: '',
    player_aura: 1.0,
    number: '',
    style: 'league',
    competition_patch_id: '',
    
    // 3. ORIGIN & AUTHENTICITY
    origin_type: 'standard',
    competition_id: '',
    match_date: '',
    opponent_team_id: '',
    special_match_type: '',
    match_result: '',
    performance: [],
    match_proof: 'none',
    
    // 4. SIGNATURE
    signed: false,
    signature_proof: 'none',
    
    // 5. PHOTOS
    front_photo: '',
    back_photo: '',
    other_photos: [],
    
    // 6. USER ESTIMATION
    user_estimate: '',
    
    // 7. NOTES
    notes: ''
  });

  // Dropdown data
  const [players, setPlayers] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [teams, setTeams] = useState([]);
  
  // Calculation results
  const [estimatedPrice, setEstimatedPrice] = useState(0);
  const [coefficients, setCoefficients] = useState({});
  const [loading, setLoading] = useState(false);

  // Load dropdown data
  useEffect(() => {
    if (isOpen) {
      loadFormData();
    }
  }, [isOpen]);

  // Calculate price when form changes
  useEffect(() => {
    if (isOpen) {
      calculatePrice();
    }
  }, [formData, isOpen]);

  const loadFormData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Load players
      const playersRes = await fetch(`${API}/api/form-data/players`, { headers });
      if (playersRes.ok) {
        const playersData = await playersRes.json();
        setPlayers(playersData);
      }

      // Load competitions
      const compsRes = await fetch(`${API}/api/form-data/competitions`, { headers });
      if (compsRes.ok) {
        const compsData = await compsRes.json();
        setCompetitions(compsData);
      }

      // Load teams
      const teamsRes = await fetch(`${API}/api/form-data/teams`, { headers });
      if (teamsRes.ok) {
        const teamsData = await teamsRes.json();
        setTeams(teamsData);
      }
    } catch (error) {
      console.error('Error loading form data:', error);
    }
  };

  const calculatePrice = async () => {
    try {
      const response = await fetch(`${API}/api/calculate-price`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const result = await response.json();
        setEstimatedPrice(result.estimated_price);
        setCoefficients(result.coefficients);
      }
    } catch (error) {
      console.error('Error calculating price:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // Auto-populate player aura when player is selected
      if (field === 'player_id' && value) {
        const selectedPlayer = players.find(p => p.id === value);
        if (selectedPlayer) {
          newData.player_aura = selectedPlayer.aura;
        }
      }
      
      return newData;
    });
  };

  const handlePerformanceChange = (performance, checked) => {
    setFormData(prev => ({
      ...prev,
      performance: checked 
        ? [...prev.performance, performance]
        : prev.performance.filter(p => p !== performance)
    }));
  };

  const handlePhotoUpload = async (photoType, file) => {
    try {
      setLoading(true);
      const formDataUpload = new FormData();
      formDataUpload.append('photo', file);

      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/upload/kit-photo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataUpload
      });

      if (response.ok) {
        const result = await response.json();
        handleInputChange(photoType, result.photo_url);
      } else {
        alert('Failed to upload photo');
      }
    } catch (error) {
      console.error('Error uploading photo:', error);
      alert('Error uploading photo');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch(`${API}/api/master-kits/${masterKit.id}/edit`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ kit_details: formData })
      });

      if (response.ok) {
        alert('Kit updated successfully!');
        onClose();
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || 'Failed to update kit'}`);
      }
    } catch (error) {
      console.error('Error saving kit:', error);
      alert('Error saving kit');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto w-full">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-800">
              Edit Kit: {masterKit?.club || masterKit?.club_name} - {masterKit?.season}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        <div className="p-6 space-y-8">
          {/* 1. BASE INFO */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">1. Base Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="replica">Replica (€90)</option>
                  <option value="authentic">Authentic (€140)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="men">Men</option>
                  <option value="women">Women</option>
                  <option value="kid">Kid</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Size</label>
                <select
                  value={formData.size}
                  onChange={(e) => handleInputChange('size', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="xs">XS</option>
                  <option value="s">S</option>
                  <option value="m">M</option>
                  <option value="l">L</option>
                  <option value="xl">XL</option>
                  <option value="xxl">XXL</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
                <select
                  value={formData.condition}
                  onChange={(e) => handleInputChange('condition', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="nwt">New with tags (+0.3)</option>
                  <option value="very_good">Very good (+0.15)</option>
                  <option value="used">Used (0)</option>
                  <option value="damaged">Damaged (-0.25)</option>
                  <option value="needs_restore">Needs restore (-0.5)</option>
                </select>
              </div>
            </div>
          </section>

          {/* 2. PLAYER & PRINTING */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">2. Player & Printing</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Player</label>
                <select
                  value={formData.player_id}
                  onChange={(e) => handleInputChange('player_id', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">No player</option>
                  {players.map(player => (
                    <option key={player.id} value={player.id}>
                      {player.display_name}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Number</label>
                <input
                  type="number"
                  min="0"
                  max="99"
                  value={formData.number}
                  onChange={(e) => handleInputChange('number', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="0-99"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Style</label>
                <select
                  value={formData.style}
                  onChange={(e) => handleInputChange('style', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="league">League</option>
                  <option value="cup">Cup</option>
                  <option value="special">Special</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Competition Patch</label>
                <select
                  value={formData.competition_patch_id}
                  onChange={(e) => handleInputChange('competition_patch_id', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">No patch</option>
                  {competitions.map(comp => (
                    <option key={comp.id} value={comp.id}>
                      {comp.competition_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </section>

          {/* 3. ORIGIN & AUTHENTICITY */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">3. Origin & Authenticity</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Origin Type</label>
                <select
                  value={formData.origin_type}
                  onChange={(e) => handleInputChange('origin_type', e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="standard">Standard (0)</option>
                  <option value="match_issued">Match Issued (+0.8)</option>
                  <option value="match_worn">Match Worn (+1.5)</option>
                </select>
              </div>
              
              {(formData.origin_type === 'match_issued' || formData.origin_type === 'match_worn') && (
                <>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Competition</label>
                      <select
                        value={formData.competition_id}
                        onChange={(e) => handleInputChange('competition_id', e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      >
                        <option value="">Select competition</option>
                        {competitions.map(comp => (
                          <option key={comp.id} value={comp.id}>
                            {comp.competition_name}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Match Date</label>
                      <input
                        type="date"
                        value={formData.match_date}
                        onChange={(e) => handleInputChange('match_date', e.target.value)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </div>
                  
                  {formData.origin_type === 'match_worn' && (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Special Match Type</label>
                          <select
                            value={formData.special_match_type}
                            onChange={(e) => handleInputChange('special_match_type', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2"
                          >
                            <option value="">Regular match</option>
                            <option value="classico">Classico (+0.7)</option>
                            <option value="derby">Derby (+0.7)</option>
                            <option value="final">Final (+1.0)</option>
                            <option value="title_decider">Title Decider (+0.8)</option>
                            <option value="historical">Historical (+0.8)</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Opponent</label>
                          <select
                            value={formData.opponent_team_id}
                            onChange={(e) => handleInputChange('opponent_team_id', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2"
                          >
                            <option value="">Select opponent</option>
                            {teams.map(team => (
                              <option key={team.id} value={team.id}>
                                {team.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Match Result</label>
                          <select
                            value={formData.match_result}
                            onChange={(e) => handleInputChange('match_result', e.target.value)}
                            className="w-full border border-gray-300 rounded-md px-3 py-2"
                          >
                            <option value="">Not specified</option>
                            <option value="win">Win (+0.3)</option>
                            <option value="draw">Draw (0)</option>
                            <option value="loss">Loss (-0.2)</option>
                          </select>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Performance</label>
                          <div className="space-y-2">
                            {[
                              { key: 'scored_goal', label: 'Scored goal (+0.5)' },
                              { key: 'decisive_assist', label: 'Decisive assist (+0.3)' },
                              { key: 'man_of_the_match', label: 'Man of the match (+0.4)' },
                              { key: 'title_winning_goal', label: 'Title winning goal (+1.0)' },
                              { key: 'clean_sheet', label: 'Clean sheet (+0.5)' }
                            ].map(perf => (
                              <label key={perf.key} className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={formData.performance.includes(perf.key)}
                                  onChange={(e) => handlePerformanceChange(perf.key, e.target.checked)}
                                  className="mr-2"
                                />
                                <span className="text-sm">{perf.label}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Proof</label>
                    <select
                      value={formData.match_proof}
                      onChange={(e) => handleInputChange('match_proof', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="none">No proof (-0.5)</option>
                      <option value="photo">Photo (+0.5)</option>
                      <option value="certificate">Certificate (+0.4)</option>
                    </select>
                  </div>
                </>
              )}
            </div>
          </section>

          {/* 4. SIGNATURE */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">4. Signature</h3>
            <div className="space-y-4">
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.signed}
                    onChange={(e) => handleInputChange('signed', e.target.checked)}
                    className="mr-2"
                  />
                  <span>Signed (+2.5)</span>
                </label>
              </div>
              
              {formData.signed && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Signature Proof</label>
                  <select
                    value={formData.signature_proof}
                    onChange={(e) => handleInputChange('signature_proof', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="none">No proof (-0.5)</option>
                    <option value="photo">Photo (+0.5)</option>
                    <option value="certificate">Certificate (+0.4)</option>
                  </select>
                </div>
              )}
            </div>
          </section>

          {/* 5. PHOTOS */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">5. Photos</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Front Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files[0] && handlePhotoUpload('front_photo', e.target.files[0])}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
                {formData.front_photo && <p className="text-xs text-green-600 mt-1">Uploaded</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Back Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => e.target.files[0] && handlePhotoUpload('back_photo', e.target.files[0])}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
                {formData.back_photo && <p className="text-xs text-green-600 mt-1">Uploaded</p>}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Other Photos (max 3)</label>
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
            </div>
          </section>

          {/* 6. USER ESTIMATION */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">6. User Estimation</h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Your Estimate (€)</label>
              <input
                type="number"
                min="0"
                value={formData.user_estimate}
                onChange={(e) => handleInputChange('user_estimate', parseFloat(e.target.value) || '')}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="Enter your price estimate"
              />
            </div>
          </section>

          {/* 7. NOTES */}
          <section className="bg-gray-50 rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">7. Notes</h3>
            <div>
              <textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 h-24"
                placeholder="Additional notes about this kit..."
              />
            </div>
          </section>

          {/* PRICE CALCULATION DISPLAY */}
          <section className="bg-blue-50 rounded-lg p-4 border-2 border-blue-200">
            <h3 className="text-lg font-semibold mb-4 text-blue-800">Estimated Price</h3>
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
        </div>

        {/* Action Buttons */}
        <div className="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 flex justify-end space-x-4">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-400"
            disabled={loading}
          >
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditKitModal;