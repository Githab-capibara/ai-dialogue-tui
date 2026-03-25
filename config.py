"""Конфигурация приложения AI Dialogue TUI.

Этот модуль содержит константы по умолчанию и класс конфигурации
с полной валидацией параметров.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from urllib.parse import urlparse

# Константы по умолчанию для параметров генерации
DEFAULT_TEMPERATURE: Final = 0.7
DEFAULT_MAX_TOKENS: Final = 200
DEFAULT_REQUEST_TIMEOUT: Final = 60  # секунд на запрос к Ollama
DEFAULT_PAUSE_BETWEEN_MESSAGES: Final = 1.0  # секунд между сообщениями

# Диапазоны валидации
MIN_TEMPERATURE: Final = 0.0
MAX_TEMPERATURE: Final = 1.0
MIN_MAX_TOKENS: Final = 1
MIN_REQUEST_TIMEOUT: Final = 1
MIN_PAUSE_BETWEEN_MESSAGES: Final = 0.0


def validate_ollama_url(url: str) -> bool:
    """
    Валидировать URL Ollama хоста.

    Проверяет:
    - Наличие схемы (http или https)
    - Наличие netloc (хост)
    - Корректность формата

    Args:
        url: URL для валидации.

    Returns:
        True если URL корректный.

    Examples:
        >>> validate_ollama_url("http://localhost:11434")
        True
        >>> validate_ollama_url("https://ollama.example.com")
        True
        >>> validate_ollama_url("localhost:11434")
        False
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        # Проверка схемы (только http или https)
        if parsed.scheme not in ("http", "https"):
            return False
        # Проверка наличия хоста
        if not parsed.netloc:
            return False
        return True
    except ValueError:
        return False


def _validate_temperature(value: float) -> None:
    """
    Валидировать параметр temperature.

    Args:
        value: Значение temperature для валидации.

    Raises:
        ValueError: Если значение вне диапазона [0.0, 1.0].
    """
    if not MIN_TEMPERATURE <= value <= MAX_TEMPERATURE:
        raise ValueError(
            f"temperature должен быть в диапазоне [{MIN_TEMPERATURE}, {MAX_TEMPERATURE}], "
            f"получено {value}"
        )


def _validate_max_tokens(value: int) -> None:
    """
    Валидировать параметр max_tokens.

    Args:
        value: Значение max_tokens для валидации.

    Raises:
        ValueError: Если значение меньше минимального.
    """
    if value < MIN_MAX_TOKENS:
        raise ValueError(
            f"max_tokens должен быть >= {MIN_MAX_TOKENS}, получено {value}"
        )


def _validate_request_timeout(value: int) -> None:
    """
    Валидировать параметр request_timeout.

    Args:
        value: Значение request_timeout для валидации.

    Raises:
        ValueError: Если значение меньше минимального.
    """
    if value < MIN_REQUEST_TIMEOUT:
        raise ValueError(
            f"request_timeout должен быть >= {MIN_REQUEST_TIMEOUT}, получено {value}"
        )


def _validate_pause_between_messages(value: float) -> None:
    """
    Валидировать параметр pause_between_messages.

    Args:
        value: Значение pause_between_messages для валидации.

    Raises:
        ValueError: Если значение меньше минимального.
    """
    if value < MIN_PAUSE_BETWEEN_MESSAGES:
        raise ValueError(
            f"pause_between_messages должен быть >= {MIN_PAUSE_BETWEEN_MESSAGES}, "
            f"получено {value}"
        )


@dataclass(frozen=True, slots=True)
class Config:
    """
    Параметры конфигурации для диалога ИИ-моделей.

    Attributes:
        temperature: Температура генерации (0.0-1.0).
        max_tokens: Максимальное количество токенов в ответе.
        request_timeout: Таймаут запроса к Ollama в секундах.
        pause_between_messages: Пауза между сообщениями в секундах.
        default_system_prompt: Шаблон системного промпта.
        ollama_host: URL хоста Ollama API.
    """

    # Параметры генерации Ollama
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS

    # Таймауты и задержки
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    pause_between_messages: float = DEFAULT_PAUSE_BETWEEN_MESSAGES

    # Системный промпт
    default_system_prompt: str = (
        "Ты участвуешь в диалоге на тему '{topic}'. "
        "Отвечай кратко и по существу. Не повторяйся. "
        "Веди себя как живой собеседник."
    )

    # URL Ollama API (по умолчанию локальный)
    ollama_host: str = "http://localhost:11434"

    def __post_init__(self) -> None:
        """
        Валидация конфигурации после инициализации.

        Raises:
            ValueError: Если какой-либо параметр некорректный.
        """
        # Валидация числовых параметров
        _validate_temperature(self.temperature)
        _validate_max_tokens(self.max_tokens)
        _validate_request_timeout(self.request_timeout)
        _validate_pause_between_messages(self.pause_between_messages)

        # Валидация URL через urllib.parse
        if not validate_ollama_url(self.ollama_host):
            raise ValueError(f"Некорректный URL Ollama: {self.ollama_host}")
