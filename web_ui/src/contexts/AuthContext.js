import React, { createContext, useState, useEffect, useContext } from 'react';
import keycloak from '../config/keycloak';
import axios from 'axios';

// Create the authentication context
const AuthContext = createContext(null);

// Authentication provider component
export const AuthProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize Keycloak - we'll skip this for now and rely on direct login
  useEffect(() => {
    // Just set loading to false since we're not doing auto-login
    setLoading(false);
  }, []);

  // Helper function to ensure we use localhost:8080 for browser requests
  const getBrowserFriendlyUrl = (url) => {
    if (typeof window !== 'undefined' && url && url.includes('keycloak:8080')) {
      return url.replace('keycloak:8080', 'localhost:8080');
    }
    return url;
  };

  // Login function with username and password (direct grant)
  const login = async (username, password) => {
    console.log('Initiating direct login process');
    
    // Always log the current configuration for debugging
    console.log('Keycloak config:', {
      authServerUrl: keycloak.authServerUrl || 'not set',
      realm: keycloak.realm || 'not set',
      clientId: keycloak.clientId || 'not set'
    });
    
    // Debug window._env_
    if (typeof window !== 'undefined') {
      console.log('window._env_:', window._env_ || 'not defined');
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Always use localhost:8080 for browser requests
      const tokenUrl = 'http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token';
      console.log('Using token URL:', tokenUrl);
      
      // Prepare the form data
      const formData = new URLSearchParams();
      formData.append('client_id', 'web-ui'); // Hardcode client_id to ensure it's correct
      formData.append('grant_type', 'password');
      formData.append('username', username);
      formData.append('password', password);
      
      console.log('Request payload:', formData.toString());
      
      // Make the request
      const response = await axios.post(tokenUrl, formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      console.log('Login successful! Response:', {
        token_type: response.data.token_type,
        expires_in: response.data.expires_in,
        access_token_preview: response.data.access_token?.substring(0, 20) + '...'
      });
      
      // Store the tokens
      const { access_token, refresh_token, expires_in } = response.data;
      keycloak.token = access_token;
      keycloak.refreshToken = refresh_token;
      keycloak.tokenParsed = parseJwt(access_token);
      keycloak.refreshTokenParsed = parseJwt(refresh_token);
      keycloak.sessionId = keycloak.tokenParsed.sid;
      keycloak.authenticated = true;
      keycloak.expiresIn = expires_in;
      
      // Set up token refresh
      setupTokenRefresh();
      
      // Update state
      setAuthenticated(true);
      setToken(access_token);
      
      // Log token contents for debugging
      console.log('Token parsed contents:', {
        sub: keycloak.tokenParsed.sub,
        preferred_username: keycloak.tokenParsed.preferred_username,
        email: keycloak.tokenParsed.email,
        roles: keycloak.tokenParsed.realm_access?.roles
      });
      
      // Set user info
      const userInfo = {
        id: keycloak.tokenParsed.sub,
        username: keycloak.tokenParsed.preferred_username,
        email: keycloak.tokenParsed.email,
        firstName: keycloak.tokenParsed.given_name,
        lastName: keycloak.tokenParsed.family_name,
        roles: keycloak.tokenParsed.realm_access?.roles || []
      };
      
      setUser(userInfo);
      setLoading(false);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      
      // Provide more detailed error information
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      
      setError(error.response?.data?.error_description || error.message || 'Failed to login');
      setLoading(false);
      return false;
    }
  };
  
  // Helper function to parse JWT
  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
      return null;
    }
  };
  
  // Set up token refresh
  const setupTokenRefresh = () => {
    if (keycloak.token && keycloak.refreshToken) {
      // Calculate when to refresh (at 70% of token lifetime)
      const expiresIn = keycloak.tokenParsed.exp - Math.ceil(new Date().getTime() / 1000);
      const timeout = Math.max((expiresIn * 0.7) * 1000, 0);
      
      // Set timeout for token refresh
      setTimeout(() => refreshToken(), timeout);
    }
  };
  
  // Refresh token function
  const refreshToken = async () => {
    try {
      // Always use localhost:8080 for browser requests
      const tokenUrl = 'http://localhost:8080/realms/sophiathoth/protocol/openid-connect/token';
      
      console.log('Using refresh token URL:', tokenUrl);
      
      const formData = new URLSearchParams();
      formData.append('client_id', 'web-ui'); // Hardcode client_id to ensure it's correct
      formData.append('grant_type', 'refresh_token');
      formData.append('refresh_token', keycloak.refreshToken);
      
      console.log('Refresh token request payload:', formData.toString());
      
      const response = await axios.post(tokenUrl, formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      console.log('Token refresh successful!');
      
      // Update tokens
      const { access_token, refresh_token, expires_in } = response.data;
      keycloak.token = access_token;
      keycloak.refreshToken = refresh_token;
      keycloak.tokenParsed = parseJwt(access_token);
      keycloak.refreshTokenParsed = parseJwt(refresh_token);
      keycloak.expiresIn = expires_in;
      
      setToken(access_token);
      
      // Set up next refresh
      setupTokenRefresh();
      
      return true;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      
      // Provide more detailed error information
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      
      logout();
      return false;
    }
  };
  
  // Legacy redirect login function
  const redirectLogin = () => {
    console.log('Initiating redirect login process');
    keycloak.login({
      redirectUri: window.location.origin + '/login',
      prompt: 'login'
    }).catch(error => {
      console.error('Login error:', error);
      setError('Failed to login: ' + (error.message || 'Unknown error'));
    });
  };

  // Logout function
  const logout = () => {
    // Clear tokens and state
    keycloak.token = null;
    keycloak.refreshToken = null;
    keycloak.tokenParsed = null;
    keycloak.refreshTokenParsed = null;
    keycloak.authenticated = false;
    
    setAuthenticated(false);
    setUser(null);
    setToken(null);
    
    // Optionally redirect to Keycloak logout endpoint
    // window.location.href = `${keycloak.authServerUrl}/realms/${keycloak.realm}/protocol/openid-connect/logout?redirect_uri=${encodeURIComponent(window.location.origin)}`;
  };

  // Check if user has a specific role
  const hasRole = (role) => {
    return user?.roles?.includes(role) || false;
  };
  
  // Check if user is a Product Manager
  const isProductManager = () => {
    return hasRole('product-manager');
  };
  
  // Check if user is a Pre-sales specialist
  const isPresales = () => {
    return hasRole('presales');
  };

  // Authentication context value
  const value = {
    authenticated,
    user,
    token,
    loading,
    error,
    login,
    logout,
    hasRole,
    isProductManager,
    isPresales,
    redirectLogin,
    refreshToken
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
