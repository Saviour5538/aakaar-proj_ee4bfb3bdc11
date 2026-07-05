import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
}

export interface Document {
  id: number;
  name: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

export interface QueryRequest {
  query: string;
  session_id: string;
  user_id: string;
}

export interface QueryResponse {
  answer: string;
  sources: string[];
}

export const register = (data: RegisterRequest) => api.post<TokenResponse>('/api/auth/register', data);

export const login = (data: LoginRequest) => api.post<TokenResponse>('/api/auth/login', data);

export const getCurrentUser = () => api.get<UserResponse>('/api/auth/me');

export const uploadDocument = (file: File, session_id: string, user_id: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', session_id);
  formData.append('user_id', user_id);
  return api.post('/api/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const listDocuments = () => api.get<Document[]>('/api/documents');

export const deleteDocument = (id: number) => api.delete(`/api/documents/${id}`);

export const createConversation = (title: string) =>
  api.post<Conversation>('/api/conversations', { title });

export const listConversations = () => api.get<Conversation[]>('/api/conversations');

export const aiQuery = (data: QueryRequest) => api.post<QueryResponse>('/api/ai/query', data);