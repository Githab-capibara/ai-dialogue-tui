"""Функции санитизации для безопасного отображения данных.

Этот модуль содержит функции для очистки пользовательского ввода
и ответов модели от потенциально опасных конструкций.
"""

from __future__ import annotations

import html
import re


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

    Args:
        response: Исходный ответ от модели.

    Returns:
        Безопасный для отображения текст.
    """
    response = html.escape(response, quote=False)
    response = response.replace("\n", " ")
    if len(response) > 100:
        response = response[:100] + "..."
    return response
