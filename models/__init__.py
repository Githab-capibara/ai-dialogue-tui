"""Модуль для работы с моделями и диалогами.

Этот модуль экспортирует абстракции и реализации для работы с LLM-провайдерами.
"""

from models.conversation import Conversation
from models.ollama_client import OllamaClient, OllamaError
from models.provider import MessageDict, ModelId, ModelProvider

__all__ = [
    # Абстракции
    "ModelProvider",
    "MessageDict",
    "ModelId",
    # Реализации
    "OllamaClient",
    "OllamaError",
    # Домен
    "Conversation",
]
