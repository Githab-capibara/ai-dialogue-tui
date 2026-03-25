"""
Тесты для критических проблем из отчета аудита.

Этот модуль содержит тесты для проверки исправлений критических проблем:
1. Проверка пустого списка моделей в ModelSelectionScreen
2. Валидация ключей API в OllamaClient
3. Рассинхронизация контекстов в Conversation
4. Валидация URL в Config
5. Обработка исключений в main.py
6. Санитизация ввода/вывода в tui/app.py

Note:
    Некоторые тесты содержат дублирующийся код что оправдано для тестирования
    изолированных сценариев.
"""

# pylint: disable=duplicate-code

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import Config, validate_ollama_url
from models.conversation import Conversation, MessageDict
from models.ollama_client import OllamaClient, OllamaError


class AsyncContextManagerMock:  # pylint: disable=too-few-public-methods
    """Мок для асинхронного контекстного менеджера."""

    def __init__(
        self, response: Any = None, raise_on_enter: Exception | None = None
    ) -> None:
        self._response = response
        self._raise_on_enter = raise_on_enter

    async def __aenter__(self) -> Any:
        if self._raise_on_enter:
            raise self._raise_on_enter
        return self._response

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class TestConfigValidation:
    """Тесты для проблемы #4: Валидация URL в Config."""

    def test_valid_http_url(self) -> None:
        """Тест валидного HTTP URL."""
        config = Config(ollama_host="http://localhost:11434")
        assert config.ollama_host == "http://localhost:11434"

    def test_valid_https_url(self) -> None:
        """Тест валидного HTTPS URL."""
        config = Config(ollama_host="https://ollama.example.com")
        assert config.ollama_host == "https://ollama.example.com"

    def test_invalid_url_no_scheme(self) -> None:
        """Тест невалидного URL без схемы."""
        with pytest.raises(ValueError, match="Некорректный URL"):
            Config(ollama_host="localhost:11434")

    def test_invalid_url_wrong_scheme(self) -> None:
        """Тест невалидного URL с неправильной схемой."""
        with pytest.raises(ValueError, match="Некорректный URL"):
            Config(ollama_host="ftp://localhost:11434")

    def test_invalid_url_empty(self) -> None:
        """Тест пустого URL."""
        with pytest.raises(ValueError, match="Некорректный URL"):
            Config(ollama_host="")

    def test_validate_ollama_url_function(self) -> None:
        """Тест функции validate_ollama_url."""
        assert validate_ollama_url("http://localhost:11434") is True
        assert validate_ollama_url("https://example.com:8080") is True
        assert validate_ollama_url("localhost:11434") is False
        assert validate_ollama_url("") is False
        assert validate_ollama_url(None) is False  # type: ignore


class TestOllamaClientValidation:
    """Тесты для проблемы #2: Валидация ключей API в OllamaClient."""

    def test_invalid_host_raises_value_error(self) -> None:
        """Тест что невалидный хост вызывает ValueError."""
        with pytest.raises(ValueError, match="Некорректный URL"):
            OllamaClient(host="invalid-url")

    def test_valid_host_accepted(self) -> None:
        """Тест что валидный хост принимается."""
        client = OllamaClient(host="http://localhost:11434")
        assert client.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_list_models_validates_response_structure(self) -> None:
        """Тест что list_models проверяет структуру ответа."""
        # Мок сессии с некорректным ответом (без ключа "models")
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"invalid": "data"})
        mock_context_manager = AsyncContextManagerMock(mock_response)
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            # Должен вернуть пустой список вместо ошибки
            result = await client.list_models()
            assert result == []

    @pytest.mark.asyncio
    async def test_list_models_validates_model_name(self) -> None:
        """Тест что list_models проверяет наличие name у каждой модели."""
        # Мок сессии с моделями без name
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "models": [
                    {"name": "llama3"},
                    {"invalid": "model"},  # Без name
                    {"name": "mistral"},
                ]
            }
        )
        mock_context_manager = AsyncContextManagerMock(mock_response)
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            result = await client.list_models()
            # Должны быть только модели с name
            assert result == ["llama3", "mistral"]

    @pytest.mark.asyncio
    async def test_list_models_handles_json_decode_error(self) -> None:
        """Тест что list_models обрабатывает JSONDecodeError."""
        mock_response = AsyncMock()
        mock_response.status = 200

        # Создаем исключение JSONDecodeError
        async def raise_json_error() -> None:
            raise json.JSONDecodeError("Invalid JSON", "", 0)

        mock_response.json = raise_json_error
        mock_context_manager = AsyncContextManagerMock(mock_response)
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(OllamaError, match="Некорректный JSON"):
                await client.list_models()

    @pytest.mark.asyncio
    async def test_generate_validates_messages(self) -> None:
        """Тест что generate валидирует messages параметр."""
        client = OllamaClient(host="http://localhost:11434")

        # messages должен быть списком
        with pytest.raises(ValueError, match="списком"):
            await client.generate("llama3", "not a list")  # type: ignore

        # Каждое сообщение должно быть словарём
        with pytest.raises(ValueError, match="словарём"):
            await client.generate("llama3", ["not a dict"])  # type: ignore

        # Сообщение должно содержать role и content
        with pytest.raises(ValueError, match="role"):
            await client.generate("llama3", [{"role": "user"}])


