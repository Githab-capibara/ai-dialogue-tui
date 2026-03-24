"""TUI приложение для диалога ИИ-моделей.

Этот модуль предоставляет Textual TUI приложение для управления диалогом
между двумя ИИ-моделями через Ollama API.
"""

from __future__ import annotations

import asyncio
import html
from typing import TYPE_CHECKING, Literal

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    RichLog,
    Static,
)

if TYPE_CHECKING:
    from models.conversation import Conversation
    from models.ollama_client import OllamaClient

from config import config

# Константы стилей
STYLE_MODEL_A = "bold green"
STYLE_MODEL_B = "bold blue"
STYLE_TURN_INDICATOR = "bold yellow"

# CSS стили вынесены в отдельную константу
MAIN_CSS = """
Screen {
    background: $surface;
}

#main-container {
    width: 100%;
    height: 100%;
    padding: 1 2;
}

#top-panel {
    width: 100%;
    height: 1fr;
    background: $panel;
    border: solid $primary;
    margin: 1 0;
    padding: 1 2;
}

#turn-indicator {
    width: 100%;
    content-align: center middle;
    background: $accent;
    color: $text;
    text-style: bold;
    padding: 1 2;
}

#log {
    width: 100%;
    height: 100%;
    background: $surface;
    border: solid $primary;
    padding: 1 2;
}

#bottom-panel {
    width: 100%;
    height: auto;
    background: $panel;
    border: solid $primary;
    margin: 1 0;
    padding: 1 2;
}

#topic-input {
    width: 100%;
    margin: 1 0;
}

.button-container {
    width: 100%;
    align: center middle;
}

Button {
    margin: 0 1;
}

#start-btn {
    background: $success;
}

#pause-btn {
    background: $warning;
}

#clear-btn {
    background: $error;
}

#quit-btn {
    background: $secondary;
}

.model-selection-item {
    width: 100%;
    padding: 1 2;
}

.selected {
    background: $primary;
    color: $text;
}

.error-message {
    color: $error;
    text-align: center;
    padding: 2;
}

.success-message {
    color: $success;
    text-align: center;
    padding: 2;
}
"""


