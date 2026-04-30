"""Controllers for managing UI state of AI Dialogue TUI application.

This module contains controllers for connecting business logic with UI.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from services.dialogue_service import DialogueService


class StateChangeCallback(Protocol):
    """Protocol for UI state change callbacks."""

    def __call__(self, state: UIState) -> None:
        """Handle state change."""
        ...


@dataclass(frozen=True, slots=True)
class UIState:
    """UI state for display.

    Attributes:
        status_text: Text to display in status bar.
        status_style: Style for status bar (green, yellow, red, etc.).
        turn_count: Number of turns made.
        current_model: Current model name (if known).
        is_dialogue_active: Whether dialogue is active.

    """

    status_text: str = "Waiting..."
    status_style: str = "dim"
    turn_count: int = 0
    current_model: str | None = None
    is_dialogue_active: bool = False


class DialogueController:
    """Controller for managing UI state based on dialogue service.

    Connects business logic (DialogueService) with UI components.
    Handles user commands and updates UI state.

    Attributes:
        service: Dialogue service for managing business logic.
        on_state_changed: Callback for UI state change notifications.

    """

    def __init__(
        self,
        service: DialogueService,
        on_state_changed: StateChangeCallback | None = None,
    ) -> None:
        """Initialize controller.

        Args:
            service: Dialogue service to manage.
            on_state_changed: Callback called when UI state changes.

        """
        self._service: DialogueService | None = service
        self._on_state_changed = on_state_changed
        self._state = UIState()

    @property
    def state(self) -> UIState:
        """Get current UI state.

        Returns:
            Current UI state.

        """
        return self._state

    @property
    def service(self) -> DialogueService | None:
        """Get dialogue service.

        Returns:
            Dialogue service or None if cleaned up.

        """
        return self._service

    def _notify_state_changed(self) -> None:
        """Notify UI state change via callback."""
        if self._on_state_changed is not None:
            callback: StateChangeCallback = self._on_state_changed
            callback(self._state)

    def _update_status(
        self,
        text: str,
        style: str,
    ) -> None:
        """Update status and notify change.

        Args:
            text: New status text.
            style: Display style.

        """
        self._state = replace(self._state, status_text=text, status_style=style)
        self._notify_state_changed()

    def handle_start(self) -> bool:
        """Handle dialogue start command.

        Returns:
            True if dialogue started successfully, False if there are errors.

        """
        if self._service is None:
            return False
        if self._service.is_running and not self._service.is_paused:
            self._update_status("Dialogue already running", "yellow")
            return False

        self._service.start()
        self._state = replace(self._state, is_dialogue_active=True)
        self._update_status("Dialogue running...", "green")
        return True

    def handle_pause(self) -> bool:
        """Handle pause/resume command.

        Returns:
            True if toggled, False if not running.

        """
        if self._service is None:
            return False
        if not self._service.is_running:
            self._update_status("Dialogue not started", "red")
            return False

        if self._service.is_paused:
            self._service.resume()
            self._update_status("Dialogue running...", "green")
        else:
            self._service.pause()
            self._update_status("Paused", "yellow")

        return True

    def handle_clear(self) -> None:
        """Handle history clear command.

        Clears dialogue contexts and resets turn counter.
        """
        if self._service is None:
            return
        self._service.clear_history()
        self._state = replace(self._state, turn_count=0)
        self._update_status("History cleared", "dim")

    def handle_stop(self) -> None:
        """Handle dialogue stop command.

        Sets is_running and is_paused flags to False.
        """
        if self._service is None:
            return
        self._service.stop()
        self._state = replace(self._state, is_dialogue_active=False)
        self._update_status("Stopped", "dim")

    def update_for_turn(
        self,
        model_name: str,
        style: str,
    ) -> None:
        """Update state for new dialogue turn.

        Args:
            model_name: Name of model making the turn.
            style: Display style (STYLE_MODEL_A or STYLE_MODEL_B).

        """
        if self._service is None:
            return
        self._state = replace(
            self._state,
            current_model=model_name,
            turn_count=self._service.turn_count,
        )
        self._update_status(f"Turn: {model_name}", style)

    def update_for_error(self, model_name: str) -> None:
        """Update state on error.

        Args:
            model_name: Name of model where error occurred.

        """
        self._update_status(f"Error: {model_name}", "red")

    async def cleanup(self) -> None:
        """Clean up controller and service resources.

        Calls dialogue service cleanup to release resources.
        Suppresses specific exceptions to ensure cleanup completes.
        """
        _log = logging.getLogger(__name__)
        if self._service is None:
            return
        try:
            await self._service.cleanup()
        except AttributeError:
            # Service already cleaned up
            _log.debug("Controller cleanup: service already cleaned up")
        except (asyncio.CancelledError, RuntimeError) as e:
            # Handle cancellation or runtime errors during cleanup
            _log.debug("Controller cleanup completed with non-critical error: %s", e)
        finally:
            # Гарантированно очищаем ссылку на сервис
            self._service = None


__all__ = ["DialogueController", "UIState"]
