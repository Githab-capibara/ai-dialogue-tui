# Autonomous Refactoring Protocol - Implementation Plan

## ЭТАП 0: Отчёт предварительного аудита

### 0.1 Результаты аудита

| Инструмент | Статус | Проблемы | Категории |
|------------|--------|----------|-----------|
| ruff | ✅ PASS | 0 | - |
| mypy | ✅ PASS | 0 | - |
| flake8 | ⚠️ WARNINGS | 35 | STYLE (E501) |
| pyright | ⚠️ WARNINGS | 30 | TYPE_SAFETY (в тестах) |
| pytest | ⚠️ 5 FAILED | 5 | TEST_EXPECTATION |
| bandit | Не проверен | - | - |
| vulture | Не проверен | - | - |

### 0.2 Реестр проблем (40 записей)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | LOW | STYLE | controllers/dialogue_controller.py:133 | E501 line too long (85 > 79) | Разбить строку |
| ISS-002 | LOW | STYLE | models/__init__.py:3 | E501 line too long (84 > 79) | Разбить строку |
| ISS-003 | LOW | STYLE | models/conversation.py:50 | E501 line too long (111 > 79) | Разбить строку |
| ISS-004 | LOW | STYLE | models/conversation.py:59 | E501 line too long (82 > 79) | Разбить строку |
| ISS-005 | LOW | STYLE | models/conversation.py:107 | E501 line too long (88 > 79) | Разбить строку |
| ISS-006 | LOW | STYLE | models/conversation.py:113 | E501 line too long (91 > 79) | Разбить строку |
| ISS-007 | LOW | STYLE | models/ollama_client.py:158 | E501 line too long (99 > 79) | Разбить строку |
| ISS-008 | LOW | STYLE | models/ollama_client.py:246 | E501 line too long (80 > 79) | Разбить строку |
| ISS-009 | LOW | STYLE | models/ollama_client.py:479 | E501 line too long (85 > 79) | Разбить строку |
| ISS-010 | LOW | STYLE | services/dialogue_runner.py:110 | E501 line too long (88 > 79) | Разбить строку |
| ISS-011 | LOW | STYLE | services/dialogue_service.py:150 | E501 line too long (82 > 79) | Разбить строку |
| ISS-012 | LOW | STYLE | tui/app.py:73 | E501 line too long (82 > 79) | Разбить строку |
| ISS-013 | LOW | STYLE | tui/app.py:92 | E501 line too long (85 > 79) | Разбить строку |
| ISS-014 | LOW | STYLE | tui/app.py:112 | E501 line too long (86 > 79) | Разбить строку |
| ISS-015 | LOW | STYLE | tui/app.py:184 | E501 line too long (82 > 79) | Разбить строку |
| ISS-016 | LOW | STYLE | tui/app.py:190 | E501 line too long (97 > 79) | Разбить строку |
| ISS-017 | LOW | STYLE | tui/app.py:197 | E501 line too long (83 > 79) | Разбить строку |
| ISS-018 | LOW | STYLE | tui/app.py:198 | E501 line too long (83 > 79) | Разбить строку |
| ISS-019 | LOW | STYLE | tui/app.py:245 | E501 line too long (82 > 79) | Разбить строку |
| ISS-020 | LOW | STYLE | tui/app.py:267 | E501 line too long (153 > 79) | Разбить строку |
| ISS-021 | LOW | STYLE | tui/app.py:269 | E501 line too long (106 > 79) | Разбить строку |
| ISS-022 | LOW | STYLE | tui/app.py:284 | E501 line too long (83 > 79) | Разбить строку |
| ISS-023 | LOW | STYLE | tui/app.py:292 | E501 line too long (87 > 79) | Разбить строку |
| ISS-024 | LOW | STYLE | tui/app.py:309 | E501 line too long (91 > 79) | Разбить строку |
| ISS-025 | LOW | STYLE | tui/app.py:337 | E501 line too long (82 > 79) | Разбить строку |
| ISS-026 | LOW | STYLE | tui/app.py:430 | E501 line too long (92 > 79) | Разбить строку |
| ISS-027 | LOW | STYLE | tui/app.py:454 | E501 line too long (86 > 79) | Разбить строку |
| ISS-028 | LOW | STYLE | tui/app.py:455 | E501 line too long (89 > 79) | Разбить строку |
| ISS-029 | LOW | STYLE | tui/app.py:460 | E501 line too long (92 > 79) | Разбить строку |
| ISS-030 | LOW | STYLE | tui/app.py:505 | E501 line too long (80 > 79) | Разбить строку |
| ISS-031 | LOW | STYLE | tui/app.py:543 | E501 line too long (92 > 79) | Разбить строку |
| ISS-032 | LOW | STYLE | tui/app.py:546 | E501 line too long (106 > 79) | Разбить строку |
| ISS-033 | LOW | STYLE | tui/app.py:582 | E501 line too long (110 > 79) | Разбить строку |
| ISS-034 | LOW | STYLE | tui/app.py:591 | E501 line too long (84 > 79) | Разбить строку |
| ISS-035 | LOW | STYLE | tui/sanitizer.py:82 | E501 line too long (84 > 79) | Разбить строку |
| ISS-036 | HIGH | TEST_EXPECTATION | tests/test_critical.py:154 | Тест ожидает "Некорректный URL", но сообщение на английском | Изменить regex в тесте на "Invalid Ollama URL" |
| ISS-037 | HIGH | TEST_EXPECTATION | tests/test_critical.py:159 | Тест ожидает "Некорректный URL", но сообщение на английском | Изменить regex в тесте на "Invalid Ollama URL" |
| ISS-038 | HIGH | TEST_EXPECTATION | tests/test_critical.py:164 | Тест ожидает "Некорректный URL", но сообщение на английском | Изменить regex в тесте на "Invalid Ollama URL" |
| ISS-039 | HIGH | TEST_EXPECTATION | tests/test_critical.py:211 | Тест ожидает "Некорректный URL", но сообщение на английском | Изменить regex в тесте на "Invalid host URL" |
| ISS-040 | HIGH | TEST_EXPECTATION | tests/test_critical.py:261 | Тест ожидает "Некорректный JSON", но сообщение на английском | Изменить regex в тесте на "Invalid JSON in API response" |

