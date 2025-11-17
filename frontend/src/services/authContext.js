// services/authContext.js
import React, { createContext, useContext, useEffect, useState } from 'react';
import { authAPI } from './api';
import websocket from './websocket';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // wait until auth is checked
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async (token) => {
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
      setIsAuthenticated(true);

      // connect websocket if token exists, but don't fail auth if WS fails
      if (token) {
        try {
          await websocket.connect(token);
        } catch (wsError) {
          console.warn(
            'WebSocket connect failed (will continue without WS):',
            wsError,
          );
        }
      }
    } catch (err) {
      console.error('Failed to fetch user:', err);
      localStorage.clear();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await authAPI.login(username, password);
      const { access_token, refresh_token } = response.data;

      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);

      // fetch user profile after login
      await fetchCurrentUser(access_token);

      return { success: true };
    } catch (err) {
      console.error('Login failed:', err);
      return {
        success: false,
        error: err.response?.data?.detail || 'Login failed',
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.clear();
      setUser(null);
      setIsAuthenticated(false);
      websocket.disconnect();
    }
  };

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
