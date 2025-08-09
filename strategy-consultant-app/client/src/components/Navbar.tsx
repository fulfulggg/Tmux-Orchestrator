import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { Business, Add, Home } from '@mui/icons-material';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <AppBar position="static">
      <Toolbar>
        <Business sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          戦略論点設計システム
        </Typography>
        <Box>
          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => navigate('/')}
            sx={{ 
              backgroundColor: location.pathname === '/' ? 'rgba(255,255,255,0.1)' : 'transparent' 
            }}
          >
            プロジェクト一覧
          </Button>
          <Button
            color="inherit"
            startIcon={<Add />}
            onClick={() => navigate('/create')}
            sx={{ 
              ml: 1,
              backgroundColor: location.pathname === '/create' ? 'rgba(255,255,255,0.1)' : 'transparent' 
            }}
          >
            新規プロジェクト
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;