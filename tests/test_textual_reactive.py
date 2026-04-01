"""
Тест для выявления проблем с reactive атрибутами Textual.

Этот модуль содержит тесты для проверки корректного определения
reactive атрибутов в Textual App, что предотвращает ошибки типа:
AttributeError: 'DialogueApp' object has no attribute '_reactive_sub_title'

Note:
    Тесты используют доступ к внутренним атрибутам Textual для проверки.
"""

# pylint: disable=protected-access,import-outside-toplevel

from textual.reactive import reactive

from tui.app import DialogueApp


def test_sub_title_is_reactive() -> None:
    """
    Тест что sub_title определён как reactive атрибут.

    Это предотвращает ошибку:
    AttributeError: 'DialogueApp' object has no attribute '_reactive_sub_title'

    Причина ошибки:
        Textual Header пытается watch'ить sub_title как reactive.
        Если sub_title определён как обычный атрибут класса,
        возникает ошибка _reactive_sub_title.
    """
    assert hasattr(DialogueApp, "sub_title"), "sub_title атрибут должен существовать"

    sub_title_attr = DialogueApp.sub_title
    assert isinstance(sub_title_attr, reactive), (
        f"sub_title должен быть reactive, получено: {type(sub_title_attr)}"
    )


def test_title_class_constant() -> None:
    """Тест что TITLE определён как классовая константа."""
    assert hasattr(DialogueApp, "TITLE")
    assert DialogueApp.TITLE == "AI Dialogue TUI"


def test_dialogueapp_can_be_instantiated() -> None:
    """Тест что DialogueApp может быть создан без ошибок."""
    app = DialogueApp()
    assert app is not None
    assert app.title == "AI Dialogue TUI"


def test_app_has_required_bindings() -> None:
    """Тест что приложение имеет необходимые bindings."""
    app = DialogueApp()
    binding_keys = [b.key for b in app.BINDINGS]
    assert "ctrl+q" in binding_keys
    assert "ctrl+p" in binding_keys
    assert "ctrl+r" in binding_keys


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
