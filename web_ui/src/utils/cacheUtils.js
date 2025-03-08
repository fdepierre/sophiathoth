/**
 * Utility functions for handling API caching and offline support
 * These functions help optimize performance on low bandwidth connections
 */

// Cache duration in milliseconds (default: 1 hour)
const DEFAULT_CACHE_DURATION = 60 * 60 * 1000;

/**
 * Store data in localStorage with expiration
 * @param {string} key - The cache key
 * @param {any} data - The data to cache
 * @param {number} duration - Cache duration in milliseconds
 */
export const cacheData = (key, data, duration = DEFAULT_CACHE_DURATION) => {
  try {
    const item = {
      data,
      expiry: new Date().getTime() + duration,
    };
    localStorage.setItem(`sophiathoth_cache_${key}`, JSON.stringify(item));
    console.log(`Cached data for key: ${key}`);
  } catch (error) {
    console.error('Error caching data:', error);
  }
};

/**
 * Retrieve data from localStorage if not expired
 * @param {string} key - The cache key
 * @returns {any|null} - The cached data or null if expired/not found
 */
export const getCachedData = (key) => {
  try {
    const cachedItem = localStorage.getItem(`sophiathoth_cache_${key}`);
    if (!cachedItem) return null;
    
    const item = JSON.parse(cachedItem);
    const now = new Date().getTime();
    
    // Return null if expired
    if (now > item.expiry) {
      localStorage.removeItem(`sophiathoth_cache_${key}`);
      return null;
    }
    
    return item.data;
  } catch (error) {
    console.error('Error retrieving cached data:', error);
    return null;
  }
};

/**
 * Clear all cached data
 */
export const clearCache = () => {
  try {
    Object.keys(localStorage)
      .filter(key => key.startsWith('sophiathoth_cache_'))
      .forEach(key => localStorage.removeItem(key));
    console.log('Cache cleared successfully');
  } catch (error) {
    console.error('Error clearing cache:', error);
  }
};

/**
 * Clear specific cached data
 * @param {string} key - The cache key to clear
 */
export const clearCacheItem = (key) => {
  try {
    localStorage.removeItem(`sophiathoth_cache_${key}`);
    console.log(`Cache cleared for key: ${key}`);
  } catch (error) {
    console.error('Error clearing cache item:', error);
  }
};

/**
 * Get all cached keys
 * @returns {string[]} - Array of cache keys
 */
export const getCachedKeys = () => {
  try {
    return Object.keys(localStorage)
      .filter(key => key.startsWith('sophiathoth_cache_'))
      .map(key => key.replace('sophiathoth_cache_', ''));
  } catch (error) {
    console.error('Error getting cached keys:', error);
    return [];
  }
};

/**
 * Check if the user is online
 * @returns {boolean} - True if online, false if offline
 */
export const isOnline = () => {
  return navigator.onLine;
};

/**
 * Register callbacks for online/offline events
 * @param {Function} onlineCallback - Function to call when online
 * @param {Function} offlineCallback - Function to call when offline
 * @returns {Function} - Function to remove event listeners
 */
export const registerConnectivityListeners = (onlineCallback, offlineCallback) => {
  window.addEventListener('online', onlineCallback);
  window.addEventListener('offline', offlineCallback);
  
  return () => {
    window.removeEventListener('online', onlineCallback);
    window.removeEventListener('offline', offlineCallback);
  };
};

/**
 * Create a cache-aware fetch function
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} cacheDuration - Cache duration in milliseconds
 * @returns {Promise<any>} - The response data
 */
export const cachingFetch = async (url, options = {}, cacheDuration = DEFAULT_CACHE_DURATION) => {
  const cacheKey = `${url}_${JSON.stringify(options)}`;
  
  // Try to get from cache first
  const cachedData = getCachedData(cacheKey);
  if (cachedData) {
    console.log(`Using cached data for: ${url}`);
    return cachedData;
  }
  
  // If offline and no cache, throw error
  if (!isOnline()) {
    throw new Error('You are offline and this data is not cached');
  }
  
  try {
    // Fetch from network
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Network response was not ok: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Cache the successful response
    cacheData(cacheKey, data, cacheDuration);
    
    return data;
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};
