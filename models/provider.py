"""Abstractions for language model providers.

This module defines protocols and types for dependency injection.
Allows replacing provider implementation without changing domain logic.
"""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict, runtime_checkable


class ProviderError(Exception):
    """Base exception for model provider errors.

    Used as a base class for provider-specific exceptions.
    Contains original exception information for debugging.
    """

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message.
            original_exception: Original exception for chaining.

        """
        super().__init__(message)
        self._original_exception = original_exception

    @property
    def original_exception(self) -> Exception | None:
        """Get the original exception."""
        return self._original_exception


class ProviderConfigurationError(ProviderError):
    """Exception for provider configuration errors.

    Raised for incorrect provider configuration:
    - Invalid host URL
    - Incorrect authentication parameters
    - Missing required settings
    """


class ProviderConnectionError(ProviderError):
    """Exception for provider connection errors.

    Raised for network connection problems:
    - Host unavailable
    - Connection timeouts
    - Network errors
    """


class ProviderGenerationError(ProviderError):
    """Exception for response generation errors.

    Raised for response generation problems:
    - Provider API errors
    - Invalid response format
    - Response validation errors
    """


class MessageDict(TypedDict, total=True):
    """Message structure in Ollama-compatible format.

    Attributes:
        role: Sender role (system, user, assistant).
        content: Message text.

    """

    role: Literal["system", "user", "assistant"]
    content: str


ModelId = Literal["A", "B"]


@runtime_checkable
class ModelProvider(Protocol):
    """Protocol for language model providers.

    Defines the interface for interacting with various LLM providers.
    Allows using dependency injection for testability and replaceability.
    """

    async def list_models(self) -> list[str]:
        """Get list of available models."""
        ...

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: float,
    ) -> str:
        """Generate response from model."""
        ...

    async def close(self) -> None:
        """Release provider resources."""
        ...


__all__ = [
    "MessageDict",
    "ModelId",
    "ModelProvider",
    "ProviderConfigurationError",
    "ProviderConnectionError",
    "ProviderError",
    "ProviderGenerationError",
]
