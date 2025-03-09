import React, { useState } from 'react';
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

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      // Check if it's an Excel file
      if (selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
          selectedFile.type === 'application/vnd.ms-excel' ||
          selectedFile.name.endsWith('.xlsx') || 
          selectedFile.name.endsWith('.xls')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setFile(null);
        setError('Please select a valid Excel file (.xlsx or .xls)');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);
    setProcessedEntries([]);

    try {
      const result = await uploadExcelDocument(file);
      setSuccess(`File uploaded successfully! Document ID: ${result.document_id}`);
      
      // If we have processed entries from the knowledge base
      if (result.processedEntries && result.processedEntries.length > 0) {
        setProcessedEntries(result.processedEntries);
      }
      
      // Reset file selection
      setFile(null);
      document.getElementById('excel-upload-input').value = '';
    } catch (err) {
      console.error('Error uploading file:', err);
      setError(err.response?.data?.detail || 'Error uploading file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Knowledge Excel File
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
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
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
