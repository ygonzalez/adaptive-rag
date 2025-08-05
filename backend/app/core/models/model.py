import logging
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)
load_dotenv()

@dataclass
class ModelConfig:
    chat_model: str = "gemini-2.0-flash"
    embedding_model: str = "models/text-embedding-004"
    temperature: float = 0.0

class ModelManager:
    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()
        self._chat_model = None
        self._embedding_model = None

    @property
    def chat_model(self):
        if self._chat_model is None:
            self._chat_model = ChatGoogleGenerativeAI(
                model=self.config.chat_model,
                temperature=self.config.temperature
            )
        return self._chat_model

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = GoogleGenerativeAIEmbeddings(
                model=self.config.embedding_model
            )
        return self._embedding_model

model_manager = ModelManager()

def get_chat_model() -> ChatGoogleGenerativeAI:
    """Get the default chat model."""
    return model_manager.chat_model

def get_embedding_model() -> GoogleGenerativeAIEmbeddings:
    """Get the default embedding model."""
    return model_manager.embedding_model