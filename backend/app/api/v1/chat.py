from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.chat_service import ChatService
from app.utils.dependencies import get_chat_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse, responses={
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    """
    Process a chat request through the RAG system
    """
    try:
        # Run the chat service directly in the async context
        # This avoids the event loop issue with ThreadPoolExecutor
        result = chat_service.process_question(
            request.question,
            request.session_id
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}", response_model=Dict[str, Any])
def get_session(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat session history
    """
    try:
        history = chat_service.get_session_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))