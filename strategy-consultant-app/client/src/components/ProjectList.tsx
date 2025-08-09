import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Business, DateRange, Person } from '@mui/icons-material';
import { projectAPI } from '../services/api';
import { Project } from '../types';

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      console.log('Starting to load projects...');
      const data = await projectAPI.getProjects();
      console.log('Projects loaded successfully:', data);
      setProjects(data);
      setError(null);
    } catch (err: any) {
      const errorMessage = err?.response?.data?.error || err?.message || 'プロジェクトの読み込みに失敗しました';
      setError(`プロジェクト読み込みエラー: ${errorMessage}`);
      console.error('Error loading projects:', err);
      console.error('Error details:', {
        message: err?.message,
        status: err?.response?.status,
        data: err?.response?.data,
        config: err?.config
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ja-JP');
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            プロジェクト一覧
          </Typography>
          <Button
            variant="contained"
            onClick={() => navigate('/create')}
          >
            新規プロジェクト作成
          </Button>
        </Box>

        {projects.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h6" color="textSecondary">
              プロジェクトがありません
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
              新しいプロジェクトを作成して開始しましょう
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {projects.map((project) => (
              <Grid item xs={12} md={6} lg={4} key={project.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {project.name}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Person fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {project.client_name}
                      </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Business fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {project.industry}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={project.theme}
                        color="primary"
                        variant="outlined"
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {project.description}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <DateRange fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        作成日: {formatDate(project.created_at)}
                      </Typography>
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      variant="contained"
                      onClick={() => navigate(`/project/${project.id}`)}
                      fullWidth
                    >
                      論点表を開く
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
    </Container>
  );
};

export default ProjectList;