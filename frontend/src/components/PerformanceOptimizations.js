import React, { createContext, useContext, useState, useEffect } from 'react';

// Cache Management
class ImageCache {
  constructor() {
    this.cache = new Map();
    this.maxSize = 50; // Maximum number of cached images
  }

  get(url) {
    return this.cache.get(url);
  }

  set(url, data) {
    if (this.cache.size >= this.maxSize) {
      // Remove oldest entry
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(url, data);
  }

  has(url) {
    return this.cache.has(url);
  }

  clear() {
    this.cache.clear();
  }
}

// API Response Cache
class APICache {
  constructor() {
    this.cache = new Map();
    this.ttl = 5 * 60 * 1000; // 5 minutes TTL
  }

  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return item.data;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }

  has(key) {
    const item = this.cache.get(key);
    if (!item) return false;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return false;
    }
    
    return true;
  }

  clear() {
    this.cache.clear();
  }
}

// Global cache instances
const imageCache = new ImageCache();
const apiCache = new APICache();

// Performance Context
const PerformanceContext = createContext({
  imageCache,
  apiCache,
  isSlowConnection: false,
  shouldOptimizeImages: false
});

export const usePerformance = () => useContext(PerformanceContext);

// Performance Provider
export const PerformanceProvider = ({ children }) => {
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [shouldOptimizeImages, setShouldOptimizeImages] = useState(false);

  useEffect(() => {
    // Detect slow connection
    if ('connection' in navigator) {
      const connection = navigator.connection;
      const updateConnectionStatus = () => {
        const isEffectiveTypeSlow = ['slow-2g', '2g', '3g'].includes(connection.effectiveType);
        const isDownlinkSlow = connection.downlink < 1.5; // Less than 1.5 Mbps
        
        setIsSlowConnection(isEffectiveTypeSlow || isDownlinkSlow);
        setShouldOptimizeImages(isEffectiveTypeSlow || isDownlinkSlow);
      };

      updateConnectionStatus();
      connection.addEventListener('change', updateConnectionStatus);

      return () => {
        connection.removeEventListener('change', updateConnectionStatus);
      };
    }

    // Fallback for browsers without Network Information API
    // Check if user prefers reduced data
    if ('matchMedia' in window) {
      const prefersReducedData = window.matchMedia('(prefers-reduced-data: reduce)');
      setShouldOptimizeImages(prefersReducedData.matches);
    }
  }, []);

  return (
    <PerformanceContext.Provider 
      value={{
        imageCache,
        apiCache,
        isSlowConnection,
        shouldOptimizeImages
      }}
    >
      {children}
    </PerformanceContext.Provider>
  );
};

// Enhanced Image Component with Performance Optimizations
export const OptimizedImage = ({ 
  src, 
  alt, 
  className = '', 
  width, 
  height,
  quality = 75,
  placeholder = '👕',
  ...props 
}) => {
  const { imageCache, shouldOptimizeImages } = usePerformance();
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  // Optimize image URL based on performance constraints
  const getOptimizedImageUrl = (originalUrl) => {
    if (!originalUrl || !shouldOptimizeImages) return originalUrl;
    
    // If it's a TopKit upload, we can add query parameters for optimization
    if (originalUrl.includes('/api/uploads/')) {
      const url = new URL(originalUrl, window.location.origin);
      if (width) url.searchParams.set('w', width);
      if (height) url.searchParams.set('h', height);
      if (quality && quality < 90) url.searchParams.set('q', quality);
      return url.toString();
    }
    
    return originalUrl;
  };

  const optimizedSrc = getOptimizedImageUrl(src);

  useEffect(() => {
    if (!optimizedSrc) return;

    // Check cache first
    if (imageCache.has(optimizedSrc)) {
      setIsLoaded(true);
      return;
    }

    // Preload image
    const img = new Image();
    img.onload = () => {
      imageCache.set(optimizedSrc, true);
      setIsLoaded(true);
    };
    img.onerror = () => {
      setError(true);
    };
    img.src = optimizedSrc;
  }, [optimizedSrc]);

  if (error) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
        <span className="text-2xl">{placeholder}</span>
      </div>
    );
  }

  if (!isLoaded) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 animate-pulse ${className}`}>
        <span className="text-2xl opacity-50">{placeholder}</span>
      </div>
    );
  }

  return (
    <img
      src={optimizedSrc}
      alt={alt}
      className={className}
      width={width}
      height={height}
      loading="lazy"
      {...props}
    />
  );
};

// Enhanced API Hook with Caching
export const useCachedAPI = (url, options = {}) => {
  const { apiCache } = usePerformance();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!url) return;

    const cacheKey = `${url}_${JSON.stringify(options)}`;
    
    // Check cache first
    const cachedData = apiCache.get(cacheKey);
    if (cachedData) {
      setData(cachedData);
      setLoading(false);
      return;
    }

    // Fetch from API
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Cache the result
        apiCache.set(cacheKey, result);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url, JSON.stringify(options), apiCache]);

  return { data, loading, error };
};

// Performance Metrics Hook
export const usePerformanceMetrics = () => {
  const [metrics, setMetrics] = useState({
    loadTime: 0,
    renderTime: 0,
    imageLoadCount: 0,
    apiCallCount: 0
  });

  useEffect(() => {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const updateMetrics = () => {
        const navigation = performance.getEntriesByType('navigation')[0];
        const resources = performance.getEntriesByType('resource');
        
        setMetrics({
          loadTime: Math.round(navigation.loadEventEnd - navigation.fetchStart),
          renderTime: Math.round(navigation.domContentLoadedEventEnd - navigation.fetchStart),
          imageLoadCount: resources.filter(r => r.initiatorType === 'img').length,
          apiCallCount: resources.filter(r => r.name.includes('/api/')).length
        });
      };

      // Update metrics after page load
      if (document.readyState === 'complete') {
        updateMetrics();
      } else {
        window.addEventListener('load', updateMetrics);
      }

      return () => {
        window.removeEventListener('load', updateMetrics);
      };
    }
  }, []);

  return metrics;
};

// Debug Performance Component (only visible in development)
export const PerformanceDebug = () => {
  const { isSlowConnection, shouldOptimizeImages } = usePerformance();
  const metrics = usePerformanceMetrics();

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-4 bg-black bg-opacity-80 text-white text-xs p-2 rounded z-50">
      <div>Connection: {isSlowConnection ? '🔴 Slow' : '🟢 Fast'}</div>
      <div>Image Opt: {shouldOptimizeImages ? '✅' : '❌'}</div>
      <div>Load: {metrics.loadTime}ms</div>
      <div>Render: {metrics.renderTime}ms</div>
      <div>Images: {metrics.imageLoadCount}</div>
    </div>
  );
};

export { imageCache, apiCache };