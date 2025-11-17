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
  (error) => Promise.reject(error),
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip token refresh for auth endpoints (login, register) - let them handle errors normally
    const isAuthEndpoint =
      originalRequest.url?.includes('/api/v1/auth/login') ||
      originalRequest.url?.includes('/api/v1/auth/register');

    // If 401 and not already retried, try to refresh token
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isAuthEndpoint
    ) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');

        // Check if refresh token exists
        if (!refreshToken) {
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(new Error('No refresh token available'));
        }

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
  },
);

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/v1/auth/login', { username, password }),

  register: (data) => api.post('/api/v1/auth/register', data),

  getCurrentUser: () => api.get('/api/v1/auth/me'),

  logout: () => api.post('/api/v1/auth/logout'),
};

// Machines API
export const machinesAPI = {
  getAll: (params = {}) => api.get('/api/v1/machines', { params }),

  getById: (id) => api.get(`/api/v1/machines/${id}`),

  getStats: () => api.get('/api/v1/machines/stats'),

  create: (data) => api.post('/api/v1/machines', data),

  update: (id, data) => api.put(`/api/v1/machines/${id}`, data),

  delete: (id) => api.delete(`/api/v1/machines/${id}`),
};

// Sensors API
export const sensorsAPI = {
  getAll: (params = {}) => api.get('/api/v1/sensors', { params }),
};

// Production API
export const productionAPI = {
  getOrders: (params = {}) => api.get('/api/v1/production/orders', { params }),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: () => api.get('/api/v1/analytics/dashboard'),

  getEnergyTrend: (hours = 24) =>
    api.get(`/api/v1/analytics/energy/trend?hours=${hours}`),

  getOEEByMachine: () => api.get('/api/v1/analytics/production/oee'),
};

// Factories API
export const factoriesAPI = {
  getAll: (params = {}) => api.get('/api/v1/factories', { params }),

  getById: (id) => api.get(`/api/v1/factories/${id}`),
};

// Suppliers API
export const suppliersAPI = {
  getAll: (params = {}) => api.get('/api/v1/suppliers', { params }),

  getById: (id) => api.get(`/api/v1/suppliers/${id}`),
};

// Materials API
export const materialsAPI = {
  getAll: (params = {}) => api.get('/api/v1/materials', { params }),

  getById: (id) => api.get(`/api/v1/materials/${id}`),
};

// Settings API
export const settingsAPI = {
  getAll: (params = {}) => api.get('/api/v1/settings', { params }),

  getByKey: (key) => api.get(`/api/v1/settings/${key}`),
};

// AI Predictions API
export const aiPredictionsAPI = {
  getHistory: (params = {}) =>
    api.get('/api/v1/ai/predictions/history', { params }),

  getById: (id) => api.get(`/api/v1/ai/predictions/history/${id}`),

  predictAdvancedDefect: (data) =>
    api.post('/api/v1/ai/predictions/advanced-defect', data),

  predictDefect: (data) =>
    api.post('/api/v1/ai/predictions/predict-defect', data),
};

// Advanced Features API
export const advancedFeaturesAPI = {
  // Autonomous Control
  detectAndAdjust: (data) =>
    api.post('/api/v1/advanced/autonomous-control/detect-adjust', data),

  getActiveControls: () =>
    api.get('/api/v1/advanced/autonomous-control/active'),

  getAdjustmentHistory: (limit = 50) =>
    api.get('/api/v1/advanced/autonomous-control/history', {
      params: { limit },
    }),

  // Orchestration
  assignAGVTask: (data) =>
    api.post('/api/v1/advanced/orchestration/assign-agv', data),

  getFleetStatus: () => api.get('/api/v1/advanced/orchestration/fleet-status'),

  // ESG Optimizer
  calculateESGScore: (data) =>
    api.post('/api/v1/advanced/esg/calculate-score', data),

  simulateScenarios: () => api.get('/api/v1/advanced/esg/simulate-scenarios'),
};

// Factory Operations API
export const factoryOperationsAPI = {
  // Recovery
  analyzeRecovery: (data) => api.post('/api/v1/factory/recovery/analyze', data),

  prioritizeRecovery: (data) =>
    api.post('/api/v1/factory/recovery/prioritize', data),

  // Inventory
  getInventoryStatus: (materialCodes) =>
    api.get('/api/v1/factory/inventory/status', {
      params: { material_codes: materialCodes },
    }),

  checkMaterialAvailability: (materialCode, requiredQuantity) =>
    api.get('/api/v1/factory/inventory/check-availability', {
      params: {
        material_code: materialCode,
        required_quantity: requiredQuantity,
      },
    }),

  // Workflow
  trackProductJourney: (qrCode) =>
    api.get(`/api/v1/factory/workflow/track/${qrCode}`),

  getWorkflowStatistics: (orderNumber) =>
    api.get('/api/v1/factory/workflow/statistics', {
      params: { order_number: orderNumber },
    }),

  // AGV Fallback
  analyzeAGVFallback: (data) =>
    api.post('/api/v1/factory/agv-fallback/handle-failure', data),

  // IoT
  getIotDeviceStatus: (deviceId) =>
    api.get('/api/v1/factory/iot/device-status', {
      params: { device_id: deviceId },
    }),
};

// Traceability API
export const traceabilityAPI = {
  traceByQrCode: (qrCode) => api.get(`/api/v1/traceability/trace/${qrCode}`),

  getQrCodeImage: (qrCode, size = 300) =>
    `${API_URL}/api/v1/traceability/qr-image/${qrCode}?size=${size}`,
};

export default api;
