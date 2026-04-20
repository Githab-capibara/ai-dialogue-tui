#!/usr/bin/env python3
"""Entry point for AI Dialogue TUI application."""

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
