import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Alert, 
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { styled } from '@mui/material/styles';
import { uploadExcelDocument } from '../services/api';

// Styled component for the file input
const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [processedEntries, setProcessedEntries] = useState([]);

  // Log environment information on component mount
  useEffect(() => {
    console.log('DocumentUpload component mounted');
    
    // Log environment variables
    console.log('Environment variables available in window._env_:', 
                window._env_ ? Object.keys(window._env_) : 'Not available');
    
    if (window._env_) {
      console.log('REACT_APP_DOC_PROCESSOR_URL:', window._env_.REACT_APP_DOC_PROCESSOR_URL);
      console.log('REACT_APP_DOCUMENT_PROCESSOR_URL:', window._env_.REACT_APP_DOCUMENT_PROCESSOR_URL);
    }
    
    // Check if we're running in development mode
    if (process.env.NODE_ENV === 'development') {
      console.log('Running in development mode');
      console.log('process.env.REACT_APP_DOC_PROCESSOR_URL:', process.env.REACT_APP_DOC_PROCESSOR_URL);
      console.log('process.env.REACT_APP_DOCUMENT_PROCESSOR_URL:', process.env.REACT_APP_DOCUMENT_PROCESSOR_URL);
    }
  }, []);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      console.log('Selected file:', selectedFile);
      console.log('File type:', selectedFile.type);
      console.log('File name:', selectedFile.name);
      console.log('File size:', selectedFile.size, 'bytes');
      
      // More permissive validation - accept any Excel-like file
      // Some browsers may not correctly identify Excel files
      const validExcelTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/octet-stream', // Some browsers might use this for Excel files
        'application/x-excel',
        'application/x-msexcel'
      ];
      
      const hasValidExtension = selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls');
      const hasValidMimeType = validExcelTypes.includes(selectedFile.type);
      
      if (hasValidExtension || hasValidMimeType) {
        console.log('File validation passed: Excel file detected');
        console.log('Validation details:', {
          extension: hasValidExtension ? 'valid' : 'invalid',
          mimeType: hasValidMimeType ? 'valid' : 'invalid',
          detectedType: selectedFile.type
        });
        setFile(selectedFile);
        setError(null);
      } else {
        console.error('File validation failed: Not an Excel file');
        console.log('Validation details:', {
          extension: hasValidExtension ? 'valid' : 'invalid',
          mimeType: hasValidMimeType ? 'valid' : 'invalid',
          detectedType: selectedFile.type,
          validTypes: validExcelTypes
        });
        setFile(null);
        setError('Please select a valid Excel file (.xlsx or .xls)');
      }
    } else {
      console.log('No file selected');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    console.log('Starting file upload process for:', file.name);
    console.log('File details:', {
      name: file.name,
      type: file.type,
      size: file.size,
      lastModified: new Date(file.lastModified).toISOString()
    });

    setLoading(true);
    setError(null);
    setSuccess(null);
    setProcessedEntries([]);

    try {
      // Check if file size is reasonable (less than 10MB)
      if (file.size > 10 * 1024 * 1024) {
        console.warn('Large file detected:', file.size, 'bytes');
      }
      
      console.log('Calling uploadExcelDocument API...');
      const result = await uploadExcelDocument(file);
      console.log('Upload successful, response:', result);
      setSuccess(`File uploaded successfully! Document ID: ${result.document_id}`);
      
      // If we have processed entries from the knowledge base
      if (result.processedEntries && result.processedEntries.length > 0) {
        console.log(`Received ${result.processedEntries.length} processed entries`);
        setProcessedEntries(result.processedEntries);
      } else {
        console.warn('No processed entries returned from the API');
      }
      
      // Reset file selection
      setFile(null);
      document.getElementById('excel-upload-input').value = '';
    } catch (err) {
      console.error('Error uploading file:', err);
      
      // Provide more detailed error information
      let errorMessage = 'Failed to upload file. ';
      
      if (err.response) {
        // The request was made and the server responded with an error status
        console.error('Server error response:', {
          status: err.response.status,
          data: err.response.data,
          headers: err.response.headers
        });
        
        if (err.response.status === 400) {
          errorMessage += 'The server rejected the file. Please ensure it is a valid Excel document.';
        } else if (err.response.status === 401 || err.response.status === 403) {
          errorMessage += 'Authentication error. Please log in again.';
        } else if (err.response.status === 413) {
          errorMessage += 'The file is too large.';
        } else if (err.response.status >= 500) {
          errorMessage += 'Server error. Please try again later.';
        } else {
          errorMessage += `Server error (${err.response.status}): ${err.response.data?.detail || 'Unknown error'}`;
        }
      } else if (err.request) {
        // The request was made but no response was received
        console.error('No response received:', err.request);
        errorMessage += 'No response from server. Please check your network connection and try again.';
      } else {
        // Something happened in setting up the request
        console.error('Request setup error:', err.message);
        errorMessage += `Error: ${err.message}`;
      }
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      setError(errorMessage);
    } finally {
      setLoading(false);
      console.log('Upload process completed');
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Knowledge Excel File
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        Upload an Excel file (.xlsx or .xls) containing tender questions and answers to process into the knowledge base.
      </Typography>
      
      <Typography variant="body1" paragraph>
        Upload an Excel file containing questions and answers to populate the knowledge base.
        The file should have columns for questions and their corresponding answers.
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <Button
            component="label"
            variant="contained"
            startIcon={<CloudUploadIcon />}
            disabled={loading}
            sx={{ mb: 2 }}
          >
            Select Excel File
            <VisuallyHiddenInput 
              id="excel-upload-input"
              type="file" 
              accept=".xlsx,.xls,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel" 
              onChange={handleFileChange} 
            />
          </Button>
          
          {file && (
            <Typography variant="body2" sx={{ mb: 2 }}>
              Selected file: {file.name}
            </Typography>
          )}
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleUpload} 
            disabled={!file || loading}
            sx={{ minWidth: 200 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Upload and Process'}
          </Button>
        </Box>
      </Paper>
      
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2, '& .MuiAlert-message': { whiteSpace: 'pre-line' } }}
          action={
            <Button 
              color="inherit" 
              size="small" 
              onClick={() => setError(null)}
            >
              Dismiss
            </Button>
          }
        >
          <Typography variant="subtitle1" component="div" sx={{ fontWeight: 'bold', mb: 0.5 }}>
            Upload Error
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
          <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
            If this problem persists, please contact support with the error details from the browser console.
          </Typography>
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      {processedEntries.length > 0 && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Processed Knowledge Entries
          </Typography>
          <List>
            {processedEntries.map((entry, index) => (
              <React.Fragment key={entry.id || index}>
                <ListItem>
                  <ListItemText 
                    primary={entry.title} 
                    secondary={`Category: ${entry.category?.name || 'Uncategorized'}`} 
                  />
                </ListItem>
                {index < processedEntries.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Instructions
        </Typography>
        <Typography variant="body2" paragraph>
          1. The Excel file should contain questions and answers in a structured format.
        </Typography>
        <Typography variant="body2" paragraph>
          2. Each row should represent a question-answer pair.
        </Typography>
        <Typography variant="body2" paragraph>
          3. The system will automatically extract the questions and answers and create knowledge entries.
        </Typography>
        <Typography variant="body2" paragraph>
          4. After processing, you can view and edit the entries in the Knowledge Entries section.
        </Typography>
      </Box>
    </Box>
  );
};

export default DocumentUpload;
