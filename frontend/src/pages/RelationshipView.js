import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, CircularProgress, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Card, CardContent, Divider, Chip
} from '@mui/material';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import LinkIcon from '@mui/icons-material/Link';

import { getRelationships } from '../services/api';

const RelationshipView = () => {
  const navigate = useNavigate();
  const [relationships, setRelationships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [domains, setDomains] = useState(new Set());

  useEffect(() => {
    fetchRelationships();
  }, []);

  const fetchRelationships = async () => {
    try {
      const data = await getRelationships();
      setRelationships(data || []);
      
      // Extract unique domains
      const domainsSet = new Set();
      data.forEach(rel => {
        domainsSet.add(rel.source_domain);
        domainsSet.add(rel.target_domain);
      });
      setDomains(domainsSet);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching relationships:', error);
      setError('Failed to load relationships. Please try again later.');
      setLoading(false);
    }
  };

  const getRelationshipStrengthColor = (strength) => {
    if (strength >= 0.8) return 'success';
    if (strength >= 0.5) return 'primary';
    if (strength >= 0.3) return 'warning';
    return 'error';
  };

  const getDomainRelationships = (domainName) => {
    return relationships.filter(rel => 
      rel.source_domain === domainName || rel.target_domain === domainName
    );
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Domain Relationships
      </Typography>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      ) : relationships.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" gutterBottom>
            No relationships detected between domains.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Relationships will be automatically detected when multiple related domains are ingested.
          </Typography>
        </Paper>
      ) : (
        <>
          {/* Relationship summary */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Cross-Domain Relationships
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Domains:</Typography>
                  <Typography variant="h5">{domains.size}</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Relationships:</Typography>
                  <Typography variant="h5">{relationships.length}</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 2 }}>
                  <Typography variant="body2" color="text.secondary">Avg. Strength:</Typography>
                  <Typography variant="h5">
                    {relationships.length > 0 ? 
                      (relationships.reduce((sum, rel) => sum + (rel.strength || 0), 0) / relationships.length).toFixed(2) : 
                      '0.00'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
          
          {/* Detailed relationships table */}
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              All Relationships
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Source Domain</TableCell>
                    <TableCell>Source Variable</TableCell>
                    <TableCell align="center">Relationship</TableCell>
                    <TableCell>Target Domain</TableCell>
                    <TableCell>Target Variable</TableCell>
                    <TableCell align="right">Strength</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {relationships.map((rel, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography 
                          variant="body2" 
                          sx={{ cursor: 'pointer', fontWeight: 'bold' }}
                          onClick={() => navigate(`/domain/${rel.source_domain}`)}
                        >
                          {rel.source_domain}
                        </Typography>
                      </TableCell>
                      <TableCell>{rel.source_variable}</TableCell>
                      <TableCell align="center">
                        <Chip 
                          icon={<LinkIcon />} 
                          label={rel.relationship_type} 
                          size="small" 
                          color={getRelationshipStrengthColor(rel.strength)} 
                        />
                      </TableCell>
                      <TableCell>
                        <Typography 
                          variant="body2" 
                          sx={{ cursor: 'pointer', fontWeight: 'bold' }}
                          onClick={() => navigate(`/domain/${rel.target_domain}`)}
                        >
                          {rel.target_domain}
                        </Typography>
                      </TableCell>
                      <TableCell>{rel.target_variable}</TableCell>
                      <TableCell align="right">
                        {rel.strength !== null && rel.strength !== undefined ? Number(rel.strength).toFixed(2) : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
          
          {/* Domain relationship cards */}
          <Typography variant="h6" gutterBottom>
            Domain Relationship Network
          </Typography>
          <Grid container spacing={3}>
            {Array.from(domains).map((domain) => {
              const domainRels = getDomainRelationships(domain);
              return (
                <Grid item xs={12} md={6} lg={4} key={domain}>
                  <Card>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <AccountTreeIcon color="primary" sx={{ mr: 1 }} />
                        <Typography variant="h6" component="div">
                          {domain}
                        </Typography>
                      </Box>
                      <Divider sx={{ mb: 2 }} />
                      
                      {domainRels.length === 0 ? (
                        <Typography variant="body2" color="text.secondary">
                          No relationships found for this domain.
                        </Typography>
                      ) : (
                        <>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            Connected to {new Set(domainRels.map(rel => 
                              rel.source_domain === domain ? rel.target_domain : rel.source_domain
                            )).size} domains
                          </Typography>
                          
                          {domainRels.map((rel, index) => {
                            const isSource = rel.source_domain === domain;
                            const otherDomain = isSource ? rel.target_domain : rel.source_domain;
                            const thisVariable = isSource ? rel.source_variable : rel.target_variable;
                            const otherVariable = isSource ? rel.target_variable : rel.source_variable;
                            
                            return (
                              <Box 
                                key={index}
                                sx={{ 
                                  p: 1, 
                                  border: 1, 
                                  borderColor: 'divider', 
                                  borderRadius: 1, 
                                  mb: 1,
                                  '&:hover': { backgroundColor: 'rgba(0,0,0,0.04)' },
                                  cursor: 'pointer'
                                }}
                                onClick={() => navigate(`/domain/${otherDomain}`)}
                              >
                                <Typography variant="body2">
                                  {isSource ? 'Connects to' : 'Connected from'} <strong>{otherDomain}</strong>
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {thisVariable} {isSource ? '→' : '←'} {otherVariable}
                                </Typography>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                                  <Chip 
                                    label={rel.relationship_type} 
                                    size="small" 
                                    variant="outlined"
                                  />
                                  <Chip 
                                    label={`Strength: ${rel.strength !== null && rel.strength !== undefined ? Number(rel.strength).toFixed(2) : 'N/A'}`} 
                                    size="small"
                                    color={getRelationshipStrengthColor(rel.strength || 0)}
                                  />
                                </Box>
                              </Box>
                            );
                          })}
                        </>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </>
      )}
    </Box>
  );
};

export default RelationshipView;
