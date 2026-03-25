"""TUI приложение для диалога двух ИИ-моделей.

Этот модуль содержит только UI-компоненты и обработчики событий.
Бизнес-логика вынесена в сервисный слой (services/dialogue_service.py).
"""

from __future__ import annotations

import asyncio
import logging

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

from controllers.dialogue_controller import DialogueController, UIState
from models.config import Config
from models.conversation import Conversation
from models.provider import ModelProvider, ProviderError
from services.dialogue_service import DialogueService, DialogueTurnResult
from tui.sanitizer import sanitize_response_for_display, sanitize_topic
from tui.styles import (
    MESSAGE_STYLES,
    UI_IDS,
    generate_main_css,
)

# Константа таймаута для уведомлений
DEFAULT_NOTIFY_TIMEOUT: int = 10

# CSS генерируется из централизованных констант
CSS = generate_main_css()

log = logging.getLogger(__name__)


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
                    model_a_value = self._get_model_value(0)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_a_select,
                        value=model_a_value,
                    )

                with Vertical(id=UI_IDS.model_b_container):
                    yield Label("Модель B:", id=UI_IDS.model_b_label)
                    model_b_value = self._get_model_value(1)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_b_select,
                        value=model_b_value,
                    )

            with Horizontal(id=UI_IDS.selection_buttons):
                yield Button("Начать диалог", id=UI_IDS.start_btn, variant="primary")
                yield Button("Отмена", id=UI_IDS.cancel_btn, variant="error")

    def _get_model_value(self, index: int) -> str | None:
        """
        Получить значение модели для селектора по индексу.

        Args:
            index: Индекс модели в списке.

        Returns:
            Название модели или None если список пуст.
        """
        if not self._available_models:
            return None
        if index < len(self._available_models):
            return self._available_models[index]
        return self._available_models[-1]

    def action_cancel(self) -> None:
        """Обработать нажатие Escape для отмены выбора модели."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Обработать нажатие кнопки.

        Args:
            event: Событие нажатия кнопки.
        """
        button_id = event.button.id
        if button_id == UI_IDS.start_btn:
            self._on_start_pressed()
        elif button_id == UI_IDS.cancel_btn:
            self.dismiss(None)

    def _on_start_pressed(self) -> None:
        """Обработать нажатие кнопки начала диалога."""
        model_a = self.query_one(f"#{UI_IDS.model_a_select}", Select).value
        model_b = self.query_one(f"#{UI_IDS.model_b_select}", Select).value

        if model_a == model_b:
            self.notify(
                "Выберите две разные модели!",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        if model_a is Select.BLANK or model_b is Select.BLANK:
            self.notify(
                "Выберите обе модели!",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        self.dismiss((model_a, model_b))


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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Обработать нажатие кнопки.

        Args:
            event: Событие нажатия кнопки.
        """
        button_id = event.button.id
        if button_id == UI_IDS.topic_start_btn:
            self._submit_topic()
        elif button_id == UI_IDS.topic_cancel_btn:
            self.dismiss(None)

    def _submit_topic(self) -> None:
        topic_input = self.query_one(f"#{UI_IDS.topic_input}", Input)
        topic = topic_input.value.strip()

        if not topic:
            self.notify(
                "Введите тему диалога!",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        self.dismiss(topic)


class DialogueApp(App):
    """Основное TUI приложение для диалога ИИ-моделей.

    Содержит только UI-логику. Бизнес-логика вынесена в DialogueService.
    """

    CSS = CSS

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
        self._client: ModelProvider | None = None
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
        except (LookupError, RuntimeError):
            log.exception("Ошибка при обновлении UI состояния")

    async def on_mount(self) -> None:
        """Инициализация при запуске приложения."""
        try:
            # Config уже валидирован при инициализации, создаем клиент
            from models.ollama_client import (
                OllamaClient,  # pylint: disable=import-outside-toplevel
            )

            self._client = OllamaClient(host=self._config.ollama_host)

            # Получаем список моделей
            self._models = await self._client.list_models()

            if not self._models:
                self.notify(
                    "Не найдено установленных моделей Ollama!\n"
                    "Установите модель командой: ollama pull llama3",
                    title="Ошибка",
                    severity="error",
                    timeout=DEFAULT_NOTIFY_TIMEOUT,
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

        except ProviderError:
            # Не раскрываем детали ошибки пользователю
            self.notify(
                "Не удалось подключиться к Ollama. Проверьте что сервис запущен.",
                title="Ошибка подключения",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            self.query_one("#status-value", Label).update(
                "[red]Ошибка подключения[/red]"
            )
        except ValueError as e:
            self.notify(
                f"Ошибка конфигурации: {e}",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            self.query_one("#status-value", Label).update(
                "[red]Ошибка конфигурации[/red]"
            )
        except (RuntimeError, SystemError) as e:
            # Не раскрываем детали внутренней ошибки
            log.exception("Внутренняя ошибка при запуске: %s", e)
            self.notify(
                "Произошла непредвиденная ошибка при запуске",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
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
            dialog_log = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
            dialog_log.write(
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
                timeout=DEFAULT_NOTIFY_TIMEOUT,
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
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return
        self._controller.handle_pause()

    @on(Button.Pressed, f"#{UI_IDS.clear_btn}")
    def on_clear_pressed(self) -> None:
        """Очистка лога и контекстов."""
        if self._controller:
            self._controller.handle_clear()

        dialog_log = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
        dialog_log.clear()
        dialog_log.write("[dim]История очищена[/dim]")

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

    def _get_model_info_and_style(self, service: DialogueService) -> tuple[str, str]:
        """Получить информацию о текущей модели и соответствующий стиль."""
        return service.get_model_info_and_style()

    async def _run_dialogue(self) -> None:
        """Основной цикл диалога."""
        if self._controller is None:
            return

        service = self._controller.service

        try:
            while service.is_running and not service.is_paused:
                if self._is_task_cancelled():
                    break

                model_name, style = self._get_model_info_and_style(service)
                self._controller.update_for_turn(model_name, style)

                try:
                    await self._process_dialogue_turn(service, model_name, style)
                except ProviderError:
                    self._handle_dialogue_error(model_name)
                    raise

                await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            log.debug("Диалог отменён")
        except ProviderError:
            log.warning("Ошибка провайдера в цикле диалога")
        except (RuntimeError, SystemError, OSError) as e:
            self._handle_critical_error(e)
        finally:
            self._controller.handle_stop()

    def _is_task_cancelled(self) -> bool:
        """Проверить отменена ли текущая задача."""
        current_task = asyncio.current_task()
        return current_task is not None and current_task.is_cancelled()

    async def _process_dialogue_turn(  # pylint: disable=unused-argument
        self,
        service: DialogueService,
        model_name: str,
        style: str,
    ) -> DialogueTurnResult | None:
        """Обработать один ход диалога и вывести результат."""
        result = await service.run_dialogue_cycle()

        if result:
            formatted_response = sanitize_response_for_display(result.response)
            message = (
                f"\n[{style}]Ход {service.turn_count}: {result.model_name}[/]\n"
                f"  {formatted_response}"
            )
            self.call_from_thread(log.write, message)

        return result

    def _handle_dialogue_error(self, model_name: str) -> None:
        """Обработать ошибку генерации ответа."""
        error_msg = f"\n[{MESSAGE_STYLES.error}]Ошибка ({model_name})[/]"
        self.call_from_thread(log.write, error_msg)
        self._controller.update_for_error(model_name)
        self.notify(
            "Ошибка генерации ответа",
            title="Ошибка",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT,
        )

    def _handle_critical_error(self, e: Exception) -> None:
        """Обработать критическую ошибку в цикле диалога."""
        log.exception("Критическая ошибка в цикле диалога: %s", e)
        self.call_from_thread(
            log.write,
            f"\n[{MESSAGE_STYLES.error}]Критическая ошибка[/]",
        )

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

        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            log.warning("Ошибка при очистке ресурсов: %s", e)
