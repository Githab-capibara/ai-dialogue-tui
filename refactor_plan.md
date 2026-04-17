# Рефакторинг: Реестр проблем (Issue Register)

## Сводная статистика аудита

| Категория | CRITICAL | HIGH | MEDIUM | LOW | Всего |
|-----------|-----------|------|--------|-----|-------|
| STYLE | 0 | 0 | 45 | 80 | 125 |
| TYPE_SAFETY | 0 | 5 | 15 | 10 | 30 |
| ARCHITECTURE | 0 | 3 | 12 | 5 | 20 |
| DEPRECATED | 0 | 2 | 8 | 0 | 10 |
| UNUSED | 0 | 0 | 5 | 5 | 10 |
| SECURITY | 0 | 0 | 3 | 2 | 5 |
| **ИТОГО** | **0** | **10** | **88** | **102** | **200** |

---

## Полный реестр проблем (ISS-001 ... ISS-200)

### ПАКЕТ-1: Критичные и высокоприоритетные проблемы (ISS-001 ... ISS-020)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | HIGH | TYPE_SAFETY | models/conversation.py:57 | Использование Config() в default_factory dataclass создаёт побочный эффект и не thread-safe | Использовать None и инициализировать в __post_init__ или передавать через __init__ |
| ISS-002 | HIGH | TYPE_SAFETY | models/conversation.py:47-64 | Превышен лимит атрибутов dataclass (8 > 7) | Рассмотреть выделение части атрибутов в отдельный dataclass |
| ISS-003 | HIGH | TYPE_SAFETY | tui/app.py:311-320 | Перехват слишком широких исключений (LookupError, RuntimeError, ScreenStackError) | Перехватывать конкретные NoMatches, LookupError отдельно |
| ISS-004 | HIGH | TYPE_SAFETY | tui/app.py:395 | asyncio.TimeoutError перехватывается с псевдонимом 'e', но 'e' не используется | Убрать 'as e' или использовать переменную |
| ISS-005 | HIGH | ARCHITECTURE | services/dialogue_runner.py:72 | Создание asyncio.Task без проверки текущего loop | Добавить проверку или использовать asyncio.get_running_loop() |
| ISS-006 | MEDIUM | ARCHITECTURE | models/ollama_client.py:333 | Комментарий "# Компоненты для обработки запросов (используем класс напрямую)" без кода | Удалить мёртвый комментарий |
| ISS-007 | MEDIUM | TYPE_SAFETY | tui/app.py:458 | Type ignore для provider без проверки совместимости | Добавить TYPE_CHECKING guard или runtime_checkable |
| ISS-008 | MEDIUM | STYLE | main.py:37 | Docstring Note превышает 79 символов | Разбить на несколько строк |
| ISS-009 | MEDIUM | STYLE | models/config.py:91,93 | ValueError сообщения превышают 79 символов | Использовать f-строки с разбивкой |
| ISS-010 | MEDIUM | STYLE | models/conversation.py:34,86,89,90,139 | Docstring строки превышают 79 символов | Переформатировать docstrings |
| ISS-011 | MEDIUM | STYLE | models/ollama_client.py:80,310,377,408,410,461,489 | Docstring и комментарии превышают 79 символов | Переформатировать |
| ISS-012 | MEDIUM | STYLE | models/provider.py:98,104 | Docstring Example превышает 79 символов | Разбить пример на несколько строк |
| ISS-013 | MEDIUM | STYLE | services/dialogue_runner.py:72,113 | Docstring и комментарии превышают 79 символов | Переформатировать |
| ISS-014 | MEDIUM | STYLE | services/dialogue_service.py:41,150,159 | Docstring строки превышают 79 символов | Переформатировать |
| ISS-015 | MEDIUM | STYLE | tui/app.py:55-68,98,118,193,197,198,265,297-300,314,360,469,471,489,524,528,603,604,611,614,629,637,641 | Множественные docstring и комментарии превышают 79 символов | Переформатировать |
| ISS-016 | MEDIUM | STYLE | tui/sanitizer.py:38 | Docstring превышает 79 символов | Разбить на несколько строк |
| ISS-017 | MEDIUM | STYLE | controllers/dialogue_controller.py:46 | Docstring превышает 79 символов | Переформатировать |
| ISS-018 | MEDIUM | ARCHITECTURE | audit_reports/run_analysis.py:6 | Неиспользуемый импорт 'os' | Удалить неиспользуемый импорт |
| ISS-019 | MEDIUM | DEPRECATED | models/ollama_client.py:11 | Использование typing.Any без TYPE_CHECKING guard | Обернуть в TYPE_CHECKING для импортов |
| ISS-020 | MEDIUM | DEPRECATED | models/conversation.py:11 | Использование typing.Literal без TYPE_CHECKING guard | Обернуть в TYPE_CHECKING |

