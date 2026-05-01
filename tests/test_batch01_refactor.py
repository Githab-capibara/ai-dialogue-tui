"""Tests for Batch-01 refactoring fixes (issues BLE001, SLF001, type annotations).

This module verifies specific refactoring improvements:
- BLE001: Blind exception catching replaced with specific exception types
- SLF001: Protected access replaced with public properties
- Type annotation gaps fixed
- Import statements moved to module level
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest


class TestBLE001ExceptionHandling:
    """Tests for BLE001: Blind exception catching fixes."""

    def test_dialogue_controller_cleanup_exception_types(self) -> None:
        """Verify DialogueController.cleanup catches specific exceptions."""
        from controllers.dialogue_controller import DialogueController

        source = inspect.getsource(DialogueController.cleanup)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должны быть конкретные типы
        assert "asyncio.CancelledError" in source or "RuntimeError" in source

    def test_main_cleanup_dialogue_task_exception_types(self) -> None:
        """Verify main._cleanup_dialogue_task catches specific exceptions."""
        import main

        source = inspect.getsource(main._cleanup_dialogue_task)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должен быть asyncio.CancelledError
        assert "asyncio.CancelledError" in source

    def test_main_cleanup_controller_exception_types(self) -> None:
        """Verify main._cleanup_controller catches specific exceptions."""
        import main

        source = inspect.getsource(main._cleanup_controller)
        # Не должно быть except Exception:
        assert "except Exception" not in source

    def test_main_cleanup_client_exception_types(self) -> None:
        """Verify main._cleanup_client catches specific exceptions."""
        import main

        source = inspect.getsource(main._cleanup_client)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должен быть asyncio.CancelledError
        assert "asyncio.CancelledError" in source

    def test_main_cleanup_log_file_exception_types(self) -> None:
        """Verify main._close_log_file catches OSError."""
        import main

        source = inspect.getsource(main._close_log_file)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должен быть OSError
        assert "OSError" in source

    def test_tui_app_cleanup_dialogue_task_exception_types(self) -> None:
        """Verify DialogueApp._cleanup_dialogue_task catches RuntimeError."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._cleanup_dialogue_task)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должен быть RuntimeError
        assert "RuntimeError" in source

    def test_tui_app_cleanup_controller_exception_types(self) -> None:
        """Verify DialogueApp._cleanup_controller catches specific exceptions."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._cleanup_controller)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должны быть конкретные типы
        assert "AttributeError" in source
        assert "asyncio.CancelledError" in source

    def test_tui_app_cleanup_client_exception_types(self) -> None:
        """Verify DialogueApp._cleanup_client catches specific exceptions."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._cleanup_client)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должны быть конкретные типы
        assert "AttributeError" in source
        assert "asyncio.CancelledError" in source

    def test_tui_app_cleanup_log_file_exception_types(self) -> None:
        """Verify DialogueApp._cleanup_log_file catches OSError."""
        from tui.app import DialogueApp

        source = inspect.getsource(DialogueApp._cleanup_log_file)
        # Не должно быть except Exception:
        assert "except Exception" not in source
        # Должен быть OSError
        assert "OSError" in source


class TestLoggingImportAtModuleLevel:
    """Tests for import statements moved to module level."""

    def test_dialogue_controller_import_logging_at_module_level(self) -> None:
        """Verify logging is imported at module level in dialogue_controller."""
        import controllers.dialogue_controller as module

        # Проверяем, что logging есть в пространстве модуля
        assert hasattr(module, "logging") or "logging" in dir(module)

    def test_dialogue_controller_no_inline_import(self) -> None:
        """Verify no inline import logging in dialogue_controller functions."""
        from controllers.dialogue_controller import DialogueController

        source = inspect.getsource(DialogueController.cleanup)
        # Не должно быть inline import
        assert "import logging" not in source


class TestSLF001ProtectedAccess:
    """Tests for SLF001: Protected access replaced with public properties."""

    def test_dialogue_app_has_dialogue_task_property(self) -> None:
        """Verify DialogueApp has dialogue_task property."""
        from tui.app import DialogueApp

        assert hasattr(DialogueApp, "dialogue_task")
        prop = getattr(DialogueApp, "dialogue_task")
        assert isinstance(prop, property)

    def test_dialogue_app_has_controller_property(self) -> None:
        """Verify DialogueApp has controller property."""
        from tui.app import DialogueApp

        assert hasattr(DialogueApp, "controller")
        prop = getattr(DialogueApp, "controller")
        assert isinstance(prop, property)

    def test_dialogue_task_property_returns_correct_type(self) -> None:
        """Verify dialogue_task property has correct return type annotation."""
        from tui.app import DialogueApp

        prop = getattr(DialogueApp, "dialogue_task")
        # Проверяем return annotation
        assert "asyncio.Task[None] | None" in prop.fget.__annotations__["return"]

    def test_controller_property_returns_correct_type(self) -> None:
        """Verify controller property has correct return type annotation."""
        from tui.app import DialogueApp

        prop = getattr(DialogueApp, "controller")
        # Проверяем return annotation
        assert "DialogueController | None" in prop.fget.__annotations__["return"]

    def test_main_uses_public_properties(self) -> None:
        """Verify main.py uses public properties instead of protected access."""
        import main

        source = inspect.getsource(main._cleanup_dialogue_task)
        # Должен использовать .dialogue_task
        assert "dialogue_task" in source
        # Не должен использовать ._dialogue_task
        assert "._dialogue_task" not in source

        source = inspect.getsource(main._cleanup_controller)
        # Должен использовать .controller
        assert "controller" in source
        # Не должен использовать ._controller
        assert "._controller" not in source


