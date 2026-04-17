"""Тесты для обработки NoMatches исключения в _on_ui_state_changed.

Этот модуль содержит тесты для проверки корректной обработки метода
_on_ui_state_changed в DialogueApp, когда элемент #status-value недоступен.
"""

# pylint: disable=protected-access,import-outside-toplevel,broad-exception-caught
# pylint: disable=duplicate-code

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest
from textual.css.query import NoMatches

from controllers.dialogue_controller import UIState
from factories.provider_factory import create_provider_factory
from models.config import Config
from tui.app import DialogueApp


class TestUIStateChangedNoMatches:
    """Тесты для обработки NoMatches исключения в _on_ui_state_changed."""

    def test_on_ui_state_changed_handles_no_matches_exception(self) -> None:
        """
        Тест проверяет, что _on_ui_state_changed не вызывает ошибок,
        когда элемент #status-value недоступен (NoMatches исключение).

        Этот тест воспроизводит сценарий, при котором элемент #status-value
        не найден в DOM, что приводит к NoMatches исключению.
        """
        # Создаем конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Создаем тестовое состояние UI
        test_state = UIState(status_text="Тест", status_style="dim")

        # Мок query_one который выбрасывает NoMatches
        with patch.object(app, "query_one", side_effect=NoMatches("#status-value")):
            # Это не должно вызывать исключение благодаря обработке NoMatches
            try:
                app._on_ui_state_changed(test_state)
                # Если мы дошли сюда, значит исключение было обработано
                assert True
            except Exception as e:
                # Если исключение все же произошло, тест падает
                pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")

    def test_on_ui_state_changed_logs_debug_on_no_matches(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        Тест проверяет, что при NoMatches исключении выполняется логирование на уровне DEBUG.

        Args:
            caplog: Фикстура pytest для перехвата логов.
        """
        # Создаем конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Создаем тестовое состояние UI
        test_state = UIState(status_text="Тест", status_style="dim")

        # Устанавливаем уровень логирования на DEBUG
        with caplog.at_level(logging.DEBUG):
            # Мок query_one который выбрасывает NoMatches
            with patch.object(app, "query_one", side_effect=NoMatches("#status-value")):
                # Вызываем метод
                app._on_ui_state_changed(test_state)

        # Проверяем что логирование произошло на уровне DEBUG
        assert "Элемент #status-value недоступен для обновления" in caplog.text

        # Проверяем что логирование было именно на уровне DEBUG (не ERROR)
        debug_records = [record for record in caplog.records if record.levelname == "DEBUG"]
        assert len(debug_records) > 0
        assert any("Элемент #status-value недоступен для обновления" in record.message for record in debug_records)

    def test_on_ui_state_changed_no_error_when_element_missing(self) -> None:
        """
        Тест проверяет, что метод завершается без ошибок при отсутствии элемента.

        Проверяет идемпотентность и безопасность вызова метода даже когда
        UI элементы ещё не инициализированы.
        """
        # Создаем конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Создаем тестовое состояние UI с различными параметрами
        test_states = [
            UIState(status_text="Тест 1", status_style="dim"),
            UIState(status_text="Тест 2", status_style="green"),
            UIState(status_text="Тест 3", status_style="red"),
            UIState(status_text="", status_style="yellow"),
        ]

        # Мок query_one который выбрасывает NoMatches для всех вызовов
        with patch.object(app, "query_one", side_effect=NoMatches("#status-value")):
            # Все вызовы должны завершиться без ошибок
            for state in test_states:
                try:
                    app._on_ui_state_changed(state)
                except Exception as e:
                    pytest.fail(f"_on_ui_state_changed raised exception for state {state}: {e}")

    def test_on_ui_state_changed_with_mock_label(self) -> None:
        """
        Тест проверяет корректную работу метода с моком Label.

        Проверяет что при успешном получении элемента update вызывается
        с правильными аргументами.
        """
        # Создаем конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Создаем тестовое состояние UI
        test_state = UIState(status_text="Готов к запуску", status_style="green")

        # Создаем мок Label
        mock_label = MagicMock()

        # Мок query_one который возвращает мок Label
        with patch.object(app, "query_one", return_value=mock_label):
            # Вызываем метод
            app._on_ui_state_changed(test_state)

        # Проверяем что update был вызван один раз
        mock_label.update.assert_called_once()

        # Проверяем аргумент вызова
        expected_arg = "[green]Готов к запуску[/green]"
        mock_label.update.assert_called_with(expected_arg)

    def test_on_ui_state_changed_preserves_exception_chain_for_other_errors(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Тест проверяет, что другие исключения (LookupError, RuntimeError)
        логируются с полным traceback.

        Args:
            caplog: Фикстура pytest для перехвата логов.
        """
        # Создаем конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Создаем тестовое состояние UI
        test_state = UIState(status_text="Тест", status_style="dim")

        # Устанавливаем уровень логирования на ERROR
        with caplog.at_level(logging.ERROR):
            # Мок query_one который выбрасывает LookupError
            with patch.object(app, "query_one", side_effect=LookupError("Test error")):
                # Вызываем метод - не должно вызывать исключение
                app._on_ui_state_changed(test_state)

        # Проверяем что логирование произошло на уровне ERROR
        error_records = [record for record in caplog.records if record.levelname == "ERROR"]
        assert len(error_records) > 0
        assert any("при обновлении UI состояния" in record.message for record in error_records)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
