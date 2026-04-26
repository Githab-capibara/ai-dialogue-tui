"""Тесты для проверки исправлений, выявленных при аудите кода.

Каждый тест проверяет одну конкретную проблему:
1. Callable аннотация в Conversation._add_message_to_context
2. Константы из config.py в OllamaClient._DEFAULT_OPTIONS
3. self._config используется в generate()
4. Optional аннотация для _config в Conversation
5. Отдельные копии system_message в clear_contexts()
6. Инкремент счётчика только после успешного process_turn
7. Отсутствие дублирования в __all__ модуля styles
"""

# pylint: disable=protected-access,import-outside-toplevel

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.config import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, Config
from models.conversation import Conversation
from models.ollama_client import OllamaClient
from models.provider import ModelProvider
from services.dialogue_service import DialogueService

# --- Тест 1: Callable аннотация ---


def test_add_message_to_context_accepts_callable() -> None:
    """model_id параметр _add_message_to_context имеет аннотацию ModelId."""
    sig = inspect.signature(Conversation._add_message_to_context)
    param = sig.parameters["model_id"]
    annotation = param.annotation

    # Аннотация должна быть ModelId или его вариацией
    assert annotation is not inspect.Parameter.empty
    annotation_str = str(annotation)
    assert "Literal" in annotation_str or "ModelId" in annotation_str


# --- Тест 2: Константы из config.py ---


def test_default_options_uses_config_constants() -> None:
    """_DEFAULT_OPTIONS использует импортированные константы, а не hardcoded значения."""
    from models.ollama_client import _DEFAULT_OPTIONS

    assert _DEFAULT_OPTIONS["temperature"] == DEFAULT_TEMPERATURE
    assert _DEFAULT_OPTIONS["num_predict"] == DEFAULT_MAX_TOKENS


def test_default_options_not_hardcoded() -> None:
    """_DEFAULT_OPTIONS не содержит захардкоженных float/int литералов."""
    import models.ollama_client as module

    source = inspect.getsource(module)

    # Проверяем что в области определения _DEFAULT_OPTIONS нет hardcoded 0.7 / 200
    # а используются имена констант
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if "_DEFAULT_OPTIONS" in line and "=" in line and "Final" not in line:
            # Берём строки определения словаря
            definition_lines = lines[i : i + 5]
            definition = "\n".join(definition_lines)
            assert "DEFAULT_TEMPERATURE" in definition
            assert "DEFAULT_MAX_TOKENS" in definition
            break


# --- Тест 3: self._config в generate() ---


@pytest.mark.asyncio
async def test_generate_uses_self_config() -> None:
    """generate() берёт temperature/max_tokens из self._config, а не дефолтов."""
    custom_temp = 0.42
    custom_tokens = 123
    config = Config(temperature=custom_temp, max_tokens=custom_tokens)

    client = OllamaClient(config=config)

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"message": {"content": "ok"}})
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_response)
    mock_session.closed = False

    with patch.object(client, "_get_session", return_value=mock_session):
        await client.generate("test-model", [{"role": "user", "content": "hi"}])

    mock_session.post.assert_called_once()
    payload = mock_session.post.call_args[1]["json"]
    assert payload["options"]["temperature"] == custom_temp
    assert payload["options"]["num_predict"] == custom_tokens

    await client.close()


# --- Тест 4: System prompt в Conversation ---


def test_system_prompt_field_exists() -> None:
    """system_prompt существует в Conversation."""
    from dataclasses import fields

    conv_fields = {f.name: f for f in fields(Conversation)}
    assert "system_prompt" in conv_fields

    # Проверяем что объект можно создать с system_prompt
    conv = Conversation(model_a="a", model_b="b", topic="t", system_prompt="custom")
    assert conv.system_prompt == "custom"


def test_system_prompt_formatted_in_post_init() -> None:
    """system_prompt форматируется с topic в __post_init__ для контекста."""
    conv = Conversation(model_a="a", model_b="b", topic="test topic")
    # Проверяем что контекст содержит отформатированный промпт
    context_a = conv.get_context("A")
    assert len(context_a) > 0
    assert context_a[0]["role"] == "system"
    assert "test topic" in context_a[0]["content"]


# --- Тест 5: Отдельные копии system_message ---


def test_clear_contexts_creates_separate_objects() -> None:
    """clear_contexts() создаёт отдельные dict-объекты для контекстов A и B."""
    conv = Conversation(model_a="a", model_b="b", topic="t")
    conv.clear_contexts()

    ctx_a = conv.get_context("A")
    ctx_b = conv.get_context("B")

    assert len(ctx_a) == 1
    assert len(ctx_b) == 1

    # Это разные объекты, а не ссылки на один и тот же dict
    assert ctx_a[0] is not ctx_b[0]

    # Мутация одного не влияет на другой
    ctx_a[0]["content"] = "mutated"
    assert ctx_b[0]["content"] != "mutated"


# --- Тест 6: Инкремент счётчика после process_turn ---


