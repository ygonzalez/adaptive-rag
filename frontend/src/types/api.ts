// API Request/Response Types
export interface ChatRequest {
  question: string;
  session_id?: string;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata: Record<string, any>;
  }>;
  used_web_search: boolean;
  session_id?: string;
}

export interface DocumentIngestionRequest {
  urls?: string[];
  texts?: string[];
}

export interface DocumentIngestionResponse {
  success: boolean;
  message: string;
  documents_processed: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  service: string;
}

// UI State Types
export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: ChatResponse['sources'];
  usedWebSearch?: boolean;
}

export interface AppState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
}