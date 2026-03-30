"""Логика диалога и хранение контекстов для двух моделей.

Этот модуль содержит доменную логику диалога.
Зависит только от абстракций (протоколов), не от конкретных реализаций.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from models.config import Config
from models.provider import MessageDict, ModelProvider

log = logging.getLogger(__name__)

# Импортируем для обратной совместимости
__all__ = ["Conversation", "MessageDict", "MAX_CONTEXT_LENGTH", "ModelId"]

# Константа для ограничения длины контекста
MAX_CONTEXT_LENGTH: int = 50


ModelId = Literal["A", "B"]


@dataclass(slots=True)
class Conversation:
    """
    Управление диалогом между двумя моделями.

    Каждая модель имеет свой независимый контекст (историю сообщений).
    Ответ одной модели добавляется в контекст другой как сообщение от пользователя.

    Attributes:
        model_a: Название модели A.
        model_b: Название модели B.
        topic: Тема диалога.
        system_prompt: Системный промпт для диалога.

    Note:
        Имеет 8 атрибутов что превышает стандартный лимит (7),
        но это оправдано сложностью предметной области.
    """

    # pylint: disable=too-many-instance-attributes
    model_a: str  # Название модели A
    model_b: str  # Название второй модели
    topic: str  # Тема диалога

    # Контексты для каждой модели (списки сообщений в формате Ollama)
    _context_a: list[MessageDict] = field(default_factory=list, repr=False)
    _context_b: list[MessageDict] = field(default_factory=list, repr=False)

    # Системный промпт по умолчанию из Config
    system_prompt: str = field(default_factory=lambda: Config().default_system_prompt)

    # Чей сейчас ход
    _current_turn: ModelId = field(default="A", init=False)

    # Флаг для предотвращения повторной инициализации
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Инициализация системного промпта после создания объекта."""
        if self._initialized:
            return
        self._initialized = True

        # Валидация обязательных параметров
        if not self.model_a or not isinstance(self.model_a, str):
            raise ValueError("model_a должен быть непустой строкой")
        if not self.model_b or not isinstance(self.model_b, str):
            raise ValueError("model_b должен быть непустой строкой")
        if not self.topic or not isinstance(self.topic, str):
            raise ValueError("topic должен быть непустой строкой")
        if self.model_a == self.model_b:
            raise ValueError("model_a и model_b должны быть разными")

        # Форматируем системный промпт с темой
        try:
            formatted_prompt = self.system_prompt.format(topic=self.topic)
        except (KeyError, ValueError):
            formatted_prompt = (
                f"You are a helpful assistant. The topic of discussion is: {self.topic}"
            )
        # Добавляем системный промпт в оба контекста
        self._context_a.append(MessageDict(role="system", content=formatted_prompt))
        self._context_b.append(MessageDict(role="system", content=formatted_prompt))

    def _trim_context_if_needed(
        self, context: list[MessageDict], max_len: int = MAX_CONTEXT_LENGTH
    ) -> list[MessageDict]:
        """
        Обрезать контекст если он превышает max_len.

        Сохраняет системный промпт (первое сообщение) и последние сообщения.
        Удаляет старые сообщения из середины контекста.

        Args:
            context: Контекст для проверки и возможной обрезки.
            max_len: Максимальная длина контекста после обрезки.

        Returns:
            Обрезанный контекст если было превышение, иначе исходный.
        """
        if len(context) <= max_len:
            return context

        system_message = context[0] if context else None

        remaining_messages = context[-max_len:]

        if system_message:
            trimmed = [system_message] + remaining_messages
        else:
            trimmed = remaining_messages

        log.warning(
            "Контекст превышен (%d сообщений), обрезано до %d",
            len(context),
            len(trimmed),
        )

        return trimmed

    def _add_message_to_context(
        self,
        model_id: ModelId,
        role: str,
        content: str,
    ) -> None:
        """Добавить сообщение в контекст модели."""
        # Прямой доступ к контексту без избыточного создания словаря
        context = self._context_a if model_id == "A" else self._context_b

        if len(context) >= MAX_CONTEXT_LENGTH:
            context = self._trim_context_if_needed(context, MAX_CONTEXT_LENGTH - 2)
            # Обновляем ссылку на обрезанный контекст
            if model_id == "A":
                self._context_a = context
            else:
                self._context_b = context

        context.append(MessageDict(role=role, content=content))

    def add_message(
        self,
        model_id: ModelId,
        role: Literal["system", "user", "assistant"],
        content: str,
    ) -> None:
        """
        Добавить сообщение в контекст указанной модели.

        Args:
            model_id: Идентификатор модели (A или B).
            role: Роль сообщения ("user", "assistant", "system").
            content: Текст сообщения.
        """
        self._add_message_to_context(model_id, role, content)
        context = self._context_a if model_id == "A" else self._context_b

        log.debug(
            "Added %s message to model %s context (total: %d)",
            role,
            model_id,
            len(context),
        )

    def get_context(self, model_id: ModelId) -> tuple[MessageDict, ...]:
        """
        Получить историю сообщений для указанной модели.

        Args:
            model_id: Идентификатор модели (A или B).

        Returns:
            Кортеж сообщений в формате Ollama (неизменяемый).
        """
        context = self._context_a if model_id == "A" else self._context_b
        # Возвращаем tuple для безопасности и производительности
        return tuple(context)

    def switch_turn(self) -> None:
        """
        Переключить ход на другую модель.

        Команда (command) - изменяет состояние, ничего не возвращает.
        Для получения текущего хода используйте свойство current_turn.
        """
        previous_turn = self._current_turn
        self._current_turn = "B" if self._current_turn == "A" else "A"
        log.debug(
            "Turn switched: model %s -> model %s",
            previous_turn,
            self._current_turn,
        )

    @property
    def current_turn(self) -> ModelId:
        """
        Получить идентификатор модели, которой сейчас ходить.

        Returns:
            Идентификатор текущей модели (A или B).
        """
        return self._current_turn

    def get_current_model_name(self) -> str:
        """Получить название текущей модели."""
        return self.model_a if self._current_turn == "A" else self.model_b

    def get_other_model_name(self) -> str:
        """Получить название другой модели."""
        return self.model_b if self._current_turn == "A" else self.model_a

    async def generate_response(
        self,
        provider: ModelProvider,
    ) -> tuple[ModelId, str]:
        """
        Сгенерировать ответ для текущей модели.

        Args:
            provider: Провайдер моделей для генерации (ModelProvider).

        Returns:
            Кортеж (идентификатор модели, сгенерированный ответ).
        """
        model_id = self.current_turn
        model_name = self.get_current_model_name()
        context = list(self.get_context(model_id))

        response = await provider.generate(
            model=model_name,
            messages=context,
        )

        return model_id, response

    async def process_turn(
        self,
        provider: ModelProvider,
    ) -> tuple[str, str, str]:
        """
        Обработать один ход диалога.

        Генерирует ответ текущей модели, добавляет его в оба контекста
        (как assistant для текущей модели и как user для другой),
        затем переключает ход.

        Args:
            provider: Провайдер моделей для генерации (ModelProvider).

        Returns:
            Кортеж (название модели, роль "assistant", текст ответа).
        """
        model_id = self.current_turn
        model_name = self.get_current_model_name()
        other_id: ModelId = "B" if model_id == "A" else "A"

        # Сохраняем состояние контекстов для rollback при ошибке
        context_a_snapshot = list(self._context_a)
        context_b_snapshot = list(self._context_b)
        turn_snapshot = self._current_turn

        try:
            # Генерируем ответ ДО любых изменений контекста
            _, response = await self.generate_response(provider)

            # Добавляем ответ в контекст текущей модели как assistant
            self.add_message(model_id, "assistant", response)

            # Добавляем ответ в контекст другой модели как user
            self.add_message(other_id, "user", response)

            # Переключаем ход
            self.switch_turn()

            return model_name, "assistant", response

        except Exception:
            # Rollback состояния контекстов при ошибке
            self._context_a = context_a_snapshot
            self._context_b = context_b_snapshot
            self._current_turn = turn_snapshot
            raise

    def clear_contexts(self) -> None:
        """
        Очистить оба контекста, сохранив только системный промпт и тему.

        Использует присваивание новых списков для простоты и читаемости.
        """
        # Форматируем системный промпт с темой
        try:
            formatted_prompt = self.system_prompt.format(topic=self.topic)
        except (KeyError, ValueError):
            formatted_prompt = (
                f"You are a helpful assistant. The topic of discussion is: {self.topic}"
            )
        # Присваиваем новые списки с отдельными копиями system_message
        self._context_a = [MessageDict(role="system", content=formatted_prompt)]
        self._context_b = [MessageDict(role="system", content=formatted_prompt)]

        # Сбрасываем ход на A
        self._current_turn = "A"

    def get_context_stats(self) -> dict[str, int]:
        """
        Получить статистику контекстов.

        Returns:
            Словарь с количеством сообщений в каждом контексте.
        """
        return {
            "model_a_messages": len(self._context_a),
            "model_b_messages": len(self._context_b),
        }
