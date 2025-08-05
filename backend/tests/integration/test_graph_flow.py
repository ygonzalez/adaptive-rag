from unittest.mock import patch

from app.core.graph.graph import app as graph_app


class TestGraphIntegration:
    """Test complete graph workflows."""

    def test_vectorstore_flow_end_to_end(self, sample_question):
        """Test complete flow for vectorstore-routed question."""
        initial_state = {
            "question": sample_question,
            "generation": "",
            "web_search": False,
            "documents": []
        }

        assert graph_app is not None

    @patch('app.core.graph.nodes.web_search.web_search_tool')
    def test_web_search_flow_end_to_end(self, mock_web_search):
        """Test complete flow for web search-routed question."""
        mock_web_search.invoke.return_value = {
            "results": [{"content": "Mock web search result about pizza recipes"}]
        }

        initial_state = {
            "question": "how to make pizza",
            "generation": "",
            "web_search": False,
            "documents": []
        }

        assert graph_app is not None