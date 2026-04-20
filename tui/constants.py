"""Константы UI для TUI приложения.

Этот модуль содержит все константы для стилизации и идентификации
UI элементов.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class MessageStyles:
    """Стили для сообщений в логе диалога.

    Attributes:
        model_a: Стиль для сообщений модели A.
        model_b: Стиль для сообщений модели B.
        system: Стиль для системных сообщений.
        error: Стиль для сообщений об ошибках.

    """

    model_a: str = "bold green"
    model_b: str = "bold blue"
    system: str = "dim italic yellow"
    error: str = "bold red"


@dataclass(frozen=True)
class UIElementIDs:
    """Идентификаторы UI элементов для предотвращения magic strings."""

    # Model Selection Screen
    model_selection_container: str = "model-selection-container"
    selection_title: str = "selection-title"
    models_row: str = "models-row"
    model_a_container: str = "model-a-container"
    model_b_container: str = "model-b-container"
    model_a_label: str = "model-a-label"
    model_b_label: str = "model-b-label"
    model_a_select: str = "model-a-select"
    model_b_select: str = "model-b-select"
    selection_buttons: str = "selection-buttons"
    start_btn: str = "start-btn"
    cancel_btn: str = "cancel-btn"

    # Topic Input Screen
    topic_input_container: str = "topic-input-container"
    topic_input_content: str = "topic-input-content"
    topic_label: str = "topic-label"
    topic_input: str = "topic-input"
    topic_buttons: str = "topic-buttons"
    topic_start_btn: str = "topic-start-btn"
    topic_cancel_btn: str = "topic-cancel-btn"

    # Main Screen
    main_container: str = "main-container"
    status_bar: str = "status-bar"
    status_row: str = "status-row"
    status_label: str = "status-label"
    status_value: str = "status-value"
    dialogue_log: str = "dialogue-log"
    controls_bar: str = "controls-bar"
    controls_row: str = "controls-row"
    pause_btn: str = "pause-btn"
    clear_btn: str = "clear-btn"
    exit_btn: str = "exit-btn"


@dataclass(frozen=True)
class CSSClasses:
    """CSS классы для стилизации элементов.

    Attributes:
        model_a_message: Класс для сообщений модели A.
        model_b_message: Класс для сообщений модели B.
        system_message: Класс для системных сообщений.
        error_message: Класс для сообщений об ошибках.

    """

    model_a_message: str = "model-a-message"
    model_b_message: str = "model-b-message"
    system_message: str = "system-message"
    error_message: str = "error-message"


MESSAGE_STYLES: Final = MessageStyles()
UI_IDS: Final = UIElementIDs()
CSS_CLASSES: Final = CSSClasses()

__all__ = [
    "CSS_CLASSES",
    "MESSAGE_STYLES",
    "UI_IDS",
    "CSSClasses",
    "MessageStyles",
    "UIElementIDs",
]
