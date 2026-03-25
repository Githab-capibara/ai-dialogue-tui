"""Сервисный слой для управления бизнес-логикой диалога.

Этот модуль содержит сервис для управления диалогом между моделями.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from models.config import Config
from models.conversation import Conversation, ModelId
from models.provider import ModelProvider, ProviderError

log = logging.getLogger(__name__)


@dataclass
class DialogueTurnResult:
    """
    Результат одного хода диалога.

    Attributes:
        model_name: Название модели которая сделала ход.
        model_id: Идентификатор модели (A или B).
        role: Роль сообщения (всегда "assistant").
        response: Сгенерированный текст ответа.
    """

    model_name: str
    model_id: ModelId
    role: str
    response: str


class DialogueService:
    """
    Сервис для управления бизнес-логикой диалога.

    Инкапсулирует логику запуска, паузы, остановки и выполнения циклов диалога.
    Работает с абстракциями (ModelProvider, Conversation), не с конкретными реализациями.

    Attributes:
        conversation: Объект диалога для управления контекстами.
        provider: Провайдер моделей для генерации ответов.
        config: Конфигурация приложения.

    Note:
        Этот класс содержит бизнес-логику и не зависит от UI.
    """

    def __init__(
        self,
        conversation: Conversation,
        provider: ModelProvider,
        config: Config | None = None,
    ) -> None:
        """
        Инициализация сервиса диалога.

        Args:
            conversation: Объект диалога для управления контекстами.
            provider: Провайдер моделей для генерации ответов.
            config: Конфигурация для параметров (паузы, таймауты).
        """
        self._conversation = conversation
        self._provider = provider
        self._config = config or Config()
        self._is_running = False
        self._is_paused = False
        self._turn_count = 0

    @property
    def conversation(self) -> Conversation:
        """Получить объект диалога."""
        return self._conversation

    @property
    def provider(self) -> ModelProvider:
        """Получить провайдер моделей."""
        return self._provider

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
        """Получить количество сделанных ходов."""
        return self._turn_count

    def start(self) -> None:
        """
        Запустить диалог.

        Устанавливает флаг _is_running в True и сбрасывает паузу.
        """
        self._is_running = True
        self._is_paused = False

    def pause(self) -> None:
        """
        Поставить диалог на паузу.

        Устанавливает флаг _is_paused в True.
        Диалог остается запущенным (is_running=True).
        """
        self._is_paused = True

    def resume(self) -> None:
        """
        Возобновить диалог после паузы.

        Сбрасывает флаг _is_paused в False.
        """
        self._is_paused = False

    def stop(self) -> None:
        """
        Остановить диалог.

        Сбрасывает флаги _is_running и _is_paused.
        """
        self._is_running = False
        self._is_paused = False

    def clear_history(self) -> None:
        """
        Очистить историю диалога.

        Очищает контексты обеих моделей и сбрасывает счетчик ходов.
        """
        self._conversation.clear_contexts()
        self._turn_count = 0

    async def run_dialogue_cycle(self) -> DialogueTurnResult | None:
        """
        Выполнить один цикл диалога.

        Генерирует ответ текущей модели, обновляет контексты,
        переключает ход и increment счетчик.

        Returns:
            DialogueTurnResult с результатом хода или None если диалог не запущен.
        """
        if not self._is_running or self._is_paused:
            return None

        model_id = self._conversation.current_turn
        model_name = self._conversation.get_current_model_name()

        try:
            _, _, response = await self._conversation.process_turn(self._provider)
            self._turn_count += 1

            result = DialogueTurnResult(
                model_name=model_name,
                model_id=model_id,
                role="assistant",
                response=response,
            )

            return result

        except ProviderError:
            log.warning("Ошибка провайдера при выполнении цикла диалога")
            raise

    async def cleanup(self) -> None:
        """
        Очистить ресурсы сервиса.

        Закрывает соединение с провайдером моделей.
        """
        await self._provider.close()

    def get_model_info_and_style(self) -> tuple[str, str]:
        """
        Получить информацию о текущей модели и стиль для отображения.

        Returns:
            Кортеж (название модели, стиль для отображения).
            Стиль определяется по идентификатору модели (A или B).
        """
        model_name = self._conversation.get_current_model_name()
        model_id = self._conversation.current_turn
        # Стиль определяется по модели - для A один, для B другой
        style = "model_a" if model_id == "A" else "model_b"
        return model_name, style
