#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей.

Этот модуль содержит точку входа приложения с обработкой исключений.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from models.config import Config
from models.ollama_client import OllamaClient
from models.provider import (
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from tui.app import DialogueApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> int:  # pylint: disable=too-many-return-statements
    """
    Запустить TUI приложение с обработкой исключений.

    Returns:
        Код выхода приложения.

    Note:
        Оборачивает app.run() в try/except для перехвата необработанных исключений.
    """
    config = Config()

    # Создаём factory для внедрения зависимости (DIP)
    def provider_factory() -> OllamaClient:
        return OllamaClient(host=config.ollama_host)

    app = DialogueApp(config=config, provider_factory=provider_factory)

    try:
        app.run()
        return 0
    except asyncio.CancelledError:
        return 0
    except KeyboardInterrupt:
        # Нормальное завершение по Ctrl+C
        return 0
    except ProviderConfigurationError as e:
        # Ошибка конфигурации
        logging.exception("Ошибка конфигурации: %s", e)
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        return 1
    except ProviderConnectionError as e:
        # Ошибка подключения
        logging.exception("Ошибка подключения: %s", e)
        print(
            f"Ошибка подключения к Ollama: {e}\n"
            "Убедитесь, что Ollama запущен и доступен.",
            file=sys.stderr,
        )
        return 1
    except ProviderGenerationError as e:
        # Ошибка генерации
        logging.exception("Ошибка генерации: %s", e)
        print(f"Ошибка генерации ответа: {e}", file=sys.stderr)
        return 1
    except ProviderError as e:
        # Общая ошибка провайдера
        logging.exception("Ошибка провайдера: %s", e)
        print(f"Ошибка провайдера моделей: {e}", file=sys.stderr)
        return 1
    except (RuntimeError, SystemError) as e:
        # Выводим понятное сообщение об ошибке
        logging.exception("Критическая ошибка приложения: %s", e)
        print(f"Критическая ошибка приложения: {e}", file=sys.stderr)
        print(
            "Пожалуйста, проверьте логи или сообщите об ошибке разработчикам.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
