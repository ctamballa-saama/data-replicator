/**
 * Authentication context for DataReplicator frontend
 * 
 * Provides authentication state and methods to components.
 */
import React, { createContext, useState, useEffect, useContext } from 'react';
import { login, logout, register, isAuthenticated, getCurrentUser, getUserProfile } from '../services/auth';

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  // State
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (isAuthenticated()) {
          // Try to get current user data
          const userData = getCurrentUser();
          if (userData) {
            setUser(userData);
          } else {
            // If no user data in localStorage, fetch from API
            try {
              const response = await getUserProfile();
              setUser(response.data);
            } catch (error) {
              console.error('Failed to fetch user profile:', error);
              // If API call fails, remove invalid tokens
              logout();
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        setError('Failed to initialize authentication');
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  // Login handler
  const handleLogin = async (email, password) => {
    setError(null);
    try {
      const response = await login(email, password);
      setUser(getCurrentUser());
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      setError(errorMessage);
      throw error;
    }
  };

  // Register handler
  const handleRegister = async (userData) => {
    setError(null);
    try {
      const response = await register(userData);
      return response;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      setError(errorMessage);
      throw error;
    }
  };

  // Logout handler
  const handleLogout = () => {
    logout();
    setUser(null);
  };

  // Context value
  const value = {
    user,
    loading,
    error,
    isAuthenticated: !!user,
    login: handleLogin,
    logout: handleLogout,
    register: handleRegister,
    clearError: () => setError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for using auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
