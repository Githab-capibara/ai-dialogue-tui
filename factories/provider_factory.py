"""Factory for creating model providers.

This module contains factory functions for dependency injection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from models.ollama_client import OllamaClient

if TYPE_CHECKING:
    from collections.abc import Callable

    from models.config import Config
    from models.provider import ModelProvider

__all__ = ["create_ollama_provider", "create_provider_factory"]


def create_ollama_provider(config: Config) -> ModelProvider:
    """Create Ollama provider.

    Args:
        config: Configuration for connection.

    Returns:
        Configured ModelProvider.

    """
    return OllamaClient(host=config.ollama_host)


def create_provider_factory(config: Config) -> Callable[[], ModelProvider]:
    """Create providers factory.

    Args:
        config: Configuration for creating providers.

    Returns:
        Factory function for creating ModelProvider.

    """

    def factory() -> ModelProvider:
        return create_ollama_provider(config)

    return factory
