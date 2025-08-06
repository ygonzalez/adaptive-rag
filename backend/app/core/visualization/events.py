"""
Process visualization events system.
Captures detailed information about each step in the RAG workflow for real-time visualization.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import asyncio
import json


class ProcessStepType(str, Enum):
    """Types of process steps in the RAG workflow"""
    ROUTING = "routing"
    RETRIEVE = "retrieve"
    GRADE_DOCUMENTS = "grade_documents"
    GENERATE = "generate"
    WEBSEARCH = "websearch"
    HALLUCINATION_CHECK = "hallucination_check"
    ANSWER_GRADING = "answer_grading"


class ProcessStepStatus(str, Enum):
    """Status of a process step"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class DocumentGrade(BaseModel):
    """Document relevance grading information"""
    content_preview: str
    relevance_score: str  # "yes" or "no"
    reasoning: Optional[str] = None
    source: Optional[str] = None


class ProcessEvent(BaseModel):
    """A single process event in the RAG workflow"""
    session_id: str
    event_id: str
    step_type: ProcessStepType
    status: ProcessStepStatus
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    # Core data
    question: Optional[str] = None
    
    # Step-specific data
    routing_decision: Optional[str] = None  # "vectorstore" or "websearch"
    routing_confidence: Optional[float] = None
    routing_reasoning: Optional[str] = None
    
    documents_found: Optional[int] = None
    documents_graded: Optional[List[DocumentGrade]] = None
    relevant_documents: Optional[int] = None
    
    web_search_query: Optional[str] = None
    web_sources_found: Optional[int] = None
    
    generation_attempt: Optional[int] = None
    generation_preview: Optional[str] = None
    
    hallucination_score: Optional[str] = None  # "yes" or "no"
    answer_grade: Optional[str] = None  # "yes" or "no"
    
    # Timing
    duration_ms: Optional[int] = None
    
    # Error information
    error_message: Optional[str] = None
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None


class ProcessVisualizationManager:
    """Manages process events and WebSocket broadcasting"""
    
    def __init__(self):
        self.active_sessions: Dict[str, List[ProcessEvent]] = {}
        self.websocket_connections: Dict[str, List] = {}
    
    async def emit_event(self, event: ProcessEvent):
        """Emit a process event and broadcast to connected WebSocket clients"""
        session_id = event.session_id
        
        # Store event in session history
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = []
        self.active_sessions[session_id].append(event)
        
        # Broadcast to WebSocket connections for this session
        if session_id in self.websocket_connections:
            try:
                event_data = event.model_dump_json()
                disconnected_connections = []
                
                for websocket in self.websocket_connections[session_id]:
                    try:
                        await websocket.send_text(event_data)
                    except Exception as e:
                        print(f"WebSocket send error: {e}")
                        disconnected_connections.append(websocket)
            except Exception as e:
                print(f"Error serializing event: {e}")
                return
            
            # Clean up disconnected connections
            for conn in disconnected_connections:
                self.websocket_connections[session_id].remove(conn)
    
    def add_websocket_connection(self, session_id: str, websocket):
        """Add a WebSocket connection for a session"""
        if session_id not in self.websocket_connections:
            self.websocket_connections[session_id] = []
        self.websocket_connections[session_id].append(websocket)
    
    def remove_websocket_connection(self, session_id: str, websocket):
        """Remove a WebSocket connection for a session"""
        if session_id in self.websocket_connections:
            try:
                self.websocket_connections[session_id].remove(websocket)
                if not self.websocket_connections[session_id]:
                    del self.websocket_connections[session_id]
            except ValueError:
                pass
    
    def get_session_events(self, session_id: str) -> List[ProcessEvent]:
        """Get all events for a session"""
        return self.active_sessions.get(session_id, [])
    
    def clear_session_events(self, session_id: str):
        """Clear events for a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]


# Global instance
process_manager = ProcessVisualizationManager()


# Helper functions for emitting events
def create_event_id() -> str:
    """Create a unique event ID"""
    return f"event-{datetime.now().timestamp()}-{id(datetime.now())}"


async def emit_routing_started(session_id: str, question: str):
    """Emit routing started event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.ROUTING,
        status=ProcessStepStatus.STARTED,
        timestamp=datetime.now(),
        question=question
    )
    await process_manager.emit_event(event)


