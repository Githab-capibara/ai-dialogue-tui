"""Функции санитизации для безопасного отображения данных.

Этот модуль содержит функции для очистки пользовательского ввода
и ответов модели от потенциально опасных конструкций.
"""

from __future__ import annotations

import html
import re
from functools import lru_cache

MAX_RESPONSE_PREVIEW_LENGTH: int = 100

_BRACKET_PATTERN = re.compile(r"\[([^\]]*)\]")

SANITIZE_CHARS: tuple[tuple[str, str], ...] = (
    ("\\", "\\\\"),
    ("[", "[["),
    ("]", "]]"),
    ("{", "{{"),
    ("}", "}}"),
    ("@", "@@"),
    ("#", "##"),
    ("*", "\\*"),
    ("_", "\\_"),
    ("`", "\\`"),
    ("~", "\\~"),
    ("|", "\\|"),
    ("\n", " "),
)

__all__ = [
    "MAX_RESPONSE_PREVIEW_LENGTH",
    "sanitize_response_for_display",
    "sanitize_topic",
]


@lru_cache(maxsize=128)
def _compile_sanitizer() -> tuple[str, ...]:
    """Кэшировать паттерн для санитизации темы."""
    return ()


def sanitize_topic(topic: str) -> str:
    """Санитизировать ввод темы для предотвращения инъекции промпта.

    Экранирует специальные символы и удаляет
    потенциально опасные конструкции.

    """
    if not isinstance(topic, str):
        msg = f"topic должен быть строкой, получен {type(topic).__name__}"
        raise TypeError(msg)
    if not topic:
        return ""
    topic = topic.strip()
    topic = topic.replace("{", "{{").replace("}", "}}")
    return _BRACKET_PATTERN.sub(r"[[\1]]", topic)


def sanitize_response_for_display(response: str) -> str:
    """Санитизировать ответ модели для безопасного отображения в TUI.

    Экранирует markup-символы Textual для предотвращения XSS-подобных атак.
    Обрезает длинные ответы до MAX_RESPONSE_PREVIEW_LENGTH символов.

    """
    if not isinstance(response, str):
        msg = f"response должен быть строкой, получен {type(response).__name__}"
        raise TypeError(msg)
    if not response:
        return ""

    response = html.escape(response, quote=False)

    for old, new in SANITIZE_CHARS:
        response = response.replace(old, new)

    if len(response) > MAX_RESPONSE_PREVIEW_LENGTH:
        response = response[:MAX_RESPONSE_PREVIEW_LENGTH] + "..."
    return response
