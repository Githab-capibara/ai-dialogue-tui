"""Модуль для работы с моделями и диалогами.

Этот модуль экспортирует абстракции и реализации для работы с LLM-провайдерами.
"""

from models.config import Config
from models.conversation import MAX_CONTEXT_LENGTH, Conversation
from models.ollama_client import OllamaClient
from models.provider import (
    MessageDict,
    ModelId,
    ModelProvider,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)

__all__ = [
    "MAX_CONTEXT_LENGTH",
    # Конфигурация
    "Config",
    # Домен
    "Conversation",
    "MessageDict",
    "ModelId",
    # Абстракции
    "ModelProvider",
    # Реализации
    "OllamaClient",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    # Исключения провайдера
    "ProviderError",
    "ProviderGenerationError",
]
