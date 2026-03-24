"""Сервисный слой для управления диалогом ИИ-моделей.

Этот модуль содержит бизнес-логику диалога, независимую от UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from models.conversation import Conversation
from models.provider import ModelProvider


@dataclass
class DialogueTurnResult:
    """Результат хода диалога.

    Attributes:
        model_name: Название модели сделавшей ход.
        response: Ответ модели.
        turn_count: Номер текущего хода.
    """

    model_name: str
    response: str
    turn_count: int


@runtime_checkable
class DialogueUICallback(Protocol):
    """
    Протокол для UI-коллбеков DialogueService.

    Позволяет внедрять UI-логику через dependency injection.
    """

    async def on_turn_complete(self, result: DialogueTurnResult) -> None:
        """Вызывается после завершения хода."""
        ...

    async def on_error(self, error: Exception) -> None:
        """Вызывается при ошибке."""
        ...

    async def on_status_change(self, status: str) -> None:
        """Вызывается при изменении статуса."""
        ...


class DialogueService:
    """
    Сервис для управления диалогом между ИИ-моделями.

    Содержит бизнес-логику диалога, независимую от UI.
    Зависимости внедряются через конструктор.

    Attributes:
        provider: Провайдер моделей (реализация ModelProvider).
        conversation: Объект диалога.

    Example:
        >>> provider = OllamaProvider()
        >>> conversation = Conversation(...)
        >>> service = DialogueService(provider, conversation)
        >>> await service.start()
    """

    def __init__(
        self,
        provider: ModelProvider,
        conversation: Conversation,
    ) -> None:
        """
        Инициализировать сервис диалога.

        Args:
            provider: Провайдер моделей.
            conversation: Объект диалога.
        """
        self._provider = provider
        self._conversation = conversation
        self._is_running = False
        self._is_paused = True
        self._turn_count = 0

    def start(self) -> None:
        """Запустить диалог."""
        self._is_running = True
        self._is_paused = False

    def pause(self) -> None:
        """Поставить диалог на паузу."""
        self._is_paused = True

    def resume(self) -> None:
        """Продолжить диалог после паузы."""
        self._is_paused = False

    def stop(self) -> None:
        """Остановить диалог."""
        self._is_running = False
        self._is_paused = True

    def clear_history(self) -> None:
        """Очистить историю диалога."""
        self._conversation.clear_contexts()
        self._turn_count = 0

    @property
    def is_running(self) -> bool:
        """Проверить запущен ли диалог."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Проверить находится ли диалог на паузе."""
        return self._is_paused

    @property
    def turn_count(self) -> int:
        """Получить количество ходов."""
        return self._turn_count

    async def run_dialogue_cycle(
        self, ui_callback: DialogueUICallback | None = None
    ) -> DialogueTurnResult | None:
        """
        Выполнить один цикл диалога.

        Args:
            ui_callback: Опциональный коллбек для UI-операций.

        Returns:
            Результат хода или None если диалог на паузе.
        """
        if self._is_paused or not self._is_running:
            return None

        try:
            model_name = self._conversation.get_current_model_name()
            model_id, response = await self._conversation.generate_response(
                self._provider
            )

            self._turn_count += 1

            result = DialogueTurnResult(
                model_name=model_name,
                response=response,
                turn_count=self._turn_count,
            )

            if ui_callback:
                await ui_callback.on_turn_complete(result)

            return result

        except Exception as e:
            if ui_callback:
                await ui_callback.on_error(e)
            raise
