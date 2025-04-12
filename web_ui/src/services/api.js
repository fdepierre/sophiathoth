import axios from 'axios';
import keycloak from '../config/keycloak';

// Access environment variables from window._env_ (set by env.sh)
const getEnv = (key, defaultValue) => {
  // Debug environment variables
  console.log('Getting environment variable:', key);
  
  // Check if running in a browser environment
  if (typeof window !== 'undefined') {
    console.log('Running in browser environment');
    
    // Debug window._env_ object
    if (window._env_) {
      console.log('window._env_ is available:', Object.keys(window._env_));
      if (window._env_[key]) {
        console.log(`Found ${key} in window._env_:`, window._env_[key]);
        return window._env_[key];
      } else {
        console.log(`${key} not found in window._env_`);
      }
    } else {
      console.log('window._env_ is not available');
    }
  } else {
    console.log('Not running in browser environment');
  }
  
  // Fallback to process.env (for development)
  if (process.env && process.env[key]) {
    console.log(`Found ${key} in process.env:`, process.env[key]);
    return process.env[key];
  } else {
    console.log(`${key} not found in process.env, using default:`, defaultValue);
    return defaultValue;
  }
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
    console.log('Creating knowledge entry with data:', JSON.stringify(entryData));
    
    // Create a separate API instance for knowledge base to ensure direct connection
    const knowledgeBaseUrl = getEnv('REACT_APP_KNOWLEDGE_BASE_URL', 'http://localhost:8003/api/v1');
    // Ensure URL doesn't end with a trailing slash
    const baseUrl = knowledgeBaseUrl.endsWith('/') ? knowledgeBaseUrl.slice(0, -1) : knowledgeBaseUrl;
    console.log('Using knowledge base URL:', baseUrl);
    
    const knowledgeApi = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000 // 30 second timeout
    });
    
    // Add auth token if authenticated
    if (keycloak.authenticated) {
      console.log('Adding authentication token to request');
      knowledgeApi.defaults.headers.common['Authorization'] = `Bearer ${keycloak.token}`;
    } else {
      console.log('No authentication token available');
    }
    
    // Log request details
    console.log('Sending POST request to:', `${baseUrl}/entries/`);
    console.log('Request headers:', JSON.stringify(knowledgeApi.defaults.headers));
    
    // Make direct request to knowledge base service
    console.log('Attempting to create knowledge entry...');
    const response = await knowledgeApi.post('/entries/', entryData);
    console.log('Knowledge entry created successfully:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error creating entry:', error);
    console.error('Error details:', error.response?.data || 'No response data');
    console.error('Error status:', error.response?.status);
    console.error('Error headers:', JSON.stringify(error.response?.headers));
    // Return error object instead of throwing to prevent batch processing from stopping
    return { error: true, message: error.message, details: error.response?.data };
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

