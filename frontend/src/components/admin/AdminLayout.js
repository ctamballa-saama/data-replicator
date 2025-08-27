/**
 * Admin Layout component for DataReplicator Admin
 * 
 * Provides navigation and layout structure for all admin pages
 */
import React, { useState } from 'react';
import { 
  Box, 
  Drawer, 
  AppBar, 
  Toolbar, 
  Typography, 
  Divider, 
  IconButton, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Container,
  useMediaQuery,
  useTheme,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Storage as StorageIcon,
  Assignment as AssignmentIcon,
  CloudDownload as DownloadIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
  AccountCircle as AccountCircleIcon,
  Notifications as NotificationsIcon,
  ExitToApp as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

// Constants
const drawerWidth = 240;

const AdminLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  // State
  const [drawerOpen, setDrawerOpen] = useState(!isMobile);
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationsAnchorEl, setNotificationsAnchorEl] = useState(null);
  
  // Menu open states
  const isMenuOpen = Boolean(anchorEl);
  const isNotificationsOpen = Boolean(notificationsAnchorEl);
  
  // Mock notifications
  const notifications = [
    { id: 1, message: "New user registration: jane.smith", read: false },
    { id: 2, message: "Job completed: gen_Demographics_random", read: false },
    { id: 3, message: "Export failed: CM_Export_Full", read: false },
  ];
  
  // Navigation items
  const navItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/admin' },
    { text: 'Users', icon: <PeopleIcon />, path: '/admin/users' },
    { text: 'Domains', icon: <StorageIcon />, path: '/admin/domains' },
    { text: 'Jobs', icon: <AssignmentIcon />, path: '/admin/jobs' },
    { text: 'Exports', icon: <DownloadIcon />, path: '/admin/exports' },
    { text: 'Settings', icon: <SettingsIcon />, path: '/admin/settings' },
  ];
  
  // Determine the current page title based on path
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/admin') return 'Admin Dashboard';
    if (path === '/admin/users') return 'User Management';
    if (path === '/admin/domains') return 'Domain Management';
    if (path === '/admin/jobs') return 'Job Management';
    if (path === '/admin/exports') return 'Export Management';
    if (path === '/admin/settings') return 'System Settings';
    return 'Admin';
  };
  
  // Handle drawer open/close
  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // Handle navigation
  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setDrawerOpen(false);
    }
  };
  
  // Handle profile menu open
  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  // Handle menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  // Handle notifications menu
  const handleNotificationsMenuOpen = (event) => {
    setNotificationsAnchorEl(event.currentTarget);
  };
  
  const handleNotificationsMenuClose = () => {
    setNotificationsAnchorEl(null);
  };
  
  // Handle logout
  const handleLogout = () => {
    handleMenuClose();
    logout();
    navigate('/login');
  };
  
  // Account menu
  const renderAccountMenu = (
    <Menu
      anchorEl={anchorEl}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isMenuOpen}
      onClose={handleMenuClose}
    >
      <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
        <ListItemIcon>
          <AccountCircleIcon fontSize="small" />
        </ListItemIcon>
        Profile
      </MenuItem>
      <MenuItem onClick={handleLogout}>
        <ListItemIcon>
          <LogoutIcon fontSize="small" />
        </ListItemIcon>
        Logout
      </MenuItem>
    </Menu>
  );
  
  // Notifications menu
  const renderNotificationsMenu = (
    <Menu
      anchorEl={notificationsAnchorEl}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      keepMounted
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      open={isNotificationsOpen}
      onClose={handleNotificationsMenuClose}
    >
      {notifications.length > 0 ? (
        notifications.map((notification) => (
          <MenuItem key={notification.id} onClick={handleNotificationsMenuClose}>
            {notification.message}
          </MenuItem>
        ))
      ) : (
        <MenuItem onClick={handleNotificationsMenuClose}>No new notifications</MenuItem>
      )}
      <Divider />
      <MenuItem onClick={handleNotificationsMenuClose}>
        <Typography variant="body2" color="primary" align="center" sx={{ width: '100%' }}>
          View all notifications
        </Typography>
      </MenuItem>
    </Menu>
  );
  
  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(drawerOpen && {
            marginLeft: drawerWidth,
            width: `calc(100% - ${drawerWidth}px)`,
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {getPageTitle()}
          </Typography>
          
          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit" onClick={handleNotificationsMenuOpen}>
              <Badge badgeContent={notifications.filter(n => !n.read).length} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          
          {/* Profile */}
          <Tooltip title={user?.email || 'Account'}>
            <IconButton
              edge="end"
              aria-label="account of current user"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <Avatar 
                sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}
              >
                {user?.name ? user.name.charAt(0).toUpperCase() : 'A'}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>
      
      {/* Navigation Drawer */}
      <Drawer
        variant={isMobile ? "temporary" : "permanent"}
        open={drawerOpen}
        onClose={isMobile ? handleDrawerToggle : undefined}
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            px: [1],
          }}
        >
          <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold', ml: 1 }}>
            DataReplicator
          </Typography>
          {!isMobile && (
            <IconButton onClick={handleDrawerToggle}>
              <ChevronLeftIcon />
            </IconButton>
          )}
        </Toolbar>
        <Divider />
        
        {/* Navigation Items */}
        <List>
          {navItems.map((item) => (
            <ListItem 
              button 
              key={item.text}
              onClick={() => handleNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'action.selected',
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                },
              }}
            >
              <ListItemIcon>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
        
        <Box sx={{ flexGrow: 1 }} />
        
        <Divider />
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary" align="center">
            &copy; {new Date().getFullYear()} Saama Technologies
          </Typography>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            v1.0.0
          </Typography>
        </Box>
      </Drawer>
      
      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          minHeight: '100vh',
          backgroundColor: (theme) => theme.palette.background.default,
          paddingTop: (theme) => theme.spacing(10),
          paddingBottom: (theme) => theme.spacing(4),
        }}
      >
        <Container maxWidth="xl">
          <Outlet />
        </Container>
      </Box>
      
      {/* Menus */}
      {renderAccountMenu}
      {renderNotificationsMenu}
    </Box>
  );
};

export default AdminLayout;
