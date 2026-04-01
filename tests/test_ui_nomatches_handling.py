"""Тесты для обработки недоступности UI элементов при активных модальных окнах."""

# pylint: disable=protected-access,import-outside-toplevel

from __future__ import annotations

import pytest
from textual.css.query import NoMatches
from textual.widgets import Label

from controllers.dialogue_controller import UIState
from models.config import Config
from tui.app import DialogueApp


class TestUINoMatchesHandling:
    """Тесты для предотвращения ошибок NoMatches при работе с модальными окнами."""

    def test_on_ui_state_changed_no_matches_logged_as_debug(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Тест проверяет, что NoMatches исключение логируется на уровне DEBUG.

        Сценарий: элемент #status-value недоступен (модальное окно активно),
        ошибка должна быть обработана без ERROR логирования.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Тест", status_style="green")

        # Вызываем метод когда UI ещё не смонтирован
        with caplog.at_level("DEBUG"):
            app._on_ui_state_changed(test_state)

        # Проверяем что было записано DEBUG сообщение
        assert "Элемент #status-value недоступен для обновления" in caplog.text
        # Проверяем что ERROR не было
        assert "Ошибка при обновлении UI состояния" not in caplog.text

    def test_on_ui_state_changed_runtime_error_logged_as_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Тест проверяет, что RuntimeError логируется на уровне ERROR.

        Сценарий: неожиданная ошибка при обновлении UI должна быть
        залогирована как ERROR с полным traceback.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Тест", status_style="green")

        # Мок query_one для выброса RuntimeError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise RuntimeError("Test runtime error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("ERROR"):
            app._on_ui_state_changed(test_state)

        # Проверяем что ERROR было записано
        assert "Ошибка при обновлении UI состояния" in caplog.text

    def test_on_ui_state_changed_lookup_error_logged_as_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Тест проверяет, что LookupError логируется на уровне ERROR.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Тест", status_style="green")

        # Мок query_one для выброса LookupError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise LookupError("Test lookup error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("ERROR"):
            app._on_ui_state_changed(test_state)

        # Проверяем что ERROR было записано
        assert "Ошибка при обновлении UI состояния" in caplog.text

    def test_on_ui_state_changed_screen_stack_error_logged_as_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Тест проверяет, что ScreenStackError логируется на уровне ERROR.
        """
        from textual.app import ScreenStackError

        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Тест", status_style="green")

        # Мок query_one для выброса ScreenStackError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise ScreenStackError("Test screen stack error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("ERROR"):
            app._on_ui_state_changed(test_state)

        # Проверяем что ERROR было записано
        assert "Ошибка при обновлении UI состояния" in caplog.text

    def test_on_ui_state_changed_no_matches_does_not_reraise(self) -> None:
        """
        Тест проверяет, что NoMatches не вызывает повторного выброса исключения.

        Метод должен обработать исключение и продолжить работу без ошибок.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Тест", status_style="green")

        # Это не должно вызывать исключение
        app._on_ui_state_changed(test_state)

        # Если код дошёл сюда - тест пройден
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
