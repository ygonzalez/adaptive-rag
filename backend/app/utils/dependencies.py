from functools import lru_cache

from app.services.chat_service import ChatService
from app.services.document_service import DocumentService

@lru_cache()
def get_chat_service() -> ChatService:
    """Get singleton instance of ChatService"""
    return ChatService()

@lru_cache()
def get_document_service() -> DocumentService:
    """Get singleton instance of DocumentService"""
    return DocumentService()