"""
Shared pytest fixtures for test suite.

This module provides common fixtures and helper utilities used across
multiple test files to reduce duplication.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.config import Config
from models.conversation import Conversation
from models.ollama_client import OllamaClient
from models.provider import ModelProvider


class AsyncContextManagerMock:
    """Mock for async context manager (aiohttp session)."""

    def __init__(
        self,
        response: Any = None,
        raise_on_enter: Exception | None = None,
    ) -> None:
        self._response = response
        self._raise_on_enter = raise_on_enter

    async def __aenter__(self) -> AsyncMock | None:
        """Enter the async context manager."""
        if self._raise_on_enter:
            raise self._raise_on_enter
        return self._response

    async def __aexit__(self, _exc_type: type, _exc_val: BaseException, _exc_tb: object) -> None:
        """Exit the async context manager."""
        pass


@pytest.fixture
def mock_async_response() -> Callable[[int, Any, Exception | None], AsyncMock]:
    """Create async HTTP response mocks."""

    def _create(
        status: int = 200,
        json_data: Any = None,
        raise_on_json: Exception | None = None,
    ) -> AsyncMock:
        mock_response = AsyncMock()
        mock_response.status = status

        if raise_on_json:

            async def raise_error() -> None:
                raise raise_on_json

            mock_response.json = raise_error
        else:

            async def return_json() -> Any:
                return json_data

            mock_response.json = return_json

        return mock_response

    return _create


@pytest.fixture
def mock_session() -> Callable[[AsyncMock | None, Exception | None], AsyncMock]:
    """Create async HTTP session mocks."""

    def _create(
        response: AsyncMock | None = None,
        raise_on_enter: Exception | None = None,
    ) -> AsyncMock:
        mock_context_manager = AsyncContextManagerMock(
            response=response,
            raise_on_enter=raise_on_enter,
        )
        mock_sess = AsyncMock()
        mock_sess.get = MagicMock(return_value=mock_context_manager)
        mock_sess.post = MagicMock(return_value=mock_context_manager)
        mock_sess.closed = False
        return mock_sess

    return _create


@pytest.fixture
def mock_get_session() -> Callable[[AsyncMock], Callable[[OllamaClient], Awaitable[Any]]]:
    """Create mock for _get_session method on OllamaClient."""

    def _create(mock_session: AsyncMock) -> Callable[[OllamaClient], Awaitable[Any]]:
        async def mock_get_session_method(_self: OllamaClient) -> Any:
            return mock_session

        return mock_get_session_method

    return _create


@pytest.fixture
def sample_config() -> Config:
    """Fixture providing a standard test configuration."""
    return Config(
        ollama_host="http://localhost:11434",
    )


@pytest.fixture
def sample_provider() -> ModelProvider:
    """Fixture providing a mock ModelProvider implementation."""
    mock_provider = AsyncMock(spec=ModelProvider)
    mock_provider.list_models = AsyncMock(return_value=["llama3", "mistral"])
    mock_provider.generate = AsyncMock(return_value={"response": "test response", "done": True})
    mock_provider.close = AsyncMock()
    return mock_provider


@pytest.fixture
def sample_conversation() -> Conversation:
    """Fixture providing a Conversation instance."""
    return Conversation(
        model_a="llama3",
        model_b="mistral",
        topic="test",
    )
