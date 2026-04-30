#!/usr/bin/env python3
"""Entry point for AI Dialogue TUI application."""

from __future__ import annotations

import asyncio
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


async def _cleanup_app(app: DialogueApp) -> None:
    """Cleanup application resources.

    Args:
        app: Application instance to cleanup.

    """
    try:
        if hasattr(app, "_controller") and app._controller is not None:
            await app._controller.cleanup()
        if hasattr(app, "_client") and app._client is not None:
            await app._client.close()
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
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если loop работает, создаём task для cleanup
                # Задача будет выполнена при следующем цикле event loop
                _cleanup_handle = loop.call_soon(
                    lambda: asyncio.create_task(_cleanup_app(app))
                )
            else:
                loop.run_until_complete(_cleanup_app(app))
        except RuntimeError:
            # Нет активного loop - пропускаем async cleanup
            pass
        except Exception as e:
            log.warning("Error during final cleanup: %s", e)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
