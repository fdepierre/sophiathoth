import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  Button,
  Chip,
  Divider,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  Tab,
  Tabs
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import HistoryIcon from '@mui/icons-material/History';
import DownloadIcon from '@mui/icons-material/Download';
import FileUploadIcon from '@mui/icons-material/FileUpload';

import { 
  getEntry, 
  updateEntry, 
  deleteEntry, 
  getCategories, 
  getTags,
  getAttachments,
  uploadAttachment,
  downloadAttachment
} from '../services/api';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`entry-tabpanel-${index}`}
      aria-labelledby={`entry-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function EntryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [entry, setEntry] = useState(null);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Dialog states
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
    category_id: '',
    tags: []
  });
  const [selectedTags, setSelectedTags] = useState([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [entryData, categoriesData, tagsData, attachmentsData] = await Promise.all([
          getEntry(id),
          getCategories(),
          getTags(),
          getAttachments(id)
        ]);
        
        setEntry(entryData);
        setCategories(categoriesData);
        setTags(tagsData || []);
        setAttachments(attachmentsData || []);
        
        // Initialize form data for editing
        setFormData({
          title: entryData.title,
          content: entryData.content,
          summary: entryData.summary || '',
          category_id: entryData.category_id || '',
          tags: entryData.tags ? entryData.tags.map(tag => tag.name) : []
        });
        
        setSelectedTags(entryData.tags || []);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching entry details:', err);
        setError('Failed to load entry details. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleOpenEditDialog = () => {
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleTagsChange = (event, newValue) => {
    setSelectedTags(newValue);
    setFormData({
      ...formData,
      tags: newValue.map(tag => tag.name)
    });
  };

  const handleSubmitEdit = async () => {
    try {
      const updatedEntry = await updateEntry(id, {
        ...formData,
        source_type: entry.source_type
      });
      
      setEntry(updatedEntry);
      handleCloseEditDialog();
    } catch (err) {
      console.error('Error updating entry:', err);
      setError('Failed to update entry. Please try again.');
    }
  };

  const handleOpenDeleteDialog = () => {
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
  };

  const handleDeleteEntry = async () => {
    try {
      await deleteEntry(id);
      navigate('/entries');
    } catch (err) {
      console.error('Error deleting entry:', err);
      setError('Failed to delete entry. Please try again.');
      handleCloseDeleteDialog();
    }
  };

  const handleOpenUploadDialog = () => {
    setUploadDialogOpen(true);
  };

  const handleCloseUploadDialog = () => {
    setUploadDialogOpen(false);
    setSelectedFile(null);
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUploadAttachment = async () => {
    if (!selectedFile) return;
    
    try {
      setUploading(true);
      const newAttachment = await uploadAttachment(id, selectedFile);
      setAttachments([...attachments, newAttachment]);
      setUploading(false);
      handleCloseUploadDialog();
    } catch (err) {
      console.error('Error uploading attachment:', err);
      setError('Failed to upload attachment. Please try again.');
      setUploading(false);
    }
  };

  const handleDownloadAttachment = async (attachmentId, filename) => {
    try {
      const blob = await downloadAttachment(id, attachmentId);
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error downloading attachment:', err);
      setError('Failed to download attachment. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 3, mb: 3, bgcolor: '#ffebee' }}>
        <Typography color="error">{error}</Typography>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/entries')}
          sx={{ mt: 2 }}
        >
          Back to Entries
        </Button>
      </Paper>
    );
  }

  if (!entry) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">Entry not found</Typography>
        <Button 
          variant="outlined" 
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/entries')}
          sx={{ mt: 2 }}
        >
          Back to Entries
        </Button>
      </Paper>
    );
  }

  const category = categories.find(c => c.id === entry.category_id);

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => navigate('/entries')} sx={{ mr: 1 }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h4">{entry.title}</Typography>
        </Box>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<EditIcon />}
            onClick={handleOpenEditDialog}
            sx={{ mr: 1 }}
          >
            Edit
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleOpenDeleteDialog}
          >
            Delete
          </Button>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="fullWidth"
        >
          <Tab label="Content" id="entry-tab-0" aria-controls="entry-tabpanel-0" />
          <Tab label="Attachments" id="entry-tab-1" aria-controls="entry-tabpanel-1" />
          <Tab label="Revisions" id="entry-tab-2" aria-controls="entry-tabpanel-2" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="h6" gutterBottom>Content</Typography>
              <Typography variant="body1" paragraph>
                {entry.content}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardHeader title="Summary" />
                <CardContent>
                  <Typography variant="body2">
                    {entry.summary || 'No summary available'}
                  </Typography>
                </CardContent>
              </Card>
              
              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardHeader title="Category" />
                <CardContent>
                  <Typography variant="body2">
                    {category ? category.name : 'Uncategorized'}
                  </Typography>
                </CardContent>
              </Card>
              
              <Card variant="outlined">
                <CardHeader title="Tags" />
                <CardContent>
                  {entry.tags && entry.tags.length > 0 ? (
                    entry.tags.map((tag) => (
                      <Chip
                        key={tag.id}
                        label={tag.name}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))
                  ) : (
                    <Typography variant="body2">No tags</Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Attachments</Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<FileUploadIcon />}
              onClick={handleOpenUploadDialog}
            >
              Upload Attachment
            </Button>
          </Box>
          
          {attachments.length === 0 ? (
            <Typography variant="body1">No attachments found for this entry.</Typography>
          ) : (
            <List>
              {attachments.map((attachment) => (
                <React.Fragment key={attachment.id}>
                  <ListItem>
                    <ListItemIcon>
                      <AttachFileIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={attachment.original_filename}
                      secondary={`Size: ${Math.round(attachment.size_bytes / 1024)} KB • Type: ${attachment.content_type}`}
                    />
                    <Tooltip title="Download">
                      <IconButton
                        color="primary"
                        onClick={() => handleDownloadAttachment(attachment.id, attachment.original_filename)}
                      >
                        <DownloadIcon />
                      </IconButton>
                    </Tooltip>
                  </ListItem>
                  <Divider variant="inset" component="li" />
                </React.Fragment>
              ))}
            </List>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>Revision History</Typography>
          <Typography variant="body1">
            Current version: {entry.version}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Created: {new Date(entry.created_at).toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date(entry.updated_at).toLocaleString()}
          </Typography>
        </TabPanel>
      </Paper>

      {/* Edit Dialog */}
      <Dialog open={openEditDialog} onClose={handleCloseEditDialog} maxWidth="md" fullWidth>
        <DialogTitle>Edit Knowledge Entry</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Title"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.title}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="summary"
            label="Summary"
            type="text"
            fullWidth
            variant="outlined"
            value={formData.summary}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="content"
            label="Content"
            multiline
            rows={6}
            fullWidth
            variant="outlined"
            value={formData.content}
            onChange={handleInputChange}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel id="category-select-label">Category</InputLabel>
            <Select
              labelId="category-select-label"
              name="category_id"
              value={formData.category_id}
              label="Category"
              onChange={handleInputChange}
            >
              {categories.map((category) => (
                <MenuItem key={category.id} value={category.id}>
                  {category.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Autocomplete
            multiple
            id="tags-input"
            options={tags}
            getOptionLabel={(option) => option.name}
            value={selectedTags}
            onChange={handleTagsChange}
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Tags"
                placeholder="Add tags"
              />
            )}
            sx={{ mb: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>Cancel</Button>
          <Button onClick={handleSubmitEdit} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the entry "{entry.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteEntry} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload Attachment Dialog */}
      <Dialog open={uploadDialogOpen} onClose={handleCloseUploadDialog}>
        <DialogTitle>Upload Attachment</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Select a file to attach to this knowledge entry.
          </Typography>
          <input
            type="file"
            onChange={handleFileChange}
            disabled={uploading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseUploadDialog} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleUploadAttachment} 
            color="primary" 
            variant="contained"
            disabled={!selectedFile || uploading}
          >
            {uploading ? <CircularProgress size={24} /> : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default EntryDetail;