### 0.3 Группировка по пакетам

**Пакет-1 (ISS-001..ISS-020)**: STYLE - Длинные строки в controllers, models
**Пакет-2 (ISS-021..ISS-035)**: STYLE - Длинные строки в tui/app.py, services
**Пакет-3 (ISS-036..ISS-040)**: TEST_EXPECTATION - Исправление тестов

---

## ЭТАП 1: Выполнение рефакторинга

### Пакет-1: STYLE - Длинные строки (ISS-001..ISS-020)

#### Задачи:
1. Исправить line length в controllers/dialogue_controller.py
2. Исправить line length в models/__init__.py
3. Исправить line length в models/conversation.py
4. Исправить line length в models/ollama_client.py

### Пакет-2: STYLE - Длинные строки в tui (ISS-021..ISS-035)

#### Задачи:
1. Исправить line length в services/dialogue_runner.py
2. Исправить line length в services/dialogue_service.py
3. Исправить line length в tui/app.py (множественные строки)
4. Исправить line length в tui/sanitizer.py

### Пакет-3: TEST_EXPECTATION (ISS-036..ISS-040)

#### Задачи:
1. Исправить тестовые ожидания в tests/test_critical.py
2. Заменить русские regex на английские эквиваленты

---

## ЭТАП 2: Валидация и завершение

### Финальные проверки:
```bash
ruff check . --fix
flake8 . --count
pytest -q --tb=short
```

### Финальный коммит после каждого пакета
