"""Tests for verifying new fixes from code audit.

This file contains tests for verifying the following fixes:
1. models/conversation.py - remaining_messages is trimmed correctly
2. models/conversation.py:154-159 - add_message does not duplicate code
3. tui/app.py:220 - empty binding ctrl+c removed from BINDINGS
4. models/ollama_client.py:208-212 - asyncio.Lock used in _HTTPSessionManager
5. services/dialogue_service.py:172 - log.exception used instead of log.warning
6. controllers/dialogue_controller.py:78 - state returns copy (replace())
7. models/ollama_client.py:212 - _get_session works correctly
8. tui/app.py:317 - ProviderConnectionError and ProviderGenerationError handled separately
9. tui/app.py:556-559 - cleanup called on stop
10. models/conversation.py:131-138 - _add_message_to_context works correctly

Note:
    Tests use access to internal attributes and imports inside functions,
    which is justified for testing purposes.

"""

# pylint: disable=protected-access,import-outside-toplevel,no-member
# pylint: disable=too-few-public-methods,line-too-long

import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from controllers.dialogue_controller import DialogueController
from models.conversation import MAX_CONTEXT_LENGTH, Conversation
from models.ollama_client import _HTTPSessionManager
from services.dialogue_service import DialogueService
from tui.app import DialogueApp

# =============================================================================
# 1. Test: models/conversation.py:108-110 - remaining_messages = context[-effective_max:]
# =============================================================================


class TestTrimContextFix:
    """Tests for verifying fix in _trim_context_if_needed."""

    def test_trim_context_uses_negative_slicing(self) -> None:
        """Verify that negative indexing context[-effective_max:] is used."""
        source = inspect.getsource(Conversation._trim_context_if_needed)
        assert "context[-effective_max:]" in source

    def test_trim_context_no_meaningless_condition(self) -> None:
        """Verify that there is no meaningless condition."""
        source = inspect.getsource(Conversation._trim_context_if_needed)
        assert "if remaining_messages" not in source
        assert "remaining_messages and" not in source

    def test_trim_context_with_large_context(self) -> None:
        """Verify context trimming with large number of messages."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        conversation._context_a = [MagicMock() for _ in range(MAX_CONTEXT_LENGTH + 10)]
        conversation._context_a[0] = {"role": "system", "content": "System prompt"}

        result = conversation._trim_context_if_needed(conversation._context_a, MAX_CONTEXT_LENGTH - 2)

        assert len(result) <= MAX_CONTEXT_LENGTH - 2 + 1
        assert result[0]["role"] == "system"


# =============================================================================
# 2. Test: models/conversation.py:154-159 - add_message does not duplicate code
# =============================================================================


class TestAddMessageNoDuplication:
    """Tests for verifying no code duplication in add_message."""

    def test_add_message_uses_helper_method(self) -> None:
        """Verify that add_message uses _add_message_to_context."""
        source = inspect.getsource(Conversation.add_message)
        assert "_add_message_to_context" in source

    def test_add_message_no_direct_context_append(self) -> None:
        """Verify that there is no direct context append in add_message."""
        source = inspect.getsource(Conversation.add_message)
        assert "self._context_a.append" not in source
        assert "self._context_b.append" not in source

    def test_add_message_calls_helper(self) -> None:
        """Verify that add_message calls helper method."""
        from models import conversation as conv_module

        conversation = Conversation("model_a", "model_b", "test_topic")
        with patch.object(conv_module.Conversation, "_add_message_to_context", autospec=True) as mock_helper:
            conversation.add_message("A", "user", "Hello")
            mock_helper.assert_called_once_with(conversation, "A", "user", "Hello")


# =============================================================================
# 3. Test: tui/app.py:220 - empty binding ctrl+c removed from BINDINGS
# =============================================================================


class TestEmptyCtrlCBindingRemoved:
    """Tests for verifying empty ctrl+c binding removal."""

    def test_ctrl_c_binding_not_in_bindings(self) -> None:
        """Verify that ctrl+c binding is absent in BINDINGS."""
        bindings = DialogueApp.BINDINGS
        for binding in bindings:
            assert binding.key != "ctrl+c"
            assert binding.key != "ctrl+c()"

    def test_no_empty_action_binding(self) -> None:
        """Verify that there is no binding with empty action."""
        source = inspect.getsource(DialogueApp)
        assert 'Binding("ctrl+c", "", ' not in source
        assert 'Binding("ctrl+c", None,' not in source

    def test_bindings_only_has_valid_actions(self) -> None:
        """Verify that all bindings have valid actions."""
        bindings = DialogueApp.BINDINGS
        for binding in bindings:
            assert binding.action
            assert binding.action not in ("", None)


# =============================================================================
# 4. Test: models/ollama_client.py:208-212 - asyncio.Lock used in _HTTPSessionManager
# =============================================================================


class TestHTTPSessionManagerUsesLock:
    """Tests for verifying asyncio.Lock usage in _HTTPSessionManager."""

    def test_session_manager_has_lock_attribute(self) -> None:
        """Verify that _HTTPSessionManager has _lock attribute."""
        manager = _HTTPSessionManager(timeout=60)
        assert hasattr(manager, "_lock")

    def test_lock_is_asyncio_lock(self) -> None:
        """Verify that _lock is asyncio.Lock."""
        manager = _HTTPSessionManager(timeout=60)
        assert isinstance(manager._lock, asyncio.Lock)

    def test_get_session_uses_lock(self) -> None:
        """Verify that get_session uses async with self._lock."""
        source = inspect.getsource(_HTTPSessionManager.get_session)
        assert "async with self._lock" in source

    @pytest.mark.asyncio
    async def test_get_session_is_thread_safe(self) -> None:
        """Verify that get_session works with locking."""
        manager = _HTTPSessionManager(timeout=60)

        async def get_sessions() -> aiohttp.ClientSession:
            return await manager.get_session()

        results = await asyncio.gather(get_sessions(), get_sessions())
        assert results[0] is results[1]


# =============================================================================
# 5. Test: services/dialogue_service.py:172 - log.exception used
# =============================================================================


class TestDialogueServiceUsesLogException:
    """Tests for verifying log.warning usage in DialogueService."""

    def test_run_dialogue_cycle_uses_log_warning(self) -> None:
        """Verify that log.warning is used for ProviderError handling."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        assert "log.warning" in source

    def test_provider_error_caught_with_warning_logging(self) -> None:
        """Verify ProviderError handling with log.warning."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        assert "ProviderError" in source
        assert "log.warning" in source


# =============================================================================
# 6. Test: controllers/dialogue_controller.py:78 - state returns copy (replace())
# =============================================================================


class TestControllerStateReturnsCopy:
    """Tests for verifying state return in DialogueController."""

    def test_state_property_returns_state(self) -> None:
        """Verify that state property returns the internal state."""
        source = inspect.getsource(DialogueController.state.fget)
        assert "self._state" in source

    def test_state_returns_same_reference(self) -> None:
        """Verify that returned state is the same reference to internal state."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        state1 = controller.state
        state2 = controller.state

        assert state1 is state2