---

### ПАКЕТ-2: Типизация и архитектурные паттерны (ISS-021 ... ISS-040)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-021 | MEDIUM | TYPE_SAFETY | tui/app.py:51-72 | Большой блок комментариев о call_from_thread vs call_after_refresh | Вынести в документацию или упростить |
| ISS-022 | MEDIUM | ARCHITECTURE | tui/app.py:75 | CSS генерируется при импорте модуля, может быть вынесено | Рассмотреть отложенную генерацию |
| ISS-023 | MEDIUM | ARCHITECTURE | models/ollama_client.py:31-35 | _DEFAULT_OPTIONS создаётся каждый раз при импорте | Вынести на уровень модуля вне класса |
| ISS-024 | MEDIUM | ARCHITECTURE | models/ollama_client.py:186-192 | Scalability Note в docstring без реализации | Добавить TODO или реализовать |
| ISS-025 | MEDIUM | ARCHITECTURE | models/conversation.py:43-45 | Note о превышении лимита атрибутов без action items | Добавить план рефакторинга |
| ISS-026 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:48 | Тип asyncio.Task[None] не аннотирован return type | Добавить -> None |
| ISS-027 | MEDIUM | TYPE_SAFETY | tui/app.py:274 | _dialogue_task не инициализирован в __init__ | Инициализировать None |
| ISS-028 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:131,163,174,190 | Прямая модификация _state атрибутов | Использовать иммутабельный подход |
| ISS-029 | MEDIUM | TYPE_SAFETY | models/provider.py:24-25 | ProviderError.__init__ не использует typing.Self | Добавить Self для future-proofing |
| ISS-030 | MEDIUM | TYPE_SAFETY | tui/app.py:276-277 | _style_mapper кэшируется, но используется только один раз | Убрать кэширование или использовать повторно |
| ISS-031 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:211 | Тип aiohttp.ClientSession | Добавить импорт из aiohttp |
| ISS-032 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:18-33 | DialogueTurnResult dataclass без slots | Добавить slots=True |
| ISS-033 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:36-180 | DialogueService dataclass без slots | Добавить slots=True |
| ISS-034 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:14-31 | UIState dataclass без slots | Добавить slots=True |
| ISS-035 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:69-71 | Мутабельные атрибуты _is_running, _is_paused, _turn_count | Использовать @property для состояния |
| ISS-036 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:15 | ProviderFactory Protocol без документации | Добавить docstring |
| ISS-037 | MEDIUM | ARCHITECTURE | models/config.py:186-236 | Config dataclass имеет сложную __post_init__ логику | Вынести валидацию в отдельные функции |
| ISS-038 | MEDIUM | ARCHITECTURE | models/ollama_client.py:41-298 | Вспомогательные классы (_RequestValidator и др.) не имеют тестов | Добавить unit-тесты |
| ISS-039 | MEDIUM | ARCHITECTURE | tui/app.py:467-489 | _finalize_setup вложенная функция без type hints | Добавить type hints |
| ISS-040 | MEDIUM | ARCHITECTURE | tui/app.py:343-355 | on_models_selected вложенная функция без type hints | Добавить type hints |