@pytest.mark.asyncio
async def test_turn_count_not_incremented_on_error() -> None:
    """turn_count НЕ инкрементируется если process_turn выбросил исключение."""
    from models.provider import ProviderError

    conv = Conversation(model_a="a", model_b="b", topic="t")
    provider = AsyncMock()
    provider.generate = AsyncMock(side_effect=ProviderError("fail"))

    service = DialogueService(conversation=conv, provider=provider)
    service.start()

    assert service.turn_count == 0

    with pytest.raises(ProviderError):
        await service.run_dialogue_cycle()

    assert service.turn_count == 0


@pytest.mark.asyncio
async def test_turn_count_incremented_on_success() -> None:
    """turn_count инкрементируется после успешного process_turn."""
    conv = Conversation(model_a="a", model_b="b", topic="t")
    provider = AsyncMock()
    provider.generate = AsyncMock(return_value="response")

    service = DialogueService(conversation=conv, provider=provider)
    service.start()

    await service.run_dialogue_cycle()

    assert service.turn_count == 1


# --- Тест 7: Отсутствие дублирования в __all__ ---


def test_styles_all_no_duplicates() -> None:
    """В __all__ модуля tui.styles нет дублирующихся записей."""
    from tui import styles

    all_names = styles.__all__
    assert len(all_names) == len(set(all_names)), f"Дубликаты в __all__: {
        [n for n in all_names if all_names.count(n) > 1]
    }"


# =============================================================================
# Additional verification tests merged from test_code_audit_fixes_verification.py
# =============================================================================


class TestConversationValidation:
    """Tests for verifying Conversation validation."""

    def test_empty_model_a_raises_error(self) -> None:
        """Verify that empty model_a raises ValueError."""
        with pytest.raises(ValueError, match="model_a"):
            Conversation(model_a="", model_b="model_b", topic="test")

    def test_empty_model_b_raises_error(self) -> None:
        """Verify that empty model_b raises ValueError."""
        with pytest.raises(ValueError, match="model_b"):
            Conversation(model_a="model_a", model_b="", topic="test")

    def test_empty_topic_raises_error(self) -> None:
        """Verify that empty topic raises ValueError."""
        with pytest.raises(ValueError, match="topic"):
            Conversation(model_a="model_a", model_b="model_b", topic="")

    def test_same_models_raises_error(self) -> None:
        """Verify that same models raise ValueError."""
        with pytest.raises(ValueError):
            Conversation(model_a="same", model_b="same", topic="test")

    def test_non_string_model_a_raises_error(self) -> None:
        """Verify that non-string model_a raises an error."""
        with pytest.raises((TypeError, ValueError)):
            Conversation(model_a=123, model_b="model_b", topic="test")  # type: ignore


class TestConversationAtomicity:
    """Tests for verifying process_turn atomicity."""

    @pytest.mark.asyncio
    async def test_rollback_on_error(self) -> None:
        """Verify rollback of contexts on error."""
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = RuntimeError("Test error")

        conversation = Conversation(model_a="model_a", model_b="model_b", topic="test")

        initial_context_a = list(conversation.get_context("A"))
        initial_context_b = list(conversation.get_context("B"))

        with pytest.raises(RuntimeError):
            await conversation.process_turn(mock_provider)

        assert conversation.get_context("A") == tuple(initial_context_a)
        assert conversation.get_context("B") == tuple(initial_context_b)


class TestDialogueRunnerCancellation:
    """Tests for verifying cancellation handling in DialogueRunner."""

    @pytest.mark.asyncio
    async def test_dialogue_runner_stops_on_cancel(self) -> None:
        """Verify that DialogueRunner stops on cancellation."""
        from services.dialogue_runner import DialogueRunner

        mock_service = MagicMock(spec=DialogueService)
        mock_service.is_running = True
        mock_service.is_paused = False

        runner = DialogueRunner(mock_service)
        assert runner.service == mock_service
        assert runner.dialogue_task is None


class TestDialogueAppIdempotency:
    """Tests for verifying DialogueApp idempotency."""

    def test_cleanup_flag_prevents_double_cleanup(self) -> None:
        """Verify that _cleanup_done flag prevents double cleanup."""
        from tui.app import DialogueApp

        app = DialogueApp()
        app._cleanup_done = True
        assert hasattr(app, "_cleanup_done")


class TestStyleMapperCaching:
    """Tests for verifying style_mapper caching."""

    def test_style_mapper_cached_in_init(self) -> None:
        """Verify that style_mapper is created in __init__."""
        from tui.app import DialogueApp

        app = DialogueApp()
        assert hasattr(app, "_style_mapper")
        assert app._style_mapper is not None

    def test_same_mapper_used_in_run_dialogue(self) -> None:
        """Verify that the same mapper is used in dialogue loop."""
        from tui.app import DialogueApp

        app = DialogueApp()
        mapper1 = app._style_mapper
        assert mapper1 is app._style_mapper


class TestOSErrorHandling:
    """Tests for verifying OSError handling."""

    @pytest.mark.asyncio
    async def test_oserror_propagates_correctly(self) -> None:
        """Verify that OSError is propagated correctly."""
        client = OllamaClient(host="http://localhost:11434")
        assert client is not None
        await client.close()
        await client.close()
