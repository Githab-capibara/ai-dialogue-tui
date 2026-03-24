"""Асинхронный клиент для взаимодействия с Ollama API.

Этот модуль предоставляет асинхронный HTTP-клиент для работы с Ollama API,
включая получение списка моделей и генерацию ответов.
"""

from __future__ import annotations

import asyncio
from typing import Any, Literal, TypedDict

import aiohttp


class OllamaError(Exception):
    """Исключение для ошибок при работе с Ollama API."""


class MessageDict(TypedDict):
    """Тип для словаря сообщения.

    Attributes:
        role: Роль отправителя (user, assistant, system).
        content: Содержание сообщения.
    """

    role: Literal["user", "assistant", "system"]
    content: str


class OllamaClient:
    """Асинхронный клиент для Ollama API.

    Attributes:
        host: URL хоста Ollama API.
        timeout: Таймаут запросов в секундах.

    Note:
        Использует aiohttp для асинхронных HTTP-запросов.
        Поддерживает ленивое создание сессии и автоматическое переподключение.
    """

    def __init__(self, host: str = "http://localhost:11434", timeout: int = 60) -> None:
        """
        Инициализировать Ollama клиент.

        Args:
            host: URL хоста Ollama API.
            timeout: Таймаут запроса в секундах.

        Raises:
            ValueError: Если URL хоста некорректен.
        """
        self._validate_host(host)
        self.host = host
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None
        self._session_closing: bool = False

    def _validate_host(self, host: str) -> None:
        """
        Проверить корректность URL хоста.

        Args:
            host: URL для проверки.

        Raises:
            ValueError: Если URL некорректен.
        """
        try:
            parsed = urlparse(host)
            if parsed.scheme not in ("http", "https"):
                raise ValueError(
                    f"Некорректный URL: {host}. "
                    "URL должен начинаться с http:// или https://"
                )
            if not parsed.netloc:
                raise ValueError(f"Некорректный URL: {host}. Отсутствует host.")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Некорректный URL хоста: {host}") from e

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Получить или создать HTTP сессию.

        Returns:
            HTTP сессия для запросов.

        Note:
            Создаёт новую сессию при необходимости.
            Если сессия закрывается, создаёт новую.
        """
        if self._session is None or self._session.closed or self._session_closing:
            self._session_closing = False
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """
        Закрыть HTTP сессию.

        Note:
            Корректно обрабатывает ситуацию когда сессия уже закрывается.
        """
        if self._session is not None and not self._session.closed:
            self._session_closing = True
            await self._session.close()
            self._session = None

    async def list_models(self) -> list[str]:
        """
        Получить список доступных моделей.

        Returns:
            Список названий моделей.

        Raises:
            OllamaError: Если не удалось получить список моделей.

        Note:
            Валидирует структуру ответа API перед парсингом.
        """
        session = await self._get_session()
        url = f"{self.host}/api/tags"
        try:
            async with session.get(url, timeout=self.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                # Валидация ключа "models"
                if "models" not in data:
                    raise OllamaError("Ответ API не содержит ключ 'models'")
                models_data = data["models"]
                if not isinstance(models_data, list):
                    raise OllamaError("Ключ 'models' должен содержать список")
                # Валидация каждого элемента
                result = []
                for model in models_data:
                    if not isinstance(model, dict):
                        continue
                    if "name" not in model:
                        continue
                    result.append(model["name"])
                return result
        except aiohttp.ClientError as e:
            raise OllamaError(f"Ошибка получения списка моделей: {e}") from e
        except (json.JSONDecodeError, ValueError) as e:
            raise OllamaError(f"Ошибка парсинга ответа: {e}") from e

    async def generate(
        self, model: str, messages: list[MessageDict], **kwargs: Any
    ) -> str:
        """
        Сгенерировать ответ модели.

        Args:
            model: Название модели.
            messages: Список сообщений для контекста.
            **kwargs: Дополнительные параметры для API.

        Returns:
            Сгенерированный ответ.

        Raises:
            OllamaError: Если не удалось сгенерировать ответ.

        Note:
            Валидирует структуру messages перед отправкой.
        """
        # Валидация messages
        if not isinstance(messages, list):
            raise ValueError("messages должен быть списком")
        for msg in messages:
            if not isinstance(msg, dict):
                raise ValueError("Каждое сообщение должно быть словарём")
            if "role" not in msg or "content" not in msg:
                raise ValueError("Сообщение должно содержать 'role' и 'content'")

        session = await self._get_session()
        url = f"{self.host}/api/chat"
        options = {
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 200),
            "stream": False,
        }
        payload = {"model": model, "messages": messages, "options": options}
        try:
            async with session.post(url, json=payload, timeout=self.timeout) as response:
                response.raise_for_status()
                data = await response.json()
                if "message" not in data:
                    raise OllamaError("Ответ API не содержит ключ 'message'")
                if "content" not in data["message"]:
                    raise OllamaError("Ответ API не содержит ключ 'content'")
                return data["message"]["content"]
        except asyncio.TimeoutError as e:
            raise OllamaError(f"Таймаут запроса к {model}: {e}") from e
        except aiohttp.ClientError as e:
            raise OllamaError(f"Ошибка запроса к {model}: {e}") from e
        except (json.JSONDecodeError, ValueError) as e:
            raise OllamaError(f"Ошибка парсинга ответа: {e}") from e
