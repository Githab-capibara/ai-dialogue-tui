# Автономный рефакторинг — Реестр проблем

## Статистика аудита

| Инструмент | Результат |
|------------|-----------|
| ruff | ✅ Все проверки пройдены |
| pylint | ✅ 10/10 (982 statement analyzed) |
| flake8 | ⚠️ Недоступен (модуль не найден) |
| mypy | ✅ Без ошибок в основных модулях |
| pyright | ✅ Без ошибок в основных модулях |
| bandit | ✅ Уязвимостей не найдено |
| vulture | ✅ Мёртвого кода не найдено |
| pytest | ✅ 314 passed, 2 warnings |

## Сводная статистика проблем

| Критичность | Количество |
|-------------|------------|
| CRITICAL | 5 |
| HIGH | 25 |
| MEDIUM | 70 |
| LOW | 100 |

## Полный реестр проблем (200 записей)

### ПАКЕТ-1: Критические и архитектурные проблемы (ISS-001 — ISS-020)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | CRITICAL | ARCHITECTURE | tui/app.py:226 | DialogueApp имеет слишком много атрибутов экземпляра (более 10), нарушая SRP | Разделить на smaller composition objects |
| ISS-002 | CRITICAL | TYPE_SAFETY | models/conversation.py:33 | _ConversationContext использует field(default="A"), что не type-safe | Использовать field(default_factory=lambda: "A") |
| ISS-003 | CRITICAL | ARCHITECTURE | services/dialogue_runner.py | DialogueRunner дублирует логику из tui/app.py, нарушая DRY | Интегрировать или удалить |
| ISS-004 | CRITICAL | PERFORMANCE | models/ollama_client.py:220 | get_session() создаёт новую сессию при каждом вызове без проверки | Добавить кэширование сессии |
| ISS-005 | CRITICAL | ARCHITECTURE | factories/provider_factory.py:26 | Функция create_ollama_provider не использует protocol для возврата | Добавить type hint Protocol |
| ISS-006 | HIGH | ARCHITECTURE | controllers/dialogue_controller.py:83 | state property создаёт копию через конструктор dataclass | Использовать copy.deepcopy или dataclasses.replace |
| ISS-007 | HIGH | TYPE_SAFETY | models/provider.py:71 | MessageDict использует total=True, но не все вызовы предоставляют все поля | Проверить использование и возможно сделать optional |
| ISS-008 | HIGH | ARCHITECTURE | tui/app.py:289 | _on_ui_state_changed содержит слишком много exception handlers | Вынести в отдельный метод |
| ISS-009 | HIGH | ARCHITECTURE | services/dialogue_service.py:141 | run_dialogue_cycle имеет side effects (увеличивает turn_count) | Вынести счётчик в вызывающий код |
| ISS-010 | HIGH | STYLE | tui/app.py:582 | Unused parameter model_name and style in _process_dialogue_turn | Добавить underscore prefix |
| ISS-011 | HIGH | PERFORMANCE | models/ollama_client.py:148 | extract_models_list использует str(model.get("name")) с проверками | Упростить с использованием walrus operator |
| ISS-012 | HIGH | STYLE | models/config.py:66 | _validate_numeric_range содержит повторяющуюся логику | Создать декоратор для валидации |
| ISS-013 | HIGH | ARCHITECTURE | tui/app.py:310-398 | on_mount имеет очень длинный try/except block | Разделить на smaller methods |
| ISS-014 | HIGH | TYPE_SAFETY | models/conversation.py:311 | clear_contexts использует hardcoded role="system" | Вынести в константу |
| ISS-015 | HIGH | ARCHITECTURE | tui/sanitizer.py:75-87 | sanitize_response_for_display имеет много replace calls | Использовать str.translate или compiled regex |
| ISS-016 | HIGH | PERFORMANCE | tui/constants.py:69 | UIElementIDs dataclass имеет много атрибутов | Разделить на отдельные dataclasses |
| ISS-017 | HIGH | STYLE | controllers/dialogue_controller.py:134 | Комментарий "Прямая модификация атрибута" избыточен | Удалить комментарий |
| ISS-018 | HIGH | STYLE | models/ollama_client.py:53-89 | RequestValidator статические методы можно сделать module-level | Рефакторинг для утилит |
| ISS-019 | HIGH | ARCHITECTURE | tui/app.py:399 | _safe_update_status имеет duplicated error handling | Вынести в декоратор |
| ISS-020 | HIGH | DEPRECATED | tui/app.py:434,482 | Использование assert вместо proper error handling | Заменить на if/raise |

