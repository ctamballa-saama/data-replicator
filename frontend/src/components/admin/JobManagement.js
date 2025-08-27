/**
 * Job Management component for DataReplicator Admin
 * 
 * Provides monitoring and control of data generation jobs
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
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  LinearProgress,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Visibility as ViewIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

// Mock job data
const mockJobs = [
  { id: 'job123', job_id: 'gen_Demographics_random', domain_name: 'Demographics', generation_mode: 'random', record_count: 500, status: 'completed', progress: 100, quality_score: 92.5, owner: 'john.doe', created_at: '2025-08-26T10:15:00Z', completed_at: '2025-08-26T10:16:30Z' },
  { id: 'job124', job_id: 'gen_AE_statistical', domain_name: 'AE', generation_mode: 'statistical', record_count: 1200, status: 'completed', progress: 100, quality_score: 87.8, owner: 'jane.smith', created_at: '2025-08-26T14:20:00Z', completed_at: '2025-08-26T14:22:15Z' },
  { id: 'job125', job_id: 'gen_Labs_random', domain_name: 'Labs', generation_mode: 'random', record_count: 3000, status: 'running', progress: 45, quality_score: null, owner: 'mark.wilson', created_at: '2025-08-27T09:30:00Z', completed_at: null },
  { id: 'job126', job_id: 'gen_VS_statistical', domain_name: 'VS', generation_mode: 'statistical', record_count: 2500, status: 'pending', progress: 0, quality_score: null, owner: 'sarah.jones', created_at: '2025-08-27T11:45:00Z', completed_at: null },
  { id: 'job127', job_id: 'gen_CM_random', domain_name: 'CM', generation_mode: 'random', record_count: 800, status: 'failed', progress: 60, quality_score: null, owner: 'chris.adams', created_at: '2025-08-27T08:15:00Z', completed_at: '2025-08-27T08:17:45Z' },
];

// Mock API functions
const fetchJobs = async (page, rowsPerPage, filters) => {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  let filteredJobs = [...mockJobs];
  
  // Apply filters
  if (filters.status && filters.status !== 'all') {
    filteredJobs = filteredJobs.filter(job => job.status === filters.status);
  }
  
  if (filters.domain) {
    filteredJobs = filteredJobs.filter(job => 
      job.domain_name.toLowerCase().includes(filters.domain.toLowerCase())
    );
  }
  
  if (filters.search) {
    filteredJobs = filteredJobs.filter(job => 
      job.job_id.toLowerCase().includes(filters.search.toLowerCase()) ||
      job.domain_name.toLowerCase().includes(filters.search.toLowerCase()) ||
      job.owner.toLowerCase().includes(filters.search.toLowerCase())
    );
  }
  
  // Sort by created_at descending
  filteredJobs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  
  // Paginate
  const paginatedJobs = filteredJobs.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return {
    jobs: paginatedJobs,
    totalCount: filteredJobs.length
  };
};

const fetchJobDetails = async (jobId) => {
  await new Promise(resolve => setTimeout(resolve, 800));
  
  const job = mockJobs.find(j => j.id === jobId);
  
  if (!job) {
    throw new Error('Job not found');
  }
  
  // Add more mock details
  return {
    ...job,
    description: `Generate synthetic ${job.domain_name} data using ${job.generation_mode} mode`,
    preserve_relationships: true,
    config: {
      seed: 42,
      distribution_method: 'gaussian',
      missing_value_rate: 0.05,
    },
    error_message: job.status === 'failed' ? 'Error generating data: Invalid distribution parameters' : null,
    result_file: job.status === 'completed' ? `/generated_data/${job.domain_name}_${job.job_id}.csv` : null,
    result_summary: job.status === 'completed' ? {
      record_count: job.record_count,
      variable_count: 24,
      missing_values: Math.floor(job.record_count * 0.05),
      data_quality: {
        completeness: job.quality_score,
        consistency: job.quality_score - 5,
        accuracy: job.quality_score + 2,
      }
    } : null,
    logs: [
      { timestamp: job.created_at, message: `Job created: ${job.job_id}` },
      { timestamp: new Date(new Date(job.created_at).getTime() + 10000).toISOString(), message: 'Initializing data generation' },
      { timestamp: new Date(new Date(job.created_at).getTime() + 20000).toISOString(), message: 'Loading domain schema' },
      { timestamp: new Date(new Date(job.created_at).getTime() + 30000).toISOString(), message: 'Generating synthetic data' },
      ...(job.status === 'completed' ? [{ timestamp: job.completed_at, message: 'Job completed successfully' }] : []),
      ...(job.status === 'failed' ? [{ timestamp: job.completed_at, message: 'Error: Invalid distribution parameters' }] : []),
    ]
  };
};

const cancelJob = async (jobId) => {
  await new Promise(resolve => setTimeout(resolve, 600));
  return { success: true };
};

const deleteJob = async (jobId) => {
  await new Promise(resolve => setTimeout(resolve, 600));
  return { success: true };
};

const JobManagement = () => {
  // State
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalJobs, setTotalJobs] = useState(0);
  
  // Filters
  const [filters, setFilters] = useState({
    status: 'all',
    domain: '',
    search: '',
  });
  
  // Job details dialog
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  
  // Action state
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Load jobs
  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchJobs(page, rowsPerPage, filters);
      setJobs(data.jobs);
      setTotalJobs(data.totalCount);
    } catch (err) {
      console.error('Error loading jobs:', err);
      setError('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load and on filter/page change
  useEffect(() => {
    loadJobs();
  }, [page, rowsPerPage, filters.status]);
  
  // Apply search and domain filters on button click or Enter key
  const applyFilters = () => {
    setPage(0); // Reset to first page
    loadJobs();
  };
  
  // Handle filter change
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-apply status filter
    if (name === 'status') {
      setPage(0);
    }
  };
  
  // Handle view job details
  const handleViewJob = async (job) => {
    setSelectedJob(job);
    setDetailsDialogOpen(true);
    setJobDetails(null);
    
    try {
      setDetailsLoading(true);
      const details = await fetchJobDetails(job.id);
      setJobDetails(details);
    } catch (err) {
      console.error('Error loading job details:', err);
      setError('Failed to load job details');
    } finally {
      setDetailsLoading(false);
    }
  };
  
  // Handle cancel job
  const handleCancelJob = async (job) => {
    try {
      setActionLoading(true);
      await cancelJob(job.id);
      
      // Update job status locally
      setJobs(jobs.map(j => 
        j.id === job.id ? { ...j, status: 'failed', progress: j.progress } : j
      ));
      
      setSuccessMessage(`Job ${job.job_id} cancelled successfully`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error cancelling job:', err);
      setError('Failed to cancel job');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Handle delete job
  const handleDeleteJob = async (job) => {
    if (!window.confirm(`Are you sure you want to delete job ${job.job_id}?`)) {
      return;
    }
    
    try {
      setActionLoading(true);
      await deleteJob(job.id);
      
      // Remove job locally
      setJobs(jobs.filter(j => j.id !== job.id));
      setTotalJobs(prev => prev - 1);
      
      setSuccessMessage(`Job ${job.job_id} deleted successfully`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error deleting job:', err);
      setError('Failed to delete job');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };
  
  // Get status chip color
  const getStatusChipColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'pending': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Job Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Monitor and manage data generation jobs
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
            <InputLabel id="status-filter-label">Status</InputLabel>
            <Select
              labelId="status-filter-label"
              name="status"
              value={filters.status}
              label="Status"
              onChange={handleFilterChange}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="running">Running</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>
          
          <TextField
            placeholder="Domain name..."
            variant="outlined"
            size="small"
            name="domain"
            value={filters.domain}
            onChange={handleFilterChange}
            label="Domain"
            sx={{ width: 180 }}
          />
          
          <TextField
            placeholder="Search jobs..."
            variant="outlined"
            size="small"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            onKeyPress={(e) => e.key === 'Enter' && applyFilters()}
            label="Search"
            sx={{ flex: 1, minWidth: 180 }}
          />
          
          <Button 
            variant="contained" 
            onClick={applyFilters}
            disabled={loading}
          >
            Apply Filters
          </Button>
          
          <Tooltip title="Refresh">
            <IconButton onClick={loadJobs} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
      
      {/* Jobs Table */}
      <Paper sx={{ width: '100%', mb: 4 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Job ID</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Records</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Created</TableCell>
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
              ) : jobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1">No jobs found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                jobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell>{job.job_id}</TableCell>
                    <TableCell>{job.domain_name}</TableCell>
                    <TableCell>{job.generation_mode}</TableCell>
                    <TableCell>{job.record_count.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={job.status}
                        color={getStatusChipColor(job.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: 100 }}>
                        <Box sx={{ width: '100%', mr: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={job.progress} 
                            color={job.status === 'failed' ? 'error' : 'primary'}
                          />
                        </Box>
                        <Box sx={{ minWidth: 35 }}>
                          <Typography variant="body2" color="text.secondary">
                            {`${Math.round(job.progress)}%`}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {job.quality_score ? job.quality_score.toFixed(1) : 'N/A'}
                    </TableCell>
                    <TableCell>{formatDate(job.created_at)}</TableCell>
                    <TableCell>{job.owner}</TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleViewJob(job)}>
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      
                      {job.status === 'completed' && (
                        <Tooltip title="Download Results">
                          <IconButton size="small">
                            <DownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      {(job.status === 'running' || job.status === 'pending') && (
                        <Tooltip title="Cancel Job">
                          <IconButton 
                            size="small" 
                            onClick={() => handleCancelJob(job)}
                            disabled={actionLoading}
                          >
                            <StopIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      
                      <Tooltip title="Delete Job">
                        <IconButton 
                          size="small" 
                          onClick={() => handleDeleteJob(job)}
                          disabled={actionLoading || job.status === 'running'}
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
          count={totalJobs}
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
      
      {/* Job Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Job Details: {selectedJob?.job_id}
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : jobDetails ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Basic Information
                </Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ width: '30%', fontWeight: 'bold' }}>
                          Job ID
                        </TableCell>
                        <TableCell>{jobDetails.job_id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Description
                        </TableCell>
                        <TableCell>{jobDetails.description}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Domain
                        </TableCell>
                        <TableCell>{jobDetails.domain_name}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Generation Mode
                        </TableCell>
                        <TableCell>{jobDetails.generation_mode}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Records
                        </TableCell>
                        <TableCell>{jobDetails.record_count.toLocaleString()}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Status
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={jobDetails.status}
                            color={getStatusChipColor(jobDetails.status)}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Created At
                        </TableCell>
                        <TableCell>{formatDate(jobDetails.created_at)}</TableCell>
                      </TableRow>
                      {jobDetails.completed_at && (
                        <TableRow>
                          <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                            Completed At
                          </TableCell>
                          <TableCell>{formatDate(jobDetails.completed_at)}</TableCell>
                        </TableRow>
                      )}
                      <TableRow>
                        <TableCell component="th" scope="row" sx={{ fontWeight: 'bold' }}>
                          Owner
                        </TableCell>
                        <TableCell>{jobDetails.owner}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
              
              {/* Show additional sections based on job status */}
              {jobDetails.status === 'failed' && jobDetails.error_message && (
                <Alert severity="error">
                  <Typography variant="subtitle2">Error:</Typography>
                  {jobDetails.error_message}
                </Alert>
              )}
              
              {jobDetails.status === 'completed' && jobDetails.result_summary && (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Result Summary
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="body2">
                      <strong>Records:</strong> {jobDetails.result_summary.record_count.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Variables:</strong> {jobDetails.result_summary.variable_count}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Missing Values:</strong> {jobDetails.result_summary.missing_values.toLocaleString()} 
                      ({(jobDetails.result_summary.missing_values / jobDetails.result_summary.record_count * 100).toFixed(1)}%)
                    </Typography>
                    
                    <Typography variant="subtitle2" sx={{ mt: 1 }}>
                      Quality Metrics:
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                      <Chip 
                        label={`Completeness: ${jobDetails.result_summary.data_quality.completeness.toFixed(1)}%`}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                      <Chip 
                        label={`Consistency: ${jobDetails.result_summary.data_quality.consistency.toFixed(1)}%`}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                      <Chip 
                        label={`Accuracy: ${jobDetails.result_summary.data_quality.accuracy.toFixed(1)}%`}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Paper>
                </Box>
              )}
              
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Job Logs
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 1, 
                    maxHeight: 200, 
                    overflowY: 'auto',
                    bgcolor: 'rgba(0, 0, 0, 0.03)' 
                  }}
                >
                  {jobDetails.logs.map((log, index) => (
                    <Box key={index} sx={{ mb: 0.5, fontFamily: 'monospace', fontSize: '0.85rem' }}>
                      <Typography component="span" sx={{ color: 'text.secondary', mr: 1 }}>
                        [{formatDate(log.timestamp)}]
                      </Typography>
                      <Typography component="span">
                        {log.message}
                      </Typography>
                    </Box>
                  ))}
                </Paper>
              </Box>
            </Box>
          ) : (
            <Typography>No job details available</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>
            Close
          </Button>
          {jobDetails?.status === 'completed' && (
            <Button 
              variant="contained" 
              startIcon={<DownloadIcon />}
            >
              Download Results
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default JobManagement;
