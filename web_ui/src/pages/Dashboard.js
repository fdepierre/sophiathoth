import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Typography, 
  Grid, 
  Paper, 
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip
} from '@mui/material';
import { styled } from '@mui/material/styles';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import CategoryIcon from '@mui/icons-material/Category';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import SearchIcon from '@mui/icons-material/Search';

import { getEntries, getCategories } from '../services/api';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(2),
  color: theme.palette.text.primary,
  height: '100%',
}));

function Dashboard() {
  const [entries, setEntries] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [entriesData, categoriesData] = await Promise.all([
          getEntries(),
          getCategories()
        ]);
        setEntries(entriesData);
        setCategories(categoriesData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom>
        Knowledge Base Dashboard
      </Typography>
      
      {error && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: '#ffebee' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      )}
      
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={3}>
          <Item>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <LibraryBooksIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Knowledge Entries</Typography>
            </Box>
            <Typography variant="h3" align="center" sx={{ my: 2 }}>
              {loading ? '...' : entries.length}
            </Typography>
            <Button 
              component={Link} 
              to="/entries" 
              variant="outlined" 
              fullWidth
            >
              View All Entries
            </Button>
          </Item>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Item>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CategoryIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Categories</Typography>
            </Box>
            <Typography variant="h3" align="center" sx={{ my: 2 }}>
              {loading ? '...' : categories.length}
            </Typography>
            <Button 
              component={Link} 
              to="/categories" 
              variant="outlined" 
              fullWidth
            >
              Manage Categories
            </Button>
          </Item>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Item>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <LocalOfferIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Tags</Typography>
            </Box>
            <Typography variant="h3" align="center" sx={{ my: 2 }}>
              {loading ? '...' : 
                entries.reduce((acc, entry) => {
                  return acc + (entry.tags ? entry.tags.length : 0);
                }, 0)
              }
            </Typography>
            <Button 
              component={Link} 
              to="/entries" 
              variant="outlined" 
              fullWidth
            >
              View Tagged Content
            </Button>
          </Item>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Item>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <SearchIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Search</Typography>
            </Box>
            <Typography variant="body1" sx={{ my: 2 }}>
              Search the knowledge base for specific information
            </Typography>
            <Button 
              component={Link} 
              to="/search" 
              variant="contained" 
              color="primary" 
              fullWidth
            >
              Advanced Search
            </Button>
          </Item>
        </Grid>
        
        {/* Recent Entries */}
        <Grid item xs={12} md={8}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Recent Knowledge Entries
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Typography>Loading recent entries...</Typography>
            ) : entries.length === 0 ? (
              <Typography>No entries found.</Typography>
            ) : (
              <List>
                {entries.slice(0, 5).map((entry) => (
                  <React.Fragment key={entry.id}>
                    <ListItem 
                      alignItems="flex-start"
                      component={Link}
                      to={`/entries/${entry.id}`}
                      sx={{ 
                        textDecoration: 'none', 
                        color: 'inherit',
                        '&:hover': {
                          bgcolor: 'rgba(0, 0, 0, 0.04)',
                        },
                      }}
                    >
                      <ListItemIcon>
                        <LibraryBooksIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={entry.title}
                        secondary={
                          <>
                            <Typography
                              component="span"
                              variant="body2"
                              color="text.primary"
                            >
                              {entry.summary || 'No summary available'}
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                              {entry.tags && entry.tags.map((tag) => (
                                <Chip 
                                  key={tag.id} 
                                  label={tag.name} 
                                  size="small" 
                                  sx={{ mr: 0.5, mb: 0.5 }} 
                                />
                              ))}
                            </Box>
                          </>
                        }
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                component={Link} 
                to="/entries" 
                color="primary"
              >
                View All Entries
              </Button>
            </Box>
          </Item>
        </Grid>
        
        {/* Categories */}
        <Grid item xs={12} md={4}>
          <Item>
            <Typography variant="h6" gutterBottom>
              Categories
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {loading ? (
              <Typography>Loading categories...</Typography>
            ) : categories.length === 0 ? (
              <Typography>No categories found.</Typography>
            ) : (
              <List>
                {categories.map((category) => (
                  <React.Fragment key={category.id}>
                    <ListItem>
                      <ListItemIcon>
                        <CategoryIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={category.name}
                        secondary={category.description || 'No description available'}
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button 
                component={Link} 
                to="/categories" 
                color="primary"
              >
                Manage Categories
              </Button>
            </Box>
          </Item>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
