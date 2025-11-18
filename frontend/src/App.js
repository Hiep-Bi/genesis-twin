import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import React from 'react';
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from 'react-router-dom';

// Pages
import AdvancedFeatures from './pages/AdvancedFeatures';
import AIPredictions from './pages/AIPredictions';
import Analytics from './pages/Analytics';
import Dashboard from './pages/Dashboard';
import Energy from './pages/Energy';
import Login from './pages/Login';
import Machines from './pages/Machines';
import Production from './pages/Production';
import QRScanner from './pages/QRScanner';

// Layout
import MainLayout from './components/Layout/MainLayout';

// Services
import ProtectedRoute from './components/Auth/ProtectedRoute';
import { AuthProvider } from './services/authContext';

// Theme - Light red and white (MUI default colors with red accent)
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#d32f2f', // Light red
      light: '#ef5350',
      dark: '#c62828',
    },
    secondary: {
      main: '#616161', // Gray
      light: '#9e9e9e',
      dark: '#424242',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
    },
    success: { main: '#2e7d32' },
    warning: { main: '#ed6c02' },
    error: { main: '#d32f2f' },
    info: { main: '#0288d1' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: { fontSize: '2.5rem', fontWeight: 700 },
    h2: { fontSize: '2rem', fontWeight: 600 },
    h3: { fontSize: '1.75rem', fontWeight: 600 },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0px 2px 4px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            {/* Public Route */}
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
              <Route path="ai-predictions" element={<AIPredictions />} />
              <Route path="advanced-features" element={<AdvancedFeatures />} />
            </Route>

            {/* Catch-all redirect */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
