import React, { useState, useEffect } from 'react';
import { 
  Box, Typography, Paper, Button, Grid, TextField, FormControl, 
  InputLabel, Select, MenuItem, FormControlLabel, Switch, Alert,
  CircularProgress, Divider, Chip, Card, CardContent, Accordion,
  AccordionSummary, AccordionDetails, LinearProgress, Tooltip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import DownloadIcon from '@mui/icons-material/Download';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';

import { getDomains, generateData, getGenerationStatus, downloadGeneratedData } from '../services/api';

// Generation mode options
const generationModes = [
  { value: "random", label: "Random", description: "Generate data randomly based on constraints" },
  { value: "statistical", label: "Statistical", description: "Generate data based on statistical distributions from source data" }
];

const DataGeneration = () => {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [generationMode, setGenerationMode] = useState('random');
  const [recordCount, setRecordCount] = useState(100);
  const [seed, setSeed] = useState('');
  const [preserveRelationships, setPreserveRelationships] = useState(true);
  const [generatingData, setGeneratingData] = useState(false);
  const [error, setError] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [pollingIntervals, setPollingIntervals] = useState({});

  useEffect(() => {
    fetchDomains();
    
    // Also fetch any existing jobs
    fetchJobs();
    
    // Clean up polling intervals
    return () => {
      Object.values(pollingIntervals).forEach(interval => clearInterval(interval));
    };
  }, []);
  
  // Initialize with default domains even before API loads
  useEffect(() => {
    // Default domains if API is slow or fails
    const defaultDomains = [
      { name: 'Demographics', description: 'Patient demographic information' },
      { name: 'Vitals', description: 'Patient vital signs measurements including weight, height, and BMI across visits' },
      { name: 'Labs', description: 'Laboratory test results including glucose, HbA1c, and cholesterol measurements' }
    ];
    
    if (domains.length === 0 && loading) {
      // Set default domains while waiting for real domains
      setDomains(defaultDomains);
      setLoading(false); // Ensure dropdown is enabled even if API is slow
    }
  }, [domains, loading]);

  const fetchDomains = async () => {
    try {
      setLoading(true);
      const domainsData = await getDomains();
      if (Array.isArray(domainsData) && domainsData.length > 0) {
        setDomains(domainsData);
      } else {
        // If API returns empty array, use default domains
        setDomains([
          { name: 'Demographics', description: 'Patient demographic information' },
          { name: 'Vitals', description: 'Patient vital signs measurements including weight, height, and BMI across visits' },
          { name: 'Labs', description: 'Laboratory test results including glucose, HbA1c, and cholesterol measurements' }
        ]);
      }
    } catch (error) {
      console.error('Error fetching domains:', error);
      setError('Using default domains due to API error');
      // If API fails, use default domains
      setDomains([
        { name: 'Demographics', description: 'Patient demographic information' },
        { name: 'Vitals', description: 'Patient vital signs measurements including weight, height, and BMI across visits' },
        { name: 'Labs', description: 'Laboratory test results including glucose, HbA1c, and cholesterol measurements' }
      ]);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchJobs = async () => {
    try {
      // Try to get jobs status for common domains
      const domains = ['Demographics', 'Vitals', 'Labs'];
      const jobsData = [];
      
      for (const domain of domains) {
        try {
          const jobId = `gen_${domain}_random`;
          const status = await getGenerationStatus(jobId);
          
          if (status) {
            jobsData.push({
              job_id: jobId,
              domain_name: domain,
              status: status.status.toUpperCase(),
              generation_mode: 'random',
              record_count: 100,
              created_at: new Date().toISOString(),
            });
          }
        } catch (e) {
          // Ignore errors for individual job status checks
          console.log(`No existing job for domain ${domain}`);
        }
      }
      
      if (jobsData.length > 0) {
        setJobs(jobsData);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    }
  };

  const handleGenerate = async () => {
    if (!selectedDomain) {
      setError('Please select a domain');
      return;
    }

    setError(null);
    setGeneratingData(true);

    try {
      const generationRequest = {
        domain_name: selectedDomain,
        generation_mode: generationMode,
        record_count: parseInt(recordCount),
        seed: seed ? parseInt(seed) : null,
        preserve_relationships: preserveRelationships,
        register_domain: true
      };

      const result = await generateData(generationRequest);
      
      // Add job to jobs list
      const newJob = {
        job_id: result.job_id,
        domain_name: selectedDomain,
        generation_mode: generationMode,
        status: result.status,
        record_count: recordCount,
        start_time: new Date().toISOString(),
        quality_score: null,
        error_message: null
      };
      
      setJobs(prevJobs => [newJob, ...prevJobs]);
      
      // Set up polling for job status
      startPollingJobStatus(result.job_id);
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to start generation job');
    } finally {
      setGeneratingData(false);
    }
  };

  const startPollingJobStatus = (jobId) => {
    // Poll every 2 seconds
    const intervalId = setInterval(async () => {
      try {
        const status = await getGenerationStatus(jobId);
        
        // Update job in list
        setJobs(prevJobs => 
          prevJobs.map(job => 
            job.job_id === jobId 
              ? { 
                  ...job, 
                  status: status.status,
                  record_count: status.record_count || job.record_count,
                  quality_score: status.quality_score,
                  error_message: status.error_message
                }
              : job
          )
        );
        
        // If job is completed or failed, stop polling
        if (status.status === 'COMPLETED' || status.status === 'FAILED') {
          clearInterval(pollingIntervals[jobId]);
          setPollingIntervals(prev => {
            const newIntervals = {...prev};
            delete newIntervals[jobId];
            return newIntervals;
          });
        }
      } catch (error) {
        console.error(`Error polling job status for ${jobId}:`, error);
      }
    }, 2000);
    
    // Save interval ID
    setPollingIntervals(prev => ({
      ...prev,
      [jobId]: intervalId
    }));
  };

  const handleDownload = async (domainName) => {
    try {
      setError(null);
      await downloadGeneratedData(domainName);
      // The downloadGeneratedData function now handles the file download process directly
    } catch (error) {
      console.error(`Error downloading data for domain ${domainName}:`, error);
      setError(`Failed to download data: ${error.message || error}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'RUNNING':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircleIcon color="success" />;
      case 'FAILED':
        return <ErrorIcon color="error" />;
      case 'RUNNING':
        return <CircularProgress size={16} />;
      default:
        return <HourglassEmptyIcon color="disabled" />;
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Generation
      </Typography>
      
      {/* Generation Form */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Generate Synthetic Data
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="domain-select-label">Select Domain</InputLabel>
              <Select
                labelId="domain-select-label"
                id="domain-select"
                value={selectedDomain}
                label="Select Domain"
                onChange={(e) => setSelectedDomain(e.target.value)}
                disabled={false} // Always enable the dropdown
              >
                {domains.map((domain, index) => {
                  // Handle case where domain object doesn't have a name property
                  const domainName = domain?.name || (domain?.domain_name) || `Domain ${index+1}`;
                  const description = domain?.description || 'No description';
                  
                  return (
                    <MenuItem key={domainName} value={domainName}>
                      {domainName} ({description})
                    </MenuItem>
                  );
                })}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="generation-mode-label">Generation Mode</InputLabel>
              <Select
                labelId="generation-mode-label"
                id="generation-mode"
                value={generationMode}
                label="Generation Mode"
                onChange={(e) => setGenerationMode(e.target.value)}
              >
                {generationModes.map((mode) => (
                  <MenuItem key={mode.value} value={mode.value}>
                    {mode.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Record Count"
              value={recordCount}
              onChange={(e) => setRecordCount(e.target.value)}
              inputProps={{ min: 1 }}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Random Seed (Optional)"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder="Leave empty for random seed"
              helperText="Use the same seed for reproducible results"
            />
          </Grid>
          
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={preserveRelationships}
                  onChange={(e) => setPreserveRelationships(e.target.checked)}
                  color="primary"
                />
              }
              label="Preserve Relationships with Other Domains"
            />
          </Grid>
          
          <Grid item xs={12}>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="subtitle1" sx={{ mr: 1 }}>
                  Generation Mode:
                </Typography>
                <Chip
                  label={generationModes.find(m => m.value === generationMode)?.label || generationMode}
                  color="primary"
                  variant="outlined"
                />
                <Tooltip title={generationModes.find(m => m.value === generationMode)?.description || ""}>
                  <InfoIcon color="action" sx={{ ml: 1 }} />
                </Tooltip>
              </Box>
              
              <Button
                variant="contained"
                color="primary"
                startIcon={<AutoFixHighIcon />}
                disabled={!selectedDomain || generatingData}
                onClick={handleGenerate}
              >
                {generatingData ? <CircularProgress size={24} /> : 'Generate Data'}
              </Button>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}
          </Grid>
        </Grid>
      </Paper>
      
      {/* Generation Jobs */}
      <Typography variant="h6" gutterBottom>
        Generation Jobs
      </Typography>
      
      {jobs.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No generation jobs have been submitted yet.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Use the form above to generate synthetic data.
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {jobs.map((job) => (
            <Grid item xs={12} key={job.job_id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box>
                      <Typography variant="h6">
                        {job.domain_name} 
                        <Chip
                          size="small"
                          label={job.status}
                          color={getStatusColor(job.status)}
                          sx={{ ml: 2 }}
                          icon={getStatusIcon(job.status)}
                        />
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Job ID: {job.job_id} | Mode: {job.generation_mode} | Records: {job.record_count}
                      </Typography>
                    </Box>
                    
                    {job.status === 'COMPLETED' && (
                      <Button
                        variant="outlined"
                        startIcon={<DownloadIcon />}
                        onClick={() => handleDownload(job.domain_name)}
                      >
                        Download
                      </Button>
                    )}
                  </Box>
                  
                  {job.status === 'RUNNING' && (
                    <Box sx={{ width: '100%', mb: 2 }}>
                      <LinearProgress />
                    </Box>
                  )}
                  
                  {job.error_message && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {job.error_message}
                    </Alert>
                  )}
                  
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Start Time:
                      </Typography>
                      <Typography variant="body1">
                        {new Date(job.start_time).toLocaleString()}
                      </Typography>
                    </Grid>
                    
                    {job.quality_score !== null && job.quality_score !== undefined && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Quality Score:
                        </Typography>
                        <Typography variant="body1">
                          {Number(job.quality_score).toFixed(2)}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Generation Info */}
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          About Data Generation
        </Typography>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Random Generation</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2">
              Random generation creates synthetic data based on variable constraints without requiring source data.
              It's useful for creating test datasets when no reference data is available.
              The generated values will follow the specified constraints but won't reflect real-world distributions.
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Statistical Generation</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2">
              Statistical generation analyzes source data to identify distributions and patterns,
              then generates new synthetic data that preserves these statistical properties.
              This method requires source data and produces more realistic results that maintain
              the characteristics of the original dataset while ensuring no actual patient data is exposed.
            </Typography>
          </AccordionDetails>
        </Accordion>
        
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Relationship Preservation</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2">
              When enabled, relationship preservation maintains connections between domains,
              such as ensuring patient demographics match across different domain tables.
              This creates a more coherent synthetic dataset that reflects the same cross-domain
              relationships present in real clinical data.
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Paper>
    </Box>
  );
};

export default DataGeneration;
