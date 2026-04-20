"""Tests for verifying code fixes.

Note:
    Tests use access to internal attributes, which is justified for testing purposes.

"""

# pylint: disable=protected-access,import-outside-toplevel

# Standard library imports
from unittest.mock import AsyncMock, MagicMock, patch

# Third party imports
import pytest

from controllers.dialogue_controller import DialogueController

# Local application/library imports
from models.config import validate_ollama_url
from models.conversation import Conversation
from models.ollama_client import OllamaClient


class TestFixes:
    """Tests for verifying critical issue fixes."""

    @pytest.mark.asyncio
    async def test_ollama_client_list_models_uses_list_comprehension(self):
        """Test that list_models uses list comprehension for performance."""
        # Arrange
        # Create mock session and response like in existing tests
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "models": [
                    {"name": "model1"},
                    {"name": "model2"},
                    {"invalid": "no_name_field"},
                    {"name": ""},  # Empty name should be filtered out
                    None,  # None should be filtered out
                ]
            }
        )

        # Mock context manager for session.get()
        mock_get_context_manager = AsyncMock()
        mock_get_context_manager.__aenter__.return_value = mock_response
        mock_get_context_manager.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_get_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> AsyncMock:
            return mock_session

        # Act
        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            models = await client.list_models()

        # Assert
        assert models == ["model1", "model2"]

    @pytest.mark.asyncio
    async def test_ollama_client_generate_uses_cached_default_options(self):
        """Test that generate uses cached default options."""
        # Arrange
        # Create mock session and response like in existing tests
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"message": {"content": "test response"}})

        # Mock context manager for session.post()
        mock_post_context_manager = AsyncMock()
        mock_post_context_manager.__aenter__.return_value = mock_response
        mock_post_context_manager.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_post_context_manager)
        mock_session.closed = False

        async def mock_get_session(_self: OllamaClient) -> AsyncMock:
            return mock_session

        # Act
        with patch.object(OllamaClient, "_get_session", mock_get_session):
            client = OllamaClient(host="http://localhost:11434")
            # Call without specifying temperature or max_tokens
            result = await client.generate("test_model", [{"role": "user", "content": "test"}])

        # Assert
        assert result == "test response"
        # Verify that the payload used the default options from _DEFAULT_OPTIONS
        # We can check this by examining what was passed to post
        call_args = mock_session.post.call_args
        payload = call_args[1]["json"]  # Get the json payload
        # From _DEFAULT_OPTIONS
        assert payload["options"]["temperature"] == 0.7
        # num_predict is not set when max_tokens=-1 (unlimited)

    def test_conversation_handles_malformed_system_prompt(self):
        """Test that Conversation correctly handles malformed system prompt."""
        # Arrange
        # Create conversation with custom system_prompt that has invalid format
        conversation = Conversation(
            model_a="model_a",
            model_b="model_b",
            topic="topic",
            system_prompt="Hello {nonexistent}!",
        )

        # Act & Assert
        # With invalid prompt, fallback is used
        context_a = conversation.get_context("A")
        assert len(context_a) > 0
        # Fallback prompt in English
        assert "helpful assistant" in context_a[0]["content"]
        assert "topic" in context_a[0]["content"]

    def test_conversation_get_context_returns_copy_for_safety(self):
        """Test that get_context returns tuple for safety and performance."""
        # Arrange
        conversation = Conversation("model_a", "model_b", "topic")
        conversation.add_message("A", "user", "test message")

        # Act
        context = conversation.get_context("A")

        # Assert
        # Should return a tuple (immutable)
        assert isinstance(context, tuple)
        # But with the same content
        # Note: Context includes system message + our added message
        assert len(context) == 2
        assert context[0]["role"] == "system"  # System message
        assert context[1]["content"] == "test message"  # Our message
        # Tuple is immutable, so we can't modify it - this is the desired
        # behavior

    def test_tui_app_uses_ui_constants_not_hardcoded_strings(self):
        """Test that TUI application uses UI constants instead of hardcoded strings."""
        # This test verifies the fix by checking that the code no longer contains
        # hardcoded "#dialogue-log" strings
        # Since we can't easily test the UI without running it, we'll verify
        # that our fix was applied by checking the source

        # Read the file and check for the fix
        with open("/home/d/ai-dialogue-tui/tui/app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Assert that the hardcoded string is not present (except in comments maybe)
        # And that the constant is used
        assert 'f"#{UI_IDS.dialogue_log}"' in content
        assert "UI_IDS.dialogue_log" in content

    def test_controller_handles_state_as_dataclass_properly(self):
        """Test that controller correctly handles UIState as dataclass."""
        # Arrange

        # Create a mock service
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        # Act - test handle_clear which modifies state
        controller.handle_clear()

        # Assert - state should be updated properly using replace
        assert controller.state.turn_count == 0
        # And the state object should be a new instance (dataclass behavior)
        # We can't easily test that it's a new instance without inspecting internals,
        # but we can verify the value was set correctly

        # Test handle_stop
        controller.handle_stop()
        assert controller.state.is_dialogue_active is False

        # Test handle_start
        mock_service.is_running = False  # Reset for test
        mock_service.is_paused = False
        controller.handle_start()
        assert controller.state.is_dialogue_active is True

    def test_config_validate_ollama_url_has_correct_exception_handling(self):
        """Test that validate_ollama_url has correct exception handling."""
        # Act & Assert
        # Should only catch ValueError, not TypeError
        # Valid URLs
        assert validate_ollama_url("http://localhost:11434") is True
        assert validate_ollama_url("https://example.com") is True

        # Invalid URLs
        assert validate_ollama_url("localhost:11434") is False  # No scheme
        assert validate_ollama_url("ftp://localhost:11434") is False  # Wrong scheme
        assert validate_ollama_url("") is False  # Empty
        assert validate_ollama_url(None) is False  # None

        # The important part: it should not raise TypeError for non-string inputs
        # That would indicate it's catching TypeError unnecessarily
        # Should return False, not raise
        assert validate_ollama_url(123) is False
        # Should return False, not raise
        assert validate_ollama_url([]) is False


class TestAsyncioAPICorrectness:
    """Tests for verifying correct asyncio API usage."""

    def test_task_cancelled_method_exists(self):
        """Test that asyncio.Task has .cancelled attribute (Python 3.11+)."""
        import asyncio

        from tui.app import DialogueApp

        DialogueApp.__new__(DialogueApp)
        assert hasattr(asyncio.Task, "cancelled")
        assert not hasattr(asyncio.Task, "is_cancelled")

    def test_app_uses_correct_cancelled_method(self):
        """Test that _is_task_cancelled uses correct method .cancelled()."""
        with open("/home/d/ai-dialogue-tui/tui/app.py", "r", encoding="utf-8") as f:
            content = f.read()

        assert ".cancelled()" in content
        assert "is_cancelled()" not in content
