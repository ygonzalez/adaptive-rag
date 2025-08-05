from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    
class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents used")
    used_web_search: bool = Field(False, description="Whether web search was used")
    session_id: Optional[str] = None
    
class DocumentIngestionRequest(BaseModel):
    urls: Optional[List[str]] = Field(None, description="URLs to ingest")
    texts: Optional[List[str]] = Field(None, description="Raw texts to ingest")
    
class DocumentIngestionResponse(BaseModel):
    success: bool
    message: str
    documents_processed: int
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)