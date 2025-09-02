import React from 'react';

const JerseyDetailModal = ({ jersey, isOpen, onClose, context = 'explorer', onAction }) => {
  if (!isOpen || !jersey) return null;

  const getImageUrl = () => {
    if (jersey.images && jersey.images.length > 0) {
      const img = jersey.images[0];
      return img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
    }
    if (jersey.front_photo_url) {
      const img = jersey.front_photo_url;
      return img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
    }
    return null;
  };

  const getBackImageUrl = () => {
    if (jersey.images && jersey.images.length > 1) {
      const img = jersey.images[1];
      return img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
    }
    if (jersey.back_photo_url) {
      const img = jersey.back_photo_url;
      return img.startsWith('uploads/') ? `/${img}` : `/images/${img}`;
    }
    return null;
  };

  const renderActionButtons = () => {
    switch (context) {
      case 'explorer':
        return (
          <div className="flex gap-3">
            <button 
              onClick={() => onAction?.('addToWishlist', jersey)}
              className="flex-1 bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              ❤️ Ajouter à ma wishlist
            </button>
            <button 
              onClick={() => onAction?.('addToCollection', jersey)}
              className="flex-1 bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              📚 Add to my collection
            </button>
          </div>
        );
      case 'collection':
        return (
          <div className="flex gap-3">
            <button 
              onClick={() => onAction?.('edit', jersey)}
              className="flex-1 bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              ✏️ Edit
            </button>
            <button 
              onClick={() => onAction?.('remove', jersey)}
              className="flex-1 bg-red-100 text-red-800 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
            >
              🗑️ Remove
            </button>
          </div>
        );
      case 'wishlist':
        return (
          <div className="flex gap-3">
            <button 
              onClick={() => onAction?.('addToCollection', jersey)}
              className="flex-1 bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              📚 Add to my collection
            </button>
            <button 
              onClick={() => onAction?.('removeFromWishlist', jersey)}
              className="flex-1 bg-red-100 text-red-800 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors"
            >
              💔 Retirer de la wishlist
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">{jersey.team}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Images */}
            <div className="space-y-4">
              {getImageUrl() && (
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  <img 
                    src={getImageUrl()}
                    alt={`${jersey.team} face`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="w-full h-full flex items-center justify-center text-4xl" style={{display: 'none'}}>👕</div>
                </div>
              )}
              
              {getBackImageUrl() && (
                <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                  <img 
                    src={getBackImageUrl()}
                    alt={`${jersey.team} dos`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                  <div className="w-full h-full flex items-center justify-center text-4xl" style={{display: 'none'}}>👕</div>
                </div>
              )}
              
              {!getImageUrl() && (
                <div className="aspect-square bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-6xl">👕</div>
                </div>
              )}
            </div>

            {/* Informations */}
            <div className="space-y-6">
              {/* Informations principales */}
              <div>
                <h3 className="font-semibold text-lg mb-3">Informations</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Équipe:</span>
                    <span className="font-medium">{jersey.team}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Championnat:</span>
                    <span className="font-medium">{jersey.league}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Saison:</span>
                    <span className="font-medium">{jersey.season}</span>
                  </div>
                  {jersey.manufacturer && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Fabricant:</span>
                      <span className="font-medium">{jersey.manufacturer}</span>
                    </div>
                  )}
                  {jersey.jersey_type && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-medium capitalize">{jersey.jersey_type}</span>
                    </div>
                  )}
                  {jersey.model && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Modèle:</span>
                      <span className="font-medium capitalize">{jersey.model}</span>
                    </div>
                  )}
                  {jersey.sku_code && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Code SKU:</span>
                      <span className="font-medium">{jersey.sku_code}</span>
                    </div>
                  )}
                  {jersey.reference_number && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Référence:</span>
                      <span className="font-medium">{jersey.reference_number}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Description */}
              {jersey.description && (
                <div>
                  <h3 className="font-semibold text-lg mb-3">Description</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{jersey.description}</p>
                </div>
              )}

              {/* Détails collection si applicable */}
              {(jersey.size || jersey.condition) && (
                <div>
                  <h3 className="font-semibold text-lg mb-3">Ma collection</h3>
                  <div className="space-y-2 text-sm">
                    {jersey.size && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">Taille:</span>
                        <span className="font-medium">{jersey.size}</span>
                      </div>
                    )}
                    {jersey.condition && (
                      <div className="flex justify-between">
                        <span className="text-gray-600">État:</span>
                        <span className="font-medium capitalize">{jersey.condition}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Boutons d'action */}
              <div className="pt-4">
                {renderActionButtons()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JerseyDetailModal;