/**
 * Enhanced Image Upload Utility
 * Integrates with the new optimized backend image processing system
 */

const API_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;

/**
 * Upload image using the optimized backend endpoint
 * @param {File} file - The image file to upload
 * @param {string} entityType - The entity type (team, brand, player, competition, master_jersey)
 * @param {boolean} generateVariants - Whether to generate multiple size variants
 * @param {function} onProgress - Progress callback function
 * @returns {Promise<Object>} Upload result with image URLs and metadata
 */
export const uploadOptimizedImage = async (file, entityType, generateVariants = true, onProgress = null) => {
  try {
    // Validate inputs
    if (!file) {
      throw new Error('No file provided');
    }

    if (!['team', 'brand', 'player', 'competition', 'master_jersey'].includes(entityType)) {
      throw new Error('Invalid entity type');
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Unsupported file format. Please use JPG, PNG, WebP, or BMP.');
    }

    // Validate file size (15MB limit)
    const maxSize = 15 * 1024 * 1024; // 15MB
    if (file.size > maxSize) {
      throw new Error('File too large. Maximum size is 15MB.');
    }

    // Get authentication token
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Authentication required');
    }

    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entity_type', entityType);
    formData.append('generate_variants', generateVariants);

    // Progress tracking
    if (onProgress) {
      onProgress({ phase: 'uploading', progress: 0 });
    }

    // Make request with progress tracking
    const response = await fetch(`${API_URL}/api/upload/image`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    if (onProgress) {
      onProgress({ phase: 'processing', progress: 50 });
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Upload failed: ${response.status}`);
    }

    const result = await response.json();

    if (onProgress) {
      onProgress({ phase: 'complete', progress: 100 });
    }

    return {
      success: true,
      data: result,
      mainImageUrl: result.image_url,
      variants: result.variants || {},
      metadata: result.metadata || {},
      optimizationApplied: result.optimization_applied || false,
      variantsCount: result.variants_count || 0
    };

  } catch (error) {
    console.error('Image upload error:', error);
    
    if (onProgress) {
      onProgress({ phase: 'error', progress: 0, error: error.message });
    }

    return {
      success: false,
      error: error.message
    };
  }
};

/**
 * Generate optimized image URL for serving
 * @param {string} entityType - The entity type 
 * @param {string} filename - The filename
 * @param {string} size - The desired size variant
 * @returns {string} Optimized image URL
 */
export const getOptimizedImageUrl = (entityType, filename, size = 'medium') => {
  if (!entityType || !filename) {
    return null;
  }

  // Normalize entity type (remove 's' if present)
  const normalizedEntityType = entityType.endsWith('s') ? entityType.slice(0, -1) : entityType;
  
  return `${API_URL}/api/serve-image/${normalizedEntityType}/${filename}?size=${size}`;
};

/**
 * Get all available variants for an image
 * @param {string} entityType - The entity type
 * @param {string} filename - The filename
 * @returns {Promise<Object>} Image variants information
 */
export const getImageVariants = async (entityType, filename) => {
  try {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('Authentication required');
    }

    const normalizedEntityType = entityType.endsWith('s') ? entityType.slice(0, -1) : entityType;
    
    const response = await fetch(`${API_URL}/api/image-info/${normalizedEntityType}/${filename}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to get image info: ${response.status}`);
    }

    return await response.json();

  } catch (error) {
    console.error('Error getting image variants:', error);
    return null;
  }
};

/**
 * Image upload component with progress feedback and optimization info
 */
export const ImageUploadProgress = ({ progress, phase, error, metadata }) => {
  const getPhaseMessage = () => {
    switch (phase) {
      case 'uploading':
        return 'Uploading image...';
      case 'processing':
        return 'Optimizing and generating variants...';
      case 'complete':
        return 'Upload complete!';
      case 'error':
        return `Error: ${error}`;
      default:
        return 'Preparing upload...';
    }
  };

  const getProgressColor = () => {
    switch (phase) {
      case 'complete':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="mt-2">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>{getPhaseMessage()}</span>
        <span>{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${getProgressColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>
      
      {phase === 'complete' && metadata && (
        <div className="mt-2 text-xs text-green-600">
          <div>✅ Optimized: {metadata.width}×{metadata.height}px</div>
          {metadata.format && <div>✅ Format: {metadata.format}</div>}
          {metadata.file_size && (
            <div>✅ Size: {(metadata.file_size / 1024).toFixed(1)}KB</div>
          )}
        </div>
      )}
      
      {phase === 'error' && (
        <div className="mt-1 text-xs text-red-600">
          ❌ {error}
        </div>
      )}
    </div>
  );
};

/**
 * Image variant selector component
 */
export const ImageVariantSelector = ({ variants, currentSize, onSizeChange, className = "" }) => {
  const sizeLabels = {
    thumbnail: 'Thumbnail (150px)',
    small: 'Small (300px)',
    medium: 'Medium (600px)',
    large: 'Large (1200px)',
    original: 'Original'
  };

  if (!variants || Object.keys(variants).length <= 1) {
    return null;
  }

  return (
    <div className={`mt-2 ${className}`}>
      <label className="block text-xs font-medium text-gray-700 mb-1">
        Image Size:
      </label>
      <select
        value={currentSize}
        onChange={(e) => onSizeChange(e.target.value)}
        className="text-xs border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        {Object.keys(variants).map(size => (
          <option key={size} value={size}>
            {sizeLabels[size] || size}
          </option>
        ))}
      </select>
    </div>
  );
};

/**
 * Optimized image component with lazy loading and variant selection
 */
export const OptimizedImage = ({ 
  entityType, 
  filename, 
  size = 'medium',
  alt = '',
  className = '',
  showVariantSelector = false,
  onVariantChange = null
}) => {
  const [currentSize, setCurrentSize] = useState(size);
  const [variants, setVariants] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (showVariantSelector && entityType && filename) {
      getImageVariants(entityType, filename)
        .then(data => {
          if (data && data.variants) {
            setVariants(data.variants);
          }
        })
        .catch(err => {
          console.error('Failed to load image variants:', err);
        });
    }
  }, [entityType, filename, showVariantSelector]);

  const handleSizeChange = (newSize) => {
    setCurrentSize(newSize);
    if (onVariantChange) {
      onVariantChange(newSize);
    }
  };

  if (!entityType || !filename) {
    return null;
  }

  const imageUrl = getOptimizedImageUrl(entityType, filename, currentSize);

  return (
    <div>
      <img
        src={imageUrl}
        alt={alt}
        className={className}
        onLoad={() => setLoading(false)}
        onError={() => {
          setError(true);
          setLoading(false);
        }}
        loading="lazy"
      />
      
      {showVariantSelector && variants && (
        <ImageVariantSelector
          variants={variants}
          currentSize={currentSize}
          onSizeChange={handleSizeChange}
        />
      )}
      
      {loading && (
        <div className="animate-pulse bg-gray-200 rounded" style={{width: '100%', height: '100px'}} />
      )}
      
      {error && (
        <div className="bg-gray-100 rounded p-4 text-center text-gray-500">
          Failed to load image
        </div>
      )}
    </div>
  );
};

// Import React hooks
import { useState, useEffect } from 'react';