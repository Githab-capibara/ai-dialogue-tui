#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей.

Этот модуль содержит точку входа приложения с обработкой исключений.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from factories.provider_factory import create_provider_factory
from models.config import Config
from models.provider import (
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from tui.app import DialogueApp

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> int:
    """Запустить TUI приложение с обработкой исключений.

    Returns:
        Код выхода приложения.

    Note:
        Оборачивает app.run() в try/except
        для перехвата необработанных исключений.

    """
    config = Config()

    # Создаём factory для внедрения зависимости (DIP)
    provider_factory = create_provider_factory(config)

    app = DialogueApp(config=config, provider_factory=provider_factory)

    try:
        app.run()
        return 0
    except asyncio.CancelledError:
        return 0
    except KeyboardInterrupt:
        return 0
    except ProviderConfigurationError as e:
        log.exception("Configuration error: %s", e)
        return 1
    except ProviderConnectionError as e:
        log.exception("Connection error: %s", e)
        return 1
    except ProviderGenerationError as e:
        log.exception("Generation error: %s", e)
        return 1
    except ProviderError as e:
        log.exception("Provider error: %s", e)
        return 1
    except (RuntimeError, SystemError) as e:
        log.exception("Critical application error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
