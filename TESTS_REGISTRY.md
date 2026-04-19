# Тестовый реестр

| Путь | Назначение | Проверяемый функционал | Дата актуализации |
|------|------------|------------------------|------------------|
| tests/test_audit_fixes.py | Аудит исправлений кода | Проверка 11+ исправлений из аудита (Exception handling, DIP, XSS, кэш) | 2026-04-19 |
| tests/test_critical.py | Критические проблемы | Валидация URL, обработка ошибок, TypedDict, санитизация | 2026-04-19 |
| tests/test_call_from_thread_fix.py | Исправление call_from_thread | Замена call_from_thread на call_after_refresh | 2026-04-19 |
| tests/test_fixes.py | Общие исправления | List comprehension, dataclass, UI константы | 2026-04-19 |
| tests/test_architecture_refactor.py | Архитектурный рефакторинг | Удаление лишних классов, упрощение методов | 2026-04-19 |
| tests/test_architecture_integrity.py | Целостность архитектуры | SOLID, ProviderError иерархия, кэширование, контекст | 2026-04-19 |
| tests/test_audit_fixes_verification.py | Верификация аудита | HIGH/MEDIUM/LOW исправления | 2026-04-19 |
| tests/test_architecture_patterns.py | Архитектурные паттерны | Separation of Concerns, циклические зависимости | 2026-04-19 |
| tests/test_textual_reactive.py | Textual реактивность | CSS, bind, reactive атрибуты | 2026-04-19 |
| tests/test_new_audit_fixes.py | Новые аудит исправления | Trim context, Ctrl+C binding, locks, cleanup | 2026-04-19 |
| tests/test_timeout_fixes.py | Таймауты | Sock read timeout, обработка TimeoutError | 2026-04-19 |
| tests/test_arch_audit_fixes.py | Архитектурный аудит | DRY, KISS, YAGNI, SRP принципы | 2026-04-19 |
| tests/test_dialogue_runner_error_handling.py | Обработка ошибок диалога | ProviderError, error handling | 2026-04-19 |
| tests/test_code_audit_fixes_verification.py | Верификация кода | Code audit исправления | 2026-04-19 |
| tests/test_code_audit_fixes.py | Аудит кода | Код исправления | 2026-04-19 |
| tests/test_architecture.py | Архитектура | Dependency injection, Protocol, service layer | 2026-04-19 |
| tests/test_arch_fixes.py | Архитектурные исправления | Sanitizer, logging, boundaries | 2026-04-19 |

Всего: 19 тестовых файлов, 314 тестов.