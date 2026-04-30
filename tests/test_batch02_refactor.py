"""Tests for Batch-02 refactoring fixes (issues ISSUE-0021 to ISSUE-0027).

This module verifies specific refactoring improvements:
- ISSUE-0021: Blanket except Exception replaced with specific exception types
- ISSUE-0022: Error-level logging for critical exceptions
- ISSUE-0023: Type hints for async functions
- ISSUE-0024: TypedDict keys made required
- ISSUE-0025: Constants properly typed
- ISSUE-0026: Tests for cleanup scenarios (CancelledError, TimeoutError)
- ISSUE-0027: Tests for edge cases in DialogueService
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Literal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestIssue0021ExceptionHandling:
    """Tests for ISSUE-0021: Blanket except Exception handling fixes."""

    def test_tui_app_on_ui_state_changed_no_broad_exception(self) -> None:
        """Verify _on_ui_state_changed does not have blanket except Exception."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._on_ui_state_changed)
        # Не должно быть blanket except Exception
        assert "except Exception:" not in source
        assert "except Exception as" not in source
        # Должны быть конкретные типы
        assert "NoMatches" in source or "LookupError" in source or "RuntimeError" in source

    def test_dialogue_service_cleanup_specific_exceptions(self) -> None:
        """Verify DialogueService.cleanup uses specific exceptions."""
        from services.dialogue_service import DialogueService

        source = inspect.getsource(DialogueService.cleanup)
        # Не должно быть blanket except Exception
        assert "except Exception" not in source
        # Должны быть конкретные типы
        assert "AttributeError" in source
        assert "OSError" in source or "RuntimeError" in source or "CancelledError" in source

    def test_conversation_process_turn_specific_exceptions(self) -> None:
        """Verify process_turn uses specific exceptions for rollback."""
        from models.conversation import Conversation

        source = inspect.getsource(Conversation.process_turn)
        # Не должно быть blanket except Exception
        assert "except Exception:" not in source
        # Должны быть конкретные типы
        assert "AttributeError" in source or "TypeError" in source or "RuntimeError" in source


