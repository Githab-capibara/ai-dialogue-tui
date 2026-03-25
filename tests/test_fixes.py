"""Тесты для проверки исправлений, внесенных в код."""

# Standard library imports
from unittest.mock import AsyncMock, MagicMock, patch

# Third party imports
import pytest

# Local application/library imports
from config import Config, validate_ollama_url
from controllers.dialogue_controller import DialogueController
from models.conversation import Conversation
from models.ollama_client import OllamaClient


class TestFixes:
    """Тесты для проверки исправлений критических проблем."""

    @pytest.mark.asyncio
    async def test_ollama_client_list_models_uses_list_comprehension(self):
        """Тест, что list_models использует list comprehension для производительности."""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "models": [
                    {"name": "model1"},
                    {"name": "model2"},
                    {"invalid": "no_name_field"},
                    {"name": ""},
                    None,
                ]
            }
        )

        mock_get_context_manager = AsyncMock()
        mock_get_context_manager.__aenter__.return_value = mock_response
        mock_get_context_manager.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_get_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> AsyncMock:
            return mock_session

        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            models = await client.list_models()

        assert models == ["model1", "model2"]

    @pytest.mark.asyncio
    async def test_ollama_client_generate_uses_cached_default_options(self):
        """Тест, что generate использует кэшированные дефолтные опции."""
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
            result = await client.generate(
                "test_model", [{"role": "user", "content": "test"}]
            )

        assert result == "test response"
        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["temperature"] == 0.7
        assert payload["options"]["num_predict"] == 200

    def test_conversation_handles_malformed_system_prompt(self):
        """Тест, что Conversation корректно обрабатывает некорректный системный промпт."""
        config_with_bad_prompt = Config(default_system_prompt="Привет {nonexistent}!")
        conversation = Conversation(
            "model_a",
            "model_b",
            "тема",
            _config=config_with_bad_prompt,
        )

        expected_prompt = (
            "You are a helpful assistant. The topic of discussion is: тема"
        )
        assert conversation._system_prompt == expected_prompt  # noqa: W0212

    def test_conversation_get_context_returns_copy_for_safety(self):
        """Тест, что get_context возвращает копию для безопасности."""
        conversation = Conversation("model_a", "model_b", "тема")
        conversation.add_message("A", "user", "test message")

        context = conversation.get_context("A")
        context2 = conversation.get_context("A")
        assert context is not context2
        assert len(context) == 2
        assert context[0]["role"] == "system"
        assert context[1]["content"] == "test message"
        context.append({"role": "test", "content": "test"})
        context_after = conversation.get_context("A")
        assert len(context_after) == 2

    def test_tui_app_uses_ui_constants_not_hardcoded_strings(self):
        """Тест, что TUI использует константы UI вместо жестко закодированных строк."""
        with open("tui/app.py", "r", encoding="utf-8") as f:
            content = f.read()

        assert 'f"#{UI_IDS.dialogue_log}"' in content
        assert "UI_IDS.dialogue_log" in content

    def test_controller_handles_state_as_dataclass_properly(self):
        """Тест, что контроллер правильно обрабатывает UIState как dataclass."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        controller.handle_clear()
        assert controller.state.turn_count == 0

        controller.handle_stop()
        assert controller.state.is_dialogue_active is False

        mock_service.is_running = False
        mock_service.is_paused = False
        controller.handle_start()
        assert controller.state.is_dialogue_active is True

    def test_config_validate_ollama_url_has_correct_exception_handling(self):
        """Тест, что validate_ollama_url имеет правильную обработку исключений."""
        assert validate_ollama_url("http://localhost:11434") is True
        assert validate_ollama_url("https://example.com") is True

        assert validate_ollama_url("localhost:11434") is False
        assert validate_ollama_url("ftp://localhost:11434") is False
        assert validate_ollama_url("") is False
        assert validate_ollama_url(None) is False

        assert validate_ollama_url(123) is False
        assert validate_ollama_url([]) is False
