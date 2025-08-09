import React, { useState } from 'react';
import { Button, Box, Typography, Alert } from '@mui/material';
import axios from 'axios';

const TestAPI: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testDirectAPI = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/projects');
      setResult(`成功: ${JSON.stringify(response.data, null, 2)}`);
    } catch (error: any) {
      setResult(`エラー: ${error.message}`);
      console.error('Direct API test error:', error);
    }
    setLoading(false);
  };

  const testFetch = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/projects');
      const data = await response.json();
      setResult(`Fetch成功: ${JSON.stringify(data, null, 2)}`);
    } catch (error: any) {
      setResult(`Fetchエラー: ${error.message}`);
      console.error('Fetch test error:', error);
    }
    setLoading(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        API接続テスト
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Button 
          variant="contained" 
          onClick={testDirectAPI} 
          disabled={loading}
          sx={{ mr: 2 }}
        >
          Axios テスト
        </Button>
        <Button 
          variant="outlined" 
          onClick={testFetch} 
          disabled={loading}
        >
          Fetch テスト
        </Button>
      </Box>

      {result && (
        <Alert severity={result.includes('成功') ? 'success' : 'error'}>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {result}
          </pre>
        </Alert>
      )}
    </Box>
  );
};

export default TestAPI;