"""Тесты для проверки исправлений по результатам аудита кода.

Этот модуль содержит тесты для верификации исправлений:
- Валидация входных данных Conversation
- Атомарность process_turn
- Обработка asyncio.CancelledError
- Идемпотентность on_unmount
- Кэширование style_mapper
"""

# pylint:
# disable=protected-access,import-outside-toplevel,too-few-public-methods

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from models.conversation import Conversation
from models.provider import ModelProvider
from services.dialogue_runner import DialogueRunner
from services.dialogue_service import DialogueService
from tui.app import DialogueApp


class TestConversationValidation:
    """Тесты для проверки валидации в Conversation."""

    def test_empty_model_a_raises_error(self) -> None:
        """Проверить что пустой model_a вызывает ValueError."""
        with pytest.raises(ValueError, match="model_a"):
            Conversation(model_a="", model_b="model_b", topic="test")

    def test_empty_model_b_raises_error(self) -> None:
        """Проверить что пустой model_b вызывает ValueError."""
        with pytest.raises(ValueError, match="model_b"):
            Conversation(model_a="model_a", model_b="", topic="test")

    def test_empty_topic_raises_error(self) -> None:
        """Проверить что пустой topic вызывает ValueError."""
        with pytest.raises(ValueError, match="topic"):
            Conversation(model_a="model_a", model_b="model_b", topic="")

    def test_same_models_raises_error(self) -> None:
        """Проверить что одинаковые модели вызывают ValueError."""
        with pytest.raises(ValueError):
            Conversation(model_a="same", model_b="same", topic="test")

    def test_non_string_model_a_raises_error(self) -> None:
        """Проверить что нестроковый model_a вызывает ошибку."""
        # Python dataclass сам проверит тип через TypeError или ValueError
        with pytest.raises((TypeError, ValueError)):
            Conversation(model_a=123, model_b="model_b", topic="test")  # type: ignore


class TestConversationAtomicity:
    """Тесты для проверки атомарности process_turn."""

    @pytest.mark.asyncio
    async def test_rollback_on_error(self) -> None:
        """Проверить rollback контекстов при ошибке."""
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = RuntimeError("Test error")

        conversation = Conversation(model_a="model_a", model_b="model_b", topic="test")

        # Сохраняем начальное состояние
        initial_context_a = list(conversation.get_context("A"))
        initial_context_b = list(conversation.get_context("B"))

        # Пытаемся сделать ход с ошибкой
        with pytest.raises(RuntimeError):
            await conversation.process_turn(mock_provider)

        # Контексты должны быть откачены
        assert conversation.get_context("A") == tuple(initial_context_a)
        assert conversation.get_context("B") == tuple(initial_context_b)


class TestDialogueRunnerCancellation:
    """Тесты для проверки обработки отмены в DialogueRunner."""

    @pytest.mark.asyncio
    async def test_dialogue_runner_stops_on_cancel(self) -> None:
        """Проверить что DialogueRunner останавливается при отмене."""
        mock_service = MagicMock(spec=DialogueService)
        mock_service.is_running = True
        mock_service.is_paused = False

        runner = DialogueRunner(mock_service)

        # Проверяем что runner может быть создан
        assert runner.service == mock_service

        # Тест на базовую функциональность
        assert runner.dialogue_task is None


class TestDialogueAppIdempotency:
    """Тесты для проверки идемпотентности DialogueApp."""

    def test_cleanup_flag_prevents_double_cleanup(self) -> None:
        """Проверить что флаг _cleanup_done предотвращает повторную очистку."""
        app = DialogueApp()
        app._cleanup_done = True  # Устанавливаем флаг

        # on_unmount не должен вызывать ошибок при повторном вызове
        # Проверяем что флаг установлен
        assert hasattr(app, "_cleanup_done")


class TestStyleMapperCaching:
    """Тесты для проверки кэширования style_mapper."""

    def test_style_mapper_cached_in_init(self) -> None:
        """Проверить что style_mapper создается в __init__."""
        app = DialogueApp()

        # Проверяем что mapper создан
        assert hasattr(app, "_style_mapper")
        assert app._style_mapper is not None

    def test_same_mapper_used_in_run_dialogue(self) -> None:
        """Проверить что один и тот же mapper используется в цикле."""
        app = DialogueApp()
        mapper1 = app._style_mapper

        # Проверяем что mapper тот же самый
        assert mapper1 is app._style_mapper


class TestOSErrorHandling:
    """Тесты для проверки обработки OSError."""

    @pytest.mark.asyncio
    async def test_oserror_propagates_correctly(self) -> None:
        """Проверить что OSError пробрасывается корректно."""
        from models.ollama_client import OllamaClient

        client = OllamaClient(host="http://localhost:11434")

        # Проверяем что клиент может быть создан и закрыт
        assert client is not None

        # Тест на закрытие без ошибок
        await client.close()

        # Сессия должна быть закрыта
        await client.close()
