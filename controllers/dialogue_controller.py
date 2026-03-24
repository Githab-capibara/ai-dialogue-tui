"""Контроллеры для управления состоянием UI.

Этот модуль содержит контроллеры для обработки пользовательских команд
и управления состоянием UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from services.dialogue_service import DialogueService


@dataclass
class UIState:
    """
    Состояние UI для отображения.

    Attributes:
        status_text: Текст статуса.
        is_dialogue_running: Запущен ли диалог.
        is_paused: На паузе ли диалог.
        turn_count: Количество ходов.
    """

    status_text: str = "Ожидание..."
    is_dialogue_running: bool = False
    is_paused: bool = True
    turn_count: int = 0


@runtime_checkable
class UIUpdater(Protocol):
    """
    Протокол для обновления UI.

    Позволяет внедрять UI-логику через dependency injection.
    """

    def update_status(self, status: str) -> None:
        """Обновить статус."""
        ...

    def refresh(self) -> None:
        """Обновить UI."""
        ...


class DialogueController:
    """
    Контроллер для управления диалогом через UI.

    Обрабатывает пользовательские команды и обновляет состояние UI.
    Зависимости внедряются через конструктор.

    Attributes:
        service: Сервис диалога.

    Example:
        >>> service = DialogueService(...)
        >>> controller = DialogueController(service)
        >>> await controller.handle_start()
    """

    def __init__(self, service: DialogueService) -> None:
        """
        Инициализировать контроллер.

        Args:
            service: Сервис диалога.
        """
        self._service = service
        self._state = UIState()

    @property
    def state(self) -> UIState:
        """Получить текущее состояние UI."""
        return self._state

    def _update_state(self) -> None:
        """Обновить внутреннее состояние из сервиса."""
        self._state.is_dialogue_running = self._service.is_running
        self._state.is_paused = self._service.is_paused
        self._state.turn_count = self._service.turn_count

    async def handle_start(self) -> None:
        """Обработать команду старта."""
        self._service.start()
        self._update_state()
        self._state.status_text = "Диалог запущен"

    async def handle_pause(self) -> None:
        """Обработать команду паузы."""
        if self._service.is_running:
            self._service.pause()
            self._update_state()
            self._state.status_text = "Пауза"

    async def handle_resume(self) -> None:
        """Обработать команду продолжения."""
        if self._service.is_running:
            self._service.resume()
            self._update_state()
            self._state.status_text = "Диалог продолжается"

    async def handle_clear(self) -> None:
        """Обработать команду очистки."""
        self._service.clear_history()
        self._update_state()
        self._state.status_text = "История очищена"

    async def handle_stop(self) -> None:
        """Обработать команду остановки."""
        self._service.stop()
        self._update_state()
        self._state.status_text = "Диалог остановлен"
