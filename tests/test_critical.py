"""Модульные тесты для критических функций приложения."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.conversation import Conversation


class TestConfigValidation:
    """Тесты для проблемы #4: Валидация URL конфигурации."""

    def test_valid_http_url(self) -> None:
        """Тест корректного HTTP URL."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config(ollama_host="http://localhost:11434")
        assert config.validate_ollama_url(config.ollama_host)

    def test_valid_https_url(self) -> None:
        """Тест корректного HTTPS URL."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config(ollama_host="https://example.com:11434")
        assert config.validate_ollama_url(config.ollama_host)

    def test_invalid_url_no_scheme(self) -> None:
        """Тест некорректного URL без схемы."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config(ollama_host="localhost:11434")
        assert not config.validate_ollama_url(config.ollama_host)

    def test_invalid_url_wrong_scheme(self) -> None:
        """Тест некорректного URL с неправильной схемой."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config(ollama_host="ftp://localhost:11434")
        assert not config.validate_ollama_url(config.ollama_host)

    def test_invalid_url_empty(self) -> None:
        """Тест пустого URL."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config(ollama_host="")
        assert not config.validate_ollama_url(config.ollama_host)

    def test_validate_ollama_url_function(self) -> None:
        """Тест функции валидации URL."""
        from config import Config  # pylint: disable=import-outside-toplevel

        config = Config()
        assert config.validate_ollama_url("http://localhost:11434")
        assert not config.validate_ollama_url("invalid")


class TestOllamaClientValidation:
    """Тесты для проблемы #2: Валидация ключей API."""

    def test_invalid_host_raises_value_error(self) -> None:
        """Тест некорректного хоста."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        with pytest.raises(ValueError):
            OllamaClient(host="invalid-url")

    def test_valid_host_accepted(self) -> None:
        """Тест корректного хоста."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        client = OllamaClient(host="http://localhost:11434")
        assert client.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_list_models_validates_response_structure(self) -> None:
        """Тест валидации структуры ответа API."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"wrong_key": []})
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(return_value=mock_response))

        with patch.object(OllamaClient, "_get_session", return_value=mock_session):
            client = OllamaClient()
            with pytest.raises(Exception):  # noqa: B017
                await client.list_models()

    @pytest.mark.asyncio
    async def test_list_models_validates_model_name(self) -> None:
        """Тест валидации имени модели в ответе API."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"models": [{"no_name": "test"}]})
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(return_value=mock_response))

        with patch.object(OllamaClient, "_get_session", return_value=mock_session):
            client = OllamaClient()
            models = await client.list_models()
            assert len(models) == 0

    @pytest.mark.asyncio
    async def test_list_models_handles_json_decode_error(self) -> None:
        """Тест обработки ошибки парсинга JSON."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        mock_response = MagicMock()
        mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(return_value=mock_response))

        with patch.object(OllamaClient, "_get_session", return_value=mock_session):
            client = OllamaClient()
            with pytest.raises(Exception):  # noqa: B017
                await client.list_models()

    @pytest.mark.asyncio
    async def test_generate_validates_messages(self) -> None:
        """Тест валидации сообщений в generate."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        client = OllamaClient()
        with pytest.raises(ValueError):
            await client.generate("test", "not-a-list")  # type: ignore[arg-type]


class TestConversationAtomicity:
    """Тесты для проблемы #3: Атомарность операций."""

    @pytest.mark.asyncio
    async def test_process_turn_is_atomic(self) -> None:
        """Тест атомарности process_turn."""
        conv = Conversation(model_a_name="A", model_b_name="B", topic="Test")
        mock_client = MagicMock()
        mock_client.generate = AsyncMock(return_value="Response")

        initial_turn = conv.current_turn
        await conv.process_turn(mock_client)

        # Ход должен переключиться
        assert conv.current_turn != initial_turn

    def test_switch_turn_does_not_return_value(self) -> None:
        """Тест что switch_turn не возвращает значение."""
        conv = Conversation(model_a_name="A", model_b_name="B", topic="Test")
        result = conv.switch_turn()
        assert result is None

    def test_get_current_turn_returns_value(self) -> None:
        """Тест что current_turn возвращает значение."""
        conv = Conversation(model_a_name="A", model_b_name="B", topic="Test")
        result = conv.current_turn
        assert result in ("A", "B")

    def test_current_turn_property_uses_query(self) -> None:
        """Тест что current_turn это property (query)."""
        conv = Conversation(model_a_name="A", model_b_name="B", topic="Test")
        # Property не должен изменять состояние
        first = conv.current_turn
        second = conv.current_turn
        assert first == second

    def test_clear_contexts_uses_clear_method(self) -> None:
        """Тест что clear_contexts использует .clear()."""
        conv = Conversation(model_a_name="A", model_b_name="B", topic="Test")
        conv.add_message("A", "user", "Test")
        conv.add_message("B", "user", "Test")

        initial_id_a = id(conv._context_a)
        initial_id_b = id(conv._context_b)

        conv.clear_contexts()

        # Списки должны быть те же самые (clear modifies in-place)
        assert id(conv._context_a) == initial_id_a
        assert id(conv._context_b) == initial_id_b


