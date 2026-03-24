#!/usr/bin/env python3
"""Точка входа для TUI приложения диалога ИИ-моделей."""

from __future__ import annotations

import sys

from tui.app import DialogueApp


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
        print(f"Критическая ошибка приложения: {e}", file=sys.stderr)
        print(
            "Пожалуйста, проверьте логи или сообщите об ошибке разработчикам.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
