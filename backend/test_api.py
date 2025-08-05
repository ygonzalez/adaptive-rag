#!/usr/bin/env python3
"""
Simple API testing script for the Adaptive RAG backend
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_readiness():
    """Test readiness check endpoint"""
    print("\n🚀 Testing Readiness Check...")
    response = requests.get(f"{BASE_URL}/api/v1/health/ready")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_chat(question="What is agent memory?"):
    """Test chat endpoint"""
    print(f"\n💬 Testing Chat with question: '{question}'")
    payload = {
        "question": question,
        "session_id": f"test-session-{datetime.now().timestamp()}"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Answer: {data['answer'][:200]}...")
        print(f"Used web search: {data['used_web_search']}")
        print(f"Number of sources: {len(data['sources'])}")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200

def test_document_ingestion():
    """Test document ingestion endpoint"""
    print("\n📄 Testing Document Ingestion...")
    payload = {
        "urls": ["https://lilianweng.github.io/posts/2023-06-23-agent/"],
        "texts": ["This is a test document about RAG systems and vector databases."]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/documents/ingest",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_clear_documents():
    """Test document clearing endpoint"""
    print("\n🗑️  Testing Clear Documents...")
    response = requests.delete(f"{BASE_URL}/api/v1/documents/clear")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def main():
    """Run all tests"""
    print("🧪 Starting API Tests...")
    print(f"Base URL: {BASE_URL}")
    print("-" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Readiness Check", test_readiness),
        ("Chat API", test_chat),
        # Uncomment these to test document operations
        # ("Document Ingestion", test_document_ingestion),
        # ("Clear Documents", test_clear_documents),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    main()