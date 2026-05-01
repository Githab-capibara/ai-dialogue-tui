"""Async client for interacting with Ollama API.

This module implements the ModelProvider protocol for working with Ollama API.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any, Final, Self
from urllib.parse import urljoin

import aiohttp

from models.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    Config,
    validate_ollama_url,
)
from models.provider import (
    MessageDict,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)

_logger = logging.getLogger(__name__)

# Cached default options for performance
_DEFAULT_OPTIONS: Final = {
    "temperature": DEFAULT_TEMPERATURE,
    "num_predict": DEFAULT_MAX_TOKENS,
}

# TTL for models cache (5 minutes)
_MODELS_CACHE_TTL: Final = 300


class _RequestValidator:
    """Request validation for Ollama API.

    Encapsulates input parameter validation logic for API requests.
    """

    @staticmethod
    def validate_host(host: str) -> None:
        """Validate host URL.

        Args:
            host: Host URL to validate.

        Raises:
            ValueError: If URL is invalid.

        """
        if not validate_ollama_url(host):
            msg = f"Invalid host URL: {host}"
            raise ValueError(msg)

    @staticmethod
    def validate_messages(messages: Sequence[Mapping[str, Any]]) -> None:
        """Validate messages for generate method.

        Args:
            messages: Messages parameter to validate.

        Raises:
            ValueError: If messages is invalid.

        """
        if not isinstance(messages, list):
            msg = "messages must be a list"
            raise TypeError(msg)

        for idx, msg in enumerate(messages):
            if not isinstance(msg, Mapping):
                err_msg = f"Message at index {idx} must be a mapping"
                raise TypeError(err_msg)
            if "role" not in msg or "content" not in msg:
                err_msg = f"Message at index {idx} must contain 'role' and 'content'"
                raise TypeError(err_msg)


# HTTP status code for successful response
HTTP_OK: int = 200


class _ResponseHandler:
    """Response handling from Ollama API.

    Encapsulates response processing and validation logic.
    Uses module-level HTTP_OK constant.
    """

    @staticmethod
    def validate_status_code(
        status: int,
        operation: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Validate HTTP status code of response.

        Args:
            status: HTTP status code.
            operation: Operation name for error message.
            data: Parsed response data for error extraction.

        Raises:
            ProviderGenerationError: If status code is not 200.

        """
        if status != HTTP_OK:
            msg = f"Error {operation}: HTTP {status}"
            if data is not None and isinstance(data, dict) and "error" in data:
                error_msg = data.get("error")
                if isinstance(error_msg, str):
                    msg = f"{operation}: {error_msg}"
            raise ProviderGenerationError(msg)

    @staticmethod
    def parse_json_response(
        data: Mapping[str, Any],
        operation: str,
    ) -> dict[str, Any]:
        """Validate and parse JSON response.

        Args:
            data: Data to validate.
            operation: Operation name for error message.

        Returns:
            Parsed data.

        Raises:
            ProviderGenerationError: If format is invalid.

        """
        if not isinstance(data, dict):
            msg = f"Invalid API response format ({operation})"
            raise ProviderGenerationError(msg)
        return data

    @staticmethod
    def extract_models_list(data: dict[str, Any]) -> list[str]:
        """Extract models list from API response.

        Args:
            data: API response data.

        Returns:
            List of model names.

        """
        models = data.get("models", [])
        if not isinstance(models, list):
            return []

        result: list[str] = []
        for model in models:
            if isinstance(model, dict):
                name = model.get("name")
                if isinstance(name, str) and name:
                    result.append(name)
        return result

    @staticmethod
    def extract_generation_response(data: dict[str, Any]) -> str:
        """Extract response text from generation API response.

        Args:
            data: API response data.

        Returns:
            Response text with thinking (if present) or empty string.

        """
        message = data.get("message", {})
        if not isinstance(message, dict):
            return ""
        content = message.get("content", "")
        thinking = message.get("thinking", "")
        if isinstance(content, str):
            if isinstance(thinking, str) and thinking:
                return f"[Thinking...]\n{thinking}\n[/]\n\n{content}"
            return content
        return ""