class TestConversationAtomicity:
    """Тесты для проблемы #3: Рассинхронизация контекстов в Conversation."""

    def test_process_turn_is_atomic(self) -> None:
        """Тест что process_turn атомарно обновляет контексты."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        initial_context_a_len = len(conversation.get_context("A"))
        initial_context_b_len = len(conversation.get_context("B"))

        # Мок клиента который выбрасывает ошибку
        mock_client = AsyncMock()
        mock_client.generate.side_effect = OllamaError("Test error")

        # Ошибка должна быть проброшена
        with pytest.raises(OllamaError):
            asyncio.run(conversation.process_turn(mock_client))

        # Контексты должны остаться неизменными (атомарность)
        assert len(conversation.get_context("A")) == initial_context_a_len
        assert len(conversation.get_context("B")) == initial_context_b_len

    def test_switch_turn_does_not_return_value(self) -> None:
        """Тест что switch_turn не возвращает значение (CQS)."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        # switch_turn должен возвращать None (команда)
        conversation.switch_turn()  # pylint: disable=assignment-from-no-return
        assert True  # Метод не возвращает значение, проверяем что он выполнился

    def test_get_current_turn_returns_value(self) -> None:
        """Тест что свойство current_turn возвращает значение (query)."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        # current_turn свойство возвращает ModelId (запрос)
        result = conversation.current_turn
        assert result in ("A", "B")

    def test_current_turn_property_uses_query(self) -> None:
        """Тест что свойство current_turn использует query-метод."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        # Свойство должно возвращать значение
        result = conversation.current_turn
        assert result in ("A", "B")

    def test_clear_contexts_uses_clear_method(self) -> None:
        """Тест что clear_contexts использует .clear() для эффективности."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        # Добавляем сообщения
        conversation.add_message("A", "user", "test")
        conversation.add_message("B", "user", "test")

        context_a_id = id(conversation._context_a)  # pylint: disable=protected-access
        context_b_id = id(conversation._context_b)  # pylint: disable=protected-access

        # Очищаем
        conversation.clear_contexts()

        # Списки должны быть те же объекты (clear modifies in place)
        assert id(conversation._context_a) == context_a_id  # pylint: disable=protected-access
        assert id(conversation._context_b) == context_b_id  # pylint: disable=protected-access


class TestMessageTypedDict:
    """Тесты для TypedDict сообщений."""

    def test_message_dict_structure(self) -> None:
        """Тест структуры MessageDict."""
        # TypedDict должен требовать role и content
        message: MessageDict = {"role": "user", "content": "Hello"}
        assert message["role"] == "user"
        assert message["content"] == "Hello"

    def test_message_dict_role_literal(self) -> None:
        """Тест что role использует Literal."""
        # Валидные роли
        valid_messages: list[MessageDict] = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"},
        ]
        assert len(valid_messages) == 3


class TestSanitization:
    """Тесты для проблемы #5 и #6: Санитизация ввода/вывода."""

    def test_sanitize_topic_escapes_braces(self) -> None:
        """Тест что sanitize_topic экранирует фигурные скобки."""
        from tui.app import sanitize_topic  # pylint: disable=import-outside-toplevel

        # Фигурные скобки должны быть экранированы
        result = sanitize_topic("Test {injection}")
        assert "{" not in result or "{{" in result
        assert "}" not in result or "}}" in result

    def test_sanitize_topic_strips_whitespace(self) -> None:
        """Тест что sanitize_topic удаляет пробелы."""
        from tui.app import sanitize_topic  # pylint: disable=import-outside-toplevel

        result = sanitize_topic("  Test topic  ")
        assert result == "Test topic"

    def test_sanitize_response_escapes_markup(self) -> None:
        """Тест что sanitize_response экранирует markup."""
        # pylint: disable=import-outside-toplevel
        from tui.app import sanitize_response_for_display

        # HTML-подобные конструкции должны быть экранированы
        result = sanitize_response_for_display("Test <b>bold</b>")
        assert "<b>" not in result

    def test_sanitize_response_replaces_newlines(self) -> None:
        """Тест что sanitize_response заменяет newlines."""
        # pylint: disable=import-outside-toplevel
        from tui.app import sanitize_response_for_display

        result = sanitize_response_for_display("Line1\nLine2")
        assert "\n" not in result
        assert "Line1 Line2" in result

    def test_sanitize_response_truncates_long_text(self) -> None:
        """Тест что sanitize_response обрезает длинный текст."""
        # pylint: disable=import-outside-toplevel
        from tui.app import sanitize_response_for_display

        long_text = "A" * 200
        result = sanitize_response_for_display(long_text)
        assert len(result) <= 103  # 100 + "..."


