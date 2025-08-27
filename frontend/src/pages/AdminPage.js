/**
 * Admin Page component for DataReplicator
 * 
 * Integrates all admin components using the AdminLayout and React Router
 */
import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

// Admin Components
import AdminLayout from '../components/admin/AdminLayout';
import AdminDashboard from '../components/admin/AdminDashboard';
import UserManagement from '../components/admin/UserManagement';
import DomainManagement from '../components/admin/DomainManagement';
import JobManagement from '../components/admin/JobManagement';
import ExportManagement from '../components/admin/ExportManagement';
import SystemSettings from '../components/admin/SystemSettings';

// Auth Context for protection
import { useAuth } from '../context/AuthContext';

/**
 * Protected Route component to ensure admin access
 */
const AdminProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth();
  
  // If still loading auth state, show nothing
  if (isLoading) {
    return <Box sx={{ p: 4 }}>Loading...</Box>;
  }
  
  // Check if user is logged in and has admin role
  if (!user || (user && user.role !== 'admin')) {
    return <Navigate to="/login" replace />;
  }
  
  // If admin, render children
  return children;
};

/**
 * Main AdminPage component with routing
 */
const AdminPage = () => {
  return (
    <AdminProtectedRoute>
      <Routes>
        <Route path="/" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="users" element={<UserManagement />} />
          <Route path="domains" element={<DomainManagement />} />
          <Route path="jobs" element={<JobManagement />} />
          <Route path="exports" element={<ExportManagement />} />
          <Route path="settings" element={<SystemSettings />} />
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Route>
      </Routes>
    </AdminProtectedRoute>
  );
};

export default AdminPage;
