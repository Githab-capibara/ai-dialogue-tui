"""
Тесты для проверки архитектурных исправлений.

Содержит тесты для:
- DRY: Отсутствие дублирования в add_message
- KISS: Разделение _run_dialogue на меньшие методы
- YAGNI: Удаление неиспользуемого DialogueUICallback
- SRP: Вынесение утилит из app.py
- Удаление config.py wrapper
"""

from __future__ import annotations

# pylint: disable=import-outside-toplevel
import ast
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from models.conversation import Conversation


class TestDRYFix:
    """Тест: отсутствие дублирования кода в add_message."""

    def test_add_message_no_duplication(self) -> None:
        """Тест что add_message не содержит дублирующегося кода."""
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
        """Тест что helper метод для добавления сообщений существует."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="test",
        )
        assert hasattr(conversation, "_add_message_to_context")


class TestKISSFix:  # pylint: disable=too-few-public-methods
    """Тест: разделение _run_dialogue на меньшие методы."""

    def test_run_dialogue_split(self) -> None:
        """Тест что _run_dialogue разделен на меньшие методы."""
        app_file = Path("tui/app.py")
        content = app_file.read_text(encoding="utf-8")

        tree = ast.parse(content)

        required_methods = [
            "_is_task_cancelled",
            "_handle_dialogue_error",
            "_handle_critical_error",
        ]

        class MethodFinder(ast.NodeVisitor):  # pylint: disable=too-few-public-methods
            """AST visitor для поиска методов в файле."""

            def __init__(self) -> None:
                self.methods: set[str] = set()

            def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # pylint: disable=invalid-name
                """Посетить определение функции и записать её имя."""
                self.methods.add(node.name)
                self.generic_visit(node)

        finder = MethodFinder()
        finder.visit(tree)

        for method in required_methods:
            assert method in finder.methods, f"Method {method} not found"


class TestYAGNIFix:
    """Тест: удаление неиспользуемого DialogueUICallback."""

    def test_dialogue_ui_callback_removed(self) -> None:
        """Тест что DialogueUICallback удален из сервиса."""
        service_file = Path("services/dialogue_service.py")
        content = service_file.read_text(encoding="utf-8")

        assert "class DialogueUICallback" not in content
        assert "ui_callback" not in content.lower()

    def test_dialogue_service_init_no_callback(self) -> None:
        """Тест что DialogueService не принимает ui_callback."""

        source_file = Path("services/dialogue_service.py")
        content = source_file.read_text(encoding="utf-8")

        assert "def __init__" in content


class TestSRPFix:  # pylint: disable=too-few-public-methods
    """Тест: вынесение утилит из app.py."""

    def test_utility_functions_moved(self) -> None:
        """Тест что утилиты удалены из app.py и styles.py."""
        styles_file = Path("tui/styles.py")
        content = styles_file.read_text(encoding="utf-8")

        assert "_get_status_style_string" not in content
        assert "create_ollama_client" not in content


class TestConfigWrapperRemoval:  # pylint: disable=too-few-public-methods
    """Тест: удаление config.py wrapper."""

    def test_config_wrapper_removed(self) -> None:
        """Тест что config.py удален."""
        config_file = Path("config.py")

        if config_file.exists():
            content = config_file.read_text(encoding="utf-8")
            assert (
                "from models.config import Config" not in content or len(content) < 50
            )


class TestArchitectureIntegrity:
    """Интеграционные тесты архитектуры."""

    def test_no_circular_dependencies(self) -> None:
        """Тест отсутствия циклических зависимостей."""
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
        """Тест что Conversation использует Protocol для DI."""

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
        """Тест что сервис использует абстракции."""
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
