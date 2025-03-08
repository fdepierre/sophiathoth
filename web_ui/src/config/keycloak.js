import Keycloak from 'keycloak-js';

// Debug function to log environment variables
const logEnvironment = () => {
  console.log('Environment variables:');
  if (typeof window !== 'undefined' && window._env_) {
    console.log('window._env_:', window._env_);
  } else {
    console.log('window._env_ is not defined');
  }
  
  if (typeof process !== 'undefined' && process.env) {
    console.log('process.env REACT_APP_* variables:', {
      REACT_APP_KEYCLOAK_URL: process.env.REACT_APP_KEYCLOAK_URL,
      REACT_APP_KEYCLOAK_REALM: process.env.REACT_APP_KEYCLOAK_REALM,
      REACT_APP_KEYCLOAK_CLIENT_ID: process.env.REACT_APP_KEYCLOAK_CLIENT_ID
    });
  }
};

// Log environment variables when this module is loaded
logEnvironment();

// Access environment variables from window._env_ (set by env.sh)
const getEnv = (key, defaultValue) => {
  // Check if running in a browser environment
  if (typeof window !== 'undefined' && window._env_ && window._env_[key]) {
    return window._env_[key];
  }
  
  // Fallback to process.env (for development)
  return process.env[key] || defaultValue;
};

// For browser environments, always use localhost:8080 instead of keycloak:8080
const getBrowserFriendlyUrl = (url) => {
  // Always use localhost:8080 for browser requests
  if (typeof window !== 'undefined') {
    // If we're in a browser, always use localhost:8080
    if (url && url.includes('keycloak:8080')) {
      return url.replace('keycloak:8080', 'localhost:8080');
    }
  }
  return url;
};

// Get the Keycloak URL with browser-friendly adjustments
const keycloakUrl = getBrowserFriendlyUrl(getEnv('REACT_APP_KEYCLOAK_URL', 'http://localhost:8080'));

// Keycloak configuration
const keycloakConfig = {
  url: keycloakUrl,
  realm: getEnv('REACT_APP_KEYCLOAK_REALM', 'sophiathoth'),
  clientId: getEnv('REACT_APP_KEYCLOAK_CLIENT_ID', 'web-ui')
};

console.log('Initializing Keycloak with config:', keycloakConfig);

// Initialize Keycloak instance
const keycloak = new Keycloak(keycloakConfig);

// Store the original URL for reference
keycloak.originalAuthServerUrl = keycloakConfig.url;

// Override the authServerUrl getter to always return the browser-friendly URL
Object.defineProperty(keycloak, 'authServerUrl', {
  get: function() {
    return getBrowserFriendlyUrl(this.originalAuthServerUrl);
  }
});

export default keycloak;
