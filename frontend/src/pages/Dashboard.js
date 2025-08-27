import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Grid, Paper, Typography, Card, CardContent, CardActionArea } from '@mui/material';
import StorageIcon from '@mui/icons-material/Storage';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';

// Import API service
import { getDomains } from '../services/api';

const StatCard = ({ title, value, icon, color, onClick }) => {
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3,
        }
      }}
    >
      <CardActionArea sx={{ height: '100%' }} onClick={onClick}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography variant="h5" component="div" gutterBottom>
                {value}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
            </Box>
            <Box 
              sx={{ 
                backgroundColor: `${color}.light`, 
                borderRadius: '50%', 
                p: 1,
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

const DomainCard = ({ domain, onClick }) => {
  return (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3,
        }
      }}
    >
      <CardActionArea sx={{ height: '100%' }} onClick={onClick}>
        <CardContent>
          <Typography variant="h6" component="div">
            {domain.name}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {domain.description || `${domain.name} domain`}
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Records
              </Typography>
              <Typography variant="body2">
                {domain.record_count}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Variables
              </Typography>
              <Typography variant="body2">
                {domain.variable_count}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const domainsData = await getDomains();
        setDomains(domainsData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching domains:', err);
        setError('Failed to load domains. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Mock data for demonstration if no real data is available
  const domainCount = domains.length || 3;
  const totalRecords = domains.reduce((sum, domain) => sum + domain.record_count, 0) || 1250;
  const relationships = 5; // Mock value
  const generatedDomains = 2; // Mock value

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Stats overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Clinical Domains" 
            value={domainCount} 
            icon={<StorageIcon sx={{ color: 'primary.main' }} />}
            color="primary"
            onClick={() => navigate('/data-ingestion')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Total Records" 
            value={totalRecords} 
            icon={<StorageIcon sx={{ color: 'secondary.main' }} />}
            color="secondary"
            onClick={() => navigate('/data-ingestion')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Domain Relationships" 
            value={relationships} 
            icon={<AccountTreeIcon sx={{ color: 'success.main' }} />}
            color="success"
            onClick={() => navigate('/relationships')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard 
            title="Generated Domains" 
            value={generatedDomains} 
            icon={<AutoFixHighIcon sx={{ color: 'warning.main' }} />}
            color="warning"
            onClick={() => navigate('/data-generation')}
          />
        </Grid>
      </Grid>

      {/* Quick actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardActionArea onClick={() => navigate('/data-ingestion')}>
                <CardContent sx={{ textAlign: 'center', p: 2 }}>
                  <StorageIcon color="primary" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body1">
                    Upload Data
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardActionArea onClick={() => navigate('/data-analysis')}>
                <CardContent sx={{ textAlign: 'center', p: 2 }}>
                  <AnalyticsIcon color="secondary" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body1">
                    Analyze Data
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardActionArea onClick={() => navigate('/relationships')}>
                <CardContent sx={{ textAlign: 'center', p: 2 }}>
                  <AccountTreeIcon color="success" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body1">
                    View Relationships
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardActionArea onClick={() => navigate('/data-generation')}>
                <CardContent sx={{ textAlign: 'center', p: 2 }}>
                  <AutoFixHighIcon color="warning" sx={{ fontSize: 48, mb: 1 }} />
                  <Typography variant="body1">
                    Generate Data
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Available domains */}
      <Typography variant="h5" gutterBottom>
        Available Domains
      </Typography>
      
      {loading ? (
        <Typography>Loading domains...</Typography>
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : domains.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" gutterBottom>
            No domains available yet.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Start by uploading clinical data in the Data Ingestion section.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {/* If no real domains available, show mock domains */}
          {domains.length > 0 ? domains.map((domain) => (
            <Grid item xs={12} sm={6} md={4} key={domain.name}>
              <DomainCard 
                domain={domain} 
                onClick={() => navigate(`/domain/${domain.name}`)}
              />
            </Grid>
          )) : (
            // Mock domains for demonstration
            <>
              <Grid item xs={12} sm={6} md={4}>
                <DomainCard 
                  domain={{ 
                    name: 'DM', 
                    description: 'Demographics', 
                    record_count: 500,
                    variable_count: 15
                  }} 
                  onClick={() => navigate('/domain/DM')}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <DomainCard 
                  domain={{ 
                    name: 'VS', 
                    description: 'Vital Signs', 
                    record_count: 750,
                    variable_count: 10
                  }} 
                  onClick={() => navigate('/domain/VS')}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <DomainCard 
                  domain={{ 
                    name: 'LB', 
                    description: 'Laboratory Tests', 
                    record_count: 1200,
                    variable_count: 20
                  }} 
                  onClick={() => navigate('/domain/LB')}
                />
              </Grid>
            </>
          )}
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard;
