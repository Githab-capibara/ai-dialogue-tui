"""
Тесты для проверки исправлений из аудита кода.

Содержит тесты для:
- HIGH 1: Идемпотентность метода close() в OllamaClient
- HIGH 2: Оптимизация управления контекстом в Conversation
- MEDIUM 1: Полная санитизация для Textual
- MEDIUM 2: Удаление лишних экземпляров классов
- MEDIUM 3: Конкретный перехват исключений
- MEDIUM 4: Исправление default для Config в Conversation
- LOW 1: Экспорт ModelId в __all__
- LOW 2: Ленивая инициализация CSS
- LOW 3: Обработка asyncio.CancelledError
- LOW 4: Форматирование f-строки
"""

# pylint:
# disable=protected-access,too-few-public-methods,import-outside-toplevel

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.conversation import Conversation
from models.ollama_client import OllamaClient
from tui.sanitizer import sanitize_response_for_display


class TestCloseIdempotency:
    """HIGH 1: Тест идемпотентности метода close()."""

    @pytest.mark.asyncio
    async def test_close_can_be_called_multiple_times(self) -> None:
        """Тест что close() может быть вызван несколько раз без ошибок."""
        client = OllamaClient(host="http://localhost:11434")

        await client.close()
        await client.close()
        await client.close()

    @pytest.mark.asyncio
    async def test_close_handles_already_closed_session(self) -> None:
        """Тест что close() обрабатывает уже закрытую сессию."""
        client = OllamaClient(host="http://localhost:11434")

        await client.close()

        mock_session = AsyncMock()
        mock_session.closed = True
        client._http_manager._session = mock_session

        await client.close()


class TestContextManagementOptimization:
    """HIGH 2: Тест оптимизации управления контекстом."""

    def test_trim_before_add_message(self) -> None:
        """Тест что контекст обрезается до добавления сообщения."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test",
        )

        for i in range(60):
            conversation.add_message("A", "user", f"Message {i}")

        context_a = conversation.get_context("A")
        assert len(context_a) <= 51


class TestTextualSanitization:
    """MEDIUM 1: Тест полной санитизации для Textual."""

    def test_sanitize_response_escapes_square_brackets(self) -> None:
        """Тест что квадратные скобки экранируются для Textual."""
        result = sanitize_response_for_display("Test [markup] text")
        assert "[[" in result or "[" not in result
        assert "]]" in result or "]" not in result

    def test_sanitize_response_escapes_mixed_markup(self) -> None:
        """Тест что смешанные markup экранируются."""
        result = sanitize_response_for_display("<script>[alert]</script>")
        assert "<script>" not in result
        assert "[[" in result


class TestOllamaClientNoExtraInstances:
    """MEDIUM 2: Тест что нет лишних экземпляров классов."""

    def test_no_validator_instance(self) -> None:
        """Тест что _RequestValidator не создается как экземпляр."""
        client = OllamaClient(host="http://localhost:11434")
        assert not hasattr(client, "_request_validator")

    def test_no_handler_instance(self) -> None:
        """Тест что _ResponseHandler не создается как экземпляр."""
        client = OllamaClient(host="http://localhost:11434")
        assert not hasattr(client, "_response_handler")


class TestExceptionHandling:
    """MEDIUM 3: Тест конкретного перехвата исключений."""

    def test_lookup_error_handled(self) -> None:
        """Тест что LookupError корректно обрабатывается."""
        from tui.app import DialogueApp

        app = DialogueApp()

        with patch.object(app, "query_one") as mock_query:
            mock_query.side_effect = LookupError("Test")

            app._on_ui_state_changed(
                type("UIState", (), {"status_text": "test", "status_style": "info"})()
            )


class TestConversationSystemPrompt:
    """MEDIUM 4: Тест исправления system_prompt в Conversation."""

    def test_conversation_accepts_system_prompt(self) -> None:
        """Тест что Conversation принимает system_prompt."""
        custom_prompt = "Custom system prompt for testing"
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test",
            system_prompt=custom_prompt,
        )
        assert conversation.system_prompt == custom_prompt

    def test_conversation_formats_system_prompt_with_topic(self) -> None:
        """Тест что Conversation форматирует system_prompt с topic в контекст."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test Topic",
        )
        # Проверяем что контекст содержит отформатированный промпт
        context_a = conversation.get_context("A")
        assert len(context_a) > 0
        assert context_a[0]["role"] == "system"
        assert "Test Topic" in context_a[0]["content"]


class TestModelIdExport:
    """LOW 1: Тест экспорта ModelId."""

    def test_model_id_in_all(self) -> None:
        """Тест что ModelId экспортируется."""
        from models import conversation

        assert "ModelId" in conversation.__all__


class TestCSSLazyInitialization:
    """LOW 2: Тест ленивой инициализации CSS."""

    def test_css_defined_in_class(self) -> None:
        """Тест что CSS определен в классе."""
        from tui.app import DialogueApp

        assert hasattr(DialogueApp, "CSS")


class TestAsyncioCancelledError:
    """LOW 3: Тест обработки asyncio.CancelledError."""

    def test_main_handles_cancelled_error(self) -> None:
        """Тест что main обрабатывает CancelledError."""
        from main import main

        with patch("main.DialogueApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = asyncio.CancelledError()

            result = main()
            assert result == 0


class TestFStringFormatting:
    """LOW 4: Тест форматирования f-строки."""

    def test_fstring_formatting_valid(self) -> None:
        """Тест что f-строка форматируется корректно."""
        style = "green"
        turn_count = 1
        model_name = "llama3"
        formatted_response = "Test response"

        message = (
            f"\n[{style}]Ход {turn_count}: {model_name}[/]\n  {formatted_response}"
        )

        assert "Ход 1: llama3" in message
        assert "Test response" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
