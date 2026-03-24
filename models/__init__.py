"""Модуль для работы с моделями и диалогами."""

from models.ollama_client import OllamaClient
from models.conversation import Conversation

__all__ = ["OllamaClient", "Conversation"]