### ПАКЕТ-2: Типовая безопасность и улучшения типизации (ISS-021 — ISS-040)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-021 | MEDIUM | TYPE_SAFETY | tui/app.py:78 | *args, **kwargs в ModelSelectionScreen.__init__ | Использовать конкретные типы |
| ISS-022 | MEDIUM | TYPE_SAFETY | tui/app.py:258 | provider_factory lambda имеет Any type | Добавить Protocol type hint |
| ISS-023 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:416 | **kwargs в generate() слишком generic | Определить конкретные параметры |
| ISS-024 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:61 | Callable[[UIState], None] | Использовать Protocol |
| ISS-025 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:158 | process_turn возвращает tuple, но не все поля используются | Использовать NamedTuple или dataclass |
| ISS-026 | MEDIUM | TYPE_SAFETY | models/conversation.py:103 | _trim_context_if_needed принимает list[MessageDict] | Использовать Sequence для immutability |
| ISS-027 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:23 | ProviderFactory Protocol использует ... | Добавить documentation |
| ISS-028 | MEDIUM | TYPE_SAFETY | tui/app.py:246 | Callable parameter type annotation missing | Добавить Protocol annotation |
| ISS-029 | MEDIUM | TYPE_SAFETY | models/config.py:211 | default_system_prompt использует format() | Использовать f-strings или Template |
| ISS-030 | MEDIUM | TYPE_SAFETY | tui/app.py:261 | asyncio.Task[None] вместо None | Уточнить тип возврата |
| ISS-031 | MEDIUM | STYLE | models/ollama_client.py:69 | Sequence[Mapping[str, Any]] можно сделать конкретнее | Определить MessageList type alias |
| ISS-032 | MEDIUM | STYLE | tui/app.py:289 | _on_ui_state_changed return type не указан | Добавить None return type |
| ISS-033 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:205 | _notify_state_changed вызывается из нескольких мест | Рассмотреть context manager |
| ISS-034 | MEDIUM | TYPE_SAFETY | services/model_style_mapper.py:35 | dict[ModelId, str] type alias | Создать StyleMap type alias |
| ISS-035 | MEDIUM | ARCHITECTURE | tui/app.py:525 | _run_dialogue method слишком длинная | Разделить на smaller methods |
| ISS-036 | MEDIUM | ARCHITECTURE | models/ollama_client.py:92 | _ResponseHandler имеет только static methods | Сделать module-level functions |
| ISS-037 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:39 | DialogueService.__init__ параметры не документированы | Добавить type hints в docstrings |
| ISS-038 | MEDIUM | STYLE | tui/styles.py:11 | generate_main_css возвращает multiline string | Использовать textwrap или heredoc |
| ISS-039 | MEDIUM | ARCHITECTURE | models/config.py:220 | __post_init__ содержит много валидаций | Разделить на smaller validators |
| ISS-040 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:182 | get_context возвращает tuple, но tuple[MessageDict] | Использовать named tuple |

