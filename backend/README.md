# Adaptive RAG Backend

This is the backend service for the Adaptive RAG (Retrieval-Augmented Generation) system.

## Overview

The backend provides:
- RESTful API for chat interactions
- Document ingestion and vector storage
- Intelligent routing between vector database and web search
- PostgreSQL for session and chat history storage

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start PostgreSQL and API services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This starts:
- **PostgreSQL**: Port 5432
- **Backend API**: Port 8000 (http://localhost:8000)
- **API Docs**: http://localhost:8000/docs

### Option 2: Local Development

1. **Start PostgreSQL locally**:
   ```bash
   # macOS
   brew services start postgresql
   
   # Or use the setup script from root directory
   ../setup_postgres.sh
   ```

2. **Set up Python environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   ```

5. **Run the API**:
   ```bash
   python run.py
   ```

## Environment Configuration

### For Docker (.env.docker)
- `DATABASE_URL`: Uses `postgres:5432` (container networking)
- Automatically used when running `docker-compose up`

### For Local Development (.env)
- `DATABASE_URL`: Uses `localhost:5432`
- Used when running `python run.py` locally

### Required API Keys
- `GOOGLE_API_KEY`: For Gemini models
- `TAVILY_API_KEY`: For web search functionality

## API Endpoints

### Health Checkcan 
```bash
GET /api/v1/health
```

### Chat
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "question": "What is adaptive RAG?",
  "session_id": "optional-session-id"
}
```

### Document Ingestion
```bash
POST /api/v1/documents/ingest
Content-Type: application/json

{
  "urls": ["https://example.com/article"],
  "texts": ["Raw text to ingest"]
}
```

### Clear Documents
```bash
DELETE /api/v1/documents/clear
```

## Docker Commands

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f api
docker-compose logs -f postgres

# Execute commands in containers
docker-compose exec api python init_db.py
docker-compose exec postgres psql -U yvettegonzalez -d adaptive_rag_db

# Stop and remove containers
docker-compose down

# Remove containers and volumes (clears database)
docker-compose down -v
```

## Development

### Running Tests
```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration
```

### Code Formatting
```bash
# Format code
black .

# Sort imports
isort .
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Architecture

The backend uses:
- **FastAPI**: Web framework
- **LangChain/LangGraph**: RAG orchestration
- **ChromaDB**: Vector storage
- **PostgreSQL**: Session persistence
- **Google Gemini**: LLM model

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :5432

# Kill process
kill -9 <PID>
```

### Database Connection Issues
1. Check PostgreSQL is running
2. Verify DATABASE_URL in `.env` or `.env.docker`
3. For Docker: Ensure postgres container is healthy
4. For local: Check PostgreSQL service status

### API Key Issues
- Ensure all required API keys are set in environment
- Check for typos or extra spaces
- Verify keys are valid and have proper permissions

## Production Deployment

For production, consider:
1. Using managed PostgreSQL (AWS RDS, Google Cloud SQL)
2. Setting `DEBUG=false` in environment
3. Configuring proper CORS origins
4. Adding authentication/authorization
5. Setting up monitoring and logging