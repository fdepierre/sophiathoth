import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Auth Provider
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import KnowledgeEntries from './pages/KnowledgeEntries';
import EntryDetail from './pages/EntryDetail';
import Categories from './pages/Categories';
import Search from './pages/Search';
import Login from './pages/Login';
import DocumentUpload from './pages/DocumentUpload';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

// Layout component with navigation for authenticated users
const AuthenticatedLayout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex' }}>
      <Navbar />
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: { sm: 30 },
          width: { sm: `calc(100% - 240px)` },
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

// Main App component
function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AppRoutes />
      </ThemeProvider>
    </AuthProvider>
  );
}

// Role-based route component
const RoleRoute = ({ element, allowedRoles }) => {
  const { hasRole } = useAuth();
  const hasAccess = allowedRoles.some(role => hasRole(role));
  
  return hasAccess ? element : <Navigate to="/unauthorized" />;
};

// Routes component
function AppRoutes() {
  const { authenticated, loading, isKnowledgeRole } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CssBaseline />
      </Box>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/unauthorized" element={
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
          <h1>Unauthorized Access</h1>
          <p>You don't have permission to access this page.</p>
        </Box>
      } />
      
      {/* Protected routes for all authenticated users */}
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={
          <AuthenticatedLayout>
            <Dashboard />
          </AuthenticatedLayout>
        } />
        <Route path="/search" element={
          <AuthenticatedLayout>
            <Search />
          </AuthenticatedLayout>
        } />
        
        {/* Knowledge role specific routes */}
        <Route path="/entries" element={
          <AuthenticatedLayout>
            {isKnowledgeRole() ? 
              <KnowledgeEntries /> : 
              <Navigate to="/unauthorized" />
            }
          </AuthenticatedLayout>
        } />
        <Route path="/entries/:id" element={
          <AuthenticatedLayout>
            {isKnowledgeRole() ? 
              <EntryDetail /> : 
              <Navigate to="/unauthorized" />
            }
          </AuthenticatedLayout>
        } />
        <Route path="/categories" element={
          <AuthenticatedLayout>
            {isKnowledgeRole() ? 
              <Categories /> : 
              <Navigate to="/unauthorized" />
            }
          </AuthenticatedLayout>
        } />
        <Route path="/document-upload" element={
          <AuthenticatedLayout>
            {isKnowledgeRole() ? 
              <DocumentUpload /> : 
              <Navigate to="/unauthorized" />
            }
          </AuthenticatedLayout>
        } />
        
        {/* Removed Pre-sales specific routes */}
      </Route>
      
      {/* Redirect any unknown routes to login or dashboard based on auth state */}
      <Route path="*" element={authenticated ? <Navigate to="/" /> : <Navigate to="/login" />} />
    </Routes>
  );
}

export default App;
