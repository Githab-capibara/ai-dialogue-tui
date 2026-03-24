"""TUI приложение для диалога двух ИИ-моделей.

Этот модуль содержит только UI-компоненты и обработчики событий.
Бизнес-логика вынесена в сервисный слой (services/dialogue_service.py).
"""

from __future__ import annotations

import asyncio
import html
import re

import aiohttp
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    Static,
)

from config import Config, validate_ollama_url
from controllers.dialogue_controller import DialogueController, UIState
from models.conversation import Conversation
from models.ollama_client import OllamaClient, OllamaError
from services.dialogue_service import DialogueService, DialogueTurnResult
from tui.styles import (
    MESSAGE_STYLES,
    UI_IDS,
    generate_main_css,
)

# CSS генерируется из централизованных констант
MAIN_CSS = generate_main_css()


def sanitize_topic(topic: str) -> str:
    """
    Санитизировать ввод темы для предотвращения инъекции промпта.

    Экранирует специальные символы и удаляет потенциально опасные конструкции.

    Args:
        topic: Исходная тема от пользователя.

    Returns:
        Очищенная тема.
    """
    # Удаляем потенциально опасные символы
    topic = topic.strip()
    # Экранируем фигурные скобки чтобы предотвратить инъекцию форматирования
    topic = topic.replace("{", "{{").replace("}", "}}")
    # Экранируем квадратные скобки для предотвращения markup инъекций
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
    # Экранируем HTML-подобные конструкции которые могут интерпретироваться
    # как markup
    response = html.escape(response, quote=False)
    # Заменяем newlines на пробелы для компактного отображения
    response = response.replace("\n", " ")
    # Обрезаем если слишком длинный
    if len(response) > 100:
        response = response[:100] + "..."
    return response


class ModelSelectionScreen(ModalScreen):
    """Модальное окно для выбора двух моделей."""

    BINDINGS = [
        Binding("escape", "cancel", "Отмена"),
    ]

    def __init__(
        self,
        models: list[str],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._available_models = models

    def compose(self) -> ComposeResult:
        with Container(id=UI_IDS.model_selection_container):
            yield Static("Выберите две модели для диалога", id=UI_IDS.selection_title)

            with Horizontal(id=UI_IDS.models_row):
                with Vertical(id=UI_IDS.model_a_container):
                    yield Label("Модель A:", id=UI_IDS.model_a_label)
                    # Проверка на пустой список моделей
                    model_a_value = (
                        self._available_models[0] if self._available_models else None
                    )
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_a_select,
                        value=model_a_value,
                    )

                with Vertical(id=UI_IDS.model_b_container):
                    yield Label("Модель B:", id=UI_IDS.model_b_label)
                    # Проверка на достаточное количество моделей
                    if len(self._available_models) > 1:
                        model_b_value = self._available_models[1]
                    elif self._available_models:
                        model_b_value = self._available_models[0]
                    else:
                        model_b_value = None
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_b_select,
                        value=model_b_value,
                    )

            with Horizontal(id=UI_IDS.selection_buttons):
                yield Button("Начать диалог", id=UI_IDS.start_btn, variant="primary")
                yield Button("Отмена", id=UI_IDS.cancel_btn, variant="error")

    def action_cancel(self) -> None:
        """Обработать нажатие Escape для отмены выбора модели."""
        self.dismiss(None)

    @on(Button.Pressed, f"#{UI_IDS.start_btn}")
    def on_start_pressed(self) -> None:
        """Обработать нажатие кнопки начала диалога."""
        model_a = self.query_one(f"#{UI_IDS.model_a_select}", Select).value
        model_b = self.query_one(f"#{UI_IDS.model_b_select}", Select).value

        if model_a == model_b:
            self.notify(
                "Выберите две разные модели!",
                title="Ошибка",
                severity="error",
            )
            return

        if model_a is Select.BLANK or model_b is Select.BLANK:
            self.notify(
                "Выберите обе модели!",
                title="Ошибка",
                severity="error",
            )
            return

        self.dismiss((model_a, model_b))

    @on(Button.Pressed, f"#{UI_IDS.cancel_btn}")
    def on_cancel_pressed(self) -> None:
        """Обработать нажатие кнопки отмены."""
        self.dismiss(None)


