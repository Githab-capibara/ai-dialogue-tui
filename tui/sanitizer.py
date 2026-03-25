"""Функции санитизации для безопасного отображения данных.

Этот модуль содержит функции для очистки пользовательского ввода
и ответов модели от потенциально опасных конструкций.
"""

from __future__ import annotations

import html
import re
from typing import Protocol, runtime_checkable

# Константа для ограничения длины превью ответа
MAX_RESPONSE_PREVIEW_LENGTH: int = 100

__all__ = [
    "sanitize_topic",
    "sanitize_response_for_display",
    "MAX_RESPONSE_PREVIEW_LENGTH",
    "Sanitizer",
]


@runtime_checkable
class Sanitizer(Protocol):
    """
    Протокол для санитизации данных.

    Определяет интерфейс для компонентов санитизации ввода и вывода.
    Позволяет использовать dependency injection для тестируемости.

    Example:
        >>> class MySanitizer:
        ...     def sanitize_topic(self, topic: str) -> str:
        ...         return topic.strip()
        ...     def sanitize_response_for_display(self, response: str) -> str:
        ...         return response
        >>> sanitizer: Sanitizer = MySanitizer()  # Типизация работает
    """

    def sanitize_topic(self, topic: str) -> str:
        """
        Санитизировать ввод темы для предотвращения инъекции промпта.

        Args:
            topic: Исходная тема от пользователя.

        Returns:
            Очищенная тема.
        """
        ...

    def sanitize_response_for_display(self, response: str) -> str:
        """
        Санитизировать ответ модели для безопасного отображения в TUI.

        Args:
            response: Исходный ответ от модели.

        Returns:
            Безопасный для отображения текст.
        """
        ...


def sanitize_topic(topic: str) -> str:
    """
    Санитизировать ввод темы для предотвращения инъекции промпта.

    Экранирует специальные символы и удаляет потенциально опасные конструкции.

    Args:
        topic: Исходная тема от пользователя.

    Returns:
        Очищенная тема.
    """
    topic = topic.strip()
    topic = topic.replace("{", "{{").replace("}", "}}")
    topic = re.sub(r"\[([^\]]*)\]", r"[[\1]]", topic)
    return topic


def sanitize_response_for_display(response: str) -> str:
    """
    Санитизировать ответ модели для безопасного отображения в TUI.

    Экранирует markup-символы Textual для предотвращения XSS-подобных атак.
    Обрезает длинные ответы до MAX_RESPONSE_PREVIEW_LENGTH символов.

    Args:
        response: Исходный ответ от модели.

    Returns:
        Безопасный для отображения текст.
    """
    response = html.escape(response, quote=False)
    response = response.replace("\n", " ")
    if len(response) > MAX_RESPONSE_PREVIEW_LENGTH:
        response = response[:MAX_RESPONSE_PREVIEW_LENGTH] + "..."
    return response
