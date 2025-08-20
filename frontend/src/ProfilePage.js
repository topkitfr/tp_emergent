import React, { useState, useEffect } from 'react';
import PaginationControls from './PaginationControls';
import JerseyDetailModal from './JerseyDetailModal';

const ProfilePage = ({ user, API }) => {
  const [activeTab, setActiveTab] = useState('info');
  const [wishlist, setWishlist] = useState([]);
  const [filteredWishlist, setFilteredWishlist] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  
  // Filter states
  const [filters, setFilters] = useState({
    league: '',
    team: '',
    season: ''
  });
  
  // Modal state
  const [selectedJersey, setSelectedJersey] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (activeTab === 'wishlist') {
      loadWishlist();
    }
  }, [activeTab]);

  useEffect(() => {
    applyFilters();
  }, [wishlist, filters]);

  const loadWishlist = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/wishlist`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setWishlist(data);
      }
    } catch (error) {
      console.error('Error loading wishlist:', error);
    }
    setLoading(false);
  };

  const applyFilters = () => {
    let filtered = [...wishlist];
    
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
    
    setFilteredWishlist(filtered);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleWishlistAction = async (action, jersey) => {
    switch (action) {
      case 'addToCollection':
        // Logic to add to collection
        console.log('Add to collection:', jersey);
        break;
      case 'removeFromWishlist':
        try {
          const response = await fetch(`${API}/api/wishlist/${jersey.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          });
          if (response.ok) {
            loadWishlist(); // Reload wishlist
          }
        } catch (error) {
          console.error('Error removing from wishlist:', error);
        }
        break;
    }
    setShowModal(false);
  };

  const openJerseyModal = (jersey) => {
    setSelectedJersey(jersey);
    setShowModal(true);
  };

  // Pagination calculations
  const totalItems = filteredWishlist.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentItems = filteredWishlist.slice(startIndex, endIndex);

  const renderInfoTab = () => (
    <div className="bg-white rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">Informations personnelles</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nom</label>
          <div className="text-gray-900">{user?.name || 'Non renseigné'}</div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <div className="text-gray-900">{user?.email || 'Non renseigné'}</div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
          <div className="text-gray-900 capitalize">{user?.role || 'Non renseigné'}</div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Membre depuis</label>
          <div className="text-gray-900">
            {user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR') : 'Non renseigné'}
          </div>
        </div>
      </div>
    </div>
  );

  const renderWishlistTab = () => (
    <div className="space-y-4">
      {/* Filtres */}
      <div className="bg-white rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Filtres</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
        </div>
      </div>

      {/* Liste wishlist */}
      <div className="bg-white rounded-lg">
        {loading ? (
          <div className="p-8 text-center text-gray-500">Chargement...</div>
        ) : currentItems.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            {wishlist.length === 0 ? 'Votre wishlist est vide' : 'Aucun résultat trouvé'}
          </div>
        ) : (
          <>
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {currentItems.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => openJerseyModal(item.jersey)}
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
                    <p className="text-xs text-gray-600">
                      {item.jersey?.league} • {item.jersey?.season}
                    </p>
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
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Mon Profil</h1>
      
      {/* Onglets */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('info')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'info'
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              👤 Informations
            </button>
            <button
              onClick={() => setActiveTab('wishlist')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'wishlist'
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              ❤️ Ma Wishlist
            </button>
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'info' && renderInfoTab()}
      {activeTab === 'wishlist' && renderWishlistTab()}

      {/* Modal détails */}
      <JerseyDetailModal
        jersey={selectedJersey}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        context="wishlist"
        onAction={handleWishlistAction}
      />
    </div>
  );
};

export default ProfilePage;