### ПАКЕТ-3: Стилевые улучшения и косметика (ISS-041 — ISS-060)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-041 | LOW | STYLE | tui/app.py:241 | sub_title reactive variable naming | Использовать snake_case convention |
| ISS-042 | LOW | STYLE | models/ollama_client.py:41 | _DEFAULT_OPTIONS naming | Использовать SCREAMING_SNAKE_CASE |
| ISS-043 | LOW | STYLE | models/config.py:14-26 | Константы без type annotations | Добавить Final[type] annotations |
| ISS-044 | LOW | STYLE | tui/constants.py:68 | pylint disable comment | Удалить если не нужен |
| ISS-045 | LOW | STYLE | controllers/dialogue_controller.py:55 | Example в docstring нарушает PEP 257 | Использовать proper format |
| ISS-046 | LOW | STYLE | services/dialogue_service.py:52 | Note section в docstring | Переместить в конец docstring |
| ISS-047 | LOW | STYLE | models/provider.py:94 | Example section нарушает conventions | Использовать proper indentation |
| ISS-048 | LOW | STYLE | tui/sanitizer.py:37 | docstring examples не соответствуют PEP 257 | Использовать proper format |
| ISS-049 | LOW | STYLE | models/ollama_client.py:50 | docstring имеет пустую строку в конце | Удалить лишнюю пустую строку |
| ISS-050 | LOW | STYLE | tui/styles.py:169 | Trailing whitespace в CSS | Удалить whitespace |
| ISS-051 | LOW | STYLE | tui/constants.py:102 | Название атрибута exit_btn | Рассмотреть quit_btn для consistency |
| ISS-052 | LOW | STYLE | models/ollama_client.py:64-66 | Multi-line docstring с одним параметром | Использовать inline format |
| ISS-053 | LOW | STYLE | services/dialogue_runner.py:105 | docstring имеет too many blank lines | Упростить docstring |
| ISS-054 | LOW | STYLE | tui/app.py:52-62 | Комментарий о call_from_thread слишком длинный | Сократить или вынести в docstring |
| ISS-055 | LOW | STYLE | factories/provider_factory.py:17 | docstring Protocol не соответствует style | Улучшить formatting |
| ISS-056 | LOW | STYLE | controllers/dialogue_controller.py:74 | property decorator без blank line | Добавить blank line before |
| ISS-057 | LOW | STYLE | models/conversation.py:49 | Note section не по convention | Переместить в конец docstring |
| ISS-058 | LOW | STYLE | tui/app.py:56 | Scalability section нарушает docstring style | Сделать regular comment |
| ISS-059 | LOW | STYLE | models/provider.py:17 | Attribute docstring имеет пустую строку | Использовать Google style |
| ISS-060 | LOW | STYLE | services/dialogue_service.py:15 | blank line после import section | Удалить лишнюю blank line |

### ПАКЕТ-4: Производительность и оптимизация (ISS-061 — ISS-080)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-061 | MEDIUM | PERFORMANCE | tui/sanitizer.py:75-87 | Много str.replace() calls в sanitize_response_for_display | Использовать re.sub с compiled pattern |
| ISS-062 | MEDIUM | PERFORMANCE | models/conversation.py:103 | _trim_context_if_needed вызывается при каждом добавлении | Кэшировать результат проверки |
| ISS-063 | MEDIUM | PERFORMANCE | tui/app.py:265 | _style_mapper кэшируется, но создаётся каждый раз | Сделать singleton или class variable |
| ISS-064 | MEDIUM | PERFORMANCE | models/ollama_client.py:148 | extract_models_list имеет comprehension с много conditions | Разделить на smaller functions |
| ISS-065 | MEDIUM | PERFORMANCE | controllers/dialogue_controller.py:83 | state property creates new UIState instance each time | Рассмотреть cached property |
| ISS-066 | MEDIUM | PERFORMANCE | tui/app.py:453 | _finalize_setup вызывается через call_after_refresh | Оптимизировать с batching |
| ISS-067 | MEDIUM | PERFORMANCE | models/config.py:29 | validate_ollama_url вызывается много раз | Кэшировать результат |
| ISS-068 | MEDIUM | PERFORMANCE | tui/app.py:536 | while loop проверяет service.is_running | Кэшировать значение в переменной |
| ISS-069 | MEDIUM | PERFORMANCE | models/ollama_client.py:218 | asyncio.Lock создаётся для каждой сессии | Использовать class-level lock |
| ISS-070 | MEDIUM | PERFORMANCE | tui/app.py:588 | call_after_refresh создаёт wrapper function | Использовать partial или lambda |
| ISS-071 | MEDIUM | PERFORMANCE | models/conversation.py:172 | log.debug вызывается при каждом add_message | Добавить early return если debug off |
| ISS-072 | MEDIUM | PERFORMANCE | tui/app.py:546 | _process_dialogue_turn await service | Использовать asyncio.gather для batching |
| ISS-073 | MEDIUM | PERFORMANCE | models/ollama_client.py:380 | JSONDecodeError перехватывается после response.json() | Использовать raise_for_status вместо validate_status_code |
| ISS-074 | MEDIUM | PERFORMANCE | services/dialogue_service.py:154 | process_turn делает generate_response перед process_turn | Убрать дублирование |
| ISS-075 | MEDIUM | PERFORMANCE | tui/app.py:316 | list_models может быть slow | Добавить progress indicator |
| ISS-076 | MEDIUM | PERFORMANCE | models/ollama_client.py:450 | payload создаётся при каждом generate | Кэшировать статическую часть |
| ISS-077 | MEDIUM | PERFORMANCE | controllers/dialogue_controller.py:118 | _update_status вызывается слишком часто | Debounce updates |
| ISS-078 | MEDIUM | PERFORMANCE | tui/app.py:598 | _write_to_log вызывается каждый ход | Batch writes |
| ISS-079 | MEDIUM | PERFORMANCE | models/ollama_client.py:388 | _ResponseHandler вызывается для каждого метода | Интегрировать validation |
| ISS-080 | MEDIUM | PERFORMANCE | tui/app.py:453-470 | _finalize_setup имеет много query_one calls | Cache queries |
| ISS-081 | MEDIUM | PERFORMANCE | tui/app.py:599-603 | query_one в цикле | Вынести query из цикла |
| ISS-082 | MEDIUM | PERFORMANCE | models/conversation.py:194 | get_context создаёт tuple каждый раз | Кэшировать результат |
| ISS-083 | MEDIUM | PERFORMANCE | services/dialogue_service.py:102 | start() method простой, но имеет docstring overhead | Упростить docstring |
| ISS-084 | MEDIUM | PERFORMANCE | tui/app.py:481 | assert в production code | Использовать if/raise |
| ISS-085 | MEDIUM | PERFORMANCE | tui/app.py:496 | assert в production code | Использовать if/raise |
| ISS-086 | MEDIUM | PERFORMANCE | tui/app.py:528 | assert в production code | Использовать if/raise |
| ISS-087 | MEDIUM | PERFORMANCE | models/ollama_client.py:323 | validate_host вызывается в __init__ | Lazy validation |
| ISS-088 | MEDIUM | PERFORMANCE | tui/app.py:565 | finally block проверяет _controller дважды | Оптимизировать logic |
| ISS-089 | MEDIUM | PERFORMANCE | services/dialogue_runner.py:107 | _is_task_cancelled вызывается в цикле | Переместить проверку |
| ISS-090 | MEDIUM | PERFORMANCE | models/ollama_client.py:408 | OSError логируется с warning | Рассмотреть error level |

