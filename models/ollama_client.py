"""Асинхронный клиент для взаимодействия с Ollama API."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from config import config


class OllamaError(Exception):
    """Исключение для ошибок Ollama API."""
    pass


class OllamaClient:
    """Асинхронный клиент для работы с локальным Ollama API."""
    
    def __init__(self, host: str | None = None):
        """
        Инициализация клиента.
        
        Args:
            host: URL хоста Ollama (по умолчанию из конфига).
        """
        self.host = host or config.ollama_host
        self._session: aiohttp.ClientSession | None = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать HTTP сессию."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config.request_timeout)
            )
        return self._session
    
    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def list_models(self) -> list[str]:
        """
        Получить список доступных локальных моделей.
        
        Returns:
            Список названий моделей.
            
        Raises:
            OllamaError: Если не удалось подключиться к Ollama.
        """
        session = await self._get_session()
        url = f"{self.host}/api/tags"
        
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise OllamaError(
                        f"Ошибка получения списка моделей: {response.status}"
                    )
                data = await response.json()
                models = data.get("models", [])
                return [model["name"] for model in models]
        except aiohttp.ClientError as e:
            raise OllamaError(
                f"Не удалось подключиться к Ollama ({self.host}): {e}"
            ) from e
    
    async def generate(
        self,
        model: str,
        messages: list[dict[str, str]],
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
        """
        session = await self._get_session()
        url = f"{self.host}/api/chat"
        
        # Параметры генерации
        options = {
            "temperature": kwargs.get("temperature", config.temperature),
            "num_predict": kwargs.get("max_tokens", config.max_tokens),
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
                        f"Ошибка генерации ({response.status}): {error_text}"
                    )
                data = await response.json()
                message = data.get("message", {})
                return message.get("content", "")
        except aiohttp.ClientError as e:
            raise OllamaError(
                f"Ошибка подключения при генерации: {e}"
            ) from e
        except asyncio.TimeoutError:
            raise OllamaError(
                f"Превышен таймаут запроса ({config.request_timeout}с)"
            )
