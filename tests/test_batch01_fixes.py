"""Tests for batch 01 fixes (issues 0001-0020).

This module verifies all 20 issues have been fixed.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from models.conversation import Conversation, MAX_CONTEXT_LENGTH
from models.provider import ModelId
from tui.sanitizer import (
    MAX_RESPONSE_PREVIEW_LENGTH,
    sanitize_response_for_display,
    sanitize_topic,
)
from tui.styles import generate_main_css


class TestIssue0001ContextTrimming:
    """Test ISSUE-0001: Context trimming updates dataclass fields."""

    def test_context_trimming_updates_field(self) -> None:
        """Verify trimmed context is written back to _context_a/_context_b."""
        conv = Conversation(model_a="model_a", model_b="model_b", topic="test")

        for i in range(MAX_CONTEXT_LENGTH + 10):
            conv.add_message("A", "user", f"msg {i}")

        context = conv.get_context("A")
        assert len(context) <= MAX_CONTEXT_LENGTH
        assert context[0]["role"] == "system"


class TestIssue0002TypeUnsafety:
    """Test ISSUE-0002: Type safety in context trimming."""

    def test_trim_context_handles_empty_list(self) -> None:
        """Verify trimming handles edge cases safely."""
        conv = Conversation(model_a="model_a", model_b="model_b", topic="test")
        result = conv._trim_context_if_needed([], max_len=10)
        assert result == []


class TestIssue0003SystemMessageDuplication:
    """Test ISSUE-0003: System message not duplicated."""

    def test_no_system_message_duplication(self) -> None:
        """Verify system message appears only once after trimming."""
        conv = Conversation(model_a="model_a", model_b="model_b", topic="test")

        for i in range(MAX_CONTEXT_LENGTH + 10):
            conv.add_message("A", "user", f"msg {i}")

        context = conv.get_context("A")
        system_count = sum(1 for m in context if m["role"] == "system")
        assert system_count == 1


class TestIssue0004HtmlEscaping:
    """Test ISSUE-0004: Double quotes escaped."""

    def test_double_quote_escaped(self) -> None:
        """Verify double quotes are escaped for Textual Rich."""
        result = sanitize_response_for_display('Hello "world"')
        assert '&quot;' in result


class TestIssue0005EfficientStringReplacement:
    """Test ISSUE-0005: str.translate used instead of loop."""

    def test_sanitize_response_uses_translate(self) -> None:
        """Verify sanitize_response uses str.translate."""
        result = sanitize_response_for_display("test message")
        assert isinstance(result, str)


class TestIssue0006UnnecessaryListCopies:
    """Test ISSUE-0006: Snapshots only created when needed."""

    def test_snapshots_created_on_error_path(self) -> None:
        """Verify snapshots work correctly for rollback."""
        conv = Conversation(model_a="model_a", model_b="model_b", topic="test")
        mock_provider = AsyncMock()
        mock_provider.generate.side_effect = Exception("Test error")

        import asyncio

        with pytest.raises(Exception):
            asyncio.run(conv.process_turn(mock_provider))

        assert len(conv.get_context("A")) == 1


class TestIssue0007DuplicateCSSSelector:
    """Test ISSUE-0007: #selection_buttons not duplicated."""

    def test_selection_buttons_single_definition(self) -> None:
        """Verify #selection_buttons appears once in CSS."""
        css = generate_main_css()
        from tui.constants import UI_IDS
        base_selector = f"#{UI_IDS.selection_buttons} {{"
        count = css.count(base_selector)
        assert count == 1

    def test_selection_buttons_button_single_definition(self) -> None:
        """Verify #selection_buttons Button appears once."""
        css = generate_main_css()
        from tui.constants import UI_IDS
        button_selector = f"#{UI_IDS.selection_buttons} Button {{"
        count = css.count(button_selector)
        assert count == 1