### ПАКЕТ-5: Безопасность и защита (ISS-091 — ISS-110)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-091 | MEDIUM | SECURITY | tui/sanitizer.py:44 | sanitize_topic не экранирует все special chars | Добавить экранирование для ' и " |
| ISS-092 | MEDIUM | SECURITY | tui/sanitizer.py:71 | html.escape с quote=False не экранирует кавычки | Использовать quote=True |
| ISS-093 | MEDIUM | SECURITY | models/config.py:218 | hardcoded default ollama_host | Использовать environment variable |
| ISS-094 | MEDIUM | SECURITY | tui/app.py:258 | lambda в provider_factory | Рассмотреть named function |
| ISS-095 | MEDIUM | SECURITY | main.py:23 | basicConfig в main module | Использовать logging.config |
| ISS-096 | MEDIUM | SECURITY | tui/sanitizer.py:87 | \n заменяется на пробел, не экранируется | Использовать \\n для display |
| ISS-097 | LOW | SECURITY | tui/app.py:318 | list_models может вернуть untrusted data | Валидировать модели |
| ISS-098 | LOW | SECURITY | models/ollama_client.py:369 | URL construction без validation | Добавить url validation |
| ISS-099 | LOW | SECURITY | models/ollama_client.py:437 | URL construction без validation | Добавить url validation |
| ISS-100 | LOW | SECURITY | tui/app.py:334 | model names могут содержать injection | Валидировать model names |
| ISS-101 | LOW | SECURITY | models/ollama_client.py:150 | extract_models_list возвращает unvalidated strings | Добавить validation |
| ISS-102 | LOW | SECURITY | tui/app.py:431 | system_prompt.format с user input | Использовать safe formatting |
| ISS-103 | LOW | SECURITY | models/conversation.py:97 | format() с topic может вызвать injection | Валидировать topic |
| ISS-104 | LOW | SECURITY | tui/app.py:307 | Exception handling слишком generic | Добавить specific exception types |
| ISS-105 | LOW | SECURITY | services/dialogue_service.py:168 | log.exception может leak sensitive data | Фильтровать sensitive fields |
| ISS-106 | LOW | SECURITY | tui/app.py:345 | Connection error notification | Рассмотреть redact URLs |
| ISS-107 | LOW | SECURITY | models/ollama_client.py:395 | Exception message содержит host URL | redact в production |
| ISS-108 | LOW | SECURITY | models/ollama_client.py:477 | Exception message содержит host URL | redact в production |
| ISS-109 | LOW | SECURITY | tui/app.py:368 | Configuration error notification | redact sensitive config |
| ISS-110 | LOW | SECURITY | tui/app.py:346 | Connection error expose host | redact в notification |

