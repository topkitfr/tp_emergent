import React, { useState, useEffect } from 'react';
import PaginationControls from './PaginationControls';
import JerseyDetailModal from './JerseyDetailModal';

const CollectionPage = ({ API }) => {
  const [collection, setCollection] = useState([]);
  const [filteredCollection, setFilteredCollection] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  
  // Filter states
  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: '',
    condition: '',
    size: ''
  });
  
  // Modal state
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadCollection();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [collection, filters]);

  const loadCollection = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/collections/my-owned`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCollection(data);
      }
    } catch (error) {
      console.error('Error loading collection:', error);
    }
    setLoading(false);
  };

  const applyFilters = () => {
    let filtered = [...collection];
    
    if (filters.league) {
      filtered = filtered.filter(item => 
        item.jersey?.league?.toLowerCase().includes(filters.league.toLowerCase())
      );
    }
    
    if (filters.team) {
      filtered = filtered.filter(item => 
        item.jersey?.team?.toLowerCase().includes(filters.team.toLowerCase())
      );
    }
    
    if (filters.season) {
      filtered = filtered.filter(item => 
        item.jersey?.season?.includes(filters.season)
      );
    }

    if (filters.condition) {
      filtered = filtered.filter(item => 
        item.condition?.toLowerCase().includes(filters.condition.toLowerCase())
      );
    }

    if (filters.size) {
      filtered = filtered.filter(item => 
        item.size?.toLowerCase().includes(filters.size.toLowerCase())
      );
    }
    
    setFilteredCollection(filtered);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleCollectionAction = async (action, jersey) => {
    switch (action) {
      case 'edit':
        // Open JerseyDetailEditor in collection-edit mode
        console.log('Edit collection item:', jersey);
        break;
      case 'remove':
        try {
          const response = await fetch(`${API_URL}/api/collections/${jersey.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          if (response.ok) {
            loadCollection(); // Reload collection
          }
        } catch (error) {
          console.error('Error removing from collection:', error);
        }
        break;
    }
    setShowModal(false);
  };

  const openJerseyModal = (item) => {
    // Merge jersey data with collection-specific data
    const jerseyWithCollection = {
      ...item.jersey,
      size: item.size,
      condition: item.condition,
      collection_id: item.id
    };
    setSelectedJersey(jerseyWithCollection);
    setShowModal(true);
  };

  // Pagination calculations
  const totalItems = filteredCollection.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentItems = filteredCollection.slice(startIndex, endIndex);

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Ma Collection</h1>
      
      {/* Filtres */}
      <div className="bg-white rounded-lg p-4 mb-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Championnat</label>
            <input
              type="text"
              value={filters.league}
              onChange={(e) => handleFilterChange('league', e.target.value)}
              placeholder="Ex: Ligue 1"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Équipe</label>
            <input
              type="text"
              value={filters.team}
              onChange={(e) => handleFilterChange('team', e.target.value)}
              placeholder="Ex: PSG"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Saison</label>
            <input
              type="text"
              value={filters.season}
              onChange={(e) => handleFilterChange('season', e.target.value)}
              placeholder="Ex: 2024/25"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Taille</label>
            <input
              type="text"
              value={filters.size}
              onChange={(e) => handleFilterChange('size', e.target.value)}
              placeholder="Ex: L"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">État</label>
            <input
              type="text"
              value={filters.condition}
              onChange={(e) => handleFilterChange('condition', e.target.value)}
              placeholder="Ex: excellent"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={() => setFilters({ league: '', team: '', season: '', condition: '', size: '' })}
            className="px-4 py-2 text-gray-600 hover:text-black transition-colors"
          >
            Réinitialiser les filtres
          </button>
        </div>
      </div>

      {/* Collection */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Chargement...</div>
        ) : currentItems.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            {collection.length === 0 ? 'Votre collection est vide' : 'Aucun résultat trouvé'}
          </div>
        ) : (
          <>
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {currentItems.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => openJerseyModal(item)}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                  >
                    <div className="aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center">
                      {(() => {
                        const jersey = item.jersey;
                        let imageUrl = null;
                        
                        if (jersey?.images && jersey.images.length > 0) {
                          const img = jersey.images[0];
                          imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                        } else if (jersey?.front_photo_url) {
                          const img = jersey.front_photo_url;
                          imageUrl = img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
                        }
                        
                        return imageUrl ? (
                          <img 
                            src={imageUrl}
                            alt={jersey?.team}
                            className="w-full h-full object-cover rounded-lg"
                            onError={(e) => {
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'flex';
                            }}
                          />
                        ) : (
                          <div className="text-4xl">👕</div>
                        );
                      })()}
                      <div className="w-full h-full flex items-center justify-center text-4xl" style={{display: 'none'}}>👕</div>
                    </div>
                    <h4 className="font-semibold text-sm mb-1">{item.jersey?.team}</h4>
                    <p className="text-xs text-gray-600 mb-2">
                      {item.jersey?.league} • {item.jersey?.season}
                    </p>
                    <div className="text-xs text-gray-500 space-y-1">
                      <div>Taille: <span className="font-medium">{item.size || 'Non renseignée'}</span></div>
                      <div>État: <span className="font-medium capitalize">{item.condition || 'Non renseigné'}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            {totalItems > itemsPerPage && (
              <PaginationControls
                currentPage={currentPage}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={setCurrentPage}
                onItemsPerPageChange={setItemsPerPage}
                itemName="maillots"
              />
            )}
          </>
        )}
      </div>

      {/* Modal détails */}
      <JerseyDetailModal
        jersey={selectedJersey}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        context="collection"
        onAction={handleCollectionAction}
      />
    </div>
  );
};

export default CollectionPage;