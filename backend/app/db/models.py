from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Message content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Metadata
    used_web_search = Column(Boolean, default=False)
    sources = Column(JSON, default=list)  # Store source documents as JSON
    generation_attempts = Column(Integer, default=0)
    web_search_attempts = Column(Integer, default=0)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")