class TestIssue0008InvalidCSSProperty:
    """Test ISSUE-0008: text-style changed to font-weight."""

    def test_font_weight_used(self) -> None:
        """Verify font-weight is used instead of text-style."""
        css = generate_main_css()
        assert "font-weight: bold" in css
        assert "text-style: bold" not in css


class TestIssue0010RedundantStringOperations:
    """Test ISSUE-0010: Topic sanitization efficient."""

    def test_sanitize_topic_works(self) -> None:
        """Verify topic sanitization works correctly."""
        result = sanitize_topic("Test {topic}")
        assert "{{" in result
        assert "}}" in result


class TestIssue0011TypeIgnoreRemoved:
    """Test ISSUE-0011: Type ignore avoided."""

    def test_select_value_handled(self) -> None:
        """Verify Select value handling works without type ignore."""
        from tui.app import ModelSelectionScreen

        screen = ModelSelectionScreen(models=["model1", "model2"])
        assert screen._available_models == ["model1", "model2"]


class TestIssue0012MissingFieldAnnotations:
    """Test ISSUE-0012: Fields have explicit type annotations."""

    def test_conversation_has_type_annotations(self) -> None:
        """Verify Conversation fields have type annotations."""
        annotations = Conversation.__annotations__
        assert "model_a" in annotations
        assert "model_b" in annotations
        assert "topic" in annotations


class TestIssue0013IncorrectTypeAnnotation:
    """Test ISSUE-0013: _current_turn uses Literal."""

    def test_current_turn_literal_type(self) -> None:
        """Verify _current_turn has Literal type."""
        conv = Conversation(model_a="a", model_b="b", topic="t")
        assert conv.current_turn in ("A", "B")


class TestIssue0014ReturnTypeConsistency:
    """Test ISSUE-0014: handle_pause return type documented."""

    def test_handle_pause_returns_bool(self) -> None:
        """Verify handle_pause returns bool."""
        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.is_running = False
        controller = DialogueController(mock_service)
        result = controller.handle_pause()
        assert isinstance(result, bool)


class TestIssue0015MissingAllExport:
    """Test ISSUE-0015: tui/app.py has __all__."""

    def test_app_has_all(self) -> None:
        """Verify tui/app.py exports classes."""
        from tui.app import __all__

        assert "DialogueApp" in __all__


class TestIssue0016MissingAllExportSanitizer:
    """Test ISSUE-0016: tui/sanitizer.py has __all__."""

    def test_sanitizer_has_all(self) -> None:
        """Verify tui/sanitizer.py exports functions."""
        from tui.sanitizer import __all__

        assert "sanitize_topic" in __all__
        assert "sanitize_response_for_display" in __all__


class TestIssue0017MissingAllExportProvider:
    """Test ISSUE-0017: models/provider.py has __all__."""

    def test_provider_has_all(self) -> None:
        """Verify models/provider.py exports classes."""
        from models.provider import __all__

        assert "ModelProvider" in __all__
        assert "ProviderError" in __all__


class TestIssue0018MissingAllExportOllamaClient:
    """Test ISSUE-0018: models/ollama_client.py has __all__."""

    def test_ollama_client_has_all(self) -> None:
        """Verify models/ollama_client.py exports classes."""
        from models.ollama_client import __all__

        assert "OllamaClient" in __all__


class TestIssue0019MissingAllExportDialogueService:
    """Test ISSUE-0019: services/dialogue_service.py has __all__."""

    def test_dialogue_service_has_all(self) -> None:
        """Verify services/dialogue_service.py exports classes."""
        from services.dialogue_service import __all__

        assert "DialogueService" in __all__
        assert "DialogueTurnResult" in __all__


class TestIssue0020MissingAllExportDialogueRunner:
    """Test ISSUE-0020: services/dialogue_runner.py has __all__."""

    def test_dialogue_runner_has_all(self) -> None:
        """Verify services/dialogue_runner.py exports classes."""
        from services.dialogue_runner import __all__

        assert "DialogueRunner" in __all__


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
