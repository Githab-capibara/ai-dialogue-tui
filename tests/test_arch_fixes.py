"""Тесты для проверки архитектурных изменений.

Note:
    Тесты используют импорты внутри функций для проверки модульной структуры.

"""

# pylint: disable=import-outside-toplevel

import logging

import pytest

from models.conversation import Conversation


class TestSanitizerModule:
    """Тесты для проверки модуля санитизации."""

    def test_sanitizer_module_exists(self) -> None:
        """Тест, что модуль sanitizer существует и импортируется."""
        from tui import sanitizer

        assert hasattr(sanitizer, "sanitize_topic")
        assert hasattr(sanitizer, "sanitize_response_for_display")

    def test_sanitize_topic_escapes_braces(self) -> None:
        """Тест, что sanitize_topic экранирует фигурные скобки."""
        from tui.sanitizer import sanitize_topic

        result = sanitize_topic("test {topic}")
        assert "{{" in result
        assert "}}" in result
        assert result == "test {{topic}}"

    def test_sanitize_topic_strips_whitespace(self) -> None:
        """Тест, что sanitize_topic удаляет пробелы."""
        from tui.sanitizer import sanitize_topic

        result = sanitize_topic("  test topic  ")
        assert result == "test topic"

    def test_sanitize_response_escapes_html(self) -> None:
        """Тест, что sanitize_response_for_display экранирует HTML."""
        from tui.sanitizer import sanitize_response_for_display

        result = sanitize_response_for_display("<script>alert(1)</script>")
        assert "<" not in result

    def test_sanitize_response_replaces_newlines(self) -> None:
        """Тест, что sanitize_response_for_display заменяет переносы строк."""
        from tui.sanitizer import sanitize_response_for_display

        result = sanitize_response_for_display("line1\nline2")
        assert "\n" not in result

    def test_sanitize_response_truncates_long_text(self) -> None:
        """Тест, что sanitize_response_for_display обрезает длинный текст."""
        from tui.sanitizer import sanitize_response_for_display

        long_text = "a" * 200
        result = sanitize_response_for_display(long_text)
        assert len(result) <= 110


class TestConversationLogging:
    """Тесты для проверки логирования в Conversation."""

    def test_conversation_module_has_logger(self) -> None:
        """Тест, что модуль conversation имеет logger."""
        from models import conversation as conversation_module

        assert hasattr(conversation_module, "log")
        assert isinstance(conversation_module.log, logging.Logger)

    def test_conversation_logger_name(self) -> None:
        """Тест, что logger имеет правильное имя."""
        from models import conversation as conversation_module

        assert conversation_module.log.name == "models.conversation"

    def test_conversation_add_message_logs(self, caplog: pytest.LogCaptureFixture) -> None:
        """Тест, что add_message логирует добавление сообщения."""
        with caplog.at_level(logging.DEBUG):
            conv = Conversation("model_a", "model_b", "test_topic")
            conv.add_message("A", "user", "test message")

        assert any("Added" in record.message for record in caplog.records)


class TestArchitecturalBoundaries:
    """Тесты для проверки границ модулей."""

    def test_sanitizer_not_in_app(self) -> None:
        """Тест, что функции санитизации не находятся в app.py."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "def sanitize_topic" not in source
        assert "def sanitize_response_for_display" not in source

    def test_sanitizer_imported_in_app(self) -> None:
        """Тест, что sanitizer импортируется в app.py."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui.sanitizer import" in source

    def test_conversation_no_direct_ollama_import(self) -> None:
        """Тест, что Conversation не импортирует OllamaClient."""
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        assert "OllamaClient" not in source
        assert "from models.ollama_client" not in source

    def test_services_no_tui_import(self) -> None:
        """Тест, что services не импортирует tui."""
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source

    def test_controllers_no_tui_import(self) -> None:
        """Тест, что controllers не импортирует tui."""
        with open("controllers/dialogue_controller.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source
