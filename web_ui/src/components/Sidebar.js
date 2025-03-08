import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import DashboardIcon from '@mui/icons-material/Dashboard';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import CategoryIcon from '@mui/icons-material/Category';
import SearchIcon from '@mui/icons-material/Search';
import DescriptionIcon from '@mui/icons-material/Description';
import SettingsIcon from '@mui/icons-material/Settings';
import AssignmentIcon from '@mui/icons-material/Assignment';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import { useAuth } from '../contexts/AuthContext';

const drawerWidth = 240;

// Common menu items for all users
const commonMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Search', icon: <SearchIcon />, path: '/search' },
];

// Product Manager specific menu items
const productManagerMenuItems = [
  { text: 'Knowledge Entries', icon: <LibraryBooksIcon />, path: '/entries' },
  { text: 'Categories', icon: <CategoryIcon />, path: '/categories' },
];

// Pre-sales specific menu items
const presalesMenuItems = [
  { text: 'Tenders', icon: <AssignmentIcon />, path: '/tenders' },
  { text: 'Analyze', icon: <AnalyticsIcon />, path: '/analyze' },
];

// Secondary menu items (currently disabled)
const secondaryMenuItems = [
  // { text: 'Documents', icon: <DescriptionIcon />, path: '/documents' },
  // { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

function Sidebar() {
  const location = useLocation();
  const { isProductManager, isPresales } = useAuth();
  
  // Determine which menu items to show based on user role
  const roleSpecificItems = [];
  
  if (isProductManager()) {
    roleSpecificItems.push(...productManagerMenuItems);
  }
  
  if (isPresales()) {
    roleSpecificItems.push(...presalesMenuItems);
  }
  
  // Combine common items with role-specific items
  const menuItems = [...commonMenuItems, ...roleSpecificItems];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { 
          width: drawerWidth, 
          boxSizing: 'border-box',
          mt: '64px', // To account for AppBar height
        },
      }}
    >
      <Toolbar />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton 
              component={Link} 
              to={item.path}
              selected={location.pathname === item.path}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      {secondaryMenuItems.length > 0 && (
        <>
          <Divider />
          <List>
            {secondaryMenuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton 
                  component={Link} 
                  to={item.path}
                  selected={location.pathname === item.path}
                >
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </>
      )}
    </Drawer>
  );
}

export default Sidebar;
