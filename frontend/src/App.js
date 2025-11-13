import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Machines from './pages/Machines';
import Energy from './pages/Energy';
import Production from './pages/Production';
import Analytics from './pages/Analytics';
import QRScanner from './pages/QRScanner';
import AdvancedFeatures from './pages/AdvancedFeatures';

// Layout
import MainLayout from './components/Layout/MainLayout';

// Services
import { AuthProvider } from './services/authContext';
import ProtectedRoute from './components/Auth/ProtectedRoute';

// Theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d9ff',
    },
    secondary: {
      main: '#ff006e',
    },
    background: {
      default: '#0a0e27',
      paper: '#151932',
    },
    success: {
      main: '#00ff88',
    },
    warning: {
      main: '#ffb800',
    },
    error: {
      main: '#ff4757',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Oxygen", "Ubuntu", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, #151932 0%, #1a1f3a 100%)',
          borderRadius: 16,
          border: '1px solid rgba(255, 255, 255, 0.05)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="machines" element={<Machines />} />
              <Route path="energy" element={<Energy />} />
              <Route path="production" element={<Production />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="qr-scanner" element={<QRScanner />} />
              <Route path="advanced-features" element={<AdvancedFeatures />} />
            </Route>
            
            {/* Catch all */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;

