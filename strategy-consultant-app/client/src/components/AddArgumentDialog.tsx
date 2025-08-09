import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
} from '@mui/material';
import { argumentAPI } from '../services/api';
import { Argument } from '../types';

interface AddArgumentDialogProps {
  open: boolean;
  onClose: () => void;
  projectId: number;
  onArgumentAdded: () => void;
}

const priorities = [
  { value: 'high', label: '高' },
  { value: 'medium', label: '中' },
  { value: 'low', label: '低' },
];

const statuses = [
  { value: 'not_started', label: '未着手' },
  { value: 'in_progress', label: '進行中' },
  { value: 'completed', label: '完了' },
  { value: 'on_hold', label: '保留' },
];

const AddArgumentDialog: React.FC<AddArgumentDialogProps> = ({
  open,
  onClose,
  projectId,
  onArgumentAdded,
}) => {
  const [formData, setFormData] = useState({
    major_point: '',
    medium_point: '',
    minor_point: '',
    hypothesis: '',
    verification_approach: '',
    required_data: '',
    assignee: '',
    priority: 'medium' as 'high' | 'medium' | 'low',
    status: 'not_started' as 'not_started' | 'in_progress' | 'completed' | 'on_hold',
    deadline: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: string) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await argumentAPI.createArgument(projectId, formData);
      
      // フォームをリセット
      setFormData({
        major_point: '',
        medium_point: '',
        minor_point: '',
        hypothesis: '',
        verification_approach: '',
        required_data: '',
        assignee: '',
        priority: 'medium' as 'high' | 'medium' | 'low',
        status: 'not_started' as 'not_started' | 'in_progress' | 'completed' | 'on_hold',
        deadline: '',
      });
      
      onArgumentAdded();
    } catch (err) {
      setError('論点の追加に失敗しました');
      console.error('Error creating argument:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      major_point: '',
      medium_point: '',
      minor_point: '',
      hypothesis: '',
      verification_approach: '',
      required_data: '',
      assignee: '',
      priority: 'medium' as 'high' | 'medium' | 'low',
      status: 'not_started' as 'not_started' | 'in_progress' | 'completed' | 'on_hold',
      deadline: '',
    });
    setError(null);
    onClose();
  };

  const isFormValid = () => {
    return formData.major_point.trim() !== '' &&
           formData.medium_point.trim() !== '' &&
           formData.minor_point.trim() !== '' &&
           formData.hypothesis.trim() !== '' &&
           formData.verification_approach.trim() !== '';
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>新規論点追加</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        
        <Grid container spacing={3} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="大論点"
              value={formData.major_point}
              onChange={handleInputChange('major_point')}
              required
              placeholder="例: 売上低迷要因の特定"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="中論点"
              value={formData.medium_point}
              onChange={handleInputChange('medium_point')}
              required
              placeholder="例: 競合環境変化による影響"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={2}
              label="小論点"
              value={formData.minor_point}
              onChange={handleInputChange('minor_point')}
              required
              placeholder="例: A社の関西エリア向け冷凍食品事業において、2023年4月のイオン向け売上が前年同月比30%減少した要因分析"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="仮説"
              value={formData.hypothesis}
              onChange={handleInputChange('hypothesis')}
              required
              placeholder="例: 競合B社の新商品『○○シリーズ』の棚割り拡大とプロモーション強化により、A社商品の売上が減少している。特に主力商品の『××冷凍餃子』が影響を受けている可能性が高い。"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="検証アプローチ"
              value={formData.verification_approach}
              onChange={handleInputChange('verification_approach')}
              required
              placeholder="例: 1)イオン各店舗の冷凍食品売場における棚割り変化の調査、2)POSデータによる競合商品と自社商品の売上推移分析、3)店舗スタッフ・顧客ヒアリングによる購買行動変化の把握"
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="必要データ・情報源"
              value={formData.required_data}
              onChange={handleInputChange('required_data')}
              placeholder="例: イオンPOSデータ、店舗棚割り情報、競合商品のプロモーション実績、営業担当者レポート"
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="担当者"
              value={formData.assignee}
              onChange={handleInputChange('assignee')}
              placeholder="例: 田中、佐藤"
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label="優先度"
              value={formData.priority}
              onChange={handleInputChange('priority')}
            >
              {priorities.map((priority) => (
                <MenuItem key={priority.value} value={priority.value}>
                  {priority.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              select
              label="ステータス"
              value={formData.status}
              onChange={handleInputChange('status')}
            >
              {statuses.map((status) => (
                <MenuItem key={status.value} value={status.value}>
                  {status.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              type="date"
              label="期限"
              value={formData.deadline}
              onChange={handleInputChange('deadline')}
              InputLabelProps={{
                shrink: true,
              }}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>
          キャンセル
        </Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={loading || !isFormValid()}
        >
          {loading ? '追加中...' : '論点追加'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AddArgumentDialog;