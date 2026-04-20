"""Sanitization functions for safe data display.

This module contains functions for cleaning user input
and model responses from potentially dangerous constructs.
"""

from __future__ import annotations

import html
import re

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
    ('"', '\\"'),
    ("\n", " "),
)

_BRACKET_TRANSLATION_TABLE = str.maketrans(
    {
        "{": "{{",
        "}": "}}",
    }
)


__all__ = [
    "MAX_RESPONSE_PREVIEW_LENGTH",
    "sanitize_response_for_display",
    "sanitize_topic",
]


def sanitize_topic(topic: str) -> str:
    """Sanitize topic input to prevent prompt injection.

    Escapes special characters and removes
    potentially dangerous constructs.

    """
    if not isinstance(topic, str):
        msg = f"topic must be a string, got {type(topic).__name__}"
        raise TypeError(msg)
    if not topic:
        return ""
    topic = html.escape(topic, quote=True)
    topic = topic.strip()
    topic = topic.translate(_BRACKET_TRANSLATION_TABLE)
    return _BRACKET_PATTERN.sub(r"[[\1]]", topic)


def sanitize_response_for_display(response: str) -> str:
    """Sanitize model response for safe display in TUI.

    Escapes Textual markup characters to prevent XSS-like attacks.
    Truncates long responses to MAX_RESPONSE_PREVIEW_LENGTH characters.

    """
    if not isinstance(response, str):
        msg = f"response must be a string, got {type(response).__name__}"
        raise TypeError(msg)
    if not response:
        return ""

    response = html.escape(response, quote=True)

    trans_table = str.maketrans(
        {char: replacement for char, replacement in SANITIZE_CHARS if char != "\n"})
    response = response.translate(trans_table)
    response = response.replace("\n", " ")

    if len(response) > MAX_RESPONSE_PREVIEW_LENGTH:
        response = response[:MAX_RESPONSE_PREVIEW_LENGTH] + "..."
    return response
