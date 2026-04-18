"""Асинхронный клиент для взаимодействия с Ollama API.

Этот модуль реализует протокол ModelProvider для работы с Ollama API.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    import aiohttp

import aiohttp

from models.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    Config,
    validate_ollama_url,
)
from models.provider import (
    MessageDict,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)

_logger = logging.getLogger(__name__)

# Кэшированные дефолтные опции для производительности
_DEFAULT_OPTIONS: Final = {
    "temperature": DEFAULT_TEMPERATURE,
    "num_predict": DEFAULT_MAX_TOKENS,
}

# TTL для кэша моделей (5 минут)
_MODELS_CACHE_TTL: Final = 300


class _RequestValidator:
    """Валидация запросов к Ollama API.

    Инкапсулирует логику валидации входных параметров для API запросов.
    """

    @staticmethod
    def validate_host(host: str) -> None:
        """Валидировать URL хоста.

        Args:
            host: URL хоста для валидации.

        Raises:
            ValueError: Если URL некорректный.

        """
        if not validate_ollama_url(host):
            msg = f"Некорректный URL хоста: {host}"
            raise ValueError(msg)

    @staticmethod
    def validate_messages(messages: Any) -> None:
        """Валидировать messages для generate метода.

        Args:
            messages: Параметр messages для валидации.

        Raises:
            ValueError: Если messages некорректный.

        """
        if not isinstance(messages, list):
            msg = "messages должен быть списком"
            raise ValueError(msg)

        for msg in messages:
            if not isinstance(msg, dict):
                msg_0 = "Каждое сообщение должно быть словарём"
                raise ValueError(msg_0)
            if "role" not in msg or "content" not in msg:
                msg_0 = "Сообщение должно содержать 'role' и 'content'"
                raise ValueError(msg_0)


class _ResponseHandler:
    """Обработка ответов от Ollama API.

    Инкапсулирует логику обработки и валидации ответов API.
    """

    @staticmethod
    def validate_status_code(status: int, operation: str) -> None:
        """Валидировать HTTP статус код ответа.

        Args:
            status: HTTP статус код.
            operation: Название операции для сообщения об ошибке.

        Raises:
            ProviderGenerationError: Если статус код не 200.

        """
        if status != 200:
            msg = f"Ошибка {operation}: HTTP {status}"
            raise ProviderGenerationError(msg)

    @staticmethod
    def parse_json_response(
        data: Any,
        operation: str,
    ) -> dict[str, Any]:
        """Валидировать и распарсить JSON ответ.

        Args:
            data: Данные для валидации.
            operation: Название операции для сообщения об ошибке.

        Returns:
            Распарсенные данные.

        Raises:
            ProviderGenerationError: Если формат некорректный.

        """
        if not isinstance(data, dict):
            msg = f"Некорректный формат ответа API ({operation})"
            raise ProviderGenerationError(msg)
        return data

    @staticmethod
    def extract_models_list(data: dict[str, Any]) -> list[str]:
        """Извлечь список моделей из ответа API.

        Args:
            data: Данные ответа API.

        Returns:
            Список названий моделей.

        """
        models = data.get("models", [])
        if not isinstance(models, list):
            return []

        return [
            str(model.get("name"))
            for model in models
            if isinstance(model, dict) and isinstance(model.get("name"), str) and model.get("name")
        ]

    @staticmethod
    def extract_generation_response(data: dict[str, Any]) -> str:
        """Извлечь текст ответа из ответа API генерации.

        Args:
            data: Данные ответа API.

        Returns:
            Текст ответа или пустая строка.

        """
        message = data.get("message", {})
        if not isinstance(message, dict):
            return ""

        content = message.get("content", "")
        return content if isinstance(content, str) else ""


class _HTTPSessionManager:
    """Управление HTTP-сессиями для Ollama API.

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

    def __init__(
        self,
        timeout: int = 60,
        conn_timeout: int = 10,
        sock_read_timeout: int = 60,
    ) -> None:
        """Инициализация менеджера сессий.

        Args:
            timeout: Общий таймаут запросов в секундах.
            conn_timeout: Таймаут подключения в секундах.
            sock_read_timeout: Таймаут чтения сокета в секундах.

        """
        self._timeout = timeout
        self._conn_timeout = conn_timeout
        self._sock_read_timeout = sock_read_timeout
        self._session: aiohttp.ClientSession | None = None
        self._lock = asyncio.Lock()

    async def get_session(self) -> aiohttp.ClientSession:
        """Получить или создать HTTP сессию.

        Returns:
            HTTP сессия для запросов.

        """
        async with self._lock:
            if self._session is None or self._session.closed:
                self._session = aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(
                        total=self._timeout,
                        connect=self._conn_timeout,
                        sock_read=self._sock_read_timeout,
                    ),
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


class _ModelsCache:
    """Кэширование списка моделей.

    Реализует простой TTL-кэш для результата list_models.
    """

    def __init__(self, ttl: int = _MODELS_CACHE_TTL) -> None:
        """Инициализация кэша.

        Args:
            ttl: Время жизни кэша в секундах.

        """
        self._ttl = ttl
        self._models: list[str] | None = None
        self._cache_timestamp: float | None = None

    def _is_cache_valid(self) -> bool:
        """Проверить валидность кэша.

        Returns:
            True если кэш валилен.

        """
        if self._models is None or self._cache_timestamp is None:
            return False

        current_time = time.time()
        return (current_time - self._cache_timestamp) < self._ttl

    def get(self) -> list[str] | None:
        """Получить закэшированные модели если кэш валиден.

        Returns:
            Список моделей или None если кэш не валиден.

        """
        if self._is_cache_valid():
            return self._models
        return None

    def set(self, models: list[str]) -> None:
        """Сохранить модели в кэш.

        Args:
            models: Список моделей для кэширования.

        """
        self._models = models
        self._cache_timestamp = time.time()

    def invalidate(self) -> None:
        """Очистить кэш."""
        self._models = None
        self._cache_timestamp = None


