#!/usr/bin/env python3
"""Entry point for AI Dialogue TUI application."""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from factories.provider_factory import create_provider_factory
from models.config import Config
from models.provider import (
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from tui.app import DialogueApp

LOG_DIR = Path("/log")
try:
    LOG_DIR.mkdir(exist_ok=True)
except PermissionError:
    LOG_DIR = Path(__file__).parent / "logs"
    LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=int(os.environ.get("LOG_LEVEL", logging.INFO)),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

file_handler = logging.FileHandler(LOG_DIR / f"dialogue_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)
logging.getLogger("aiohttp").setLevel(logging.WARNING)


async def _cleanup_dialogue_task(app: DialogueApp) -> None:
    """Останавливаем dialogue task если он запущен."""
    if not hasattr(app, "dialogue_task") or app.dialogue_task is None:
        return
    if app.dialogue_task.done():
        return

    app.dialogue_task.cancel()
    try:
        await asyncio.wait_for(app.dialogue_task, timeout=5.0)
    except (TimeoutError, asyncio.CancelledError):
        pass


async def _cleanup_controller(app: DialogueApp) -> None:
    """Очищаем controller."""
    if not hasattr(app, "controller") or app.controller is None:
        return
    try:
        await asyncio.wait_for(app.controller.cleanup(), timeout=5.0)
    except (TimeoutError, asyncio.CancelledError, AttributeError):
        log.debug("Controller cleanup timed out or cancelled")


async def _cleanup_client(app: DialogueApp) -> None:
    """Закрываем клиент."""
    if not hasattr(app, "_client") or app._client is None:
        return
    try:
        await asyncio.wait_for(app._client.close(), timeout=5.0)
    except (TimeoutError, asyncio.CancelledError):
        log.debug("Client close timed out or cancelled")


def _cleanup_log_file(app: DialogueApp) -> None:
    """Закрываем log файл."""
    if not hasattr(app, "_dialogue_log_file") or app._dialogue_log_file is None:
        return
    try:
        app._dialogue_log_file.close()
    except OSError:
        log.debug("Log file close error")


async def _cleanup_app(app: DialogueApp) -> None:
    """Cleanup application resources.

    Args:
        app: Application instance to cleanup.

    """
    try:
        await _cleanup_dialogue_task(app)
        await _cleanup_controller(app)
        await _cleanup_client(app)
        _cleanup_log_file(app)
    except Exception as e:
        log.warning("Error during cleanup: %s", e)


def main() -> int:
    """Run the TUI application with exception handling.

    Returns:
        Application exit code.

    """
    config = Config()

    # Create factory for dependency injection (DIP)
    provider_factory = create_provider_factory(config)

    app = DialogueApp(config=config, provider_factory=provider_factory)

    exit_code = 0
    try:
        app.run()
    except asyncio.CancelledError:
        log.warning("Application cancelled")
    except KeyboardInterrupt:
        log.info("Application interrupted by user")
    except (ProviderConfigurationError, ProviderConnectionError, ProviderGenerationError, ProviderError):
        log.exception("Provider error occurred")
        exit_code = 1
    except (RuntimeError, SystemError):
        log.exception("Critical application error")
        exit_code = 1
    finally:
        # Гарантированный cleanup ресурсов
        try:
            # Проверяем, есть ли уже запущенный event loop
            try:
                asyncio.get_running_loop()
                # Если loop уже работает, запускаем cleanup в новом потоке
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(asyncio.run, _cleanup_app(app))
                    future.result(timeout=10.0)  # Ждём максимум 10 секунд
            except RuntimeError:
                # Нет активного loop - создаём новый
                asyncio.run(_cleanup_app(app))
            except concurrent.futures.TimeoutError:
                log.warning("Cleanup timed out after 10 seconds")
            except Exception as e:
                log.warning("Error during final cleanup: %s", e)
        except Exception as e:
            log.warning("Error during final cleanup setup: %s", e)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
