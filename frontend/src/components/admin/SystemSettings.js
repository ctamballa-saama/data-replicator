/**
 * System Settings component for DataReplicator Admin
 * 
 * Allows configuration of system-wide settings for the application
 */
import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  Paper,
  Typography,
  Divider,
  TextField,
  Switch,
  FormControlLabel,
  Grid,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CardHeader,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  HelpOutline as HelpIcon,
} from '@mui/icons-material';

// Mock API functions
const fetchSettings = async () => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock settings data
  return {
    general: {
      applicationName: 'DataReplicator',
      applicationVersion: '1.0.0',
      maxUploadFileSizeMB: 50,
      defaultPageSize: 20,
      enableDebugMode: false,
    },
    security: {
      sessionTimeoutMinutes: 30,
      passwordMinLength: 8,
      passwordRequireNumbers: true,
      passwordRequireSpecialChars: true,
      allowedFailedLoginAttempts: 5,
      enforcePasswordExpiration: false,
      passwordExpirationDays: 90,
    },
    dataGeneration: {
      maxJobsPerUser: 10,
      maxRecordsPerJob: 100000,
      defaultGenerationMode: 'statistical',
      preserveRelationships: true,
      jobTimeoutMinutes: 60,
      enableAdvancedOptions: true,
      defaultRandomSeed: 42,
    },
    storage: {
      dataRetentionDays: 30,
      maxStoragePerUserMB: 1000,
      autoDeleteCompletedJobs: false,
      autoDeleteAfterDays: 7,
      exportFileFormat: 'CSV',
      compressionEnabled: false,
    },
  };
};

const saveSettings = async (settings) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Return success response
  return { success: true };
};

