"""Module for working with models and conversations.

This module exports abstractions and implementations for working with LLM providers.
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
    # Configuration
    "Config",
    # Domain
    "Conversation",
    "MessageDict",
    "ModelId",
    # Abstractions
    "ModelProvider",
    # Implementations
    "OllamaClient",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    # Provider exceptions
    "ProviderError",
    "ProviderGenerationError",
]
