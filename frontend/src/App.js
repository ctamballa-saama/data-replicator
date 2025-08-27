import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Auth Context
import { AuthProvider, useAuth } from './context/AuthContext';

// Import components
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import DataIngestion from './pages/DataIngestion';
import DataAnalysis from './pages/DataAnalysis';
import DataGeneration from './pages/DataGeneration';
import RelationshipView from './pages/RelationshipView';
import DomainDetails from './pages/DomainDetails';
import Login from './components/auth/Login';
import AdminPage from './pages/AdminPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>Loading...</Box>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Main layout with navigation
const MainLayout = ({ children }) => (
  <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
    <Header />
    <Navigation />
    <Box
      component="main"
      sx={{
        flexGrow: 1,
        p: 3,
        width: { sm: `calc(100% - 240px)` },
        ml: { sm: '240px' },
        mt: '64px',
        overflow: 'auto',
        height: 'calc(100vh - 64px)',
      }}
    >
      {children}
    </Box>
  </Box>
);

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Routes>
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes with main layout */}
          <Route path="/" element={
            <ProtectedRoute>
              <MainLayout>
                <Dashboard />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/data-ingestion" element={
            <ProtectedRoute>
              <MainLayout>
                <DataIngestion />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/data-analysis" element={
            <ProtectedRoute>
              <MainLayout>
                <DataAnalysis />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/data-generation" element={
            <ProtectedRoute>
              <MainLayout>
                <DataGeneration />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/relationships" element={
            <ProtectedRoute>
              <MainLayout>
                <RelationshipView />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          <Route path="/domain/:domainName" element={
            <ProtectedRoute>
              <MainLayout>
                <DomainDetails />
              </MainLayout>
            </ProtectedRoute>
          } />
          
          {/* Admin routes */}
          <Route path="/admin/*" element={
            <ProtectedRoute>
              <AdminPage />
            </ProtectedRoute>
          } />
          
          {/* Redirect all other routes to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