// TabPanel component for tab content
const TabPanel = (props) => {
  const { children, value, index, ...other } = props;
  
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

// Tab props
const a11yProps = (index) => {
  return {
    id: `settings-tab-${index}`,
    'aria-controls': `settings-tabpanel-${index}`,
  };
};

const SystemSettings = () => {
  // State
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  
  // Load settings on mount
  React.useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchSettings();
        setSettings(data);
      } catch (err) {
        console.error('Error loading settings:', err);
        setError('Failed to load settings. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    loadSettings();
  }, []);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle setting change
  const handleSettingChange = (category, setting, value) => {
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [setting]: value
      }
    });
  };
  
  // Handle number input change
  const handleNumberChange = (category, setting, value) => {
    const numValue = value === '' ? '' : Number(value);
    handleSettingChange(category, setting, numValue);
  };
  
  // Handle form submission
  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      await saveSettings(settings);
      setSuccessMessage('Settings saved successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };
  
  // Handle reset
  const handleReset = async () => {
    if (window.confirm('Are you sure you want to reset all settings to default values?')) {
      try {
        setLoading(true);
        const data = await fetchSettings();
        setSettings(data);
        setSuccessMessage('Settings reset to default values');
        setTimeout(() => setSuccessMessage(''), 3000);
      } catch (err) {
        console.error('Error resetting settings:', err);
        setError('Failed to reset settings. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };
  
  if (loading && !settings) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <Typography>Loading settings...</Typography>
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          System Settings
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Configure application-wide settings and defaults
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 4 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={() => setSuccessMessage('')}
        message={successMessage}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSuccessMessage('')}>
          {successMessage}
        </Alert>
      </Snackbar>
      
      <Paper sx={{ width: '100%', mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange} 
            aria-label="settings tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="General" {...a11yProps(0)} />
            <Tab label="Security" {...a11yProps(1)} />
            <Tab label="Data Generation" {...a11yProps(2)} />
            <Tab label="Storage" {...a11yProps(3)} />
          </Tabs>
        </Box>
        
        {settings && (
          <>
            {/* General Settings */}
            <TabPanel value={activeTab} index={0}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Application Name"
                    value={settings.general.applicationName}
                    onChange={(e) => handleSettingChange('general', 'applicationName', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Application Version"
                    value={settings.general.applicationVersion}
                    onChange={(e) => handleSettingChange('general', 'applicationVersion', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Upload File Size (MB)"
                    type="number"
                    value={settings.general.maxUploadFileSizeMB}
                    onChange={(e) => handleNumberChange('general', 'maxUploadFileSizeMB', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Page Size"
                    type="number"
                    value={settings.general.defaultPageSize}
                    onChange={(e) => handleNumberChange('general', 'defaultPageSize', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 5, max: 100 } }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.general.enableDebugMode}
                        onChange={(e) => handleSettingChange('general', 'enableDebugMode', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable Debug Mode"
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Security Settings */}
            <TabPanel value={activeTab} index={1}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Session Timeout (minutes)"
                    type="number"
                    value={settings.security.sessionTimeoutMinutes}
                    onChange={(e) => handleNumberChange('security', 'sessionTimeoutMinutes', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Password Minimum Length"
                    type="number"
                    value={settings.security.passwordMinLength}
                    onChange={(e) => handleNumberChange('security', 'passwordMinLength', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 6 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Allowed Failed Login Attempts"
                    type="number"
                    value={settings.security.allowedFailedLoginAttempts}
                    onChange={(e) => handleNumberChange('security', 'allowedFailedLoginAttempts', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.enforcePasswordExpiration}
                        onChange={(e) => handleSettingChange('security', 'enforcePasswordExpiration', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enforce Password Expiration"
                  />
                </Grid>
                {settings.security.enforcePasswordExpiration && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Password Expiration (days)"
                      type="number"
                      value={settings.security.passwordExpirationDays}
                      onChange={(e) => handleNumberChange('security', 'passwordExpirationDays', e.target.value)}
                      margin="normal"
                      InputProps={{ inputProps: { min: 1 } }}
                    />
                  </Grid>
                )}
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireNumbers}
                        onChange={(e) => handleSettingChange('security', 'passwordRequireNumbers', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Numbers in Passwords"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.security.passwordRequireSpecialChars}
                        onChange={(e) => handleSettingChange('security', 'passwordRequireSpecialChars', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Require Special Characters in Passwords"
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Data Generation Settings */}
            <TabPanel value={activeTab} index={2}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Jobs Per User"
                    type="number"
                    value={settings.dataGeneration.maxJobsPerUser}
                    onChange={(e) => handleNumberChange('dataGeneration', 'maxJobsPerUser', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Records Per Job"
                    type="number"
                    value={settings.dataGeneration.maxRecordsPerJob}
                    onChange={(e) => handleNumberChange('dataGeneration', 'maxRecordsPerJob', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 100 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="default-generation-mode-label">Default Generation Mode</InputLabel>
                    <Select
                      labelId="default-generation-mode-label"
                      value={settings.dataGeneration.defaultGenerationMode}
                      onChange={(e) => handleSettingChange('dataGeneration', 'defaultGenerationMode', e.target.value)}
                      label="Default Generation Mode"
                    >
                      <MenuItem value="random">Random</MenuItem>
                      <MenuItem value="statistical">Statistical</MenuItem>
                      <MenuItem value="realistic">Realistic</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Job Timeout (minutes)"
                    type="number"
                    value={settings.dataGeneration.jobTimeoutMinutes}
                    onChange={(e) => handleNumberChange('dataGeneration', 'jobTimeoutMinutes', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Random Seed"
                    type="number"
                    value={settings.dataGeneration.defaultRandomSeed}
                    onChange={(e) => handleNumberChange('dataGeneration', 'defaultRandomSeed', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.dataGeneration.preserveRelationships}
                        onChange={(e) => handleSettingChange('dataGeneration', 'preserveRelationships', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Preserve Relationships by Default"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.dataGeneration.enableAdvancedOptions}
                        onChange={(e) => handleSettingChange('dataGeneration', 'enableAdvancedOptions', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable Advanced Options"
                  />
                </Grid>
              </Grid>
            </TabPanel>
            
            {/* Storage Settings */}
            <TabPanel value={activeTab} index={3}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Data Retention Period (days)"
                    type="number"
                    value={settings.storage.dataRetentionDays}
                    onChange={(e) => handleNumberChange('storage', 'dataRetentionDays', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Max Storage Per User (MB)"
                    type="number"
                    value={settings.storage.maxStoragePerUserMB}
                    onChange={(e) => handleNumberChange('storage', 'maxStoragePerUserMB', e.target.value)}
                    margin="normal"
                    InputProps={{ inputProps: { min: 1 } }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="export-file-format-label">Default Export Format</InputLabel>
                    <Select
                      labelId="export-file-format-label"
                      value={settings.storage.exportFileFormat}
                      onChange={(e) => handleSettingChange('storage', 'exportFileFormat', e.target.value)}
                      label="Default Export Format"
                    >
                      <MenuItem value="CSV">CSV</MenuItem>
                      <MenuItem value="Excel">Excel</MenuItem>
                      <MenuItem value="SAS">SAS</MenuItem>
                      <MenuItem value="JSON">JSON</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.storage.autoDeleteCompletedJobs}
                        onChange={(e) => handleSettingChange('storage', 'autoDeleteCompletedJobs', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Auto-delete Completed Jobs"
                  />
                </Grid>
                {settings.storage.autoDeleteCompletedJobs && (
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Auto-delete After (days)"
                      type="number"
                      value={settings.storage.autoDeleteAfterDays}
                      onChange={(e) => handleNumberChange('storage', 'autoDeleteAfterDays', e.target.value)}
                      margin="normal"
                      InputProps={{ inputProps: { min: 1 } }}
                    />
                  </Grid>
                )}
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.storage.compressionEnabled}
                        onChange={(e) => handleSettingChange('storage', 'compressionEnabled', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable File Compression"
                  />
                </Grid>
              </Grid>
            </TabPanel>
          </>
        )}
        
        {/* Actions */}
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2, gap: 2 }}>
          <Button 
            variant="outlined" 
            startIcon={<RefreshIcon />} 
            onClick={handleReset}
            disabled={loading || saving}
          >
            Reset to Defaults
          </Button>
          <Button 
            variant="contained" 
            startIcon={<SaveIcon />} 
            onClick={handleSaveSettings}
            disabled={loading || saving}
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default SystemSettings;
