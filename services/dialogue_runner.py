"""Service for managing dialogue loop cycle.

This module contains the business logic for executing dialogue loops.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from models.config import Config
from models.provider import ProviderError

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.dialogue_service import DialogueService, DialogueTurnResult

log = logging.getLogger(__name__)


class DialogueRunner:
    """Service for running and managing dialogue loop.

    Encapsulates the logic of executing the main dialogue loop,
    error handling, and task management.
    """

    def __init__(
        self,
        service: DialogueService,
        config: Config | None = None,
    ) -> None:
        """Initialize dialogue runner.

        Args:
            service: Dialogue service to manage.
            config: Configuration for loop parameters.

        """
        self._service = service
        self._config = config or Config()
        self._dialogue_task: asyncio.Task[None] | None = None

    @property
    def service(self) -> DialogueService:
        """Get dialogue service."""
        return self._service

    @property
    def dialogue_task(self) -> asyncio.Task[None] | None:
        """Get dialogue task."""
        return self._dialogue_task

    async def start(
        self,
        on_turn: Callable[[DialogueTurnResult], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        """Start dialogue loop in background task.

        Args:
            on_turn: Callback for processing each turn.
            on_error: Callback for handling generation errors.

        """
        loop = asyncio.get_running_loop()
        self._dialogue_task = loop.create_task(self._run_loop(on_turn, on_error))

    async def stop(self) -> None:
        """Stop dialogue loop.

        Cancels dialogue task if active.
        """
        if self._dialogue_task and not self._dialogue_task.done():
            self._dialogue_task.cancel()
            try:
                await self._dialogue_task
            except asyncio.CancelledError:
                pass
            finally:
                self._dialogue_task = None

    async def _run_loop(
        self,
        on_turn: Callable[[DialogueTurnResult], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        """Run main dialogue loop.

        Args:
            on_turn: Callback for processing each turn.
            on_error: Callback for handling generation errors.

        """
        try:
            while self._service.is_running and not self._service.is_paused:
                if self._is_task_cancelled():
                    break

                try:
                    result = await self._process_turn()
                    if result and on_turn:
                        on_turn(result)
                except ProviderError as exc:
                    log.warning("Provider error in dialogue loop: %s", exc)
                    if on_error:
                        model_name = self._service.conversation.get_current_model_name()
                        on_error(model_name)

                    await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            log.debug("Dialogue cancelled")
            raise
        except (RuntimeError, SystemError, OSError) as exc:
            log.exception("Critical error in dialogue loop: %s", exc)
        finally:
            self._service.stop()

    async def _process_turn(self) -> DialogueTurnResult | None:
        """Process one dialogue turn.

        Returns:
            DialogueTurnResult with turn result.

        """
        return await self._service.run_dialogue_cycle()

    def _is_task_cancelled(self) -> bool:
        """Check if current task is cancelled."""
        task = asyncio.current_task()
        return task is not None and task.cancelled()

    async def cleanup(self) -> None:
        """Clean up runner resources."""
        await self.stop()


__all__ = ["DialogueRunner"]
