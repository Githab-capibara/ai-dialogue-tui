"""Тесты архитектурных принципов для проверки правильного разделения слоёв.

Этот модуль проверяет что:
1. Сервис не содержит UI-концепций
2. Разделение styles и constants
3. Маппинг style в UI слое
4. Отсутствие циклических зависимостей
5. Separation of Concerns
"""

from __future__ import annotations

import ast

import pytest

from services.dialogue_service import DialogueService


def get_imports_from_file(filepath: str) -> list[str]:
    """Получить список импортов из файла."""
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


class TestServiceNoUIConcepts:
    """Тест: Сервис не содержит UI-концепций."""

    def test_dialogue_service_has_no_get_model_info_and_style_method(self) -> None:
        """Проверить, что DialogueService НЕ имеет метода get_model_info_and_style."""
        assert not hasattr(DialogueService, "get_model_info_and_style")

    def test_dialogue_service_no_tui_imports(self) -> None:
        """Проверить, что DialogueService НЕ импортирует из tui."""
        imports = get_imports_from_file("services/dialogue_service.py")

        tui_imports = [imp for imp in imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, f"Found tui imports in service: {tui_imports}"


class TestStylesAndConstantsSeparation:
    """Тест: Разделение styles и constants."""

    def test_constants_file_exists(self) -> None:
        """Проверить существование tui/constants.py."""
        import os

        assert os.path.exists("tui/constants.py"), "tui/constants.py should exist"

    def test_styles_only_contains_generate_main_css(self) -> None:
        """Проверить, что tui/styles.py содержит только generate_main_css."""
        with open("tui/styles.py", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)

        functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]

        assert "generate_main_css" in functions
        assert len(functions) == 1, f"Found extra functions in styles.py: {functions}"

    def test_ui_ids_imported_from_constants(self) -> None:
        """Проверить, что UI_IDS импортируется из tui.constants."""
        with open("tui/styles.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui.constants import" in source
        assert "UI_IDS" in source

    def test_message_styles_imported_from_constants(self) -> None:
        """Проверить, что MESSAGE_STYLES импортируется из tui.constants."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui.constants import" in source
        assert "MESSAGE_STYLES" in source


class TestStyleMappingInUI:
    """Тест: Маппинг style в UI слое."""

    def test_model_style_mapper_exists(self) -> None:
        """Проверить, что ModelStyleMapper существует."""
        from services.model_style_mapper import ModelStyleMapper

        assert ModelStyleMapper is not None

    def test_style_mapping_works_correctly(self) -> None:
        """Проверить, что маппинг model_id -> style работает корректно."""
        from services.model_style_mapper import ModelStyleMapper

        mapper = ModelStyleMapper()

        # Тест для модели A
        info_a = mapper.get_style_info("A", "llama3")
        assert info_a.model_name == "llama3"
        assert info_a.style_id == "model_a"
        assert info_a.model_id == "A"

        # Тест для модели B
        info_b = mapper.get_style_info("B", "mistral")
        assert info_b.model_name == "mistral"
        assert info_b.style_id == "model_b"
        assert info_b.model_id == "B"


class TestNoCircularDependencies:
    """Тест: Отсутствие циклических зависимостей."""

    def test_models_no_tui_imports(self) -> None:
        """Проверить, что models не импортирует из tui."""
        models_imports = get_imports_from_file("models/conversation.py")

        tui_imports = [imp for imp in models_imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, f"Found tui imports in models: {tui_imports}"

    def test_services_no_tui_imports(self) -> None:
        """Проверить, что services не импортирует из tui."""
        services_imports = get_imports_from_file("services/dialogue_service.py")

        tui_imports = [imp for imp in services_imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, f"Found tui imports in services: {tui_imports}"

    def test_controllers_no_tui_imports(self) -> None:
        """Проверить, что controllers не импортирует из tui."""
        controllers_imports = get_imports_from_file(
            "controllers/dialogue_controller.py"
        )

        tui_imports = [imp for imp in controllers_imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, f"Found tui imports in controllers: {tui_imports}"


class TestSeparationOfConcerns:
    """Тест: Separation of Concerns."""

    def test_ui_can_import_from_models(self) -> None:
        """Проверить, что UI (tui) может импортировать из models."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from models" in source
        assert "Conversation" in source

    def test_ui_can_import_from_services(self) -> None:
        """Проверить, что UI (tui) может импортировать из services."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from services" in source
        assert "DialogueService" in source

    def test_ui_can_import_from_controllers(self) -> None:
        """Проверить, что UI (tui) может импортировать из controllers."""
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        assert "from controllers" in source
        assert "DialogueController" in source

    def test_models_no_ui_imports(self) -> None:
        """Проверить, что models НЕ импортирует из tui."""
        imports = get_imports_from_file("models/conversation.py")

        tui_imports = [imp for imp in imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, (
            f"models should not import from tui: {tui_imports}"
        )

    def test_services_no_ui_imports(self) -> None:
        """Проверить, что services НЕ импортирует из tui."""
        imports = get_imports_from_file("services/dialogue_service.py")

        tui_imports = [imp for imp in imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, (
            f"services should not import from tui: {tui_imports}"
        )

    def test_controllers_no_ui_imports(self) -> None:
        """Проверить, что controllers НЕ импортирует из tui."""
        imports = get_imports_from_file("controllers/dialogue_controller.py")

        tui_imports = [imp for imp in imports if imp.startswith("tui")]
        assert len(tui_imports) == 0, (
            f"controllers should not import from tui: {tui_imports}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
