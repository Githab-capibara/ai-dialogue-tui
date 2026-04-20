"""Контроллеры для управления состоянием UI приложения AI Dialogue TUI.

Этот модуль содержит контроллеры для связи бизнес-логики с UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.dialogue_service import DialogueService


@dataclass(slots=True)
class UIState:
    """Состояние UI для отображения.

    Attributes:
        status_text: Текст для отображения в статус-баре.
        status_style: Стиль для статус-бара (green, yellow, red, etc.).
        turn_count: Количество сделанных ходов.
        current_model: Название текущей модели (если известна).
        is_dialogue_active: Активен ли диалог в данный момент.

    """

    status_text: str = "Ожидание..."
    status_style: str = "dim"
    turn_count: int = 0
    current_model: str | None = None
    is_dialogue_active: bool = False


class DialogueController:
    """Контроллер для управления состоянием UI на основе сервиса диалога.

    Связывает бизнес-логику (DialogueService) с UI-компонентами.
    Обрабатывает команды от пользователя и обновляет состояние UI.

    Attributes:
        service: Сервис диалога для управления бизнес-логикой.
        on_state_changed: Callback для уведомления об изменении состояния UI.

    """

    def __init__(
        self,
        service: DialogueService,
        on_state_changed: Callable[[UIState], None] | None = None,
    ) -> None:
        """Инициализация контроллера.

        Args:
            service: Сервис диалога для управления.
            on_state_changed: Callback вызываемый при изменении состояния UI.

        """
        self._service = service
        self._on_state_changed = on_state_changed
        self._state = UIState()

    @property
    def state(self) -> UIState:
        """Получить текущее состояние UI.

        Returns:
            Текущее состояние UI.

        """
        # Возвращаем копию для безопасности через конструктор
        return UIState(
            status_text=self._state.status_text,
            status_style=self._state.status_style,
            turn_count=self._state.turn_count,
            current_model=self._state.current_model,
            is_dialogue_active=self._state.is_dialogue_active,
        )

    @property
    def service(self) -> DialogueService:
        """Получить сервис диалога.

        Returns:
            Сервис диалога.

        """
        return self._service

    def _notify_state_changed(self) -> None:
        """Уведомить об изменении состояния UI через callback."""
        if self._on_state_changed:
            self._on_state_changed(self._state)

    def _update_status(
        self,
        text: str,
        style: str,
    ) -> None:
        """Обновить статус и уведомить об изменении.

        Args:
            text: Новый текст статуса.
            style: Стиль для отображения.

        """
        self._state.status_text = text
        self._state.status_style = style
        self._notify_state_changed()

    def handle_start(self) -> bool:
        """Обработать команду запуска диалога.

        Returns:
            True если диалог успешно запущен, False если есть ошибки.

        """
        if self._service.is_running and not self._service.is_paused:
            self._update_status("Диалог уже запущен", "yellow")
            return False

        self._service.start()
        self._state.is_dialogue_active = True
        self._update_status("Диалог идёт...", "green")
        return True

    def handle_pause(self) -> bool:
        """Обработать команду паузы/продолжения.

        Returns:
            True если команда выполнена, False если диалог не настроен.

        """
        if not self._service.is_running:
            self._update_status("Диалог не запущен", "red")
            return False

        if self._service.is_paused:
            self._service.resume()
            self._update_status("Диалог идёт...", "green")
        else:
            self._service.pause()
            self._update_status("На паузе", "yellow")

        return True

    def handle_clear(self) -> None:
        """Обработать команду очистки истории.

        Очищает контексты диалога и сбрасывает счетчик ходов.
        """
        self._service.clear_history()
        self._state.turn_count = 0
        self._update_status("История очищена", "dim")

    def handle_stop(self) -> None:
        """Обработать команду остановки диалога.

        Устанавливает флаги is_running и is_paused в False.
        """
        self._service.stop()
        self._state.is_dialogue_active = False
        self._update_status("Остановлен", "dim")

    def update_for_turn(
        self,
        model_name: str,
        style: str,
    ) -> None:
        """Обновить состояние для нового хода диалога.

        Args:
            model_name: Название модели которая делает ход.
            style: Стиль для отображения (STYLE_MODEL_A или STYLE_MODEL_B).

        """
        self._state.current_model = model_name
        self._state.turn_count = self._service.turn_count
        self._update_status(f"Ход: {model_name}", style)

    def update_for_error(self, model_name: str) -> None:
        """Обновить состояние при ошибке.

        Args:
            model_name: Название модели где произошла ошибка.

        """
        self._update_status(f"Ошибка: {model_name}", "red")

    async def cleanup(self) -> None:
        """Очистить ресурсы контроллера и сервиса.

        Вызывает cleanup сервиса диалога для освобождения ресурсов.
        """
        await self._service.cleanup()


__all__ = ["DialogueController", "UIState"]