// Document Processing
export const uploadExcelDocument = async (file) => {
  try {
    console.log('uploadExcelDocument called with file:', file.name, 'size:', file.size, 'type:', file.type);
    
    const formData = new FormData();
    formData.append('file', file);
    console.log('FormData created with file appended');
    
    // Try both environment variable names that might be used
    let docProcessorUrl = getEnv('REACT_APP_DOC_PROCESSOR_URL', null);
    if (!docProcessorUrl) {
      docProcessorUrl = getEnv('REACT_APP_DOCUMENT_PROCESSOR_URL', 'http://localhost:8001/api/v1');
    }
    console.log('Document processor URL from env:', docProcessorUrl);
    
    // Hardcoded fallback for testing
    if (!docProcessorUrl || docProcessorUrl === 'undefined' || docProcessorUrl === 'null') {
      docProcessorUrl = 'http://localhost:8001/api/v1';
      console.log('Using hardcoded fallback URL:', docProcessorUrl);
    }
    
    // Ensure URL doesn't end with a trailing slash
    const baseUrl = docProcessorUrl.endsWith('/') ? docProcessorUrl.slice(0, -1) : docProcessorUrl;
    console.log('Final document processor base URL:', baseUrl);
    
    // Log all available environment variables for debugging
    console.log('All available environment variables in window._env_:', window._env_ ? Object.keys(window._env_) : 'Not available');
    
    // Create axios instance without setting Content-Type header
    // Let axios set the correct multipart boundary
    const docProcessorApi = axios.create({
      baseURL: baseUrl,
      // Don't set Content-Type here, let axios handle it for multipart/form-data
      timeout: 60000 // Increase timeout to 60 seconds for larger files
    });
    
    // Add auth token if authenticated
    if (keycloak.authenticated) {
      console.log('Adding authentication token to document processor request');
      docProcessorApi.defaults.headers.common['Authorization'] = `Bearer ${keycloak.token}`;
    } else {
      console.log('No authentication token available for document processor');
    }
    
    console.log('Sending POST request to:', `${baseUrl}/documents/`);
    
    // Log form data contents (without exposing the actual file data)
    for (let pair of formData.entries()) {
      console.log('FormData entry:', pair[0], 'type:', typeof pair[1], 
                 'name:', pair[1].name || 'N/A', 
                 'size:', pair[1].size || 'N/A');
    }
    
    // First, check if the document processor API is accessible
    try {
      console.log('Testing document processor API accessibility...');
      const healthCheck = await axios.get(`${baseUrl}/health`, { timeout: 5000 });
      console.log('Document processor API health check:', healthCheck.status, healthCheck.data);
    } catch (healthError) {
      console.warn('Document processor API health check failed:', healthError.message);
      console.log('Will still attempt to upload document');
      
      // Try the root endpoint as a fallback
      try {
        const rootCheck = await axios.get(baseUrl.split('/api')[0], { timeout: 5000 });
        console.log('Document processor root endpoint accessible:', rootCheck.status);
      } catch (rootError) {
        console.error('Document processor root endpoint also inaccessible:', rootError.message);
      }
    }
    
    // Set up request with better error handling
    let uploadResponse;
    
    try {
      console.log('Attempting document upload with default axios handling');
      
      // Let axios handle the content-type header automatically
      const response = await docProcessorApi.post('/documents/', formData);
      
      console.log('Document upload response status:', response.status);
      console.log('Document upload response data:', response.data);
      uploadResponse = response;
      
    } catch (uploadError) {
      console.error('Specific upload error:', uploadError.message);
      
      if (uploadError.response) {
        console.error('Upload error response:', {
          status: uploadError.response.status,
          data: uploadError.response.data,
          headers: uploadError.response.headers
        });
      } else if (uploadError.request) {
        console.error('Upload error - no response received:', uploadError.request);
      }
      
      // Try alternative approaches
      console.log('Trying alternative upload approaches...');
      
      // Try with explicit content type
      try {
        console.log('Attempt 1: Using explicit multipart/form-data content type');
        const newFormData = new FormData();
        newFormData.append('file', file);
        
        const altResponse1 = await axios.post(`${baseUrl}/documents/`, newFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('Alternative upload 1 succeeded:', altResponse1.status);
        uploadResponse = altResponse1;
      } catch (altError1) {
        console.error('Alternative upload 1 failed:', altError1.message);
        
        // Try with application/octet-stream
        try {
          console.log('Attempt 2: Using direct axios without FormData');
          const altResponse2 = await axios.post(`${baseUrl}/documents/`, formData, {
            headers: {
              // Let browser set the content type and boundary
            }
          });
          console.log('Alternative upload 2 succeeded:', altResponse2.status);
          uploadResponse = altResponse2;
        } catch (altError2) {
          console.error('Alternative upload 2 also failed:', altError2.message);
          throw uploadError; // Throw the original error if all attempts fail
        }
      }
    }
    
    // After successful upload, process the document questions into knowledge entries
    if (uploadResponse && uploadResponse.data && uploadResponse.data.document_id) {
      console.log(`Document uploaded successfully with ID: ${uploadResponse.data.document_id}`);
      console.log('Processing document questions into knowledge entries...');
      
      const processedEntries = await processDocumentToKnowledge(uploadResponse.data.document_id);
      console.log(`Processed ${processedEntries.length} entries from document`);
      
      // Add the processed entries to the response data
      return {
        ...uploadResponse.data,
        processedEntries
      };
    } else {
      console.warn('Document uploaded but no document_id returned in response');
      return uploadResponse ? uploadResponse.data : { error: 'No valid response from document upload' };
    }
  } catch (error) {
    console.error('Error uploading Excel document:', error);
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      stack: error.stack
    });
    throw error;
  }
};

