from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "adaptive-rag-api"
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # TODO: Add actual readiness checks (DB connection, model loading, etc.)
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }