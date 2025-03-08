import { useState, useEffect, useCallback } from 'react';
import { cachingFetch, getCachedData, cacheData, isOnline } from '../utils/cacheUtils';

/**
 * Custom hook for API calls with caching support for low bandwidth connections
 * 
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Fetch options
 * @param {number} cacheDuration - Cache duration in milliseconds (default: 1 hour)
 * @param {boolean} skipCache - Whether to skip cache and force network request
 * @returns {Object} - { data, loading, error, refetch }
 */
const useApiWithCache = (url, options = {}, cacheDuration = 60 * 60 * 1000, skipCache = false) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastFetched, setLastFetched] = useState(null);
  const [offlineMode, setOfflineMode] = useState(!isOnline());

  // Generate a unique cache key for this request
  const cacheKey = `${url}_${JSON.stringify(options)}`;

  // Function to fetch data
  const fetchData = useCallback(async (forceNetwork = false) => {
    setLoading(true);
    setError(null);
    
    try {
      let result;
      
      // Check if we're offline
      if (!isOnline()) {
        setOfflineMode(true);
        // Try to get from cache when offline
        const cachedData = getCachedData(cacheKey);
        if (cachedData) {
          setData(cachedData);
          setLoading(false);
          return;
        } else {
          throw new Error('You are offline and this data is not available in cache');
        }
      }
      
      setOfflineMode(false);
      
      // If we should skip cache or force network request
      if (skipCache || forceNetwork) {
        // Fetch from network
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }
        
        result = await response.json();
        
        // Cache the successful response
        cacheData(cacheKey, result, cacheDuration);
      } else {
        // Try to use cachingFetch which handles both cache and network
        result = await cachingFetch(url, options, cacheDuration);
      }
      
      setData(result);
      setLastFetched(new Date());
    } catch (err) {
      console.error('Error in useApiWithCache:', err);
      setError(err.message);
      
      // Try to get from cache as fallback even if skipCache was true
      if (skipCache) {
        const cachedData = getCachedData(cacheKey);
        if (cachedData) {
          setData(cachedData);
          console.log('Using cached data as fallback after network error');
        }
      }
    } finally {
      setLoading(false);
    }
  }, [url, options, cacheKey, cacheDuration, skipCache]);

  // Function to manually refetch data
  const refetch = useCallback(() => {
    return fetchData(true);
  }, [fetchData]);

  // Set up online/offline event listeners
  useEffect(() => {
    const handleOnline = () => {
      setOfflineMode(false);
      // Refresh data when coming back online
      fetchData(true);
    };
    
    const handleOffline = () => {
      setOfflineMode(true);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [fetchData]);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch, offlineMode, lastFetched };
};

export default useApiWithCache;
