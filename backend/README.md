# Adaptive RAG Backend

Production-ready FastAPI backend for the Adaptive RAG system.

## Structure

```
backend/app/
├── core/            # Business logic core
│   ├── graph/       # RAG system with LangGraph
│   ├── models/      # Model management
│   └── ingestion/   # Document processing
├── api/             # FastAPI routes
├── services/        # Business services
├── models/          # Pydantic schemas
└── utils/           # Utilities
```

## Setup

1. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python run.py
```

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/chat` - Process a question through RAG
- `POST /api/v1/documents/ingest` - Ingest new documents
- `DELETE /api/v1/documents/clear` - Clear vector store

## Docker

Build and run with Docker:
```bash
docker-compose up --build
```

## CLI Usage

For interactive chat:
```bash
python cli.py
```

## Testing

Run all tests:
```bash
pytest
```

Run only unit tests:
```bash
pytest -m unit
```

Run only integration tests:
```bash
pytest -m integration
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```