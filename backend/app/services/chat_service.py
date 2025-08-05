from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.core.graph.graph import app as graph_app
from app.core.graph.state import GraphState

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
    
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
                "documents": []
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
            
            # Store in session if session_id provided
            if session_id:
                if session_id not in self.sessions:
                    self.sessions[session_id] = []
                
                self.sessions[session_id].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "question": question,
                    "answer": result.get("generation", ""),
                    "used_web_search": result.get("web_search", False)
                })
            
            return {
                "answer": result.get("generation", ""),
                "sources": sources,
                "used_web_search": result.get("web_search", False),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error in process_question: {str(e)}")
            raise
    
    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history for a session
        """
        return self.sessions.get(session_id, [])