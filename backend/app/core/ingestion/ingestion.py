import os
import shutil
import logging
from typing import List
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..models.model import get_embedding_model
from .healthcare_data import get_healthcare_urls

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class DocumentIngestion:
    """Simple document ingestion with semantic chunking."""

    def __init__(self, collection_name: str = "rag-chroma", persist_directory: str = "./.chroma"):
        self.embed_model = get_embedding_model()
        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Semantic chunker - the main improvement
        self.semantic_splitter = SemanticChunker(
            self.embed_model,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=90
        )

        # Fallback for edge cases
        self.fallback_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=500,
            chunk_overlap=50
        )

        self.vectorstore = self._get_vectorstore()

    def _get_vectorstore(self) -> Chroma:
        """Get or create vectorstore."""
        if os.path.exists(self.persist_directory):
            logger.info("Loading existing vectorstore")
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embed_model,
                persist_directory=self.persist_directory
            )
        else:
            logger.info("Creating new vectorstore")
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embed_model,
                persist_directory=self.persist_directory
            )

    def load_documents(self, urls: List[str]) -> List[Document]:
        """Load documents from URLs."""
        docs = []
        for url in urls:
            try:
                logger.info(f"Loading: {url}")
                loader = WebBaseLoader(url)
                docs.extend(loader.load())
            except Exception as e:
                logger.error(f"Failed to load {url}: {e}")
        return docs

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Chunk documents using semantic chunking with fallback."""
        all_chunks = []

        for doc in documents:
            try:
                # Try semantic chunking first
                chunks = self.semantic_splitter.split_documents([doc])

                # Use fallback for very large chunks
                final_chunks = []
                for chunk in chunks:
                    if len(chunk.page_content) > 1500:
                        final_chunks.extend(self.fallback_splitter.split_documents([chunk]))
                    else:
                        final_chunks.append(chunk)

                all_chunks.extend(final_chunks)
                logger.info(f"Created {len(final_chunks)} chunks from {doc.metadata.get('source', 'document')}")

            except Exception as e:
                logger.error(f"Semantic chunking failed: {e}, using fallback")
                all_chunks.extend(self.fallback_splitter.split_documents([doc]))

        return all_chunks

    def add_to_vectorstore(self, chunks: List[Document]) -> None:
        """Add chunks to vectorstore."""
        if chunks:
            self.vectorstore.add_documents(chunks)
            logger.info(f"Added {len(chunks)} chunks to vectorstore")

    def get_retriever(self):
        """Get retriever for the vectorstore."""
        return self.vectorstore.as_retriever()

def create_vectorstore(urls: List[str] = None) -> DocumentIngestion:
    """Create and populate vectorstore with documents."""

    # Default URLs if none provided - AI in Healthcare focus
    if urls is None:
        urls = get_healthcare_urls()

    # Create ingestion system
    ingestion = DocumentIngestion()

    # Load and process documents
    logger.info("🚀 Starting document ingestion")
    documents = ingestion.load_documents(urls)

    if not documents:
        logger.error("No documents loaded!")
        return ingestion

    logger.info(f"Loaded {len(documents)} documents")

    # Chunk documents
    chunks = ingestion.chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")

    # Add to vectorstore
    ingestion.add_to_vectorstore(chunks)
    logger.info("✅ Ingestion complete!")

    return ingestion

# Simple access functions
def get_retriever():
    """Get the default retriever from existing vectorstore."""
    # Just load existing vectorstore without re-ingesting
    ingestion = DocumentIngestion()
    return ingestion.get_retriever()

def clear_vectorstore(persist_directory: str = "./.chroma"):
    """Clear the existing vectorstore."""
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        logger.info(f"Cleared vectorstore at {persist_directory}")
    else:
        logger.info("No existing vectorstore to clear")

def ingest_urls(urls: List[str]) -> None:
    """Ingest documents from URLs."""
    clear_vectorstore()
    create_vectorstore(urls)

def ingest_texts(texts: List[str]) -> None:
    """Ingest documents from raw texts."""
    # Create Document objects from texts
    documents = [Document(page_content=text) for text in texts]
    
    # Create ingestion system
    ingestion = DocumentIngestion()
    
    # Chunk documents
    chunks = ingestion.chunk_documents(documents)
    
    # Add to vectorstore
    ingestion.add_to_vectorstore(chunks)

def ensure_vectorstore_exists() -> None:
    """Ensure the vectorstore exists, create if not."""
    if not os.path.exists("./.chroma"):
        logger.info("No vectorstore found, creating with default documents...")
        create_vectorstore()

if __name__ == "__main__":
    # Clear existing vectorstore to ensure no duplicates
    clear_vectorstore()
    
    # Create fresh vectorstore
    ingestion = create_vectorstore()
    retriever = ingestion.get_retriever()
    print(f"Retriever ready with vectorstore: {ingestion.vectorstore}")