class _HTTPSessionManager:
    """HTTP session management for Ollama API.

    Encapsulates HTTP session creation, retrieval, and closing logic.
    Extracted for improved cohesion and testability.

    Note:
        Implements connection pooling via aiohttp.ClientSession:
        - One session is used for all requests to Ollama
        - Connections are automatically reused (HTTP keep-alive)
        - Session is created lazily on first request
        - Automatic recreation on close
        - Timeout configured via configuration

    Scalability:
        Current implementation uses one session per OllamaClient instance.
        For high-load scenarios, consider:
        - Session pool with max connection limit
        - Load balancing across multiple Ollama instances
        - Model response caching

    """

    def __init__(
        self,
        timeout: int = 60,
        conn_timeout: int = 10,
        sock_read_timeout: int = 60,
    ) -> None:
        """Initialize session manager.

        Args:
            timeout: Total request timeout in seconds.
            conn_timeout: Connection timeout in seconds.
            sock_read_timeout: Socket read timeout in seconds.

        """
        self._timeout = timeout
        self._conn_timeout = conn_timeout
        self._sock_read_timeout = sock_read_timeout
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session.

        Returns:
            HTTP session for requests.

        """
        if self._session is not None and not self._session.closed:
            return self._session
        async with self._lock:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(
                        total=self._timeout,
                        connect=self._conn_timeout,
                        sock_read=self._sock_read_timeout,
                    ),
                )
            return self._session

    async def close(self) -> None:
        """Close HTTP session and reset reference."""
        if self._session is not None:
            if not self._session.closed:
                try:
                    await self._session.close()
                except (aiohttp.ClientError, asyncio.CancelledError, RuntimeError):
                    pass  # Игнорируем ошибки при закрытии
            self._session = None

    async def close_session_only(self) -> None:
        """Close current session without resetting reference."""
        if self._session is not None:
            if not self._session.closed:
                with contextlib.suppress(aiohttp.ClientError, asyncio.CancelledError, RuntimeError):
                    await self._session.close()
            self._session = None


class _ModelsCache:
    """Model list caching.

    Implements a simple TTL cache for list_models result.
    """

    def __init__(self, ttl: int = _MODELS_CACHE_TTL) -> None:
        """Initialize cache.

        Args:
            ttl: Cache time-to-live in seconds.

        """
        self._ttl = ttl
        self._models: list[str] | None = None
        self._cache_timestamp: float | None = None

    def _is_cache_valid(self) -> bool:
        """Check cache validity.

        Returns:
            True if cache is valid.

        """
        if self._ttl <= 0:
            return False

        if self._models is None or self._cache_timestamp is None:
            return False

        current_time = time.time()
        return (current_time - self._cache_timestamp) < self._ttl

    def get(self) -> list[str] | None:
        """Get cached models if cache is valid.

        Returns:
            List of models or None if cache is invalid.

        """
        if self._is_cache_valid():
            return self._models
        return None

    def set(self, models: list[str]) -> None:
        """Store models in cache.

        Args:
            models: List of models to cache.

        """
        self._models = models
        self._cache_timestamp = time.time()

    def invalidate(self) -> None:
        """Clear cache."""
        self._models = None
        self._cache_timestamp = None


class OllamaClient:
    """Async client for working with local Ollama API.

    Implements the ModelProvider protocol for dependency injection.
    """

    def __init__(
        self,
        host: str | None = None,
        config: Config | None = None,
    ) -> None:
        """Initialize client.

        Args:
            host: Ollama host URL (default from config).
            config: Configuration for dependency injection.

        Raises:
            ValueError: If host is invalid.

        """
        self._config = config or Config()
        resolved_host = host if host is not None else self._config.ollama_host
        _RequestValidator.validate_host(resolved_host)
        self.host = resolved_host

        self._http_manager = _HTTPSessionManager(
            timeout=min(self._config.request_timeout, 30),
            conn_timeout=10,
            sock_read_timeout=self._config.sock_read_timeout,
        )

        self._models_cache = _ModelsCache(ttl=_MODELS_CACHE_TTL)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get HTTP session via manager."""
        return await self._http_manager.get_session()

    async def close(self) -> None:
        """Close HTTP session and clear cache."""
        await self._http_manager.close()
        self._models_cache.invalidate()

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: BaseException | None,
    ) -> None:
        """Async context manager exit - ensures proper cleanup."""
        del exc_type, exc_val, exc_tb  # Unused but required by protocol
        await self.close()

    async def list_models(self) -> list[str]:
        """Get list of available local models.

        Uses caching to improve performance.
        Cache is valid for _MODELS_CACHE_TTL seconds.

        Returns:
            List of model names.

        Raises:
            ProviderConnectionError: If unable to connect to Ollama.
            ProviderGenerationError: If unable to get data.

        """
        cached_models = self._models_cache.get()
        if cached_models is not None:
            return cached_models

        session = await self._get_session()
        url = urljoin(self.host, "/api/tags")

        max_retries = 3
        base_delay = 1.0  # Начальная задержка в секундах

        for attempt in range(max_retries):
            try:
                async with session.get(url) as response:
                    data = await self._parse_json_response(response)
                    _ResponseHandler.validate_status_code(response.status, "list_models", data)
                    _ResponseHandler.parse_json_response(data, "list_models")
                    models = _ResponseHandler.extract_models_list(data)
                    self._models_cache.set(models)
                    return models

            except (aiohttp.ClientError, TimeoutError) as err:
                error_msg = str(err) if str(err).strip() else repr(err) if err.args else type(err).__name__
                if attempt < max_retries - 1:
                    # Экспоненциальная задержка: 1, 2, 4 секунды
                    delay = base_delay * (2**attempt)
                    _logger.warning(
                        "Request failed (attempt %d/%d): %s, retrying in %.1fs...",
                        attempt + 1,
                        max_retries,
                        error_msg,
                        delay,
                    )
                    # Закрываем текущую сессию без инвалидации кэша
                    await self._http_manager.close_session_only()
                    session = await self._get_session()
                    await asyncio.sleep(delay)
                    continue
                timeout_val = self._config.sock_read_timeout
                msg = (
                    f"Could not connect to Ollama ({self.host}): "
                    f"{error_msg}. Timeout: {timeout_val}s. "
                    f"Check that Ollama is running."
                )
                raise ProviderConnectionError(msg, err) from err
            except ProviderError:
                _logger.debug("ProviderError when getting models list", exc_info=True)
                raise
            except (json.JSONDecodeError, KeyError, TypeError) as err:
                msg = f"API response validation error: {err}"
                raise ProviderGenerationError(msg) from err

        return []

    async def _parse_json_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        """Parse JSON response with error handling."""
        try:
            json_data: dict[str, Any] = await response.json()
        except json.JSONDecodeError as e:
            msg = "Invalid JSON in API response"
            raise ProviderGenerationError(msg) from e
        else:
            return json_data

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: float,
    ) -> str:
        """Generate response from model.

        Preconditions:
            - model must be a non-empty string
            - messages must be a non-empty list of valid MessageDict

        Args:
            model: Model name (must be non-empty string).
            messages: List of messages in Ollama format.
            **kwargs: Additional generation parameters.

        Returns:
            Generated text (may be empty string on error).

        Raises:
            ProviderError: If generation failed.
            ValueError: If messages is invalid.

        """
        _RequestValidator.validate_messages(messages)
        session = await self._get_session()
        url = urljoin(self.host, "/api/chat")
        payload = self._build_request_payload(model, messages, kwargs)

        max_retries = 3
        base_delay = 2.0  # Начальная задержка в секундах

        for attempt in range(max_retries):
            try:
                async with session.post(url, json=payload) as response:
                    data = await self._parse_json_response(response)
                    _ResponseHandler.validate_status_code(response.status, "generate", data)
                    _ResponseHandler.parse_json_response(data, "generate")
                    return _ResponseHandler.extract_generation_response(data)

            except (aiohttp.ClientError, TimeoutError) as err:
                error_msg = str(err) if str(err).strip() else repr(err) if err.args else type(err).__name__
                if attempt < max_retries - 1:
                    # Экспоненциальная задержка: 2, 4, 8 секунд
                    delay = base_delay * (2**attempt)
                    _logger.warning(
                        "Request failed (attempt %d/%d): %s, retrying in %.1fs...",
                        attempt + 1,
                        max_retries,
                        error_msg,
                        delay,
                    )
                    # Закрываем текущую сессию и создаём новую
                    await self._http_manager.close_session_only()
                    session = await self._get_session()
                    await asyncio.sleep(delay)
                    continue
                # Последняя попытка не удалась
                timeout_val = self._config.sock_read_timeout
                msg = (
                    f"Ollama request failed after {max_retries} attempts. {error_msg}. "
                    f"Timeout: {timeout_val}s. Check that Ollama is running and model is loaded."
                )
                raise ProviderConnectionError(msg, err) from err
            except ProviderError:
                _logger.debug("ProviderError during response generation")
                raise
            except (json.JSONDecodeError, KeyError, TypeError) as err:
                msg = f"API response validation error: {err}"
                raise ProviderGenerationError(msg) from err
            except OSError as err:
                msg = f"IO error communicating with Ollama ({self.host}): {err}"
                _logger.warning("OSError during generation: %s", err)
                raise ProviderGenerationError(msg) from err

        return ""

    def _build_request_payload(
        self,
        model: str,
        messages: list[MessageDict],
        kwargs: dict[str, float | int],
    ) -> dict[str, Any]:
        """Build request payload for generate method.

        Не ограничиваем количество токенов - модель сама решает сколько думать.
        """
        options: dict[str, Any] = {
            "temperature": kwargs.get("temperature", self._config.temperature),
        }
        # НЕ ограничиваем max_tokens - пусть модель думает сколько хочет

        return {
            "model": model,
            "messages": messages,
            "options": options,
            "stream": False,
        }


__all__ = ["OllamaClient"]
