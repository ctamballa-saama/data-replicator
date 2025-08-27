/**
 * Export Management component for DataReplicator Admin
 * 
 * Allows administrators to manage and monitor data exports
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
  TextField,
  CircularProgress,
  Alert,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  FilterAlt as FilterIcon,
} from '@mui/icons-material';

// Mock API functions
const fetchExports = async (page, rowsPerPage, filters) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock export data
  const allExports = [
    { id: 'exp-001', name: 'Demographics_Export_01', domain_name: 'DM', format: 'CSV', record_count: 850, file_size: 56320, status: 'completed', created_at: '2025-08-25T14:30:00Z', owner: 'john.doe', download_count: 5 },
    { id: 'exp-002', name: 'AE_Export_Statistical', domain_name: 'AE', format: 'SAS', record_count: 1240, file_size: 128500, status: 'completed', created_at: '2025-08-26T09:15:00Z', owner: 'jane.smith', download_count: 3 },
    { id: 'exp-003', name: 'Labs_Export_Full', domain_name: 'LB', format: 'Excel', record_count: 7850, file_size: 950000, status: 'completed', created_at: '2025-08-26T16:45:00Z', owner: 'mark.wilson', download_count: 8 },
    { id: 'exp-004', name: 'VS_Export_Sample', domain_name: 'VS', format: 'CSV', record_count: 500, file_size: 42000, status: 'completed', created_at: '2025-08-27T10:20:00Z', owner: 'sarah.jones', download_count: 2 },
    { id: 'exp-005', name: 'CM_Export_Full', domain_name: 'CM', format: 'CSV', record_count: 1920, file_size: 215000, status: 'failed', created_at: '2025-08-27T11:30:00Z', owner: 'alex.brown', download_count: 0 },
    { id: 'exp-006', name: 'DM_AE_Export_Combined', domain_name: 'Multiple', format: 'SAS', record_count: 2090, file_size: 310000, status: 'processing', created_at: '2025-08-27T12:05:00Z', owner: 'emily.davis', download_count: 0 },
  ];
  
  // Filter exports
  let filteredExports = [...allExports];
  
  if (filters.search) {
    const searchTerm = filters.search.toLowerCase();
    filteredExports = filteredExports.filter(exp => 
      exp.name.toLowerCase().includes(searchTerm) ||
      exp.domain_name.toLowerCase().includes(searchTerm) ||
      exp.owner.toLowerCase().includes(searchTerm)
    );
  }
  
  if (filters.format && filters.format !== 'all') {
    filteredExports = filteredExports.filter(exp => exp.format === filters.format);
  }
  
  if (filters.status && filters.status !== 'all') {
    filteredExports = filteredExports.filter(exp => exp.status === filters.status);
  }
  
  // Sort by created_at descending
  filteredExports.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  
  // Paginate
  const paginatedExports = filteredExports.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return {
    exports: paginatedExports,
    totalCount: filteredExports.length
  };
};

const fetchExportDetails = async (exportId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock export details
  return {
    id: exportId,
    name: 'Demographics_Export_01',
    domain_name: 'DM',
    format: 'CSV',
    record_count: 850,
    file_size: 56320,
    status: 'completed',
    created_at: '2025-08-25T14:30:00Z',
    completed_at: '2025-08-25T14:31:15Z',
    owner: 'john.doe',
    download_count: 5,
    last_downloaded: '2025-08-26T10:15:00Z',
    description: 'Full export of Demographics domain with all variables',
    config: {
      included_variables: ['USUBJID', 'AGE', 'SEX', 'RACE', 'COUNTRY', 'SITEID'],
      filters: { 'AGE': '> 18' },
      sort_by: 'USUBJID',
      include_header: true,
      delimiter: ',',
    },
    metadata: {
      source_domain: 'DM',
      source_file: 'dm_generation_job123.csv',
      generation_job_id: 'job123',
      quality_score: 92.5,
    },
    file_path: '/generated_data/exports/DM_export_001.csv',
    preview_data: [
      ['USUBJID', 'AGE', 'SEX', 'RACE', 'COUNTRY', 'SITEID'],
      ['001-001', '45', 'M', 'WHITE', 'USA', '001'],
      ['001-002', '52', 'F', 'BLACK OR AFRICAN AMERICAN', 'USA', '001'],
      ['001-003', '38', 'M', 'ASIAN', 'JPN', '002'],
    ]
  };
};

const deleteExport = async (exportId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 600));
  return { success: true };
};

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

const ExportManagement = () => {
  // State
  const [exports, setExports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalExports, setTotalExports] = useState(0);
  
  // Filters
  const [filters, setFilters] = useState({
    status: 'all',
    format: 'all',
    search: '',
  });
  
  // Export details dialog
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedExport, setSelectedExport] = useState(null);
  const [exportDetails, setExportDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  
  // Action state
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Load exports
  const loadExports = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchExports(page, rowsPerPage, filters);
      setExports(data.exports);
      setTotalExports(data.totalCount);
    } catch (err) {
      console.error('Error loading exports:', err);
      setError('Failed to load exports. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load and on filter/page change
  useEffect(() => {
    loadExports();
  }, [page, rowsPerPage, filters.status, filters.format]);
  
  // Apply search filter
  const handleSearch = () => {
    setPage(0);
    loadExports();
  };
  
  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-apply status and format filters
    if (name === 'status' || name === 'format') {
      setPage(0);
    }
  };
  
  // Handle view export details
  const handleViewExport = async (exportItem) => {
    setSelectedExport(exportItem);
    setDetailsDialogOpen(true);
    setExportDetails(null);
    
    try {
      setDetailsLoading(true);
      const details = await fetchExportDetails(exportItem.id);
      setExportDetails(details);
    } catch (err) {
      console.error('Error loading export details:', err);
      setError('Failed to load export details. Please try again.');
    } finally {
      setDetailsLoading(false);
    }
  };
  
  // Handle delete export
  const handleDeleteExport = async (exportItem) => {
    if (!window.confirm(`Are you sure you want to delete export "${exportItem.name}"?`)) {
      return;
    }
    
    try {
      setActionLoading(true);
      await deleteExport(exportItem.id);
      
      // Remove export locally
      setExports(exports.filter(e => e.id !== exportItem.id));
      setTotalExports(prev => prev - 1);
      
      setSuccessMessage(`Export "${exportItem.name}" deleted successfully`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error deleting export:', err);
      setError('Failed to delete export. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Get status chip color
  const getStatusChipColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'failed': return 'error';
      default: return 'default';
    }
  };
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Export Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage and monitor data exports
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {successMessage && (
        <Alert severity="success" sx={{ mb: 4 }}>
          {successMessage}
        </Alert>
      )}
      
      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, alignItems: 'center' }}>
          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel id="format-filter-label">Format</InputLabel>
            <Select
              labelId="format-filter-label"
              name="format"
              value={filters.format}
              label="Format"
              onChange={handleFilterChange}
            >
              <MenuItem value="all">All Formats</MenuItem>
              <MenuItem value="CSV">CSV</MenuItem>
              <MenuItem value="SAS">SAS</MenuItem>
              <MenuItem value="Excel">Excel</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel id="status-filter-label">Status</InputLabel>
            <Select
              labelId="status-filter-label"
              name="status"
              value={filters.status}
              label="Status"
              onChange={handleFilterChange}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="processing">Processing</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            placeholder="Search exports..."
            variant="outlined"
            size="small"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{
              startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{ width: 250 }}
          />
          
          <Button 
            variant="contained" 
            startIcon={<FilterIcon />}
            onClick={handleSearch}
            disabled={loading}
          >
            Apply Filters
          </Button>
          
          <Tooltip title="Refresh">
            <IconButton onClick={loadExports} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
      
      {/* Exports Table */}
      <Paper sx={{ width: '100%', mb: 4 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Format</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Downloads</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={10} align="center" sx={{ py: 3 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : exports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1">No exports found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                exports.map((exportItem) => (
                  <TableRow key={exportItem.id}>
                    <TableCell>{exportItem.name}</TableCell>
                    <TableCell>{exportItem.domain_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={exportItem.format}
                        size="small"
                        color={
                          exportItem.format === 'CSV' ? 'primary' :
                          exportItem.format === 'SAS' ? 'secondary' : 'default'
                        }
                        variant={exportItem.format === 'Excel' ? 'outlined' : 'filled'}
                      />
                    </TableCell>
                    <TableCell>{exportItem.record_count.toLocaleString()}</TableCell>
                    <TableCell>{formatBytes(exportItem.file_size)}</TableCell>
                    <TableCell>
                      <Chip
                        label={exportItem.status}
                        size="small"
                        color={getStatusChipColor(exportItem.status)}
                      />
                    </TableCell>
                    <TableCell>{formatDate(exportItem.created_at)}</TableCell>
                    <TableCell>{exportItem.download_count}</TableCell>
                    <TableCell>{exportItem.owner}</TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewExport(exportItem)}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      {exportItem.status === 'completed' && (
                        <Tooltip title="Download">
                          <IconButton size="small">
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Delete Export">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteExport(exportItem)}
                          disabled={actionLoading || exportItem.status === 'processing'}
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
          count={totalExports}
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
      
      {/* Export Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Export Details: {selectedExport?.name}
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : exportDetails ? (
            <Grid container spacing={3}>
              {/* Basic Information */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Basic Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Export Name
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.name}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Domain
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.domain_name}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Format
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.format}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Record Count
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.record_count.toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        File Size
                      </Typography>
                      <Typography variant="body1">
                        {formatBytes(exportDetails.file_size)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Download Count
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.download_count}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Created At
                      </Typography>
                      <Typography variant="body1">
                        {formatDate(exportDetails.created_at)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Completed At
                      </Typography>
                      <Typography variant="body1">
                        {formatDate(exportDetails.completed_at)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                      <Typography variant="body2" color="text.secondary">
                        Last Downloaded
                      </Typography>
                      <Typography variant="body1">
                        {formatDate(exportDetails.last_downloaded)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        Description
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.description}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
              
              {/* Export Configuration */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Export Configuration
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        Included Variables
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                        {exportDetails.config.included_variables.map((variable, index) => (
                          <Chip 
                            key={index}
                            label={variable}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Grid>
                    {Object.entries(exportDetails.config.filters || {}).length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">
                          Filters
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                          {Object.entries(exportDetails.config.filters).map(([key, value], index) => (
                            <Chip 
                              key={index}
                              label={`${key} ${value}`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Sort By
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.config.sort_by}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Include Header
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.config.include_header ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Delimiter
                      </Typography>
                      <Typography variant="body1">
                        {exportDetails.config.delimiter === ',' ? 'Comma' : 
                         exportDetails.config.delimiter === ';' ? 'Semicolon' : 
                         exportDetails.config.delimiter === '\t' ? 'Tab' : 
                         exportDetails.config.delimiter}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>
              
              {/* Data Preview */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Data Preview
                  </Typography>
                  <TableContainer sx={{ maxHeight: 300 }}>
                    <Table size="small" stickyHeader>
                      <TableHead>
                        <TableRow>
                          {exportDetails.preview_data[0].map((header, index) => (
                            <TableCell key={index}>{header}</TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {exportDetails.preview_data.slice(1).map((row, rowIndex) => (
                          <TableRow key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <TableCell key={cellIndex}>{cell}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary">
              No export details available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>
            Close
          </Button>
          {exportDetails?.status === 'completed' && (
            <Button 
              variant="contained"
              startIcon={<DownloadIcon />}
            >
              Download
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ExportManagement;
