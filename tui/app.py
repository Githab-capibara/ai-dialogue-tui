"""TUI приложение для диалога двух ИИ-моделей.

Этот модуль содержит только UI-компоненты и обработчики событий.
Бизнес-логика вынесена в сервисный слой (services/dialogue_service.py).
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, ClassVar

import aiohttp
from textual import on
from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
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
from models.ollama_client import OllamaClient
from models.provider import (
    ModelProvider,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from services.dialogue_service import DialogueService, DialogueTurnResult
from services.model_style_mapper import ModelStyleMapper
from tui.constants import MESSAGE_STYLES, UI_IDS
from tui.sanitizer import sanitize_response_for_display, sanitize_topic
from tui.styles import generate_main_css

if TYPE_CHECKING:
    from collections.abc import Callable

# Константа таймаута для уведомлений
DEFAULT_NOTIFY_TIMEOUT: int = 10

# =============================================================================
# call_from_thread vs call_after_refresh в Textual
# =============================================================================
# call_from_thread: используется для threading.Thread
# call_after_refresh: используется в asyncio.create_task, async def
#
# В этом модуле все методы работают в асинхронном контексте,
# поэтому используется call_after_refresh, а НЕ call_from_thread!
# =============================================================================

# CSS генерируется из централизованных констант
CSS = generate_main_css()

log = logging.getLogger(__name__)


class ModelSelectionScreen(ModalScreen[tuple[str, str] | None]):
    """Модальное окно для выбора двух моделей."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Отмена"),
    ]

    def __init__(self, models: list[str], *args: Any, **kwargs: Any) -> None:
        """Initialize the model selection screen.

        Args:
            models: List of available model names.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self._available_models = models

    def compose(self) -> ComposeResult:
        """Compose the model selection UI."""
        with Container(id=UI_IDS.model_selection_container):
            yield Static("Выберите две модели для диалога", id=UI_IDS.selection_title)

            with Vertical(id=UI_IDS.models_row):
                with Horizontal(id=UI_IDS.model_a_container):
                    yield Label("Модель A:", id=UI_IDS.model_a_label)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_a_select,
                        value=self._get_model_value(0),
                    )

                with Horizontal(id=UI_IDS.model_b_container):
                    yield Label("Модель B:", id=UI_IDS.model_b_label)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_b_select,
                        value=self._get_model_value(1),
                    )

            with Horizontal(id=UI_IDS.selection_buttons):
                yield Button("Начать диалог", id=UI_IDS.start_btn, variant="primary")
                yield Button("Отмена", id=UI_IDS.cancel_btn, variant="error")

    def _get_model_value(self, index: int) -> str | None:
        """Получить значение модели для селектора по индексу.

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
        """Обработать нажатие кнопки.

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
        model_a_select = self.query_one(f"#{UI_IDS.model_a_select}", Select)
        model_b_select = self.query_one(f"#{UI_IDS.model_b_select}", Select)
        model_a_value = model_a_select.value
        model_b_value = model_b_select.value

        if model_a_value is Select.BLANK or model_b_value is Select.BLANK:
            self.notify(
                "Выберите обе модели!",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        model_a: str = model_a_value  # type: ignore[assignment]
        model_b: str = model_b_value  # type: ignore[assignment]

        if model_a == model_b:
            self.notify(
                "Выберите две разные модели!",
                title="Ошибка",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        self.dismiss((model_a, model_b))


class TopicInputScreen(ModalScreen[str | None]):
    """Модальное окно для ввода темы диалога."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Отмена"),
        Binding("enter", "submit", "OK"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id=UI_IDS.topic_input_container), Vertical(id=UI_IDS.topic_input_content):
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
        """Обработать нажатие кнопки.

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


class DialogueApp(App[None]):
    """Основное TUI приложение для диалога ИИ-моделей.

    Содержит только UI-логику. Бизнес-логика вынесена в DialogueService.
    """

    CSS = CSS

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("ctrl+q", "quit", "Выход", priority=True),
        Binding("ctrl+p", "toggle_pause", "Пауза/Старт"),
        Binding("ctrl+r", "clear_log", "Очистить"),
    ]

    TITLE = "AI Dialogue TUI"
    sub_title = reactive("Диалог двух ИИ-моделей через Ollama")

    def __init__(
        self,
        config: Config | None = None,
        provider_factory: Callable[[], ModelProvider] | None = None,
    ) -> None:
        """Инициализация приложения.

        Args:
            config: Опциональная конфигурация для dependency injection.
            provider_factory: Фабрика для создания ModelProvider.
                              Если не указана, используется OllamaClient по умолчанию.

        """
        super().__init__()
        self._config = config or Config()
        self._provider_factory = provider_factory or (lambda: OllamaClient(host=self._config.ollama_host))
        self._client: ModelProvider | None = None
        self._controller: DialogueController | None = None
        self._dialogue_task: asyncio.Task[None] | None = None
        self._models: list[str] = []
        # Кэшируем style_mapper для производительности
        self._style_mapper = ModelStyleMapper()
        # Флаг для идемпотентности on_unmount
        self._cleanup_done = False

    def compose(self) -> ComposeResult:
        """Compose the main application UI."""
        yield Header()

        with Container(id=UI_IDS.main_container):
            # Статус бар
            with Container(id=UI_IDS.status_bar), Horizontal(id=UI_IDS.status_row):
                yield Label("Статус: ", id=UI_IDS.status_label)
                yield Label("Ожидание...", id=UI_IDS.status_value)

            # Лог диалога
            yield RichLog(id=UI_IDS.dialogue_log, highlight=True, markup=True)

            # Панель управления
            with Container(id=UI_IDS.controls_bar), Horizontal(id=UI_IDS.controls_row):
                yield Button("▶ Старт", id=UI_IDS.start_btn, variant="success")
                yield Button("⏸ Пауза", id=UI_IDS.pause_btn, variant="warning")
                yield Button("🗑 Очистить", id=UI_IDS.clear_btn, variant="default")
                yield Button("✕ Выход", id=UI_IDS.exit_btn, variant="error")

        yield Footer()

    def _on_ui_state_changed(self, state: UIState) -> None:
        """Обработчик изменения состояния UI.

        Args:
            state: Новое состояние UI от контроллера.

        """
        try:
            status_label: Label = self.query_one("#status-value", Label)
            style_tag = f"[{state.status_style}]{state.status_text}[/{state.status_style}]"
            status_label.update(style_tag)
        except (NoMatches, ScreenStackError):
            log.debug("Элемент #status-value недоступен для обновления")
        except LookupError:
            log.exception("LookupError при обновлении UI состояния")
        except RuntimeError:
            log.exception("RuntimeError при обновлении UI состояния")
        except Exception as e:
            log.exception("Ошибка при обновлении UI состояния: %s", e)

    async def on_mount(self) -> None:
        """Инициализация при запуске приложения."""
        try:
            self._client = self._provider_factory()
            self._models = await self._client.list_models()

            if not self._models:
                self._notify_error("Не найдено установленных моделей Ollama!")
                self._safe_update_status("[red]Нет моделей[/red]")
                return

            self.push_screen(
                ModelSelectionScreen(self._models),
                callback=self._on_models_selected,
            )

        except ProviderConnectionError:
            self._handle_connection_error()
        except ProviderGenerationError:
            self._handle_generation_error()
        except ValueError as exc:
            self._handle_config_error(exc)
        except aiohttp.ClientError:
            self._handle_network_error()
        except asyncio.TimeoutError:
            self._handle_timeout_error()
        except (RuntimeError, SystemError):
            self._handle_internal_error()

    def _on_models_selected(self, result: tuple[str, str] | None) -> None:
        """Обработать выбор моделей."""
        if result is None:
            self.exit()
            return
        model_a, model_b = result
        self._setup_conversation(model_a, model_b)

    def _notify_error(self, message: str) -> None:
        """Уведомить об ошибке."""
        self.notify(
            message,
            title="Ошибка",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT,
        )

    def _handle_connection_error(self) -> None:
        """Обработать ошибку подключения."""
        log.exception("Connection error to Ollama")
        self._notify_error("Не удалось подключиться к Ollama. Проверьте что сервис запущен.")
        self._safe_update_status("[red]Ошибка подключения[/red]")

    def _handle_generation_error(self) -> None:
        """Обработать ошибку генерации."""
        log.exception("Generation error while getting models")
        self._notify_error("Ошибка генерации ответа. Проверьте модель...")
        self._safe_update_status("[red]Ошибка подключения[/red]")

    def _handle_config_error(self, exc: ValueError) -> None:
        """Обработать ошибку конфигурации."""
        log.exception("Configuration validation error")
        self._notify_error(f"Configuration error: {exc}")
        self._safe_update_status("[red]Config error[/red]")

    def _handle_network_error(self) -> None:
        """Обработать сетевую ошибку."""
        log.exception("HTTP client error at startup")
        self._notify_error("Ошибка сетевого подключения")
        self._safe_update_status("[red]Ошибка подключения[/red]")

    def _handle_timeout_error(self) -> None:
        """Обработать таймаут."""
        log.exception("Таймаут при запуске")
        self._notify_error("Превышено время ожидания подключения")
        self._safe_update_status("[red]Таймаут[/red]")

    def _handle_internal_error(self) -> None:
        """Обработать внутреннюю ошибку."""
        log.exception("Internal error at startup")
        self._notify_error("Произошла непредвиденная ошибка при запуске")
        self._safe_update_status("[red]Неизвестная ошибка[/red]")

    def _safe_update_status(self, status: str) -> None:
        """Безопасно обновить статус с обработкой ошибок."""
        try:
            status_label = self.query_one("#status-value", Label)
            status_label.update(status)
        except (NoMatches, LookupError, RuntimeError):
            log.warning("Не удалось обновить статус")

    def _setup_conversation(self, model_a: str, model_b: str) -> None:
        """Настроить диалог после выбора моделей.

        Args:
            model_a: Название первой модели.
            model_b: Название второй модели.

        """

        def on_topic_entered(topic: str | None) -> None:
            if topic is None:
                self.exit()
                return

            # Санитизация темы перед использованием
            sanitized_topic = sanitize_topic(topic)

            # Форматируем системный промпт
            system_prompt = self._config.default_system_prompt.format(topic=sanitized_topic)

            if self._client is None:
                log.error("Client not initialized")
                return
            conversation = Conversation(
                model_a=model_a,
                model_b=model_b,
                topic=sanitized_topic,
                system_prompt=system_prompt,
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

            # Обновляем заголовок и статус через call_after_refresh
            # чтобы UI успел обновиться после закрытия модального окна
            def _finalize_setup() -> None:
                self.sub_title = f"{model_a} ↔ {model_b} | Тема: {sanitized_topic}"
                ready_state = UIState(status_text="Готов к запуску", status_style="green")
                self._on_ui_state_changed(ready_state)

                # Логируем начало с обработкой ошибок
                try:
                    dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
                    dialog_log.write(
                        f"[bold]=== Диалог начат ===[/bold]\n"
                        f"[bold]Модель A:[/bold] [{MESSAGE_STYLES.model_a}]"
                        f"{model_a}[/{MESSAGE_STYLES.model_a}]\n"
                        f"[bold]Модель B:[/bold] [{MESSAGE_STYLES.model_b}]"
                        f"{model_b}[/{MESSAGE_STYLES.model_b}]\n"
                        f"[bold]Тема:[/bold] {sanitized_topic}\n"
                        "[dim]Нажмите 'Старт' для начала диалога[/dim]",
                    )
                except (NoMatches, LookupError, RuntimeError):
                    log.warning("Не удалось записать в лог при инициализации")

            self.call_after_refresh(_finalize_setup)

        self.push_screen(TopicInputScreen(), callback=on_topic_entered)

    @on(Button.Pressed, f"#{UI_IDS.start_btn}")
    def on_start_pressed(self) -> None:
        """Запуск диалога."""
        if self._controller is None:
            log.error("Controller not initialized")
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
            return
        self._controller.handle_pause()

    @on(Button.Pressed, f"#{UI_IDS.clear_btn}")
    def on_clear_pressed(self) -> None:
        """Очистка лога и контекстов."""
        if self._controller:
            self._controller.handle_clear()

        dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
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

    async def _run_dialogue(self) -> None:
        """Основной цикл диалога."""
        if self._controller is None or self._client is None:
            log.error("Controller or client not initialized")
            return

        service = self._controller.service
        # Используем кэшированный style_mapper из __init__
        style_mapper = self._style_mapper

        try:
            while service.is_running and not service.is_paused:
                if self._is_task_cancelled():
                    break

                model_id = service.conversation.current_turn
                model_name = service.conversation.get_current_model_name()
                style_info = style_mapper.get_style_info(model_id, model_name)
                self._controller.update_for_turn(style_info.model_name, style_info.style_id)

                try:
                    await self._process_dialogue_turn(service, style_info.model_name, style_info.style_id)
                except ProviderError as e:
                    # Унифицированная обработка всех ProviderError
                    log.warning("Ошибка провайдера в цикле диалога: %s", e)
                    self._handle_dialogue_error(style_info.model_name)
                    raise

                await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            log.debug("Диалог отменён")
        except ProviderError:
            log.debug("ProviderError обработан")
        except (RuntimeError, SystemError, OSError) as e:
            self._handle_critical_error(e)
        finally:
            self._controller.handle_stop()
            if self._controller:
                await self._controller.cleanup()

    def _is_task_cancelled(self) -> bool:
        """Проверить отменена ли текущая задача."""
        current_task = asyncio.current_task()
        return current_task is not None and current_task.cancelled()

    async def _process_dialogue_turn(
        self,
        service: DialogueService,
        _model_name: str,
        style: str,
    ) -> DialogueTurnResult | None:
        """Обработать один ход диалога и вывести результат."""
        result = await service.run_dialogue_cycle()

        if result:
            formatted_response = sanitize_response_for_display(result.response)
            turn_msg = f"\n[{style}]Ход {service.turn_count}: {result.model_name}[/]\n  {formatted_response}"
            message = turn_msg
            self.call_after_refresh(self._write_to_log, message)

        return result

    def _write_to_log(self, message: str) -> None:
        """Безопасно записать сообщение в лог UI."""
        try:
            dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
            dialog_log.write(message)
        except (NoMatches, LookupError, RuntimeError):
            log.warning("Не удалось записать в лог")

    def _handle_dialogue_error(self, model_name: str) -> None:
        """Обработать ошибку генерации ответа.

        Этот метод вызывается из асинхронного контекста (_process_dialogue_turn),
        поэтому используем call_after_refresh вместо call_from_thread.
        """
        error_msg = f"\n[{MESSAGE_STYLES.error}]Ошибка ({model_name})[/]"
        # Используем call_after_refresh т.к. мы в асинхронном контексте, а не в
        # потоке
        self.call_after_refresh(self._write_to_log, error_msg)
        if self._controller:
            self._controller.update_for_error(model_name)
        self.notify(
            "Ошибка генерации ответа",
            title="Ошибка",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT,
        )

    def _handle_critical_error(self, _e: BaseException) -> None:
        """Обработать критическую ошибку в цикле диалога."""
        log.exception("Critical error in dialogue loop")
        self.call_after_refresh(
            self._write_to_log,
            f"\n[{MESSAGE_STYLES.error}]Критическая ошибка[/]",
        )

    async def on_unmount(self) -> None:
        """Очистка при закрытии приложения."""
        # Проверяем флаг для идемпотентности
        if self._cleanup_done:
            return

        try:
            self._cleanup_done = True

            # Отменяем задачу диалога
            if self._dialogue_task and not self._dialogue_task.done():
                self._dialogue_task.cancel()
                try:
                    await self._dialogue_task
                except asyncio.CancelledError:
                    pass
                finally:
                    self._dialogue_task = None

            # Очищаем контроллер и клиент
            try:
                if self._controller:
                    await self._controller.cleanup()
                elif self._client:
                    await self._client.close()
            finally:
                self._controller = None
                self._client = None

        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
            log.warning("Ошибка при очистке ресурсов: %s", e)
        except RuntimeError:
            log.exception("Unexpected error during cleanup")
