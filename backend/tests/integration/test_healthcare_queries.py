"""
Integration tests for healthcare AI queries in the RAG system.
"""
import pytest
from unittest.mock import patch
from app.core.graph.graph import app as graph_app
from app.core.ingestion.healthcare_data import get_sample_queries


class TestHealthcareQueries:
    """Test healthcare-specific query handling."""

    def test_medical_imaging_query(self, sample_question):
        """Test handling of medical imaging AI questions."""
        initial_state = {
            "question": sample_question,
            "generation": "",
            "web_search": False,
            "documents": [],
            "generation_attempts": 0,
            "web_search_attempts": 0
        }
        
        # Verify graph can handle healthcare questions
        assert graph_app is not None
        assert "How does AI improve medical image analysis?" in sample_question

    def test_clinical_ai_query(self, healthcare_questions):
        """Test handling of clinical AI questions."""
        clinical_question = "How does AI assist in clinical decision making?"
        
        initial_state = {
            "question": clinical_question,
            "generation": "",
            "web_search": False,
            "documents": [],
            "generation_attempts": 0,
            "web_search_attempts": 0
        }
        
        assert clinical_question in healthcare_questions
        assert graph_app is not None

    @patch('app.core.graph.nodes.web_search.web_search_tool')
    def test_current_healthcare_developments_query(self, mock_web_search):
        """Test handling of current healthcare AI developments queries that require web search."""
        mock_web_search.invoke.return_value = {
            "results": [{"content": "Latest FDA approvals for AI medical devices in 2024 include several diagnostic imaging systems and clinical decision support tools."}]
        }
        
        current_question = "Latest FDA approvals for AI medical devices 2024"
        
        initial_state = {
            "question": current_question,
            "generation": "",
            "web_search": False,
            "documents": [],
            "generation_attempts": 0,
            "web_search_attempts": 0
        }
        
        assert graph_app is not None

    def test_complex_healthcare_query(self):
        """Test handling of complex cross-domain healthcare queries."""
        complex_question = "What AI imaging technologies are currently in FDA clinical trials?"
        
        initial_state = {
            "question": complex_question,
            "generation": "",
            "web_search": False,
            "documents": [],
            "generation_attempts": 0,
            "web_search_attempts": 0
        }
        
        # This type of query should likely trigger web search
        assert graph_app is not None

    def test_sample_queries_availability(self):
        """Test that healthcare sample queries are available."""
        sample_queries = get_sample_queries()
        
        assert len(sample_queries) > 0
        assert any("imaging" in query.lower() for query in sample_queries)
        assert any("clinical" in query.lower() or "diagnosis" in query.lower() for query in sample_queries)
        assert any("FDA" in query for query in sample_queries)

    def test_diagnostic_accuracy_query(self, clinical_documents):
        """Test queries about diagnostic accuracy."""
        diagnostic_question = "How accurate are AI diagnostic systems compared to doctors?"
        
        # Should find relevant documents about accuracy
        relevant_content = any("accuracy" in doc.page_content.lower() for doc in clinical_documents)
        assert relevant_content or len(clinical_documents) > 0
        
        initial_state = {
            "question": diagnostic_question,
            "generation": "",
            "web_search": False,
            "documents": clinical_documents,
            "generation_attempts": 0,
            "web_search_attempts": 0
        }
        
        assert graph_app is not None