async def emit_routing_completed(
    session_id: str, 
    question: str, 
    decision: str, 
    confidence: Optional[float] = None,
    reasoning: Optional[str] = None,
    duration_ms: Optional[int] = None
):
    """Emit routing completed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.ROUTING,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        routing_decision=decision,
        routing_confidence=confidence,
        routing_reasoning=reasoning,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_retrieve_started(session_id: str, question: str):
    """Emit retrieve started event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.RETRIEVE,
        status=ProcessStepStatus.STARTED,
        timestamp=datetime.now(),
        question=question
    )
    await process_manager.emit_event(event)


async def emit_retrieve_completed(
    session_id: str, 
    question: str, 
    documents_found: int,
    duration_ms: Optional[int] = None
):
    """Emit retrieve completed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.RETRIEVE,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        documents_found=documents_found,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_grading_started(session_id: str, question: str):
    """Emit document grading started event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.GRADE_DOCUMENTS,
        status=ProcessStepStatus.STARTED,
        timestamp=datetime.now(),
        question=question
    )
    await process_manager.emit_event(event)


async def emit_grading_completed(
    session_id: str, 
    question: str, 
    documents_graded: List[DocumentGrade],
    relevant_documents: int,
    duration_ms: Optional[int] = None
):
    """Emit document grading completed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.GRADE_DOCUMENTS,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        documents_graded=documents_graded,
        relevant_documents=relevant_documents,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_websearch_started(session_id: str, question: str, query: str):
    """Emit web search started event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.WEBSEARCH,
        status=ProcessStepStatus.STARTED,
        timestamp=datetime.now(),
        question=question,
        web_search_query=query
    )
    await process_manager.emit_event(event)


async def emit_websearch_completed(
    session_id: str, 
    question: str, 
    query: str,
    sources_found: int,
    duration_ms: Optional[int] = None
):
    """Emit web search completed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.WEBSEARCH,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        web_search_query=query,
        web_sources_found=sources_found,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_generation_started(
    session_id: str, 
    question: str, 
    attempt: int
):
    """Emit generation started event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.GENERATE,
        status=ProcessStepStatus.STARTED,
        timestamp=datetime.now(),
        question=question,
        generation_attempt=attempt
    )
    await process_manager.emit_event(event)


async def emit_generation_completed(
    session_id: str, 
    question: str, 
    attempt: int,
    generation_preview: str,
    duration_ms: Optional[int] = None
):
    """Emit generation completed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.GENERATE,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        generation_attempt=attempt,
        generation_preview=generation_preview[:200] + "..." if len(generation_preview) > 200 else generation_preview,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_hallucination_check(
    session_id: str, 
    question: str, 
    score: str,
    duration_ms: Optional[int] = None
):
    """Emit hallucination check event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.HALLUCINATION_CHECK,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        hallucination_score=score,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_answer_grading(
    session_id: str, 
    question: str, 
    grade: str,
    duration_ms: Optional[int] = None
):
    """Emit answer grading event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=ProcessStepType.ANSWER_GRADING,
        status=ProcessStepStatus.COMPLETED,
        timestamp=datetime.now(),
        question=question,
        answer_grade=grade,
        duration_ms=duration_ms
    )
    await process_manager.emit_event(event)


async def emit_step_failed(
    session_id: str, 
    step_type: ProcessStepType, 
    question: str,
    error_message: str
):
    """Emit step failed event"""
    event = ProcessEvent(
        session_id=session_id,
        event_id=create_event_id(),
        step_type=step_type,
        status=ProcessStepStatus.FAILED,
        timestamp=datetime.now(),
        question=question,
        error_message=error_message
    )
    await process_manager.emit_event(event)