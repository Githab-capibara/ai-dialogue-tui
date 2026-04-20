"""Tests for verifying architectural refactoring.

Each test verifies one specific architectural fix:
1. Removal of create_ollama_client from tui/styles.py (Clean Architecture)
2. Removal of StatusStyle from tui/styles.py (YAGNI)
3. Removal of get_status_style_string from tui/styles.py (YAGNI)
4. Removal of Sanitizer Protocol from tui/sanitizer.py (YAGNI)
5. Removal of _RequestConfig from models/ollama_client.py (YAGNI)
6. Simplification of _add_message_to_context (KISS)
7. Using ModelProvider for typing in tui/app.py (DIP)
8. No coupling between tui/styles.py and models/ollama_client.py
"""

# pylint: disable=protected-access,import-outside-toplevel,consider-using-with

from __future__ import annotations

import ast
import inspect

import pytest

from models.conversation import Conversation

# --- Test 1: create_ollama_client removed from tui/styles.py ---


def test_create_ollama_client_removed_from_styles() -> None:
    """create_ollama_client should not be in tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "def create_ollama_client" not in source
    assert "create_ollama_client" not in source.split("__all__")[1] if "__all__" in source else True


def test_styles_no_ollama_import() -> None:
    """tui/styles.py should not import models.ollama_client."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "from models.ollama_client" not in source
    assert "import models.ollama_client" not in source


# --- Test 2: StatusStyle removed from tui/styles.py ---


def test_status_style_removed_from_styles() -> None:
    """StatusStyle Enum should not be in tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "class StatusStyle" not in source
    assert "from enum import Enum" not in source


# --- Test 3: get_status_style_string removed from tui/styles.py ---


def test_get_status_style_string_removed_from_styles() -> None:
    """get_status_style_string should not be in tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "def get_status_style_string" not in source


# --- Test 4: Sanitizer Protocol removed from tui/sanitizer.py ---


def test_sanitizer_protocol_removed() -> None:
    """Sanitizer Protocol should not be in tui/sanitizer.py."""
    with open("tui/sanitizer.py", encoding="utf-8") as f:
        source = f.read()

    assert "class Sanitizer" not in source
    assert "Protocol" not in source or "typing.Protocol" not in source
    assert "runtime_checkable" not in source


def test_sanitizer_module_has_only_functions() -> None:
    """tui/sanitizer.py should contain only functions, not classes."""
    tree = ast.parse(open("tui/sanitizer.py", encoding="utf-8").read())

    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    assert len(classes) == 0, f"Found classes in sanitizer.py: {[c.name for c in classes]}"


# --- Test 5: _RequestConfig removed from models/ollama_client.py ---


def test_request_config_removed() -> None:
    """_RequestConfig should not be in models/ollama_client.py."""
    with open("models/ollama_client.py", encoding="utf-8") as f:
        source = f.read()

    assert "class _RequestConfig" not in source


def test_request_config_not_in_module() -> None:
    """_RequestConfig should not be accessible in module."""
    import models.ollama_client as module

    assert not hasattr(module, "_RequestConfig")


# --- Test 6: _add_message_to_context simplified ---


def test_add_message_to_context_no_callable_param() -> None:
    """_add_message_to_context should not accept Callable parameter."""
    sig = inspect.signature(Conversation._add_message_to_context)
    params = list(sig.parameters.keys())

    assert "set_context" not in params
    assert "model_id" in params or len(params) <= 3


def test_add_message_to_context_simple_signature() -> None:
    """_add_message_to_context signature should be simplified."""
    sig = inspect.signature(Conversation._add_message_to_context)
    params = sig.parameters

    # Should be: self, context, model_id (or role, content)
    assert len(params) <= 4, f"Too many parameters: {list(params.keys())}"


# --- Test 7: tui/app.py uses ModelProvider for typing ---


def test_app_uses_model_provider_type() -> None:
    """tui/app.py should use ModelProvider for _client type."""
    with open("tui/app.py", encoding="utf-8") as f:
        source = f.read()

    assert "ModelProvider" in source


# --- Test 8: No coupling between tui/styles.py and models/ollama_client ---


def test_no_coupling_styles_to_ollama() -> None:
    """tui/styles.py should not depend on models.ollama_client."""
    with open("tui/styles.py", encoding="utf-8") as f:
        styles_source = f.read()

    assert "ollama_client" not in styles_source.lower()
    assert "OllamaClient" not in styles_source


def test_styles_only_contains_style_definitions() -> None:
    """tui/styles.py should contain only styles and UI identifiers."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    # At top level should be only:
    # - dataclass definitions (MessageStyles, UIElementIDs, CSSClasses)
    # - Constants (MESSAGE_STYLES, UI_IDS, CSS_CLASSES)
    # - generate_main_css function
    allowed_functions = {"generate_main_css"}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.name in allowed_functions, f"Unexpected function: {node.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