---

### ПАКЕТ-3: Устаревшие конструкции и зависимости (ISS-041 ... ISS-060)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-041 | HIGH | DEPRECATED | models/provider.py:92 | @runtime_checkable на ModelProvider | Проверить необходимость runtime проверки |
| ISS-042 | HIGH | DEPRECATED | main.py:29 | pylint disable too-many-return-statements | Рефакторить функцию main для уменьшения return |
| ISS-043 | MEDIUM | DEPRECATED | models/conversation.py:47 | pylint disable too-many-instance-attributes | Рассмотреть выделение в отдельный класс |
| ISS-044 | MEDIUM | DEPRECATED | tui/app.py:237 | pylint disable too-many-instance-attributes | Рассмотреть выделение в отдельный класс |
| ISS-045 | MEDIUM | DEPRECATED | controllers/dialogue_controller.py | pylint disable в нескольких местах | Устранить причины suppressions |
| ISS-046 | MEDIUM | DEPRECATED | tui/app.py:595 | pylint disable unused-argument | Убрать неиспользуемые параметры или использовать |
| ISS-047 | MEDIUM | DEPRECATED | tui/app.py:421 | pylint disable assignment-from-no-return | Рефакторить метод _safe_update_status |
| ISS-048 | MEDIUM | DEPRECATED | factories/provider_factory.py:15 | pylint disable too-few-public-methods | Document Protocol usage |
| ISS-049 | LOW | DEPRECATED | tui/app.py:343 | Lambda без type hints | Добавить type hints |
| ISS-050 | LOW | DEPRECATED | tui/app.py:436 | Lambda без type hints | Добавить type hints |
| ISS-051 | LOW | DEPRECATED | tui/app.py:468 | Nested function без type hints | Добавить type hints |
| ISS-052 | LOW | DEPRECATED | models/ollama_client.py:409-413 | OSError перехватывается с логированием | Рассмотреть более специфичную обработку |
| ISS-053 | LOW | DEPRECATED | models/ollama_client.py:490-494 | OSError перехватывается с логированием | Рассмотреть более специфичную обработку |
| ISS-054 | LOW | DEPRECATED | services/dialogue_runner.py:121-122 | except ProviderError: pass | Добавить логирование |
| ISS-055 | LOW | DEPRECATED | tui/app.py:580-582 | except ProviderError: pass | Добавить логирование |
| ISS-056 | LOW | DEPRECATED | audit_reports/run_analysis.py | Неиспользуемый код анализа | Удалить или использовать |
| ISS-057 | LOW | DEPRECATED | audit_reports/analyze_test.py | Тестовый файл в папке audit_reports | Переместить в tests/ |
| ISS-058 | LOW | DEPRECATED | audit_reports/run_analysis.py:55 | Строка превышает 79 символов | Переформатировать |
| ISS-059 | LOW | DEPRECATED | audit_reports/analyze_test.py:44,52,74,75 | Строки превышают 79 символов | Переформатировать |
| ISS-060 | LOW | DEPRECATED | audit_reports/run_analysis.py | Неиспользуемый os import | Удалить |

---