// Process document questions into knowledge entries
export const processDocumentToKnowledge = async (documentId) => {
  try {
    const docProcessorUrl = getEnv('REACT_APP_DOCUMENT_PROCESSOR_URL', 'http://localhost:8001/api/v1');
    // Ensure URL doesn't end with a trailing slash
    const baseUrl = docProcessorUrl.endsWith('/') ? docProcessorUrl.slice(0, -1) : docProcessorUrl;
    console.log('Using document processor URL:', baseUrl);
    
    const docProcessorApi = axios.create({
      baseURL: baseUrl,
      headers: {
        'Content-Type': 'application/json',
      },
      // Add timeout to prevent hanging requests
      timeout: 30000
    });
    
    // Add auth token if authenticated
    if (keycloak.authenticated) {
      console.log('Adding authentication token to document processor request');
      docProcessorApi.defaults.headers.common['Authorization'] = `Bearer ${keycloak.token}`;
    } else {
      console.log('No authentication token available for document processor');
    }
    
    // Get questions from the document
    console.log(`Fetching questions for document ${documentId}`);
    console.log('Request URL:', `${baseUrl}/documents/${documentId}/questions`);
    
    try {
      const questionsResponse = await docProcessorApi.get(`/documents/${documentId}/questions`);
      const questions = questionsResponse.data;
      
      console.log('Questions response status:', questionsResponse.status);
      
      if (!questions || questions.length === 0) {
        console.warn(`No questions found for document ${documentId}`);
        return [];
      }
      
      console.log(`Processing ${questions.length} questions from document ${documentId}`);
      console.log('First question sample:', JSON.stringify(questions[0]));
      
      // Process questions in smaller batches to prevent freezing
      const batchSize = 5;
      const successfulEntries = [];
      const failedEntries = [];
      
      // Process in batches
      for (let i = 0; i < questions.length; i += batchSize) {
        const batch = questions.slice(i, i + batchSize);
        console.log(`Processing batch ${i/batchSize + 1} of ${Math.ceil(questions.length/batchSize)}`);
        
        // Process each question in the batch
        const batchPromises = batch.map(async (question) => {
          try {
            // Ensure proper data types for metadata
            const rowIndex = typeof question.row_index === 'string' ? parseInt(question.row_index, 10) : question.row_index;
            const columnIndex = typeof question.column_index === 'string' ? parseInt(question.column_index, 10) : question.column_index;
            
            // Log the question structure to help debug field mapping
            console.log('Question structure:', JSON.stringify(question, null, 2));
            
            // Determine which fields to use for question and answer
            // The Excel file might have different column names, so we need to be flexible
            let questionText = '';
            let answerText = '';
            
            // Check if we have explicit question/answer fields
            if (question.question && (question.answer || question.response)) {
              // Direct question/answer mapping
              questionText = question.question;
              answerText = question.answer || question.response || '';
            } else if (question.text && question.context) {
              // Document processor's default mapping
              questionText = question.text;
              answerText = question.context;
            } else {
              // Fallback to using available fields
              questionText = question.text || question.title || question.question || 'Unknown Question';
              answerText = question.context || question.content || question.answer || 
                          question.response || question.summary || 'No answer provided yet';
            }
            
            // Create a knowledge entry for each question
            const entryData = {
              title: questionText, // Map question to title field
              content: answerText, // Map answer to content field
              summary: questionText.substring(0, 200), // Use question as summary but limit length
              source_type: 'document',
              source_id: documentId,
              tags: ['imported', 'document', 'tender-qa'],
              entry_metadata: {
                document_id: documentId,
                question_id: question.id,
                sheet_id: question.sheet_id,
                row_index: rowIndex || 0,
                column_index: columnIndex || 0,
                original_fields: Object.keys(question).join(',') // Store original field names for debugging
              }
            };
            
            console.log(`Creating entry for question: ${question.text.substring(0, 30)}...`);
            
            // Create the knowledge entry
            const result = await createEntry(entryData);
            
            if (result && result.error) {
              console.error(`Failed to create entry for question ${question.id}:`, result.message);
              failedEntries.push({ question: question.text, error: result.message });
              return { error: true, questionId: question.id, message: result.message };
            }
            
            console.log(`Successfully created entry for question ${question.id}`);
            return result;
          } catch (questionError) {
            console.error(`Error processing question ${question.id}:`, questionError);
            failedEntries.push({ question: question.text, error: questionError.message });
            return { error: true, questionId: question.id, message: questionError.message };
          }
        });
        
        // Wait for the current batch to complete
        const batchResults = await Promise.allSettled(batchPromises);
        
        // Add successful entries from this batch
        const batchSuccesses = batchResults
          .filter(result => result.status === 'fulfilled' && result.value && !result.value.error)
          .map(result => result.value);
        
        // Log failed entries
        const batchFailures = batchResults
          .filter(result => result.status === 'rejected' || (result.status === 'fulfilled' && result.value && result.value.error))
          .map(result => result.status === 'rejected' ? result.reason : result.value);
        
        if (batchFailures.length > 0) {
          console.error(`Batch ${i/batchSize + 1} had ${batchFailures.length} failures:`, batchFailures);
        }
        
        successfulEntries.push(...batchSuccesses);
        console.log(`Batch ${i/batchSize + 1} complete: ${batchSuccesses.length} entries created, ${batchFailures.length} failures`);
      }
      
      console.log(`Successfully created ${successfulEntries.length} knowledge entries out of ${questions.length} questions`);
      console.log(`Failed to create ${failedEntries.length} entries`);
      
      if (failedEntries.length > 0) {
        console.error('Failed entries:', failedEntries);
      }
      
      // Verify entries were created by fetching them
      try {
        console.log('Verifying entries were created by fetching them...');
        const entries = await getEntries();
        console.log(`Found ${entries.length} entries in the knowledge base`);
      } catch (verifyError) {
        console.error('Error verifying entries:', verifyError);
      }
      
      return successfulEntries;
    } catch (questionsError) {
      console.error('Error fetching questions:', questionsError);
      console.error('Error details:', questionsError.response?.data || 'No response data');
      console.error('Error status:', questionsError.response?.status);
      return [];
    }
  } catch (error) {
    console.error(`Error processing document ${documentId} to knowledge:`, error);
    console.error('Stack trace:', error.stack);
    // Return an empty array instead of throwing to prevent UI freezing
    return [];
  }
};

export default api;
