"""AI Dialogue TUI application configuration.

This module contains default constants and a configuration class
with full parameter validation.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Final, TypeVar
from urllib.parse import urlparse

log = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_PAUSE_BETWEEN_MESSAGES",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_SOCK_READ_TIMEOUT",
    "DEFAULT_TEMPERATURE",
    "MAX_TEMPERATURE",
    "MIN_MAX_TOKENS",
    "MIN_PAUSE_BETWEEN_MESSAGES",
    "MIN_REQUEST_TIMEOUT",
    "MIN_SOCK_READ_TIMEOUT",
    "MIN_TEMPERATURE",
    "Config",
    "validate_ollama_url",
]

# Default constants for generation parameters
DEFAULT_TEMPERATURE: Final = 0.7
DEFAULT_MAX_TOKENS: Final = -1  # No limit - модель думает сколько хочет
DEFAULT_REQUEST_TIMEOUT: Final = 3600  # 1 час - модель думает сколько угодно
DEFAULT_SOCK_READ_TIMEOUT: Final = 3600  # 1 час - без ограничений на размышления
DEFAULT_PAUSE_BETWEEN_MESSAGES: Final = 1.0  # seconds between messages

# Системный промпт для развернутых ответов на русском языке
DEFAULT_SYSTEM_PROMPT: Final = (
    "Ты участвуешь в увлекательном диалоге на тему: '{topic}'. "
    "Твоя задача — давать максимально развёрнутые, глубокие и подробные ответы. "
    "Не ограничивай себя краткостью — раскрывай тему со всех сторон, приводи примеры, "
    "рассуждай вслух, анализируй контраргументы, приводи аналогии и сравнения. "
    "Используй сложные конструкции, передавай нюансы и оттенки смысла. "
    "Если нужно — разбивай ответ на части, используй абзацы для логической структуры. "
    "Выражай своё мнение аргументированно, ссылаясь на факты и логику. "
    "Будь как настоящий эксперт в дискуссии — мысли вслух, сомневайся, исследуй, "
    "а затем приходи к обоснованным выводам. "
    "Всё общение ведётся на русском языке. "
    "Отвечай так, будто пишешь развёрнутую статью или эссе, но сохраняя живость диалога."
)

# Validation ranges
MIN_TEMPERATURE: Final = 0.0
MAX_TEMPERATURE: Final = 1.0
MIN_MAX_TOKENS: Final = -1  # -1 means no limit
MIN_REQUEST_TIMEOUT: Final = 1
MIN_SOCK_READ_TIMEOUT: Final = 1
MIN_PAUSE_BETWEEN_MESSAGES: Final = 0.0


def validate_ollama_url(url: str) -> bool:
    """Validate Ollama host URL.

    Checks:
    - Presence of scheme (http or https)
    - Presence of netloc (host)
    - Correct format

    Args:
        url: URL to validate.

    Returns:
        True if URL is valid.

    Examples:
        >>> validate_ollama_url("http://localhost:11434")
        True
        >>> validate_ollama_url("https://ollama.example.com")
        True
        >>> validate_ollama_url("localhost:11434")
        False

    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
    except (TypeError, AttributeError):
        return False
    if not parsed.scheme or parsed.scheme not in ("http", "https"):
        return False
    return bool(parsed.netloc)


TNum = TypeVar("TNum", int, float)


def _validate_range[TNum: (int, float)](  # pylint: disable=redefined-outer-name
    value: TNum,
    min_value: TNum,
    max_value: TNum | None = None,
    param_name: str = "parameter",
) -> None:
    """Validate a numeric parameter in range.

    Args:
        value: Value to validate.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value (None for infinity).
        param_name: Parameter name for error message.

    Raises:
        ValueError: If value is out of range.

    """
    if value < min_value:
        msg = f"{param_name} must be >= {min_value}, got {value}"
        raise ValueError(msg)
    if max_value is not None and value > max_value:
        msg = f"{param_name} must be <= {max_value}, got {value}"
        raise ValueError(msg)


