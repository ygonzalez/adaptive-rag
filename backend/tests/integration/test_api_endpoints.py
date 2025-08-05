import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create TestClient instance for testing
@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as c:
        yield c

@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "adaptive-rag-api"
    
    def test_readiness_check(self, client):
        """Test readiness check"""
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
        assert "timestamp" in data

@pytest.mark.integration
class TestChatEndpoints:
    """Test chat-related endpoints"""
    
    def test_chat_basic_request(self, client):
        """Test basic chat request"""
        response = client.post(
            "/api/v1/chat",
            json={"question": "What is agent memory?"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "used_web_search" in data
        assert isinstance(data["sources"], list)
        assert isinstance(data["used_web_search"], bool)
    
    def test_chat_with_session(self, client):
        """Test chat request with session ID"""
        session_id = "test-session-123"
        response = client.post(
            "/api/v1/chat",
            json={
                "question": "What is RAG?",
                "session_id": session_id
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
    
    def test_chat_invalid_request(self, client):
        """Test chat with invalid request"""
        response = client.post(
            "/api/v1/chat",
            json={}  # Missing required 'question' field
        )
        assert response.status_code == 422  # Validation error
    
    def test_get_session_history(self, client):
        """Test getting session history"""
        session_id = "test-session-456"
        
        # First, create some history
        client.post(
            "/api/v1/chat",
            json={
                "question": "Test question",
                "session_id": session_id
            }
        )
        
        # Then get the history
        response = client.get(f"/api/v1/chat/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "history" in data
        assert data["session_id"] == session_id

@pytest.mark.integration
class TestDocumentEndpoints:
    """Test document management endpoints"""
    
    @pytest.mark.slow
    def test_ingest_texts(self, client):
        """Test ingesting text documents"""
        response = client.post(
            "/api/v1/documents/ingest",
            json={
                "texts": [
                    "This is a test document about artificial intelligence.",
                    "RAG systems combine retrieval and generation."
                ]
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["documents_processed"] == 2
        assert "message" in data
    
    def test_ingest_invalid_request(self, client):
        """Test ingesting with invalid request"""
        response = client.post(
            "/api/v1/documents/ingest",
            json={}  # No URLs or texts
        )
        # Should handle gracefully, even if no documents provided
        assert response.status_code in [200, 400]
    
    def test_clear_documents(self, client):
        """Test clearing documents"""
        response = client.delete("/api/v1/documents/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "message" in data

@pytest.mark.integration
class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Adaptive RAG API"
    
    def test_docs_redirect(self, client):
        """Test docs redirect"""
        response = client.get("/docs", follow_redirects=False)
        assert response.status_code in [200, 307]  # 307 is temporary redirect