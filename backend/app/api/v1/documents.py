from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import DocumentIngestionRequest, DocumentIngestionResponse, ErrorResponse
from app.services.document_service import DocumentService
from app.utils.dependencies import get_document_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/documents/ingest", response_model=DocumentIngestionResponse, responses={
    500: {"model": ErrorResponse, "description": "Internal server error"}
})
async def ingest_documents(
    request: DocumentIngestionRequest,
    document_service: DocumentService = Depends(get_document_service)
) -> DocumentIngestionResponse:
    """
    Ingest documents into the vector store
    """
    try:
        result = await document_service.ingest_documents(
            urls=request.urls,
            texts=request.texts
        )
        return DocumentIngestionResponse(**result)
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/clear")
async def clear_documents(
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Clear all documents from the vector store
    """
    try:
        await document_service.clear_vectorstore()
        return {"success": True, "message": "Vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))