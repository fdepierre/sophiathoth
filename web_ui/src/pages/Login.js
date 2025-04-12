import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, 
  Button, 
  Container, 
  Paper, 
  Typography, 
  CircularProgress,
  Alert,
  Snackbar,
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { useAuth } from '../contexts/AuthContext';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

function Login() {
  const { authenticated, loading, login, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [errorMessage, setErrorMessage] = useState('');
  const [showError, setShowError] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  
  // Check for error in URL params (from Keycloak)
  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const urlError = searchParams.get('error');
    const urlErrorDescription = searchParams.get('error_description');
    
    if (urlError) {
      setErrorMessage(urlErrorDescription || 'Authentication failed');
      setShowError(true);
    }
  }, [location]);

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (authenticated && !loading) {
      navigate('/');
    }
  }, [authenticated, loading, navigate]);

  // Handle login button click
  const handleLogin = async () => {
    setErrorMessage('');
    setLoginLoading(true);
    
    try {
      const success = await login(username, password);
      if (!success) {
        setErrorMessage('Login failed. Please check your credentials.');
        setShowError(true);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Login failed');
      setShowError(true);
    } finally {
      setLoginLoading(false);
    }
  };
  
  // Toggle password visibility
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  // Show error from context
  useEffect(() => {
    if (error) {
      setErrorMessage(error);
      setShowError(true);
    }
  }, [error]);

  // Show loading indicator while checking authentication
  if (loading && !loginLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Box
            sx={{
              backgroundColor: 'primary.main',
              color: 'white',
              borderRadius: '50%',
              padding: 1,
              marginBottom: 2,
            }}
          >
            <LockOutlinedIcon fontSize="large" />
          </Box>
          
          <Typography component="h1" variant="h5" gutterBottom>
            SophiaThoth
          </Typography>
          
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Sign in to access the collaborative knowledge management system
          </Typography>
          
          <TextField
            label="Username"
            variant="outlined"
            fullWidth
            margin="normal"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loginLoading}
          />
          
          <TextField
            label="Password"
            variant="outlined"
            fullWidth
            margin="normal"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loginLoading}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={togglePasswordVisibility}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          
          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={handleLogin}
            disabled={loginLoading}
            sx={{ mt: 3 }}
          >
            {loginLoading ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
          </Button>
        </Paper>
      </Box>
      
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} SophiaThoth
        </Typography>
      </Box>
      
      <Snackbar 
        open={showError} 
        autoHideDuration={6000} 
        onClose={() => setShowError(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowError(false)} 
          severity="error" 
          variant="filled"
          sx={{ width: '100%' }}
        >
          {errorMessage || 'Authentication failed'}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default Login;
