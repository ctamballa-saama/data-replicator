import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, FormControl, InputLabel, 
  Select, MenuItem, CircularProgress, Alert, Tabs, Tab,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';
import { Bar, Pie, Line } from 'react-chartjs-2';

import { getDomains, getDomainDetails, getDomainStatistics, getVariableStatistics } from '../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

// Function to generate a random color
const getRandomColor = () => {
  const letters = '0123456789ABCDEF';
  let color = '#';
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
};

// Function to generate a list of colors
const generateColors = (count) => {
  const colors = [];
  for (let i = 0; i < count; i++) {
    colors.push(getRandomColor());
  }
  return colors;
};

const DataAnalysis = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [domainDetails, setDomainDetails] = useState(null);
  const [domainStats, setDomainStats] = useState(null);
  const [selectedVariable, setSelectedVariable] = useState('');
  const [variableStats, setVariableStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        const domainsData = await getDomains();
        setDomains(domainsData);
        
        // Check if domain was specified in URL
        const domainParam = searchParams.get('domain');
        if (domainParam && domainsData.some(d => d.name === domainParam)) {
          setSelectedDomain(domainParam);
        } else if (domainsData.length > 0) {
          setSelectedDomain(domainsData[0].name);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching domains:', error);
        setError('Failed to load domains. Please try again later.');
        setLoading(false);
      }
    };

    fetchDomains();
  }, [searchParams]);

  useEffect(() => {
    if (selectedDomain) {
      fetchDomainData();
    }
  }, [selectedDomain]);

  // Fetch variable statistics when selectedVariable changes
  useEffect(() => {
    if (selectedDomain && selectedVariable) {
      fetchVariableStats();
    }
  }, [selectedDomain, selectedVariable]);

  const fetchDomainData = async () => {
    setLoadingStats(true);
    setError(null);
    try {
      // Fetch domain details
      const details = await getDomainDetails(selectedDomain);
      setDomainDetails(details);
      
      // Fetch domain statistics
      const stats = await getDomainStatistics(selectedDomain);
      setDomainStats(stats);
      
      // Set default selected variable
      if (details.variables && details.variables.length > 0) {
        setSelectedVariable(details.variables[0]);
      } else {
        setSelectedVariable('');
      }
      
      setLoadingStats(false);
    } catch (error) {
      console.error('Error fetching domain data:', error);
      setError('Failed to load domain data. Please try again later.');
      setLoadingStats(false);
    }
  };

  const fetchVariableStats = async () => {
    if (!selectedDomain || !selectedVariable) return;
    
    setLoadingStats(true);
    setError(null);
    
    try {
      console.log(`Fetching stats for domain: ${selectedDomain}, variable: ${selectedVariable}`);
      const stats = await getVariableStatistics(selectedDomain, selectedVariable);
      
      if (stats) {
        console.log('Successfully received variable statistics');
        setVariableStats(stats);
        setError(null);
      } else {
        console.warn('Received empty statistics data');
        setError('No statistics available for this variable.');
      }
    } catch (error) {
      console.error('Error fetching variable statistics:', error);
      
      // Display more descriptive error message
      if (error.response && error.response.status === 404) {
        setError(`Variable statistics not available. Please try selecting a different variable.`);
      } else {
        setError('Failed to load variable statistics. The system is attempting to use fuzzy matching.');
      }
    } finally {
      setLoadingStats(false);
    }
  };

  const handleDomainChange = (event) => {
    setSelectedDomain(event.target.value);
  };

  const handleVariableChange = (event) => {
    setSelectedVariable(event.target.value);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Prepare charts data
  const prepareNumericChart = (stats) => {
    if (!stats || !stats.histogram) return null;
    
    const labels = stats.histogram.bins.map((bin, index) => `${bin !== null && bin !== undefined ? Number(bin).toFixed(1) : 'N/A'}`);
    const data = stats.histogram.counts;
    
    return {
      labels,
      datasets: [
        {
          label: selectedVariable,
          data,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1,
        },
      ],
    };
  };

  const prepareCategoricalChart = (stats) => {
    if (!stats || !stats.frequency_table) return null;
    
    const labels = Object.keys(stats.frequency_table);
    const data = Object.values(stats.frequency_table);
    const backgroundColors = generateColors(labels.length);
    
    return {
      labels,
      datasets: [
        {
          label: selectedVariable,
          data,
          backgroundColor: backgroundColors,
          borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
          borderWidth: 1,
        },
      ],
    };
  };

  const renderVariableVisualization = () => {
    if (!variableStats) return null;
    
    // Check variable type and render appropriate visualization
    if (variableStats.data_type === 'NUMERIC' && variableStats.stats.histogram) {
      const chartData = prepareNumericChart(variableStats.stats);
      if (!chartData) return <Alert severity="info">No histogram data available</Alert>;
      
      return (
        <Box sx={{ height: 300 }}>
          <Bar 
            data={chartData}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { position: 'top' },
                title: { display: true, text: `Distribution of ${selectedVariable}` },
              },
            }} 
          />
        </Box>
      );
    } else if ((variableStats.data_type === 'CATEGORICAL' || variableStats.data_type === 'TEXT') && variableStats.stats.frequency_table) {
      const chartData = prepareCategoricalChart(variableStats.stats);
      if (!chartData) return <Alert severity="info">No frequency data available</Alert>;
      
      // If too many categories, use bar chart instead of pie
      const tooManyCategories = Object.keys(variableStats.stats.frequency_table).length > 10;
      
      return (
        <Box sx={{ height: 300 }}>
          {tooManyCategories ? (
            <Bar 
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: true, text: `Frequencies of ${selectedVariable}` },
                },
              }} 
            />
          ) : (
            <Pie 
              data={chartData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { position: 'right' },
                  title: { display: true, text: `Frequencies of ${selectedVariable}` },
                },
              }} 
            />
          )}
        </Box>
      );
    } else if (variableStats.data_type === 'DATE' && variableStats.stats.date_range) {
      // For date variables, show a simple info panel
      return (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body1" gutterBottom>
            Date Range: {variableStats.stats.date_range.min} to {variableStats.stats.date_range.max}
          </Typography>
          <Typography variant="body1">
            Most common date: {variableStats.stats.most_common_date || 'N/A'}
          </Typography>
        </Alert>
      );
    } else {
      return <Alert severity="info">No visualization available for this variable type</Alert>;
    }
  };

  const renderVariableStatistics = () => {
    if (!variableStats) return null;
    
    return (
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Statistic</TableCell>
              <TableCell>Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {variableStats.data_type === 'NUMERIC' && (
              <>
                <TableRow>
                  <TableCell>Mean</TableCell>
                  <TableCell>{variableStats.stats.mean !== null && variableStats.stats.mean !== undefined ? Number(variableStats.stats.mean).toFixed(4) : 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Median</TableCell>
                  <TableCell>{variableStats.stats.median !== null && variableStats.stats.median !== undefined ? Number(variableStats.stats.median).toFixed(4) : 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Standard Deviation</TableCell>
                  <TableCell>{variableStats.stats.std !== null && variableStats.stats.std !== undefined ? Number(variableStats.stats.std).toFixed(4) : 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Min</TableCell>
                  <TableCell>{variableStats.stats.min !== null && variableStats.stats.min !== undefined ? Number(variableStats.stats.min).toFixed(4) : 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Max</TableCell>
                  <TableCell>{variableStats.stats.max !== null && variableStats.stats.max !== undefined ? Number(variableStats.stats.max).toFixed(4) : 'N/A'}</TableCell>
                </TableRow>
              </>
            )}
            
            {(variableStats.data_type === 'CATEGORICAL' || variableStats.data_type === 'TEXT') && (
              <>
                <TableRow>
                  <TableCell>Unique Values</TableCell>
                  <TableCell>{variableStats.stats.unique_count || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Most Common</TableCell>
                  <TableCell>{variableStats.stats.most_common || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Most Common Count</TableCell>
                  <TableCell>{variableStats.stats.most_common_count || 'N/A'}</TableCell>
                </TableRow>
              </>
            )}
            
            {variableStats.data_type === 'DATE' && (
              <>
                <TableRow>
                  <TableCell>Earliest Date</TableCell>
                  <TableCell>{variableStats.stats.date_range?.min || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Latest Date</TableCell>
                  <TableCell>{variableStats.stats.date_range?.max || 'N/A'}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Most Common Date</TableCell>
                  <TableCell>{variableStats.stats.most_common_date || 'N/A'}</TableCell>
                </TableRow>
              </>
            )}
            
            <TableRow>
              <TableCell>Missing Values</TableCell>
              <TableCell>{variableStats.missing_count || 0}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Missing Percentage</TableCell>
              <TableCell>
                {domainDetails?.record_count ? 
                  `${Number(((variableStats.missing_count || 0) / domainDetails.record_count) * 100).toFixed(2)}%` : 
                  'N/A'
                }
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Analysis
      </Typography>
      
      {/* Domain Selection */}
      <Paper sx={{ p: 3, mb: 4 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="domain-select-label">Select Domain</InputLabel>
                <Select
                  labelId="domain-select-label"
                  id="domain-select"
                  value={selectedDomain}
                  label="Select Domain"
                  onChange={handleDomainChange}
                >
                  {domains.map((domain) => (
                    <MenuItem key={domain.name} value={domain.name}>
                      {domain.name} ({domain.record_count || 0} records)
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {domainDetails && (
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="variable-select-label">Select Variable</InputLabel>
                  <Select
                    labelId="variable-select-label"
                    id="variable-select"
                    value={selectedVariable}
                    label="Select Variable"
                    onChange={handleVariableChange}
                  >
                    {domainDetails.variables.map((variable) => (
                      <MenuItem key={variable} value={variable}>
                        {variable}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
          </Grid>
        )}
      </Paper>
      
      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      {/* Domain statistics and visualizations */}
      {loadingStats ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        domainDetails && (
          <>
            {/* Domain overview */}
            <Paper sx={{ p: 3, mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                Domain Overview: {selectedDomain}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">Records:</Typography>
                  <Typography variant="body1">{domainDetails.record_count}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">Variables:</Typography>
                  <Typography variant="body1">{domainDetails.variable_count}</Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="body2" color="text.secondary">Sample Data:</Typography>
                  <Typography variant="body1">
                    {domainDetails.sample_data && domainDetails.sample_data.length > 0 ? 
                      `${domainDetails.sample_data.length} records available` : 
                      'No sample data available'}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
            
            {/* Variable analysis */}
            <Paper sx={{ p: 3 }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                <Tabs value={activeTab} onChange={handleTabChange}>
                  <Tab label="Visualization" />
                  <Tab label="Statistics" />
                </Tabs>
              </Box>
              
              {/* Variable details */}
              {variableStats && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    {selectedVariable}
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="text.secondary">Type:</Typography>
                      <Typography variant="body1">{variableStats.data_type}</Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="text.secondary">Missing Values:</Typography>
                      <Typography variant="body1">
                        {variableStats.missing_count || 0} ({Number(((variableStats.missing_count || 0) / (domainDetails?.record_count || 1)) * 100).toFixed(2)}%)
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Typography variant="body2" color="text.secondary">Description:</Typography>
                      <Typography variant="body1">{variableStats.description || 'No description available'}</Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}
              
              {/* Tab content */}
              <Box sx={{ py: 2 }}>
                {activeTab === 0 && renderVariableVisualization()}
                {activeTab === 1 && renderVariableStatistics()}
              </Box>
            </Paper>
          </>
        )
      )}
    </Box>
  );
};

export default DataAnalysis;
