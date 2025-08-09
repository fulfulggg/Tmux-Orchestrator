import React, { useState } from 'react';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
} from '@mui/x-data-grid';
import {
  Box,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Psychology as PsychologyIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { Argument, AIFeedback } from '../types';
import { argumentAPI } from '../services/api';

interface ArgumentTableProps {
  arguments: Argument[];
  onRefresh: () => void;
}

const ArgumentTable: React.FC<ArgumentTableProps> = ({ arguments: argumentsList, onRefresh }) => {
  const [selectedArgument, setSelectedArgument] = useState<Argument | null>(null);
  const [aiFeedbackDialog, setAiFeedbackDialog] = useState(false);
  const [aiFeedback, setAiFeedback] = useState<AIFeedback | null>(null);
  const [loading, setLoading] = useState(false);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'high':
        return '高';
      case 'medium':
        return '中';
      case 'low':
        return '低';
      default:
        return priority;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'info';
      case 'not_started':
        return 'default';
      case 'on_hold':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return '完了';
      case 'in_progress':
        return '進行中';
      case 'not_started':
        return '未着手';
      case 'on_hold':
        return '保留';
      default:
        return status;
    }
  };

  const getConsensusIcon = (consensus: number) => {
    if (consensus === 3) {
      return <CheckCircleIcon color="success" />;
    } else if (consensus === 2) {
      return <WarningIcon color="warning" />;
    } else if (consensus === 1) {
      return <ErrorIcon color="error" />;
    }
    return null;
  };

  const handleAIVerify = async (argument: Argument) => {
    try {
      setLoading(true);
      const feedback = await argumentAPI.verifyWithAI(argument.id);
      setAiFeedback(feedback);
      setSelectedArgument(argument);
      setAiFeedbackDialog(true);
      onRefresh(); // テーブルを更新
    } catch (error) {
      console.error('AI verification failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'major_point',
      headerName: '大論点',
      width: 200,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            fontWeight: 'medium'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'medium_point',
      headerName: '中論点',
      width: 200,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'minor_point',
      headerName: '小論点',
      width: 250,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'hypothesis',
      headerName: '仮説',
      width: 300,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'verification_approach',
      headerName: '検証アプローチ',
      width: 250,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'required_data',
      headerName: '必要データ',
      width: 200,
      renderCell: (params: GridRenderCellParams) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden', 
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      ),
    },
    {
      field: 'assignee',
      headerName: '担当者',
      width: 120,
    },
    {
      field: 'priority',
      headerName: '優先度',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={getPriorityLabel(params.value as string)}
          color={getPriorityColor(params.value as string) as any}
          size="small"
        />
      ),
    },
    {
      field: 'status',
      headerName: 'ステータス',
      width: 120,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={getStatusLabel(params.value as string)}
          color={getStatusColor(params.value as string) as any}
          size="small"
          variant="outlined"
        />
      ),
    },
    {
      field: 'deadline',
      headerName: '期限',
      width: 120,
    },
    {
      field: 'ai_consensus',
      headerName: 'AI検証',
      width: 100,
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {getConsensusIcon(params.value as number)}
        </Box>
      ),
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'アクション',
      width: 150,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleAIVerify(params.row as Argument)}
            disabled={loading}
          >
            <Tooltip title="AI検証実行">
              <PsychologyIcon />
            </Tooltip>
          </IconButton>
          <IconButton
            size="small"
            onClick={() => {
              // TODO: 編集ダイアログを実装
              alert('編集機能は開発中です');
            }}
          >
            <Tooltip title="編集">
              <EditIcon />
            </Tooltip>
          </IconButton>
          <IconButton
            size="small"
            onClick={() => {
              // TODO: 削除機能を実装
              if (window.confirm('この論点を削除しますか？')) {
                alert('削除機能は開発中です');
              }
            }}
          >
            <Tooltip title="削除">
              <DeleteIcon />
            </Tooltip>
          </IconButton>
        </Box>
      ),
    },
  ];

  return (
    <>
      <Box sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={argumentsList}
          columns={columns}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          checkboxSelection={false}
          sx={{
            '& .MuiDataGrid-cell': {
              alignItems: 'flex-start',
              paddingTop: 1,
              paddingBottom: 1,
            },
            '& .MuiDataGrid-row': {
              minHeight: '60px !important',
            },
          }}
        />
      </Box>

      {/* AI検証結果ダイアログ */}
      <Dialog
        open={aiFeedbackDialog}
        onClose={() => setAiFeedbackDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          AI相互検証結果
          {selectedArgument && (
            <Typography variant="subtitle2" color="textSecondary">
              論点: {selectedArgument.minor_point}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {aiFeedback && (
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                {aiFeedback.overall_feedback}
              </Alert>
              
              <Typography variant="h6" gutterBottom>
                各AIモデルからのフィードバック
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  Claude 4.1 Opus:
                </Typography>
                <Typography variant="body2">
                  {aiFeedback.claude_feedback}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  o3 Pro:
                </Typography>
                <Typography variant="body2">
                  {aiFeedback.openai_feedback}
                </Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold">
                  Gemini 2.5:
                </Typography>
                <Typography variant="body2">
                  {aiFeedback.gemini_feedback}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiFeedbackDialog(false)}>
            閉じる
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ArgumentTable;
