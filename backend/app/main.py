from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.v1 import chat, documents, health, visualization
from app.core.ingestion.ingestion import ensure_vectorstore_exists

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting up...")
    ensure_vectorstore_exists()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Adaptive RAG API",
    description="A production-ready RAG system with intelligent routing and web search fallback",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(visualization.router, prefix="/api/v1", tags=["visualization"])

@app.get("/")
async def root():
    return {"message": "Welcome to Adaptive RAG API"}