import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Configure axios
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Data domain endpoints
export const getDomains = async () => {
  try {
    const response = await api.get('/data/domains');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch domains:', error);
    throw error;
  }
};

export const getDomainDetails = async (domainName) => {
  try {
    const response = await api.get(`/data/domain/${domainName}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch domain ${domainName}:`, error);
    throw error;
  }
};

// Data upload
export const uploadData = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/data/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Failed to upload data:', error);
    throw error;
  }
};

// Analysis endpoints
export const getDomainStatistics = async (domainName) => {
  try {
    const response = await api.get(`/analysis/statistics/${domainName}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get statistics for domain ${domainName}:`, error);
    throw error;
  }
};

export const getVariableStatistics = async (domainName, variableName) => {
  try {
    const response = await api.get(`/analysis/variable/${domainName}/${variableName}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get statistics for variable ${variableName}:`, error);
    throw error;
  }
};

export const getRelationships = async () => {
  try {
    const response = await api.get('/analysis/relationships');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch relationships:', error);
    throw error;
  }
};

// Data generation endpoints
export const generateData = async (generationRequest) => {
  try {
    const response = await api.post('/generation/generate', generationRequest);
    return response.data;
  } catch (error) {
    console.error('Failed to start data generation:', error);
    throw error;
  }
};

export const getGenerationStatus = async (jobId) => {
  try {
    const response = await api.get(`/generation/status/${jobId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get generation status for job ${jobId}:`, error);
    throw error;
  }
};

export const downloadGeneratedData = async (domainName) => {
  try {
    const response = await api.get(`/generation/download/${domainName}`, {
      responseType: 'blob',
    });
    
    // Extract filename from Content-Disposition header if available
    const contentDisposition = response.headers['content-disposition'];
    let filename = `${domainName}.csv`; // Default filename
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/i);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }
    
    // Create a blob URL and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    return true;
  } catch (error) {
    console.error(`Failed to download generated data for ${domainName}:`, error);
    throw error;
  }
};

// Validation endpoints
export const getValidators = async () => {
  try {
    const response = await api.get('/validation/validators');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch validators:', error);
    throw error;
  }
};

export const getValidationRules = async (validatorId = null) => {
  try {
    let url = '/validation/rules';
    if (validatorId) {
      url += `?validator_id=${validatorId}`;
    }
    const response = await api.get(url);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch validation rules:', error);
    throw error;
  }
};

export const validateDomain = async (domainName, validatorIds = null) => {
  try {
    const payload = {
      domain_name: domainName,
      validator_ids: validatorIds
    };
    const response = await api.post('/validation/validate', payload);
    return response.data;
  } catch (error) {
    console.error(`Failed to validate domain ${domainName}:`, error);
    throw error;
  }
};
