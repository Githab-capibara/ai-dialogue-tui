"""Централизованные стили для TUI приложения.

Этот модуль содержит все константы стилей для генерации CSS
и использования в коде приложения.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class StatusStyle(Enum):
    """Enum для стилей статусных сообщений."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class MessageStyles:
    """
    Стили для сообщений в логе диалога.

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
    """
    Идентификаторы UI элементов для предотвращения magic strings.

    Attributes:
        model_selection_container: Контейнер выбора моделей.
        selection_title: Заголовок выбора моделей.
        models_row: Строка с моделями.
        model_a_container: Контейнер модели A.
        model_b_container: Контейнер модели B.
        model_a_label: Метка модели A.
        model_b_label: Метка модели B.
        model_a_select: Селектор модели A.
        model_b_select: Селектор модели B.
        selection_buttons: Кнопки выбора моделей.
        start_btn: Кнопка старта.
        cancel_btn: Кнопка отмены.
        topic_input_container: Контейнер ввода темы.
        topic_label: Метка темы.
        topic_input: Поле ввода темы.
        topic_buttons: Кнопки темы.
        topic_start_btn: Кнопка старта темы.
        topic_cancel_btn: Кнопка отмены темы.
        main_container: Главный контейнер.
        status_bar: Статус бар.
        status_row: Строка статуса.
        status_label: Метка статуса.
        status_value: Значение статуса.
        dialogue_log: Лог диалога.
        controls_bar: Панель управления.
        controls_row: Строка управления.
        pause_btn: Кнопка паузы.
        clear_btn: Кнопка очистки.
        exit_btn: Кнопка выхода.
    """

    # pylint: disable=too-many-instance-attributes

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
    """
    CSS классы для стилизации элементов.

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


# Глобальные константы для использования в приложении
MESSAGE_STYLES: Final = MessageStyles()
UI_IDS: Final = UIElementIDs()
CSS_CLASSES: Final = CSSClasses()

# Экспорт публичного API модуля
__all__ = [
    "StatusStyle",
    "MessageStyles",
    "UIElementIDs",
    "CSSClasses",
    "MESSAGE_STYLES",
    "UI_IDS",
    "CSS_CLASSES",
    "generate_main_css",
]


def generate_main_css() -> str:
    """
    Сгенерировать основной CSS из централизованных констант.

    Returns:
        CSS строка для приложения.
    """
    return f"""
#{UI_IDS.model_selection_container} {{
    align: center middle;
    height: 100%;
    background: $surface;
}}

#{UI_IDS.selection_title} {{
    text-align: center;
    text-style: bold;
    padding: 1 2;
    margin-bottom: 2;
}}

#{UI_IDS.models_row} {{
    height: auto;
    align: center middle;
}}

#{UI_IDS.model_a_container}, #{UI_IDS.model_b_container} {{
    width: 30;
    margin: 0 2;
    border: solid $primary;
    padding: 1 2;
}}

#{UI_IDS.model_a_label}, #{UI_IDS.model_b_label} {{
    margin-bottom: 1;
    text-align: center;
}}

#{UI_IDS.selection_buttons} {{
    height: auto;
    align: center middle;
    margin-top: 2;
}}

#{UI_IDS.selection_buttons} Button {{
    margin: 0 1;
}}

#{UI_IDS.topic_input_container} {{
    align: center middle;
    height: 100%;
    background: $surface;
}}

#{UI_IDS.topic_label} {{
    text-align: center;
    text-style: bold;
    padding: 1 2;
    margin-bottom: 1;
}}

#{UI_IDS.topic_input} {{
    width: 60;
    margin-bottom: 2;
}}

#{UI_IDS.topic_buttons} {{
    height: auto;
    align: center middle;
}}

#{UI_IDS.topic_buttons} Button {{
    margin: 0 1;
}}

#{UI_IDS.main_container} {{
    height: 100%;
}}

#{UI_IDS.status_bar} {{
    height: 3;
    background: $surface;
    border: solid $primary;
    margin: 1;
    padding: 0 2;
}}

#{UI_IDS.status_row} {{
    height: 100%;
    align: left middle;
}}

#{UI_IDS.status_label} {{
    width: auto;
    padding: 0 1;
}}

#{UI_IDS.dialogue_log} {{
    height: 1fr;
    margin: 0 1;
    border: solid $secondary;
}}

#{UI_IDS.controls_bar} {{
    height: 4;
    background: $surface;
    border: solid $primary;
    margin: 1;
    padding: 0 2;
}}

#{UI_IDS.controls_row} {{
    height: 100%;
    align: center middle;
}}

#{UI_IDS.controls_row} Button {{
    margin: 0 1;
    width: 16;
}}

.{CSS_CLASSES.model_a_message} {{
    color: $success;
    text-style: bold;
}}

.{CSS_CLASSES.model_b_message} {{
    color: $accent;
    text-style: bold;
}}

.{CSS_CLASSES.system_message} {{
    color: $warning;
    text-style: italic;
}}

.{CSS_CLASSES.error_message} {{
    color: $error;
    text-style: bold;
}}
"""
