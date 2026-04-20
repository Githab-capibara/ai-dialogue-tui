"""TUI application for dialogue between two AI models.

This module contains only UI components and event handlers.
Business logic is moved to the service layer (services/dialogue_service.py).
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

# Timeout constant for notifications
DEFAULT_NOTIFY_TIMEOUT: int = 10

# =============================================================================
# call_from_thread vs call_after_refresh in Textual
# =============================================================================
# call_from_thread: used for threading.Thread
# call_after_refresh: used in asyncio.create_task, async def
#
# In this module all methods work in async context,
# so call_after_refresh is used, NOT call_from_thread!
# =============================================================================

# CSS is generated from centralized constants
CSS = generate_main_css()

log = logging.getLogger(__name__)


class ModelSelectionScreen(ModalScreen[tuple[str, str] | None]):
    """Modal window for selecting two models."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape", "cancel", "Cancel"),
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
            yield Static("Select two models for dialogue", id=UI_IDS.selection_title)

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
                yield Button("Start Dialogue", id=UI_IDS.start_btn, variant="primary")
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

        assert isinstance(model_a_value, str) and model_a_value
        assert isinstance(model_b_value, str) and model_b_value
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
        with Container(id=UI_IDS.topic_input_container), Vertical(id=UI_IDS.topic_input_content):
            yield Static("Enter dialogue topic:", id=UI_IDS.topic_label)
            yield Input(
                placeholder="For example: Debate on Python advantages over Go",
                id=UI_IDS.topic_input,
            )
            with Horizontal(id=UI_IDS.topic_buttons):
                yield Button("Start", id=UI_IDS.topic_start_btn, variant="primary")
                yield Button("Cancel", id=UI_IDS.topic_cancel_btn, variant="error")

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
        self.sub_title = reactive("Dialogue between two AI models via Ollama")
        self._config = config or Config()
        self._provider_factory = provider_factory or (lambda: OllamaClient(host=self._config.ollama_host))
        self._client: ModelProvider | None = None
        self._controller: DialogueController | None = None
        self._dialogue_task: asyncio.Task[None] | None = None
        self._models: list[str] = []
        self._style_mapper = ModelStyleMapper()
        self._cleanup_done = False
        self._cleanup_lock = asyncio.Lock()

    def compose(self) -> ComposeResult:
        """Compose the main application UI."""
        yield Header()

        with Container(id=UI_IDS.main_container):
            # Status bar
            with Container(id=UI_IDS.status_bar), Horizontal(id=UI_IDS.status_row):
                yield Label("Status: ", id=UI_IDS.status_label)
                yield Label("Waiting...", id=UI_IDS.status_value)

            # Dialogue log
            yield RichLog(id=UI_IDS.dialogue_log, highlight=True, markup=True)

            # Control panel
            with Container(id=UI_IDS.controls_bar), Horizontal(id=UI_IDS.controls_row):
                yield Button("Start", id=UI_IDS.start_btn, variant="success")
                yield Button("Pause", id=UI_IDS.pause_btn, variant="warning")
                yield Button("Clear", id=UI_IDS.clear_btn, variant="default")
                yield Button("Exit", id=UI_IDS.exit_btn, variant="error")

        yield Footer()

    def _on_ui_state_changed(self, state: UIState) -> None:
        """Handle UI state change.

        Args:
            state: New UI state from controller.

        """
        try:
            status_label: Label = self.query_one("#status-value", Label)
            style_tag = f"[{state.status_style}]{state.status_text}[/{state.status_style}]"
            status_label.update(style_tag)
        except (NoMatches, ScreenStackError):
            log.debug("Element #status-value not available for update")
        except LookupError:
            log.exception("LookupError when updating UI state")
        except RuntimeError:
            log.exception("RuntimeError when updating UI state")

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
                "Failed to connect to Ollama. Check that the service is running.",
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
        except asyncio.TimeoutError:
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

            # Update title and status via call_after_refresh
            # so UI has time to update after modal closes
            def _finalize_setup() -> None:
                self.sub_title = f"{model_a} <-> {model_b} | Topic: {sanitized_topic}"
                ready_state = UIState(status_text="Ready to start", status_style="green")
                self._on_ui_state_changed(ready_state)

                # Log initialization with error handling
                try:
                    dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
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
        if self._controller is None:
            log.error("Controller not initialized")
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

        dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
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
                self._controller.update_for_turn(style_info.model_name, style_info.style_id)

                try:
                    await self._process_dialogue_turn(service, style_info.model_name, style_info.style_id)
                except ProviderError as e:
                    # Unified handling of all ProviderError
                    log.warning("Provider error in dialogue loop: %s", e)
                    self._handle_dialogue_error(style_info.model_name)
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
        current_task = asyncio.current_task()
        return current_task is not None and current_task.cancelled()

    async def _process_dialogue_turn(
        self,
        service: DialogueService,
        _model_name: str,
        style: str,
    ) -> DialogueTurnResult | None:
        """Process one dialogue turn and output result."""
        result = await service.run_dialogue_cycle()

        if result:
            formatted_response = sanitize_response_for_display(result.response)
            turn_msg = f"\n[{style}]Turn {service.turn_count}: {result.model_name}[/]\n  {formatted_response}"
            message = turn_msg
            self.call_after_refresh(self._write_to_log, message)

        return result

    def _write_to_log(self, message: str) -> None:
        """Safely write message to UI log."""
        try:
            dialog_log: RichLog = self.query_one(f"#{UI_IDS.dialogue_log}", RichLog)
            dialog_log.write(message)
        except (NoMatches, LookupError, RuntimeError):
            log.warning("Failed to write to log")

    def _handle_dialogue_error(self, model_name: str) -> None:
        """Handle response generation error.

        This method is called from async context (_process_dialogue_turn),
        so we use call_after_refresh instead of call_from_thread.
        """
        error_msg = f"\n[{MESSAGE_STYLES.error}]Error ({model_name})[/]"
        # Use call_after_refresh since we are in async context, not
        # in a thread
        self.call_after_refresh(self._write_to_log, error_msg)
        if self._controller:
            self._controller.update_for_error(model_name)
        self.notify(
            "Response generation error",
            title="Error",
            severity="error",
            timeout=DEFAULT_NOTIFY_TIMEOUT,
        )

    def _handle_critical_error(self, _e: BaseException) -> None:
        """Handle critical error in dialogue loop."""
        log.exception("Critical error in dialogue loop")
        self.call_after_refresh(
            self._write_to_log,
            f"\n[{MESSAGE_STYLES.error}]Critical error[/]",
        )

    async def on_unmount(self) -> None:
        """Clean up on application close."""
        async with self._cleanup_lock:
            if self._cleanup_done:
                return
            self._cleanup_done = True

        try:
            # Cancel dialogue task
            if self._dialogue_task and not self._dialogue_task.done():
                self._dialogue_task.cancel()
                try:
                    await self._dialogue_task
                except asyncio.CancelledError:
                    pass
                finally:
                    self._dialogue_task = None

            # Clean up controller and client
            try:
                if self._controller:
                    await self._controller.cleanup()
                elif self._client:
                    await self._client.close()
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                log.warning("Error during resource cleanup: %s", e)
            finally:
                self._controller = None
                self._client = None

        except RuntimeError:
            log.exception("Unexpected error during cleanup")


__all__ = [
    "DialogueApp",
    "ModelSelectionScreen",
    "TopicInputScreen",
]