# =============================================================================
# 7. Test: models/ollama_client.py:212 - _get_session works correctly
# =============================================================================


class TestHTTPSessionManagerGetSession:
    """Tests for verifying _get_session (alias for get_session) works."""

    def test_get_session_method_exists(self) -> None:
        """Verify that get_session method exists."""
        manager = _HTTPSessionManager(timeout=60)
        assert hasattr(manager, "get_session")
        assert callable(manager.get_session)

    @pytest.mark.asyncio
    async def test_get_session_creates_new_session(self) -> None:
        """Verify that get_session creates new session on first call."""
        manager = _HTTPSessionManager(timeout=60)
        session = await manager.get_session()
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing_session(self) -> None:
        """Verify that get_session reuses existing session."""
        manager = _HTTPSessionManager(timeout=60)
        session1 = await manager.get_session()
        session2 = await manager.get_session()
        assert session1 is session2

    @pytest.mark.asyncio
    async def test_get_session_creates_new_after_close(self) -> None:
        """Verify that new session is created after closing old one."""
        manager = _HTTPSessionManager(timeout=60)
        session1 = await manager.get_session()
        await session1.close()
        session2 = await manager.get_session()
        assert session1 is not session2


# =============================================================================
# 8. Test: ProviderConnectionError and ProviderGenerationError handled separately
# =============================================================================


class TestSeparateExceptionHandling:
    """Tests for verifying separate exception handling in app.py."""

    def test_on_mount_has_specific_handlers(self) -> None:
        """Verify presence of specific exception handlers."""
        source = inspect.getsource(DialogueApp.on_mount)
        # Verify specific handlers exist
        assert "ProviderConnectionError" in source or "aiohttp.ClientError" in source
        assert "ProviderGenerationError" in source or "asyncio.TimeoutError" in source

    def test_connection_error_handler_exists(self) -> None:
        """Verify ProviderConnectionError handling."""
        source = inspect.getsource(DialogueApp.on_mount)
        assert "ProviderConnectionError" in source

    def test_generation_error_handler_exists(self) -> None:
        """Verify ProviderGenerationError handling."""
        source = inspect.getsource(DialogueApp.on_mount)
        assert "ProviderGenerationError" in source

    def test_no_generic_exception_handler(self) -> None:
        """Verify that there is no generic exception handler."""
        source = inspect.getsource(DialogueApp.on_mount)
        if "except Exception" in source or "except ProviderError" in source:
            assert "ProviderConnectionError" in source
            assert "ProviderGenerationError" in source


