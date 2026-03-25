"""Тесты для проверки архитектурных изменений.

Note:
    Тесты используют импорты внутри функций для проверки модульной структуры.
"""

# pylint: disable=import-outside-toplevel

import logging

from models.conversation import Conversation


class TestSanitizerModule:
    """Тесты для проверки модуля санитизации."""

    def test_sanitizer_module_exists(self):
        """Тест, что модуль sanitizer существует и импортируется."""
        from tui import sanitizer

        assert hasattr(sanitizer, "sanitize_topic")
        assert hasattr(sanitizer, "sanitize_response_for_display")

    def test_sanitize_topic_escapes_braces(self):
        """Тест, что sanitize_topic экранирует фигурные скобки."""
        from tui.sanitizer import sanitize_topic

        result = sanitize_topic("test {topic}")
        assert "{{" in result
        assert "}}" in result
        assert result == "test {{topic}}"

    def test_sanitize_topic_strips_whitespace(self):
        """Тест, что sanitize_topic удаляет пробелы."""
        from tui.sanitizer import sanitize_topic

        result = sanitize_topic("  test topic  ")
        assert result == "test topic"

    def test_sanitize_response_escapes_html(self):
        """Тест, что sanitize_response_for_display экранирует HTML."""
        from tui.sanitizer import sanitize_response_for_display

        result = sanitize_response_for_display("<script>alert(1)</script>")
        assert "<" not in result

    def test_sanitize_response_replaces_newlines(self):
        """Тест, что sanitize_response_for_display заменяет переносы строк."""
        from tui.sanitizer import sanitize_response_for_display

        result = sanitize_response_for_display("line1\nline2")
        assert "\n" not in result

    def test_sanitize_response_truncates_long_text(self):
        """Тест, что sanitize_response_for_display обрезает длинный текст."""
        from tui.sanitizer import sanitize_response_for_display

        long_text = "a" * 200
        result = sanitize_response_for_display(long_text)
        assert len(result) <= 110


class TestStatusStyleEnum:
    """Тесты для проверки StatusStyle enum."""

    def test_status_style_enum_exists(self):
        """Тест, что StatusStyle enum существует."""
        from tui.styles import StatusStyle

        assert hasattr(StatusStyle, "INFO")
        assert hasattr(StatusStyle, "SUCCESS")
        assert hasattr(StatusStyle, "WARNING")
        assert hasattr(StatusStyle, "ERROR")

    def test_status_style_values(self):
        """Тест, что StatusStyle имеет правильные строковые значения."""
        from tui.styles import StatusStyle

        assert StatusStyle.INFO.value == "info"
        assert StatusStyle.SUCCESS.value == "success"
        assert StatusStyle.WARNING.value == "warning"
        assert StatusStyle.ERROR.value == "error"

    def test_get_status_style_string_function_exists(self):
        """Тест, что функция _get_status_style_string существует в app."""
        from tui.app import _get_status_style_string

        assert callable(_get_status_style_string)


class TestConversationLogging:
    """Тесты для проверки логирования в Conversation."""

    def test_conversation_module_has_logger(self):
        """Тест, что модуль conversation имеет logger."""
        from models import conversation as conversation_module

        assert hasattr(conversation_module, "log")
        assert isinstance(conversation_module.log, logging.Logger)

    def test_conversation_logger_name(self):
        """Тест, что logger имеет правильное имя."""
        from models import conversation as conversation_module

        assert conversation_module.log.name == "models.conversation"

    def test_conversation_add_message_logs(self, caplog):
        """Тест, что add_message логирует добавление сообщения."""

        with caplog.at_level(logging.DEBUG):
            conv = Conversation("model_a", "model_b", "test_topic")
            conv.add_message("A", "user", "test message")

        assert any("Added" in record.message for record in caplog.records)


class TestOllamaClientFactory:
    """Тест для проверки фабрики OllamaClient."""

    def test_create_ollama_client_function_exists(self):
        """Тест, что функция create_ollama_client существует."""
        from tui.app import create_ollama_client

        assert callable(create_ollama_client)

    def test_create_ollama_client_returns_client(self):
        """Тест, что create_ollama_client возвращает клиент."""
        from tui.app import create_ollama_client

        host = "http://localhost:11434"
        client = create_ollama_client(host)

        assert client is not None
        assert hasattr(client, "list_models")
        assert hasattr(client, "generate")


class TestArchitecturalBoundaries:
    """Тесты для проверки границ модулей."""

    def test_sanitizer_not_in_app(self):
        """Тест, что функции санитизации не находятся в app.py."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "def sanitize_topic" not in source
        assert "def sanitize_response_for_display" not in source

    def test_sanitizer_imported_in_app(self):
        """Тест, что sanitizer импортируется в app.py."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui.sanitizer import" in source

    def test_conversation_no_direct_ollama_import(self):
        """Тест, что Conversation не импортирует OllamaClient."""
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        assert "OllamaClient" not in source
        assert "from models.ollama_client" not in source

    def test_services_no_tui_import(self):
        """Тест, что services не импортирует tui."""
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source

    def test_controllers_no_tui_import(self):
        """Тест, что controllers не импортирует tui."""
        with open("controllers/dialogue_controller.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source
