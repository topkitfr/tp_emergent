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
        'master_jersey': 'master-jerseys',
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

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            
            {/* Description */}
            {contribution.description && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <h3 className="font-medium text-blue-900 mb-2">💭 Justification du contributeur</h3>
                <p className="text-blue-800 text-sm">{contribution.description}</p>
              </div>
            )}

            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <>
                {/* BEFORE/AFTER Comparison */}
                {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold text-gray-900 mb-4">📊 Comparaison AVANT / APRÈS</h3>
                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      
                      {/* BEFORE Column */}
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-700 mb-3 flex items-center">
                          ⬅️ AVANT (Actuel)
                        </h4>
                        <div className="space-y-3">
                          {Object.entries(contribution.proposed_data).map(([key, proposedValue]) => (
                            <div key={`before-${key}`} className="flex flex-col">
                              <span className="text-xs font-medium text-gray-600 mb-1">
                                {getFieldLabel(key)}
                              </span>
                              <div className={`p-2 bg-white rounded border text-sm ${
                                hasChanged(key, proposedValue) ? 'border-red-200 bg-red-50' : 'border-gray-200'
                              }`}>
                                {currentData ? formatValue(key, currentData[key]) : 'Loading...'}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* AFTER Column */}
                      <div className="bg-green-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-700 mb-3 flex items-center">
                          ➡️ APRÈS (Proposé)
                        </h4>
                        <div className="space-y-3">
                          {Object.entries(contribution.proposed_data).map(([key, proposedValue]) => (
                            <div key={`after-${key}`} className="flex flex-col">
                              <span className="text-xs font-medium text-gray-600 mb-1">
                                {getFieldLabel(key)}
                              </span>
                              <div className={`p-2 bg-white rounded border text-sm ${
                                hasChanged(key, proposedValue) ? 'border-green-200 bg-green-50 font-medium' : 'border-gray-200'
                              }`}>
                                {formatValue(key, proposedValue)}
                                {hasChanged(key, proposedValue) && (
                                  <span className="ml-2 text-green-600 text-xs">✨ MODIFIÉ</span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Images Comparison */}
                {contribution.images && Object.keys(contribution.images).length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-semibold text-gray-900 mb-4">🖼️ Images proposées</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(contribution.images).map(([imageKey, imageData]) => {
                        const imageSrc = Array.isArray(imageData) ? imageData[0] : imageData;
                        return (
                          <div key={imageKey} className="bg-gray-50 rounded-lg p-4">
                            <h4 className="text-sm font-medium text-gray-700 mb-2 capitalize">
                              {getFieldLabel(imageKey)}
                            </h4>
                            <div className="relative">
                              <img 
                                src={imageSrc}
                                alt={imageKey}
                                className="w-full h-32 object-cover rounded border cursor-pointer hover:opacity-75 transition-opacity"
                                onClick={() => setSelectedImageView({ src: imageSrc, alt: imageKey })}
                              />
                              <div className="absolute top-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                                🔍 Cliquer pour agrandir
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Original Form Data */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-3">📋 Données du formulaire original</h3>
                  <div className="text-sm space-y-2">
                    <div><strong>ID Entité:</strong> {contribution.entity_id}</div>
                    <div><strong>Statut:</strong> {contribution.status}</div>
                    {contribution.source_urls && contribution.source_urls.length > 0 && (
                      <div>
                        <strong>Sources:</strong>
                        <ul className="list-disc list-inside ml-4 mt-1">
                          {contribution.source_urls.map((url, index) => (
                            <li key={index}>
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Footer with voting actions */}
          <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                Cette contribution nécessite votre vote pour être appliquée
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={() => onVote(contribution.id, 'downvote')}
                  disabled={voting}
                  className="px-6 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg font-medium disabled:opacity-50 transition-colors"
                >
                  {voting ? 'Vote...' : '👎 Rejeter'}
                </button>
                <button
                  onClick={() => onVote(contribution.id, 'upvote')}
                  disabled={voting}
                  className="px-6 py-2 bg-green-100 hover:bg-green-200 text-green-700 rounded-lg font-medium disabled:opacity-50 transition-colors"
                >
                  {voting ? 'Vote...' : '👍 Approuver'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Zoom Modal */}
      {selectedImageView && (
        <ImageZoomModal 
          src={selectedImageView.src}
          alt={selectedImageView.alt}
          onClose={() => setSelectedImageView(null)}
        />
      )}
    </>
  );
};

export default ContributionDetailModal;