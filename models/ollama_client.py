"""Асинхронный клиент для взаимодействия с Ollama API.

Этот модуль реализует протокол ModelProvider для работы с Ollama API.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Final

import aiohttp

from config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    Config,
    validate_ollama_url,
)
from models.provider import MessageDict

# Кэшированные дефолтные опции для производительности
_DEFAULT_OPTIONS: Final = {
    "temperature": DEFAULT_TEMPERATURE,
    "num_predict": DEFAULT_MAX_TOKENS,
}

# Маппинг исключений для обработки ошибок API
_EXCEPTION_HANDLERS: Final[dict[type[Exception], Callable[..., str]]] = {
    aiohttp.ClientError: lambda host, **_: f"Не удалось подключиться к Ollama ({host})",
    asyncio.TimeoutError: lambda timeout, **_: f"Превышен таймаут запроса ({timeout}с)",
    json.JSONDecodeError: lambda **_: "Некорректный JSON в ответе API",
    KeyError: lambda operation, **_: f"Неожиданная ошибка при {operation}",
    TypeError: lambda operation, **_: f"Неожиданная ошибка при {operation}",
    ValueError: lambda **_: "Некорректный формат ответа API",
}


def _get_error_message(
    exc_type: type[Exception],
    operation: str,
    host: str | None = None,
    timeout: int | None = None,
) -> str:
    """
    Получить сообщение об ошибке на основе типа исключения.

    Args:
        exc_type: Тип исключения.
        operation: Название операции ("list_models" или "generate").
        host: URL хоста (опционально).
        timeout: Таймаут в секундах (опционально).

    Returns:
        Сообщение об ошибке.
    """
    # Ищем подходящий обработчик в иерархии исключений
    for exception_class, handler in _EXCEPTION_HANDLERS.items():
        if issubclass(exc_type, exception_class):
            return handler(
                operation=operation,
                host=host,
                timeout=timeout,
            )
    return f"Неожиданная ошибка при {operation}"


def _handle_api_error(
    operation: str,
    exc: Exception,
    host: str | None = None,
    timeout: int | None = None,
) -> OllamaError:
    """
    Обработать исключение API и вернуть OllamaError.

    Централизованная обработка ошибок для методов list_models и generate.
    Использует словарь маппинга исключений для определения сообщения об ошибке.

    Args:
        operation: Название операции ("list_models" или "generate").
        exc: Оригинальное исключение.
        host: URL хоста (опционально).
        timeout: Таймаут в секундах (опционально).

    Returns:
        OllamaError с соответствующим сообщением.
    """
    # Пробрасываем наши ошибки дальше
    if isinstance(exc, OllamaError):
        return exc

    # Получаем сообщение об ошибке через маппинг
    message = _get_error_message(
        type(exc),
        operation=operation,
        host=host,
        timeout=timeout,
    )

    return OllamaError(message, original_exception=exc)


def _validate_messages(messages: Any) -> None:
    """
    Валидировать параметр messages для generate метода.

    Args:
        messages: Параметр messages для валидации.

    Raises:
        ValueError: Если messages некорректный.
    """
    if not isinstance(messages, list):
        raise ValueError("messages должен быть списком")

    for msg in messages:
        if not isinstance(msg, dict):
            raise ValueError("Каждое сообщение должно быть словарём")
        if "role" not in msg or "content" not in msg:
            raise ValueError("Сообщение должно содержать 'role' и 'content'")


def _validate_response_structure(data: Any, _operation: str) -> None:
    """
    Валидировать структуру ответа API.

    Args:
        data: Данные ответа для валидации.
        _operation: Название операции для сообщения об ошибке.

    Raises:
        OllamaError: Если структура некорректная.
    """
    if not isinstance(data, dict):
        raise OllamaError("Некорректный формат ответа API")


class _HTTPSessionManager:
    """
    Управление HTTP-сессиями для Ollama API.

    Инкапсулирует логику создания, получения и закрытия HTTP-сессий.
    Вынесен для улучшения связности и тестируемости.

    Note:
        Реализует пулинг соединений через aiohttp.ClientSession:
        - Одна сессия используется для всех запросов к Ollama
        - Соединения автоматически переиспользуются (HTTP keep-alive)
        - Сессия создаётся лениво при первом запросе
        - Автоматическое пересоздание при закрытии
        - Таймаут настраивается через конфигурацию

    Scalability:
        Текущая реализация использует одну сессию на экземпляр OllamaClient.
        Для высоконагруженных сценариев можно рассмотреть:
        - Пул сессий с ограничением максимального количества соединений
        - Балансировку между несколькими экземплярами Ollama
        - Кэширование ответов моделей
    """

    def __init__(self, timeout: int = 60) -> None:
        """
        Инициализация менеджера сессий.

        Args:
            timeout: Таймаут запросов в секундах.
        """
        self._timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        """
        Получить или создать HTTP сессию.

        Returns:
            HTTP сессия для запросов.
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            )
        return self._session

    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        if self._session and not self._session.closed:
            try:
                await self._session.close()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                # Игнорируем ошибки при закрытии
                pass