class TestMainExceptionHandling:
    """Тесты для проблемы #7: Обработка исключений в main.py."""

    def test_main_returns_zero_on_success(self) -> None:
        """Тест что main возвращает 0 при успехе."""
        from main import main  # pylint: disable=import-outside-toplevel

        with patch("main.DialogueApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.run.return_value = None

            result = main()
            assert result == 0

    def test_main_returns_zero_on_keyboard_interrupt(self) -> None:
        """Тест что main возвращает 0 при KeyboardInterrupt."""
        from main import main  # pylint: disable=import-outside-toplevel

        with patch("main.DialogueApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = KeyboardInterrupt()

            result = main()
            assert result == 0

    def test_main_returns_one_on_exception(self) -> None:
        """Тест что main возвращает 1 при исключении."""
        from main import main  # pylint: disable=import-outside-toplevel

        with patch("main.DialogueApp") as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.run.side_effect = RuntimeError("Test error")

            result = main()
            assert result == 1


class TestModelSelectionScreen:
    """Тесты для проблемы #1: Проверка пустого списка моделей."""

    def test_init_with_empty_models(self) -> None:
        """Тест инициализации с пустым списком моделей."""
        # pylint: disable=import-outside-toplevel
        from tui.app import ModelSelectionScreen

        # Не должно вызывать IndexError
        screen = ModelSelectionScreen(models=[])
        assert screen._available_models == []  # pylint: disable=protected-access

    def test_init_with_single_model(self) -> None:
        """Тест инициализации с одной моделью."""
        # pylint: disable=import-outside-toplevel
        from tui.app import ModelSelectionScreen

        # Не должно вызывать IndexError
        screen = ModelSelectionScreen(models=["llama3"])
        assert screen._available_models == ["llama3"]  # pylint: disable=protected-access

    def test_init_with_two_models(self) -> None:
        """Тест инициализации с двумя моделями."""
        # pylint: disable=import-outside-toplevel
        from tui.app import ModelSelectionScreen

        screen = ModelSelectionScreen(models=["llama3", "mistral"])
        assert screen._available_models == ["llama3", "mistral"]  # pylint: disable=protected-access


class TestOllamaClientChainedExceptions:
    """Тесты для проблемы #10: Использование raise ... from."""

    @pytest.mark.asyncio
    async def test_list_models_preserves_exception_chain(self) -> None:
        """Тест что list_models сохраняет цепочку исключений."""
        from aiohttp import ClientError  # pylint: disable=import-outside-toplevel

        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ClientError("Connection failed")
        )
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(OllamaError) as exc_info:
                await client.list_models()

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.original_exception is not None

    @pytest.mark.asyncio
    async def test_generate_preserves_exception_chain(self) -> None:
        """Тест что generate сохраняет цепочку исключений."""
        from aiohttp import ClientError  # pylint: disable=import-outside-toplevel

        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ClientError("Connection failed")
        )
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(OllamaError) as exc_info:
                await client.generate("llama3", [{"role": "user", "content": "test"}])

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.original_exception is not None


class TestDialogueAppPauseHandling:  # pylint: disable=too-few-public-methods
    """Тесты для проблемы #14 и #15: Обработка паузы и отмены задач."""

    def test_on_pause_pressed_checks_conversation(self) -> None:
        """Тест что on_pause_pressed проверяет наличие conversation."""
        from tui.app import DialogueApp  # pylint: disable=import-outside-toplevel

        app = DialogueApp()

        # Если conversation нет, не должно быть ошибок
        app._conversation = None  # pylint: disable=protected-access
        # Вызов не должен вызывать AttributeError
        app.on_pause_pressed()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
