from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.graph.graph import app as graph_app
from app.core.graph.state import GraphState
from app.db.database import db
from app.db.models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        # Initialize database tables
        db.create_tables()
    
    def process_question(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a question through the RAG graph
        """
        try:
            # Create initial state
            initial_state: GraphState = {
                "question": question,
                "generation": "",
                "web_search": False,
                "documents": [],
                "generation_attempts": 0,
                "web_search_attempts": 0
            }
            
            # Run the graph
            result = graph_app.invoke(initial_state)
            
            # Extract source information
            sources = []
            for doc in result.get("documents", []):
                source = {
                    "content": doc.page_content[:200] + "...",  # First 200 chars
                    "metadata": getattr(doc, 'metadata', {})
                }
                sources.append(source)
            
            # Check if we hit max retries and provide a fallback message
            answer = result.get("generation", "")
            if not answer or answer == "":
                if result.get("generation_attempts", 0) >= 3 or result.get("web_search_attempts", 0) >= 2:
                    answer = (
                        "I apologize, but I'm having difficulty generating a proper response to your question. "
                        "This might be due to the complexity of the query or limitations in the available information. "
                        "Please try rephrasing your question or breaking it down into smaller parts."
                    )
            
            # Store in database if session_id provided
            if session_id:
                with db.session_scope() as session:
                    # Get or create session
                    chat_session = session.query(ChatSession).filter_by(id=session_id).first()
                    if not chat_session:
                        chat_session = ChatSession(id=session_id)
                        session.add(chat_session)
                    
                    # Create message record
                    message = ChatMessage(
                        session_id=session_id,
                        question=question,
                        answer=answer,
                        used_web_search=result.get("web_search", False),
                        sources=sources,
                        generation_attempts=result.get("generation_attempts", 0),
                        web_search_attempts=result.get("web_search_attempts", 0)
                    )
                    session.add(message)
            
            return {
                "answer": answer,
                "sources": sources,
                "used_web_search": result.get("web_search", False),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error in process_question: {str(e)}")
            raise
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for a session from database
        """
        with db.session_scope() as session:
            chat_session = session.query(ChatSession).filter_by(id=session_id).first()
            if not chat_session:
                return []
            
            history = []
            for message in chat_session.messages:
                history.append({
                    "timestamp": message.timestamp.isoformat(),
                    "question": message.question,
                    "answer": message.answer,
                    "used_web_search": message.used_web_search,
                    "sources": message.sources
                })
            
            return history