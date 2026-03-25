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
__all__ = ["Conversation", "MessageDict", "MAX_CONTEXT_LENGTH"]

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

    Note:
        Имеет 8 атрибутов что превышает стандартный лимит (7),
        но это оправдано сложностью предметной области.
    """

    # pylint: disable=too-many-instance-attributes
    model_a: str  # Название модели A
    model_b: str  # Название второй модели
    topic: str  # Тема диалога

    # Конфигурация для dependency injection
    _config: Config = field(default_factory=Config, repr=False)

    # Контексты для каждой модели (списки сообщений в формате Ollama)
    _context_a: list[MessageDict] = field(default_factory=list, repr=False)
    _context_b: list[MessageDict] = field(default_factory=list, repr=False)

    # Чей сейчас ход
    _current_turn: ModelId = field(default="A", init=False)

    # Системный промпт
    _system_prompt: str = field(init=False, repr=False)

    # Флаг для предотвращения повторной инициализации
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        """Инициализация системного промпта после создания объекта."""
        if self._initialized:
            return
        self._initialized = True

        try:
            self._system_prompt = self._config.default_system_prompt.format(
                topic=self.topic
            )
        except (KeyError, ValueError):
            self._system_prompt = (
                f"You are a helpful assistant. The topic of discussion is: {self.topic}"
            )
        # Добавляем системный промпт в оба контекста
        self._context_a.append(MessageDict(role="system", content=self._system_prompt))
        self._context_b.append(MessageDict(role="system", content=self._system_prompt))

    def _trim_context_if_needed(self, context: list[MessageDict]) -> list[MessageDict]:
        """
        Обрезать контекст если он превышает MAX_CONTEXT_LENGTH.

        Сохраняет системный промпт (первое сообщение) и последние сообщения.
        Удаляет старые сообщения из середины контекста.

        Args:
            context: Контекст для проверки и возможной обрезки.

        Returns:
            Обрезанный контекст если было превышение, иначе исходный.
        """
        if len(context) <= MAX_CONTEXT_LENGTH:
            return context

        # Сохраняем системный промпт (первое сообщение)
        system_message = context[0] if context else None

        # Берем последние MAX_CONTEXT_LENGTH - 1 сообщений
        remaining_messages = (
            context[-(MAX_CONTEXT_LENGTH - 1) :] if len(context) > 1 else []
        )

        # Восстанавливаем контекст с системным промптом
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
        context = self._context_a if model_id == "A" else self._context_b
        context.append(MessageDict(role=role, content=content))

        # Проверяем и обрезаем контекст если нужно
        if len(context) > MAX_CONTEXT_LENGTH:
            if model_id == "A":
                self._context_a = self._trim_context_if_needed(context)
            else:
                self._context_b = self._trim_context_if_needed(context)

        log.debug(
            "Added %s message to model %s context (total: %d)",
            role,
            model_id,
            len(context),
        )

    def get_context(self, model_id: ModelId) -> list[MessageDict]:
        """
        Получить историю сообщений для указанной модели.

        Args:
            model_id: Идентификатор модели (A или B).

        Returns:
            Список сообщений в формате Ollama.
        """
        context = self._context_a if model_id == "A" else self._context_b
        # Возвращаем копию для безопасности (чтобы не позволять внешнему коду
        # изменять внутреннее состояние)
        return context.copy()

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
        context = self.get_context(model_id)

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

        # Генерируем ответ ДО любых изменений контекста
        _, response = await self.generate_response(provider)

        # Добавляем ответ в контекст текущей модели как assistant
        self.add_message(model_id, "assistant", response)

        # Добавляем ответ в контекст другой модели как user
        self.add_message(other_id, "user", response)

        # Переключаем ход
        self.switch_turn()

        return model_name, "assistant", response

    def clear_contexts(self) -> None:
        """
        Очистить оба контекста, сохранив только системный промпт и тему.

        Использует присваивание новых списков для простоты и читаемости.
        """
        # Создаём новый системный промпт
        system_message = MessageDict(role="system", content=self._system_prompt)

        # Присваиваем новые списки (проще и понятнее чем .clear())
        self._context_a = [system_message]
        self._context_b = [system_message]

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
