"""Тесты для проверки устойчивости цикла диалога к ошибкам провайдера.

Проверяет что диалог продолжается после ProviderError,
а не останавливается из-за проброса исключения.
"""

# pylint: disable=protected-access,redefined-outer-name

from __future__ import annotations

import asyncio
from itertools import chain, repeat
from unittest.mock import AsyncMock

import pytest

from models.config import Config
from models.conversation import Conversation
from models.provider import (
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from services.dialogue_runner import DialogueRunner
from services.dialogue_service import DialogueService


class TestDialogueRunnerProviderErrorHandling:
    """Тесты что DialogueRunner корректно обрабатывает ProviderError.

    Проверяет что:
    1. ProviderError не пробрасывается из _run_loop
    2. Диалог продолжает работу после ошибки
    3. Callback on_error вызывается с правильным именем модели
    4. Разные типы ProviderError обрабатываются одинаково
    """

    def _create_service_and_runner(
        self,
    ) -> tuple[DialogueService, DialogueRunner, AsyncMock]:
        """Создать сервис, раннер и мок провайдера."""
        conversation = Conversation(
            model_a="model-a",
            model_b="model-b",
            topic="Test topic",
        )
        mock_provider = AsyncMock()
        config = Config(pause_between_messages=0.0)

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
            config=config,
        )
        runner = DialogueRunner(service=service, config=config)

        return service, runner, mock_provider

    @pytest.mark.asyncio
    async def test_dialogue_continues_after_provider_connection_error(self) -> None:
        """Диалог продолжается после ProviderConnectionError."""
        service, runner, mock_provider = self._create_service_and_runner()

        error_model_names: list[str] = []

        def on_error(model_name: str) -> None:
            error_model_names.append(model_name)

        turn_results: list = []

        def on_turn(result: object) -> None:
            turn_results.append(result)

        # Ошибка один раз, потом бесконечные успехи
        mock_provider.generate.side_effect = chain(
            [ProviderConnectionError("Connection failed")],
            repeat("Success response"),
        )

        service.start()

        async def stop_after_turns() -> None:
            while len(turn_results) < 1:
                await asyncio.sleep(0.01)
            service.stop()

        stop_task = asyncio.create_task(stop_after_turns())

        await runner.start(on_turn=on_turn, on_error=on_error)
        await runner._dialogue_task  # type: ignore[union-attr]
        stop_task.cancel()
        try:
            await stop_task
        except asyncio.CancelledError:
            pass

        assert len(error_model_names) >= 1
        assert error_model_names[0] == "model-a"
        assert len(turn_results) >= 1

    @pytest.mark.asyncio
    async def test_dialogue_continues_after_provider_generation_error(self) -> None:
        """Диалог продолжается после ProviderGenerationError."""
        service, runner, mock_provider = self._create_service_and_runner()

        error_raised = False

        def on_error(_model_name: str) -> None:
            nonlocal error_raised
            error_raised = True

        turn_results: list = []

        def on_turn(result: object) -> None:
            turn_results.append(result)

        mock_provider.generate.side_effect = chain(
            [ProviderGenerationError("Generation failed")],
            repeat("Success response"),
        )

        service.start()

        async def stop_after_turns() -> None:
            while len(turn_results) < 1 and not error_raised:
                await asyncio.sleep(0.01)
            service.stop()

        stop_task = asyncio.create_task(stop_after_turns())

        await runner.start(on_turn=on_turn, on_error=on_error)
        await runner._dialogue_task  # type: ignore[union-attr]
        stop_task.cancel()
        try:
            await stop_task
        except asyncio.CancelledError:
            pass

        assert error_raised is True
        assert len(turn_results) >= 1

    @pytest.mark.asyncio
    async def test_provider_error_does_not_propagate_from_run_loop(self) -> None:
        """ProviderError не должен пробрасываться из _run_loop."""
        service, runner, mock_provider = self._create_service_and_runner()

        mock_provider.generate.side_effect = ProviderError("Test error")

        service.start()

        async def stop_after_short_time() -> None:
            await asyncio.sleep(0.05)
            service.stop()

        stop_task = asyncio.create_task(stop_after_short_time())

        try:
            await runner.start(on_turn=None, on_error=None)
            await runner._dialogue_task  # type: ignore[union-attr]
        except ProviderError:
            pytest.fail("ProviderError пробросился из _run_loop!")
        finally:
            stop_task.cancel()
            try:
                await stop_task
            except asyncio.CancelledError:
                pass

    @pytest.mark.asyncio
    async def test_multiple_consecutive_errors_handled(self) -> None:
        """Множественные ошибки подряд обрабатываются корректно."""
        service, runner, mock_provider = self._create_service_and_runner()

        error_count = 0

        def on_error(_model_name: str) -> None:
            nonlocal error_count
            error_count += 1

        mock_provider.generate.side_effect = ProviderConnectionError("Fail")

        service.start()

        async def stop_after_errors() -> None:
            while error_count < 2:
                await asyncio.sleep(0.01)
            service.stop()

        stop_task = asyncio.create_task(stop_after_errors())

        try:
            await runner.start(on_turn=None, on_error=on_error)
            await runner._dialogue_task  # type: ignore[union-attr]
        except ProviderError:
            pytest.fail("ProviderError пробросился из _run_loop!")
        finally:
            stop_task.cancel()
            try:
                await stop_task
            except asyncio.CancelledError:
                pass

        assert error_count >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