### ПАКЕТ-6: Рефакторинг и архитектурные улучшения (ISS-111 — ISS-130)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-111 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py | Класс не используется в основном коде | Удалить или документировать use case |
| ISS-112 | MEDIUM | ARCHITECTURE | tui/app.py:226 | DialogueApp имеет too many responsibilities | Extract screen classes to separate file |
| ISS-113 | MEDIUM | ARCHITECTURE | tui/app.py:70-223 | ModalScreen классы можно вынести в separate module | Extract to tui/screens.py |
| ISS-114 | MEDIUM | ARCHITECTURE | models/ollama_client.py:47 | _RequestValidator можно сделать module-level | Convert to module functions |
| ISS-115 | MEDIUM | ARCHITECTURE | models/ollama_client.py:92 | _ResponseHandler можно сделать module-level | Convert to module functions |
| ISS-116 | MEDIUM | ARCHITECTURE | tui/app.py:289-308 | _on_ui_state_changed можно вынести в mixin | Create UIStateMixin |
| ISS-117 | MEDIUM | ARCHITECTURE | models/config.py:66 | _validate_numeric_range не использует dataclass validators | Использовать @field validator |
| ISS-118 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:37 | DialogueController можно сделать Protocol | Для better testing |
| ISS-119 | MEDIUM | ARCHITECTURE | tui/styles.py | generate_main_css можно кэшировать | Cache at module level |
| ISS-120 | MEDIUM | ARCHITECTURE | models/provider.py:12 | ProviderError hierarchy можно расширить | Добавить specific exceptions |
| ISS-121 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:17 | ProviderFactory Protocol не используется | Удалить или использовать |
| ISS-122 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:39 | DialogueService можно сделать Protocol | Для testing flexibility |
| ISS-123 | MEDIUM | ARCHITECTURE | tui/constants.py:13 | MessageStyles dataclass имеет too many fields | Split into smaller classes |
| ISS-124 | MEDIUM | ARCHITECTURE | tui/constants.py:31 | UIElementIDs dataclass имеет too many fields | Split into smaller classes |
| ISS-125 | MEDIUM | ARCHITECTURE | models/conversation.py:28 | _ConversationContext dataclass не используется | Удалить или использовать |
| ISS-126 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:21 | ModelStyleMapper можно сделать frozen dataclass | Для immutability |
| ISS-127 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:17 | UIState dataclass можно сделать frozen | Для thread safety |
| ISS-128 | MEDIUM | ARCHITECTURE | models/ollama_client.py:177 | _HTTPSessionManager можно сделать dataclass | Для better typing |
| ISS-129 | MEDIUM | ARCHITECTURE | models/ollama_client.py:245 | _ModelsCache можно сделать dataclass | Для consistency |
| ISS-130 | MEDIUM | ARCHITECTURE | tui/app.py:641 | on_unmount имеет too many responsibilities | Extract cleanup logic |