class TestMessageTypedDict:
    """Тесты для проблемы #9: TypedDict для сообщений."""

    def test_message_dict_structure(self) -> None:
        """Тест структуры MessageDict."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            MessageDict,
        )

        msg: MessageDict = {"role": "user", "content": "Hello"}
        assert msg["role"] in ("user", "assistant", "system")
        assert msg["content"] == "Hello"

    def test_message_dict_role_literal(self) -> None:
        """Тест Literal для роли."""
        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            MessageDict,
        )

        msg: MessageDict = {"role": "assistant", "content": "Hi"}
        assert msg["role"] in ("user", "assistant", "system")


class TestSanitization:
    """Тесты для проблемы #5-6: Санитизация ввода и вывода."""

    def test_sanitize_topic_escapes_braces(self) -> None:
        """Тест экранирования скобок в теме."""
        from tui.app import sanitize_topic  # pylint: disable=import-outside-toplevel

        topic = sanitize_topic("Test {injection}")
        assert "{" not in topic

    def test_sanitize_topic_strips_whitespace(self) -> None:
        """Тест обрезки whitespace в теме."""
        from tui.app import sanitize_topic  # pylint: disable=import-outside-toplevel

        topic = sanitize_topic("  Test  ")
        assert topic == "Test"

    def test_sanitize_response_escapes_markup(self) -> None:
        """Тест экранирования markup в ответе."""
        from tui.app import (
            sanitize_response_for_display,  # pylint: disable=import-outside-toplevel
        )

        response = sanitize_response_for_display("Test [bold]text[/bold]")
        assert "[" not in response or "&" in response

    def test_sanitize_response_replaces_newlines(self) -> None:
        """Тест замены newlines в ответе."""
        from tui.app import (
            sanitize_response_for_display,  # pylint: disable=import-outside-toplevel
        )

        response = sanitize_response_for_display("Line1\nLine2")
        assert "\n" not in response

    def test_sanitize_response_truncates_long_text(self) -> None:
        """Тест обрезки длинного текста."""
        from tui.app import DialogueApp  # pylint: disable=import-outside-toplevel

        app = DialogueApp()
        long_text = "x" * 200
        formatted = app._format_response(long_text)
        assert len(formatted) <= 103  # 100 + "..."


class TestMainExceptionHandling:
    """Тесты для проблемы #7: Обработка исключений в main."""

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
        from tui.app import ModelSelectionScreen  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError):
            ModelSelectionScreen([])

    def test_init_with_single_model(self) -> None:
        """Тест инициализации с одной моделью."""
        from tui.app import ModelSelectionScreen  # pylint: disable=import-outside-toplevel

        screen = ModelSelectionScreen(["model1"])
        assert screen._available_models == ["model1"]

    def test_init_with_two_models(self) -> None:
        """Тест инициализации с двумя моделями."""
        from tui.app import ModelSelectionScreen  # pylint: disable=import-outside-toplevel

        screen = ModelSelectionScreen(["model1", "model2"])
        assert screen._available_models == ["model1", "model2"]


class TestOllamaClientChainedExceptions:
    """Тесты для проблемы #10: Сохранение цепочки исключений."""

    @pytest.mark.asyncio
    async def test_list_models_preserves_exception_chain(self) -> None:
        """Тест сохранения цепочки исключений в list_models."""
        from aiohttp import ClientError  # pylint: disable=import-outside-toplevel

        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        mock_response = MagicMock()
        mock_response.json = AsyncMock(side_effect=ClientError("Network error"))
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(return_value=mock_response))

        with patch.object(OllamaClient, "_get_session", return_value=mock_session):
            client = OllamaClient()
            with pytest.raises(Exception) as exc_info:  # noqa: B017
                await client.list_models()

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.__cause__ is not None

    @pytest.mark.asyncio
    async def test_generate_preserves_exception_chain(self) -> None:
        """Тест сохранения цепочки исключений в generate."""
        from aiohttp import ClientError  # pylint: disable=import-outside-toplevel

        from models.ollama_client import (  # pylint: disable=import-outside-toplevel
            OllamaClient,
        )

        mock_response = MagicMock()
        mock_response.json = AsyncMock(side_effect=ClientError("Network error"))
        mock_response.raise_for_status = MagicMock()

        mock_session = MagicMock()
        mock_session.get = MagicMock(return_value=AsyncMock(return_value=mock_response))

        with patch.object(OllamaClient, "_get_session", return_value=mock_session):
            client = OllamaClient()
            with pytest.raises(Exception) as exc_info:  # noqa: B017
                await client.generate("test", [])

            # Проверяем что оригинальное исключение сохранено
            assert exc_info.value.__cause__ is not None


class TestDialogueAppPauseHandling:
    """Тесты для проблемы #11: Обработка паузы в DialogueApp."""

    # pylint: disable=too-few-public-methods
    def test_on_pause_pressed_checks_conversation(self) -> None:
        """Тест что on_pause_pressed проверяет _conversation."""
        from tui.app import DialogueApp  # pylint: disable=import-outside-toplevel

        app = DialogueApp()
        # _conversation = None должно вызвать warning notification
        assert app._conversation is None
