import React, { useState, useEffect } from 'react';
import { 
  Container, Typography, Paper, Box, Grid, 
  FormControl, InputLabel, MenuItem, Select,
  Button, Chip, Divider, CircularProgress,
  Card, CardContent, Alert, AlertTitle,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useSnackbar } from 'notistack';

import { getDomains, getValidators, validateDomain } from '../services/api';

const ValidationPage = () => {
  const [domains, setDomains] = useState([]);
  const [validators, setValidators] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedValidators, setSelectedValidators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [validationResults, setValidationResults] = useState(null);
  const { enqueueSnackbar } = useSnackbar();

  // Fetch domains and validators on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [domainsData, validatorsData] = await Promise.all([
          getDomains(),
          getValidators()
        ]);
        setDomains(domainsData);
        setValidators(validatorsData);
      } catch (error) {
        console.error('Error fetching initial data:', error);
        enqueueSnackbar('Failed to load validation data', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [enqueueSnackbar]);

  const handleDomainChange = (event) => {
    setSelectedDomain(event.target.value);
    // Reset validation results when domain changes
    setValidationResults(null);
  };

  const handleValidatorChange = (event) => {
    setSelectedValidators(event.target.value);
  };

  const handleValidate = async () => {
    if (!selectedDomain) {
      enqueueSnackbar('Please select a domain to validate', { variant: 'warning' });
      return;
    }

    try {
      setLoading(true);
      const validatorIds = selectedValidators.length > 0 ? selectedValidators : null;
      const results = await validateDomain(selectedDomain, validatorIds);
      setValidationResults(results);
      
      // Show summary notification
      if (results.is_valid) {
        enqueueSnackbar('Validation passed successfully', { variant: 'success' });
      } else {
        const message = `Validation completed with ${results.error_count} errors, ${results.warning_count} warnings`;
        enqueueSnackbar(message, { variant: results.error_count > 0 ? 'error' : 'warning' });
      }
    } catch (error) {
      console.error('Error validating domain:', error);
      enqueueSnackbar(`Failed to validate domain: ${error.message}`, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity.toUpperCase()) {
      case 'ERROR':
        return <ErrorIcon color="error" />;
      case 'WARNING':
        return <WarningIcon color="warning" />;
      case 'INFO':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity.toUpperCase()) {
      case 'ERROR':
        return 'error';
      case 'WARNING':
        return 'warning';
      case 'INFO':
        return 'info';
      default:
        return 'info';
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3, mt: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Data Validation
        </Typography>
        <Typography variant="body1" paragraph>
          Validate your data domains against CDISC standards and custom validation rules.
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={5}>
              <FormControl fullWidth>
                <InputLabel id="domain-select-label">Domain</InputLabel>
                <Select
                  labelId="domain-select-label"
                  id="domain-select"
                  value={selectedDomain}
                  label="Domain"
                  onChange={handleDomainChange}
                  disabled={loading}
                >
                  {domains.map((domain) => (
                    <MenuItem key={domain.domain_name} value={domain.domain_name}>
                      {domain.domain_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={5}>
              <FormControl fullWidth>
                <InputLabel id="validator-select-label">Validators</InputLabel>
                <Select
                  labelId="validator-select-label"
                  id="validator-select"
                  multiple
                  value={selectedValidators}
                  label="Validators"
                  onChange={handleValidatorChange}
                  disabled={loading}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((validatorId) => {
                        const validator = validators.find(v => v.id === validatorId);
                        return (
                          <Chip key={validatorId} label={validator ? validator.name : validatorId} />
                        );
                      })}
                    </Box>
                  )}
                >
                  {validators.map((validator) => (
                    <MenuItem key={validator.id} value={validator.id}>
                      {validator.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button 
                variant="contained" 
                color="primary" 
                fullWidth 
                sx={{ height: '56px' }}
                onClick={handleValidate}
                disabled={loading || !selectedDomain}
              >
                {loading ? <CircularProgress size={24} /> : 'Validate'}
              </Button>
            </Grid>
          </Grid>
        </Box>
        
        {validationResults && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              Validation Results
            </Typography>
            
            <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
              {validationResults.is_valid ? (
                <Alert severity="success" icon={<CheckCircleIcon />}>
                  <AlertTitle>Validation Passed</AlertTitle>
                  The domain {validationResults.domain_name} passed all validation checks.
                </Alert>
              ) : (
                <Alert severity={validationResults.error_count > 0 ? 'error' : 'warning'}>
                  <AlertTitle>
                    {validationResults.error_count > 0 
                      ? `Validation Failed with ${validationResults.error_count} errors` 
                      : `Validation has ${validationResults.warning_count} warnings`}
                  </AlertTitle>
                  <Typography variant="body2">
                    Domain: {validationResults.domain_name}<br />
                    Errors: {validationResults.error_count}<br />
                    Warnings: {validationResults.warning_count}<br />
                    Info: {validationResults.info_count}
                  </Typography>
                </Alert>
              )}
            </Box>

            {validationResults.results.length > 0 && (
              <TableContainer component={Paper} sx={{ mt: 2 }}>
                <Table aria-label="validation results table">
                  <TableHead>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>Rule</TableCell>
                      <TableCell>Field</TableCell>
                      <TableCell>Row</TableCell>
                      <TableCell>Message</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {validationResults.results
                      .sort((a, b) => {
                        // Sort by severity (ERROR, WARNING, INFO)
                        const severityOrder = { ERROR: 0, WARNING: 1, INFO: 2 };
                        return severityOrder[a.severity] - severityOrder[b.severity];
                      })
                      .map((result, index) => (
                        <TableRow
                          key={index}
                          sx={{ 
                            '&:last-child td, &:last-child th': { border: 0 },
                            backgroundColor: result.is_valid ? '' : 'rgba(255, 0, 0, 0.05)'
                          }}
                        >
                          <TableCell>
                            {getSeverityIcon(result.severity)}
                            <Chip 
                              size="small" 
                              label={result.severity} 
                              color={getSeverityColor(result.severity)}
                              sx={{ ml: 1 }}
                            />
                          </TableCell>
                          <TableCell>
                            {result.rule_description}
                            <Typography variant="caption" display="block" color="textSecondary">
                              {result.rule_id}
                            </Typography>
                          </TableCell>
                          <TableCell>{result.field_name || '-'}</TableCell>
                          <TableCell>{result.row_index !== null ? result.row_index + 1 : '-'}</TableCell>
                          <TableCell>{result.error_message || (result.is_valid ? 'Valid' : 'Invalid')}</TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default ValidationPage;
