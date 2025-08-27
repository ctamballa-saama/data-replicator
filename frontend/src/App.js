import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';

// Import components
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import DataIngestion from './pages/DataIngestion';
import DataAnalysis from './pages/DataAnalysis';
import DataGeneration from './pages/DataGeneration';
import RelationshipView from './pages/RelationshipView';
import DomainDetails from './pages/DomainDetails';

const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Header />
        <Navigation />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            width: { sm: `calc(100% - 240px)` },
            ml: { sm: '240px' },
            mt: '64px',
            overflow: 'auto',
            height: 'calc(100vh - 64px)',
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/data-ingestion" element={<DataIngestion />} />
            <Route path="/data-analysis" element={<DataAnalysis />} />
            <Route path="/data-generation" element={<DataGeneration />} />
            <Route path="/relationships" element={<RelationshipView />} />
            <Route path="/domain/:domainName" element={<DomainDetails />} />
          </Routes>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
