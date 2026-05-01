# Реестр проблем автономного рефакторинга
# Дата: 2026-05-01
# Проект: AI Dialogue TUI

## СВОДНАЯ СТАТИСТИКА АУДИТА

### Проблемы по категориям:
- STYLE: 52 (E501 line-too-long)
- LOGGING: 2 (logging.error вместо logging.exception)
- TYPE_SAFETY: 33 (pyright errors)
- ARCHITECTURE: 4 (prospector messages)
- SECURITY: 0 (bandit - только в .venv)

### Проблемы по уровню критичности:
- CRITICAL: 0
- HIGH: 2 (logging.error)
- MEDIUM: 4 (prospector)
- LOW: 81 (style + type)

---

## РЕЕСТР ПРОБЛЕМ

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | HIGH | LOGGING | services/dialogue_service.py:169 | Использование log.error вместо log.exception | Заменить на logging.exception |
| ISS-002 | HIGH | LOGGING | tui/app.py:689 | Использование log.error вместо log.exception | Заменить на logging.exception |
| ISS-003 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:22 | E704: multiple statements on one line (def) | Разделить определение на отдельные строки |
| ISS-004 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:31 | E704: multiple statements on one line (def) | Разделить определение на отдельные строки |
| ISS-005 | MEDIUM | ARCHITECTURE | main.py:69 | pylint: protected-access _client | Добавить публичный метод close или использовать existing |
| ISS-006 | MEDIUM | ARCHITECTURE | main.py:79 | pylint: protected-access _dialogue_log_file | Добавить публичный метод или сделать атрибут публичным |
| ISS-007 | MEDIUM | ARCHITECTURE | models/ollama_client.py:444 | line-too-long (135/120) | Разбить строку для читаемости |
| ISS-008 | LOW | STYLE | tests/test_textual_reactive.py:30 | E501 line too long (85 > 79) | Укоротить строку |
| ISS-009 | LOW | STYLE | tests/test_textual_reactive.py:33 | E501 line too long (87 > 79) | Укоротить строку |
| ISS-010 | LOW | STYLE | tests/test_timeout_fixes.py:46 | E501 line too long (100 > 79) | Укоротить строку |
| ISS-011 | LOW | STYLE | tests/test_timeout_fixes.py:66 | E501 line too long (94 > 79) | Укоротить строку |
| ISS-012 | LOW | STYLE | tests/test_timeout_fixes.py:76 | E501 line too long (97 > 79) | Укоротить строку |
| ISS-013 | LOW | STYLE | tests/test_timeout_fixes.py:128 | E501 line too long (85 > 79) | Укоротить строку |
| ISS-014 | LOW | STYLE | tests/test_timeout_fixes.py:137 | E501 line too long (91 > 79) | Укоротить строку |
| ISS-015 | LOW | STYLE | tests/test_timeout_fixes.py:147 | E501 line too long (84 > 79) | Укоротить строку |
| ISS-016 | LOW | STYLE | tests/test_timeout_fixes.py:152 | E501 line too long (95 > 79) | Укоротить строку |
| ISS-017 | LOW | STYLE | tests/test_timeout_fixes.py:158 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-018 | LOW | STYLE | tests/test_timeout_fixes.py:168 | E501 line too long (84 > 79) | Укоротить строку |
| ISS-019 | LOW | STYLE | tests/test_timeout_fixes.py:173 | E501 line too long (95 > 79) | Укоротить строку |
| ISS-020 | LOW | STYLE | tests/test_timeout_fixes.py:179 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-021 | LOW | STYLE | tests/test_timeout_fixes.py:182 | E501 line too long (83 > 79) | Укоротить строку |
| ISS-022 | LOW | STYLE | tests/test_timeout_fixes.py:183 | E501 line too long (99 > 79) | Укоротить строку |
| ISS-023 | LOW | STYLE | tests/test_ui_nomatches_handling.py:17 | E501 line too long (80 > 79) | Укоротить строку |
| ISS-024 | LOW | STYLE | tui/app.py:25 | E501 line too long (89 > 79) | Укоротить строку |
| ISS-025 | LOW | STYLE | tui/app.py:47 | E501 line too long (88 > 79) | Укоротить строку |
| ISS-026 | LOW | STYLE | tui/app.py:66 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-027 | LOW | STYLE | tui/app.py:198 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-028 | LOW | STYLE | tui/app.py:273 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-029 | LOW | STYLE | tui/app.py:295 | E501 line too long (106 > 79) | Укоротить строку |
| ISS-030 | LOW | STYLE | tui/app.py:297 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-031 | LOW | STYLE | tui/app.py:306 | E501 line too long (85 > 79) | Укоротить строку |
| ISS-032 | LOW | STYLE | tui/app.py:309 | E501 line too long (93 > 79) | Укоротить строку |
| ISS-033 | LOW | STYLE | tui/app.py:352 | E501 line too long (89 > 79) | Укоротить строку |
| ISS-034 | LOW | STYLE | tui/app.py:392 | E501 line too long (91 > 79) | Укоротить строку |
| ISS-035 | LOW | STYLE | tui/app.py:399 | E501 line too long (83 > 79) | Укоротить строку |
| ISS-036 | LOW | STYLE | tui/app.py:401 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-037 | LOW | STYLE | tui/app.py:402 | E501 line too long (84 > 79) | Укоротить строку |
| ISS-038 | LOW | STYLE | tui/app.py:404 | E501 line too long (85 > 79) | Укоротить строку |
| ISS-039 | LOW | STYLE | tui/app.py:544 | E501 line too long (95 > 79) | Укоротить строку |
| ISS-040 | LOW | STYLE | tui/app.py:545 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-041 | LOW | STYLE | tui/app.py:701 | E501 line too long (85 > 79) | Укоротить строку |
| ISS-042 | LOW | STYLE | tui/app.py:720 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-043 | LOW | STYLE | tui/app.py:723 | E501 line too long (80 > 79) | Укоротить строку |
| ISS-044 | LOW | STYLE | tui/app.py:725 | E501 whitespace before ':' + line too long | Исправить пробел перед ':' и разбить строку |
| ISS-045 | LOW | STYLE | tui/app.py:732 | E501 line too long (80 > 79) | Укоротить строку |
| ISS-046 | LOW | STYLE | tui/app.py:742 | E501 line too long (106 > 79) | Укоротить строку |
| ISS-047 | LOW | STYLE | tui/app.py:743 | E501 line too long (104 > 79) | Укоротить строку |
| ISS-048 | LOW | STYLE | tui/app.py:768 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-049 | LOW | STYLE | tui/app.py:777 | E501 line too long (113 > 79) | Укоротить строку |
| ISS-050 | LOW | STYLE | tui/app.py:780 | E501 line too long (82 > 79) | Укоротить строку |
| ISS-051 | LOW | STYLE | tui/app.py:786 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-052 | LOW | STYLE | tui/app.py:837 | E501 line too long (105 > 79) | Укоротить строку |
| ISS-053 | LOW | STYLE | tui/app.py:848 | E501 line too long (105 > 79) | Укоротить строку |
| ISS-054 | LOW | STYLE | tui/app.py:855 | E501 line too long (86 > 79) | Укоротить строку |
| ISS-055 | LOW | STYLE | tui/sanitizer.py:88 | E501 line too long (84 > 79) | Укоротить строку |

---

## ПАКЕТЫ ПРОБЛЕМ

### Пакет-1 (ISS-001 - ISS-020): Критичные исправления (логирование + архитектура)
- 2 критических исправления логирования
- 2 архитектурных исправления
- 16 стилистических в тестах

### Пакет-2 (ISS-021 - ISS-040): Стилевые исправления tui/app.py

### Пакет-3 (ISS-041 - ISS-055): Финальные стилистические исправления

### Пакеты 4-10: Дополнительные улучшения (на основе pyright type errors)

---

## ПЛАН ВЫПОЛНЕНИЯ

1. Исправить logging.error → logging.exception (2 файла)
2. Исправить E704 в dialogue_runner.py
3. Исправить pylint protected-access в main.py
4. Исправить line-too-long в ollama_client.py
5. Исправить все E501 line-too-long
6. Исправить type errors в тестах (pytest fixtures)
7. Запустить валидацию
8. Зафиксировать изменения
9. Обработать архивные отчёты