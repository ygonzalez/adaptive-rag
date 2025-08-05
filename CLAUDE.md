# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Commands
- **Format code**: `black .` - Formats Python code to Black style
- **Sort imports**: `isort .` - Sorts and organizes imports
- **Run tests**: `pytest` - Runs all tests
- **Type check**: Check if mypy or other type checkers are configured
- **Run ingestion**: `python ingestion.py` - Clears existing vectorstore and ingests documents fresh (prevents duplicates)
- **Run application**: `python main.py` - Starts the interactive chatbot (uses existing vectorstore)

### Environment Setup
Create a `.env` file with these required API keys:
- `GOOGLE_API_KEY` - Required for Gemini models
- `TAVILY_API_KEY` - Required for web search functionality

## Architecture

This is an Adaptive RAG (Retrieval-Augmented Generation) system using LangChain and LangGraph that implements a sophisticated question-answering workflow with fallback to web search.

### Core Components

1. **Document Ingestion** (`ingestion.py`)
   - Uses `SemanticChunker` for intelligent text splitting based on semantic similarity
   - Falls back to `RecursiveCharacterTextSplitter` for chunks >1500 chars
   - Stores embeddings in Chroma vector database persisted to `./.chroma`
   - Default ingestion URLs are Lilian Weng's blog posts
   - Provides `get_retriever()` for accessing the vector store

2. **Model Management** (`model.py`)
   - Chat model: `gemini-2.0-flash` via Google Generative AI
   - Embedding model: `models/text-embedding-004`
   - Singleton pattern for model instances via `ModelManager`
   - Lazy loading of models for performance

3. **Graph Workflow** (`graph/`)
   - **State Management** (`state.py`): `GraphState` tracks question, generation, web_search flag, and documents
   - **Node Constants** (`consts.py`): RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
   - **Workflow Flow**:
     1. Route question (vectorstore vs web search)
     2. Retrieve documents from vector store
     3. Grade document relevance
     4. Generate answer (with hallucination/answer grading)
     5. Fall back to web search if needed
   
4. **Chain Components** (`graph/chains/`)
   - `router.py`: Routes questions to vectorstore or web search
   - `retrieval_grader.py`: Grades document relevance to question
   - `generation.py`: Generates answers from documents
   - `hallucination_grader.py`: Checks if generation is grounded in documents
   - `answer_grader.py`: Verifies answer addresses the question

5. **Node Implementations** (`graph/nodes/`)
   - `retrieve.py`: Retrieves documents from vector store
   - `grade_documents.py`: Filters relevant documents
   - `generate.py`: Generates final answer
   - `web_search.py`: Performs Tavily web search

### Key Design Patterns
- Graph-based control flow with conditional routing
- Multi-stage answer validation (hallucination check + answer grading)
- Automatic fallback to web search for inadequate answers
- Semantic chunking with 90th percentile breakpoint threshold
- Interactive CLI interface in `main.py`