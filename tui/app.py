"""TUI application for dialogue between two AI models.

This module contains only UI components and event handlers.
Business logic is moved to the service layer (services/dialogue_service.py).
"""

from __future__ import annotations

import asyncio
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, TextIO

import aiohttp
from textual import on
from textual.app import App, ComposeResult, ScreenStackError
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, RichLog, Select, Static

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
from tui.constants import DEFAULT_NOTIFY_TIMEOUT, MESSAGE_STYLES, UI_IDS
from tui.sanitizer import sanitize_response_for_display, sanitize_topic
from tui.styles import generate_main_css

if TYPE_CHECKING:
    from collections.abc import Callable

# Компилируем regex на уровне модуля для производительности
# Паттерн для удаления текстовых markup-тегов: [bold], [/], [red], [/red], [dim], [/dim]
_LOG_CLEANUP_PATTERN = re.compile(r"\[/?[^\]]+\]")

LOG_DIR = Path("/log")
try:
    LOG_DIR.mkdir(exist_ok=True)
except PermissionError:
    LOG_DIR = Path(sys.argv[0]).parent if sys.argv else Path.cwd()
    LOG_DIR = LOG_DIR / "logs"
    LOG_DIR.mkdir(exist_ok=True)

CSS = generate_main_css()

log = logging.getLogger(__name__)


