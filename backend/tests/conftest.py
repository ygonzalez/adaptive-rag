import pytest
from unittest.mock import Mock, patch
from typing import List
from langchain.schema import Document

@pytest.fixture
def sample_question():
    """Sample healthcare AI question for testing."""
    return "How does AI improve medical image analysis?"

@pytest.fixture
def sample_documents():
    """Sample healthcare AI documents for testing."""
    return [
        Document(
            page_content="Deep learning algorithms have revolutionized medical image analysis by automatically detecting patterns in radiological images that may be missed by human observers. These systems use convolutional neural networks to analyze X-rays, CT scans, and MRI images for early disease detection.",
            metadata={"source": "medical_imaging_ai"}
        ),
        Document(
            page_content="AI-powered diagnostic imaging systems have shown remarkable accuracy in detecting cancer, with some studies demonstrating performance comparable to or exceeding that of expert radiologists. These systems can identify subtle abnormalities in mammograms, chest X-rays, and dermatological images.",
            metadata={"source": "ai_diagnostic_accuracy"}
        ),
        Document(
            page_content="Machine learning models in healthcare require extensive validation to ensure safety and efficacy. Regulatory bodies like the FDA have established guidelines for AI medical device approval, emphasizing the need for diverse training datasets and robust testing protocols.",
            metadata={"source": "ai_healthcare_validation"}
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

@pytest.fixture
def healthcare_questions():
    """Sample healthcare AI questions for testing."""
    return [
        "How does AI assist in clinical decision making?",
        "What are the challenges of AI in radiology?",
        "How accurate is AI for detecting skin cancer?",
        "What validation methods are used for diagnostic AI?",
        "How does AI predict patient deterioration in hospitals?"
    ]

@pytest.fixture
def clinical_documents():
    """Sample clinical AI documents for testing."""
    return [
        Document(
            page_content="Clinical decision support systems powered by AI can analyze patient data, medical history, and current symptoms to provide evidence-based treatment recommendations. These systems help reduce diagnostic errors and improve patient outcomes by alerting clinicians to potential drug interactions, allergies, and contraindications.",
            metadata={"source": "clinical_decision_ai"}
        ),
        Document(
            page_content="AI systems in intensive care units continuously monitor patient vital signs and can predict deterioration hours before traditional methods. These early warning systems analyze patterns in heart rate, blood pressure, respiratory rate, and other biomarkers to identify patients at risk of sepsis or cardiac arrest.",
            metadata={"source": "icu_monitoring_ai"}
        )
    ]

@pytest.fixture(scope="session", autouse=True)
def load_environment():
    """Load environment variables for all tests."""
    from dotenv import load_dotenv
    load_dotenv()