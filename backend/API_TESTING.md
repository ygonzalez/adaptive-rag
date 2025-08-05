# API Testing Guide

## Quick Start

1. Start the server:
```bash
cd backend
python run.py
```

2. In another terminal, run the test script:
```bash
cd backend
python test_api.py
```

## Testing Methods

### 1. Using cURL

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Chat API
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is agent memory?",
    "session_id": "test-123"
  }'
```

#### Ingest Documents
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://lilianweng.github.io/posts/2023-06-23-agent/"]
  }'
```

#### Clear Documents
```bash
curl -X DELETE http://localhost:8000/api/v1/documents/clear
```

### 2. Using HTTPie (more user-friendly)

Install HTTPie:
```bash
pip install httpie
```

#### Health Check
```bash
http GET localhost:8000/api/v1/health
```

#### Chat API
```bash
http POST localhost:8000/api/v1/chat \
  question="What is agent memory?" \
  session_id="test-123"
```

### 3. Interactive API Documentation

FastAPI provides automatic interactive documentation:

1. **Swagger UI**: http://localhost:8000/docs
   - Interactive API testing
   - Try out endpoints directly
   - See request/response schemas

2. **ReDoc**: http://localhost:8000/redoc
   - Clean API documentation
   - Better for reading

### 4. Using Postman

1. Import this collection:

```json
{
  "info": {
    "name": "Adaptive RAG API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/v1/health"
      }
    },
    {
      "name": "Chat",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/v1/chat",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"question\": \"What is agent memory?\",\n  \"session_id\": \"test-123\"\n}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

### 5. Python Requests (programmatic)

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# Chat
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"question": "What is agent memory?"}
)
print(response.json())
```

### 6. Using pytest for API tests

Create `tests/test_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post(
        "/api/v1/chat",
        json={"question": "test question"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()
```

Run with: `pytest tests/test_api.py`

## Common Test Scenarios

### 1. Basic Chat Flow
```bash
# Ask a question about agent memory (should use vectorstore)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is agent memory?"}'
```

### 2. Web Search Fallback
```bash
# Ask about current events (should trigger web search)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What happened in the news today?"}'
```

### 3. Session Management
```bash
# First question
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "session_id": "user-123"}'

# Follow-up question in same session
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Can you explain more?", "session_id": "user-123"}'

# Get session history
curl http://localhost:8000/api/v1/chat/sessions/user-123
```

## Monitoring & Debugging

1. **Check logs**: The server prints detailed logs for each request
2. **Check vectorstore**: Verify `.chroma/` directory exists
3. **Environment variables**: Ensure `.env` file has valid API keys

## Performance Testing

Using Apache Bench (ab):
```bash
# Test 100 requests with 10 concurrent
ab -n 100 -c 10 -p request.json -T application/json \
  http://localhost:8000/api/v1/chat
```

Using locust:
```python
# locustfile.py
from locust import HttpUser, task

class RAGUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/api/v1/chat", json={
            "question": "What is agent memory?"
        })
```

Run with: `locust -f locustfile.py --host=http://localhost:8000`