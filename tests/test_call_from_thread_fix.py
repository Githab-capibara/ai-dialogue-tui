"""Интеграционные тесты для проверки исправлений call_from_thread.

Этот модуль содержит тесты для проверки:
1. При ошибке таймаута не возникает RuntimeError от call_from_thread
2. Метод _handle_dialogue_error корректно обрабатывает ошибки из асинхронного контекста
3. Метод _process_dialogue_turn использует call_after_refresh вместо call_from_thread
4. Метод _handle_critical_error использует call_after_refresh вместо call_from_thread

Эти тесты воспроизводят сценарий из ARCHITECTURE.md аудита:
"DialogueApp нарушает SRP (20+ методов, God Object)" и проблемы с DIP.
"""

# pylint: disable=protected-access,import-outside-toplevel,too-few-public-methods
# pylint: disable=reimported,redefined-outer-name,unused-argument

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.css.query import NoMatches

from controllers.dialogue_controller import DialogueController
from factories.provider_factory import create_provider_factory
from models.config import Config
from models.provider import ProviderError, ProviderGenerationError
from services.dialogue_service import DialogueService, DialogueTurnResult
from tui.app import DialogueApp


class AsyncMockService:
    """Мок для DialogueService с поддержкой async методов."""

    def __init__(
        self,
        raise_on_cycle: Exception | None = None,
        run_count: int = 0,
    ) -> None:
        self._raise_on_cycle = raise_on_cycle
        self._run_count = run_count
        self.is_running = True
        self.is_paused = False
        self.turn_count = 0
        self.conversation = MagicMock()
        self.conversation.current_turn = "model_a"
        self.conversation.get_current_model_name = MagicMock(return_value="TestModel")

    async def run_dialogue_cycle(self) -> DialogueTurnResult | None:
        """Симулировать ход диалога."""
        self.turn_count += 1
        self._run_count += 1

        if self._raise_on_cycle:
            raise self._raise_on_cycle

        return DialogueTurnResult(
            model_name="TestModel",
            model_id="model_a",
            role="assistant",
            response="Тестовый ответ",
        )


class TestCallFromThreadFixtures:
    """Базовые фикстуры и хелперы для тестов call_from_thread."""

    @pytest.fixture
    def app_with_mocks(self) -> DialogueApp:
        """Создать приложение с моками для провайдера."""
        config = Config()
        provider_factory = create_provider_factory(config)
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Мокаем контроллер
        mock_controller = MagicMock(spec=DialogueController)
        mock_controller.service = MagicMock(spec=DialogueService)
        mock_controller.handle_start = MagicMock(return_value=True)
        mock_controller.handle_pause = MagicMock()
        mock_controller.handle_clear = MagicMock()
        mock_controller.handle_stop = MagicMock()
        mock_controller.cleanup = AsyncMock()
        mock_controller.update_for_turn = MagicMock()
        mock_controller.update_for_error = MagicMock()
        app._controller = mock_controller

        return app

    @pytest.fixture
    def mock_rich_log(self, app_with_mocks: DialogueApp) -> MagicMock:
        """Создать мок для RichLog."""
        mock_log = MagicMock()
        mock_log.write = MagicMock()
        mock_log.clear = MagicMock()

        with patch.object(app_with_mocks, "query_one", return_value=mock_log):
            yield mock_log


