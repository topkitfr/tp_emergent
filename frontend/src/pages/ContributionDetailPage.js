import React, { useState, useEffect } from 'react';

const ContributionDetailPage = ({ contributionId, user, API, onNavigateBack }) => {
  const [contribution, setContribution] = useState(null);
  const [currentData, setCurrentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [expandedImage, setExpandedImage] = useState(null);
  const [contributorHistory, setContributorHistory] = useState([]);
  const [entityHistory, setEntityHistory] = useState([]);
  const [voteComment, setVoteComment] = useState('');
  const [showVoteDialog, setShowVoteDialog] = useState(false);
  const [pendingVoteType, setPendingVoteType] = useState(null);
  const [fieldVotes, setFieldVotes] = useState({});

  useEffect(() => {
    if (contributionId) {
      loadContributionDetails();
    }
  }, [contributionId]);

  const loadContributionDetails = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      // Load contribution details
      const contributionResponse = await fetch(`${API}/api/contributions-v2/${contributionId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (contributionResponse.ok) {
        const contributionData = await contributionResponse.json();
        setContribution(contributionData);

        // Load current entity data
        await loadCurrentEntityData(contributionData);
        
        // Load contributor history
        await loadContributorHistory(contributionData.contributor_id);
        
        // Load entity modification history
        await loadEntityHistory(contributionData.entity_id, contributionData.entity_type);
      }
    } catch (error) {
      console.error('Error loading contribution details:', error);
    }
    setLoading(false);
  };

  const loadCurrentEntityData = async (contribution) => {
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
  };

  const loadContributorHistory = async (contributorId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/contributions?contributor_id=${contributorId}&limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setContributorHistory(data);
      }
    } catch (error) {
      console.error('Error loading contributor history:', error);
    }
  };

  const loadEntityHistory = async (entityId, entityType) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/contributions?entity_id=${entityId}&entity_type=${entityType}&status=approved&limit=10`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEntityHistory(data);
      }
    } catch (error) {
      console.error('Error loading entity history:', error);
    }
  };

  const formatFieldName = (field) => {
    const fieldNames = {
      name: 'Nom',
      short_name: 'Nom court',
      city: 'Ville',
      country: 'Pays',
      founded_year: 'Année de fondation',
      colors: 'Couleurs',
      logo_url: 'URL du logo',
      official_name: 'Nom officiel',
      competition_type: 'Type de compétition',
      level: 'Niveau',
      website: 'Site web',
      nationality: 'Nationalité',
      position: 'Position',
      birth_date: 'Date de naissance'
    };
    return fieldNames[field] || field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatValue = (value) => {
    if (Array.isArray(value)) return value.join(', ');
    if (value === null || value === undefined || value === '') return 'Non spécifié';
    return String(value);
  };

  const hasChanged = (field, proposedValue) => {
    if (!currentData) return true;
    const currentValue = currentData[field];
    
    if (Array.isArray(proposedValue) && Array.isArray(currentValue)) {
      return JSON.stringify(proposedValue.sort()) !== JSON.stringify(currentValue.sort());
    }
    
    return currentValue !== proposedValue;
  };

  const handleFieldVote = (field, voteType) => {
    setFieldVotes(prev => ({
      ...prev,
      [field]: voteType
    }));
  };

  const handleOverallVote = (voteType) => {
    setPendingVoteType(voteType);
    setShowVoteDialog(true);
  };

  const submitVote = async () => {
    if (!voteComment.trim()) {
      alert('Veuillez ajouter un commentaire pour justifier votre vote');
      return;
    }

    setVoting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/api/contributions-v2/${contribution.id}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          vote_type: pendingVoteType,
          comment: voteComment,
          field_votes: fieldVotes
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message || 'Vote enregistré avec succès!');
        await loadContributionDetails(); // Reload to show updated data
        setShowVoteDialog(false);
        setVoteComment('');
        setPendingVoteType(null);
        setFieldVotes({});
      } else {
        const error = await response.text();
        alert(`Erreur lors du vote: ${error}`);
      }
    } catch (error) {
      console.error('Error submitting vote:', error);
      alert('Une erreur est survenue lors du vote');
    } finally {
      setVoting(false);
    }
  };

  const getEntityTypeConfig = (entityType) => {
    const configs = {
      team: { icon: '⚽', label: 'Équipe', color: 'blue' },
      brand: { icon: '👕', label: 'Marque', color: 'purple' },
      player: { icon: '🏃', label: 'Joueur', color: 'green' },
      competition: { icon: '🏆', label: 'Compétition', color: 'yellow' },
      master_jersey: { icon: '👕', label: 'Master Jersey', color: 'red' },
      jersey_release: { icon: '📦', label: 'Jersey Release', color: 'cyan' }
    };
    return configs[entityType] || { icon: '📄', label: entityType, color: 'gray' };
  };

  const getContributorStats = () => {
    const approved = contributorHistory.filter(c => c.status === 'approved').length;
    const rejected = contributorHistory.filter(c => c.status === 'rejected').length;
    const pending = contributorHistory.filter(c => c.status === 'pending').length;
    const total = contributorHistory.length;
    const successRate = total > 0 ? Math.round((approved / total) * 100) : 0;

    let level = 'Nouveau';
    let levelColor = 'gray';
    
    if (total >= 10 && successRate >= 90) {
      level = 'Expert';
      levelColor = 'purple';
    } else if (total >= 5 && successRate >= 80) {
      level = 'Expérimenté';
      levelColor = 'blue';
    } else if (total >= 3 && successRate >= 70) {
      level = 'Confirmé';
      levelColor = 'green';
    } else if (total >= 1 && successRate >= 50) {
      level = 'Apprenti';
      levelColor = 'yellow';
    } else if (total >= 1) {
      level = 'Débutant';
      levelColor = 'red';
    }

    return {
      approved,
      rejected,
      pending,
      total,
      successRate,
      level,
      levelColor
    };
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Chargement de la contribution...</span>
        </div>
      </div>
    );
  }

  if (!contribution) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">❌</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Contribution non trouvée</h3>
          <p className="text-gray-600 mb-4">Cette contribution n'existe pas ou vous n'avez pas les droits pour la consulter.</p>
          <button
            onClick={onNavigateBack}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retour aux contributions
          </button>
        </div>
      </div>
    );
  }

  const entityConfig = getEntityTypeConfig(contribution.entity_type);
  const contributorStats = getContributorStats();

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <button
            onClick={onNavigateBack}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <span>←</span>
            <span>Retour aux contributions</span>
          </button>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-${entityConfig.color}-100 text-${entityConfig.color}-800`}>
                  {entityConfig.icon} {entityConfig.label}
                </span>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  contribution.status === 'pending' ? 'bg-orange-100 text-orange-800' :
                  contribution.status === 'approved' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {contribution.status === 'pending' ? '⏳ En attente' :
                   contribution.status === 'approved' ? '✅ Approuvée' :
                   '❌ Rejetée'}
                </span>
              </div>
              
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {contribution.title || contribution.entity_name}
              </h1>
              
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full overflow-hidden">
                    {contribution.user_profile_picture ? (
                      <img 
                        src={`${API}/${contribution.user_profile_picture}`}
                        alt="Profile"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-white">
                          {contribution.user_name?.charAt(0).toUpperCase() || 'U'}
                        </span>
                      </div>
                    )}
                  </div>
                  <span>par {contribution.user_name}</span>
                </div>
                <span>•</span>
                <span>{new Date(contribution.created_at).toLocaleDateString('fr-FR', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}</span>
                <span>•</span>
                <span className="text-gray-500">Réf: {contribution.topkit_reference || contribution.id}</span>
              </div>
            </div>
            
            <div className="text-right">
              <div className="flex items-center space-x-4 mb-2">
                <div className="text-center">
                  <div className="text-lg font-bold text-green-600">{contribution.upvotes || 0}</div>
                  <div className="text-xs text-gray-500">👍 Positifs</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold text-red-600">{contribution.downvotes || 0}</div>
                  <div className="text-xs text-gray-500">👎 Négatifs</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-blue-600">{contribution.vote_score || 0}</div>
                  <div className="text-xs text-gray-500">Score final</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-gray-200 mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Comparaison AVANT/APRÈS
            </button>
            
            {contribution.images && Object.keys(contribution.images).length > 0 && (
              <button
                onClick={() => setActiveTab('images')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'images'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📸 Galerie d'images ({Object.keys(contribution.images).length})
              </button>
            )}
            
            <button
              onClick={() => setActiveTab('contributor')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'contributor'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🏆 Profil contributeur
            </button>
            
            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📈 Historique entité ({entityHistory.length})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Description */}
              {contribution.description && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900 mb-2">💬 Justification du contributeur</h3>
                  <p className="text-blue-800">{contribution.description}</p>
                </div>
              )}

              {/* Sources */}
              {contribution.source_urls && contribution.source_urls.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">🔗 Sources de validation ({contribution.source_urls.length})</h3>
                  <div className="space-y-2">
                    {contribution.source_urls.map((url, index) => (
                      <a 
                        key={index}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block bg-gray-50 text-blue-600 text-sm p-3 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        🌐 {url}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Field Comparisons */}
              {contribution.proposed_data && Object.keys(contribution.proposed_data).length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">📊 Comparaison détaillée des champs</h3>
                  <div className="space-y-4">
                    {Object.entries(contribution.proposed_data).map(([field, proposedValue]) => {
                      const fieldChanged = hasChanged(field, proposedValue);
                      const fieldVote = fieldVotes[field];
                      const currentValue = currentData?.[field];

                      return (
                        <div key={field} className={`border rounded-lg overflow-hidden ${
                          fieldChanged ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'
                        }`}>
                          {/* Field Header */}
                          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                              <h4 className="font-medium text-gray-900">{formatFieldName(field)}</h4>
                              <div className="flex items-center space-x-3">
                                {fieldChanged && (
                                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">
                                    Modifié
                                  </span>
                                )}
                                {contribution.status === 'pending' && fieldChanged && (
                                  <div className="flex space-x-1">
                                    <button
                                      onClick={() => handleFieldVote(field, 'reject')}
                                      className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                        fieldVote === 'reject'
                                          ? 'bg-red-600 text-white'
                                          : 'bg-red-100 text-red-700 hover:bg-red-200'
                                      }`}
                                    >
                                      ❌ Rejeter ce champ
                                    </button>
                                    <button
                                      onClick={() => handleFieldVote(field, 'approve')}
                                      className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                                        fieldVote === 'approve'
                                          ? 'bg-green-600 text-white'
                                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                                      }`}
                                    >
                                      ✅ Approuver ce champ
                                    </button>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Before/After Comparison */}
                          <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-200">
                            {/* Current/Before */}
                            <div className="p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                  ⬅️ AVANT (Actuel)
                                </span>
                              </div>
                              <div className={`p-4 rounded border ${
                                fieldChanged ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'
                              }`}>
                                <div className={`text-sm ${
                                  fieldChanged ? 'text-red-700' : 'text-gray-700'
                                }`}>
                                  {formatValue(currentValue)}
                                </div>
                              </div>
                            </div>

                            {/* Proposed/After */}
                            <div className="p-4">
                              <div className="flex items-center gap-2 mb-3">
                                <span className={`text-xs font-medium px-2 py-1 rounded ${
                                  fieldChanged 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-blue-100 text-blue-800'
                                }`}>
                                  ➡️ APRÈS (Proposé)
                                </span>
                                {fieldChanged && (
                                  <span className="text-green-600 text-xs font-medium">✨ MODIFIÉ</span>
                                )}
                              </div>
                              <div className={`p-4 rounded border ${
                                fieldChanged 
                                  ? 'bg-green-50 border-green-200' 
                                  : 'bg-blue-50 border-blue-200'
                              }`}>
                                <div className={`text-sm font-medium ${
                                  fieldChanged 
                                    ? 'text-green-700' 
                                    : 'text-blue-700'
                                }`}>
                                  {formatValue(proposedValue)}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'images' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-gray-900">📸 Galerie d'images proposées</h3>
                <span className="text-sm text-gray-500">
                  {contribution.images ? Object.keys(contribution.images).length : 0} image{contribution.images && Object.keys(contribution.images).length !== 1 ? 's' : ''}
                </span>
              </div>
              {contribution.images && Object.keys(contribution.images).length > 0 ? (
                <div className="space-y-6">
                  {/* Main Gallery Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {Object.entries(contribution.images).map(([imageType, imageData], index) => {
                      const imageUrl = Array.isArray(imageData) ? imageData[0] : imageData;
                      // Construct proper image URL - API already includes /api prefix
                      const imageSrc = imageUrl.startsWith('http') ? imageUrl : `${API}/${imageUrl}`;
                      return (
                        <div key={imageType} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-200">
                          <div className="aspect-w-1 aspect-h-1 relative">
                            <img 
                              src={imageSrc}
                              alt={formatFieldName(imageType)}
                              className="w-full h-64 object-cover cursor-pointer hover:scale-105 transition-transform duration-200"
                              onClick={() => setExpandedImage({ src: imageSrc, alt: formatFieldName(imageType) })}
                              onError={(e) => {
                                console.warn(`Failed to load image: ${imageSrc}`);
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                              }}
                            />
                            {/* Fallback for failed images */}
                            <div 
                              className="w-full h-64 bg-gray-100 flex items-center justify-center text-gray-400 hidden"
                              style={{ display: 'none' }}
                            >
                              <div className="text-center">
                                <div className="text-4xl mb-2">📷</div>
                                <p className="text-sm">Image non disponible</p>
                              </div>
                            </div>
                            {/* Image type badge */}
                            <div className="absolute top-3 left-3">
                              <span className="bg-black bg-opacity-60 text-white text-xs px-2 py-1 rounded-md font-medium">
                                {formatFieldName(imageType)}
                              </span>
                            </div>
                            {/* Click to expand hint */}
                            <div className="absolute bottom-3 right-3">
                              <div className="bg-black bg-opacity-60 text-white rounded-full p-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                                </svg>
                              </div>
                            </div>
                          </div>
                          <div className="p-4">
                            <h4 className="font-medium text-gray-900 text-center">{formatFieldName(imageType)}</h4>
                            <p className="text-sm text-gray-500 text-center mt-1">Cliquez pour agrandir</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Image Actions */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-sm text-blue-800">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span>Cliquez sur une image pour l'afficher en plein écran. Les images sont proposées pour améliorer le profil de l'entité.</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <div className="text-6xl mb-4 text-gray-400">📷</div>
                  <h4 className="text-lg font-medium text-gray-900 mb-2">Aucune image proposée</h4>
                  <p className="text-gray-600">Cette contribution ne contient pas d'images.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'contributor' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {contribution.user_name}
                    </h3>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${contributorStats.levelColor}-100 text-${contributorStats.levelColor}-800`}>
                        {contributorStats.level}
                      </span>
                      <span className="text-sm text-gray-600">
                        {contributorStats.successRate}% de contributions approuvées
                      </span>
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-900">{contributorStats.total}</div>
                    <div className="text-sm text-gray-600">contributions totales</div>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-2xl font-bold text-green-600">{contributorStats.approved}</div>
                    <div className="text-sm text-gray-600">Approuvées</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-red-600">{contributorStats.rejected}</div>
                    <div className="text-sm text-gray-600">Rejetées</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-orange-600">{contributorStats.pending}</div>
                    <div className="text-sm text-gray-600">En attente</div>
                  </div>
                </div>
              </div>

              {/* Recent Contributions */}
              <div>
                <h4 className="font-medium text-gray-900 mb-4">Contributions récentes</h4>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {contributorHistory.slice(0, 10).map(item => (
                    <div key={item.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm text-gray-900 truncate">{item.title}</p>
                        <p className="text-xs text-gray-600">
                          {new Date(item.created_at).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ml-2 ${
                        item.status === 'approved' ? 'bg-green-100 text-green-800' :
                        item.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        'bg-orange-100 text-orange-800'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="space-y-6">
              <h3 className="font-semibold text-gray-900">📈 Historique des modifications de cette entité</h3>
              {entityHistory.length > 0 ? (
                <div className="space-y-4">
                  {entityHistory.map(item => (
                    <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-medium text-gray-900">{item.title}</h4>
                          <p className="text-sm text-gray-600">par {item.contributor_name || item.user_name}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">
                            {new Date(item.created_at).toLocaleDateString('fr-FR')}
                          </p>
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-medium">
                            Approuvé
                          </span>
                        </div>
                      </div>
                      {item.description && (
                        <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded mt-2">
                          {item.description}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-4">📅</div>
                  <p>Aucune modification précédente pour cette entité</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Voting Section */}
      {contribution.status === 'pending' && user && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">🗳️ Voter sur cette contribution</h3>
          
          {/* Field Votes Summary */}
          {Object.keys(fieldVotes).length > 0 && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-900 mb-2">Votes par champ :</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(fieldVotes).map(([field, vote]) => (
                  <span
                    key={field}
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      vote === 'approve' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {formatFieldName(field)}: {vote === 'approve' ? '✅' : '❌'}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          <div className="flex space-x-4">
            <button
              onClick={() => handleOverallVote('downvote')}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              👎 Rejeter la contribution
            </button>
            <button
              onClick={() => handleOverallVote('upvote')}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
            >
              👍 Approuver la contribution
            </button>
          </div>
        </div>
      )}

      {/* Vote Dialog */}
      {showVoteDialog && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowVoteDialog(false)}></div>
            
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  💬 Commentaire de vote {pendingVoteType === 'upvote' ? '(Approbation)' : '(Rejet)'}
                </h3>
                <textarea
                  value={voteComment}
                  onChange={(e) => setVoteComment(e.target.value)}
                  placeholder="Expliquez votre décision (obligatoire pour justifier votre vote)..."
                  className="w-full p-3 border border-gray-300 rounded-md resize-none"
                  rows={4}
                />
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  onClick={submitVote}
                  disabled={voting || !voteComment.trim()}
                  className={`w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 ${
                    pendingVoteType === 'upvote'
                      ? 'bg-green-600 hover:bg-green-700'
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {voting ? 'Vote en cours...' : 'Confirmer le vote'}
                </button>
                <button
                  onClick={() => setShowVoteDialog(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 sm:mt-0 sm:mr-3 sm:w-auto sm:text-sm"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Image Expansion Modal */}
      {expandedImage && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center p-4" onClick={() => setExpandedImage(null)}>
          <div className="relative max-w-6xl max-h-full">
            <img 
              src={expandedImage.src}
              alt={expandedImage.alt}
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute top-4 right-4">
              <button
                onClick={() => setExpandedImage(null)}
                className="bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75 transition-opacity"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="absolute bottom-4 left-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded">
              {expandedImage.alt}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContributionDetailPage;