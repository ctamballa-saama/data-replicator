/**
 * Configuration for API services
 * 
 * Central configuration for API endpoints and other service settings
 */

// API base URL - configurable based on environment
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Default request timeout in milliseconds
export const API_TIMEOUT = 30000;

// Authentication endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH: '/auth/refresh',
  PROFILE: '/auth/profile',
  LOGOUT: '/auth/logout',
};

// API endpoints for various services
export const API_ENDPOINTS = {
  DOMAINS: '/domains',
  VARIABLES: '/variables',
  GENERATION: '/generation',
  ANALYSIS: '/analysis',
  JOBS: '/jobs',
  EXPORTS: '/exports',
  USERS: '/users',
  SETTINGS: '/settings',
};

// Default pagination settings
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 25, 50, 100],
};
