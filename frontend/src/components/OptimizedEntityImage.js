/**
 * Optimized Entity Image Component
 * Displays images for any entity type (teams, brands, players, etc.) using the optimized serving system
 */

import React, { useState, useEffect } from 'react';
import { getOptimizedImageUrl, getImageVariants } from '../utils/imageUpload';

const OptimizedEntityImage = ({ 
  entity,
  entityType,
  size = 'medium',
  className = '',
  fallbackSrc = null,
  showVariantSelector = false,
  alt = '',
  lazy = true
}) => {
  const [currentSize, setCurrentSize] = useState(size);
  const [variants, setVariants] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);

  // Determine image source from entity
  useEffect(() => {
    let primaryImageUrl = null;
    
    // Check different possible image field names
    if (entity?.logo_url) {
      primaryImageUrl = entity.logo_url;
    } else if (entity?.image_url) {
      primaryImageUrl = entity.image_url;
    } else if (entity?.photo_url) {
      primaryImageUrl = entity.photo_url;
    } else if (entity?.logo) {
      primaryImageUrl = entity.logo;
    } else if (entity?.image) {
      primaryImageUrl = entity.image;
    }

    if (primaryImageUrl) {
      // Check if it's already an optimized URL
      if (primaryImageUrl.includes('/api/serve-image/')) {
        setImageUrl(primaryImageUrl);
      } else if (primaryImageUrl.includes('uploads/')) {
        // Extract filename from uploads path and convert to optimized URL
        const pathParts = primaryImageUrl.split('/');
        const filename = pathParts[pathParts.length - 1];
        const optimizedUrl = getOptimizedImageUrl(entityType, filename, currentSize);
        setImageUrl(optimizedUrl);
      } else {
        // Use original URL if not an uploads path
        setImageUrl(primaryImageUrl);
      }
    } else if (fallbackSrc) {
      setImageUrl(fallbackSrc);
    }

    // Load variants if requested
    if (showVariantSelector && primaryImageUrl && primaryImageUrl.includes('uploads/')) {
      const pathParts = primaryImageUrl.split('/');
      const filename = pathParts[pathParts.length - 1];
      
      getImageVariants(entityType, filename)
        .then(data => {
          if (data && data.variants) {
            setVariants(data.variants);
          }
        })
        .catch(err => {
          console.error('Failed to load variants:', err);
        });
    }
  }, [entity, entityType, currentSize, fallbackSrc, showVariantSelector]);

  const handleSizeChange = (newSize) => {
    setCurrentSize(newSize);
    
    // Update image URL for new size
    if (entity?.logo_url || entity?.image_url) {
      const primaryImageUrl = entity.logo_url || entity.image_url;
      if (primaryImageUrl.includes('uploads/')) {
        const pathParts = primaryImageUrl.split('/');
        const filename = pathParts[pathParts.length - 1];
        const optimizedUrl = getOptimizedImageUrl(entityType, filename, newSize);
        setImageUrl(optimizedUrl);
      }
    }
  };

  const handleImageLoad = () => {
    setLoading(false);
    setError(false);
  };

  const handleImageError = () => {
    setLoading(false);
    setError(true);
    
    // Try fallback if available
    if (fallbackSrc && imageUrl !== fallbackSrc) {
      setImageUrl(fallbackSrc);
      setError(false);
      setLoading(true);
    }
  };

  const sizeLabels = {
    thumbnail: 'Thumbnail (150px)',
    small: 'Small (300px)', 
    medium: 'Medium (600px)',
    large: 'Large (1200px)',
    original: 'Original'
  };

  if (!imageUrl) {
    return (
      <div className={`bg-gray-100 rounded flex items-center justify-center ${className}`}>
        <span className="text-gray-400 text-sm">No image</span>
      </div>
    );
  }

  return (
    <div className="relative">
      {loading && (
        <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
      )}
      
      {error ? (
        <div className={`bg-gray-100 rounded flex items-center justify-center ${className}`}>
          <span className="text-gray-400 text-xs">Failed to load</span>
        </div>
      ) : (
        <img
          src={imageUrl}
          alt={alt || `${entityType} image`}
          className={`${className} ${loading ? 'opacity-0' : 'opacity-100'} transition-opacity`}
          onLoad={handleImageLoad}
          onError={handleImageError}
          loading={lazy ? 'lazy' : 'eager'}
        />
      )}

      {/* Variant Selector */}
      {showVariantSelector && variants && Object.keys(variants).length > 1 && (
        <div className="absolute top-2 right-2 bg-white bg-opacity-90 rounded px-2 py-1">
          <select
            value={currentSize}
            onChange={(e) => handleSizeChange(e.target.value)}
            className="text-xs border-none bg-transparent focus:outline-none"
          >
            {Object.keys(variants).map(sizeKey => (
              <option key={sizeKey} value={sizeKey}>
                {sizeLabels[sizeKey] || sizeKey}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Optimization Badge */}
      {imageUrl && imageUrl.includes('/api/serve-image/') && (
        <div className="absolute bottom-1 left-1 bg-green-500 text-white text-xs px-1 rounded opacity-75">
          ⚡
        </div>
      )}
    </div>
  );
};

export default OptimizedEntityImage;