def _validate_temperature(value: float) -> None:
    """Validate temperature parameter."""
    _validate_range(value, MIN_TEMPERATURE, MAX_TEMPERATURE, "temperature")


def _validate_max_tokens(value: int) -> None:
    """Validate max_tokens parameter."""
    _validate_range(value, MIN_MAX_TOKENS, None, "max_tokens")


def _validate_request_timeout(value: int) -> None:
    """Validate request_timeout parameter."""
    _validate_range(value, MIN_REQUEST_TIMEOUT, None, "request_timeout")


def _validate_sock_read_timeout(value: int) -> None:
    """Validate sock_read_timeout parameter."""
    _validate_range(value, MIN_SOCK_READ_TIMEOUT, None, "sock_read_timeout")


def _validate_pause_between_messages(value: float) -> None:
    """Validate pause_between_messages parameter."""
    _validate_range(value, MIN_PAUSE_BETWEEN_MESSAGES, None, "pause_between_messages")


@dataclass(slots=True, eq=False)
class Config:
    """Configuration parameters for AI model dialogue.

    Attributes:
        temperature: Generation temperature (0.0-1.0).
        max_tokens: Maximum number of tokens in response.
        request_timeout: Request timeout to Ollama in seconds.
        sock_read_timeout: Response reading timeout from server in seconds.
        pause_between_messages: Pause between messages in seconds.
        default_system_prompt: System prompt template.
        ollama_host: Ollama API host URL.

    """

    # Ollama generation parameters
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS

    # Timeouts and delays
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    sock_read_timeout: int = DEFAULT_SOCK_READ_TIMEOUT
    pause_between_messages: float = DEFAULT_PAUSE_BETWEEN_MESSAGES

    # System prompt - развернутые ответы на русском
    default_system_prompt: str = DEFAULT_SYSTEM_PROMPT

    # Ollama API URL (default is local)
    ollama_host: str = "http://localhost:11434"

    def __post_init__(self) -> None:
        """Validate configuration after initialization.

        Raises:
            ValueError: If any parameter is incorrect.

        """
        self._apply_env_overrides()
        # Validate numeric parameters via common function
        _validate_temperature(self.temperature)
        _validate_max_tokens(self.max_tokens)
        _validate_request_timeout(self.request_timeout)
        _validate_sock_read_timeout(self.sock_read_timeout)
        _validate_pause_between_messages(self.pause_between_messages)

        # Validate URL via urllib.parse
        if not validate_ollama_url(self.ollama_host):
            msg = f"Invalid Ollama URL: {self.ollama_host}"
            raise ValueError(msg)

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration.

        Environment variables:
            OLLAMA_TEMPERATURE: Override temperature (float)
            OLLAMA_MAX_TOKENS: Override max_tokens (int)
            OLLAMA_HOST: Override ollama_host (str)
            OLLAMA_REQUEST_TIMEOUT: Override request_timeout (int)
            OLLAMA_SOCK_READ_TIMEOUT: Override sock_read_timeout (int)
            OLLAMA_PAUSE_BETWEEN: Override pause_between_messages (float)

        """
        env_mappings = {
            "OLLAMA_TEMPERATURE": ("temperature", float),
            "OLLAMA_MAX_TOKENS": ("max_tokens", int),
            "OLLAMA_HOST": ("ollama_host", str),
            "OLLAMA_REQUEST_TIMEOUT": ("request_timeout", int),
            "OLLAMA_SOCK_READ_TIMEOUT": ("sock_read_timeout", int),
            "OLLAMA_PAUSE_BETWEEN": ("pause_between_messages", float),
        }

        for env_var, (attr_name, type_func) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    value = type_func(env_value)
                    setattr(self, attr_name, value)
                except (ValueError, TypeError):
                    log.warning(
                        "Failed to apply environment override: %s=%s (expected %s)",
                        env_var,
                        env_value,
                        type_func.__name__,
                    )
