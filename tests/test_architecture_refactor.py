"""Тесты для проверки архитектурного рефакторинга.

Каждый тест проверяет одно конкретное архитектурное исправление:
1. Удаление create_ollama_client из tui/styles.py (Clean Architecture)
2. Удаление StatusStyle из tui/styles.py (YAGNI)
3. Удаление get_status_style_string из tui/styles.py (YAGNI)
4. Удаление Sanitizer Protocol из tui/sanitizer.py (YAGNI)
5. Удаление _RequestConfig из models/ollama_client.py (YAGNI)
6. Упрощение _add_message_to_context (KISS)
7. Отсутствие прямого импорта OllamaClient в tui/app.py (DIP)
8. Отсутствие coupling между tui/styles.py и models/ollama_client.py
"""

# pylint: disable=protected-access,import-outside-toplevel,consider-using-with

from __future__ import annotations

import ast
import inspect

import pytest

from models.conversation import Conversation

# --- Тест 1: create_ollama_client удалён из tui/styles.py ---


def test_create_ollama_client_removed_from_styles() -> None:
    """create_ollama_client не должен быть в tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "def create_ollama_client" not in source
    assert (
        "create_ollama_client" not in source.split("__all__")[1]
        if "__all__" in source
        else True
    )


def test_styles_no_ollama_import() -> None:
    """tui/styles.py не должен импортировать models.ollama_client."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "from models.ollama_client" not in source
    assert "import models.ollama_client" not in source


# --- Тест 2: StatusStyle удалён из tui/styles.py ---


def test_status_style_removed_from_styles() -> None:
    """StatusStyle Enum не должен быть в tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "class StatusStyle" not in source
    assert "from enum import Enum" not in source


# --- Тест 3: get_status_style_string удалён из tui/styles.py ---


def test_get_status_style_string_removed_from_styles() -> None:
    """get_status_style_string не должен быть в tui/styles.py."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    assert "def get_status_style_string" not in source


# --- Тест 4: Sanitizer Protocol удалён из tui/sanitizer.py ---


def test_sanitizer_protocol_removed() -> None:
    """Sanitizer Protocol не должен быть в tui/sanitizer.py."""
    with open("tui/sanitizer.py", encoding="utf-8") as f:
        source = f.read()

    assert "class Sanitizer" not in source
    assert "Protocol" not in source or "typing.Protocol" not in source
    assert "runtime_checkable" not in source


def test_sanitizer_module_has_only_functions() -> None:
    """tui/sanitizer.py должен содержать только функции, не классы."""
    tree = ast.parse(open("tui/sanitizer.py", encoding="utf-8").read())

    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    assert len(classes) == 0, (
        f"Найдены классы в sanitizer.py: {[c.name for c in classes]}"
    )


# --- Тест 5: _RequestConfig удалён из models/ollama_client.py ---


def test_request_config_removed() -> None:
    """_RequestConfig не должен быть в models/ollama_client.py."""
    with open("models/ollama_client.py", encoding="utf-8") as f:
        source = f.read()

    assert "class _RequestConfig" not in source


def test_request_config_not_in_module() -> None:
    """_RequestConfig не должен быть доступен в модуле."""
    import models.ollama_client as module

    assert not hasattr(module, "_RequestConfig")


# --- Тест 6: _add_message_to_context упрощён ---


def test_add_message_to_context_no_callable_param() -> None:
    """_add_message_to_context не должен принимать Callable параметр."""
    sig = inspect.signature(Conversation._add_message_to_context)
    params = list(sig.parameters.keys())

    assert "set_context" not in params
    assert "model_id" in params or len(params) <= 3


def test_add_message_to_context_simple_signature() -> None:
    """Сигнатура _add_message_to_context должна быть упрощена."""
    sig = inspect.signature(Conversation._add_message_to_context)
    params = sig.parameters

    # Должно быть: self, context, model_id (или role, content)
    assert len(params) <= 4, f"Слишком много параметров: {list(params.keys())}"


# --- Тест 7: tui/app.py не импортирует OllamaClient напрямую ---


def test_app_no_direct_ollama_import() -> None:
    """tui/app.py не должен импортировать OllamaClient на верхнем уровне."""
    with open("tui/app.py", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    # Проверяем top-level импорты
    top_level_imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                top_level_imports.append(node.module)

    assert "models.ollama_client" not in top_level_imports


def test_app_uses_model_provider_type() -> None:
    """tui/app.py должен использовать ModelProvider для типа _client."""
    with open("tui/app.py", encoding="utf-8") as f:
        source = f.read()

    assert "ModelProvider" in source


# --- Тест 8: Отсутствие coupling между tui/styles.py и models/ollama_client ---


def test_no_coupling_styles_to_ollama() -> None:
    """tui/styles.py не должен зависеть от models.ollama_client."""
    with open("tui/styles.py", encoding="utf-8") as f:
        styles_source = f.read()

    assert "ollama_client" not in styles_source.lower()
    assert "OllamaClient" not in styles_source


def test_styles_only_contains_style_definitions() -> None:
    """tui/styles.py должен содержать только стили и UI-идентификаторы."""
    with open("tui/styles.py", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)

    # На верхнем уровне должны быть только:
    # - dataclass определения (MessageStyles, UIElementIDs, CSSClasses)
    # - Константы (MESSAGE_STYLES, UI_IDS, CSS_CLASSES)
    # - Функция generate_main_css
    allowed_functions = {"generate_main_css"}

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.name in allowed_functions, f"Неожиданная функция: {node.name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
