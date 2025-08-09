import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import { Add, Psychology, History } from '@mui/icons-material';
import { projectAPI, argumentAPI } from '../services/api';
import { Project, Argument } from '../types';
import ArgumentTable from './ArgumentTable';
import AddArgumentDialog from './AddArgumentDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [argumentsList, setArgumentsList] = useState<Argument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [openAddDialog, setOpenAddDialog] = useState(false);

  useEffect(() => {
    if (id) {
      loadProjectData(parseInt(id));
    }
  }, [id]);

  const loadProjectData = async (projectId: number) => {
    try {
      setLoading(true);
      const [projectData, argumentsData] = await Promise.all([
        projectAPI.getProject(projectId),
        argumentAPI.getArguments(projectId),
      ]);
      setProject(projectData);
      setArgumentsList(argumentsData);
      setError(null);
    } catch (err) {
      setError('プロジェクトデータの読み込みに失敗しました');
      console.error('Error loading project data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleArgumentAdded = () => {
    if (id) {
      loadProjectData(parseInt(id));
    }
    setOpenAddDialog(false);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const generateAIArguments = async () => {
    if (!project) return;
    
    // TODO: 実際のAI生成機能を実装
    alert('AI論点生成機能は開発中です。複数のAIモデルから論点を生成し、相互検証を行います。');
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !project) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Alert severity="error">{error || 'プロジェクトが見つかりません'}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              {project.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip label={project.industry} color="primary" variant="outlined" />
              <Chip label={project.theme} color="secondary" variant="outlined" />
            </Box>
            <Typography variant="body1" color="text.secondary">
              クライアント: {project.client_name}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {project.description}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<Psychology />}
              onClick={generateAIArguments}
              color="secondary"
            >
              AI論点生成
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenAddDialog(true)}
            >
              論点追加
            </Button>
          </Box>
        </Box>
      </Paper>

      <Paper>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab 
              label={`論点表 (${argumentsList.length})`} 
              icon={<Typography variant="body2">📊</Typography>} 
              iconPosition="start" 
            />
            <Tab 
              label="過去事例" 
              icon={<History />} 
              iconPosition="start" 
            />
            <Tab 
              label="AI検証レポート" 
              icon={<Psychology />} 
              iconPosition="start" 
            />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          {argumentsList.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography variant="h6" color="textSecondary">
                まだ論点が追加されていません
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 2, mb: 3 }}>
                AI論点生成機能を使用するか、手動で論点を追加してください
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  startIcon={<Psychology />}
                  onClick={generateAIArguments}
                  color="secondary"
                >
                  AI論点生成
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => setOpenAddDialog(true)}
                >
                  手動で追加
                </Button>
              </Box>
            </Box>
          ) : (
            <ArgumentTable 
              arguments={argumentsList} 
              onRefresh={() => id && loadProjectData(parseInt(id))}
            />
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            関連する過去事例
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {project.industry}×{project.theme}に関連する過去事例を表示します。
            この機能は開発中です。
          </Typography>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            AI相互検証レポート
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Claude 4.1 Opus、o3 Pro、Gemini 2.5による論点の相互検証結果を表示します。
            この機能は開発中です。
          </Typography>
        </TabPanel>
      </Paper>

      <AddArgumentDialog
        open={openAddDialog}
        onClose={() => setOpenAddDialog(false)}
        projectId={project.id}
        onArgumentAdded={handleArgumentAdded}
      />
    </Container>
  );
};

export default ProjectDetail;