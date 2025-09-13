import React, { useState, useEffect } from 'react';

const ContributionDetailModal = ({ 
  contribution, 
  isOpen, 
  onClose, 
  onVote, 
  voting = false,
  API 
}) => {
  const [currentData, setCurrentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedImageView, setSelectedImageView] = useState(null);
  const [activeTab, setActiveTab] = useState('comparison'); // 'comparison' | 'history' | 'analytics'
  const [voteComments, setVoteComments] = useState({});
  const [granularVotes, setGranularVotes] = useState({});
  const [showVoteComment, setShowVoteComment] = useState(false);
  const [pendingVoteType, setPendingVoteType] = useState(null);
  const [contributorHistory, setContributorHistory] = useState([]);
  const [entityHistory, setEntityHistory] = useState([]);

  // Load current entity data for comparison
  useEffect(() => {
    if (isOpen && contribution) {
      loadCurrentEntityData();
      loadContributorHistory();
      loadEntityHistory();
    }
  }, [isOpen, contribution]);

  const loadCurrentEntityData = async () => {
    setLoading(true);
    try {
      const entityEndpoints = {
        'team': 'teams',
        'brand': 'brands',
        'player': 'players',
        'competition': 'competitions',
        'master_kit': 'master-kits',
        'jersey_release': 'jersey-releases'
      };

      const endpoint = entityEndpoints[contribution.entity_type];
      if (endpoint) {
        const response = await fetch(`${API}/api/${endpoint}/${contribution.entity_id}`);
        if (response.ok) {
          const data = await response.json();
          setCurrentData(data);
        }
      }
    } catch (error) {
      console.error('Error loading current entity data:', error);
    }
    setLoading(false);
  };

  // Load contributor's history for reputation
  const loadContributorHistory = async () => {
    try {
      const response = await fetch(`${API}/api/contributions?contributor_id=${contribution.contributor_id}&limit=10`);
      if (response.ok) {
        const data = await response.json();
        setContributorHistory(data);
      }
    } catch (error) {
      console.error('Error loading contributor history:', error);
    }
  };

  // Load entity modification history
  const loadEntityHistory = async () => {
    try {
      const response = await fetch(`${API}/api/contributions?entity_id=${contribution.entity_id}&entity_type=${contribution.entity_type}&status=approved&limit=5`);
      if (response.ok) {
        const data = await response.json();
        setEntityHistory(data);
      }
    } catch (error) {
      console.error('Error loading entity history:', error);
    }
  };

  // Get entity type badge configuration
  const getEntityBadge = (entityType) => {
    const badges = {
      'team': { label: '🏟️ ÉQUIPE', bgColor: 'bg-blue-100', textColor: 'text-blue-800' },
      'brand': { label: '👕 MARQUE', bgColor: 'bg-purple-100', textColor: 'text-purple-800' },
      'player': { label: '👤 JOUEUR', bgColor: 'bg-green-100', textColor: 'text-green-800' },
      'competition': { label: '🏆 COMPÉTITION', bgColor: 'bg-orange-100', textColor: 'text-orange-800' },
      'master_jersey': { label: '👕 MASTER JERSEY', bgColor: 'bg-red-100', textColor: 'text-red-800' },
      'jersey_release': { label: '📦 JERSEY RELEASE', bgColor: 'bg-cyan-100', textColor: 'text-cyan-800' }
    };
    return badges[entityType] || { label: entityType.toUpperCase(), bgColor: 'bg-gray-100', textColor: 'text-gray-800' };
  };

  // Format field values for display
  const formatValue = (key, value) => {
    if (!value) return 'Non spécifié';
    if (key === 'colors' && Array.isArray(value)) {
      return value.join(', ');
    }
    if (key === 'founded_year' && value) {
      return `Fondée en ${value}`;
    }
    if (typeof value === 'boolean') {
      return value ? 'Oui' : 'Non';
    }
    return value.toString();
  };

  // Get human-readable field names
  const getFieldLabel = (key) => {
    const labels = {
      'name': 'Nom',
      'official_name': 'Nom officiel',
      'short_name': 'Nom court',
      'city': 'Ville',
      'country': 'Pays',
      'founded_year': 'Année de fondation',
      'colors': 'Couleurs',
      'primary_colors': 'Couleurs primaires',
      'logo_url': 'Logo',
      'photo_url': 'Photo',
      'front_photo_url': 'Photo avant',
      'back_photo_url': 'Photo arrière',
      'nationality': 'Nationalité',
      'position': 'Position',
      'birth_date': 'Date de naissance',
      'organizer': 'Organisateur',
      'level': 'Niveau',
      'competition_type': 'Type de compétition'
    };
    return labels[key] || key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  // Check if field has changed
  const hasChanged = (key, proposedValue) => {
    if (!currentData) return true;
    const currentValue = currentData[key];
    
    // Handle arrays (like colors)
    if (Array.isArray(proposedValue) && Array.isArray(currentValue)) {
      return JSON.stringify(proposedValue.sort()) !== JSON.stringify(currentValue.sort());
    }
    
    return currentValue !== proposedValue;
  };

  // Handle granular voting (by field)
  const handleGranularVote = (field, voteType) => {
    setGranularVotes(prev => ({
      ...prev,
      [field]: voteType
    }));
  };

  // Handle vote with comment
  const handleVoteWithComment = (voteType) => {
    setPendingVoteType(voteType);
    setShowVoteComment(true);
  };

  // Submit vote with comment
  const submitVoteWithComment = () => {
    if (!voteComments[pendingVoteType]?.trim()) {
      alert('Veuillez ajouter un commentaire pour justifier votre vote');
      return;
    }
    
    const voteData = {
      type: pendingVoteType,
      comment: voteComments[pendingVoteType],
      granular_votes: granularVotes
    };
    
    onVote(contribution.id, pendingVoteType, voteData);
    setShowVoteComment(false);
    setPendingVoteType(null);
  };

  // Get contributor reputation
  const getContributorReputation = () => {
    const approved = contributorHistory.filter(c => c.status === 'approved').length;
    const rejected = contributorHistory.filter(c => c.status === 'rejected').length;
    const total = contributorHistory.length;
    
    if (total === 0) return { level: 'Nouveau', color: 'gray', score: 0 };
    
    const ratio = approved / total;
    
    if (ratio >= 0.9 && total >= 10) return { level: 'Expert', color: 'purple', score: Math.round(ratio * 100) };
    if (ratio >= 0.8 && total >= 5) return { level: 'Expérimenté', color: 'blue', score: Math.round(ratio * 100) };
    if (ratio >= 0.7) return { level: 'Confirmé', color: 'green', score: Math.round(ratio * 100) };
    if (ratio >= 0.5) return { level: 'Apprenti', color: 'yellow', score: Math.round(ratio * 100) };
    return { level: 'Débutant', color: 'red', score: Math.round(ratio * 100) };
  };

  // Enhanced Image zoom modal with gallery navigation
  const ImageZoomModal = ({ images, selectedIndex, onClose, onNavigate }) => {
    const currentImage = images[selectedIndex];
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50" onClick={onClose}>
        <div className="max-w-6xl max-h-6xl p-4 relative">
          {/* Navigation arrows */}
          {images.length > 1 && (
            <>
              <button
                onClick={(e) => { e.stopPropagation(); onNavigate(selectedIndex - 1); }}
                disabled={selectedIndex === 0}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white p-2 rounded-full disabled:opacity-30"
              >
                ←
              </button>
              <button
                onClick={(e) => { e.stopPropagation(); onNavigate(selectedIndex + 1); }}
                disabled={selectedIndex === images.length - 1}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white p-2 rounded-full disabled:opacity-30"
              >
                →
              </button>
            </>
          )}
          
          {/* Image */}
          <img 
            src={currentImage.src} 
            alt={currentImage.alt} 
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
          
          {/* Image info */}
          <div className="absolute bottom-4 left-4 bg-black bg-opacity-70 text-white p-2 rounded">
            <p className="text-sm font-medium">{currentImage.alt}</p>
            {images.length > 1 && (
              <p className="text-xs opacity-75">{selectedIndex + 1} / {images.length}</p>
            )}
          </div>
          
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-black bg-opacity-70 text-white p-2 rounded-full hover:bg-opacity-90"
          >
            ×
          </button>
        </div>
      </div>
    );
  };

  if (!isOpen || !contribution) return null;

  const badge = getEntityBadge(contribution.entity_type);

  return (
    <>
      {/* Main Modal */}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-40 p-4">
        <div className="bg-white rounded-lg shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`px-3 py-1 rounded-full text-xs font-bold ${badge.bgColor} ${badge.textColor}`}>
                  {badge.label}
                </div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {contribution.title || 'Modification proposée'}
                </h2>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            
            {/* Contribution metadata */}
            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
              <span>Par {contribution.contributor_name || 'Anonyme'}</span>
              <span>•</span>
              <span>{new Date(contribution.created_at).toLocaleDateString('fr-FR')}</span>
              <span>•</span>
              <div className="flex items-center space-x-2">
                <span className="text-green-600">👍 {contribution.upvotes || 0}</span>
                <span className="text-red-600">👎 {contribution.downvotes || 0}</span>
              </div>
            </div>
          </div>

          {/* Content with Tabs */}
          <div className="p-6">
            
            {/* Advanced Tabs */}
            <div className="mb-6">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  <button
                    onClick={() => setActiveTab('comparison')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'comparison'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    📊 Comparaison AVANT/APRÈS
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'history'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    📈 Historique ({entityHistory.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('analytics')}
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'analytics'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    🏆 Contributeur
                  </button>
                </nav>
              </div>
            </div>

            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <>
                {/* COMPARISON TAB */}
                {activeTab === 'comparison' && (
                  <div>
                    {/* Description */}
                    {contribution.description && (
                      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                        <h3 className="font-medium text-blue-900 mb-2">💭 Justification du contributeur</h3>
                        <p className="text-blue-800 text-sm">{contribution.description}</p>
                      </div>
                    )}

                    {/* BEFORE/AFTER Comparison with Granular Voting */}
                    {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
                      <div className="mb-6">
                        <h3 className="font-semibold text-gray-900 mb-4">📊 Comparaison détaillée avec vote granulaire</h3>
                        
                        <div className="space-y-4">
                          {Object.entries(contribution.proposed_data).map(([key, proposedValue]) => {
                            const fieldChanged = hasChanged(key, proposedValue);
                            const granularVote = granularVotes[key];
                            
                            return (
                              <div key={key} className={`border rounded-lg p-4 ${fieldChanged ? 'border-yellow-200 bg-yellow-50' : 'border-gray-200'}`}>
                                <div className="flex justify-between items-center mb-3">
                                  <h4 className="font-medium text-gray-900">{getFieldLabel(key)}</h4>
                                  {fieldChanged && (
                                    <div className="flex space-x-2">
                                      <button
                                        onClick={() => handleGranularVote(key, 'reject')}
                                        className={`px-2 py-1 rounded text-xs ${
                                          granularVote === 'reject'
                                            ? 'bg-red-500 text-white'
                                            : 'bg-red-100 text-red-700 hover:bg-red-200'
                                        }`}
                                      >
                                        ❌ Rejeter ce champ
                                      </button>
                                      <button
                                        onClick={() => handleGranularVote(key, 'approve')}
                                        className={`px-2 py-1 rounded text-xs ${
                                          granularVote === 'approve'
                                            ? 'bg-green-500 text-white'
                                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                                        }`}
                                      >
                                        ✅ Approuver ce champ
                                      </button>
                                    </div>
                                  )}
                                </div>
                                
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  {/* BEFORE */}
                                  <div className="bg-gray-50 rounded p-3">
                                    <p className="text-xs font-medium text-gray-600 mb-1">⬅️ AVANT (Actuel)</p>
                                    <div className={`p-2 bg-white rounded border text-sm ${
                                      fieldChanged ? 'border-red-200 text-red-700' : 'border-gray-200'
                                    }`}>
                                      {currentData ? formatValue(key, currentData[key]) : 'Loading...'}
                                    </div>
                                  </div>
                                  
                                  {/* AFTER */}
                                  <div className="bg-green-50 rounded p-3">
                                    <p className="text-xs font-medium text-gray-600 mb-1">➡️ APRÈS (Proposé)</p>
                                    <div className={`p-2 bg-white rounded border text-sm ${
                                      fieldChanged ? 'border-green-200 text-green-700 font-medium' : 'border-gray-200'
                                    }`}>
                                      {formatValue(key, proposedValue)}
                                      {fieldChanged && (
                                        <span className="ml-2 text-green-600 text-xs">✨ MODIFIÉ</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Enhanced Images Gallery */}
                    {contribution.images && Object.keys(contribution.images).length > 0 && (
                      <div className="mb-6">
                        <h3 className="font-semibold text-gray-900 mb-4">🖼️ Galerie d'images proposées</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                          {Object.entries(contribution.images).map(([imageKey, imageData], index) => {
                            const imageSrc = Array.isArray(imageData) ? imageData[0] : imageData;
                            return (
                              <div key={imageKey} className="bg-gray-50 rounded-lg p-2">
                                <div className="relative group">
                                  <img 
                                    src={imageSrc}
                                    alt={imageKey}
                                    className="w-full h-24 object-cover rounded border cursor-pointer hover:opacity-75 transition-opacity"
                                    onClick={() => {
                                      const allImages = Object.entries(contribution.images).map(([key, data]) => ({
                                        src: Array.isArray(data) ? data[0] : data,
                                        alt: getFieldLabel(key)
                                      }));
                                      setSelectedImageView({ images: allImages, selectedIndex: index });
                                    }}
                                  />
                                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all flex items-center justify-center">
                                    <span className="text-white text-sm font-medium opacity-0 group-hover:opacity-100">🔍 Zoom</span>
                                  </div>
                                </div>
                                <p className="text-xs text-gray-600 mt-1 text-center font-medium">{getFieldLabel(imageKey)}</p>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* HISTORY TAB */}
                {activeTab === 'history' && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-4">📈 Historique des modifications de cette entité</h3>
                    {entityHistory.length > 0 ? (
                      <div className="space-y-3">
                        {entityHistory.map((historyItem, index) => (
                          <div key={historyItem.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <h4 className="font-medium text-sm">{historyItem.title}</h4>
                                <p className="text-xs text-gray-600">Par {historyItem.contributor_name}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-xs text-gray-500">{new Date(historyItem.created_at).toLocaleDateString('fr-FR')}</p>
                                <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Approuvé</div>
                              </div>
                            </div>
                            {historyItem.description && (
                              <p className="text-xs text-gray-700 bg-gray-50 p-2 rounded">{historyItem.description}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>Aucune modification précédente pour cette entité</p>
                      </div>
                    )}
                  </div>
                )}

                {/* ANALYTICS TAB */}
                {activeTab === 'analytics' && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-4">🏆 Profil du contributeur</h3>
                    
                    {/* Contributor Reputation */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="font-semibold text-lg">{contribution.contributor_name || 'Anonyme'}</h4>
                          {(() => {
                            const reputation = getContributorReputation();
                            return (
                              <div className="flex items-center space-x-2">
                                <div className={`px-3 py-1 rounded-full text-sm font-bold bg-${reputation.color}-100 text-${reputation.color}-800`}>
                                  {reputation.level}
                                </div>
                                <span className="text-sm text-gray-600">{reputation.score}% de contributions approuvées</span>
                              </div>
                            );
                          })()}
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-gray-900">{contributorHistory.length}</p>
                          <p className="text-sm text-gray-600">contributions totales</p>
                        </div>
                      </div>
                      
                      {/* Reputation Stats */}
                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div>
                          <p className="text-xl font-bold text-green-600">
                            {contributorHistory.filter(c => c.status === 'approved').length}
                          </p>
                          <p className="text-xs text-gray-600">Approuvées</p>
                        </div>
                        <div>
                          <p className="text-xl font-bold text-red-600">
                            {contributorHistory.filter(c => c.status === 'rejected').length}
                          </p>
                          <p className="text-xs text-gray-600">Rejetées</p>
                        </div>
                        <div>
                          <p className="text-xl font-bold text-orange-600">
                            {contributorHistory.filter(c => c.status === 'pending').length}
                          </p>
                          <p className="text-xs text-gray-600">En attente</p>
                        </div>
                      </div>
                    </div>

                    {/* Recent Contributions */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Contributions récentes</h4>
                      <div className="space-y-2 max-h-40 overflow-y-auto">
                        {contributorHistory.slice(0, 5).map(item => (
                          <div key={item.id} className="flex justify-between items-center text-sm p-2 bg-gray-50 rounded">
                            <span className="truncate">{item.title}</span>
                            <div className={`px-2 py-1 rounded text-xs ${
                              item.status === 'approved' ? 'bg-green-100 text-green-800' :
                              item.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              'bg-orange-100 text-orange-800'
                            }`}>
                              {item.status}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer with advanced voting */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
            
            {/* Vote Comment Modal */}
            {showVoteComment && (
              <div className="mb-4 p-4 bg-white border border-gray-200 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">
                  💬 Commentaire de vote {pendingVoteType === 'upvote' ? '(Approbation)' : '(Rejet)'}
                </h4>
                <textarea
                  value={voteComments[pendingVoteType] || ''}
                  onChange={(e) => setVoteComments(prev => ({ ...prev, [pendingVoteType]: e.target.value }))}
                  placeholder="Expliquez votre décision (obligatoire pour justifier votre vote)..."
                  className="w-full p-2 border border-gray-300 rounded-md text-sm resize-none"
                  rows={3}
                />
                
                {/* Granular vote summary */}
                {Object.keys(granularVotes).length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded">
                    <p className="text-sm font-medium text-gray-700 mb-2">Votes par champ :</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(granularVotes).map(([field, vote]) => (
                        <span
                          key={field}
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            vote === 'approve' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {getFieldLabel(field)}: {vote === 'approve' ? '✅' : '❌'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end space-x-2 mt-3">
                  <button
                    onClick={() => {
                      setShowVoteComment(false);
                      setPendingVoteType(null);
                    }}
                    className="px-3 py-1 text-gray-600 hover:text-gray-800 text-sm"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={submitVoteWithComment}
                    className={`px-4 py-2 rounded font-medium text-sm ${
                      pendingVoteType === 'upvote'
                        ? 'bg-green-600 hover:bg-green-700 text-white'
                        : 'bg-red-600 hover:bg-red-700 text-white'
                    }`}
                  >
                    Confirmer le vote
                  </button>
                </div>
              </div>
            )}
            
            {!showVoteComment && (
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  <p>📊 Vote avec commentaire obligatoire</p>
                  {Object.keys(granularVotes).length > 0 && (
                    <p className="text-xs text-blue-600 mt-1">
                      {Object.keys(granularVotes).length} champ(s) évalué(s) individuellement
                    </p>
                  )}
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={onClose}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Fermer
                  </button>
                  <button
                    onClick={() => handleVoteWithComment('downvote')}
                    disabled={voting}
                    className="px-6 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg font-medium disabled:opacity-50 transition-colors flex items-center space-x-2"
                  >
                    <span>👎</span>
                    <span>{voting ? 'Vote...' : 'Rejeter avec commentaire'}</span>
                  </button>
                  <button
                    onClick={() => handleVoteWithComment('upvote')}
                    disabled={voting}
                    className="px-6 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg font-medium disabled:opacity-50 transition-colors flex items-center space-x-2"
                  >
                    <span>👍</span>
                    <span>{voting ? 'Vote...' : 'Approuver avec commentaire'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Image Zoom Modal with Gallery */}
      {selectedImageView && selectedImageView.images && (
        <ImageZoomModal 
          images={selectedImageView.images}
          selectedIndex={selectedImageView.selectedIndex}
          onClose={() => setSelectedImageView(null)}
          onNavigate={(newIndex) => {
            const clampedIndex = Math.max(0, Math.min(newIndex, selectedImageView.images.length - 1));
            setSelectedImageView(prev => ({ ...prev, selectedIndex: clampedIndex }));
          }}
        />
      )}
    </>
  );
};

export default ContributionDetailModal;