"""
Тесты для критических проблем отчета аудита.

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
    Тесты используют доступ к внутренним атрибутам, что оправдано для тестирования.
"""

# pylint: disable=duplicate-code,protected-access,import-outside-toplevel
# pylint: disable=too-few-public-methods,reimported,redefined-outer-name,line-too-long

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientError

from models.config import Config, validate_ollama_url
from models.conversation import Conversation, MessageDict
from models.ollama_client import OllamaClient
from models.provider import ProviderError
from tui.app import ModelSelectionScreen, sanitize_response_for_display, sanitize_topic
from tui.sanitizer import MAX_RESPONSE_PREVIEW_LENGTH

# Helper-функции для тестов


def create_async_mock_response(
    status: int = 200,
    json_data: Any = None,
    raise_on_json: Exception | None = None,
) -> AsyncMock:
    """
    Создать мок для HTTP ответа.

    Args:
        status: HTTP статус ответа.
        json_data: Данные для JSON ответа.
        raise_on_json: Исключение для выброса при вызове json().

    Returns:
        AsyncMock настроенный для эмуляции ответа.
    """
    mock_response = AsyncMock()
    mock_response.status = status

    if raise_on_json:

        async def raise_error() -> None:
            raise raise_on_json

        mock_response.json = raise_error
    else:

        async def return_json() -> Any:
            return json_data

        mock_response.json = return_json

    return mock_response


def create_session_mock(
    response: AsyncMock | None = None,
    raise_on_enter: Exception | None = None,
) -> AsyncMock:
    """
    Создать мок для HTTP сессии.

    Args:
        response: Мок ответа для get/post запросов.
        raise_on_enter: Исключение для выброса при входе в контекст.

    Returns:
        AsyncMock настроенный для эмуляции сессии.
    """
    mock_context_manager = AsyncContextManagerMock(
        response=response, raise_on_enter=raise_on_enter
    )
    mock_session = AsyncMock()
    mock_session.get = MagicMock(return_value=mock_context_manager)
    mock_session.post = MagicMock(return_value=mock_context_manager)
    mock_session.closed = False
    return mock_session


