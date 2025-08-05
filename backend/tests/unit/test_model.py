from unittest.mock import patch, Mock

from app.core.models.model import ModelManager, ModelConfig


class TestModelManager:
    """Test the ModelManager class."""

    def test_default_initialization(self):
        """Test ModelManager with default configuration."""
        manager = ModelManager()

        assert manager.config.chat_model == "gemini-2.0-flash"
        assert manager.config.embedding_model == "models/text-embedding-004"
        assert manager.config.temperature == 0.0

    def test_custom_configuration(self):
        """Test ModelManager with custom configuration."""
        config = ModelConfig(
            chat_model="gemini-1.5-flash",
            temperature=0.7
        )
        manager = ModelManager(config)

        assert manager.config.chat_model == "gemini-1.5-flash"
        assert manager.config.temperature == 0.7

    @patch('app.core.models.model.ChatGoogleGenerativeAI')
    def test_lazy_loading_chat_model(self, mock_chat_class):
        """Test that chat model is only created when accessed."""
        mock_instance = Mock()
        mock_chat_class.return_value = mock_instance

        manager = ModelManager()

        # Model not created yet
        mock_chat_class.assert_not_called()

        # Access model - should create it
        model = manager.chat_model

        mock_chat_class.assert_called_once()
        assert model == mock_instance

        # Second access should reuse cached model
        model2 = manager.chat_model
        assert model2 == mock_instance
        mock_chat_class.assert_called_once()  # Still only called once
