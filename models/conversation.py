"""Dialogue logic and context storage for two models.

This module contains the domain logic of the dialogue.
Depends only on abstractions (protocols), not on concrete implementations.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from models.config import Config
from models.provider import MessageDict, ModelId, ModelProvider

log = logging.getLogger(__name__)

__all__ = ["Conversation", "ModelId"]

MAX_CONTEXT_LENGTH: int = 50


@dataclass(slots=True)
class _ConversationContext:
    """Context for each model - separated to reduce Conversation attributes."""

    messages: list[MessageDict] = field(default_factory=list)
    model_id: ModelId = field(default_factory=lambda: "A")


@dataclass(slots=True)
class Conversation:
    """Manage dialogue between two models.

    Each model has its own independent context (message history).
    Response from one model is added to the other model's context
    as a user message.

    """

    model_a: str  # Name of model A
    model_b: str  # Name of second model
    topic: str  # Dialogue topic

    # Contexts for each model (message lists in Ollama format)
    _context_a: list[MessageDict] = field(default_factory=list, repr=False)
    _context_b: list[MessageDict] = field(default_factory=list, repr=False)

    system_prompt: str = ""

    # Whose turn it is
    _current_turn: ModelId = field(default="A", init=False)

    # Flag to prevent re-initialization
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Initialize system prompt after object creation."""
        if self._initialized:
            return
        self._initialized = True

        self._validate_params()
        formatted_prompt = self._create_system_prompt()
        self._context_a.append(MessageDict(role="system", content=formatted_prompt))
        self._context_b.append(MessageDict(role="system", content=formatted_prompt))

    def _validate_params(self) -> None:
        """Validate constructor parameters."""
        if not self.model_a or not isinstance(self.model_a, str):
            msg = "model_a must be a non-empty string"
            raise ValueError(msg)
        if not self.model_b or not isinstance(self.model_b, str):
            msg = "model_b must be a non-empty string"
            raise ValueError(msg)
        if not self.topic or not isinstance(self.topic, str):
            msg = "topic must be a non-empty string"
            raise ValueError(msg)
        if self.model_a == self.model_b:
            msg = "model_a and model_b must be different"
            raise ValueError(msg)

    def _create_system_prompt(self) -> str:
        """Create formatted system prompt."""
        _default_prompt = Config().default_system_prompt
        effective_prompt = self.system_prompt or _default_prompt

        try:
            return effective_prompt.format(topic=self.topic)
        except (KeyError, ValueError):
            return f"You are a helpful assistant. The topic of discussion is: {self.topic}"

    def _trim_context_if_needed(
        self,
        context: list[MessageDict],
        max_len: int = MAX_CONTEXT_LENGTH,
    ) -> list[MessageDict]:
        """Trim context if it exceeds max_len.

        Preserves system prompt (first message) and last messages.
        Removes old messages from the middle of context.

        Args:
            context: Context to check and possibly trim.
            max_len: Maximum context length after trimming.

        Returns:
            Trimmed context if exceeded, otherwise original.

        """
        if len(context) <= max_len:
            return context

        system_message = context[0] if context else None

        remaining_messages = context[-max_len:]

        trimmed = [system_message, *remaining_messages] if system_message else remaining_messages

        log.warning(
            "Context exceeded (%d messages), trimmed to %d",
            len(context),
            len(trimmed),
        )

        return trimmed

    def _add_message_to_context(
        self,
        model_id: ModelId,
        role: Literal["system", "user", "assistant"],
        content: str,
    ) -> None:
        """Add message to model context."""
        # Direct context access without redundant dictionary creation
        context = self._context_a if model_id == "A" else self._context_b

        if len(context) >= MAX_CONTEXT_LENGTH:
            context = self._trim_context_if_needed(context, MAX_CONTEXT_LENGTH - 2)
            # Update reference to trimmed context
            if model_id == "A":
                self._context_a = context
            else:
                self._context_b = context

        context.append(MessageDict(role=role, content=content))

    def add_message(
        self,
        model_id: ModelId,
        role: Literal["system", "user", "assistant"],
        content: str,
    ) -> None:
        """Add message to the specified model's context.

        Args:
            model_id: Model identifier (A or B).
            role: Message role ("user", "assistant", "system").
            content: Message text.

        """
        self._add_message_to_context(model_id, role, content)
        context = self._context_a if model_id == "A" else self._context_b

        log.debug(
            "Added %s message to model %s context (total: %d)",
            role,
            model_id,
            len(context),
        )

    def get_context(self, model_id: ModelId) -> tuple[MessageDict, ...]:
        """Get message history for the specified model.

        Args:
            model_id: Model identifier (A or B).

        Returns:
            Tuple of messages in Ollama format (immutable).

        """
        context = self._context_a if model_id == "A" else self._context_b
        # Return tuple for safety and performance
        return tuple(context)

    def switch_turn(self) -> None:
        """Switch turn to the other model.

        Command (command) - changes state, returns nothing.
        Use current_turn property to get the current turn.
        """
        previous_turn = self._current_turn
        self._current_turn = "B" if self._current_turn == "A" else "A"
        log.debug(
            "Turn switched: model %s -> model %s",
            previous_turn,
            self._current_turn,
        )

    @property
    def current_turn(self) -> ModelId:
        """Get the identifier of the model whose turn it is.

        Returns:
            Current model identifier (A or B).

        """
        return self._current_turn

    def get_current_model_name(self) -> str:
        """Get the name of the current model."""
        return self.model_a if self._current_turn == "A" else self.model_b

    def get_other_model_name(self) -> str:
        """Get the name of the other model."""
        return self.model_b if self._current_turn == "A" else self.model_a

    async def generate_response(
        self,
        provider: ModelProvider,
    ) -> tuple[ModelId, str]:
        """Generate response for the current model.

        Args:
            provider: Model provider for generation (ModelProvider).

        Returns:
            Tuple (model identifier, generated response).

        """
        model_id = self.current_turn
        model_name = self.get_current_model_name()
        context = list(self.get_context(model_id))

        response = await provider.generate(
            model=model_name,
            messages=context,
        )

        return model_id, response

    async def process_turn(
        self,
        provider: ModelProvider,
    ) -> tuple[str, str, str]:
        """Process one dialogue turn.

        Generates response for the current model, adds it to both contexts
        (as assistant for current model and as user for the other),
        then switches turn.

        Args:
            provider: Model provider for generation (ModelProvider).

        Returns:
            Tuple (model name, role "assistant", response text).

        """
        model_id = self.current_turn
        model_name = self.get_current_model_name()
        other_id: ModelId = "B" if model_id == "A" else "A"

        # Save context state for rollback on error
        context_a_snapshot = list(self._context_a)
        context_b_snapshot = list(self._context_b)
        turn_snapshot = self._current_turn

        try:
            # Generate response BEFORE any context changes
            _, response = await self.generate_response(provider)

            # Add response to current model's context as assistant
            self.add_message(model_id, "assistant", response)

            # Add response to other model's context as user
            self.add_message(other_id, "user", response)

            # Switch turn
            self.switch_turn()

            return model_name, "assistant", response

        except Exception:
            # Rollback context state on error
            self._context_a = context_a_snapshot
            self._context_b = context_b_snapshot
            self._current_turn = turn_snapshot
            raise

    def clear_contexts(self) -> None:
        """Clear both contexts, preserving only system prompt and topic."""
        formatted_prompt = self._create_system_prompt()
        self._context_a = [MessageDict(role="system", content=formatted_prompt)]
        self._context_b = [MessageDict(role="system", content=formatted_prompt)]
        self._current_turn = "A"

    def get_context_stats(self) -> dict[str, int]:
        """Get context statistics.

        Returns:
            Dictionary with message count in each context.

        """
        return {
            "model_a_messages": len(self._context_a),
            "model_b_messages": len(self._context_b),
        }