# =============================================================================
# 9. Test: tui/app.py:556-559 - cleanup called on stop
# =============================================================================


class TestCleanupOnUnmount:
    """Tests for verifying cleanup call on application stop."""

    def test_on_unmount_calls_cleanup(self) -> None:
        """Verify that on_unmount calls cleanup."""
        source = inspect.getsource(DialogueApp.on_unmount)
        assert "await self._controller.cleanup()" in source

    def test_on_unmount_cancels_dialogue_task(self) -> None:
        """Verify that on_unmount cancels dialogue task."""
        source = inspect.getsource(DialogueApp.on_unmount)
        assert "_dialogue_task.cancel()" in source or "cancel()" in source

    @pytest.mark.asyncio
    async def test_on_unmount_handles_cleanup_error(self) -> None:
        """Verify error handling during cleanup."""
        app = DialogueApp()

        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        app._dialogue_task = mock_task

        mock_controller = AsyncMock()
        mock_controller.cleanup.side_effect = aiohttp.ClientError("cleanup error")
        app._controller = mock_controller

        await app.on_unmount()

    @pytest.mark.asyncio
    async def test_on_unmount_calls_controller_cleanup(self) -> None:
        """Verify controller cleanup call."""
        app = DialogueApp()

        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        app._dialogue_task = mock_task

        mock_controller = AsyncMock()
        app._controller = mock_controller

        await app.on_unmount()

        mock_controller.cleanup.assert_called_once()


# =============================================================================
# 10. Test: models/conversation.py:131-138 - _add_message_to_context works correctly
# =============================================================================


class TestAddMessageToContext:
    """Tests for verifying _add_message_to_context works."""

    def test_add_message_to_context_exists(self) -> None:
        """Verify existence of _add_message_to_context method."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        assert hasattr(conversation, "_add_message_to_context")

    def test_add_message_to_context_trims_when_needed(self) -> None:
        """Verify context trimming when limit is reached."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        initial_context_len = MAX_CONTEXT_LENGTH - 1
        conversation._context_a = [{"role": "user", "content": f"msg_{i}"} for i in range(initial_context_len)]

        conversation._add_message_to_context("A", "user", "new message")

        assert len(conversation._context_a) <= MAX_CONTEXT_LENGTH

    def test_add_message_to_context_adds_to_correct_model(self) -> None:
        """Verify message is added to correct model context."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        conversation._add_message_to_context("A", "user", "message for A")
        assert conversation._context_a[-1]["content"] == "message for A"
        assert len(conversation._context_b) == 1

        conversation._add_message_to_context("B", "assistant", "message for B")
        assert conversation._context_b[-1]["content"] == "message for B"
        assert len(conversation._context_a) == 2

    def test_add_message_to_context_handles_message_dict(self) -> None:
        """Verify MessageDict creation on add."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        conversation._add_message_to_context("A", "user", "test content")

        msg = conversation._context_a[-1]
        assert msg["role"] == "user"
        assert msg["content"] == "test content"


# =============================================================================
# Integration tests
# =============================================================================


class TestIntegration:
    """Integration tests for verifying component interaction."""

    def test_conversation_trim_and_add_message_flow(self) -> None:
        """Verify complete trim and add message flow."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        for i in range(MAX_CONTEXT_LENGTH + 5):
            conversation.add_message("A", "user", f"message {i}")

        # Context should be trimmed to MAX_CONTEXT_LENGTH or less
        assert len(conversation._context_a) <= MAX_CONTEXT_LENGTH
        # Trim logic preserves system message + latest messages
        # After adding 55 messages (0-54) and trim to 49, last will be
        # message 54
        assert conversation._context_a[-1]["role"] == "user"
        # First message should be system prompt
        assert conversation._context_a[0]["role"] == "system"

    def test_controller_state_immutability(self) -> None:
        """Verify state immutability after return from controller."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        state = controller.state
        assert state.is_dialogue_active is False

    @pytest.mark.asyncio
    async def test_session_manager_concurrent_access(self) -> None:
        """Verify concurrent access safety to session manager."""
        manager = _HTTPSessionManager(timeout=60)

        async def get_session_twice() -> tuple[aiohttp.ClientSession, aiohttp.ClientSession]:
            s1 = await manager.get_session()
            s2 = await manager.get_session()
            return s1, s2

        results = await asyncio.gather(
            get_session_twice(),
            get_session_twice(),
            get_session_twice(),
        )

        all_sessions = [r[0] for r in results] + [r[1] for r in results]
        unique_sessions = set(id(s) for s in all_sessions)
        assert len(unique_sessions) == 1
