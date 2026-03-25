#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей.

Этот модуль содержит точку входа приложения с обработкой исключений.
"""

from __future__ import annotations

import logging
import sys

from tui.app import DialogueApp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> int:
    """
    Запустить TUI приложение с обработкой исключений.

    Returns:
        Код выхода приложения.

    Note:
        Оборачивает app.run() в try/except для перехвата необработанных исключений.
    """
    app = DialogueApp()

    try:
        app.run()
        return 0
    except KeyboardInterrupt:
        # Нормальное завершение по Ctrl+C
        return 0
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
