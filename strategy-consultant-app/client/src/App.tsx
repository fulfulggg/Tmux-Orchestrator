import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ProjectList from './components/ProjectList';
import ProjectDetail from './components/ProjectDetail';
import CreateProject from './components/CreateProject';
import Navbar from './components/Navbar';
import TestAPI from './components/TestAPI';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<ProjectList />} />
            <Route path="/create" element={<CreateProject />} />
            <Route path="/project/:id" element={<ProjectDetail />} />
            <Route path="/test" element={<TestAPI />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