class ModelSelectionScreen(Screen[str]):
    """Экран выбора модели из списка доступных.

    Attributes:
        available_models: Список доступных моделей для выбора.

    Note:
        Обрабатывает случаи с пустым списком моделей.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Отмена"),
        Binding("enter", "select", "Выбрать"),
    ]

    def __init__(self, available_models: list[str]) -> None:
        """
        Инициализировать экран выбора модели.

        Args:
            available_models: Список доступных моделей.

        Raises:
            ValueError: Если список моделей пуст.
        """
        super().__init__()
        if not available_models:
            raise ValueError("Список моделей не может быть пустым")
        self._available_models = available_models
        self._selected_index = 0
        self._selected_model: str | None = None

    def compose(self) -> ComposeResult:
        """Создать UI экрана выбора модели."""
        with Vertical():
            yield Static("Выберите модель:", classes="model-selection-item")
            for idx, model in enumerate(self._available_models):
                prefix = "> " if idx == self._selected_index else "  "
                yield Static(f"{prefix}{model}", classes="model-selection-item")
            yield Static(
                "Используйте ↑↓ для навигации, Enter для выбора",
                classes="model-selection-item",
            )

    def on_key(self, event: str) -> None:
        """
        Обработать нажатие клавиши.

        Args:
            event: Событие клавиши.
        """
        if event == "up":
            self._selected_index = (self._selected_index - 1) % len(
                self._available_models
            )
        elif event == "down":
            self._selected_index = (self._selected_index + 1) % len(
                self._available_models
            )
        elif event == "enter":
            self._selected_model = self._available_models[self._selected_index]
            self.dismiss(self._selected_model)
        elif event == "escape":
            self.dismiss(None)
        self.refresh()


class DialogueApp(App[None]):
    """Основное TUI приложение для диалога ИИ-моделей.

    Attributes:
        TITLE: Заголовок приложения.
        sub_title: Подзаголовок приложения.
        CSS: Стили приложения.
        BINDINGS: Привязки клавиш.

    Note:
        Поддерживает паузу диалога, очистку истории и обработку ошибок.
    """

    TITLE = "AI Dialogue TUI"
    sub_title = "Диалог двух ИИ-моделей"
    CSS = MAIN_CSS
    BINDINGS = [
        Binding("ctrl+q", "quit", "Выход"),
        Binding("ctrl+p", "pause", "Пауза/Старт"),
        Binding("ctrl+r", "clear", "Очистить"),
    ]

    def __init__(self) -> None:
        """Инициализировать приложение."""
        super().__init__()
        self._client: OllamaClient | None = None
        self._conversation: Conversation | None = None
        self._is_paused = True
        self._dialogue_task: asyncio.Task[None] | None = None
        self._available_models: list[str] = []

    def compose(self) -> ComposeResult:
        """Создать основной UI приложения."""
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="top-panel"):
                yield Static("Ожидание выбора моделей...", id="turn-indicator")
                yield RichLog(id="log", highlight=True, markup=True)
            with Vertical(id="bottom-panel"):
                yield Input(
                    placeholder="Введите тему диалога",
                    id="topic-input",
                )
                with Horizontal(classes="button-container"):
                    yield Button("Старт", id="start-btn", variant="success")
                    yield Button("Пауза", id="pause-btn", variant="warning")
                    yield Button("Очистить", id="clear-btn", variant="error")
                    yield Button("Выход", id="quit-btn", variant="default")
        yield LoadingIndicator()
        yield Footer()

    async def on_mount(self) -> None:
        """
        Обработать событие монтирования приложения.

        Note:
            Инициализирует клиент Ollama и загружает список моделей.
            Обрабатывает ошибки подключения.
        """
        try:
            self._client = OllamaClient(host=config.ollama_host)
            self._available_models = await self._client.list_models()
            if not self._available_models:
                self.notify(
                    "Нет доступных моделей. Установите модели через 'ollama pull'.",
                    severity="error",
                )
                return
            # Запускаем экран выбора первой модели
            first_model = await self.push_screen_wait(ModelSelectionScreen(self._available_models))
            if first_model is None:
                self.exit()
                return
            # Запускаем экран выбора второй модели
            second_model = await self.push_screen_wait(
                ModelSelectionScreen([m for m in self._available_models if m != first_model])
            )
            if second_model is None:
                self.exit()
                return
            # Создаем диалог
            self._conversation = Conversation(
                model_a_name=first_model,
                model_b_name=second_model,
                topic="Общая тема",
            )
            self.query_one("#turn-indicator", Static).update(
                f"[bold]Ход:[/bold] {first_model}"
            )
            self.notify(f"Диалог initialized: {first_model} vs {second_model}")
        except aiohttp.ClientError as e:
            self.notify(f"Ошибка подключения к Ollama: {e}", severity="error")
            self.exit()
        except (ValueError, RuntimeError) as e:
            self.notify(f"Ошибка инициализации: {e}", severity="error")
            self.exit()

    def action_cancel(self) -> None:
        """Обработать действие отмены."""
        self.exit()

    @on(Button.Pressed, "#start-btn")
    def on_start_pressed(self) -> None:
        """
        Обработать нажатие кнопки старта.

        Note:
            Запускает диалог если он еще не запущен.
        """
        self.action_toggle_pause()

    @on(Button.Pressed, "#pause-btn")
    def on_pause_pressed(self) -> None:
        """
        Обработать нажатие кнопки паузы.

        Note:
            Проверяет наличие диалога перед переключением паузы.
        """
        if self._conversation is None:
            self.notify("Сначала выберите модели", severity="warning")
            return
        self.action_toggle_pause()

    @on(Button.Pressed, "#clear-btn")
    def on_clear_pressed(self) -> None:
        """Обработать нажатие кнопки очистки."""
        if self._conversation:
            self._conversation.clear_contexts()
            self.query_one("#log", RichLog).clear()
            self.notify("История очищена")

    @on(Button.Pressed, "#quit-btn")
    def on_quit_pressed(self) -> None:
        """Обработать нажатие кнопки выхода."""
        self.exit()

    def action_toggle_pause(self) -> None:
        """
        Переключить состояние паузы диалога.

        Note:
            Запускает диалог если он был на паузе.
        """
        if self._conversation is None:
            self.notify("Сначала выберите модели", severity="warning")
            return
        self._is_paused = not self._is_paused
        if not self._is_paused:
            if self._dialogue_task is None or self._dialogue_task.done():
                self._dialogue_task = asyncio.create_task(self._run_dialogue())
            self.notify("Диалог запущен")
        else:
            self.notify("Диалог на паузе")

    def _format_response(self, response: str, max_length: int = 100) -> str:
        """
        Отформатировать ответ для отображения.

        Args:
            response: Исходный ответ.
            max_length: Максимальная длина.

        Returns:
            Отформатированный ответ.
        """
        sanitized = sanitize_response_for_display(response)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        return sanitized

    async def _run_dialogue(self) -> None:
        """
        Запустить цикл диалога.

        Note:
            Проверяет флаг паузы и отмену задачи.
            Обрабатывает ошибки генерации.
        """
        log_widget = self.query_one("#log", RichLog)
        turn_indicator = self.query_one("#turn-indicator", Static)

        assert self._conversation is not None
        assert self._client is not None

        while not self._is_paused:
            try:
                # Проверка отмены задачи
                if self._dialogue_task and self._dialogue_task.cancelled():
                    break

                current_model = (
                    self._conversation.model_a_name
                    if self._conversation.current_turn == "A"
                    else self._conversation.model_b_name
                )
                turn_indicator.update(f"[bold]Ход:[/bold] {current_model}")

                response = await self._conversation.process_turn(self._client)

                # Отображаем ответ
                formatted_response = self._format_response(response)
                log_widget.write(f"{current_model}: {formatted_response}")

                # Пауза между сообщениями
                await asyncio.sleep(config.pause_between_messages)

            except aiohttp.ClientError as e:
                self.notify(f"Ошибка сети: {e}", severity="error")
                break
            except (RuntimeError, ValueError) as e:
                self.notify(f"Ошибка диалога: {e}", severity="error")
                break
            except Exception as e:
                self.notify(f"Неизвестная ошибка: {e}", severity="error")
                break

    async def on_unmount(self) -> None:
        """
        Обработать событие размонтирования приложения.

        Note:
            Корректно отменяет задачу диалога и закрывает клиент.
        """
        if self._dialogue_task and not self._dialogue_task.done():
            self._dialogue_task.cancel()
            try:
                await self._dialogue_task
            except asyncio.CancelledError:
                pass
        if self._client:
            try:
                await self._client.close()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                pass


def sanitize_topic(topic: str) -> str:
    """
    Санитизировать ввод темы для безопасного использования.

    Args:
        topic: Исходная тема.

    Returns:
        Санитизированная тема.
    """
    # Экранирование специальных символов и обрезка
    sanitized = html.escape(topic.strip())
    # Дополнительная защита от инъекций
    sanitized = sanitized.replace("{", "{{").replace("}", "}}")
    return sanitized


def sanitize_response_for_display(response: str) -> str:
    """
    Санитизировать ответ модели для безопасного отображения.

    Args:
        response: Исходный ответ.

    Returns:
        Санитизированный ответ.
    """
    # Экранирование markup символов
    sanitized = html.escape(response)
    # Замена newlines на пробелы для компактности
    sanitized = sanitized.replace("\n", " ")
    return sanitized