class OllamaError(Exception):
    """
    Исключение для ошибок Ollama API.

    Возникает при проблемах с подключением, валидацией или обработкой ответов.
    """

    def __init__(
        self, message: str, original_exception: Exception | None = None
    ) -> None:
        """
        Инициализация исключения.

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


class OllamaClient:
    """
    Асинхронный клиент для работы с локальным Ollama API.

    Реализует протокол ModelProvider для dependency injection.

    Implements:
        ModelProvider: Протокол провайдера языковых моделей.
    """

    def __init__(self, host: str | None = None, config: Config | None = None) -> None:
        """
        Инициализация клиента.

        Args:
            host: URL хоста Ollama (по умолчанию из конфига).
            config: Конфигурация для dependency injection.

        Raises:
            ValueError: Если host некорректный.
        """
        self._config = config or Config()
        self.host = host or self._config.ollama_host

        # Валидация host параметра
        if not validate_ollama_url(self.host):
            raise ValueError(f"Некорректный URL хоста: {self.host}")

        # Выносим HTTP-логику в отдельный класс
        self._http_manager = _HTTPSessionManager(timeout=self._config.request_timeout)

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получить HTTP сессию через менеджер.

        Returns:
            HTTP сессия для запросов.
        """
        return await self._http_manager.get_session()

    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        await self._http_manager.close()

    async def list_models(self) -> list[str]:
        """
        Получить список доступных локальных моделей.

        Returns:
            Список названий моделей.

        Raises:
            OllamaError: Если не удалось подключиться к Ollama или получить данные.
        """
        session = await self._get_session()
        url = f"{self.host}/api/tags"

        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise OllamaError(
                        f"Ошибка получения списка моделей: {response.status}"
                    )

                # Обработка JSON с валидацией
                try:
                    data = await response.json()
                except json.JSONDecodeError as e:
                    raise OllamaError("Некорректный JSON в ответе API") from e

                # Валидация структуры ответа
                _validate_response_structure(data, "list_models")

                # Проверка ключа "models" с дефолтным значением
                models = data.get("models", [])

                if not isinstance(models, list):
                    raise OllamaError("Некорректный формат списка моделей")

                # Извлечение названий с валидацией каждого элемента
                return [
                    model.get("name")
                    for model in models
                    if isinstance(model, dict)
                    and isinstance(model.get("name"), str)
                    and model.get("name")
                ]

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            raise _handle_api_error(
                "list_models", e, host=self.host, timeout=self._config.request_timeout
            ) from e

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: Any,
    ) -> str:
        """
        Сгенерировать ответ от модели.

        Args:
            model: Название модели.
            messages: Список сообщений в формате Ollama.
            **kwargs: Дополнительные параметры генерации.

        Returns:
            Сгенерированный текст.

        Raises:
            OllamaError: Если генерация не удалась.
            ValueError: Если messages некорректный.
        """
        # Валидация параметра messages
        _validate_messages(messages)

        session = await self._get_session()
        url = f"{self.host}/api/chat"

        # Кэшированные дефолтные опции для производительности
        # Note: num_predict = max_tokens в терминах Ollama API
        options = {
            "temperature": kwargs.get("temperature", _DEFAULT_OPTIONS["temperature"]),
            "num_predict": kwargs.get("max_tokens", _DEFAULT_OPTIONS["num_predict"]),
        }

        payload = {
            "model": model,
            "messages": messages,
            "options": options,
            "stream": False,
        }

        try:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise OllamaError(
                        f"Ошибка генерации ({response.status})",
                        original_exception=Exception(error_text),
                    )

                # Обработка JSON с валидацией
                try:
                    data = await response.json()
                except json.JSONDecodeError as e:
                    raise OllamaError("Некорректный JSON в ответе API") from e

                # Валидация структуры ответа
                _validate_response_structure(data, "generate")

                # Использование .get() с дефолтными значениями
                message = data.get("message", {})
                if not isinstance(message, dict):
                    return ""

                content = message.get("content", "")
                return content if isinstance(content, str) else ""

        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            raise _handle_api_error(
                "generate", e, host=self.host, timeout=self._config.request_timeout
            ) from e