### ПАКЕТ-4: Стилевые проблемы - источники (ISS-061 ... ISS-080)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-061 | LOW | STYLE | main.py:37 | Line 37 превышает 79 символов | Разбить docstring |
| ISS-062 | LOW | STYLE | models/config.py:91 | "{param_name} должен быть >= {min_value}, получено {value}" превышает 79 | Разбить сообщение |
| ISS-063 | LOW | STYLE | models/config.py:93 | "{param_name} должен быть <= {max_value}, получено {value}" превышает 79 | Разбить сообщение |
| ISS-064 | LOW | STYLE | models/conversation.py:34 | Docstring превышает 79 символов | Переформатировать |
| ISS-065 | LOW | STYLE | models/conversation.py:57 | Docstring превышает 79 символов | Переформатировать |
| ISS-066 | LOW | STYLE | models/conversation.py:86 | Docstring превышает 79 символов | Переформатировать |
| ISS-067 | LOW | STYLE | models/conversation.py:89 | Docstring превышает 79 символов | Переформатировать |
| ISS-068 | LOW | STYLE | models/conversation.py:90 | Docstring превышает 79 символов | Переформатировать |
| ISS-069 | LOW | STYLE | models/conversation.py:139 | Docstring превышает 79 символов | Переформатировать |
| ISS-070 | LOW | STYLE | models/conversation.py:302 | Docstring превышает 79 символов | Переформатировать |
| ISS-071 | LOW | STYLE | models/conversation.py:305 | Docstring превышает 79 символов | Переформатировать |
| ISS-072 | LOW | STYLE | models/conversation.py:306 | Docstring превышает 79 символов | Переформатировать |
| ISS-073 | LOW | STYLE | models/ollama_client.py:80 | Docstring превышает 79 символов | Переформатировать |
| ISS-074 | LOW | STYLE | models/ollama_client.py:310 | Docstring превышает 79 символов | Переформатировать |
| ISS-075 | LOW | STYLE | models/ollama_client.py:377 | Docstring превышает 79 символов | Переформатировать |
| ISS-076 | LOW | STYLE | models/ollama_client.py:408 | Docstring превышает 79 символов | Переформатировать |
| ISS-077 | LOW | STYLE | models/ollama_client.py:410 | Docstring превышает 79 символов | Переформатировать |
| ISS-078 | LOW | STYLE | models/ollama_client.py:461 | Docstring превышает 79 символов | Переформатировать |
| ISS-079 | LOW | STYLE | models/ollama_client.py:489 | Docstring превышает 79 символов | Переформатировать |
| ISS-080 | LOW | STYLE | models/provider.py:98 | Docstring превышает 79 символов | Переформатировать |

---

### ПАКЕТ-5: Стилевые проблемы - tui модуль (ISS-081 ... ISS-100)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-081 | LOW | STYLE | tui/app.py:55 | Comment превышает 79 символов | Переформатировать |
| ISS-082 | LOW | STYLE | tui/app.py:56 | Comment превышает 79 символов | Переформатировать |
| ISS-083 | LOW | STYLE | tui/app.py:66 | Comment превышает 79 символов | Переформатировать |
| ISS-084 | LOW | STYLE | tui/app.py:67 | Comment превышает 79 символов | Переформатировать |
| ISS-085 | LOW | STYLE | tui/app.py:68 | Comment превышает 79 символов | Переформатировать |
| ISS-086 | LOW | STYLE | tui/app.py:98 | Comment превышает 79 символов | Переформатировать |
| ISS-087 | LOW | STYLE | tui/app.py:118 | Comment превышает 79 символов | Переформатировать |
| ISS-088 | LOW | STYLE | tui/app.py:193 | Comment превышает 79 символов | Переформатировать |
| ISS-089 | LOW | STYLE | tui/app.py:197 | Comment превышает 79 символов | Переформатировать |
| ISS-090 | LOW | STYLE | tui/app.py:198 | Comment превышает 79 символов | Переформатировать |
| ISS-091 | LOW | STYLE | tui/app.py:265 | Comment превышает 79 символов | Переформатировать |
| ISS-092 | LOW | STYLE | tui/app.py:297 | Comment превышает 79 символов | Переформатировать |
| ISS-093 | LOW | STYLE | tui/app.py:298 | Comment превышает 79 символов | Переформатировать |
| ISS-094 | LOW | STYLE | tui/app.py:299 | Comment превышает 79 символов | Переформатировать |
| ISS-095 | LOW | STYLE | tui/app.py:300 | Comment превышает 79 символов | Переформатировать |
| ISS-096 | LOW | STYLE | tui/app.py:314 | Comment превышает 79 символов | Переформатировать |
| ISS-097 | LOW | STYLE | tui/app.py:360 | Comment превышает 79 символов | Переформатировать |
| ISS-098 | LOW | STYLE | tui/app.py:469 | Comment превышает 79 символов | Переформатировать |
| ISS-099 | LOW | STYLE | tui/app.py:471 | Comment превышает 79 символов | Переформатировать |
| ISS-100 | LOW | STYLE | tui/app.py:489 | Comment превышает 79 символов | Переформатировать |

