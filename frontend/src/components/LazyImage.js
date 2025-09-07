import React, { useState, useRef, useEffect } from 'react';
import { Image as ImageIcon, AlertCircle } from 'lucide-react';

const LazyImage = ({ 
  src, 
  alt, 
  className = '', 
  fallback = null,
  placeholder = null,
  onLoad = () => {},
  onError = () => {},
  threshold = 0.1,
  ...props 
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const imgRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: threshold,
        rootMargin: '50px'
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [threshold]);

  const handleLoad = (e) => {
    setIsLoaded(true);
    setIsLoading(false);
    onLoad(e);
  };

  const handleError = (e) => {
    setHasError(true);
    setIsLoading(false);
    onError(e);
  };

  const handleImageStart = () => {
    setIsLoading(true);
  };

  const DefaultPlaceholder = () => (
    <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
      <ImageIcon className="w-8 h-8 text-gray-400" />
    </div>
  );

  const ErrorFallback = () => (
    <div className={`flex items-center justify-center bg-red-50 ${className}`}>
      <AlertCircle className="w-8 h-8 text-red-400" />
    </div>
  );

  const LoadingPlaceholder = () => (
    <div className={`flex items-center justify-center bg-gray-100 animate-pulse ${className}`}>
      <ImageIcon className="w-8 h-8 text-gray-400 animate-pulse" />
    </div>
  );

  return (
    <div ref={imgRef} className={`relative ${className}`}>
      {!isInView && (
        placeholder || <DefaultPlaceholder />
      )}
      
      {isInView && !hasError && (
        <>
          {isLoading && (
            <div className="absolute inset-0">
              <LoadingPlaceholder />
            </div>
          )}
          <img
            src={src}
            alt={alt}
            className={`${className} ${isLoaded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-300`}
            onLoad={handleLoad}
            onError={handleError}
            onLoadStart={handleImageStart}
            style={{
              display: isLoaded ? 'block' : 'none'
            }}
            {...props}
          />
        </>
      )}
      
      {hasError && (
        fallback || <ErrorFallback />
      )}
    </div>
  );
};

export default LazyImage;