"""Модуль конфигурации для приложения AI Dialogue TUI.

Этот модуль предоставляет централизованное управление конфигурацией приложения,
включая параметры для Ollama API и настройки приложения.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class Config:
    """Класс конфигурации приложения.

    Attributes:
        ollama_host: URL для подключения к Ollama API.
        temperature: Температура генерации (0.0-1.0).
        max_tokens: Максимальное количество токенов в ответе.
        request_timeout: Таймаут запроса в секундах.
        pause_between_messages: Пауза между сообщениями в секундах.
    """

    ollama_host: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 200
    request_timeout: int = 60
    pause_between_messages: float = 1.0

    def validate_ollama_url(self, url: str) -> bool:
        """
        Проверить корректность URL для Ollama API.

        Args:
            url: URL для проверки.

        Returns:
            True если URL корректен, False в противном случае.
        """
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            # Проверка наличия netloc
            if not parsed.netloc:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def __post_init__(self) -> None:
        """Валидация конфигурации после инициализации."""
        if not self.validate_ollama_url(self.ollama_host):
            raise ValueError(
                f"Некорректный URL Ollama: {self.ollama_host}. "
                "URL должен начинаться с http:// или https:// и содержать host."
            )


class _ConfigSingleton:
    """Синглтон для хранения конфигурации.

    Note:
        Реализует паттерн Singleton для обеспечения единственного экземпляра
        конфигурации на всё приложение.
    """

    _instance: Config | None = None

    @classmethod
    def get_config(cls) -> Config:
        """
        Получить экземпляр конфигурации.

        Returns:
            Экземпляр Config.
        """
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance


# pylint: disable=invalid-name
config: Config = _ConfigSingleton.get_config()
# pylint: enable=invalid-name
