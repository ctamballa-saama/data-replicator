/**
 * Admin Dashboard component for DataReplicator
 * 
 * Main admin control panel showing system statistics and quick access to admin functions
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PeopleAlt as UsersIcon,
  Storage as DomainsIcon,
  Task as JobsIcon,
  CloudDownload as ExportsIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Pending as PendingIcon,
} from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';

// Mock API call - replace with actual API integration
const fetchAdminStats = async () => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return mock statistics data
  return {
    userStats: {
      total: 42,
      active: 37,
      admins: 3,
    },
    domainStats: {
      total: 15,
      public: 5,
    },
    jobStats: {
      total: 287,
      pending: 5,
      running: 2,
      completed: 275,
      failed: 5,
    },
    exportStats: {
      total: 156,
      formats: {
        csv: 72,
        json: 43,
        xml: 21,
        sas: 12,
        excel: 8,
      },
    },
    recentJobs: [
      { id: 'job123', name: 'Generate Demographics', status: 'completed', user: 'john.doe', timestamp: '2025-08-27T10:15:00Z' },
      { id: 'job124', name: 'Export AE Domain', status: 'completed', user: 'jane.smith', timestamp: '2025-08-27T11:30:00Z' },
      { id: 'job125', name: 'Generate Labs', status: 'running', user: 'mark.wilson', timestamp: '2025-08-27T12:00:00Z' },
      { id: 'job126', name: 'Analyze VS Domain', status: 'pending', user: 'sarah.jones', timestamp: '2025-08-27T12:05:00Z' },
      { id: 'job127', name: 'Export CM Domain', status: 'failed', user: 'chris.adams', timestamp: '2025-08-27T12:07:00Z' },
    ],
  };
};

const AdminDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    const loadDashboardStats = async () => {
      try {
        setLoading(true);
        const data = await fetchAdminStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error loading admin stats:', err);
        setError('Failed to load admin dashboard statistics');
      } finally {
        setLoading(false);
      }
    };
    
    loadDashboardStats();
    
    // Refresh stats every 60 seconds
    const interval = setInterval(loadDashboardStats, 60000);
    return () => clearInterval(interval);
  }, []);
  
  // Status icon mapper
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <SuccessIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <CircularProgress size={20} />;
      case 'pending':
        return <PendingIcon color="info" />;
      default:
        return null;
    }
  };
  
  // Format timestamp to local time
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };
  
  if (loading && !stats) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Admin Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Welcome back, {user?.full_name || 'Administrator'}
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {stats && (
        <>
          {/* Statistics Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {/* Users Stats */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardHeader title="Users" avatar={<UsersIcon color="primary" />} />
                <Divider />
                <CardContent>
                  <Typography variant="h3" align="center">{stats.userStats.total}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">Active: {stats.userStats.active}</Typography>
                    <Typography variant="body2" color="text.secondary">Admins: {stats.userStats.admins}</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Domains Stats */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardHeader title="Domains" avatar={<DomainsIcon color="primary" />} />
                <Divider />
                <CardContent>
                  <Typography variant="h3" align="center">{stats.domainStats.total}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">Public: {stats.domainStats.public}</Typography>
                    <Typography variant="body2" color="text.secondary">Private: {stats.domainStats.total - stats.domainStats.public}</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Jobs Stats */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardHeader title="Jobs" avatar={<JobsIcon color="primary" />} />
                <Divider />
                <CardContent>
                  <Typography variant="h3" align="center">{stats.jobStats.total}</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', mt: 2 }}>
                    <Typography variant="body2" color="success.main">Completed: {stats.jobStats.completed}</Typography>
                    <Typography variant="body2" color="error.main">Failed: {stats.jobStats.failed}</Typography>
                    <Typography variant="body2" color="info.main">Running: {stats.jobStats.running}</Typography>
                    <Typography variant="body2" color="text.secondary">Pending: {stats.jobStats.pending}</Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            {/* Exports Stats */}
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardHeader title="Exports" avatar={<ExportsIcon color="primary" />} />
                <Divider />
                <CardContent>
                  <Typography variant="h3" align="center">{stats.exportStats.total}</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', mt: 2 }}>
                    {Object.entries(stats.exportStats.formats).map(([format, count]) => (
                      <Typography key={format} variant="body2" color="text.secondary">
                        {format.toUpperCase()}: {count}
                      </Typography>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          {/* Recent Jobs */}
          <Paper sx={{ p: 2, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Recent Jobs
            </Typography>
            <List>
              {stats.recentJobs.map((job) => (
                <React.Fragment key={job.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(job.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={job.name}
                      secondary={`Job ID: ${job.id} | User: ${job.user} | ${formatTimestamp(job.timestamp)}`}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography 
                        variant="body2"
                        sx={{ 
                          textTransform: 'uppercase', 
                          fontWeight: 'bold',
                          color: job.status === 'completed' ? 'success.main' : 
                                 job.status === 'failed' ? 'error.main' : 
                                 job.status === 'running' ? 'info.main' : 
                                 'text.secondary'
                        }}
                      >
                        {job.status}
                      </Typography>
                    </Box>
                  </ListItem>
                  <Divider variant="inset" component="li" />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </>
      )}
    </Container>
  );
};

export default AdminDashboard;
