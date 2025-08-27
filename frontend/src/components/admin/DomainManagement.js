/**
 * Domain Management component for DataReplicator Admin
 * 
 * Provides functionality to view, manage, and analyze clinical domains
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  FormControlLabel,
  Switch,
  CircularProgress,
  Alert,
  Tooltip,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  CloudDownload as ExportIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';

// Mock API functions - replace with actual API integration
const fetchDomains = async (page, rowsPerPage, searchTerm = '') => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock domain data
  const allDomains = [
    { id: 'dom1', name: 'DM', description: 'Demographics', record_count: 850, variable_count: 24, source_format: 'CSV', created_at: '2025-03-15T10:30:00Z', owner: 'john.doe', is_active: true },
    { id: 'dom2', name: 'AE', description: 'Adverse Events', record_count: 1240, variable_count: 35, source_format: 'SAS', created_at: '2025-04-02T14:15:00Z', owner: 'jane.smith', is_active: true },
    { id: 'dom3', name: 'VS', description: 'Vital Signs', record_count: 3600, variable_count: 18, source_format: 'CSV', created_at: '2025-04-12T09:45:00Z', owner: 'mark.wilson', is_active: true },
    { id: 'dom4', name: 'LB', description: 'Laboratory Tests', record_count: 7850, variable_count: 42, source_format: 'Excel', created_at: '2025-05-08T16:20:00Z', owner: 'sarah.jones', is_active: true },
    { id: 'dom5', name: 'CM', description: 'Concomitant Medications', record_count: 1920, variable_count: 28, source_format: 'CSV', created_at: '2025-06-22T11:10:00Z', owner: 'alex.brown', is_active: true },
    { id: 'dom6', name: 'MH', description: 'Medical History', record_count: 780, variable_count: 22, source_format: 'SAS', created_at: '2025-07-14T13:55:00Z', owner: 'emily.davis', is_active: true },
    { id: 'dom7', name: 'EX', description: 'Exposure', record_count: 850, variable_count: 19, source_format: 'CSV', created_at: '2025-08-05T10:40:00Z', owner: 'chris.adams', is_active: false },
  ];
  
  // Filter domains by search term if provided
  const filteredDomains = searchTerm
    ? allDomains.filter(domain => 
        domain.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        domain.description.toLowerCase().includes(searchTerm.toLowerCase()) || 
        domain.owner.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : allDomains;
  
  // Paginate results
  const paginatedDomains = filteredDomains.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return {
    domains: paginatedDomains,
    totalCount: filteredDomains.length
  };
};

const fetchDomainDetails = async (domainId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock domain details
  const domainDetails = {
    id: domainId,
    name: 'DM',
    description: 'Demographics',
    record_count: 850,
    variable_count: 24,
    source_file: 'dm.csv',
    source_format: 'CSV',
    created_at: '2025-03-15T10:30:00Z',
    updated_at: '2025-08-10T15:45:00Z',
    owner: 'john.doe',
    is_active: true,
    schema: {
      columns: [
        { name: 'USUBJID', label: 'Subject ID', datatype: 'string', required: true },
        { name: 'AGE', label: 'Age', datatype: 'integer', required: true },
        { name: 'SEX', label: 'Sex', datatype: 'string', required: true },
        { name: 'RACE', label: 'Race', datatype: 'string', required: true },
        { name: 'COUNTRY', label: 'Country', datatype: 'string', required: false },
      ]
    },
    sample_data: [
      { USUBJID: '001-001', AGE: 45, SEX: 'M', RACE: 'WHITE', COUNTRY: 'USA' },
      { USUBJID: '001-002', AGE: 52, SEX: 'F', RACE: 'BLACK OR AFRICAN AMERICAN', COUNTRY: 'USA' },
      { USUBJID: '001-003', AGE: 38, SEX: 'M', RACE: 'ASIAN', COUNTRY: 'JPN' },
    ],
    relationships_data: {
      related_domains: [
        { domain: 'AE', key: 'USUBJID', relationship: 'one-to-many' },
        { domain: 'VS', key: 'USUBJID', relationship: 'one-to-many' },
        { domain: 'LB', key: 'USUBJID', relationship: 'one-to-many' },
      ]
    }
  };
  
  return domainDetails;
};

const deleteDomain = async (domainId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return { success: true };
};

const toggleDomainStatus = async (domainId, status) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return { 
    success: true,
    status: status
  };
};

const DomainManagement = () => {
  // State
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalDomains, setTotalDomains] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('view'); // 'view', 'delete'
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [domainDetails, setDomainDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Load domains
  const loadDomains = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchDomains(page, rowsPerPage, searchTerm);
      setDomains(data.domains);
      setTotalDomains(data.totalCount);
    } catch (err) {
      console.error('Error loading domains:', err);
      setError('Failed to load domains. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load
  useEffect(() => {
    loadDomains();
  }, [page, rowsPerPage, searchTerm]);
  
  // Handle search
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setPage(0); // Reset to first page when searching
      loadDomains();
    }
  };
  
  // Handle view domain details
  const handleViewDomain = async (domain) => {
    setSelectedDomain(domain);
    setDialogMode('view');
    setOpenDialog(true);
    setDomainDetails(null);
    
    try {
      setDetailsLoading(true);
      const details = await fetchDomainDetails(domain.id);
      setDomainDetails(details);
    } catch (err) {
      console.error('Error loading domain details:', err);
      setError('Failed to load domain details. Please try again.');
    } finally {
      setDetailsLoading(false);
    }
  };
  
  // Handle delete dialog
  const handleDeleteDialog = (domain) => {
    setSelectedDomain(domain);
    setDialogMode('delete');
    setOpenDialog(true);
  };
  
  // Handle dialog close
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedDomain(null);
    setDomainDetails(null);
  };
  
  // Handle domain deletion
  const handleDeleteDomain = async () => {
    if (!selectedDomain) return;
    
    setActionLoading(true);
    try {
      await deleteDomain(selectedDomain.id);
      
      // Close dialog and reload domains
      handleCloseDialog();
      loadDomains();
      setSuccessMessage(`Domain ${selectedDomain.name} deleted successfully`);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error deleting domain:', err);
      setError('Failed to delete domain. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Handle domain status toggle
  const handleToggleDomainStatus = async (domain) => {
    setActionLoading(true);
    try {
      const newStatus = !domain.is_active;
      await toggleDomainStatus(domain.id, newStatus);
      
      // Update domains list with new status
      setDomains(domains.map(d => 
        d.id === domain.id ? { ...d, is_active: newStatus } : d
      ));
      
      setSuccessMessage(`Domain ${domain.name} ${newStatus ? 'activated' : 'deactivated'} successfully`);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error toggling domain status:', err);
      setError('Failed to update domain status. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Domain Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage and analyze clinical data domains
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}
      
      {successMessage && (
        <Alert severity="success" sx={{ mb: 4 }}>
          {successMessage}
        </Alert>
      )}
      
      <Paper sx={{ mb: 4, p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              placeholder="Search domains..."
              variant="outlined"
              size="small"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={handleSearch}
              InputProps={{
                startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ width: 250 }}
            />
            <Tooltip title="Refresh">
              <IconButton onClick={loadDomains} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Domain</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Variables</TableCell>
                <TableCell>Format</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 3 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : domains.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1">No domains found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                domains.map((domain) => (
                  <TableRow key={domain.id}>
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {domain.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{domain.description}</TableCell>
                    <TableCell>{domain.record_count.toLocaleString()}</TableCell>
                    <TableCell>{domain.variable_count}</TableCell>
                    <TableCell>{domain.source_format}</TableCell>
                    <TableCell>
                      <Chip 
                        label={domain.is_active ? "Active" : "Inactive"} 
                        color={domain.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{domain.owner}</TableCell>
                    <TableCell>{formatDate(domain.created_at)}</TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleViewDomain(domain)}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Export Domain">
                        <IconButton size="small">
                          <ExportIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Analyze Domain">
                        <IconButton size="small">
                          <AnalyticsIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Toggle Status">
                        <IconButton 
                          size="small" 
                          onClick={() => handleToggleDomainStatus(domain)}
                          disabled={actionLoading}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Domain">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteDialog(domain)}
                          disabled={actionLoading}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={totalDomains}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[5, 10, 25]}
        />
      </Paper>
      
      {/* Domain Details Dialog */}
      {dialogMode === 'view' && (
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {selectedDomain?.name} - {selectedDomain?.description}
          </DialogTitle>
          <DialogContent>
            {detailsLoading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : domainDetails ? (
              <>
                <Grid container spacing={3}>
                  {/* Basic Information */}
                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Basic Information
                      </Typography>
                      <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Domain
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.name}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Description
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.description}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Source Format
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.source_format}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Records
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.record_count.toLocaleString()}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Variables
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.variable_count}
                          </Typography>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                          <Typography variant="body2" color="text.secondary">
                            Owner
                          </Typography>
                          <Typography variant="body1">
                            {domainDetails.owner}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>
                  
                  {/* Schema */}
                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Schema
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Name</TableCell>
                              <TableCell>Label</TableCell>
                              <TableCell>Data Type</TableCell>
                              <TableCell>Required</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {domainDetails.schema.columns.map((column) => (
                              <TableRow key={column.name}>
                                <TableCell>{column.name}</TableCell>
                                <TableCell>{column.label}</TableCell>
                                <TableCell>{column.datatype}</TableCell>
                                <TableCell>
                                  {column.required ? (
                                    <Chip label="Required" size="small" color="primary" />
                                  ) : (
                                    <Chip label="Optional" size="small" variant="outlined" />
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Paper>
                  </Grid>
                  
                  {/* Sample Data */}
                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Sample Data
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              {Object.keys(domainDetails.sample_data[0] || {}).map((key) => (
                                <TableCell key={key}>{key}</TableCell>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {domainDetails.sample_data.map((row, index) => (
                              <TableRow key={index}>
                                {Object.values(row).map((value, valueIndex) => (
                                  <TableCell key={valueIndex}>{value}</TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Paper>
                  </Grid>
                  
                  {/* Relationships */}
                  <Grid item xs={12}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="h6" gutterBottom>
                        Relationships
                      </Typography>
                      {domainDetails.relationships_data?.related_domains?.length > 0 ? (
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow>
                                <TableCell>Related Domain</TableCell>
                                <TableCell>Key</TableCell>
                                <TableCell>Relationship Type</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {domainDetails.relationships_data.related_domains.map((rel, index) => (
                                <TableRow key={index}>
                                  <TableCell>{rel.domain}</TableCell>
                                  <TableCell>{rel.key}</TableCell>
                                  <TableCell>{rel.relationship}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No relationships defined
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                </Grid>
              </>
            ) : (
              <Typography variant="body1" color="text.secondary">
                No domain details available
              </Typography>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Close</Button>
            <Button 
              variant="outlined" 
              startIcon={<DownloadIcon />}
              disabled={!domainDetails}
            >
              Download Data
            </Button>
            <Button 
              variant="contained" 
              startIcon={<AnalyticsIcon />}
              disabled={!domainDetails}
            >
              Analyze
            </Button>
          </DialogActions>
        </Dialog>
      )}
      
      {/* Delete Domain Dialog */}
      {dialogMode === 'delete' && (
        <Dialog open={openDialog} onClose={handleCloseDialog}>
          <DialogTitle>Delete Domain</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete domain <strong>{selectedDomain?.name}</strong> ({selectedDomain?.description})? This will permanently remove all associated data and cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleDeleteDomain} 
              color="error" 
              variant="contained" 
              disabled={actionLoading}
            >
              {actionLoading ? <CircularProgress size={24} /> : 'Delete'}
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Container>
  );
};

export default DomainManagement;
