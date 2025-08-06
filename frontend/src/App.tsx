import React, { useState, useEffect } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Alert, Snackbar } from '@mui/material';
import Layout from '@/components/Layout/Layout';
import ChatInterface from '@/components/Chat/ChatInterface';
import { apiService } from '@/services/api';

const App: React.FC = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [healthStatus, setHealthStatus] = useState<'loading' | 'healthy' | 'error'>('loading');

  // Create healthcare-focused theme
  const theme = createTheme({
    palette: {
      mode: darkMode ? 'dark' : 'light',
      primary: {
        main: '#2e7d32', // Medical green
      },
      secondary: {
        main: '#1565c0', // Medical blue
      },
      info: {
        main: '#0277bd', // Healthcare blue
      },
    },
    components: {
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
        },
      },
    },
  });

  // Check backend health on startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiService.health();
        setHealthStatus('healthy');
        console.log('✅ Backend is healthy');
      } catch (error) {
        setHealthStatus('error');
        console.error('❌ Backend health check failed:', error);
      }
    };

    checkHealth();
  }, []);

  const handleToggleDarkMode = () => {
    setDarkMode(prev => !prev);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout darkMode={darkMode} onToggleDarkMode={handleToggleDarkMode}>
        {healthStatus === 'healthy' && <ChatInterface />}

        {healthStatus === 'loading' && (
          <Alert severity="info">
            Connecting to backend...
          </Alert>
        )}

        {healthStatus === 'error' && (
          <Alert severity="error">
            Unable to connect to backend. Please ensure the FastAPI server is running on port 8000.
          </Alert>
        )}
      </Layout>
    </ThemeProvider>
  );
};

export default App;