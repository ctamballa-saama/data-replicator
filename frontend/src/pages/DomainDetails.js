import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, Button, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Tabs, Tab, IconButton, Chip, Tooltip
} from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import LinkIcon from '@mui/icons-material/Link';

import { getDomainDetails, getDomainStatistics, getRelationships } from '../services/api';

const DomainDetails = () => {
  const { domainName } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [domain, setDomain] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [relationships, setRelationships] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [rowsPerPage] = useState(10);

  useEffect(() => {
    if (domainName) {
      fetchDomainData();
    }
  }, [domainName]);

  const fetchDomainData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch domain details
      const domainData = await getDomainDetails(domainName);
      setDomain(domainData);
      
      // Fetch domain statistics
      try {
        const stats = await getDomainStatistics(domainName);
        setStatistics(stats);
      } catch (statsError) {
        console.error('Error fetching statistics:', statsError);
        // Non-critical error, continue without stats
      }
      
      // Fetch relationships
      try {
        const rels = await getRelationships();
        const filteredRels = rels.filter(
          rel => rel.source_domain === domainName || rel.target_domain === domainName
        );
        setRelationships(filteredRels);
      } catch (relsError) {
        console.error('Error fetching relationships:', relsError);
        // Non-critical error, continue without relationships
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching domain data:', error);
      setError(`Failed to load domain '${domainName}'. Please try again later.`);
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const handleAnalyze = () => {
    navigate(`/data-analysis?domain=${domainName}`);
  };

  const handleGenerateData = () => {
    navigate(`/data-generation?domain=${domainName}`);
  };

  const downloadSampleData = () => {
    if (!domain || !domain.sample_data) return;
    
    // Create downloadable JSON file
    const jsonString = JSON.stringify(domain.sample_data, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Create temporary link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = `${domainName}_sample.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    URL.revokeObjectURL(url);
  };

  // Format variable types for display
  const formatVariableType = (variable) => {
    // This is a placeholder. In a real implementation, you would get this 
    // information from the domain.variables array
    if (!domain || !domain.variables) return 'Unknown';
    
    // For demo purposes, making educated guesses
    if (variable.includes('DT') || variable.includes('DATE')) return 'DATE';
    if (variable.includes('NUM') || variable.includes('COUNT')) return 'NUMERIC';
    if (variable.includes('FLAG')) return 'CATEGORICAL';
    return 'TEXT';
  };

  // Render sample data table
  const renderSampleData = () => {
    if (!domain || !domain.sample_data || domain.sample_data.length === 0) {
      return (
        <Alert severity="info">
          No sample data available for this domain.
        </Alert>
      );
    }

    // Get column names from first row
    const columns = Object.keys(domain.sample_data[0]);
    
    // Paginate the data
    const startIdx = currentPage * rowsPerPage;
    const endIdx = startIdx + rowsPerPage;
    const paginatedData = domain.sample_data.slice(startIdx, endIdx);
    
    return (
      <>
        <TableContainer sx={{ maxHeight: 400 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column}>
                    <Typography variant="subtitle2">{column}</Typography>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedData.map((row, rowIndex) => (
                <TableRow key={rowIndex} hover>
                  {columns.map((column) => (
                    <TableCell key={`${rowIndex}-${column}`}>
                      {row[column] !== null && row[column] !== undefined ? 
                        String(row[column]) : 
                        <span style={{ color: '#999' }}>NULL</span>
                      }
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* Pagination controls */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', py: 2 }}>
          <Button 
            disabled={currentPage === 0}
            onClick={() => handlePageChange(currentPage - 1)}
            sx={{ mr: 1 }}
          >
            Previous
          </Button>
          <Typography sx={{ mx: 2, alignSelf: 'center' }}>
            Page {currentPage + 1} of {Math.ceil(domain.sample_data.length / rowsPerPage)}
          </Typography>
          <Button 
            disabled={currentPage >= Math.ceil(domain.sample_data.length / rowsPerPage) - 1}
            onClick={() => handlePageChange(currentPage + 1)}
          >
            Next
          </Button>
        </Box>
      </>
    );
  };

  // Render variables table
  const renderVariables = () => {
    if (!domain || !domain.variables || domain.variables.length === 0) {
      return (
        <Alert severity="info">
          No variables available for this domain.
        </Alert>
      );
    }

    return (
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Variable Name</TableCell>
              <TableCell>Data Type</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {domain.variables.map((variable, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {variable}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={formatVariableType(variable)}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {/* This would normally come from the domain data */}
                  <Typography variant="body2" color="text.secondary">
                    {variable.includes('ID') ? 'Identifier' : 
                     variable.includes('DT') ? 'Date value' :
                     variable.includes('FLAG') ? 'Flag indicator' :
                     'Data variable'}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="Analyze Variable">
                    <IconButton 
                      size="small"
                      onClick={() => navigate(`/data-analysis?domain=${domainName}&variable=${variable}`)}
                    >
                      <AnalyticsIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  // Render relationships
  const renderRelationships = () => {
    if (!relationships || relationships.length === 0) {
      return (
        <Alert severity="info">
          No relationships found for this domain.
        </Alert>
      );
    }

    return (
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Related Domain</TableCell>
              <TableCell>Relationship</TableCell>
              <TableCell>Variables</TableCell>
              <TableCell align="right">Strength</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {relationships.map((rel, index) => {
              const isSource = rel.source_domain === domainName;
              const otherDomain = isSource ? rel.target_domain : rel.source_domain;
              const direction = isSource ? 'to' : 'from';
              
              return (
                <TableRow key={index}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {otherDomain}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      icon={<LinkIcon />}
                      label={`${rel.relationship_type} (${direction})`}
                      size="small"
                      color={rel.strength > 0.7 ? 'primary' : 'default'}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {isSource ? rel.source_variable : rel.target_variable} →{' '}
                      {isSource ? rel.target_variable : rel.source_variable}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {rel.strength !== null && rel.strength !== undefined ? Number(rel.strength).toFixed(2) : 'N/A'}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton 
                      size="small" 
                      onClick={() => navigate(`/domain/${otherDomain}`)}
                    >
                      <KeyboardArrowRightIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      ) : domain ? (
        <>
          {/* Domain header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4" component="h1">
              {domainName}
              <Typography 
                variant="subtitle1" 
                component="span" 
                sx={{ ml: 2, color: 'text.secondary' }}
              >
                Domain Details
              </Typography>
            </Typography>
            
            <Box>
              <Button
                variant="outlined"
                startIcon={<AnalyticsIcon />}
                onClick={handleAnalyze}
                sx={{ mr: 2 }}
              >
                Analyze
              </Button>
              <Button
                variant="contained"
                color="primary"
                startIcon={<AutoFixHighIcon />}
                onClick={handleGenerateData}
              >
                Generate Data
              </Button>
            </Box>
          </Box>
          
          {/* Domain overview */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Domain Overview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">Records:</Typography>
                <Typography variant="body1">{domain.record_count}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">Variables:</Typography>
                <Typography variant="body1">{domain.variable_count}</Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" color="text.secondary">Related Domains:</Typography>
                <Typography variant="body1">{relationships.length}</Typography>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Tabs for different views */}
          <Paper sx={{ mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={activeTab} onChange={handleTabChange}>
                <Tab label="Sample Data" />
                <Tab label="Variables" />
                <Tab label="Relationships" />
              </Tabs>
            </Box>
            
            <Box sx={{ p: 3 }}>
              {activeTab === 0 && (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      Sample Records
                    </Typography>
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={downloadSampleData}
                      disabled={!domain.sample_data || domain.sample_data.length === 0}
                    >
                      Download
                    </Button>
                  </Box>
                  {renderSampleData()}
                </>
              )}
              
              {activeTab === 1 && (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      Variables ({domain.variables?.length || 0})
                    </Typography>
                  </Box>
                  {renderVariables()}
                </>
              )}
              
              {activeTab === 2 && (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      Relationships ({relationships.length})
                    </Typography>
                    <Button
                      size="small"
                      startIcon={<VisibilityIcon />}
                      onClick={() => navigate('/relationships')}
                      disabled={relationships.length === 0}
                    >
                      View All
                    </Button>
                  </Box>
                  {renderRelationships()}
                </>
              )}
            </Box>
          </Paper>
        </>
      ) : (
        <Alert severity="warning">
          Domain not found. Please select a valid domain.
        </Alert>
      )}
    </Box>
  );
};

export default DomainDetails;
