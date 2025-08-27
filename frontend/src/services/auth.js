/**
 * Authentication service for DataReplicator frontend
 * 
 * Handles user authentication, token management, and API requests.
 */
import axios from 'axios';
import { API_BASE_URL } from './config';

// Create an axios instance with authentication headers
const authAxios = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Intercept requests to add authorization header
authAxios.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Intercept responses to handle token expiration
authAxios.interceptors.response.use(
  response => response,
  error => {
    const originalRequest = error.config;
    
    // If unauthorized and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      return refreshToken()
        .then(res => {
          if (res.data.access_token) {
            localStorage.setItem('auth_token', res.data.access_token);
            authAxios.defaults.headers['Authorization'] = `Bearer ${res.data.access_token}`;
            originalRequest.headers['Authorization'] = `Bearer ${res.data.access_token}`;
            return authAxios(originalRequest);
          }
        })
        .catch(refreshError => {
          // If refresh fails, logout
          logout();
          return Promise.reject(refreshError);
        });
    }
    
    return Promise.reject(error);
  }
);

/**
 * Login with email and password
 * 
 * @param {string} email User email
 * @param {string} password User password
 * @returns {Promise} Promise with login response
 */
export const login = (email, password) => {
  // DEVELOPMENT MODE: Use mock authentication instead of real backend
  console.log('Using mock authentication for development');
  
  // Hardcoded credentials for development
  const validCredentials = [
    { username: 'admin@datareplicator.com', password: 'admin123', role: 'admin' },
    { username: 'admin', password: 'password', role: 'admin' },
    { username: 'user@datareplicator.com', password: 'user123', role: 'user' },
    { username: 'dev', password: 'dev', role: 'developer' }
  ];
  
  // Check if credentials are valid
  const user = validCredentials.find(u => 
    (u.username === email && u.password === password)
  );
  
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (user) {
        // Create mock tokens
        const mockTokens = {
          access_token: 'mock_access_token_' + Math.random().toString(36).substring(2),
          refresh_token: 'mock_refresh_token_' + Math.random().toString(36).substring(2),
          token_type: 'bearer',
          expires_in: 3600
        };
        
        // Store tokens in localStorage
        localStorage.setItem('auth_token', mockTokens.access_token);
        localStorage.setItem('refresh_token', mockTokens.refresh_token);
        
        // Create mock user profile
        const mockUser = {
          id: '1',
          email: email,
          username: email.split('@')[0],
          first_name: email === 'admin@datareplicator.com' ? 'Admin' : 'Test',
          last_name: 'User',
          role: user.role,
          is_active: true,
          created_at: new Date().toISOString(),
          permissions: user.role === 'admin' ? ['admin', 'read', 'write', 'delete'] : ['read']
        };
        
        // Store user profile
        localStorage.setItem('user', JSON.stringify(mockUser));
        
        resolve({ data: mockTokens });
      } else {
        reject({ 
          response: { 
            status: 401, 
            data: { detail: 'Invalid username or password' } 
          } 
        });
      }
    }, 500); // Add a small delay to simulate network request
  });
};

/**
 * Register a new user
 * 
 * @param {Object} userData User registration data
 * @returns {Promise} Promise with registration response
 */
export const register = (userData) => {
  return axios.post(`${API_BASE_URL}/auth/register`, userData);
};

/**
 * Refresh access token using refresh token
 * 
 * @returns {Promise} Promise with refresh response
 */
export const refreshToken = () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  if (!refreshToken) {
    return Promise.reject('No refresh token available');
  }
  
  return axios.post(`${API_BASE_URL}/auth/refresh`, {
    refresh_token: refreshToken
  });
};

/**
 * Get current user profile
 * 
 * @returns {Promise} Promise with user data
 */
export const getUserProfile = () => {
  // Development mode: Return the mock user from localStorage
  const user = getCurrentUser();
  
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (user) {
        resolve({ data: user });
      } else {
        reject({ 
          response: { 
            status: 401, 
            data: { detail: 'User not authenticated' } 
          } 
        });
      }
    }, 100);
  });
};

/**
 * Logout user by removing tokens
 */
export const logout = () => {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Check if user is authenticated
 * 
 * @returns {boolean} True if authenticated
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('auth_token');
  return !!token;
};

/**
 * Get current authenticated user data
 * 
 * @returns {Object|null} User object or null if not authenticated
 */
export const getCurrentUser = () => {
  try {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
};

/**
 * Update user profile
 * 
 * @param {Object} userData Updated user data
 * @returns {Promise} Promise with update response
 */
export const updateUserProfile = (userData) => {
  return authAxios.put('/auth/users/me', userData).then(response => {
    if (response.data) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response;
  });
};

/**
 * Change user password
 * 
 * @param {string} currentPassword Current password
 * @param {string} newPassword New password
 * @returns {Promise} Promise with response
 */
export const changePassword = (currentPassword, newPassword) => {
  return authAxios.post('/auth/users/me/password', {
    current_password: currentPassword,
    new_password: newPassword
  });
};

export default {
  login,
  register,
  logout,
  refreshToken,
  getUserProfile,
  updateUserProfile,
  isAuthenticated,
  getCurrentUser,
  changePassword,
  authAxios
};