---

### ПАКЕТ-6: Стилевые проблемы - tui модуль (ISS-101 ... ISS-120)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-101 | LOW | STYLE | tui/app.py:524 | Comment превышает 79 символов | Переформатировать |
| ISS-102 | LOW | STYLE | tui/app.py:528 | Comment превышает 79 символов | Переформатировать |
| ISS-103 | LOW | STYLE | tui/app.py:603 | Comment превышает 79 символов | Переформатировать |
| ISS-104 | LOW | STYLE | tui/app.py:604 | Comment превышает 79 символов | Переформатировать |
| ISS-105 | LOW | STYLE | tui/app.py:611 | Comment превышает 79 символов | Переформатировать |
| ISS-106 | LOW | STYLE | tui/app.py:614 | Comment превышает 79 символов | Переформатировать |
| ISS-107 | LOW | STYLE | tui/app.py:629 | Comment превышает 79 символов | Переформатировать |
| ISS-108 | LOW | STYLE | tui/app.py:637 | Comment превышает 79 символов | Переформатировать |
| ISS-109 | LOW | STYLE | tui/app.py:641 | Comment превышает 79 символов | Переформатировать |
| ISS-110 | LOW | STYLE | tui/sanitizer.py:38 | Docstring превышает 79 символов | Переформатировать |
| ISS-111 | LOW | STYLE | controllers/dialogue_controller.py:46 | Docstring превышает 79 символов | Переформатировать |
| ISS-112 | LOW | STYLE | services/dialogue_runner.py:72 | Docstring превышает 79 символов | Переформатировать |
| ISS-113 | LOW | STYLE | services/dialogue_runner.py:113 | Docstring превышает 79 символов | Переформатировать |
| ISS-114 | LOW | STYLE | services/dialogue_service.py:41 | Docstring превышает 79 символов | Переформатировать |
| ISS-115 | LOW | STYLE | services/dialogue_service.py:150 | Docstring превышает 79 символов | Переформатировать |
| ISS-116 | LOW | STYLE | services/dialogue_service.py:159 | Docstring превышает 79 символов | Переформатировать |

---

