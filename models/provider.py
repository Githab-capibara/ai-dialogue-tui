"""Абстракции для провайдеров языковых моделей.

Этот модуль определяет протоколы и типы для dependency injection.
Позволяет заменять реализацию провайдера без изменения доменной логики.
"""

from __future__ import annotations

from typing import Any, Literal, Protocol, TypedDict, runtime_checkable


class ProviderError(Exception):
    """Базовое исключение для ошибок провайдера моделей.

    Используется как базовый класс для специфичных исключений провайдера.
    Содержит информацию об оригинальном исключении для отладки.
    """

    __slots__ = ("_original_exception",)

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
    ) -> None:
        """Инициализация исключения.

        Args:
            message: Сообщение об ошибке.
            original_exception: Оригинальное исключение для цепочки.

        """
        super().__init__(message)
        self._original_exception = original_exception

    @property
    def original_exception(self) -> Exception | None:
        """Получить оригинальное исключение."""
        return self._original_exception


class ProviderConfigurationError(ProviderError):
    """Исключение для ошибок конфигурации провайдера.

    Возникает при некорректной конфигурации провайдера:
    - Некорректный URL хоста
    - Неверные параметры аутентификации
    - Отсутствующие обязательные настройки
    """

    __slots__ = ()


class ProviderConnectionError(ProviderError):
    """Исключение для ошибок подключения к провайдеру.

    Возникает при проблемах с сетевым подключением:
    - Недоступность хоста
    - Таймауты соединения
    - Ошибки сети
    """

    __slots__ = ()


class ProviderGenerationError(ProviderError):
    """Исключение для ошибок генерации ответа.

    Возникает при проблемах с генерацией ответа моделью:
    - Ошибки API провайдера
    - Некорректный формат ответа
    - Ошибки валидации ответа
    """

    __slots__ = ()


class MessageDict(TypedDict, total=True):
    """Структура сообщения в формате совместимом с Ollama.

    Attributes:
        role: Роль отправителя (system, user, assistant).
        content: Текст сообщения.

    """

    role: Literal["system", "user", "assistant"]
    content: str


ModelId = Literal["A", "B"]


@runtime_checkable
class ModelProvider(Protocol):
    """Протокол для провайдеров языковых моделей.

    Определяет интерфейс для взаимодействия с различными LLM-провайдерами.
    Позволяет использовать dependency injection для тестируемости и заменяемости.
    """

    async def list_models(self) -> list[str]:
        """Получить список доступных моделей."""
        ...  # pragma: no cover

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: Any,
    ) -> str:
        """Сгенерировать ответ от модели."""
        ...  # pragma: no cover

    async def close(self) -> None:
        """Освободить ресурсы провайдера."""
        ...  # pragma: no cover
        ...  # pragma: no cover