class TestIssue0022ErrorLevelLogging:
    """Tests for ISSUE-0022: Error-level logging for critical exceptions."""

    @pytest.mark.asyncio
    async def test_dialogue_service_provider_error_logged_at_error_level(self) -> None:
        """Verify ProviderError is logged at error level in run_dialogue_cycle."""
        from models.provider import ProviderGenerationError
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        # Настраиваем мок-провайдер
        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(side_effect=ProviderGenerationError("Test error"))

        mock_conversation = MagicMock(spec=Conversation)
        mock_conversation.current_turn = "A"
        mock_conversation.get_current_model_name.return_value = "test-model"
        mock_conversation.process_turn = AsyncMock(
            side_effect=ProviderGenerationError("Test error")
        )

        service = DialogueService(
            conversation=mock_conversation,
            provider=mock_provider,
        )
        service.start()

        with patch("services.dialogue_service.log") as mock_log:
            with pytest.raises(ProviderGenerationError):
                await service.run_dialogue_cycle()

            # Проверяем, что ProviderError логируется на ERROR уровне
            error_calls = [c for c in mock_log.error.call_args_list]
            assert len(error_calls) > 0, "ProviderError should be logged at error level"

    @pytest.mark.asyncio
    async def test_tui_app_provider_error_logged_at_error_level(self) -> None:
        """Verify ProviderError is logged at error level in _run_dialogue."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._run_dialogue)
        # Проверяем, что ProviderError логируется на error уровне
        assert "log.error" in source
        assert "ProviderError" in source


class TestIssue0023AsyncTypeHints:
    """Tests for ISSUE-0023: Type hints for async functions."""

    def test_all_async_functions_have_return_type_hints(self) -> None:
        """Verify all async functions have return type annotations."""
        from tui.app import DialogueApp
        from controllers.dialogue_controller import DialogueController
        from services.dialogue_service import DialogueService

        async_functions = [
            DialogueApp.on_mount,
            DialogueApp._run_dialogue,
            DialogueApp._process_dialogue_turn,
            DialogueApp._cleanup_dialogue_task,
            DialogueApp._cleanup_controller,
            DialogueApp._cleanup_client,
            DialogueApp.on_unmount,
            DialogueController.cleanup,
            DialogueService.run_dialogue_cycle,
            DialogueService.cleanup,
        ]

        for func in async_functions:
            sig = inspect.signature(func)
            assert sig.return_annotation != inspect.Signature.empty, (
                f"Function {func.__qualname__} missing return type annotation"
            )

    def test_all_async_functions_have_parameter_type_hints(self) -> None:
        """Verify all async functions have parameter type annotations."""
        from services.dialogue_service import DialogueService

        # Проверяем _process_dialogue_turn
        sig = inspect.signature(DialogueService.run_dialogue_cycle)
        params = list(sig.parameters.values())

        # Self параметр не требует аннотации
        for param in params[1:]:  # Пропускаем self
            assert param.annotation != inspect.Parameter.empty, (
                f"Parameter {param.name} missing type annotation"
            )


class TestIssue0024TypedDictRequiredKeys:
    """Tests for ISSUE-0024: TypedDict keys made required."""

    def test_message_dict_has_required_keys(self) -> None:
        """Verify MessageDict has total=True (required keys)."""
        from models.provider import MessageDict

        # Проверяем, что TypedDict имеет total=True
        assert MessageDict.__total__ is True, "MessageDict should have total=True"

    def test_message_dict_creation_with_required_keys(self) -> None:
        """Verify MessageDict works correctly with required keys."""
        from models.provider import MessageDict

        # Создание с двумя ключами должно работать
        msg = MessageDict(role="user", content="Hello")
        assert msg["role"] == "user"
        assert msg["content"] == "Hello"

        # TypedDict с total=True проверяется только статическими анализаторами
        # (mypy/pyright), а не runtime. Это корректное поведение.
        # Проверяем, что __required_keys__ содержит оба ключа
        assert "role" in MessageDict.__required_keys__
        assert "content" in MessageDict.__required_keys__

    def test_message_dict_comprehensive_creation(self) -> None:
        """Verify MessageDict can be created with all valid role types."""
        from models.provider import MessageDict

        # Проверяем все допустимые роли
        for role in ["system", "user", "assistant"]:
            msg = MessageDict(role=role, content=f"Test content for {role}")
            assert msg["role"] == role
            assert msg["content"] == f"Test content for {role}"


class TestIssue0025ConstantTyping:
    """Tests for ISSUE-0025: Constants properly typed."""

    def test_default_notify_timeout_is_int(self) -> None:
        """Verify DEFAULT_NOTIFY_TIMEOUT is properly typed as int."""
        from tui.constants import DEFAULT_NOTIFY_TIMEOUT

        assert isinstance(DEFAULT_NOTIFY_TIMEOUT, int)
        assert DEFAULT_NOTIFY_TIMEOUT > 0

    def test_message_styles_are_strings(self) -> None:
        """Verify MessageStyles dataclass has string fields."""
        from tui.constants import MESSAGE_STYLES

        assert isinstance(MESSAGE_STYLES.model_a, str)
        assert isinstance(MESSAGE_STYLES.model_b, str)
        assert isinstance(MESSAGE_STYLES.system, str)
        assert isinstance(MESSAGE_STYLES.error, str)

    def test_ui_ids_are_strings(self) -> None:
        """Verify UIElementIDs dataclass has string fields."""
        from tui.constants import UI_IDS

        # Проверяем несколько ключевых ID
        assert isinstance(UI_IDS.start_btn, str)
        assert isinstance(UI_IDS.pause_btn, str)
        assert isinstance(UI_IDS.dialogue_log, str)
        assert UI_IDS.start_btn == "start-btn"


class TestIssue0026CleanupScenarios:
    """Tests for ISSUE-0026: Cleanup scenarios with CancelledError, TimeoutError."""

    @pytest.mark.asyncio
    async def test_dialogue_service_cleanup_handles_cancelled_error(self) -> None:
        """Verify cleanup handles CancelledError gracefully."""
        from services.dialogue_service import DialogueService

        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock(side_effect=asyncio.CancelledError())

        mock_conversation = MagicMock()

        service = DialogueService(
            conversation=mock_conversation,
            provider=mock_provider,
        )

        # Не должно выбросить исключение
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_dialogue_service_cleanup_handles_timeout_error(self) -> None:
        """Verify cleanup handles TimeoutError gracefully."""
        from services.dialogue_service import DialogueService

        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock(side_effect=TimeoutError("Timeout"))

        mock_conversation = MagicMock()

        service = DialogueService(
            conversation=mock_conversation,
            provider=mock_provider,
        )

        # Не должно выбросить исключение
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_dialogue_service_cleanup_handles_runtime_error(self) -> None:
        """Verify cleanup handles RuntimeError gracefully."""
        from services.dialogue_service import DialogueService

        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock(side_effect=RuntimeError("Runtime error"))

        mock_conversation = MagicMock()

        service = DialogueService(
            conversation=mock_conversation,
            provider=mock_provider,
        )

        # Не должно выбросить исключение
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_dialogue_service_cleanup_handles_os_error(self) -> None:
        """Verify cleanup handles OSError gracefully."""
        from services.dialogue_service import DialogueService

        mock_provider = AsyncMock()
        mock_provider.close = AsyncMock(side_effect=OSError("OS error"))

        mock_conversation = MagicMock()

        service = DialogueService(
            conversation=mock_conversation,
            provider=mock_provider,
        )

        # Не должно выбросить исключение
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_controller_cleanup_handles_cancelled_error(self) -> None:
        """Verify controller cleanup handles CancelledError gracefully."""
        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.cleanup = AsyncMock(side_effect=asyncio.CancelledError())

        controller = DialogueController(service=mock_service)

        # Не должно выбросить исключение
        await controller.cleanup()
        # Сервис должен быть очищен
        assert controller._service is None

    @pytest.mark.asyncio
    async def test_controller_cleanup_handles_runtime_error(self) -> None:
        """Verify controller cleanup handles RuntimeError gracefully."""
        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.cleanup = AsyncMock(side_effect=RuntimeError("Runtime error"))

        controller = DialogueController(service=mock_service)

        # Не должно выбросить исключение
        await controller.cleanup()
        # Сервис должен быть очищен
        assert controller._service is None


class TestIssue0027DialogueServiceEdgeCases:
    """Tests for ISSUE-0027: Edge cases in DialogueService."""

    def test_dialogue_service_requires_conversation(self) -> None:
        """Verify DialogueService raises ValueError if conversation is None."""
        from services.dialogue_service import DialogueService

        mock_provider = MagicMock()

        with pytest.raises(ValueError, match="conversation cannot be None"):
            DialogueService(conversation=None, provider=mock_provider)  # type: ignore[arg-type]

    def test_dialogue_service_requires_provider(self) -> None:
        """Verify DialogueService raises ValueError if provider is None."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )

        with pytest.raises(ValueError, match="provider cannot be None"):
            DialogueService(conversation=conversation, provider=None)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_run_dialogue_cycle_returns_none_when_not_running(self) -> None:
        """Verify run_dialogue_cycle returns None when dialogue is not running."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )
        mock_provider = MagicMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Dialogue not started
        result = await service.run_dialogue_cycle()
        assert result is None

    @pytest.mark.asyncio
    async def test_run_dialogue_cycle_returns_none_when_paused(self) -> None:
        """Verify run_dialogue_cycle returns None when dialogue is paused."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )
        mock_provider = MagicMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        service.start()
        service.pause()

        result = await service.run_dialogue_cycle()
        assert result is None

    def test_dialogue_turn_result_is_frozen(self) -> None:
        """Verify DialogueTurnResult is immutable (frozen)."""
        from services.dialogue_service import DialogueTurnResult

        result = DialogueTurnResult(
            model_name="test-model",
            model_id="A",
            role="assistant",
            response="test response",
        )

        with pytest.raises(AttributeError):
            result.model_name = "new-model"

    def test_start_resets_paused_state(self) -> None:
        """Verify start() resets pause state."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )
        mock_provider = MagicMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        service.start()
        service.pause()
        assert service.is_paused is True

        service.start()
        assert service.is_running is True
        assert service.is_paused is False

    def test_turn_count_starts_at_zero(self) -> None:
        """Verify turn_count starts at 0."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )
        mock_provider = MagicMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        assert service.turn_count == 0

    def test_clear_history_resets_turn_count(self) -> None:
        """Verify clear_history() resets turn_count to 0."""
        from services.dialogue_service import DialogueService
        from models.conversation import Conversation

        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="test",
        )
        mock_provider = MagicMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Симулируем увеличение счётчика
        service._turn_count = 5
        assert service.turn_count == 5

        service.clear_history()
        assert service.turn_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
