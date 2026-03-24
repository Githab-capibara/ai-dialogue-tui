"""Конфигурация приложения AI Dialogue TUI."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


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


@dataclass(frozen=True)
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
    temperature: float = 0.7
    max_tokens: int = 200

    # Таймауты и задержки
    request_timeout: int = 60  # секунд на запрос к Ollama
    pause_between_messages: float = 1.0  # секунд между сообщениями

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
            ValueError: Если ollama_host некорректный.
        """
        # Валидация URL через urllib.parse
        if not validate_ollama_url(self.ollama_host):
            raise ValueError(f"Некорректный URL Ollama: {self.ollama_host}")
