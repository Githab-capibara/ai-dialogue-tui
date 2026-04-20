"""Фабрика для создания провайдеров моделей.

Этот модуль содержит фабричные функции для внедрения зависимостей.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from models.ollama_client import OllamaClient

if TYPE_CHECKING:
    from models.config import Config
    from models.provider import ModelProvider


class ProviderFactory(Protocol):
    """Протокол фабрики провайдеров моделей.

    Используется для dependency injection в приложении.
    """

    def __call__(self) -> ModelProvider:
        """Создать экземпляр провайдера моделей."""


def create_ollama_provider(config: Config) -> ModelProvider:
    """Создать провайдер Ollama.

    Args:
        config: Конфигурация для подключения.

    Returns:
        Настроенный провайдер ModelProvider.

    """
    return OllamaClient(host=config.ollama_host)


def create_provider_factory(config: Config) -> ProviderFactory:
    """Создать фабрику провайдеров.

    Args:
        config: Конфигурация для создания провайдеров.

    Returns:
        Фабричная функция для создания ModelProvider.

    """

    def factory() -> ModelProvider:
        return create_ollama_provider(config)

    return factory