class TestTypeAnnotationGaps:
    """Tests for type annotation gaps fixed."""

    def test_ollama_client_aexit_has_type_annotations(self) -> None:
        """Verify OllamaClient.__aexit__ has type annotations for all parameters."""
        from models.ollama_client import OllamaClient

        sig = inspect.signature(OllamaClient.__aexit__)
        params = sig.parameters

        # Проверяем, что все параметры имеют аннотации
        for param_name in ["exc_type", "exc_val", "exc_tb"]:
            assert param_name in params
            assert params[param_name].annotation != inspect.Parameter.empty

    def test_ollama_client_aexit_exc_type_annotation(self) -> None:
        """Verify __aexit__ exc_type has BaseException type annotation."""
        from models.ollama_client import OllamaClient

        sig = inspect.signature(OllamaClient.__aexit__)
        exc_type_param = sig.parameters["exc_type"]

        # Аннотация должна быть BaseException | None
        annotation_str = str(exc_type_param.annotation)
        assert "BaseException" in annotation_str
        assert "None" in annotation_str

    def test_ollama_client_aexit_exc_val_annotation(self) -> None:
        """Verify __aexit__ exc_val has BaseException | None annotation."""
        from models.ollama_client import OllamaClient

        sig = inspect.signature(OllamaClient.__aexit__)
        exc_val_param = sig.parameters["exc_val"]

        annotation_str = str(exc_val_param.annotation)
        assert "BaseException" in annotation_str
        assert "None" in annotation_str

    def test_ollama_client_aexit_exc_tb_annotation(self) -> None:
        """Verify __aexit__ exc_tb has BaseException | None annotation."""
        from models.ollama_client import OllamaClient

        sig = inspect.signature(OllamaClient.__aexit__)
        exc_tb_param = sig.parameters["exc_tb"]

        annotation_str = str(exc_tb_param.annotation)
        assert "BaseException" in annotation_str
        assert "None" in annotation_str

    def test_ollama_client_aexit_returns_none(self) -> None:
        """Verify __aexit__ has None return annotation."""
        from models.ollama_client import OllamaClient

        sig = inspect.signature(OllamaClient.__aexit__)
        assert sig.return_annotation is None or "None" in str(sig.return_annotation)


class TestImportAtModuleLevel:
    """Tests for imports moved to module level."""

    def test_main_imports_concurrent_futures_at_module_level(self) -> None:
        """Verify concurrent.futures is imported at module level in main.py."""
        import main

        # Проверяем, что concurrent.futures есть в модуле
        assert hasattr(main, "concurrent") or "concurrent" in dir(main)

    def test_main_no_inline_import_of_concurrent_futures(self) -> None:
        """Verify no inline import of concurrent.futures in main functions."""
        import main

        # Проверяем, что ни одна функция не содержит inline import
        for name in dir(main):
            if name.startswith("_") and callable(getattr(main, name)):
                source = inspect.getsource(getattr(main, name))
                if "import concurrent" in source:
                    pytest.fail(f"Function {name} has inline import of concurrent")


class TestImportAsyncioAtModuleLevel:
    """Tests for asyncio import at module level."""

    def test_dialogue_controller_imports_asyncio_at_module_level(self) -> None:
        """Verify asyncio is imported at module level in dialogue_controller."""
        import controllers.dialogue_controller as module

        # Проверяем, что asyncio есть в пространстве модуля
        assert hasattr(module, "asyncio") or "asyncio" in dir(module)


class TestDialogueControllerCleanupIntegration:
    """Integration tests for DialogueController cleanup behavior."""

    @pytest.mark.asyncio
    async def test_cleanup_handles_attribute_error(self) -> None:
        """Verify cleanup handles AttributeError when service already cleaned."""
        from unittest.mock import AsyncMock, MagicMock

        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.cleanup = AsyncMock(side_effect=AttributeError("already cleaned"))
        mock_callback = MagicMock()

        controller = DialogueController(
            service=mock_service,
            on_state_changed=mock_callback,
        )

        # Не должно выбросить исключение
        await controller.cleanup()

    @pytest.mark.asyncio
    async def test_cleanup_handles_cancelled_error(self) -> None:
        """Verify cleanup handles CancelledError gracefully."""
        from unittest.mock import AsyncMock, MagicMock

        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.cleanup = AsyncMock(side_effect=asyncio.CancelledError())
        mock_callback = MagicMock()

        controller = DialogueController(
            service=mock_service,
            on_state_changed=mock_callback,
        )

        # Не должно выбросить исключение
        await controller.cleanup()

    @pytest.mark.asyncio
    async def test_cleanup_handles_runtime_error(self) -> None:
        """Verify cleanup handles RuntimeError gracefully."""
        from unittest.mock import AsyncMock, MagicMock

        from controllers.dialogue_controller import DialogueController

        mock_service = MagicMock()
        mock_service.cleanup = AsyncMock(side_effect=RuntimeError("service error"))
        mock_callback = MagicMock()

        controller = DialogueController(
            service=mock_service,
            on_state_changed=mock_callback,
        )

        # Не должно выбросить исключение
        await controller.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