class TopicInputScreen(ModalScreen):
    """Модальное окно для ввода темы диалога."""

    BINDINGS = [
        Binding("escape", "cancel", "Отмена"),
        Binding("enter", "submit", "OK"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id=UI_IDS.topic_input_container):
            yield Static("Введите тему диалога:", id=UI_IDS.topic_label)
            yield Input(
                placeholder="Например: Спор о преимуществах Python перед Go",
                id=UI_IDS.topic_input,
            )
            with Horizontal(id=UI_IDS.topic_buttons):
                yield Button("Начать", id=UI_IDS.topic_start_btn, variant="primary")
                yield Button("Отмена", id=UI_IDS.topic_cancel_btn, variant="error")

    def action_submit(self) -> None:
        """Обработать нажатие Enter для подтверждения темы."""
        self._submit_topic()

    def action_cancel(self) -> None:
        """Обработать нажатие Escape для отмены ввода темы."""
        self.dismiss(None)

    @on(Button.Pressed, f"#{UI_IDS.topic_start_btn}")
    def on_start_pressed(self) -> None:
        """Обработать нажатие кнопки начала диалога."""
        self._submit_topic()

    @on(Button.Pressed, f"#{UI_IDS.topic_cancel_btn}")
    def on_cancel_pressed(self) -> None:
        """Обработать нажатие кнопки отмены."""
        self.dismiss(None)

    def _submit_topic(self) -> None:
        topic_input = self.query_one(f"#{UI_IDS.topic_input}", Input)
        topic = topic_input.value.strip()

        if not topic:
            self.notify(
                "Введите тему диалога!",
                title="Ошибка",
                severity="error",
            )
            return

        self.dismiss(topic)


class DialogueApp(App):
    """Основное TUI приложение для диалога ИИ-моделей.

    Содержит только UI-логику. Бизнес-логика вынесена в DialogueService.
    """

    CSS = MAIN_CSS

    BINDINGS = [
        Binding("ctrl+q", "quit", "Выход", priority=True),
        Binding("ctrl+p", "toggle_pause", "Пауза/Старт"),
        Binding("ctrl+r", "clear_log", "Очистить"),
        Binding("ctrl+c", "", ""),  # Отключаем стандартное поведение
    ]

    TITLE = "AI Dialogue TUI"
    sub_title = "Диалог двух ИИ-моделей через Ollama"

    def __init__(self, config: Config | None = None) -> None:
        """
        Инициализация приложения.

        Args:
            config: Опциональная конфигурация для dependency injection.
        """
        super().__init__()
        self._config = config or Config()
        self._client: OllamaClient | None = None
        self._controller: DialogueController | None = None
        self._dialogue_task: asyncio.Task[None] | None = None
        self._models: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id=UI_IDS.main_container):
            # Статус бар
            with Container(id=UI_IDS.status_bar):
                with Horizontal(id=UI_IDS.status_row):
                    yield Label("Статус: ", id=UI_IDS.status_label)
                    yield Label("Ожидание...", id=UI_IDS.status_value)

            # Лог диалога
            yield RichLog(id=UI_IDS.dialogue_log, highlight=True, markup=True)

            # Панель управления
            with Container(id=UI_IDS.controls_bar):
                with Horizontal(id=UI_IDS.controls_row):
                    yield Button("▶ Старт", id=UI_IDS.start_btn, variant="success")
                    yield Button("⏸ Пауза", id=UI_IDS.pause_btn, variant="warning")
                    yield Button("🗑 Очистить", id=UI_IDS.clear_btn, variant="default")
                    yield Button("✕ Выход", id=UI_IDS.exit_btn, variant="error")

        yield Footer()

    def _on_ui_state_changed(self, state: UIState) -> None:
        """
        Обработчик изменения состояния UI.

        Args:
            state: Новое состояние UI от контроллера.
        """
        try:
            status_label = self.query_one("#status-value", Label)
            status_label.update(
                f"[{state.status_style}]{state.status_text}[/{state.status_style}]"
            )
        except Exception:  # pylint: disable=broad-exception-caught
            # Игнорируем ошибки если UI ещё не готов
            pass

    async def on_mount(self) -> None:
        """Инициализация при запуске приложения."""
        try:
            # Валидация URL перед использованием
            if not validate_ollama_url(self._config.ollama_host):
                raise ValueError(f"Некорректный URL Ollama: {self._config.ollama_host}")

            self._client = OllamaClient(host=self._config.ollama_host)

            # Получаем список моделей
            self._models = await self._client.list_models()

            if not self._models:
                self.notify(
                    "Не найдено установленных моделей Ollama!\n"
                    "Установите модель командой: ollama pull llama3",
                    title="Ошибка",
                    severity="error",
                    timeout=10,
                )
                self.query_one("#status-value", Label).update("[red]Нет моделей[/red]")
                return

            # Показываем окно выбора моделей
            def on_models_selected(result: tuple[str, str] | None) -> None:
                if result is None:
                    self.exit(1)
                    return

                model_a, model_b = result
                self._setup_conversation(model_a, model_b)

            # Показываем модальное окно выбора моделей
            self.push_screen(
                ModelSelectionScreen(self._models),
                callback=on_models_selected,
            )

        except OllamaError:
            # Не раскрываем детали ошибки пользователю
            self.notify(
                "Не удалось подключиться к Ollama. Проверьте что сервис запущен.",
                title="Ошибка подключения",
                severity="error",
                timeout=10,
            )
            self.query_one("#status-value", Label).update(
                "[red]Ошибка подключения[/red]"
            )
        except ValueError as e:
            self.notify(
                f"Ошибка конфигурации: {e}",
                title="Ошибка",
                severity="error",
            )
            self.query_one("#status-value", Label).update(
                "[red]Ошибка конфигурации[/red]"
            )
        except (RuntimeError, SystemError):
            # Не раскрываем детали внутренней ошибки
            self.notify(
                "Произошла непредвиденная ошибка при запуске",
                title="Ошибка",
                severity="error",
            )
            self.query_one("#status-value", Label).update(
                "[red]Неизвестная ошибка[/red]"
            )

    def _setup_conversation(self, model_a: str, model_b: str) -> None:
        """
        Настроить диалог после выбора моделей.

        Args:
            model_a: Название первой модели.
            model_b: Название второй модели.
        """

        def on_topic_entered(topic: str | None) -> None:
            if topic is None:
                self.exit(1)
                return

            # Санитизация темы перед использованием
            sanitized_topic = sanitize_topic(topic)

            # Создаём объекты с dependency injection
            conversation = Conversation(
                model_a=model_a,
                model_b=model_b,
                topic=sanitized_topic,
            )
            service = DialogueService(
                conversation=conversation,
                provider=self._client,
                config=self._config,
            )
            self._controller = DialogueController(
                service=service,
                on_state_changed=self._on_ui_state_changed,
            )

            # Обновляем заголовок и статус
            self.sub_title = f"{model_a} ↔ {model_b} | Тема: {sanitized_topic}"
            self._on_ui_state_changed(
                UIState(status_text="Готов к запуску", status_style="green")
            )

            # Логируем начало
            log = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
            log.write(
                f"[bold]=== Диалог начат ===[/bold]\n"
                f"[bold]Модель A:[/bold] [{MESSAGE_STYLES.model_a}]"
                f"{model_a}[/{MESSAGE_STYLES.model_a}]\n"
                f"[bold]Модель B:[/bold] [{MESSAGE_STYLES.model_b}]"
                f"{model_b}[/{MESSAGE_STYLES.model_b}]\n"
                f"[bold]Тема:[/bold] {sanitized_topic}\n"
                f"[dim]Нажмите 'Старт' для начала диалога[/dim]"
            )

        # Показываем окно ввода темы
        self.push_screen(TopicInputScreen(), callback=on_topic_entered)

    @on(Button.Pressed, f"#{UI_IDS.start_btn}")
    def on_start_pressed(self) -> None:
        """Запуск диалога."""
        if self._controller is None:
            self.notify(
                "Сначала выберите модели и тему!",
                title="Ошибка",
                severity="error",
            )
            return

        if not self._controller.handle_start():
            # Ошибка уже обработана в контроллере
            return

        # Запускаем основной цикл диалога
        self._dialogue_task = asyncio.create_task(self._run_dialogue())
        self.notify("Диалог запущен!", title="Старт", severity="information")

    @on(Button.Pressed, f"#{UI_IDS.pause_btn}")
    def on_pause_pressed(self) -> None:
        """Пауза/продолжение диалога."""
        if self._controller is None:
            self.notify(
                "Диалог ещё не настроен!",
                title="Ошибка",
                severity="error",
            )
            return
        self._controller.handle_pause()

    @on(Button.Pressed, f"#{UI_IDS.clear_btn}")
    def on_clear_pressed(self) -> None:
        """Очистка лога и контекстов."""
        if self._controller:
            self._controller.handle_clear()

        log = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
        log.clear()
        log.write("[dim]История очищена[/dim]")

        self.notify("История очищена!", title="Очистка", severity="information")

    @on(Button.Pressed, f"#{UI_IDS.exit_btn}")
    def on_exit_pressed(self) -> None:
        """Выход из приложения."""
        self.exit()

    def action_toggle_pause(self) -> None:
        """Переключить паузу."""
        if self._controller:
            self._controller.handle_pause()

    def action_clear_log(self) -> None:
        """Очистить лог (горячая клавиша)."""
        self.on_clear_pressed()

    def _get_model_info_and_style(self, service) -> tuple[str, str]:
        """Получить информацию о текущей модели и соответствующий стиль."""
        model_name = service.conversation.get_current_model_name()
        model_id = service.conversation.current_turn
        style = MESSAGE_STYLES.model_a if model_id == "A" else MESSAGE_STYLES.model_b
        return model_name, style

    async def _run_dialogue(self) -> None:
        """Основной цикл диалога."""
        if self._controller is None:
            return

        log = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
        service = self._controller.service

        try:
            while service.is_running and not service.is_paused:
                # Проверка на отмену задачи
                if asyncio.current_task() and asyncio.current_task().cancelled():
                    break

                # Получаем информацию о текущей модели
                model_name, style = self._get_model_info_and_style(service)

                # Обновляем статус для нового хода
                self._controller.update_for_turn(model_name, style)

                try:
                    # Выполняем цикл диалога
                    result: (
                        DialogueTurnResult | None
                    ) = await service.run_dialogue_cycle()

                    if result:
                        # Форматируем и выводим сообщение с санитизацией
                        formatted_response = sanitize_response_for_display(
                            result.response
                        )

                        message = (
                            f"\n[{style}]Ход {service.turn_count}: {
                                result.model_name
                            }[/]\n"
                            f"  {formatted_response}"
                        )
                        self.call_from_thread(log.write, message)

                except OllamaError:
                    error_msg = f"\n[{MESSAGE_STYLES.error}]Ошибка ({model_name})[/]"
                    self.call_from_thread(log.write, error_msg)
                    self._controller.update_for_error(model_name)
                    self.notify(
                        "Ошибка генерации ответа",
                        title="Ошибка",
                        severity="error",
                    )
                    raise  # Пробрасываем ошибку дальше для обработки

                # Пауза между сообщениями
                await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            # Нормальное завершение при отмене задачи
            pass
        except OllamaError:
            # Ошибка уже была залогирована
            pass
        except (RuntimeError, SystemError, OSError):
            self.call_from_thread(
                log.write,
                f"\n[{MESSAGE_STYLES.error}]Критическая ошибка[/]",
            )
        finally:
            self._controller.handle_stop()

    async def on_unmount(self) -> None:
        """Очистка при закрытии приложения."""
        try:
            # Отменяем задачу диалога
            if self._dialogue_task and not self._dialogue_task.done():
                self._dialogue_task.cancel()
                try:
                    await self._dialogue_task
                except asyncio.CancelledError:
                    pass

            # Очищаем контроллер и клиент
            if self._controller:
                await self._controller.cleanup()
            elif self._client:
                await self._client.close()

        except (aiohttp.ClientError, asyncio.TimeoutError, OSError):
            # Игнорируем ошибки при очистке
            pass
