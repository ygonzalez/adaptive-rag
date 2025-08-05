from typing import List, Optional, Dict, Any
import asyncio
import logging
import shutil
import os

from app.core.ingestion.ingestion import ingest_urls, ingest_texts

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.vectorstore_path = "./.chroma"
    
    async def ingest_documents(
        self, 
        urls: Optional[List[str]] = None, 
        texts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Ingest documents from URLs or raw texts
        """
        try:
            documents_processed = 0
            
            if urls:
                # Run URL ingestion in thread pool
                await asyncio.to_thread(ingest_urls, urls)
                documents_processed += len(urls)
            
            if texts:
                # Run text ingestion in thread pool
                await asyncio.to_thread(ingest_texts, texts)
                documents_processed += len(texts)
            
            return {
                "success": True,
                "message": f"Successfully ingested {documents_processed} documents",
                "documents_processed": documents_processed
            }
            
        except Exception as e:
            logger.error(f"Error ingesting documents: {str(e)}")
            return {
                "success": False,
                "message": f"Error ingesting documents: {str(e)}",
                "documents_processed": 0
            }
    
    async def clear_vectorstore(self) -> None:
        """
        Clear the vector store
        """
        try:
            if os.path.exists(self.vectorstore_path):
                await asyncio.to_thread(shutil.rmtree, self.vectorstore_path)
                logger.info("Vector store cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            raise