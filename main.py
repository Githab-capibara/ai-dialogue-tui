#!/usr/bin/env python3
"""Entry point for AI Dialogue TUI application."""

from __future__ import annotations

import asyncio
import logging
import os
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
    level=int(os.environ.get("LOG_LEVEL", logging.INFO)),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)


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
    except (ProviderConfigurationError, ProviderConnectionError, ProviderGenerationError, ProviderError) as e:
        log.exception("%s: %s", type(e).__name__, e)
        exit_code = 1
    except (RuntimeError, SystemError):
        log.exception("Critical application error")
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
