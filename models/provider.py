"""Абстракции для провайдеров языковых моделей.

Этот модуль определяет протоколы и типы для dependency injection.
Позволяет заменять реализацию провайдера без изменения доменной логики.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, TypedDict, runtime_checkable


class MessageDict(TypedDict):
    """
    Структура сообщения в формате совместимом с Ollama.

    Attributes:
        role: Роль отправителя (system, user, assistant).
        content: Текст сообщения.
    """

    role: Literal["system", "user", "assistant"]
    content: str


ModelId = Literal["A", "B"]


@runtime_checkable
class ModelProvider(Protocol):
    """
    Протокол для провайдеров языковых моделей.

    Определяет интерфейс для взаимодействия с различными LLM-провайдерами.
    Позволяет использовать dependency injection для тестируемости и заменяемости.

    Example:
        >>> class MyProvider:
        ...     async def list_models(self) -> list[str]:
        ...         return ["model1", "model2"]
        ...     async def generate(self, model: str, messages: list[MessageDict]) -> str:
        ...         return "response"
        ...     async def close(self) -> None:
        ...         pass
        >>> provider: ModelProvider = MyProvider()  # Типизация работает
    """

    async def list_models(self) -> list[str]:
        """
        Получить список доступных моделей.

        Returns:
            Список названий доступных моделей.

        Raises:
            Exception: Если не удалось получить список моделей.
        """

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: Any,
    ) -> str:
        """
        Сгенерировать ответ от модели.

        Args:
            model: Название модели для генерации.
            messages: Список сообщений в формате MessageDict.
            **kwargs: Дополнительные параметры генерации.

        Returns:
            Сгенерированный текст ответа.

        Raises:
            Exception: Если не удалось сгенерировать ответ.
        """

    async def close(self) -> None:
        """
        Освободить ресурсы провайдера.

        Закрывает соединения, очищает кэши и т.д.
        Вызывается при завершении работы приложения.

        Note:
            Метод должен быть идемпотентным (безопасным для повторного вызова).
        """
