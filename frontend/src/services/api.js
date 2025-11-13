import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/v1/auth/login', { username, password }),
  
  register: (data) =>
    api.post('/api/v1/auth/register', data),
  
  getCurrentUser: () =>
    api.get('/api/v1/auth/me'),
  
  logout: () =>
    api.post('/api/v1/auth/logout'),
};

// Machines API
export const machinesAPI = {
  getAll: (params = {}) =>
    api.get('/api/v1/machines', { params }),
  
  getById: (id) =>
    api.get(`/api/v1/machines/${id}`),
  
  getStats: () =>
    api.get('/api/v1/machines/stats'),
  
  create: (data) =>
    api.post('/api/v1/machines', data),
  
  update: (id, data) =>
    api.put(`/api/v1/machines/${id}`, data),
  
  delete: (id) =>
    api.delete(`/api/v1/machines/${id}`),
};

// Sensors API
export const sensorsAPI = {
  getAll: (params = {}) =>
    api.get('/api/v1/sensors', { params }),
};

// Production API
export const productionAPI = {
  getOrders: (params = {}) =>
    api.get('/api/v1/production/orders', { params }),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () =>
    api.get('/api/v1/analytics/dashboard'),
  
  getEnergyTrend: (hours = 24) =>
    api.get(`/api/v1/analytics/energy/trend?hours=${hours}`),
  
  getOEEByMachine: () =>
    api.get('/api/v1/analytics/production/oee'),
};

export default api;

