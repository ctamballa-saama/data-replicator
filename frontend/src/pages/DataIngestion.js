import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, Typography, Paper, Button, Grid, Alert, 
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Divider
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

import { uploadData, getDomains } from '../services/api';

const DataIngestion = () => {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const data = await getDomains();
      setDomains(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching domains:', error);
      setLoading(false);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadSuccess(null);
    setUploadError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setUploadSuccess(null);
    setUploadError(null);

    try {
      const result = await uploadData(selectedFile);
      setUploadSuccess(`Successfully uploaded ${result.domain_name} with ${result.record_count} records.`);
      setSelectedFile(null);
      // Refresh the domains list
      fetchDomains();
    } catch (error) {
      setUploadError(error.response?.data?.detail || 'Error uploading file. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Ingestion
      </Typography>
      
      {/* Upload Section */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Upload Clinical Data Files
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Upload CSV files containing clinical data. Each file will be processed as a separate domain.
          File name will be used as the domain name (e.g., DM.csv → DM domain).
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2, mb: 3 }}>
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUploadIcon />}
          >
            Select File
            <input
              type="file"
              accept=".csv"
              hidden
              onChange={handleFileChange}
            />
          </Button>
          
          {selectedFile && (
            <Typography variant="body2">
              Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
            </Typography>
          )}
          
          <Button
            variant="contained"
            color="primary"
            disabled={!selectedFile || uploading}
            onClick={handleUpload}
            sx={{ ml: 'auto' }}
          >
            {uploading ? <CircularProgress size={24} /> : 'Upload'}
          </Button>
        </Box>
        
        {uploadSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {uploadSuccess}
          </Alert>
        )}
        
        {uploadError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {uploadError}
          </Alert>
        )}
      </Paper>
      
      {/* Domains Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Ingested Domains
        </Typography>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : domains.length === 0 ? (
          <Alert severity="info">
            No domains available. Upload data files to get started.
          </Alert>
        ) : (
          <TableContainer>
            <Table aria-label="domains table">
              <TableHead>
                <TableRow>
                  <TableCell>Domain Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Records</TableCell>
                  <TableCell align="right">Variables</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {domains.map((domain) => (
                  <TableRow key={domain.name}>
                    <TableCell component="th" scope="row">
                      <strong>{domain.name}</strong>
                    </TableCell>
                    <TableCell>{domain.description || '-'}</TableCell>
                    <TableCell align="right">{domain.record_count}</TableCell>
                    <TableCell align="right">{domain.variable_count}</TableCell>
                    <TableCell align="center">
                      <Button 
                        size="small" 
                        onClick={() => navigate(`/domain/${domain.name}`)}
                        sx={{ mx: 1 }}
                      >
                        View
                      </Button>
                      <Button 
                        size="small"
                        color="primary" 
                        onClick={() => navigate(`/data-analysis?domain=${domain.name}`)}
                        sx={{ mx: 1 }}
                      >
                        Analyze
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Data Import Guidelines */}
      <Paper sx={{ p: 3, mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Data Import Guidelines
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              File Format Requirements:
            </Typography>
            <ul>
              <li>CSV format with header row</li>
              <li>UTF-8 encoding recommended</li>
              <li>First row should contain variable names</li>
              <li>Date format: YYYY-MM-DD or MM/DD/YYYY</li>
              <li>Missing values can be empty or "NULL"</li>
            </ul>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Best Practices:
            </Typography>
            <ul>
              <li>Use CDISC domain naming conventions</li>
              <li>Ensure consistent data types per column</li>
              <li>Include subject IDs for relationship mapping</li>
              <li>Check for duplicate records before upload</li>
              <li>Verify date formats are consistent</li>
            </ul>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default DataIngestion;