class ModelSelectionScreen(ModalScreen[tuple[str, str] | None]):
    """Modal window for selecting two models."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, models: list[str], *args: str, **kwargs: str) -> None:
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
            yield Static(
                "Select two models for dialogue",
                id=UI_IDS.selection_title,
            )

            with Vertical(id=UI_IDS.models_row):
                with Horizontal(id=UI_IDS.model_a_container):
                    yield Label("Model A:", id=UI_IDS.model_a_label)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_a_select,
                        value=self._get_model_value(0),
                    )

                with Horizontal(id=UI_IDS.model_b_container):
                    yield Label("Model B:", id=UI_IDS.model_b_label)
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id=UI_IDS.model_b_select,
                        value=self._get_model_value(1),
                    )

            with Horizontal(id=UI_IDS.selection_buttons):
                yield Button(
                    "Start Dialogue",
                    id=UI_IDS.start_btn,
                    variant="primary",
                )
                yield Button("Cancel", id=UI_IDS.cancel_btn, variant="error")

    def _get_model_value(self, index: int) -> str | None:
        """Get model value for selector by index.

        Args:
            index: Model index in list.

        Returns:
            Model name or None if list is empty.

        """
        if not self._available_models:
            return None
        if index < len(self._available_models):
            return self._available_models[index]
        return self._available_models[-1]

    def action_cancel(self) -> None:
        """Handle Escape key press to cancel selection."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button press event.

        """
        button_id = event.button.id
        if button_id == UI_IDS.start_btn:
            self._on_start_pressed()
        elif button_id == UI_IDS.cancel_btn:
            self.dismiss(None)

    def _on_start_pressed(self) -> None:
        """Handle dialogue start button press."""
        model_a_select = self.query_one(f"#{UI_IDS.model_a_select}", Select)
        model_b_select = self.query_one(f"#{UI_IDS.model_b_select}", Select)
        model_a_value = model_a_select.value
        model_b_value = model_b_select.value

        if model_a_value is Select.BLANK or model_b_value is Select.BLANK:
            self.notify(
                "Please select both models!",
                title="Error",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        if not model_a_value or not isinstance(model_a_value, str):
            self.notify(
                "Invalid model A selection!",
                title="Error",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return
        if not model_b_value or not isinstance(model_b_value, str):
            self.notify(
                "Invalid model B selection!",
                title="Error",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return
        model_a = model_a_value
        model_b = model_b_value

        if model_a == model_b:
            self.notify(
                "Please select two different models!",
                title="Error",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        self.dismiss((model_a, model_b))


class TopicInputScreen(ModalScreen[str | None]):
    """Modal window for entering dialogue topic."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "submit", "OK"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the topic input UI."""
        with (
            Container(id=UI_IDS.topic_input_container),
            Vertical(
                id=UI_IDS.topic_input_content,
            ),
        ):
            yield Static("Enter dialogue topic:", id=UI_IDS.topic_label)
            yield Input(
                placeholder="For example: Debate on Python advantages over Go",
                id=UI_IDS.topic_input,
            )
            with Horizontal(id=UI_IDS.topic_buttons):
                yield Button(
                    "Start",
                    id=UI_IDS.topic_start_btn,
                    variant="primary",
                )
                yield Button(
                    "Cancel",
                    id=UI_IDS.topic_cancel_btn,
                    variant="error",
                )

    def action_submit(self) -> None:
        """Handle Enter key press to confirm topic."""
        self._submit_topic()

    def action_cancel(self) -> None:
        """Handle Escape key press to cancel topic input."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press.

        Args:
            event: Button press event.

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
                "Please enter a topic!",
                title="Error",
                severity="error",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        self.dismiss(topic)


class DialogueApp(App[None]):
    """Main TUI application for AI model dialogue.

    Contains only UI logic. Business logic is moved to DialogueService.
    """

    CSS = CSS

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("ctrl+q", "quit", "Exit", priority=True),
        Binding("ctrl+p", "toggle_pause", "Pause/Start"),
        Binding("ctrl+r", "clear_log", "Clear"),
    ]

    TITLE = "AI Dialogue TUI"

    def __init__(
        self,
        config: Config | None = None,
        provider_factory: Callable[[], ModelProvider] | None = None,
    ) -> None:
        """Initialize application.

        Args:
            config: Optional configuration for dependency injection.
            provider_factory: Factory for creating ModelProvider.
                              If not specified, default OllamaClient is used.

        """
        super().__init__()
        self.sub_title = reactive("Dialogue between two AI models via Ollama")  # type: ignore[assignment]
        self._config = config or Config()
        self._provider_factory = provider_factory or self._create_default_provider
        self._client: ModelProvider | None = None
        self._controller: DialogueController | None = None
        self._dialogue_task: asyncio.Task[None] | None = None
        self._models: list[str] = []
        self._style_mapper = ModelStyleMapper()
        self._cleanup_done = False
        self._cleanup_lock = asyncio.Lock()
        self._dialogue_log_file: TextIO | None = None
        self._is_setup_complete = False  # Флаг для отслеживания завершения настройки

        LOG_DIR.mkdir(exist_ok=True)
        log_path = LOG_DIR / f"dialogue_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}.txt"
        self._dialogue_log_file = log_path.open("w", encoding="utf-8")

    def _create_default_provider(self) -> OllamaClient:
        """Create default Ollama provider."""
        return OllamaClient(host=self._config.ollama_host)

    def compose(self) -> ComposeResult:
        """Compose the main application UI."""
        yield Header()

        with Container(id=UI_IDS.main_container):
            # Status bar
            with (
                Container(id=UI_IDS.status_bar),
                Horizontal(
                    id=UI_IDS.status_row,
                ),
            ):
                yield Label("Status: ", id=UI_IDS.status_label)
                yield Label("Waiting...", id=UI_IDS.status_value)

            # Dialogue log
            yield RichLog(id=UI_IDS.dialogue_log, highlight=True, markup=True, wrap=True)

            # Control panel
            with (
                Container(id=UI_IDS.controls_bar),
                Horizontal(
                    id=UI_IDS.controls_row,
                ),
            ):
                yield Button("Start", id=UI_IDS.start_btn, variant="success")
                yield Button("Pause", id=UI_IDS.pause_btn, variant="warning")
                yield Button("Clear", id=UI_IDS.clear_btn, variant="default")
                yield Button("Exit", id=UI_IDS.exit_btn, variant="error")

        yield Footer()

    def _update_button_states(self) -> None:
        """Update button enabled/disabled states based on app state."""
        try:
            start_btn = self.query_one(f"#{UI_IDS.start_btn}", Button)
            pause_btn = self.query_one(f"#{UI_IDS.pause_btn}", Button)
            clear_btn = self.query_one(f"#{UI_IDS.clear_btn}", Button)

            # Start button enabled only after setup is complete
            start_btn.disabled = not self._is_setup_complete
            # Pause и Clear buttons enabled only when controller exists
            pause_btn.disabled = self._controller is None
            clear_btn.disabled = self._controller is None
        except (NoMatches, LookupError, RuntimeError):
            log.debug("Failed to update button states")

    def _on_ui_state_changed(self, state: UIState) -> None:
        """Handle UI state change.

        Args:
            state: New UI state from controller.

        """
        try:
            status_label = self.query_one("#status-value", Label)
            style_tag = f"[{state.status_style}]{state.status_text}[/{state.status_style}]"
            status_label.update(style_tag)
        except (NoMatches, ScreenStackError):
            # Элемент недоступен (модальное окно активно) - это нормально
            log.debug("Element #status-value not available for update")
        except LookupError:
            # Элемент не найден - логируем на debug уровне
            log.debug("LookupError when updating UI state - element may not exist")
        except RuntimeError:
            # RuntimeError может быть при тестировании или неинициализированном UI
            log.debug("RuntimeError when updating UI state - UI may not be mounted")
        except Exception:
            # Все прочие ошибки также на debug уровне
            log.debug("Unexpected error when updating UI state")

    async def on_mount(self) -> None:
        """Initialize on application start."""
        try:
            self._client = self._provider_factory()
            self._models = await self._client.list_models()

            if not self._models:
                self._notify_error("No Ollama models found!")
                self._safe_update_status("[red]No models[/red]")
                return

            self.push_screen(
                ModelSelectionScreen(self._models),
                callback=self._on_models_selected,
            )

        except ProviderConnectionError:
            self._handle_startup_error(
                "Connection error",
                "Failed to connect to Ollama. Check that service is running.",
            )
        except ProviderGenerationError:
            self._handle_startup_error(
                "Generation error",
                "Generation response error. Check the model...",
            )
        except ValueError as exc:
            self._handle_startup_error(
                "Config error",
                f"Configuration error: {exc}",
                exc,
            )
        except aiohttp.ClientError:
            self._handle_startup_error(
                "Network error",
                "Network connection error",
            )
        except TimeoutError:
            self._handle_startup_error(
                "Timeout",
                "Connection timeout exceeded",
            )
        except (RuntimeError, SystemError):
            self._handle_startup_error(
                "Internal error",
                "An unexpected error occurred at startup",
            )

    def _on_models_selected(self, result: tuple[str, str] | None) -> None:
        """Handle model selection."""
        if result is None:
            self.exit()
            return
        model_a, model_b = result
        self._setup_conversation(model_a, model_b)

    def _notify_error(self, message: str) -> None:
        """Notify about error."""
        self.notify(
            message,
            title="Error",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT,
        )

    def _handle_startup_error(
        self,
        error_type: str,
        message: str,
        exc: BaseException | None = None,
    ) -> None:
        """Handle startup error with consistent logging and UI updates.

        Args:
            error_type: Type of error for logging.
            message: User-facing error message.
            exc: Optional exception for logging details.

        """
        if exc is not None:
            log.exception("%s: %s", error_type, exc)
        else:
            log.exception(error_type)
        self._notify_error(message)
        self._safe_update_status(f"[red]{error_type}[/red]")

    def _safe_update_status(self, status: str) -> None:
        """Safely update status with error handling."""
        try:
            status_label = self.query_one("#status-value", Label)
            status_label.update(status)
        except (NoMatches, LookupError, RuntimeError):
            log.warning("Failed to update status")

    def _setup_conversation(self, model_a: str, model_b: str) -> None:
        """Set up dialogue after model selection.

        Args:
            model_a: First model name.
            model_b: Second model name.

        """

        def on_topic_entered(topic: str | None) -> None:
            if topic is None:
                self.exit()
                return

            # Sanitize topic before use
            sanitized_topic = sanitize_topic(topic)

            # Format system prompt
            system_prompt = self._config.default_system_prompt.format(
                topic=sanitized_topic,
            )

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

            # Update title and status via call_after_refresh
            # so UI has time to update after modal closes
            def _finalize_setup() -> None:
                self._is_setup_complete = True  # Устанавливаем флаг после завершения настройки
                self.sub_title = f"{model_a} <-> {model_b} | Topic: {sanitized_topic}"
                ready_state = UIState(
                    status_text="Ready to start",
                    status_style="green",
                )
                self._on_ui_state_changed(ready_state)

                # Обновляем состояние кнопок после завершения настройки
                self._update_button_states()

                # Log initialization with error handling
                try:
                    dialog_log: RichLog = self.query_one(
                        f"#{UI_IDS.dialogue_log}",
                        RichLog,
                    )
                    dialog_log.write(
                        f"[bold]=== Dialogue started ===[/bold]\n"
                        f"[bold]Model A:[/bold] [{MESSAGE_STYLES.model_a}]"
                        f"{model_a}[/{MESSAGE_STYLES.model_a}]\n"
                        f"[bold]Model B:[/bold] [{MESSAGE_STYLES.model_b}]"
                        f"{model_b}[/{MESSAGE_STYLES.model_b}]\n"
                        f"[bold]Topic:[/bold] {sanitized_topic}\n"
                        "[dim]Press 'Start' to begin dialogue[/dim]",
                    )
                except (NoMatches, LookupError, RuntimeError):
                    log.warning("Failed to write to log during initialization")

            self.call_after_refresh(_finalize_setup)

        self.push_screen(TopicInputScreen(), callback=on_topic_entered)

    @on(Button.Pressed, f"#{UI_IDS.start_btn}")
    def on_start_pressed(self) -> None:
        """Start dialogue."""
        # Проверяем флаг завершения настройки
        if not self._is_setup_complete or self._controller is None:
            log.warning("Start pressed before setup complete")
            self.notify(
                "Please wait for model selection and topic input to complete!",
                title="Not Ready",
                severity="warning",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        # Проверяем, что предыдущая задача завершена или не запущена
        if self._dialogue_task is not None and not self._dialogue_task.done():
            log.warning("Dialogue task already running")
            self.notify(
                "Dialogue is already running!",
                title="Already Running",
                severity="warning",
                timeout=DEFAULT_NOTIFY_TIMEOUT,
            )
            return

        if not self._controller.handle_start():
            # Error already handled in controller
            return

        # Start main dialogue loop
        self._dialogue_task = asyncio.create_task(self._run_dialogue())
        self.notify("Dialogue started!", title="Start", severity="information")

    @on(Button.Pressed, f"#{UI_IDS.pause_btn}")
    def on_pause_pressed(self) -> None:
        """Pause/resume dialogue."""
        if self._controller is None:
            return
        self._controller.handle_pause()

    @on(Button.Pressed, f"#{UI_IDS.clear_btn}")
    def on_clear_pressed(self) -> None:
        """Clear log and contexts."""
        if self._controller:
            self._controller.handle_clear()

        dialog_log: RichLog = self.query_one(
            f"#{UI_IDS.dialogue_log}",
            RichLog,
        )
        dialog_log.clear()
        dialog_log.write("[dim]History cleared[/dim]")

        self.notify("History cleared!", title="Clear", severity="information")

    @on(Button.Pressed, f"#{UI_IDS.exit_btn}")
    def on_exit_pressed(self) -> None:
        """Exit application."""
        self.exit()

    def action_toggle_pause(self) -> None:
        """Toggle pause."""
        if self._controller:
            self._controller.handle_pause()

    def action_clear_log(self) -> None:
        """Clear log (hotkey)."""
        self.on_clear_pressed()

    async def _run_dialogue(self) -> None:
        """Run main dialogue loop."""
        if self._controller is None or self._client is None:
            log.error("Controller or client not initialized")
            return

        service = self._controller.service
        # Use cached style_mapper from __init__
        style_mapper = self._style_mapper

        try:
            while service.is_running and not service.is_paused:
                if self._is_task_cancelled():
                    break

                model_id = service.conversation.current_turn
                model_name = service.conversation.get_current_model_name()
                style_info = style_mapper.get_style_info(model_id, model_name)
                self._controller.update_for_turn(
                    style_info.model_name,
                    style_info.style_id,
                )

                try:
                    await self._process_dialogue_turn(
                        service,
                        style_info.model_name,
                        style_info.style_id,
                    )
                except ProviderError as e:
                    # Unified handling of all ProviderError
                    log.warning("Provider error in dialogue loop: %s", e)
                    self._handle_dialogue_error(style_info.model_name, str(e))
                    raise

                await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            log.debug("Dialogue cancelled")
        except ProviderError:
            log.debug("ProviderError handled")
        except (RuntimeError, SystemError, OSError) as e:
            self._handle_critical_error(e)
        finally:
            self._controller.handle_stop()
            if self._controller:
                await self._controller.cleanup()

    def _is_task_cancelled(self) -> bool:
        """Check if current task is cancelled."""
        try:
            loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
            current_task: asyncio.Task[None] | None = asyncio.current_task(loop=loop)
            return current_task is not None and current_task.cancelled()
        except RuntimeError:
            return False

    async def _process_dialogue_turn(
        self,
        service: DialogueService,
        _model_name: str,
        style: str,
    ) -> DialogueTurnResult | None:
        """Process one dialogue turn and output result."""
        thinking_msg = f"[dim]{_model_name} is thinking...[/]"
        self.call_after_refresh(self._write_to_log, thinking_msg)
        result = await service.run_dialogue_cycle()

        if result:
            response_text = result.response
            response_lines = []
            # Безопасный парсинг блока [Think...]: ищем закрывающую ] ПОСЛЕ [Think
            if "[Think" in response_text:
                think_start = response_text.find("[Think")
                # Ищем ] после [Think (может быть на той же или следующей стнии)
                next_newline = response_text.find("\n", think_start)
                search_range = response_text[think_start:next_newline if next_newline >= 0 else len(response_text)]
                think_end_idx = search_range.find("]")

                if think_end_idx >= 0:
                    # Нашли закрывающую ] в той же строке/блоке
                    thinking_part = search_range[:think_end_idx + 1]
                    # Проверяем что thinking_part не пустой (не просто "[]")
                    min_thinking_length = 3  # Минимум "[X]" для валидного блока
                    if len(thinking_part) > min_thinking_length:
                        response_lines.append(f"[dim]{thinking_part}[/]")
                    # Обрезаем response_text до конца блока [Think...]
                    content_start = think_start + len(thinking_part)
                    newline_pos = response_text.find("\n\n", content_start)
                    if newline_pos >= 0:
                        content_start = newline_pos + 2
                    response_text = response_text[content_start:].strip()
            response_text = sanitize_response_for_display(response_text)
            response_text = response_text.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
            message = f"\n[{style}]Turn {service.turn_count}: {result.model_name}[/]\n  {response_text}"
            if response_lines:
                message = "\n" + response_lines[0] + message
            self.call_after_refresh(self._write_to_log, message)

        return result

    def _write_to_log(self, message: str) -> None:
        """Safely write message to UI log and file."""
        clean_msg = _LOG_CLEANUP_PATTERN.sub("", message)
        try:
            if hasattr(self, "_dialogue_log_file") and self._dialogue_log_file:
                self._dialogue_log_file.write(clean_msg + "\n")
                self._dialogue_log_file.flush()
        except OSError:
            log.debug("Failed to write to log file: %s", message[:50])
        try:
            dialog_log: RichLog = self.query_one(
                f"#{UI_IDS.dialogue_log}",
                RichLog,
            )
            dialog_log.write(message)
        except (NoMatches, LookupError, RuntimeError, AttributeError):
            log.warning("Failed to write to log")

    def _handle_dialogue_error(self, model_name: str, error_detail: str = "") -> None:
        """Handle response generation error.

        This method is called from async context (_process_dialogue_turn),
        so we use call_after_refresh instead of call_from_thread.
        """
        # Улучшенное форматирование ошибки для пользователя
        if "Timeout" in error_detail or "timeout" in error_detail.lower():
            error_text = (
                "Ollama timed out. The model may be slow or overloaded. "
                "Try a smaller model or wait and restart."
            )
        elif "Connection" in error_detail or "connect" in error_detail.lower():
            error_text = (
                "Cannot connect to Ollama. Check that Ollama is running."
            )
        elif "failed" in error_detail.lower():
            error_text = f"Generation failed: {error_detail}"
        else:
            error_text = error_detail or "Generation failed"

        error_msg = f"\n[{MESSAGE_STYLES.error}]Error ({model_name}): {error_text}[/]"
        # Use call_after_refresh since we are in async context, not
        # in a thread
        self.call_after_refresh(self._write_to_log, error_msg)
        if self._controller:
            self._controller.update_for_error(model_name)
        self.notify(
            error_text,
            title=f"Error: {model_name}",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT * 2,  # Увеличиваем время показа
        )

    def _handle_critical_error(self, _e: BaseException) -> None:
        """Handle critical error in dialogue loop."""
        log.exception("Critical error in dialogue loop")
        error_msg = (
            f"\n[{MESSAGE_STYLES.error}]Critical error[/]: "
            "An unexpected error occurred. Please restart the application."
        )
        self.call_after_refresh(
            self._write_to_log,
            error_msg,
        )
        self.notify(
            "Critical error occurred. Please restart.",
            title="Critical Error",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT * 2,
        )

    async def _cleanup_dialogue_task(self) -> None:
        """Cancel and await dialogue task."""
        if self._dialogue_task is None or self._dialogue_task.done():
            return
        self._dialogue_task.cancel()
        try:
            await self._dialogue_task
        except asyncio.CancelledError:
            pass
        except Exception:
            log.debug("Error awaiting cancelled task")
        finally:
            self._dialogue_task = None

    async def _cleanup_controller(self) -> None:
        """Clean up controller resources."""
        if self._controller is None:
            return
        try:
            await self._controller.cleanup()
        except (aiohttp.ClientError, TimeoutError, OSError) as e:
            log.warning("Error during controller cleanup: %s", e)
        except Exception:
            log.debug("Unexpected error during controller cleanup")
        finally:
            self._controller = None

    async def _cleanup_client(self) -> None:
        """Clean up client resources."""
        if self._client is None:
            return
        try:
            await self._client.close()
        except (aiohttp.ClientError, TimeoutError, OSError) as e:
            log.warning("Error during client cleanup: %s", e)
        except Exception:
            log.debug("Unexpected error during client cleanup")
        finally:
            self._client = None

    def _cleanup_log_file(self) -> None:
        """Close dialogue log file."""
        if not hasattr(self, "_dialogue_log_file") or self._dialogue_log_file is None:
            return
        try:
            self._dialogue_log_file.close()
        except Exception:
            log.debug("Error closing log file")
        finally:
            self._dialogue_log_file = None

    async def on_unmount(self) -> None:
        """Clean up on application close."""
        async with self._cleanup_lock:
            if self._cleanup_done:
                return
            self._cleanup_done = True

        await self._cleanup_dialogue_task()
        await self._cleanup_controller()
        await self._cleanup_client()
        self._cleanup_log_file()


__all__ = [
    "DialogueApp",
    "ModelSelectionScreen",
    "TopicInputScreen",
]