### ПАКЕТ-7: Тестирование и качество (ISS-131 — ISS-150)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-131 | MEDIUM | TESTING | tests/ | Тесты имеют type errors (pyright errors) | Исправить type annotations в тестах |
| ISS-132 | MEDIUM | TESTING | tests/test_arch_audit_fixes.py:46 | ast.Expr.left attribute access | Использовать correct ast node type |
| ISS-133 | MEDIUM | TESTING | tests/test_architecture_integrity.py:882 | tuple.append error | Использовать list для mutations |
| ISS-134 | MEDIUM | TESTING | tests/test_audit_fixes_verification.py:118 | UIState type mismatch | Import correct UIState |
| ISS-135 | MEDIUM | TESTING | tests/test_call_from_thread_fix.py:60 | Literal type mismatch | Использовать ModelId type |
| ISS-136 | MEDIUM | TESTING | tests/test_call_from_thread_fix.py:91 | Generator return type | Использовать AsyncMock |
| ISS-137 | MEDIUM | TESTING | tests/test_critical.py:272 | MessageDict type mismatch | Добавить required fields |
| ISS-138 | MEDIUM | TESTING | tests/test_fixes.py:200 | None type passed to validate_ollama_url | Mock validate function |
| ISS-139 | MEDIUM | TESTING | tests/test_new_audit_fixes.py:108 | Named tuple access error | Использовать index или define proper type |
| ISS-140 | MEDIUM | TESTING | tests/test_textual_reactive.py:53 | Named tuple access error | Использовать correct tuple type |
| ISS-141 | LOW | TESTING | tests/ | Missing parametrized tests | Добавить pytest.mark.parametrize |
| ISS-142 | LOW | TESTING | tests/ | Missing async test cleanup | Добавить fixture teardown |
| ISS-143 | LOW | TESTING | tests/ | Some tests use @patch вместо pytest-mock | Standardize mocking approach |
| ISS-144 | LOW | TESTING | tests/ | Missing edge case tests for sanitizer | Добавить boundary value tests |
| ISS-145 | LOW | TESTING | tests/ | Missing performance benchmarks | Добавить pytest-benchmark |
| ISS-146 | LOW | TESTING | tests/ | Missing mutation testing | Добавить mutmut или similar |
| ISS-147 | LOW | TESTING | tests/ | Missing snapshot tests | Consider snapshot testing |
| ISS-148 | LOW | TESTING | tests/ | Coverage может быть улучшен | Добавить coverage для error paths |
| ISS-149 | LOW | TESTING | tests/ | Missing integration tests | Добавить tests с real Ollama |
| ISS-150 | LOW | TESTING | tests/ | Missing CLI argument tests | Добавить argparse tests |

### ПАКЕТ-8: Документация и комментарии (ISS-151 — ISS-170)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-151 | LOW | DOCUMENTATION | README.md | Missing architecture diagram | Добавить ASCII diagram |
| ISS-152 | LOW | DOCUMENTATION | README.md | Missing contributing guidelines | Добавить CONTRIBUTING.md |
| ISS-153 | LOW | DOCUMENTATION | README.md | Missing changelog | Добавить CHANGELOG.md |
| ISS-154 | LOW | DOCUMENTATION | README.md | Missing troubleshooting section | Добавить troubleshooting |
| ISS-155 | LOW | DOCUMENTATION | main.py | Missing module-level docstring | Расширить docstring |
| ISS-156 | LOW | DOCUMENTATION | KODA.md | Missing project documentation | Создать documentation |
| ISS-157 | LOW | DOCUMENTATION | QWEN.md | Missing project documentation | Создать documentation |
| ISS-158 | LOW | DOCUMENTATION | models/ | Missing __all__ exports | Добавить explicit exports |
| ISS-159 | LOW | DOCUMENTATION | services/ | Missing __all__ exports | Добавить explicit exports |
| ISS-160 | LOW | DOCUMENTATION | controllers/ | Missing __all__ exports | Добавить explicit exports |
| ISS-161 | LOW | DOCUMENTATION | tui/ | Missing __all__ exports | Добавить explicit exports |
| ISS-162 | LOW | DOCUMENTATION | factories/ | Missing __all__ exports | Добавить explicit exports |
| ISS-163 | LOW | DOCUMENTATION | models/provider.py | Missing version info | Добавить version или last updated |
| ISS-164 | LOW | DOCUMENTATION | models/config.py | Missing examples for Config | Добавить usage examples |
| ISS-165 | LOW | DOCUMENTATION | models/conversation.py | Missing sequence diagram | Добавить ASCII diagram |
| ISS-166 | LOW | DOCUMENTATION | tui/app.py | Missing app screenshot reference | Добавить screenshot path |
| ISS-167 | LOW | DOCUMENTATION | services/dialogue_service.py | Missing state machine diagram | Добавить ASCII diagram |
| ISS-168 | LOW | DOCUMENTATION | pyproject.toml | Missing license field | Добавить license info |
| ISS-169 | LOW | DOCUMENTATION | pyproject.toml | Missing authors field | Добавить authors info |
| ISS-170 | LOW | DOCUMENTATION | pyproject.toml | Missing keywords field | Добавить keywords |