### ПАКЕТ-7: Неиспользуемый код и тестовые файлы (ISS-121 ... ISS-140)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-121 | LOW | UNUSED | audit_reports/ | Папка содержит неиспользуемые файлы анализа | Удалить или интегрировать |
| ISS-122 | LOW | UNUSED | audit_reports/run_analysis.py:6 | Неиспользуемый импорт os | Удалить импорт |
| ISS-123 | LOW | UNUSED | audit_reports/analyze_test.py | Тестовый файл в неправильном месте | Переместить в tests/ |
| ISS-124 | LOW | UNUSED | audit_reports/run_analysis.py:55 | Строка превышает 79 символов | Переформатировать |
| ISS-125 | LOW | UNUSED | audit_reports/analyze_test.py:44,52,74,75 | Строки превышают 79 символов | Переформатировать |
| ISS-126 | LOW | ARCHITECTURE | models/ollama_client.py:333 | Мёртвый комментарий | Удалить |
| ISS-127 | LOW | ARCHITECTURE | tui/app.py:51-72 | Избыточный комментарий о call_from_thread | Упростить |
| ISS-128 | LOW | ARCHITECTURE | models/conversation.py:43-45 | Note без action items | Добавить TODO или удалить |
| ISS-129 | LOW | ARCHITECTURE | models/ollama_client.py:186-192 | Scalability Note без реализации | Добавить TODO или реализовать |
| ISS-130 | LOW | ARCHITECTURE | factories/provider_factory.py:15 | Protocol без документации | Добавить docstring |
| ISS-131 | LOW | ARCHITECTURE | models/ollama_client.py:41-298 | Вспомогательные классы без тестов | Добавить unit-тесты |
| ISS-132 | LOW | ARCHITECTURE | tui/app.py:467-489 | Nested function без type hints | Добавить type hints |
| ISS-133 | LOW | ARCHITECTURE | tui/app.py:343-355 | Nested callback без type hints | Добавить type hints |
| ISS-134 | LOW | TYPE_SAFETY | tui/app.py:395 | asyncio.TimeoutError as e не используется | Убрать 'as e' |
| ISS-135 | LOW | TYPE_SAFETY | services/dialogue_runner.py:121-122 | except ProviderError: pass без логирования | Добавить log |
| ISS-136 | LOW | TYPE_SAFETY | tui/app.py:580-582 | except ProviderError: pass без логирования | Добавить log |
| ISS-137 | LOW | TYPE_SAFETY | models/ollama_client.py:409-413 | OSError с логированием но без обработки | Улучшить обработку |
| ISS-138 | LOW | TYPE_SAFETY | models/ollama_client.py:490-494 | OSError с логированием но без обработки | Улучшить обработку |
| ISS-139 | LOW | TYPE_SAFETY | tui/app.py:276-277 | _style_mapper кэшируется без явной необходимости | Рассмотреть必要性 |
| ISS-140 | LOW | TYPE_SAFETY | tui/app.py:278-279 | _cleanup_done флаг без документации | Добавить docstring |

---

### ПАКЕТ-8: Тесты - стиль и качество (ISS-141 ... ISS-160)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-141 | LOW | STYLE | tests/test_arch_audit_fixes.py:38,55,83,89,143 | E501 line too long | Переформатировать |
| ISS-142 | LOW | STYLE | tests/test_architecture.py:223,237 | E501 line too long | Переформатировать |
| ISS-143 | LOW | STYLE | tests/test_architecture_integrity.py:56,416,828,832,845 | E501 line too long | Переформатировать |
| ISS-144 | LOW | STYLE | tests/test_architecture_patterns.py:46,47,55,65,75,79,136,140,142,143,151,152 | E501 line too long | Переформатировать |
| ISS-145 | LOW | STYLE | tests/test_architecture_refactor.py:90,147,174 | E501 line too long | Переформатировать |
| ISS-146 | LOW | STYLE | tests/test_audit_fixes.py:52,54,76,77,92,233,280,383,518,685 | E501 line too long | Переформатировать |
| ISS-147 | LOW | STYLE | tests/test_audit_fixes_verification.py:119,138,198 | E501 line too long | Переформатировать |
| ISS-148 | LOW | STYLE | tests/test_call_from_thread_fix.py:5,6,7,13,48,104,108,129,130,151,155,174,187 | E501 line too long | Переформатировать |
| ISS-149 | LOW | STYLE | tests/test_call_from_thread_fix.py:212,213,237,255,263,267,288,289,352,377,392,395,396,397,399,402,405,408,413,416,419 | E501 line too long | Переформатировать |
| ISS-150 | LOW | STYLE | tests/test_code_audit_fixes.py:46,59,65,77,95,116 | E501 line too long | Переформатировать |
| ISS-151 | LOW | STYLE | tests/test_code_audit_fixes_verification.py:54,66 | E501 line too long | Переформатировать |
| ISS-152 | LOW | STYLE | tests/test_critical.py:15,19,39,135,223 | E501 line too long | Переформатировать |
| ISS-153 | LOW | STYLE | tests/test_critical.py:326,548,565,567,577,579,588,598,609,612,623,628,631,640,642,649,664,665 | E501 line too long | Переформатировать |
| ISS-154 | LOW | STYLE | tests/test_dialogue_runner_error_handling.py:60,102,143 | E501 line too long | Переформатировать |
| ISS-155 | LOW | STYLE | tests/test_fixes.py:4,28,54,85,98,107,126,148,154,157,163,179,193,202,206,227,228 | E501 line too long | Переформатировать |
| ISS-156 | LOW | STYLE | tests/test_new_audit_fixes.py:7,8,11,37,45,58,59,97,130,185,199,228,253,264,265,314,338,356 | E501 line too long | Переформатировать |
| ISS-157 | LOW | STYLE | tests/test_textual_reactive.py:31 | E501 line too long | Переформатировать |
| ISS-158 | LOW | STYLE | tests/test_timeout_fixes.py:78,86,106,115,124,129,148,161,171,184 | E501 line too long | Переформатировать |
| ISS-159 | LOW | STYLE | tests/test_ui_nomatches_handling.py:1,17,124 | E501 line too long | Переформатировать |
| ISS-160 | LOW | STYLE | tests/test_ui_shutdown_error.py:3,21,33,44,67,90 | E501 line too long | Переформатировать |

