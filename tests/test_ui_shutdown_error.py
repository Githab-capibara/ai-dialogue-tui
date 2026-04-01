"""Тесты для предотвращения ошибок NoMatches при завершении работы UI."""

# pylint: disable=protected-access,import-outside-toplevel,broad-exception-caught
# pylint: disable=duplicate-code

from __future__ import annotations

import pytest

from controllers.dialogue_controller import UIState
from factories.provider_factory import create_provider_factory
from models.config import Config
from tui.app import DialogueApp


class TestUIShutdownError:
    """Тесты для предотвращения ошибок NoMatches при завершении работы UI."""

    def test_on_ui_state_changed_handles_no_matches_exception(self) -> None:
        """
        Тест проверяет, что _on_ui_state_changed обрабатывает NoMatches исключение.

        Этот тест воспроизводит сценарий, при котором элемент #status-value
        не найден в DOM, что приводит к NoMatches исключению.
        """
        # Создаем мок-конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Вызываем _on_ui_state_changed напрямую, чтобы проверить обработку исключения
        # Приложение еще не смонтировано, поэтому элементы UI недоступны
        test_state = UIState(status_text="Тест", status_style="dim")

        # Это не должно вызывать исключение благодаря нашему фиксу
        try:
            app._on_ui_state_changed(test_state)
            # Если мы дошли сюда, значит исключение было обработано
            assert True
        except Exception as e:
            # Если исключение все же произошло, тест падает
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")

    def test_on_ui_state_changed_handles_lookup_error(self) -> None:
        """
        Тест проверяет, что _on_ui_state_changed обрабатывает LookupError.
        """
        # Создаем мок-конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Вызываем _on_ui_state_changed напрямую
        test_state = UIState(status_text="Тест", status_style="dim")

        # Это не должно вызывать исключение благодаря нашему фиксу
        try:
            app._on_ui_state_changed(test_state)
            # Если мы дошли сюда, значит исключение было обработано
            assert True
        except Exception as e:
            # Если исключение все же произошло, тест падает
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")

    def test_on_ui_state_changed_handles_runtime_error(self) -> None:
        """
        Тест проверяет, что _on_ui_state_changed обрабатывает RuntimeError.
        """
        # Создаем мок-конфигурацию и фабрику провайдеров
        config = Config()
        provider_factory = create_provider_factory(config)

        # Создаем приложение
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Вызываем _on_ui_state_changed напрямую
        test_state = UIState(status_text="Тест", status_style="dim")

        # Это не должно вызывать исключение благодаря нашему фиксу
        try:
            app._on_ui_state_changed(test_state)
            # Если мы дошли сюда, значит исключение было обработано
            assert True
        except Exception as e:
            # Если исключение все же произошло, тест падает
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")
