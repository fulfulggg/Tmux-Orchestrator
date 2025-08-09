import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  MenuItem,
  Alert,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { projectAPI } from '../services/api';

const industries = [
  '製造業',
  '小売業',
  '金融業',
  'IT・テクノロジー',
  'ヘルスケア',
  'エネルギー',
  '不動産',
  '建設業',
  '運輸・物流',
  'その他'
];

const themes = [
  'M&A',
  '事業戦略',
  '組織改革',
  'デジタル変革（DX）',
  'コスト削減',
  '新規事業開発',
  '市場参入戦略',
  'オペレーション改善',
  '人材戦略',
  'その他'
];

const steps = ['基本情報', 'クライアント情報', '確認・作成'];

const CreateProject: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    client_name: '',
    industry: '',
    theme: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleInputChange = (field: string) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await projectAPI.createProject(formData);
      navigate(`/project/${result.id}`);
    } catch (err) {
      setError('プロジェクトの作成に失敗しました');
      console.error('Error creating project:', err);
    } finally {
      setLoading(false);
    }
  };

  const isStepValid = (step: number) => {
    switch (step) {
      case 0:
        return formData.name.trim() !== '' && formData.industry !== '' && formData.theme !== '';
      case 1:
        return formData.client_name.trim() !== '' && formData.description.trim() !== '';
      default:
        return true;
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="プロジェクト名"
                value={formData.name}
                onChange={handleInputChange('name')}
                required
                placeholder="例: A社関西エリア冷凍食品事業の売上回復戦略"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="業界"
                value={formData.industry}
                onChange={handleInputChange('industry')}
                required
              >
                {industries.map((industry) => (
                  <MenuItem key={industry} value={industry}>
                    {industry}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="テーマ"
                value={formData.theme}
                onChange={handleInputChange('theme')}
                required
              >
                {themes.map((theme) => (
                  <MenuItem key={theme} value={theme}>
                    {theme}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="クライアント企業名"
                value={formData.client_name}
                onChange={handleInputChange('client_name')}
                required
                placeholder="例: 株式会社A社"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="プロジェクト概要"
                value={formData.description}
                onChange={handleInputChange('description')}
                required
                placeholder="具体的なプロジェクトの背景、課題、目的を記述してください"
              />
            </Grid>
          </Grid>
        );
      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                プロジェクト情報の確認
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography><strong>プロジェクト名:</strong> {formData.name}</Typography>
                <Typography><strong>クライアント:</strong> {formData.client_name}</Typography>
                <Typography><strong>業界:</strong> {formData.industry}</Typography>
                <Typography><strong>テーマ:</strong> {formData.theme}</Typography>
                <Typography><strong>概要:</strong> {formData.description}</Typography>
              </Box>
            </Grid>
          </Grid>
        );
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          新規プロジェクト作成
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 4 }}>
          {renderStepContent(activeStep)}
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
          <Button
            color="inherit"
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            戻る
          </Button>
          <Box sx={{ flex: '1 1 auto' }} />
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? '作成中...' : 'プロジェクト作成'}
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={!isStepValid(activeStep)}
            >
              次へ
            </Button>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default CreateProject;