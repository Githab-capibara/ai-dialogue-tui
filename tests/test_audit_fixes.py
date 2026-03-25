"""Тесты для проверки исправлений после аудита кода."""

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import Config, validate_ollama_url
from models.conversation import Conversation
from models.ollama_client import _DEFAULT_OPTIONS, OllamaClient
from services.dialogue_service import DialogueService


class TestAuditFixes:
    """Тесты для проверки исправлений после аудита."""

    def test_conversation_initialization_flag_prevents_duplicate_system_message(self):
        """Тест, что флаг _initialized предотвращает дублирование системного сообщения."""
        config = Config(default_system_prompt="Test {topic}")
        conversation = Conversation(
            "model_a",
            "model_b",
            "test_topic",
            _config=config,
        )

        context_a = conversation.get_context("A")
        context_b = conversation.get_context("B")

        system_messages_a = [m for m in context_a if m["role"] == "system"]
        system_messages_b = [m for m in context_b if m["role"] == "system"]

        assert len(system_messages_a) == 1, (
            "Should have exactly one system message in context A"
        )
        assert len(system_messages_b) == 1, (
            "Should have exactly one system message in context B"
        )

    def test_conversation_init_flag_exists_and_is_boolean(self):
        """Тест, что поле _initialized существует и имеет правильный тип."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        assert hasattr(conversation, "_initialized")
        assert isinstance(conversation._initialized, bool)  # noqa: W0212
        assert conversation._initialized is True  # noqa: W0212

    def test_ollama_client_num_predict_comment_exists(self):
        """Тест, что в ollama_client есть комментарий о num_predict = max_tokens."""
        source = inspect.getsource(OllamaClient.generate)
        assert "num_predict" in source or "max_tokens" in source

    @pytest.mark.asyncio
    async def test_ollama_client_generate_uses_max_tokens_as_num_predict(self):
        """Тест, что max_tokens корректно маппится в num_predict для Ollama."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"message": {"content": "test response"}}
        )

        mock_post_context_manager = AsyncMock()
        mock_post_context_manager.__aenter__.return_value = mock_response
        mock_post_context_manager.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> AsyncMock:
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            await client.generate(
                "test_model",
                [{"role": "user", "content": "test"}],
                max_tokens=500,
            )

        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["num_predict"] == 500

    def test_validate_ollama_url_checks_type_explicitly(self):
        """Тест, что validate_ollama_url проверяет тип явно."""
        assert validate_ollama_url("http://localhost:11434") is True
        assert validate_ollama_url(None) is False
        assert validate_ollama_url("") is False
        assert validate_ollama_url(123) is False
        assert validate_ollama_url([]) is False

    def test_config_validate_ollama_url_with_invalid_scheme(self):
        """Тест, что неправильные схемы отклоняются."""
        assert validate_ollama_url("ftp://localhost:11434") is False
        assert validate_ollama_url("ws://localhost:11434") is False
        assert validate_ollama_url("tcp://localhost:11434") is False

    def test_config_validate_ollama_url_with_missing_netloc(self):
        """Тест, что URL без хоста отклоняются."""
        assert validate_ollama_url("http://") is False

    def test_conversation_fallback_prompt_with_bad_format(self):
        """Тест, что fallback промпт работает при некорректном формате."""
        config = Config(default_system_prompt="Hello {nonexistent_field}!")
        conversation = Conversation(
            "model_a",
            "model_b",
            "my_topic",
            _config=config,
        )

        assert conversation._system_prompt is not None  # noqa: W0212
        assert "my_topic" in conversation._system_prompt  # noqa: W0212

    def test_conversation_fallback_prompt_with_empty_topic(self):
        """Тест, что fallback промпт работает с пустой темой."""
        config = Config(default_system_prompt="Hello {topic}!")
        conversation = Conversation(
            "model_a",
            "model_b",
            "",
            _config=config,
        )

        assert conversation._system_prompt is not None  # noqa: W0212

    def test_default_options_temperature_value(self):
        """Тест, что дефолтные опции содержат правильные значения."""
        assert "temperature" in _DEFAULT_OPTIONS
        assert "num_predict" in _DEFAULT_OPTIONS
        assert _DEFAULT_OPTIONS["temperature"] == 0.7
        assert _DEFAULT_OPTIONS["num_predict"] == 200


class TestLoggingConfiguration:
    """Тесты для проверки конфигурации логирования."""

    def test_main_module_has_logging_import(self):
        """Тест, что main.py импортирует logging."""
        import main  # noqa: W0212

        assert hasattr(main, "logging") or "logging" in dir(main)

    def test_dialogue_service_pause_check_is_running(self):
        """Тест, что pause() проверяет is_running."""
        mock_controller = MagicMock()
        mock_controller.is_running = False
        mock_controller.is_paused = False

        conversation = Conversation("model_a", "model_b", "test_topic")
        mock_provider = MagicMock()

        service = DialogueService(conversation, mock_provider)
        service._is_running = False  # noqa: W0212
        service.pause()

        assert service.is_paused is False

    def test_dialogue_service_pause_when_running(self):
        """Тест, что pause() работает когда is_running=True."""
        mock_controller = MagicMock()
        mock_controller.is_running = True
        mock_controller.is_paused = False

        conversation = Conversation("model_a", "model_b", "test_topic")
        mock_provider = MagicMock()

        service = DialogueService(conversation, mock_provider)
        service._is_running = True  # noqa: W0212
        service.pause()

        assert service.is_paused is True
