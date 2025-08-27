import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import Box from '@mui/material/Box';
import { useTheme } from '@mui/material/styles';

const Header = () => {
  const theme = useTheme();

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: theme.palette.primary.main,
      }}
    >
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="menu"
          edge="start"
          sx={{ mr: 2, display: { sm: 'none' } }}
        >
          <MenuIcon />
        </IconButton>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6" noWrap component="div">
            DataReplicator
          </Typography>
          <Typography 
            variant="subtitle1" 
            sx={{ ml: 1, opacity: 0.8, fontStyle: 'italic' }}
          >
            Clinical Data Analysis & Generation
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
