import axios from 'axios';
import keycloak from '../config/keycloak';

// Access environment variables from window._env_ (set by env.sh)
const getEnv = (key, defaultValue) => {
  // Check if running in a browser environment
  if (typeof window !== 'undefined' && window._env_ && window._env_[key]) {
    return window._env_[key];
  }
  
  // Fallback to process.env (for development)
  return process.env[key] || defaultValue;
};

const API_URL = getEnv('REACT_APP_API_URL', 'http://localhost:8003/api/v1');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token
api.interceptors.request.use(
  (config) => {
    // If authenticated, add the token
    if (keycloak.authenticated) {
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already tried to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry && keycloak.authenticated) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshed = await keycloak.updateToken(30);
        
        if (refreshed) {
          // Update the auth header with the new token
          originalRequest.headers.Authorization = `Bearer ${keycloak.token}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Force logout if token refresh fails
        keycloak.logout();
      }
    }
    
    return Promise.reject(error);
  }
);

// Knowledge Entries
export const getEntries = async (page = 1, limit = 10) => {
  try {
    const response = await api.get('/entries/');
    return response.data;
  } catch (error) {
    console.error('Error fetching entries:', error);
    throw error;
  }
};

export const getEntry = async (id) => {
  try {
    const response = await api.get(`/entries/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching entry ${id}:`, error);
    throw error;
  }
};

export const createEntry = async (entryData) => {
  try {
    const response = await api.post('/entries/', entryData);
    return response.data;
  } catch (error) {
    console.error('Error creating entry:', error);
    throw error;
  }
};

export const updateEntry = async (id, entryData) => {
  try {
    const response = await api.put(`/entries/${id}`, entryData);
    return response.data;
  } catch (error) {
    console.error(`Error updating entry ${id}:`, error);
    throw error;
  }
};

export const deleteEntry = async (id) => {
  try {
    const response = await api.delete(`/entries/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting entry ${id}:`, error);
    throw error;
  }
};

// Categories
export const getCategories = async () => {
  try {
    const response = await api.get('/categories/');
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

export const createCategory = async (categoryData) => {
  try {
    const response = await api.post('/categories/', categoryData);
    return response.data;
  } catch (error) {
    console.error('Error creating category:', error);
    throw error;
  }
};

// Tags
export const getTags = async () => {
  try {
    const response = await api.get('/tags/');
    return response.data;
  } catch (error) {
    console.error('Error fetching tags:', error);
    throw error;
  }
};

// Attachments
export const getAttachments = async (entryId) => {
  try {
    const response = await api.get(`/entries/${entryId}/attachments`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching attachments for entry ${entryId}:`, error);
    throw error;
  }
};

export const uploadAttachment = async (entryId, file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/entries/${entryId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Error uploading attachment for entry ${entryId}:`, error);
    throw error;
  }
};

export const downloadAttachment = async (entryId, attachmentId) => {
  try {
    const response = await api.get(`/entries/${entryId}/attachments/${attachmentId}`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    console.error(`Error downloading attachment ${attachmentId}:`, error);
    throw error;
  }
};

// Search
export const searchEntries = async (query, limit = 10) => {
  try {
    const response = await api.get(`/search/?query=${encodeURIComponent(query)}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error(`Error searching for "${query}":`, error);
    throw error;
  }
};

export default api;