---

### ПАКЕТ-9: Тесты - стиль и качество (ISS-161 ... ISS-180)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-161 | LOW | STYLE | tests/test_ui_state_changed.py:7,46,54,60,78,97,118,125,143,183 | E501 line too long | Переформатировать |
| ISS-162 | LOW | UNUSED | tests/audit_reports/ | Дублирование папки audit_reports в tests | Удалить дубликат |
| ISS-163 | MEDIUM | ARCHITECTURE | tests/test_ui_nomatches_handling.py:38 | Failing test: assertion check wrong message | Исправить assertion |
| ISS-164 | LOW | ARCHITECTURE | tests/ | Избыточное количество тестовых файлов | Рассмотреть консолидацию |
| ISS-165 | LOW | ARCHITECTURE | tests/ | Тесты дублируют функциональность | Устранить дублирование |
| ISS-166 | LOW | ARCHITECTURE | tests/test_arch_*.py | Тесты архитектуры без четкой структуры | Рефакторить |
| ISS-167 | LOW | ARCHITECTURE | tests/test_audit_*.py | Тесты аудита без четкой структуры | Рефакторить |
| ISS-168 | LOW | ARCHITECTURE | tests/test_code_audit_*.py | Тесты code audit без четкой структуры | Рефакторить |
| ISS-169 | MEDIUM | ARCHITECTURE | tests/__init__.py | Пустой __init__.py | Добавить конфигурацию или удалить |
| ISS-170 | LOW | STYLE | audit_reports/__init__.py | Отсутствует | Создать или удалить папку |
| ISS-171 | LOW | STYLE | services/__init__.py | Пустой __init__.py | Добавить экспорты |
| ISS-172 | LOW | STYLE | factories/__init__.py | Пустой __init__.py | Добавить экспорты |
| ISS-173 | LOW | STYLE | models/__init__.py | Пустой __init__.py | Добавить экспорты |
| ISS-174 | LOW | STYLE | controllers/__init__.py | Пустой __init__.py | Добавить экспорты |
| ISS-175 | LOW | ARCHITECTURE | tui/__init__.py | Пустой __init__.py | Добавить экспорты |
| ISS-176 | LOW | STYLE | models/conversation.py:19 | __all__ содержит MessageDict который импортирован | Убрать из __all__ или оставить для совместимости |
| ISS-177 | LOW | STYLE | models/provider.py | MessageDict определен здесь, используется в conversation.py | Документировать зависимость |
| ISS-178 | LOW | ARCHITECTURE | models/ollama_client.py:41-298 | Вспомогательные классы используют staticmethod | Рассмотреть module-level функции |
| ISS-179 | LOW | ARCHITECTURE | models/ollama_client.py:31-35 | _DEFAULT_OPTIONS создаётся на уровне класса | Вынести на уровень модуля |
| ISS-180 | LOW | ARCHITECTURE | models/ollama_client.py:37-38 | _MODELS_CACHE_TTL определен дважды | Удалить дублирование |