class OllamaClient:
    """Асинхронный клиент для работы с локальным Ollama API.

    Реализует протокол ModelProvider для dependency injection.

    Implements:
        ModelProvider: Протокол провайдера языковых моделей.
    """

    def __init__(self, host: str | None = None, config: Config | None = None) -> None:
        """Инициализация клиента.

        Args:
            host: URL хоста Ollama (по умолчанию из конфига).
            config: Конфигурация для dependency injection.

        Raises:
            ValueError: Если host некорректный.

        """
        self._config = config or Config()
        self.host = host or self._config.ollama_host

        # Валидация host параметра через вынесенный класс
        _RequestValidator.validate_host(self.host)

        self._http_manager = _HTTPSessionManager(
            timeout=self._config.request_timeout,
            sock_read_timeout=self._config.sock_read_timeout,
        )

        self._models_cache = _ModelsCache(ttl=_MODELS_CACHE_TTL)
        self._models_cache = _ModelsCache(ttl=_MODELS_CACHE_TTL)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить HTTP сессию через менеджер.

        Returns:
            HTTP сессия для запросов.

        """
        return await self._http_manager.get_session()

    async def close(self) -> None:
        """Закрыть HTTP сессию и очистить кэш."""
        await self._http_manager.close()
        self._models_cache.invalidate()

    async def list_models(self) -> list[str]:
        """Получить список доступных локальных моделей.

        Использует кэширование для улучшения производительности.
        Кэш действителен в течение _MODELS_CACHE_TTL секунд.

        Returns:
            Список названий моделей.

        Raises:
            ProviderConnectionError: Если не удалось подключиться к Ollama.
            ProviderGenerationError: Если не удалось получить данные.

        """
        # Проверяем кэш
        cached_models = self._models_cache.get()
        if cached_models is not None:
            return cached_models

        session = await self._get_session()
        url = f"{self.host}/api/tags"

        try:
            async with session.get(url) as response:
                # Валидация статуса
                _ResponseHandler.validate_status_code(response.status, "list_models")

                # Обработка JSON с валидацией
                try:
                    data = await response.json()
                except json.JSONDecodeError as e:
                    msg = "Некорректный JSON в ответе API"
                    raise ProviderGenerationError(msg) from e

                # Валидация структуры ответа
                _ResponseHandler.parse_json_response(data, "list_models")

                # Извлечение списка моделей
                models = _ResponseHandler.extract_models_list(data)

                # Кэшируем результат
                self._models_cache.set(models)

                return models

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            msg = f"Не удалось подключиться к Ollama ({self.host})"
            raise ProviderConnectionError(
                msg,
                e,
            ) from e
        except ProviderError as e:
            # Логируем и пробрасываем наши ошибки дальше
            _logger.debug("ProviderError при получении списка моделей: %s", e)
            raise
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            msg = f"Ошибка валидации ответа API: {e}"
            raise ProviderGenerationError(msg) from e
        except OSError as e:
            _logger.warning("Игнорируемое OSError при получении списка моделей: %s", e)
            msg = f"Ошибка ввода-вывода при получении списка моделей: {e}"
            raise ProviderGenerationError(msg) from e

    async def generate(
        self,
        model: str,
        messages: list[MessageDict],
        **kwargs: Any,
    ) -> str:
        """Сгенерировать ответ от модели.

        Args:
            model: Название модели.
            messages: Список сообщений в формате Ollama.
            **kwargs: Дополнительные параметры генерации.

        Returns:
            Сгенерированный текст.

        Raises:
            ProviderError: Если генерация не удалась.
            ValueError: Если messages некорректный.

        """
        # Валидация параметра messages
        _RequestValidator.validate_messages(messages)

        session = await self._get_session()
        url = f"{self.host}/api/chat"

        # Кэшированные дефолтные опции для производительности
        # Note: num_predict = max_tokens в терминах Ollama API
        options = {
            "temperature": kwargs.get("temperature", self._config.temperature),
        }
        max_tokens = kwargs.get("max_tokens", self._config.max_tokens)
        if max_tokens > 0:
            options["num_predict"] = max_tokens

        payload = {
            "model": model,
            "messages": messages,
            "options": options,
            "stream": False,
        }

        try:
            async with session.post(url, json=payload) as response:
                # Валидация статуса
                _ResponseHandler.validate_status_code(response.status, "generate")

                # Обработка JSON с валидацией
                try:
                    data = await response.json()
                except json.JSONDecodeError as e:
                    msg = "Некорректный JSON в ответе API"
                    raise ProviderGenerationError(msg) from e

                # Валидация структуры ответа
                _ResponseHandler.parse_json_response(data, "generate")

                # Извлечение ответа
                return _ResponseHandler.extract_generation_response(data)

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            timeout_info = f"Таймаут: {self._config.sock_read_timeout}с"
            msg = (
                f"Не удалось подключиться к Ollama ({self.host}). "
                f"{timeout_info}. Попробуйте увеличить таймаут в настройках."
            )
            raise ProviderConnectionError(
                msg,
                e,
            ) from e
        except ProviderError as e:
            # Логируем и пробрасываем наши ошибки дальше
            _logger.debug("ProviderError при генерации ответа: %s", e)
            raise
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            msg = f"Ошибка валидации ответа API: {e}"
            raise ProviderGenerationError(msg) from e
        except OSError as e:
            _logger.warning("Игнорируемое OSError при генерации ответа: %s", e)
            msg = f"Ошибка ввода-вывода при генерации ответа: {e}"
            raise ProviderGenerationError(msg) from e
