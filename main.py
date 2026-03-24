#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей."""

import asyncio
import sys

from tui.app import DialogueApp


def main() -> int:
    """
    Запустить TUI приложение.
    
    Returns:
        Код выхода приложения.
    """
    app = DialogueApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
