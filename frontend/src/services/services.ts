import axios from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  DocumentIngestionRequest,
  DocumentIngestionResponse,
  HealthResponse
} from '@/types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000, // 30 seconds for chat requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  async health(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },

  // Chat functionality
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat', request);
    return response.data;
  },

  // Document management
  async ingestDocuments(request: DocumentIngestionRequest): Promise<DocumentIngestionResponse> {
    const response = await api.post<DocumentIngestionResponse>('/documents/ingest', request);
    return response.data;
  },

  async clearDocuments(): Promise<{ success: boolean; message: string }> {
    const response = await api.delete('/documents/clear');
    return response.data;
  },

  // Session management
  async getSessionHistory(sessionId: string): Promise<{ session_id: string; history: any[] }> {
    const response = await api.get(`/chat/sessions/${sessionId}`);
    return response.data;
  },
};

export default apiService;