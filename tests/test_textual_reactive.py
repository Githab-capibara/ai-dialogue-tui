"""
Тест для выявления проблем с reactive атрибутами Textual.

Этот модуль содержит тесты для проверки корректного определения
reactive атрибутов в Textual App, что предотвращает ошибки типа:
AttributeError: 'DialogueApp' object has no attribute '_reactive_sub_title'

Note:
    Тесты используют доступ к внутренним атрибутам Textual для проверки.

"""

# pylint: disable=protected-access,import-outside-toplevel

from tui.app import DialogueApp


def test_sub_title_attribute_exists() -> None:
    """
    Тест что sub_title атрибут существует и может быть использован.

    Это предотвращает ошибку:
    AttributeError: 'DialogueApp' object has no attribute '_reactive_sub_title'

    Причина ошибки:
        Textual Header пытается watch'ить sub_title как reactive.
        Если sub_title определён как обычный атрибут класса,
        возникает ошибка _reactive_sub_title.
    """
    assert hasattr(DialogueApp, "sub_title"), "sub_title атрибут должен существовать"

    app = DialogueApp()
    assert hasattr(app, "sub_title"), "sub_title экземпляр атрибут должен существовать"
    assert isinstance(app.sub_title, str), "sub_title должен быть строкой"


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
    # Проверяем что bindings это список
    bindings_list: list = list(app.BINDINGS) if hasattr(app, "BINDINGS") else []  # type: ignore[assignment]
    keys: list[str] = []
    for b in bindings_list:
        if hasattr(b, 'key'):
            keys.append(b.key)  # type: ignore[attr-defined]
        elif isinstance(b, tuple) and len(b) > 0:
            keys.append(str(b[0]))  # type: ignore[union-attr]
    assert "ctrl+q" in keys
    assert "ctrl+p" in keys
    assert "ctrl+r" in keys


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
