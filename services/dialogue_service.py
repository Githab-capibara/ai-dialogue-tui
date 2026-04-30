"""Service layer for managing dialogue business logic.

This module contains the service for managing dialogue between models.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from models.config import Config
from models.provider import ModelId, ModelProvider, ProviderError

if TYPE_CHECKING:
    from models.conversation import Conversation

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DialogueTurnResult:
    """Result of one dialogue turn.

    Attributes:
        model_name: Name of the model that made the turn.
        model_id: Model identifier (A or B).
        role: Message role (always "assistant").
        response: Generated response text.

    """

    model_name: str
    model_id: ModelId
    role: Literal["assistant"]
    response: str


class DialogueService:
    """Service for managing dialogue business logic.

    Encapsulates the logic of starting, pausing, stopping, and executing
    dialogue cycles. Works with abstractions (ModelProvider, Conversation),
    not with concrete implementations.
    """

    def __init__(
        self,
        conversation: Conversation,
        provider: ModelProvider,
        config: Config | None = None,
    ) -> None:
        """Initialize dialogue service.

        Args:
            conversation: Conversation object for managing contexts.
            provider: Model provider for generating responses.
            config: Configuration for parameters (pauses, timeouts).

        """
        if conversation is None:
            err_msg = "conversation cannot be None"
            raise ValueError(err_msg)
        if provider is None:
            err_msg = "provider cannot be None"
            raise ValueError(err_msg)
        self._conversation = conversation
        self._provider = provider
        self._config = config or Config()
        self._is_running = False
        self._is_paused = False
        self._turn_count = 0

    @property
    def conversation(self) -> Conversation:
        """Get conversation object."""
        return self._conversation

    @property
    def provider(self) -> ModelProvider:
        """Get model provider."""
        return self._provider

    @property
    def is_running(self) -> bool:
        """Check if dialogue is running."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Check if dialogue is paused."""
        return self._is_paused

    @property
    def turn_count(self) -> int:
        """Get number of turns made."""
        return self._turn_count

    def start(self) -> None:
        """Start dialogue.

        Sets _is_running flag to True and resets pause.
        """
        self._is_running = True
        self._is_paused = False

    def pause(self) -> None:
        """Pause dialogue.

        Sets _is_paused flag to True.
        Dialogue remains running (is_running=True).
        """
        self._is_paused = True

    def resume(self) -> None:
        """Resume dialogue after pause.

        Resets _is_paused flag to False.
        """
        self._is_paused = False

    def stop(self) -> None:
        """Stop dialogue.

        Resets _is_running and _is_paused flags.
        """
        self._is_running = False
        self._is_paused = False

    def clear_history(self) -> None:
        """Clear dialogue history.

        Clears contexts of both models and resets turn counter.
        """
        self._conversation.clear_contexts()
        self._turn_count = 0

    async def run_dialogue_cycle(self) -> DialogueTurnResult | None:
        """Execute one dialogue cycle.

        Generates response for current model, updates contexts,
        switches turn, and increments counter.

        Returns:
            DialogueTurnResult or None if dialogue is not running.

        """
        if not self._is_running or self._is_paused:
            return None

        model_id = self._conversation.current_turn
        model_name = self._conversation.get_current_model_name()

        try:
            _, _, response = await self._conversation.process_turn(self._provider)
            self._turn_count += 1
            return DialogueTurnResult(
                model_name=model_name,
                model_id=model_id,
                role="assistant",
                response=response,
            )

        except asyncio.CancelledError:
            log.info("Dialogue cycle cancelled")
            raise
        except ProviderError:
            log.warning("Provider error during dialogue cycle execution")
            raise

    async def cleanup(self) -> None:
        """Clean up service resources.

        Closes connection to model provider.
        All exceptions are suppressed to ensure cleanup completes.
        """
        try:
            await self._provider.close()
        except Exception:
            log.debug("Provider cleanup completed with non-critical error")


__all__ = [
    "DialogueService",
    "DialogueTurnResult",
]
