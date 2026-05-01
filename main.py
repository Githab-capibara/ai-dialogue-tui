#!/usr/bin/env python3
"""Entry point for AI Dialogue TUI application."""

from __future__ import annotations

import asyncio
import concurrent.futures
import contextlib
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

file_handler = logging.FileHandler(
    LOG_DIR / f"dialogue_{datetime.now(tz=UTC).strftime('%Y%m%d_%H%M%S')}.log",
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)
logging.getLogger().addHandler(file_handler)
logging.getLogger("aiohttp").setLevel(logging.WARNING)


async def _cleanup_dialogue_task(app: DialogueApp) -> None:
    """Останавливаем dialogue task если он запущен."""
    if not hasattr(app, "dialogue_task") or app.dialogue_task is None:
        return
    if app.dialogue_task.done():
        return

    app.dialogue_task.cancel()
    with contextlib.suppress(TimeoutError, asyncio.CancelledError):
        await asyncio.wait_for(app.dialogue_task, timeout=5.0)


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
    client = getattr(app, "_client", None)
    if client is None:
        return
    try:
        await asyncio.wait_for(client.close(), timeout=5.0)
    except (TimeoutError, asyncio.CancelledError):
        log.debug("Client close timed out or cancelled")


def _close_log_file(app: DialogueApp) -> None:
    """Закрываем log файл."""
    log_file = getattr(app, "_dialogue_log_file", None)
    if log_file is not None:
        try:
            log_file.close()
        except OSError:
            log.debug("Log file close error")


async def _cleanup_app(app: DialogueApp) -> None:
    """Cleanup application resources.

    Args:
        app: Application instance to cleanup.

    """
    await _cleanup_dialogue_task(app)
    await _cleanup_controller(app)
    await _cleanup_client(app)
    _close_log_file(app)


def _run_cleanup(app: DialogueApp) -> None:
    """Run cleanup in a thread if event loop is running."""
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, _cleanup_app(app))
            try:
                future.result(timeout=10.0)
            except concurrent.futures.TimeoutError as err:
                log.warning("Cleanup error: %s", err)
    except RuntimeError:
        # Нет активного loop - создаём новый
        try:
            asyncio.run(_cleanup_app(app))
        except (asyncio.CancelledError, OSError) as err:
            log.warning("Cleanup error: %s", err)
    except (asyncio.CancelledError, OSError) as err:
        log.warning("Cleanup setup error: %s", err)


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
    except RuntimeError:
        log.exception("Runtime error in application")
        exit_code = 1
    except SystemError:
        log.exception("System error in application")
        exit_code = 1
    finally:
        _run_cleanup(app)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
