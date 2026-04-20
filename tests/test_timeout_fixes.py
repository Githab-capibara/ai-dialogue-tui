"""Tests for verifying timeout issue fixes.

This module contains tests for verifying:
1. sock_read_timeout parameter validation in Config
2. Proper passing of sock_read_timeout to _HTTPSessionManager
3. Correct timeout error message

Note:
    Tests use access to internal attributes for testing purposes.

"""

# pylint: disable=protected-access,import-outside-toplevel

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ServerTimeoutError

from models.config import Config
from models.ollama_client import OllamaClient, _HTTPSessionManager
from models.provider import ProviderConnectionError


def create_async_mock_response(
    status: int = 200,
    json_data: Any = None,
) -> AsyncMock:
    """Create mock for HTTP response."""
    mock_response = AsyncMock()
    mock_response.status = status

    async def return_json() -> Any:
        return json_data

    mock_response.json = return_json
    return mock_response


def create_session_mock(
    response: AsyncMock | None = None,
    raise_on_enter: Exception | None = None,
) -> AsyncMock:
    """Create mock for HTTP session."""
    mock_context_manager = AsyncContextManagerMock(response=response, raise_on_enter=raise_on_enter)
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_context_manager)
    mock_session.post = MagicMock(return_value=mock_context_manager)
    mock_session.closed = False
    return mock_session


def create_mock_get_session(mock_session: AsyncMock):
    """Create function for mocking _get_session method."""

    async def mock_get_session(_self: OllamaClient) -> Any:
        return mock_session

    return mock_get_session


class AsyncContextManagerMock:
    """Mock for async context manager."""

    def __init__(self, response: Any = None, raise_on_enter: Exception | None = None) -> None:
        self._response = response
        self._raise_on_enter = raise_on_enter

    async def __aenter__(self) -> Any:
        if self._raise_on_enter:
            raise self._raise_on_enter
        return self._response

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class TestSockReadTimeoutValidation:
    """Tests for sock_read_timeout validation in Config."""

    def test_default_sock_read_timeout(self) -> None:
        """Test that default sock_read_timeout is set correctly."""
        config = Config()
        assert config.sock_read_timeout == 300

    def test_custom_sock_read_timeout(self) -> None:
        """Test that custom sock_read_timeout value is accepted."""
        config = Config(sock_read_timeout=600)
        assert config.sock_read_timeout == 600

    def test_sock_read_timeout_validation_min(self) -> None:
        """Test minimum sock_read_timeout value."""
        config = Config(sock_read_timeout=1)
        assert config.sock_read_timeout == 1

    def test_sock_read_timeout_validation_out_of_range(self) -> None:
        """Test that sock_read_timeout out of range raises error."""
        with pytest.raises(ValueError, match="sock_read_timeout"):
            Config(sock_read_timeout=0)

    def test_sock_read_timeout_validation_negative(self) -> None:
        """Test that negative sock_read_timeout raises error."""
        with pytest.raises(ValueError, match="sock_read_timeout"):
            Config(sock_read_timeout=-1)


class TestHTTPSessionManagerTimeout:
    """Tests for verifying timeout passing to _HTTPSessionManager."""

    def test_session_manager_uses_custom_sock_read_timeout(self) -> None:
        """Test that _HTTPSessionManager uses passed sock_read_timeout."""
        manager = _HTTPSessionManager(
            timeout=60,
            conn_timeout=10,
            sock_read_timeout=300,
        )
        assert manager._sock_read_timeout == 300

    def test_session_manager_default_sock_read_timeout(self) -> None:
        """Test that _HTTPSessionManager has default sock_read_timeout."""
        manager = _HTTPSessionManager(timeout=60)
        assert manager._sock_read_timeout == 60

    def test_ollama_client_passes_sock_read_timeout(self) -> None:
        """Test that OllamaClient passes sock_read_timeout to _HTTPSessionManager."""
        config = Config(sock_read_timeout=300)
        client = OllamaClient(config=config)
        assert client._http_manager._sock_read_timeout == 300

    def test_ollama_client_default_sock_read_timeout(self) -> None:
        """Test that OllamaClient uses default value from Config."""
        config = Config()
        client = OllamaClient(config=config)
        assert client._http_manager._sock_read_timeout == 300


class TestTimeoutErrorHandling:
    """Tests for verifying timeout error handling."""

    @pytest.mark.asyncio
    async def test_generate_timeout_error_message(self) -> None:
        """Test that informative message is shown on timeout error."""
        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ServerTimeoutError("Timeout on reading data from socket")
        )
        mock_session = create_session_mock(response=None)
        mock_session.post = MagicMock(return_value=mock_context_manager)

        with patch.object(OllamaClient, "_get_session", create_mock_get_session(mock_session)):
            client = OllamaClient(
                host="http://localhost:11434",
                config=Config(sock_read_timeout=300),
            )
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.generate("llama3", [{"role": "user", "content": "test"}])

            error_message = str(exc_info.value)
            assert "Timeout" in error_message
            assert "300s" in error_message

    @pytest.mark.asyncio
    async def test_generate_timeout_error_suggests_increase(self) -> None:
        """Test that increasing timeout is suggested on timeout error."""
        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ServerTimeoutError("Timeout on reading data from socket")
        )
        mock_session = create_session_mock(response=None)
        mock_session.post = MagicMock(return_value=mock_context_manager)

        with patch.object(OllamaClient, "_get_session", create_mock_get_session(mock_session)):
            client = OllamaClient(
                host="http://localhost:11434",
                config=Config(sock_read_timeout=120),
            )
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.generate("llama3", [{"role": "user", "content": "test"}])

            error_message = str(exc_info.value)
            assert "increase" in error_message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
