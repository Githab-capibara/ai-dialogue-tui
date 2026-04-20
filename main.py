#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей."""

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> int:
    """Запустить TUI приложение с обработкой исключений.

    Returns:
        Код выхода приложения.

    """
    config = Config()

    # Создаём factory для внедрения зависимости (DIP)
    provider_factory = create_provider_factory(config)

    app = DialogueApp(config=config, provider_factory=provider_factory)

    exit_code = 0
    try:
        app.run()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    except ProviderConfigurationError:
        log.exception("Configuration error")
        exit_code = 1
    except ProviderConnectionError:
        log.exception("Connection error")
        exit_code = 1
    except ProviderGenerationError:
        log.exception("Generation error")
        exit_code = 1
    except ProviderError:
        log.exception("Provider error")
        exit_code = 1
    except (RuntimeError, SystemError):
        log.exception("Critical application error")
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
