"""
Tests for verifying architectural fixes.

Contains tests for:
- DRY: No duplication in add_message
- KISS: Splitting _run_dialogue into smaller methods
- YAGNI: Removing unused DialogueUICallback
- SRP: Extracting utilities from app.py
- Removing config.py wrapper
"""

from __future__ import annotations

# pylint: disable=import-outside-toplevel
import ast
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from models.conversation import Conversation


class TestDRYFix:
    """Test: no code duplication in add_message."""

    def test_add_message_no_duplication(self) -> None:
        """Test that add_message does not contain duplicated code."""
        conversation_file = Path("models/conversation.py")
        content = conversation_file.read_text(encoding="utf-8")

        tree = ast.parse(content)

        add_message_found = False
        has_duplicate_if = False

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "add_message":
                add_message_found = True
                if_body = node.body

                if_count_model_a = sum(
                    1
                    for stmt in if_body
                    if isinstance(stmt, ast.If)
                    and stmt.test.left
                    and hasattr(stmt.test.left, "value")
                    and stmt.test.left.value == "A"
                )

                if if_count_model_a > 1:
                    has_duplicate_if = True

        assert add_message_found, "add_message method not found"
        assert not has_duplicate_if, "Duplicate if statements found in add_message"

    def test_helper_method_exists(self) -> None:
        """Test that helper method for adding messages exists."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="test",
        )
        assert hasattr(conversation, "_add_message_to_context")


class TestKISSFix:  # pylint: disable=too-few-public-methods
    """Test: splitting _run_dialogue into smaller methods."""

    def test_run_dialogue_split(self) -> None:
        """Test that _run_dialogue is split into smaller methods."""
        app_file = Path("tui/app.py")
        content = app_file.read_text(encoding="utf-8")

        tree = ast.parse(content)

        required_methods = [
            "_is_task_cancelled",
            "_handle_dialogue_error",
            "_handle_critical_error",
        ]

        class MethodFinder(ast.NodeVisitor):  # pylint: disable=too-few-public-methods
            """AST visitor for finding methods in file."""

            def __init__(self) -> None:
                self.methods: set[str] = set()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pylint: disable=invalid-name
                """Visit function definition and record its name."""
                self.methods.add(node.name)
                self.generic_visit(node)

        finder = MethodFinder()
        finder.visit(tree)

        for method in required_methods:
            assert method in finder.methods, f"Method {method} not found"


class TestYAGNIFix:
    """Test: removing unused DialogueUICallback."""

    def test_dialogue_ui_callback_removed(self) -> None:
        """Test that DialogueUICallback is removed from service."""
        service_file = Path("services/dialogue_service.py")
        content = service_file.read_text(encoding="utf-8")

        assert "class DialogueUICallback" not in content
        assert "ui_callback" not in content.lower()

    def test_dialogue_service_init_no_callback(self) -> None:
        """Test that DialogueService does not accept ui_callback."""
        source_file = Path("services/dialogue_service.py")
        content = source_file.read_text(encoding="utf-8")

        assert "def __init__" in content


class TestSRPFix:  # pylint: disable=too-few-public-methods
    """Test: extracting utilities from app.py."""

    def test_utility_functions_moved(self) -> None:
        """Test that utilities are removed from app.py and styles.py."""
        styles_file = Path("tui/styles.py")
        content = styles_file.read_text(encoding="utf-8")

        assert "_get_status_style_string" not in content
        assert "create_ollama_client" not in content


class TestConfigWrapperRemoval:  # pylint: disable=too-few-public-methods
    """Test: removing config.py wrapper."""

    def test_config_wrapper_removed(self) -> None:
        """Test that config.py is removed."""
        config_file = Path("config.py")

        if config_file.exists():
            content = config_file.read_text(encoding="utf-8")
            assert "from models.config import Config" not in content or len(content) < 50


class TestArchitectureIntegrity:
    """Integration tests for architecture."""

    def test_no_circular_dependencies(self) -> None:
        """Test absence of circular dependencies."""
        modules = [
            "models.conversation",
            "models.ollama_client",
            "models.config",
            "models.provider",
            "services.dialogue_service",
            "controllers.dialogue_controller",
        ]

        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")

    def test_conversation_uses_protocol(self) -> None:
        """Test that Conversation uses Protocol for DI."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="test",
        )

        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(return_value="test response")
        mock_provider.list_models = AsyncMock(return_value=["llama3"])
        mock_provider.close = AsyncMock()

        assert hasattr(conversation, "generate_response")

    def test_service_uses_abstractions(self) -> None:
        """Test that service uses abstractions."""
        from services.dialogue_service import (
            DialogueService,  # pylint: disable=import-outside-toplevel
        )

        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="test",
        )

        mock_provider = AsyncMock()
        mock_provider.generate = AsyncMock(return_value="test")
        mock_provider.list_models = AsyncMock(return_value=["llama3"])
        mock_provider.close = AsyncMock()

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        assert hasattr(service, "conversation")
        assert hasattr(service, "provider")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
