import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  CircularProgress,
  InputAdornment,
  IconButton,
  Card,
  CardContent,
  Alert
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ClearIcon from '@mui/icons-material/Clear';
import DescriptionIcon from '@mui/icons-material/Description';

import { searchEntries } from '../services/api';

function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState(null);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setSearched(false);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const results = await searchEntries(searchQuery);
      setSearchResults(results);
      setSearched(true);
      setLoading(false);
    } catch (err) {
      console.error('Error searching entries:', err);
      setError('Failed to search. Please try again later.');
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Search Knowledge Base
      </Typography>
      
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSearch}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search for knowledge entries..."
            value={searchQuery}
            onChange={handleSearchChange}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
              endAdornment: searchQuery && (
                <InputAdornment position="end">
                  <IconButton
                    aria-label="clear search"
                    onClick={clearSearch}
                    edge="end"
                  >
                    <ClearIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={!searchQuery.trim() || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
          >
            Search
          </Button>
        </form>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {searched && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Search Results {searchResults.length > 0 && `(${searchResults.length})`}
          </Typography>
          
          {searchResults.length === 0 ? (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="body1" align="center">
                  No results found for "{searchQuery}"
                </Typography>
                <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
                  Try using different keywords or check your spelling
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <Paper>
              <List>
                {searchResults.map((result) => (
                  <React.Fragment key={result.id}>
                    <ListItem
                      button
                      component={Link}
                      to={`/entries/${result.id}`}
                      alignItems="flex-start"
                    >
                      <ListItemIcon>
                        <DescriptionIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={result.title}
                        secondary={
                          <React.Fragment>
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.primary"
                            >
                              {result.summary || (result.content && result.content.substring(0, 150) + '...') || 'No content available'}
                            </Typography>
                            
                            {result.score && (
                              <Typography
                                component="span"
                                variant="body2"
                                color="text.secondary"
                                sx={{ display: 'block', mt: 1 }}
                              >
                                Relevance: {Math.round(result.score * 100)}%
                              </Typography>
                            )}
                            
                            {result.tags && result.tags.length > 0 && (
                              <Box sx={{ mt: 1 }}>
                                {result.tags.map((tag) => (
                                  <Chip
                                    key={tag.id}
                                    label={tag.name}
                                    size="small"
                                    sx={{ mr: 0.5, mb: 0.5 }}
                                  />
                                ))}
                              </Box>
                            )}
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
}

export default Search;