---

### ПАКЕТ-10: Финальные улучшения (ISS-181 ... ISS-200)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-181 | LOW | SECURITY | models/ollama_client.py | Отсутствует проверка URL на localhost only | Добавить ограничение |
| ISS-182 | LOW | SECURITY | models/ollama_client.py | Отсутствует rate limiting | Добавить rate limiting |
| ISS-183 | LOW | SECURITY | tui/sanitizer.py | HTML escape может быть неполным | Использовать bleach или similar |
| ISS-184 | MEDIUM | ARCHITECTURE | models/config.py | Hardcoded defaults | Вынести в конфигурацию |
| ISS-185 | MEDIUM | ARCHITECTURE | tui/constants.py | Magic strings в CSS | Использовать CSS variables |
| ISS-186 | MEDIUM | ARCHITECTURE | tui/app.py:75 | CSS генерируется при импорте | Lazy initialization |
| ISS-187 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py | asyncio.create_task без loop проверки | Добавить проверку |
| ISS-188 | MEDIUM | TYPE_SAFETY | models/conversation.py:63-64 | _initialized flag не синхронизирован | Использовать threading.Lock |
| ISS-189 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:258 | _cache_timestamp использует time.time() | Использовать datetime |
| ISS-190 | MEDIUM | ARCHITECTURE | factories/provider_factory.py | Simple factory без абстракции | Рассмотреть ABC |
| ISS-191 | MEDIUM | ARCHITECTURE | models/provider.py | Exception hierarchy без base usage | Добавить logging base |
| ISS-192 | MEDIUM | ARCHITECTURE | tui/app.py | Много Exception handlers | Унифицировать обработку |
| ISS-193 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py | Callback-driven architecture хрупкая | Рассмотреть observer pattern |
| ISS-194 | MEDIUM | ARCHITECTURE | models/conversation.py | Conversation создаёт Config() неявно | DI через конструктор |
| ISS-195 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py | UIState изменяемый | Сделать immutable |
| ISS-196 | MEDIUM | ARCHITECTURE | tui/app.py | DialogueApp слишком большой | Разделить на Screen классы |
| ISS-197 | MEDIUM | ARCHITECTURE | tui/app.py | Отсутствует interface для callbacks | Создать Protocol |
| ISS-198 | MEDIUM | TYPE_SAFETY | tui/app.py:343,436,468 | Lambda callbacks без type hints | Добавить type hints |
| ISS-199 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py | ProviderError перехватывается без логирования | Добавить log |
| ISS-200 | MEDIUM | ARCHITECTURE | models/ollama_client.py | _HTTPSessionManager создан в __init__ | Lazy initialization |

---

## Группировка по пакетам

### Пакет-1 (ISS-001...ISS-020)
Критичные и высокоприоритетные проблемы: TYPE_SAFETY, архитектурные антипаттерны

### Пакет-2 (ISS-021...ISS-040)
Типизация и архитектурные паттерны: улучшение type safety

### Пакет-3 (ISS-041...ISS-060)
Устаревшие конструкции и зависимости: pylint suppressions, deprecated patterns

### Пакет-4 (ISS-061...ISS-080)
Стилевые проблемы - источники: основные файлы src/

### Пакет-5 (ISS-081...ISS-100)
Стилевые проблемы - tui модуль: tui/app.py

### Пакет-6 (ISS-101...ISS-120)
Стилевые проблемы - остальные модули tui/

### Пакет-7 (ISS-121...ISS-140)
Неиспользуемый код и архитектурные замечания

### Пакет-8 (ISS-141...ISS-160)
Тесты - стиль и качество: test_arch_*, test_audit_*

### Пакет-9 (ISS-161...ISS-180)
Тесты - стиль и качество: остальные тесты

### Пакет-10 (ISS-181...ISS-200)
Финальные улучшения: security, architecture, type safety

---

*Дата формирования: 2026-04-18*
*Автономный аудит завершён*
