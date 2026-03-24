"""Модуль управления диалогом между ИИ-моделями.

Этот модуль предоставляет класс Conversation для управления диалогом
между двумя моделями с независимыми контекстами.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from models.ollama_client import MessageDict, OllamaClient


class MessageDict(TypedDict):
    """Тип для словаря сообщения.

    Attributes:
        role: Роль отправителя (user, assistant, system).
        content: Содержание сообщения.
    """

    role: Literal["user", "assistant", "system"]
    content: str


@dataclass
class Conversation:
    """Управление диалогом между двумя моделями.

    Attributes:
        model_a_name: Название первой модели.
        model_b_name: Название второй модели.
        topic: Тема диалога.

    Note:
        Каждая модель имеет независимый контекст (историю сообщений).
        Реализует атомарные операции для предотвращения рассинхронизации.
    """

    model_a_name: str
    model_b_name: str
    topic: str
    _context_a: list[MessageDict] = field(default_factory=list)
    _context_b: list[MessageDict] = field(default_factory=list)
    _current_turn: Literal["A", "B"] = "A"

    def __post_init__(self) -> None:
        """Инициализировать контексты системными промптами."""
        system_message: MessageDict = {
            "role": "system",
            "content": f"Тема диалога: {self.topic}",
        }
        self._context_a.append(system_message)
        self._context_b.append(system_message)

    @property
    def current_turn(self) -> Literal["A", "B"]:
        """
        Получить текущий ход.

        Returns:
            'A' если ход первой модели, 'B' если второй.
        """
        return self._current_turn

    def switch_turn(self) -> None:
        """
        Переключить ход между моделями.

        Note:
            Метод не возвращает значение (Command-Query Separation).
        """
        self._current_turn = "B" if self._current_turn == "A" else "A"

    def get_context(self, for_model: Literal["A", "B"]) -> list[MessageDict]:
        """
        Получить контекст для указанной модели.

        Args:
            for_model: Модель для которой получить контекст ('A' или 'B').

        Returns:
            Копия списка сообщений контекста.
        """
        context = self._context_a if for_model == "A" else self._context_b
        return context.copy()

    def add_message(
        self,
        for_model: Literal["A", "B"],
        role: Literal["user", "assistant", "system"],
        content: str,
    ) -> None:
        """
        Добавить сообщение в контекст модели.

        Args:
            for_model: Модель в чей контекст добавить сообщение.
            role: Роль отправителя.
            content: Содержание сообщения.
        """
        message: MessageDict = {"role": role, "content": content}
        if for_model == "A":
            self._context_a.append(message)
        else:
            self._context_b.append(message)

    async def process_turn(self, client: OllamaClient) -> str:
        """
        Обработать текущий ход диалога.

        Args:
            client: Клиент Ollama для генерации ответа.

        Returns:
            Сгенерированный ответ модели.

        Raises:
            RuntimeError: Если произошла ошибка при генерации ответа.

        Note:
            Операция атомарна: при ошибке все изменения откатываются.
        """
        current_model = self.model_a_name if self._current_turn == "A" else self.model_b_name
        context = self.get_context(self._current_turn)

        # Сохраняем состояние для отката
        old_context_a_len = len(self._context_a)
        old_context_b_len = len(self._context_b)
        old_turn = self._current_turn

        try:
            # Генерируем ответ
            response = await client.generate(model=current_model, messages=context)

            # Добавляем в контекст текущей модели как assistant
            self.add_message(self._current_turn, "assistant", response)

            # Добавляем в контекст другой модели как user
            other_model = "B" if self._current_turn == "A" else "A"
            self.add_message(other_model, "user", response)

            # Переключаем ход
            self.switch_turn()

            return response
        except Exception as e:
            # Откат изменений при ошибке
            while len(self._context_a) > old_context_a_len:
                self._context_a.pop()
            while len(self._context_b) > old_context_b_len:
                self._context_b.pop()
            self._current_turn = old_turn
            raise RuntimeError(f"Ошибка обработки хода: {e}") from e

    def clear_contexts(self) -> None:
        """
        Очистить оба контекста и добавить системные промпты.

        Note:
            Использует .clear() для оптимального использования памяти.
        """
        self._context_a.clear()
        self._context_b.clear()
        self.__post_init__()
