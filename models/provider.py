"""Протоколы и абстракции для работы с LLM-провайдерами.

Этот модуль определяет абстрактный интерфейс для взаимодействия
с различными провайдерами языковых моделей.
"""

from __future__ import annotations

from typing import Literal, Protocol, TypedDict, runtime_checkable


class MessageDict(TypedDict):
    """Тип для словаря сообщения.

    Attributes:
        role: Роль отправителя (user, assistant, system).
        content: Содержание сообщения.
    """

    role: Literal["user", "assistant", "system"]
    content: str


ModelId = Literal["A", "B"]


@runtime_checkable
class ModelProvider(Protocol):
    """
    Протокол для провайдеров языковых моделей.

    Этот протокол определяет интерфейс для взаимодействия с различными
    LLM-провайдерами (Ollama, OpenAI, Anthropic и т.д.).

    Example:
        >>> class OllamaProvider:
        ...     async def list_models(self) -> list[str]: ...
        ...     async def generate(self, model: str, messages: list[MessageDict]) -> str: ...
        ...     async def close(self) -> None: ...
        >>> assert isinstance(OllamaProvider(), ModelProvider)
    """

    async def list_models(self) -> list[str]:
        """
        Получить список доступных моделей.

        Returns:
            Список названий моделей.
        """
        ...

    async def generate(
        self, model: str, messages: list[MessageDict]
    ) -> str:
        """
        Сгенерировать ответ модели.

        Args:
            model: Название модели.
            messages: Список сообщений для контекста.

        Returns:
            Сгенерированный ответ.
        """
        ...

    async def close(self) -> None:
        """Закрыть соединение с провайдером."""
        ...
