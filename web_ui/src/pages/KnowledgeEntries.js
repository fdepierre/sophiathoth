import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
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
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

import { getEntries, getCategories, getTags, createEntry, deleteEntry } from '../services/api';

function KnowledgeEntries() {
  const [entries, setEntries] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
    category_id: '',
    tags: []
  });
  const [selectedTags, setSelectedTags] = useState([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [entryToDelete, setEntryToDelete] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [entriesData, categoriesData, tagsData] = await Promise.all([
          getEntries(),
          getCategories(),
          getTags()
        ]);
        setEntries(entriesData);
        setCategories(categoriesData);
        setTags(tagsData || []);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching entries data:', err);
        setError('Failed to load entries. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleOpenCreateDialog = () => {
    setDialogMode('create');
    setFormData({
      title: '',
      content: '',
      summary: '',
      category_id: '',
      tags: []
    });
    setSelectedTags([]);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
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

  const handleSubmit = async () => {
    try {
      if (dialogMode === 'create') {
        const newEntry = await createEntry({
          ...formData,
          source_type: 'manual'
        });
        setEntries([...entries, newEntry]);
      }
      
      handleCloseDialog();
    } catch (err) {
      console.error('Error submitting entry:', err);
      setError('Failed to save entry. Please try again.');
    }
  };

  const handleOpenDeleteDialog = (entry) => {
    setEntryToDelete(entry);
    setDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setEntryToDelete(null);
  };

  const handleDeleteEntry = async () => {
    try {
      await deleteEntry(entryToDelete.id);
      setEntries(entries.filter(entry => entry.id !== entryToDelete.id));
      handleCloseDeleteDialog();
    } catch (err) {
      console.error('Error deleting entry:', err);
      setError('Failed to delete entry. Please try again.');
      handleCloseDeleteDialog();
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Knowledge Entries</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Add New Entry
        </Button>
      </Box>

      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: '#ffebee' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : entries.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="h6">No entries found</Typography>
          <Typography variant="body1" sx={{ mt: 1 }}>
            Create your first knowledge entry to get started
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenCreateDialog}
            sx={{ mt: 2 }}
          >
            Add New Entry
          </Button>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Summary</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {entries.map((entry) => {
                const category = categories.find(c => c.id === entry.category_id);
                
                return (
                  <TableRow key={entry.id}>
                    <TableCell component="th" scope="row">
                      {entry.title}
                    </TableCell>
                    <TableCell>{entry.summary || 'No summary'}</TableCell>
                    <TableCell>{category ? category.name : 'Uncategorized'}</TableCell>
                    <TableCell>
                      {entry.tags && entry.tags.map((tag) => (
                        <Chip
                          key={tag.id}
                          label={tag.name}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View">
                        <IconButton 
                          component={Link} 
                          to={`/entries/${entry.id}`}
                          color="primary"
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit">
                        <IconButton 
                          component={Link} 
                          to={`/entries/${entry.id}`}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          color="error"
                          onClick={() => handleOpenDeleteDialog(entry)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New Knowledge Entry' : 'Edit Knowledge Entry'}
        </DialogTitle>
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
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {dialogMode === 'create' ? 'Create' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the entry "{entryToDelete?.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>Cancel</Button>
          <Button onClick={handleDeleteEntry} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default KnowledgeEntries;
