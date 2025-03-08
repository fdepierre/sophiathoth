/* eslint-disable no-restricted-globals */

// This service worker can be customized!
// See https://developers.google.com/web/tools/workbox/modules
// for the list of available Workbox modules, or add any other
// code you'd like.

// Cache names
const CACHE_NAME = 'sophiathoth-cache-v1';
const API_CACHE_NAME = 'sophiathoth-api-cache-v1';
const STATIC_CACHE_ITEMS = [
  '/',
  '/index.html',
  '/static/js/main.chunk.js',
  '/static/js/bundle.js',
  '/static/js/vendors~main.chunk.js',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(STATIC_CACHE_ITEMS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  const cacheAllowlist = [CACHE_NAME, API_CACHE_NAME];

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheAllowlist.includes(cacheName)) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
          return null;
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Helper function to determine if a request is for an API
const isApiRequest = (url) => {
  return (
    url.pathname.startsWith('/api/') || 
    url.pathname.includes('localhost:8001') || 
    url.pathname.includes('localhost:8002') || 
    url.pathname.includes('localhost:8003')
  );
};

// Helper function to determine if a request is for an image
const isImageRequest = (url) => {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'];
  return imageExtensions.some(ext => url.pathname.endsWith(ext));
};

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Skip cross-origin requests
  if (url.origin !== self.location.origin && !url.hostname.includes('localhost')) {
    return;
  }

  // For API requests - use network first, fall back to cache
  if (isApiRequest(url)) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clone the response
          const responseToCache = response.clone();
          
          // Only cache successful responses
          if (response.status === 200) {
            caches.open(API_CACHE_NAME)
              .then((cache) => {
                // Cache for 1 hour
                const headers = new Headers(responseToCache.headers);
                headers.append('sw-fetched-on', new Date().getTime().toString());
                
                // Create a new response with the updated headers
                const cachedResponse = new Response(responseToCache.body, {
                  status: responseToCache.status,
                  statusText: responseToCache.statusText,
                  headers: headers
                });
                
                cache.put(event.request, cachedResponse);
              });
          }
          
          return response;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(event.request)
            .then((cachedResponse) => {
              if (cachedResponse) {
                // Check if the cached response is still valid (less than 1 hour old)
                const fetchedOn = cachedResponse.headers.get('sw-fetched-on');
                if (fetchedOn) {
                  const fetchedOnTime = parseInt(fetchedOn, 10);
                  const oneHourAgo = new Date().getTime() - (60 * 60 * 1000);
                  
                  if (fetchedOnTime > oneHourAgo) {
                    return cachedResponse;
                  }
                }
                
                // Return cached response even if expired when offline
                return cachedResponse;
              }
              
              // If no cached response, return a custom offline page or error
              return new Response(JSON.stringify({ error: 'You are offline and no cached data is available' }), {
                headers: { 'Content-Type': 'application/json' }
              });
            });
        })
    );
  } 
  // For image requests - use cache first, fall back to network
  else if (isImageRequest(url)) {
    event.respondWith(
      caches.match(event.request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          return fetch(event.request)
            .then((response) => {
              // Clone the response
              const responseToCache = response.clone();
              
              // Only cache successful responses
              if (response.status === 200) {
                caches.open(CACHE_NAME)
                  .then((cache) => {
                    cache.put(event.request, responseToCache);
                  });
              }
              
              return response;
            });
        })
    );
  }
  // For all other requests - use stale-while-revalidate strategy
  else {
    event.respondWith(
      caches.match(event.request)
        .then((cachedResponse) => {
          const fetchPromise = fetch(event.request)
            .then((networkResponse) => {
              // Update the cache
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, networkResponse.clone());
                });
              
              return networkResponse;
            })
            .catch((error) => {
              console.error('Fetch failed:', error);
              // Return a custom offline page if fetch fails and no cache is available
              if (!cachedResponse) {
                return caches.match('/offline.html');
              }
              throw error;
            });
          
          // Return the cached response immediately, or wait for network response
          return cachedResponse || fetchPromise;
        })
    );
  }
});

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'syncPendingRequests') {
    event.waitUntil(syncPendingRequests());
  }
});

// Function to sync pending requests
async function syncPendingRequests() {
  try {
    // Get all pending requests from IndexedDB
    const pendingRequests = await getPendingRequests();
    
    // Process each pending request
    for (const request of pendingRequests) {
      try {
        await fetch(request.url, {
          method: request.method,
          headers: request.headers,
          body: request.body
        });
        
        // Remove the request from the pending list
        await removePendingRequest(request.id);
      } catch (error) {
        console.error('Failed to sync request:', error);
      }
    }
  } catch (error) {
    console.error('Error syncing pending requests:', error);
  }
}

// These functions would interact with IndexedDB
// Placeholder implementations
async function getPendingRequests() {
  return [];
}

async function removePendingRequest(id) {
  // Implementation would remove the request from IndexedDB
}

// Listen for messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
