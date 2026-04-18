"""Сервис для управления циклом диалога.

Этот модуль содержит бизнес-логику выполнения циклов диалога.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from models.config import Config
from models.provider import ProviderError

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.dialogue_service import DialogueService, DialogueTurnResult

log = logging.getLogger(__name__)


class DialogueRunner:
    """Сервис для запуска и управления циклом диалога.

    Инкапсулирует логику выполнения основного цикла диалога,
    обработки ошибок и управления задачами.

    Attributes:
        service: Сервис диалога для управления бизнес-логикой.
        config: Конфигурация для параметров (паузы, таймауты).

    Note:
        Этот класс содержит бизнес-логику цикла диалога и не зависит от UI.

    """

    def __init__(
        self,
        service: DialogueService,
        config: Config | None = None,
    ) -> None:
        """Инициализация раннера диалога.

        Args:
            service: Сервис диалога для управления.
            config: Конфигурация для параметров цикла.

        """
        self._service = service
        self._config = config or Config()
        self._dialogue_task: asyncio.Task[None] | None = None

    @property
    def service(self) -> DialogueService:
        """Получить сервис диалога."""
        return self._service

    @property
    def dialogue_task(self) -> asyncio.Task[None] | None:
        """Получить задачу диалога."""
        return self._dialogue_task

    async def start(
        self,
        on_turn: Callable[[DialogueTurnResult], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        """Запустить цикл диалога в фоновой задаче.

        Args:
            on_turn: Callback для обработки каждого хода.
            on_error: Callback для обработки ошибок генерации.

        """
        loop = asyncio.get_running_loop()
        self._dialogue_task = loop.create_task(self._run_loop(on_turn, on_error))

    async def stop(self) -> None:
        """Остановить цикл диалога.

        Отменяет задачу диалога если она активна.
        """
        if self._dialogue_task and not self._dialogue_task.done():
            self._dialogue_task.cancel()
            try:
                await self._dialogue_task
            except asyncio.CancelledError:
                pass
            finally:
                self._dialogue_task = None

    async def _run_loop(
        self,
        on_turn: Callable[[DialogueTurnResult], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        """Основной цикл диалога.

        Args:
            on_turn: Callback для обработки каждого хода.
            on_error: Callback для обработки ошибок генерации.

        """
        try:
            while self._service.is_running and not self._service.is_paused:
                if self._is_task_cancelled():
                    break

                try:
                    result = await self._process_turn()
                    if result and on_turn:
                        on_turn(result)
                except ProviderError as e:
                    log.warning("Ошибка провайдера в цикле диалога: %s", e)
                    if on_error:
                        model_name = self._service.conversation.get_current_model_name()
                        on_error(model_name)

                await asyncio.sleep(self._config.pause_between_messages)

        except asyncio.CancelledError:
            log.debug("Диалог отменён")
            raise
        except ProviderError:
            log.debug("ProviderError обработан в цикле диалога")
        except (RuntimeError, SystemError, OSError):
            log.exception("Critical error in dialogue loop")
        finally:
            self._service.stop()

    async def _process_turn(self) -> DialogueTurnResult | None:
        """Обработать один ход диалога.

        Returns:
            DialogueTurnResult с результатом хода.

        """
        return await self._service.run_dialogue_cycle()

    def _is_task_cancelled(self) -> bool:
        """Проверить отменена ли текущая задача."""
        current_task = asyncio.current_task()
        return current_task is not None and current_task.cancelled()

    async def cleanup(self) -> None:
        """Очистить ресурсы раннера."""
        await self.stop()
