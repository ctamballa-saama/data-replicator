/**
 * User Management component for DataReplicator Admin
 * 
 * Provides functionality to view, add, edit, and delete users
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
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LockReset as ResetIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

// Mock API functions - replace with actual API integration
const fetchUsers = async (page, rowsPerPage, searchTerm = '') => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock user data
  const allUsers = [
    { id: 'user1', username: 'admin', email: 'admin@example.com', full_name: 'System Admin', is_active: true, is_superuser: true, created_at: '2025-01-15T10:00:00Z' },
    { id: 'user2', username: 'john.doe', email: 'john.doe@example.com', full_name: 'John Doe', is_active: true, is_superuser: false, created_at: '2025-02-20T14:30:00Z' },
    { id: 'user3', username: 'jane.smith', email: 'jane.smith@example.com', full_name: 'Jane Smith', is_active: true, is_superuser: false, created_at: '2025-03-10T09:15:00Z' },
    { id: 'user4', username: 'mark.wilson', email: 'mark.wilson@example.com', full_name: 'Mark Wilson', is_active: true, is_superuser: false, created_at: '2025-04-05T11:45:00Z' },
    { id: 'user5', username: 'sarah.jones', email: 'sarah.jones@example.com', full_name: 'Sarah Jones', is_active: true, is_superuser: false, created_at: '2025-05-22T16:20:00Z' },
    { id: 'user6', username: 'chris.adams', email: 'chris.adams@example.com', full_name: 'Chris Adams', is_active: false, is_superuser: false, created_at: '2025-06-18T13:10:00Z' },
    { id: 'user7', username: 'alex.brown', email: 'alex.brown@example.com', full_name: 'Alex Brown', is_active: true, is_superuser: false, created_at: '2025-07-09T15:55:00Z' },
    { id: 'user8', username: 'emily.davis', email: 'emily.davis@example.com', full_name: 'Emily Davis', is_active: true, is_superuser: false, created_at: '2025-08-01T10:30:00Z' },
  ];
  
  // Filter users by search term if provided
  const filteredUsers = searchTerm
    ? allUsers.filter(user => 
        user.username.includes(searchTerm) || 
        user.email.includes(searchTerm) || 
        user.full_name.includes(searchTerm)
      )
    : allUsers;
  
  // Paginate results
  const paginatedUsers = filteredUsers.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return {
    users: paginatedUsers,
    totalCount: filteredUsers.length
  };
};

const createUser = async (userData) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return {
    success: true,
    user: {
      id: `user${Math.floor(Math.random() * 1000)}`,
      ...userData,
      created_at: new Date().toISOString()
    }
  };
};

const updateUser = async (userId, userData) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return {
    success: true,
    user: {
      id: userId,
      ...userData,
      updated_at: new Date().toISOString()
    }
  };
};

const deleteUser = async (userId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return { success: true };
};

const resetUserPassword = async (userId) => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return success response
  return { 
    success: true,
    message: 'Password reset email sent to user'
  };
};

const UserManagement = () => {
  // State
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);
  const [totalUsers, setTotalUsers] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState('add'); // 'add', 'edit', 'delete'
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    is_active: true,
    is_superuser: false,
  });
  const [formErrors, setFormErrors] = useState({});
  const [actionLoading, setActionLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Load users
  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchUsers(page, rowsPerPage, searchTerm);
      setUsers(data.users);
      setTotalUsers(data.totalCount);
    } catch (err) {
      console.error('Error loading users:', err);
      setError('Failed to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Initial load
  useEffect(() => {
    loadUsers();
  }, [page, rowsPerPage, searchTerm]);
  
  // Handle search
  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setPage(0); // Reset to first page when searching
      loadUsers();
    }
  };
  
  // Handle dialog open
  const handleOpenDialog = (mode, user = null) => {
    setDialogMode(mode);
    setSelectedUser(user);
    
    // Reset form
    if (mode === 'add') {
      setFormData({
        username: '',
        email: '',
        full_name: '',
        password: '',
        is_active: true,
        is_superuser: false,
      });
    } else if (mode === 'edit' && user) {
      setFormData({
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        password: '',
        is_active: user.is_active,
        is_superuser: user.is_superuser,
      });
    }
    
    setFormErrors({});
    setOpenDialog(true);
  };
  
  // Handle dialog close
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedUser(null);
  };
  
  // Handle input change
  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    const val = name === 'is_active' || name === 'is_superuser' ? checked : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: val
    }));
    
    // Clear field error
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };
  
  // Validate form
  const validateForm = () => {
    const errors = {};
    
    if (!formData.username) {
      errors.username = 'Username is required';
    }
    
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!formData.full_name) {
      errors.full_name = 'Full name is required';
    }
    
    if (dialogMode === 'add' && !formData.password) {
      errors.password = 'Password is required for new users';
    } else if (formData.password && formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    
    return errors;
  };
  
  // Handle form submission
  const handleSubmit = async () => {
    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    setActionLoading(true);
    try {
      if (dialogMode === 'add') {
        // Create user
        await createUser(formData);
        setSuccessMessage('User created successfully');
      } else if (dialogMode === 'edit') {
        // Update user
        await updateUser(selectedUser.id, formData);
        setSuccessMessage('User updated successfully');
      }
      
      // Close dialog and reload users
      handleCloseDialog();
      loadUsers();
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error(`Error ${dialogMode === 'add' ? 'creating' : 'updating'} user:`, err);
      setError(`Failed to ${dialogMode === 'add' ? 'create' : 'update'} user. Please try again.`);
    } finally {
      setActionLoading(false);
    }
  };
  
  // Handle user deletion
  const handleDeleteUser = async () => {
    if (!selectedUser) return;
    
    setActionLoading(true);
    try {
      await deleteUser(selectedUser.id);
      
      // Close dialog and reload users
      handleCloseDialog();
      loadUsers();
      setSuccessMessage('User deleted successfully');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error deleting user:', err);
      setError('Failed to delete user. Please try again.');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Handle password reset
  const handleResetPassword = async (userId) => {
    setActionLoading(true);
    try {
      await resetUserPassword(userId);
      setSuccessMessage('Password reset email sent to user');
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error resetting password:', err);
      setError('Failed to reset password. Please try again.');
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
          User Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage users and their permissions
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
              placeholder="Search users..."
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
              <IconButton onClick={loadUsers} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog('add')}
          >
            Add User
          </Button>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Username</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Created</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : users.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3 }}>
                    <Typography variant="body1">No users found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.full_name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={user.is_active ? "Active" : "Inactive"} 
                        color={user.is_active ? "success" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={user.is_superuser ? "Admin" : "User"} 
                        color={user.is_superuser ? "primary" : "default"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell align="right">
                      <Tooltip title="Edit User">
                        <IconButton size="small" onClick={() => handleOpenDialog('edit', user)}>
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Reset Password">
                        <IconButton size="small" onClick={() => handleResetPassword(user.id)}>
                          <ResetIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete User">
                        <IconButton 
                          size="small" 
                          onClick={() => handleOpenDialog('delete', user)}
                          disabled={user.is_superuser && users.filter(u => u.is_superuser).length === 1}
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
          count={totalUsers}
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
      
      {/* Add/Edit User Dialog */}
      {(dialogMode === 'add' || dialogMode === 'edit') && (
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {dialogMode === 'add' ? 'Add New User' : 'Edit User'}
          </DialogTitle>
          <DialogContent>
            <TextField
              margin="normal"
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              error={!!formErrors.username}
              helperText={formErrors.username || ''}
              disabled={dialogMode === 'edit'}
            />
            <TextField
              margin="normal"
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              error={!!formErrors.email}
              helperText={formErrors.email || ''}
            />
            <TextField
              margin="normal"
              fullWidth
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleInputChange}
              error={!!formErrors.full_name}
              helperText={formErrors.full_name || ''}
            />
            <TextField
              margin="normal"
              fullWidth
              label={dialogMode === 'add' ? 'Password' : 'New Password (leave blank to keep current)'}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              error={!!formErrors.password}
              helperText={formErrors.password || ''}
            />
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    name="is_active"
                  />
                }
                label="Active"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_superuser}
                    onChange={handleInputChange}
                    name="is_superuser"
                  />
                }
                label="Admin Access"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleSubmit} 
              variant="contained" 
              disabled={actionLoading}
            >
              {actionLoading ? <CircularProgress size={24} /> : (dialogMode === 'add' ? 'Add' : 'Save')}
            </Button>
          </DialogActions>
        </Dialog>
      )}
      
      {/* Delete User Dialog */}
      {dialogMode === 'delete' && (
        <Dialog open={openDialog} onClose={handleCloseDialog}>
          <DialogTitle>Delete User</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete user <strong>{selectedUser?.username}</strong>? This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={handleDeleteUser} 
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

export default UserManagement;