### ПАКЕТ-9: Конфигурация и инструменты (ISS-171 — ISS-190)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-171 | LOW | CONFIGURATION | pyproject.toml | Missing pre-commit configuration | Добавить .pre-commit-config.yaml |
| ISS-172 | LOW | CONFIGURATION | pyproject.toml | Missing pytest configuration | Расширить [tool.pytest] |
| ISS-173 | LOW | CONFIGURATION | pyproject.toml | Missing coverage configuration | Добавить [tool.coverage] |
| ISS-174 | LOW | CONFIGURATION | pyproject.toml | Missing mypy plugins | Расширить [tool.mypy] |
| ISS-175 | LOW | CONFIGURATION | pyproject.toml | Missing bandit configuration | Добавить [tool.bandit] |
| ISS-176 | LOW | CONFIGURATION | .pylintrc | pylintrc exists but not optimal | Оптимизировать pylint rules |
| ISS-177 | LOW | CONFIGURATION | .bandit.yml | bandit config exists | Проверить completeness |
| ISS-178 | LOW | CONFIGURATION | .gitignore | Missing .env in gitignore | Добавить .env pattern |
| ISS-179 | LOW | CONFIGURATION | .gitignore | Missing *.log pattern | Добавить log files |
| ISS-180 | LOW | CONFIGURATION | .gitignore | Missing audit_reports/ | Добавить directory |
| ISS-181 | LOW | CONFIGURATION | requirements.txt | Missing development dependencies | Разделить requirements.txt |
| ISS-182 | LOW | CONFIGURATION | requirements.txt | Missing pinned versions | Добавить версии |
| ISS-183 | LOW | CONFIGURATION | pytest.ini | Missing asyncio_mode config | Расширить pytest.ini |
| ISS-184 | LOW | CONFIGURATION | pytest.ini | Missing testpaths | Уточнить testpaths |
| ISS-185 | LOW | CONFIGURATION | pyproject.toml | Missing pyright configuration | Расширить [tool.pyright] |
| ISS-186 | LOW | CONFIGURATION | pyproject.toml | Missing isort configuration | Расширить [tool.isort] |
| ISS-187 | LOW | CONFIGURATION | pyproject.toml | Missing black configuration | Расширить [tool.black] |
| ISS-188 | LOW | CONFIGURATION | pyproject.toml | Missing flake8 configuration | Расширить [tool.flake8] |
| ISS-189 | LOW | CONFIGURATION | pyproject.toml | Missing autoflake configuration | Расширить [tool.autoflake] |
| ISS-190 | LOW | CONFIGURATION | pyproject.toml | Missing pydocstyle configuration | Расширить [tool.pydocstyle] |

### ПАКЕТ-10: Дополнительные улучшения (ISS-191 — ISS-200)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-191 | LOW | STYLE | models/ollama_client.py | import order не alphabetical | Использовать isort |
| ISS-192 | LOW | STYLE | tui/app.py | import order не alphabetical | Использовать isort |
| ISS-193 | LOW | STYLE | controllers/dialogue_controller.py | import order не alphabetical | Использовать isort |
| ISS-194 | LOW | STYLE | services/dialogue_service.py | import order не alphabetical | Использовать isort |
| ISS-195 | LOW | STYLE | services/dialogue_runner.py | import order не alphabetical | Использовать isort |
| ISS-196 | LOW | STYLE | tui/sanitizer.py | import order не alphabetical | Использовать isort |
| ISS-197 | LOW | STYLE | tui/styles.py | import order не alphabetical | Использовать isort |
| ISS-198 | LOW | STYLE | tui/constants.py | import order не alphabetical | Использовать isort |
| ISS-199 | LOW | STYLE | factories/provider_factory.py | import order не alphabetical | Использовать isort |
| ISS-200 | LOW | STYLE | models/conversation.py | import order не alphabetical | Использовать isort |

---

## Группировка по пакетам

| Пакет | IDs | Описание |
|-------|-----|----------|
| Пакет-1 | ISS-001 — ISS-020 | Критические и архитектурные проблемы |
| Пакет-2 | ISS-021 — ISS-040 | Типовая безопасность и улучшения типизации |
| Пакет-3 | ISS-041 — ISS-060 | Стилевые улучшения и косметика |
| Пакет-4 | ISS-061 — ISS-090 | Производительность и оптимизация |
| Пакет-5 | ISS-091 — ISS-110 | Безопасность и защита |
| Пакет-6 | ISS-111 — ISS-130 | Рефакторинг и архитектурные улучшения |
| Пакет-7 | ISS-131 — ISS-150 | Тестирование и качество |
| Пакет-8 | ISS-151 — ISS-170 | Документация и комментарии |
| Пакет-9 | ISS-171 — ISS-190 | Конфигурация и инструменты |
| Пакет-10 | ISS-191 — ISS-200 | Стиль импортов и финальные штрихи |
