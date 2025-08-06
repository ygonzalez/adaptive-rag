/**
 * TypeScript types for RAG process visualization
 */

export type ProcessStepType = 
  | 'routing'
  | 'retrieve'
  | 'grade_documents'
  | 'websearch'
  | 'generate'
  | 'hallucination_check'
  | 'answer_grading';

export type ProcessStepStatus = 
  | 'started'
  | 'completed'
  | 'failed'
  | 'skipped';

export interface DocumentGrade {
  content_preview: string;
  relevance_score: string; // "yes" or "no"
  reasoning?: string;
  source?: string;
}

export interface ProcessEvent {
  session_id: string;
  event_id: string;
  step_type: ProcessStepType;
  status: ProcessStepStatus;
  timestamp: string; // ISO string
  
  // Core data
  question?: string;
  
  // Step-specific data
  routing_decision?: string; // "vectorstore" or "websearch"
  routing_confidence?: number;
  routing_reasoning?: string;
  
  documents_found?: number;
  documents_graded?: DocumentGrade[];
  relevant_documents?: number;
  
  web_search_query?: string;
  web_sources_found?: number;
  
  generation_attempt?: number;
  generation_preview?: string;
  
  hallucination_score?: string; // "yes" or "no"
  answer_grade?: string; // "yes" or "no"
  
  // Timing
  duration_ms?: number;
  
  // Error information
  error_message?: string;
  
  // Additional metadata
  metadata?: Record<string, any>;
}

export interface ProcessVisualizationState {
  events: ProcessEvent[];
  isConnected: boolean;
  connectionError: string | null;
  enabled: boolean;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'ping' | 'pong' | 'get_events' | 'session_events';
  events?: ProcessEvent[];
}

// Step configuration for UI
export interface StepConfig {
  type: ProcessStepType;
  label: string;
  icon: React.ComponentType;
  description: string;
  color: string;
}

export interface ProcessMetrics {
  totalSteps: number;
  completedSteps: number;
  failedSteps: number;
  totalDuration: number;
  averageStepDuration: number;
  retryCount: number;
}

export interface SessionVisualizationData {
  sessionId: string;
  events: ProcessEvent[];
  metrics: ProcessMetrics;
  lastActivity: string;
  isActive: boolean;
}