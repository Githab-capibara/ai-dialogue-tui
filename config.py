"""Обратная совместимость для импортов из корневого config.py.

Этот модуль перенаправляет импорты в models.config для обратной совместимости.
Новый код должен использовать: from models.config import Config
"""

from models.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_PAUSE_BETWEEN_MESSAGES,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_TEMPERATURE,
    MAX_TEMPERATURE,
    MIN_MAX_TOKENS,
    MIN_PAUSE_BETWEEN_MESSAGES,
    MIN_REQUEST_TIMEOUT,
    MIN_TEMPERATURE,
    Config,
    validate_ollama_url,
)

__all__ = [
    "Config",
    "validate_ollama_url",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_PAUSE_BETWEEN_MESSAGES",
    "MIN_TEMPERATURE",
    "MAX_TEMPERATURE",
    "MIN_MAX_TOKENS",
    "MIN_REQUEST_TIMEOUT",
    "MIN_PAUSE_BETWEEN_MESSAGES",
]
