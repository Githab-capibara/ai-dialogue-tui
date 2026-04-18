"""Функции санитизации для безопасного отображения данных.

Этот модуль содержит функции для очистки пользовательского ввода
и ответов модели от потенциально опасных конструкций.
"""

from __future__ import annotations

import html
import re

# Константа для ограничения длины превью ответа
MAX_RESPONSE_PREVIEW_LENGTH: int = 100

__all__ = [
    "MAX_RESPONSE_PREVIEW_LENGTH",
    "sanitize_response_for_display",
    "sanitize_topic",
]


def sanitize_topic(topic: str) -> str:
    """Санитизировать ввод темы для предотвращения инъекции промпта.

    Экранирует специальные символы и удаляет
    потенциально опасные конструкции.

    Args:
        topic: Исходная тема от пользователя.

    Returns:
        Очищенная тема.

    Raises:
        TypeError: Если topic не является строкой.

    """
    if not isinstance(topic, str):
        msg = f"topic должен быть строкой, получен {type(topic).__name__}"
        raise TypeError(msg)
    if not topic:
        return ""
    topic = topic.strip()
    topic = topic.replace("{", "{{").replace("}", "}}")
    return re.sub(r"\[([^\]]*)\]", r"[[\1]]", topic)


def sanitize_response_for_display(response: str) -> str:
    """Санитизировать ответ модели для безопасного отображения в TUI.

    Экранирует markup-символы Textual для предотвращения XSS-подобных атак.
    Обрезает длинные ответы до MAX_RESPONSE_PREVIEW_LENGTH символов.

    Args:
        response: Исходный ответ от модели.

    Returns:
        Безопасный для отображения текст.

    Raises:
        TypeError: Если response не является строкой.

    """
    if not isinstance(response, str):
        msg = f"response должен быть строкой, получен {type(response).__name__}"
        raise TypeError(msg)
    if not response:
        return ""

    # HTML экранирование базовых символов
    response = html.escape(response, quote=False)

    # Экранирование Textual markup символов
    # Порядок важен: сначала экранируем специальные символы
    response = response.replace("\\", "\\\\")  # Экранируем backslash
    response = response.replace("[", "[[")  # Square brackets
    response = response.replace("]", "]]")  # Square brackets
    response = response.replace("{", "{{")  # Curly braces
    response = response.replace("}", "}}")  # Curly braces
    response = response.replace("@", "@@")  # CSS class prefix
    response = response.replace("#", "##")  # ID prefix
    response = response.replace("*", "\\*")  # Bold/italic marker
    response = response.replace("_", "\\_")  # Italic marker
    response = response.replace("`", "\\`")  # Code marker
    response = response.replace("~", "\\~")  # Strikethrough marker
    response = response.replace("|", "\\|")  # Table separator
    response = response.replace("\n", " ")  # Newlines

    if len(response) > MAX_RESPONSE_PREVIEW_LENGTH:
        response = response[:MAX_RESPONSE_PREVIEW_LENGTH] + "..."
    return response