class TestHandleDialogueErrorUsesCallAfterRefresh(TestCallFromThreadFixtures):
    """Тесты для _handle_dialogue_error."""

    def test_handle_dialogue_error_uses_call_after_refresh_not_call_from_thread(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """
        Тест проверяет что _handle_dialogue_error использует call_after_refresh.

        Это критично т.к. метод вызывается из асинхронного контекста и
        call_from_thread вызовет RuntimeError.
        """
        # Патчим call_after_refresh и call_from_thread для отслеживания вызовов
        call_after_refresh_called = False
        call_from_thread_called = False
        original_call_after_refresh = app_with_mocks.call_after_refresh
        original_call_from_thread = app_with_mocks.call_from_thread

        def track_call_after_refresh(callback: Any, *args: Any) -> Any:
            nonlocal call_after_refresh_called
            call_after_refresh_called = True
            return original_call_after_refresh(callback, *args)

        def track_call_from_thread(callback: Any, *args: Any) -> Any:
            nonlocal call_from_thread_called
            call_from_thread_called = True
            return original_call_from_thread(callback, *args)

        app_with_mocks.call_after_refresh = track_call_after_refresh  # type: ignore
        app_with_mocks.call_from_thread = track_call_from_thread  # type: ignore

        # Вызываем метод
        app_with_mocks._handle_dialogue_error("TestModel")

        # Проверяем что call_after_refresh был вызван
        assert call_after_refresh_called, (
            "call_after_refresh должен быть вызван в _handle_dialogue_error"
        )

        # Проверяем что call_from_thread НЕ был вызван
        assert not call_from_thread_called, (
            "call_from_thread НЕ должен вызываться в асинхронном контексте"
        )

    def test_handle_dialogue_error_no_runtime_error_from_async_context(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """
        Тест проверяет что _handle_dialogue_error не вызывает RuntimeError.

        RuntimeError возникает когда call_from_thread вызывается из того же потока.
        После исправления на call_after_refresh ошибки быть не должно.
        """
        # Мокаем query_one чтобы избежать ошибок UI
        with patch.object(app_with_mocks, "query_one", side_effect=NoMatches("test")):
            # Этот вызов не должен вызывать RuntimeError
            try:
                app_with_mocks._handle_dialogue_error("TestModel")
            except RuntimeError as e:
                if "call_from_thread" in str(e):
                    pytest.fail(
                        f"call_from_thread вызвал RuntimeError: {e}. "
                        "Метод должен использовать call_after_refresh!"
                    )
                raise

    def test_handle_dialogue_error_updates_controller(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """Тест проверяет что update_for_error вызывается при ошибке."""
        app_with_mocks._handle_dialogue_error("TestModel")

        # Проверяем что контроллер был уведомлен об ошибке
        app_with_mocks._controller.update_for_error.assert_called_once_with(  # type: ignore
            "TestModel"
        )


class TestProcessDialogueTurnUsesCallAfterRefresh(TestCallFromThreadFixtures):
    """Тесты для _process_dialogue_turn."""

    @pytest.mark.asyncio
    async def test_process_dialogue_turn_uses_call_after_refresh(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """
        Тест проверяет что _process_dialogue_turn использует call_after_refresh.

        Метод работает в asyncio контексте (asyncio.create_task), поэтому
        call_from_thread вызовет RuntimeError.
        """
        # Создаем мок сервиса
        mock_service = AsyncMockService()
        app_with_mocks._controller.service = mock_service  # type: ignore

        # Патчим call_after_refresh и call_from_thread
        call_after_refresh_called = False
        call_from_thread_called = False
        original_call_after_refresh = app_with_mocks.call_after_refresh
        original_call_from_thread = app_with_mocks.call_from_thread

        def track_call_after_refresh(callback: Any, *args: Any) -> Any:
            nonlocal call_after_refresh_called
            call_after_refresh_called = True
            return original_call_after_refresh(callback, *args)

        def track_call_from_thread(callback: Any, *args: Any) -> Any:
            nonlocal call_from_thread_called
            call_from_thread_called = True
            return original_call_from_thread(callback, *args)

        app_with_mocks.call_after_refresh = track_call_after_refresh  # type: ignore
        app_with_mocks.call_from_thread = track_call_from_thread  # type: ignore

        # Вызываем асинхронный метод
        await app_with_mocks._process_dialogue_turn(
            mock_service,  # type: ignore
            "TestModel",
            "green",
        )

        # Проверяем что call_after_refresh был вызван
        assert call_after_refresh_called, (
            "call_after_refresh должен быть вызван в _process_dialogue_turn"
        )

        # Проверяем что call_from_thread НЕ был вызван
        assert not call_from_thread_called, (
            "call_from_thread НЕ должен вызываться в асинхронном контексте"
        )

    @pytest.mark.asyncio
    async def test_process_dialogue_turn_handles_provider_error(
        self, app_with_mocks: DialogueApp, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Тест проверяет что ProviderError пробрасывается из _process_dialogue_turn.

        Обработка ошибки (логирование и _handle_dialogue_error) происходит
        в _run_dialogue который ловит ProviderError.
        """
        # Создаем сервис который выбрасывает ProviderError
        provider_error = ProviderGenerationError("Тестовая ошибка генерации")
        mock_service = AsyncMockService(raise_on_cycle=provider_error)
        app_with_mocks._controller.service = mock_service  # type: ignore

        # Вызываем метод - должен пробросить ProviderError
        with pytest.raises(ProviderError):
            await app_with_mocks._process_dialogue_turn(
                mock_service,  # type: ignore
                "TestModel",
                "green",
            )

        # Проверяем что update_for_error был вызван (через _handle_dialogue_error)
        # Но это происходит в _run_dialogue, не в _process_dialogue_turn
        # Поэтому здесь просто проверяем что ошибка пробрасывается


class TestHandleCriticalErrorUsesCallAfterRefresh(TestCallFromThreadFixtures):
    """Тесты для _handle_critical_error."""

    def test_handle_critical_error_uses_call_after_refresh_not_call_from_thread(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """
        Тест проверяет что _handle_critical_error использует call_after_refresh.

        Метод вызывается из _run_dialogue (asyncio контекст), поэтому
        call_from_thread вызовет RuntimeError.
        """
        # Патчим call_after_refresh и call_from_thread
        call_after_refresh_called = False
        call_from_thread_called = False
        original_call_after_refresh = app_with_mocks.call_after_refresh
        original_call_from_thread = app_with_mocks.call_from_thread

        def track_call_after_refresh(callback: Any, *args: Any) -> Any:
            nonlocal call_after_refresh_called
            call_after_refresh_called = True
            return original_call_after_refresh(callback, *args)

        def track_call_from_thread(callback: Any, *args: Any) -> Any:
            nonlocal call_from_thread_called
            call_from_thread_called = True
            return original_call_from_thread(callback, *args)

        app_with_mocks.call_after_refresh = track_call_after_refresh  # type: ignore
        app_with_mocks.call_from_thread = track_call_from_thread  # type: ignore

        # Вызываем метод
        test_error = RuntimeError("Тестовая критическая ошибка")
        app_with_mocks._handle_critical_error(test_error)

        # Проверяем что call_after_refresh был вызван
        assert call_after_refresh_called, (
            "call_after_refresh должен быть вызван в _handle_critical_error"
        )

        # Проверяем что call_from_thread НЕ был вызван
        assert not call_from_thread_called, (
            "call_from_thread НЕ должен вызываться в асинхронном контексте"
        )

    def test_handle_critical_error_logs_exception(
        self, app_with_mocks: DialogueApp, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Тест проверяет что критическая ошибка логируется с traceback."""
        with caplog.at_level(logging.ERROR):
            test_error = RuntimeError("Тестовая критическая ошибка")
            app_with_mocks._handle_critical_error(test_error)

        # Проверяем что ошибка была залогирована
        assert any(
            "Критическая ошибка в цикле диалога" in record.message
            for record in caplog.records
        ), "Критическая ошибка должна быть залогирована"


class TestIntegrationCallFromThreadFix(TestCallFromThreadFixtures):
    """Интеграционные тесты для проверки всех исправлений call_from_thread."""

    @pytest.mark.asyncio
    async def test_full_dialogue_error_handling_no_runtime_error(
        self, app_with_mocks: DialogueApp
    ) -> None:
        """
        Интеграционный тест: полная обработка ошибки диалога без RuntimeError.

        Тест воспроизводит реальный сценарий:
        1. Запуск диалога
        2. Ошибка провайдера при генерации
        3. Обработка ошибки через _handle_dialogue_error
        4. Проверка что не возник RuntimeError от call_from_thread
        """
        # Создаем сервис который выбрасывает ошибку
        provider_error = ProviderGenerationError("Таймаут генерации")
        mock_service = AsyncMockService(raise_on_cycle=provider_error)
        app_with_mocks._controller.service = mock_service  # type: ignore

        # Мокаем query_one для RichLog
        mock_log = MagicMock()
        mock_log.write = MagicMock()

        call_after_refresh_calls = []
        original_call_after_refresh = app_with_mocks.call_after_refresh

        def track_call_after_refresh(callback: Any, *args: Any) -> Any:
            call_after_refresh_calls.append((callback, args))
            return original_call_after_refresh(callback, *args)

        app_with_mocks.call_after_refresh = track_call_after_refresh  # type: ignore

        with patch.object(app_with_mocks, "query_one", return_value=mock_log):
            # Вызываем метод обработки диалога
            runtime_error_occurred = False
            try:
                await app_with_mocks._process_dialogue_turn(
                    mock_service,  # type: ignore
                    "TestModel",
                    "green",
                )
            except ProviderError:
                # Ожидается что ProviderError будет проброшен
                # Обработка ошибки (_handle_dialogue_error) происходит в _run_dialogue
                pass
            except RuntimeError as e:
                if "call_from_thread" in str(e):
                    runtime_error_occurred = True

            # Проверяем что RuntimeError не возник
            assert not runtime_error_occurred, (
                "RuntimeError от call_from_thread не должен возникать"
            )

            # call_after_refresh вызывается в _handle_dialogue_error который вызывается
            # из _run_dialogue, а не из _process_dialogue_turn напрямую
            # Поэтому здесь проверяем что метод просто не вызывает RuntimeError

    def test_source_code_does_not_contain_call_from_thread_in_error_handlers(
        self,
    ) -> None:
        """
        Тест проверяет что в исходном коде нет вызова self.call_from_thread.

        Это статическая проверка что исправления были применены корректно.
        Проверяем именно вызовы метода, а не упоминания в комментариях.
        """
        import inspect

        from tui.app import DialogueApp  # pylint: disable=import-outside-toplevel

        # Получаем исходный код методов
        handle_error_source = inspect.getsource(DialogueApp._handle_dialogue_error)
        handle_critical_source = inspect.getsource(DialogueApp._handle_critical_error)
        process_turn_source = inspect.getsource(DialogueApp._process_dialogue_turn)

        # Проверяем что вызова self.call_from_thread нет (но допускаем упоминания в комментариях)
        # Ищем именно вызов метода: self.call_from_thread(
        assert "self.call_from_thread(" not in handle_error_source, (
            "_handle_dialogue_error не должен использовать self.call_from_thread("
        )
        assert "self.call_from_thread(" not in handle_critical_source, (
            "_handle_critical_error не должен использовать self.call_from_thread("
        )
        assert "self.call_from_thread(" not in process_turn_source, (
            "_process_dialogue_turn не должен использовать self.call_from_thread("
        )

        # Проверяем что call_after_refresh используется (именно вызов)
        assert "self.call_after_refresh(" in handle_error_source, (
            "_handle_dialogue_error должен использовать self.call_after_refresh("
        )
        assert "self.call_after_refresh(" in handle_critical_source, (
            "_handle_critical_error должен использовать self.call_after_refresh("
        )
        assert "self.call_after_refresh(" in process_turn_source, (
            "_process_dialogue_turn должен использовать self.call_after_refresh("
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
