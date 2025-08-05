import pytest
from unittest.mock import Mock, patch
from typing import List
from langchain.schema import Document

@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "agent memory"

@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        Document(
            page_content="Agent memory consists of short-term and long-term components for information storage.",
            metadata={"source": "test_doc_1"}
        ),
        Document(
            page_content="Memory systems in AI agents use vector databases for efficient retrieval of past experiences.",
            metadata={"source": "test_doc_2"}
        ),
        Document(
            page_content="Long-term memory allows agents to maintain context across multiple interactions.",
            metadata={"source": "test_doc_3"}
        )
    ]

@pytest.fixture
def irrelevant_documents():
    """Documents that should be graded as irrelevant."""
    return [
        Document(
            page_content="Pizza recipes require flour, water, yeast, and tomato sauce for the best results.",
            metadata={"source": "pizza_doc"}
        )
    ]

@pytest.fixture
def mock_retriever(sample_documents):
    """Mock retriever that returns sample documents."""
    mock = Mock()
    mock.invoke.return_value = sample_documents
    return mock

@pytest.fixture
def mock_empty_retriever():
    """Mock retriever that returns no documents."""
    mock = Mock()
    mock.invoke.return_value = []
    return mock

@pytest.fixture(scope="session", autouse=True)
def load_environment():
    """Load environment variables for all tests."""
    from dotenv import load_dotenv
    load_dotenv()