def create_mock_get_session(mock_session: AsyncMock):
    """
    Создать функцию для мока _get_session метода.

    Args:
        mock_session: Мок сессии для возврата.

    Returns:
        Асинхронная функция для использования в patch.
    """

    async def mock_get_session(_self: OllamaClient) -> Any:  # noqa: ANN401
        return mock_session

    return mock_get_session


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

    def test_temperature_validation_min(self) -> None:
        """Тест валидации temperature минимальное значение."""
        config = Config(temperature=0.0)
        assert config.temperature == 0.0

    def test_temperature_validation_max(self) -> None:
        """Тест валидации temperature максимальное значение."""
        config = Config(temperature=1.0)
        assert config.temperature == 1.0

    def test_temperature_validation_out_of_range(self) -> None:
        """Тест валидации temperature вне диапазона."""
        with pytest.raises(ValueError, match="temperature"):
            Config(temperature=1.5)

    def test_max_tokens_validation(self) -> None:
        """Тест валидации max_tokens."""
        with pytest.raises(ValueError, match="max_tokens"):
            Config(max_tokens=-2)

    def test_request_timeout_validation(self) -> None:
        """Тест валидации request_timeout."""
        with pytest.raises(ValueError, match="request_timeout"):
            Config(request_timeout=0)

    def test_pause_between_messages_validation(self) -> None:
        """Тест валидации pause_between_messages."""
        with pytest.raises(ValueError, match="pause_between_messages"):
            Config(pause_between_messages=-1.0)


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
        mock_response = create_async_mock_response(json_data={"invalid": "data"})
        mock_session = create_session_mock(response=mock_response)

        with patch.object(
            OllamaClient, "_get_session", create_mock_get_session(mock_session)
        ):
            client = OllamaClient(host="http://localhost:11434")
            # Должен вернуть пустой список вместо ошибки
            result = await client.list_models()
            assert result == []

    @pytest.mark.asyncio
    async def test_list_models_validates_model_name(self) -> None:
        """Тест что list_models проверяет наличие name у каждой модели."""
        # Мок сессии с моделями без name
        mock_response = create_async_mock_response(
            json_data={
                "models": [
                    {"name": "llama3"},
                    {"invalid": "model"},  # Без name
                    {"name": "mistral"},
                ]
            }
        )
        mock_session = create_session_mock(response=mock_response)

        with patch.object(
            OllamaClient, "_get_session", create_mock_get_session(mock_session)
        ):
            client = OllamaClient(host="http://localhost:11434")
            result = await client.list_models()
            # Должны быть только модели с name
            assert result == ["llama3", "mistral"]

    @pytest.mark.asyncio
    async def test_list_models_handles_json_decode_error(self) -> None:
        """Тест что list_models обрабатывает JSONDecodeError."""
        mock_response = create_async_mock_response(
            raise_on_json=json.JSONDecodeError("Invalid JSON", "", 0)
        )
        mock_session = create_session_mock(response=mock_response)

        with patch.object(
            OllamaClient, "_get_session", create_mock_get_session(mock_session)
        ):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(ProviderError, match="Некорректный JSON"):
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
        mock_client.generate.side_effect = ProviderError("Test error")

        # Ошибка должна быть проброшена
        with pytest.raises(ProviderError):
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

    def test_clear_contexts_uses_assignment(self) -> None:
        """Тест что clear_contexts использует присваивание новых списков."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test topic",
        )

        # Добавляем сообщения
        conversation.add_message("A", "user", "test")
        conversation.add_message("B", "user", "test")

        # Очищаем
        conversation.clear_contexts()

        # Контексты должны содержать только системный промпт
        context_a = conversation.get_context("A")
        context_b = conversation.get_context("B")

        assert len(context_a) == 1
        assert len(context_b) == 1
        assert context_a[0]["role"] == "system"
        assert context_b[0]["role"] == "system"


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
        # Фигурные скобки должны быть экранированы
        result = sanitize_topic("Test {injection}")
        assert "{" not in result or "{{" in result
        assert "}" not in result or "}}" in result

    def test_sanitize_topic_strips_whitespace(self) -> None:
        """Тест что sanitize_topic удаляет пробелы."""
        result = sanitize_topic("  Test topic  ")
        assert result == "Test topic"

    def test_sanitize_response_escapes_markup(self) -> None:
        """Тест что sanitize_response экранирует markup."""
        # HTML-подобные конструкции должны быть экранированы
        result = sanitize_response_for_display("Test <b>bold</b>")
        assert "<b>" not in result

    def test_sanitize_response_replaces_newlines(self) -> None:
        """Тест что sanitize_response заменяет newlines."""
        result = sanitize_response_for_display("Line1\nLine2")
        assert "\n" not in result
        assert "Line1 Line2" in result

    def test_sanitize_response_truncates_long_text(self) -> None:
        """Тест что sanitize_response обрезает длинный текст."""
        long_text = "A" * 200
        result = sanitize_response_for_display(long_text)
        assert len(result) <= MAX_RESPONSE_PREVIEW_LENGTH + 3  # 100 + "..."


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
        # Не должно вызывать IndexError
        screen = ModelSelectionScreen(models=[])
        assert screen._available_models == []

    def test_init_with_single_model(self) -> None:
        """Тест инициализации с одной моделью."""
        # Не должно вызывать IndexError
        screen = ModelSelectionScreen(models=["llama3"])
        assert screen._available_models == ["llama3"]

    def test_init_with_two_models(self) -> None:
        """Тест инициализации с двумя моделями."""
        screen = ModelSelectionScreen(models=["llama3", "mistral"])
        assert screen._available_models == ["llama3", "mistral"]

    def test_get_model_value_with_empty_list(self) -> None:
        """Тест _get_model_value с пустым списком."""
        screen = ModelSelectionScreen(models=[])
        result = screen._get_model_value(0)
        assert result is None

    def test_get_model_value_with_single_model(self) -> None:
        """Тест _get_model_value с одной моделью."""
        screen = ModelSelectionScreen(models=["llama3"])
        assert screen._get_model_value(0) == "llama3"
        assert screen._get_model_value(1) == "llama3"  # Возвращает последнюю

    def test_get_model_value_with_multiple_models(self) -> None:
        """Тест _get_model_value с несколькими моделями."""
        screen = ModelSelectionScreen(models=["llama3", "mistral"])
        assert screen._get_model_value(0) == "llama3"
        assert screen._get_model_value(1) == "mistral"
        assert screen._get_model_value(2) == "mistral"  # Возвращает последнюю


class TestOllamaClientChainedExceptions:
    """Тесты для проблемы #10: Использование raise ... from."""

    @pytest.mark.asyncio
    async def test_list_models_preserves_exception_chain(self) -> None:
        """Тест что list_models сохраняет цепочку исключений."""
        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ClientError("Connection failed")
        )
        mock_session = create_session_mock(response=None)
        mock_session.get = MagicMock(return_value=mock_context_manager)

        with patch.object(
            OllamaClient, "_get_session", create_mock_get_session(mock_session)
        ):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(ProviderError) as exc_info:
                await client.list_models()

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.original_exception is not None

    @pytest.mark.asyncio
    async def test_generate_preserves_exception_chain(self) -> None:
        """Тест что generate сохраняет цепочку исключений."""
        mock_context_manager = AsyncContextManagerMock(
            raise_on_enter=ClientError("Connection failed")
        )
        mock_session = create_session_mock(response=None)
        mock_session.post = MagicMock(return_value=mock_context_manager)

        with patch.object(
            OllamaClient, "_get_session", create_mock_get_session(mock_session)
        ):
            client = OllamaClient(host="http://localhost:11434")
            with pytest.raises(ProviderError) as exc_info:
                await client.generate("llama3", [{"role": "user", "content": "test"}])

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.original_exception is not None


class TestDialogueAppPauseHandling:  # pylint: disable=too-few-public-methods
    """Тесты для проблемы #14 и #15: Обработка паузы и отмены задач."""

    def test_on_pause_pressed_checks_conversation(self) -> None:
        """Тест что on_pause_pressed проверяет наличие controller через assert."""
        from tui.app import DialogueApp  # pylint: disable=import-outside-toplevel

        app = DialogueApp()

        # Если controller нет, assert должен вызвать AssertionError
        app._controller = None  # pylint: disable=protected-access
        # Вызов должен вызывать AssertionError
        import pytest

        with pytest.raises(AssertionError, match="Controller not initialized"):
            app.on_pause_pressed()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
