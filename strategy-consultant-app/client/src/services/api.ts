import axios from 'axios';
import { Project, Argument, PastCase, ClientInfo, AIFeedback } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（デバッグ用）
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', {
      url: config.url,
      method: config.method,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`
    });
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// レスポンスインターセプター（デバッグ用）
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', {
      status: response.status,
      data: response.data,
      url: response.config.url
    });
    return response;
  },
  (error) => {
    console.error('API Response Error:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    });
    return Promise.reject(error);
  }
);

// プロジェクト関連API
export const projectAPI = {
  // プロジェクト一覧取得
  getProjects: (): Promise<Project[]> =>
    api.get('/projects').then(response => response.data),

  // プロジェクト作成
  createProject: (project: Omit<Project, 'id' | 'created_at' | 'updated_at'>): Promise<{ id: number; message: string }> =>
    api.post('/projects', project).then(response => response.data),

  // プロジェクト詳細取得
  getProject: (id: number): Promise<Project> =>
    api.get(`/projects/${id}`).then(response => response.data),
};

// 論点関連API
export const argumentAPI = {
  // プロジェクトの論点一覧取得
  getArguments: (projectId: number): Promise<Argument[]> =>
    api.get(`/projects/${projectId}/arguments`).then(response => response.data),

  // 論点作成
  createArgument: (projectId: number, argument: Omit<Argument, 'id' | 'project_id' | 'created_at' | 'updated_at' | 'ai_consensus' | 'ai_feedback'>): Promise<{ id: number; message: string }> =>
    api.post(`/projects/${projectId}/arguments`, argument).then(response => response.data),

  // 論点更新
  updateArgument: (id: number, argument: Partial<Argument>): Promise<{ message: string }> =>
    api.put(`/arguments/${id}`, argument).then(response => response.data),

  // 論点削除
  deleteArgument: (id: number): Promise<{ message: string }> =>
    api.delete(`/arguments/${id}`).then(response => response.data),

  // AI検証実行
  verifyWithAI: (id: number): Promise<AIFeedback> =>
    api.post(`/ai-verify/${id}`).then(response => response.data),
};

// 過去事例関連API
export const pastCaseAPI = {
  // 過去事例検索
  searchPastCases: (params: {
    industry?: string;
    theme?: string;
    tags?: string;
  }): Promise<PastCase[]> =>
    api.get('/past-cases', { params }).then(response => response.data),

  // 過去事例作成
  createPastCase: (pastCase: Omit<PastCase, 'id' | 'created_at'>): Promise<{ id: number; message: string }> =>
    api.post('/past-cases', pastCase).then(response => response.data),
};

// クライアント情報関連API
export const clientInfoAPI = {
  // クライアント情報取得
  getClientInfo: (projectId: number): Promise<ClientInfo> =>
    api.get(`/projects/${projectId}/client-info`).then(response => response.data),

  // クライアント情報作成・更新
  saveClientInfo: (projectId: number, clientInfo: Omit<ClientInfo, 'id' | 'project_id'>): Promise<{ message: string }> =>
    api.post(`/projects/${projectId}/client-info`, clientInfo).then(response => response.data),
};

export default api;