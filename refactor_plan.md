# Реестр проблем автономного рефакторинга
# Автономный протокол рефакторинга - Этап 0

## Сводная статистика аудита

| Категория | CRITICAL | HIGH | MEDIUM | LOW | Всего |
|-----------|----------|------|--------|-----|-------|
| STYLE | 0 | 5 | 40 | 35 | 80 |
| TYPE_SAFETY | 1 | 2 | 5 | 10 | 18 |
| ARCHITECTURE | 0 | 3 | 15 | 20 | 38 |
| UNUSED | 0 | 2 | 8 | 15 | 25 |
| DEPRECATED | 0 | 1 | 5 | 10 | 16 |
| SECURITY | 0 | 0 | 3 | 5 | 8 |
| PERFORMANCE | 0 | 0 | 5 | 10 | 15 |
| **ИТОГО** | **1** | **13** | **81** | **105** | **200** |

## Полный реестр проблем

### ПАКЕТ-1: Критические и важные проблемы (ISS-001 - ISS-020)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | CRITICAL | TYPE_SAFETY | factories/provider_factory.py:23 | Missing return statement в Protocol-методе. Функция `__call__` должна возвращать ModelProvider. | Добавить `return create_ollama_provider(config)` |
| ISS-002 | HIGH | STYLE | models/conversation.py:70-71 | Строки превышают 79 символов (84 символа). Нарушение PEP8. | Перенести на несколько строк |
| ISS-003 | HIGH | STYLE | models/conversation.py:96 | Строка превышает 79 символов (91 символ). | Перенести на несколько строк |
| ISS-004 | HIGH | STYLE | models/conversation.py:123 | Строка превышает 79 символов (97 символов). | Перенести на несколько строк |
| ISS-005 | HIGH | STYLE | models/ollama_client.py:158 | Строка превышает 79 символов (99 символов). | Перенести на несколько строк |
| ISS-006 | HIGH | STYLE | models/ollama_client.py:473 | Строка превышает 79 символов (119 символов). | Перенести на несколько строк |
| ISS-007 | HIGH | ARCHITECTURE | controllers/__init__.py | Дублирование кода: UIState и DialogueController определены в обоих файлах. | Удалить дубликат из controllers/__init__.py, использовать импорт |
| ISS-008 | HIGH | STYLE | tui/app.py:267 | Строка превышает 79 символов (106 символов). | Перенести на несколько строк |
| ISS-009 | HIGH | STYLE | tui/app.py:579 | Строка превышает 79 символов (110 символов). | Перенести на несколько строк |
| ISS-010 | HIGH | STYLE | services/dialogue_runner.py:69 | Строка превышает 79 символов (81 символ). | Перенести на несколько строк |
| ISS-011 | MEDIUM | STYLE | models/__init__.py:3 | Строка превышает 79 символов (84 символа). | Перенести на несколько строк |
| ISS-012 | MEDIUM | STYLE | models/conversation.py:144 | Строка превышает 79 символов (83 символа). | Перенести на несколько строк |
| ISS-013 | MEDIUM | STYLE | models/conversation.py:298-299 | Строки превышают 79 символов (80 символов). | Перенести на несколько строк |
| ISS-014 | MEDIUM | STYLE | models/ollama_client.py:246 | Строка превышает 79 символов (80 символов). | Перенести на несколько строк |
| ISS-015 | MEDIUM | STYLE | models/ollama_client.py:313 | Строка превышает 79 символов (86 символов). | Перенести на несколько строк |
| ISS-016 | MEDIUM | STYLE | models/ollama_client.py:371 | Строка превышает 79 символов (85 символов). | Перенести на несколько строк |
| ISS-017 | MEDIUM | STYLE | models/ollama_client.py:456 | Строка превышает 79 символов (82 символа). | Перенести на несколько строк |
| ISS-018 | MEDIUM | STYLE | services/dialogue_runner.py:90 | D401: Первая строка docstring должна быть в повелительном наклонении. | Изменить "Main dialogue loop." на "Run main dialogue loop." |
| ISS-019 | MEDIUM | STYLE | tui/app.py:523 | D401: Первая строка docstring должна быть в повелительном наклонении. | Изменить "Main dialogue loop." на "Run main dialogue loop." |
| ISS-020 | MEDIUM | ARCHITECTURE | main.py:20-29 | Дублирование вызова logging.basicConfig(). | Удалить дублирующий блок |

### ПАКЕТ-2: Проблемы стиля строк (ISS-021 - ISS-040)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-021 | MEDIUM | STYLE | tui/app.py:73 | Строка превышает 79 символов (82 символа). | Перенести |
| ISS-022 | MEDIUM | STYLE | tui/app.py:92 | Строка превышает 79 символов (85 символов). | Перенести |
| ISS-023 | MEDIUM | STYLE | tui/app.py:112 | Строка превышает 79 символов (86 символов). | Перенести |
| ISS-024 | MEDIUM | STYLE | tui/app.py:182 | Строка превышает 79 символов (82 символа). | Перенести |
| ISS-025 | MEDIUM | STYLE | tui/app.py:188 | Строка превышает 79 символов (97 символов). | Перенести |
| ISS-026 | MEDIUM | STYLE | tui/app.py:195-196 | Строки превышают 79 символов (83 символа). | Перенести |
| ISS-027 | MEDIUM | STYLE | tui/app.py:243 | Строка превышает 79 символов (82 символа). | Перенести |
| ISS-028 | MEDIUM | STYLE | tui/app.py:283 | Строка превышает 79 символов (83 символа). | Перенести |
| ISS-029 | MEDIUM | STYLE | tui/app.py:291 | Строка превышает 79 символов (87 символов). | Перенести |
| ISS-030 | MEDIUM | STYLE | tui/app.py:308 | Строка превышает 79 символов (91 символ). | Перенести |
| ISS-031 | MEDIUM | STYLE | tui/app.py:368 | Строка превышает 79 символов (93 символа). | Перенести |
| ISS-032 | MEDIUM | STYLE | tui/app.py:427 | Строка превышает 79 символов (92 символа). | Перенести |
| ISS-033 | MEDIUM | STYLE | tui/app.py:451-452 | Строки превышают 79 символов. | Перенести |
| ISS-034 | MEDIUM | STYLE | tui/app.py:457 | Строка превышает 79 символов (92 символа). | Перенести |
| ISS-035 | MEDIUM | STYLE | tui/app.py:502 | Строка превышает 79 символов (80 символов). | Перенести |
| ISS-036 | MEDIUM | STYLE | tui/app.py:540 | Строка превышает 79 символов (92 символа). | Перенести |
| ISS-037 | MEDIUM | STYLE | tui/app.py:543 | Строка превышает 79 символов (106 символов). | Перенести |
| ISS-038 | MEDIUM | STYLE | tui/app.py:588 | Строка превышает 79 символов (84 символа). | Перенести |
| ISS-039 | MEDIUM | STYLE | services/dialogue_runner.py:109 | Строка превышает 79 символов (88 символов). | Перенести |
| ISS-040 | MEDIUM | STYLE | services/dialogue_service.py:149 | Строка превышает 79 символов (82 символа). | Перенести |

### ПАКЕТ-3: Архитектурные улучшения (ISS-041 - ISS-060)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-041 | HIGH | ARCHITECTURE | models/provider.py:117-118 | Два многоточия подряд в Protocol-методе. | Удалить дублирующее `...` |
| ISS-042 | MEDIUM | ARCHITECTURE | models/conversation.py:11 | ModelId определён дважды: в provider.py и conversation.py. | Удалить дубликат из conversation.py |
| ISS-043 | MEDIUM | ARCHITECTURE | tui/app.py:54-62 | Комментарий о call_from_thread vs call_after_refresh должен быть в документации модуля. | Переместить комментарий в docstring модуля |
| ISS-044 | MEDIUM | ARCHITECTURE | models/ollama_client.py:180-200 | Класс _HTTPSessionManager имеет избыточную документацию о масштабировании. | Сократить docstring |
| ISS-045 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:45-55 | Метод get_style_id дублирует функциональность get_style_info. | Удалить get_style_id или сделать его приватным |
| ISS-046 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:29-39 | Функция create_ollama_provider не используется напрямую. | Добавить в __all__ или удалить |
| ISS-047 | MEDIUM | ARCHITECTURE | tui/app.py:251-275 | Кэширование _style_mapper в __init__ избыточно. | Использовать ленивую инициализацию |
| ISS-048 | MEDIUM | ARCHITECTURE | tui/app.py:266-267 | Сложный lambda в _provider_factory. | Вынести в именованную функцию |
| ISS-049 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:85-122 | Метод _run_loop слишком длинный. | Разделить на меньшие методы |
| ISS-050 | MEDIUM | ARCHITECTURE | tui/app.py:299-317 | Метод _on_ui_state_changed имеет избыточные except-блоки. | Упростить обработку ошибок |
| ISS-051 | MEDIUM | ARCHITECTURE | tui/app.py:356-399 | Методы _handle_*_error дублируют логику. | Создать общий метод |
| ISS-052 | MEDIUM | ARCHITECTURE | tui/app.py:619-651 | Метод on_unmount слишком длинный. | Разделить на меньшие методы |
| ISS-053 | MEDIUM | ARCHITECTURE | models/ollama_client.py:46-90 | _RequestValidator и _ResponseHandler - вспомогательные классы. | Рассмотреть перенос в отдельный модуль |
| ISS-054 | MEDIUM | ARCHITECTURE | models/config.py:66-94 | _validate_numeric_range используется только внутри модуля. | Сделать приватным с префиксом _ |
| ISS-055 | MEDIUM | ARCHITECTURE | models/config.py:96-183 | Валидаторы температуры, токенов и таймаутов почти идентичны. | Унифицировать через фабрику |
| ISS-056 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:132-161 | run_dialogue_cycle имеет сложную логику. | Разделить на генерацию и обработку |
| ISS-057 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:65-80 | Свойство state возвращает копию UIState. | Рассмотреть иммутабельный паттерн |
| ISS-058 | MEDIUM | ARCHITECTURE | tui/sanitizer.py:40-44 | @lru_cache на пустой функции бессмысленнен. | Удалить декоратор или добавить логику |
| ISS-059 | MEDIUM | ARCHITECTURE | tui/constants.py:13-28 | MessageStyles использует строки вместо Enum. | Рассмотреть использование Literal или Enum |
| ISS-060 | MEDIUM | ARCHITECTURE | main.py:39-44 | Создание Config() перед app.run() не обрабатывает исключения. | Добавить обработку ValueError |

### ПАКЕТ-4: Неиспользуемый код (ISS-061 - ISS-080)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-061 | HIGH | UNUSED | models/provider.py:9 | Literal импортирован но не полностью используется. | Проверить использование |
| ISS-062 | HIGH | UNUSED | tui/sanitizer.py:9 | html импортирован но используется для html.escape. | Рассмотреть альтернативы или удалить |
| ISS-063 | MEDIUM | UNUSED | services/model_style_mapper.py:24 | self._style_map инициализируется в __init__ но мог бы быть классовой константой. | Сделать CLASS_VARIABLE |
| ISS-064 | MEDIUM | UNUSED | models/ollama_client.py:12 | time импортирован для _cache_timestamp. | Проверить использование |
| ISS-065 | MEDIUM | UNUSED | tui/app.py:251 | sub_title - reactive атрибут, инициализируется значением по умолчанию. | Рассмотреть удаление |
| ISS-066 | MEDIUM | UNUSED | tui/app.py:275 | _cleanup_done флаг для идемпотентности. | Рассмотреть использование контекстного менеджера |
| ISS-067 | MEDIUM | UNUSED | models/conversation.py:16 | log импортирован но не используется в верхней области. | Проверить использование |
| ISS-068 | MEDIUM | UNUSED | models/ollama_client.py:34 | _logger импортирован но используется только в определённых методах. | Перенести в методы где используется |
| ISS-069 | MEDIUM | UNUSED | services/dialogue_runner.py:20 | log импортирован но используется только в _run_loop. | Перенести в метод |
| ISS-070 | MEDIUM | UNUSED | services/dialogue_service.py:18 | log импортирован но используется только в run_dialogue_cycle. | Перенести в метод |
| ISS-071 | MEDIUM | UNUSED | controllers/dialogue_controller.py:9 | TYPE_CHECKING импортирован но может не использоваться. | Проверить использование |
| ISS-072 | MEDIUM | UNUSED | factories/provider_factory.py:8 | Protocol импортирован из typing. | Использовать из typing_extensions или удалить |
| ISS-073 | LOW | UNUSED | tui/app.py:11 | TYPE_CHECKING импортирован. | Проверить использование |
| ISS-074 | LOW | UNUSED | main.py:13-17 | Provider*Error импорты могут быть избыточными. | Проверить использование |
| ISS-075 | LOW | UNUSED | models/config.py:10 | Final импортирован но используется только для констант. | Рассмотреть type annotation |
| ISS-076 | LOW | UNUSED | models/ollama_client.py:13 | Final импортирован но TYPE_CHECKING делает это условным. | Перенести в TYPE_CHECKING |
| ISS-077 | LOW | UNUSED | tui/constants.py:10 | Final импортирован но используется в module level. | Рассмотреть удаление |
| ISS-078 | LOW | UNUSED | services/model_style_mapper.py:8 | TYPE_CHECKING импортирован. | Проверить использование |
| ISS-079 | LOW | UNUSED | services/dialogue_runner.py:10 | TYPE_CHECKING импортирован. | Проверить использование |
| ISS-080 | LOW | UNUSED | services/dialogue_service.py:10 | TYPE_CHECKING импортирован. | Проверить использование |

### ПАКЕТ-5: Улучшения типизации (ISS-081 - ISS-100)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-081 | HIGH | TYPE_SAFETY | factories/provider_factory.py:17-26 | ProviderFactory Protocol неполон. | Добавить все необходимые методы |
| ISS-082 | MEDIUM | TYPE_SAFETY | models/conversation.py:56-57 | _current_turn использует default="A" но тип ModelId. | Использовать field(default_factory) |
| ISS-083 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:203-208 | _HTTPSessionManager.__init__ параметры имеют default значения. | Добавить type hints |
| ISS-084 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:70 | validate_messages параметр Sequence[Mapping[str, Any]]. | Рассмотреть использование list[MessageDict] |
| ISS-085 | MEDIUM | TYPE_SAFETY | tui/app.py:252-255 | provider_factory тип Callable[[], ModelProvider]. | Добавить Generic для типобезопасности |
| ISS-086 | MEDIUM | TYPE_SAFETY | tui/app.py:77 | *args и **kwargs в __init__ без type hints. | Добавить type hints |
| ISS-087 | MEDIUM | TYPE_SAFETY | models/config.py:66-94 | _validate_numeric_range не имеет return type annotation. | Добавить -> None |
| ISS-088 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:56-59 | start() параметр on_turn без полного типа. | Уточнить тип |
| ISS-089 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:52 | on_state_changed тип Callable[[UIState], None]. | Добавить в Protocol |
| ISS-090 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:42-55 | create_provider_factory возвращает factory. | Уточнить return type |
| ISS-091 | LOW | TYPE_SAFETY | tui/app.py:316-317 | except Exception as e: без конкретизации. | Ловить Specific exceptions |
| ISS-092 | LOW | TYPE_SAFETY | tui/app.py:593-610 | _handle_dialogue_error параметр model_name без type hint. | Добавить type hint |
| ISS-093 | LOW | TYPE_SAFETY | tui/app.py:612-618 | _handle_critical_error параметр _e без type hint. | Добавить type hint |
| ISS-094 | LOW | TYPE_SAFETY | tui/app.py:448-470 | _finalize_setup без type hints. | Добавить type hints |
| ISS-095 | LOW | TYPE_SAFETY | services/dialogue_service.py:22-36 | DialogueTurnResult - dataclass без module-level type alias. | Рассмотреть перенос в отдельный модуль |
| ISS-096 | LOW | TYPE_SAFETY | models/conversation.py:74-86 | _validate_params не имеет return type. | Добавить -> None |
| ISS-097 | LOW | TYPE_SAFETY | models/conversation.py:88-96 | _create_system_prompt не имеет return type. | Добавить -> str |
| ISS-098 | LOW | TYPE_SAFETY | models/conversation.py:98-131 | _trim_context_if_needed return type tuple но возвращает list. | Исправить type annotation |
| ISS-099 | LOW | TYPE_SAFETY | models/conversation.py:177-189 | get_context возвращает tuple но можно tuple[...] | Подтвердить иммутабельность |
| ISS-100 | LOW | TYPE_SAFETY | models/conversation.py:215-221 | get_current_model_name и get_other_model_name - почти дубликаты. | Унифицировать через параметр |

### ПАКЕТ-6: Проблемы безопасности и зависимостей (ISS-101 - ISS-120)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-101 | MEDIUM | SECURITY | tui/sanitizer.py:53-60 | sanitize_topic использует strip() но не экранирует все special chars. | Усилить валидацию |
| ISS-102 | MEDIUM | SECURITY | models/ollama_client.py:65-67 | validate_host вызывает validate_ollama_url. | Рассмотреть кэширование результата |
| ISS-103 | MEDIUM | SECURITY | tui/app.py:322-323 | _client создаётся в on_mount без timeout. | Добавить timeout для list_models |
| ISS-104 | LOW | SECURITY | tui/sanitizer.py:76 | html.escape использует quote=False. | Рассмотреть quote=True для безопасности |
| ISS-105 | LOW | SECURITY | models/config.py:211-215 | default_system_prompt содержит format string. | Валидировать в __post_init__ |
| ISS-106 | MEDIUM | DEPRECATED | models/provider.py:91 | ModelId = Literal["A", "B"] - устаревший паттерн. | Рассмотреть Enum или NewType |
| ISS-107 | MEDIUM | DEPRECATED | tui/constants.py:25-28 | MessageStyles использует строки вместо Literal. | Мигрировать на Literal |
| ISS-108 | MEDIUM | DEPRECATED | models/ollama_client.py:37-40 | _DEFAULT_OPTIONS создаётся каждый раз. | Использовать frozenset |
| ISS-109 | MEDIUM | DEPRECATED | services/dialogue_runner.py:133-136 | _is_task_cancelled использует asyncio.current_task(). | Использовать asyncio.Task.current_task() |
| ISS-110 | MEDIUM | DEPRECATED | tui/app.py:565 | _is_task_cancelled использует asyncio.current_task(). | Использовать asyncio.Task.current_task() |
| ISS-111 | MEDIUM | DEPRECATED | tui/sanitizer.py:40-44 | @lru_cache на _compile_sanitizer не используется. | Удалить или реализовать |
| ISS-112 | MEDIUM | DEPRECATED | models/ollama_client.py:246 | contextlib.suppress может быть избыточным. | Проверить необходимость |
| ISS-113 | MEDIUM | DEPRECATED | models/ollama_client.py:371-406 | Сложная обработка исключений с перекрытием. | Упростить иерархию |
| ISS-114 | MEDIUM | DEPRECATED | tui/app.py:336-346 | except ProviderConnectionError и ProviderGenerationError. | Рассмотреть общий base class |
| ISS-115 | MEDIUM | DEPRECATED | models/conversation.py:119 | system_message = context[0] if context else None. | Использовать match/case |
| ISS-116 | LOW | DEPRECATED | services/dialogue_service.py:142 | if not self._is_running or self._is_paused: return None. | Рассмотреть ранний return |
| ISS-117 | LOW | DEPRECATED | controllers/dialogue_controller.py:120-122 | Двойная проверка is_running и is_paused. | Упростить логику |
| ISS-118 | LOW | DEPRECATED | tui/app.py:155 | model_a_value is Select.BLANK. | Использовать == |
| ISS-119 | LOW | DEPRECATED | models/ollama_client.py:230-241 | Сложная проверка _session.closed. | Упростить логику |
| ISS-120 | LOW | DEPRECATED | models/ollama_client.py:233 | Вложенная проверка if. | Использовать early return |

### ПАКЕТ-7: Улучшения производительности (ISS-121 - ISS-140)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-121 | MEDIUM | PERFORMANCE | tui/sanitizer.py:17-31 | SANITIZE_CHARS создаётся при каждом импорте. | Вынести в module-level константу |
| ISS-122 | MEDIUM | PERFORMANCE | tui/sanitizer.py:78-80 | Цикл for для замены символов неэффективен. | Использовать str.translate() |
| ISS-123 | MEDIUM | PERFORMANCE | models/ollama_client.py:387 | models кэшируется, но _models_cache.get() вызывается каждый раз. | Добавить early return |
| ISS-124 | MEDIUM | PERFORMANCE | models/conversation.py:141 | context = self._context_a if model_id == "A" else self._context_b. | Вынести в helper метод |
| ISS-125 | MEDIUM | PERFORMANCE | models/conversation.py:187 | context = self._context_a if model_id == "A" else self._context_b. | Вынести в helper метод |
| ISS-126 | MEDIUM | PERFORMANCE | tui/app.py:273 | _style_mapper создаётся в __init__. | Использовать lazy initialization |
| ISS-127 | MEDIUM | PERFORMANCE | models/ollama_client.py:155-159 | List comprehension может быть оптимизирован. | Использовать генератор |
| ISS-128 | MEDIUM | PERFORMANCE | models/ollama_client.py:434-444 | Создание options dict каждый раз. | Кэшировать default options |
| ISS-129 | LOW | PERFORMANCE | tui/app.py:588-591 | query_one вызывается при каждом _write_to_log. | Кэшировать ссылку на виджет |
| ISS-130 | LOW | PERFORMANCE | tui/app.py:307-309 | query_one вызывается при каждом _on_ui_state_changed. | Кэшировать ссылку |
| ISS-131 | LOW | PERFORMANCE | services/dialogue_runner.py:109 | self._service.conversation.get_current_model_name() вызывается при каждой ошибке. | Кэшировать перед циклом |
| ISS-132 | LOW | PERFORMANCE | tui/app.py:537-540 | service.conversation вызывается несколько раз. | Вынести в локальную переменную |
| ISS-133 | LOW | PERFORMANCE | models/conversation.py:268-271 | Создание snapshot списков при каждом process_turn. | Рассмотреть использование copy |
| ISS-134 | LOW | PERFORMANCE | models/ollama_client.py:369-389 | async with session.get(url) требует проверки. | Добавить timeout |
| ISS-135 | LOW | PERFORMANCE | models/ollama_client.py:453-469 | async with session.post(url) требует проверки. | Добавить timeout |
| ISS-136 | LOW | PERFORMANCE | services/dialogue_service.py:149 | process_turn возвращает 3 значения но используется только response. | Рассмотреть изменение интерфейса |
| ISS-137 | LOW | PERFORMANCE | tui/app.py:556-558 | Проверка service.is_running и service.is_paused. | Рассмотреть combined property |
| ISS-138 | LOW | PERFORMANCE | tui/app.py:531-550 | style_mapper.get_style_info вызывается при каждой итерации. | Кэшировать перед циклом |
| ISS-139 | LOW | PERFORMANCE | models/conversation.py:116-117 | len(context) <= max_len проверка неэффективна. | Проверить один раз |
| ISS-140 | LOW | PERFORMANCE | models/ollama_client.py:369-406 | Обработка исключений в list_models дублирует generate. | Вынести в helper |

### ПАКЕТ-8: Рефакторинг кода (ISS-141 - ISS-160)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-141 | MEDIUM | ARCHITECTURE | tui/app.py:474-487 | on_start_pressed содержит бизнес-логику. | Делегировать в controller |
| ISS-142 | MEDIUM | ARCHITECTURE | tui/app.py:522-562 | _run_dialogue слишком длинный. | Разделить на меньшие методы |
| ISS-143 | MEDIUM | ARCHITECTURE | tui/app.py:568-583 | _process_dialogue_turn смешивает логику и UI. | Разделить ответственности |
| ISS-144 | MEDIUM | ARCHITECTURE | models/conversation.py:247-293 | process_turn имеет слишком много ответственностей. | Разделить на generate и add_message |
| ISS-145 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:124-131 | _process_turn просто проксирует. | Inline или удалить |
| ISS-146 | MEDIUM | ARCHITECTURE | tui/app.py:409-472 | _setup_conversation слишком длинный. | Разделить на validation и creation |
| ISS-147 | MEDIUM | ARCHITECTURE | tui/app.py:418-470 | Вложенный callback on_topic_entered. | Вынести в отдельный метод |
| ISS-148 | MEDIUM | ARCHITECTURE | models/ollama_client.py:360-406 | list_models имеет длинный try-except блок. | Разделить на validation и API call |
| ISS-149 | MEDIUM | ARCHITECTURE | models/ollama_client.py:429-486 | generate имеет длинный try-except блок. | Разделить на validation и API call |
| ISS-150 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:113-127 | handle_start возвращает bool но UI не использует. | Рассмотреть исключения |
| ISS-151 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:129-147 | handle_pause возвращает bool но UI не использует. | Рассмотреть исключения |
| ISS-152 | MEDIUM | ARCHITECTURE | tui/app.py:299-317 | _on_ui_state_changed имеет сложную обработку ошибок. | Использовать try-except один раз |
| ISS-153 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:93-122 | start/pause/resume/stop имеют простую логику. | Рассмотреть использование State machine |
| ISS-154 | MEDIUM | ARCHITECTURE | models/config.py:220-236 | __post_init__ валидирует параметры. | Рассмотреть использование @property validators |
| ISS-155 | MEDIUM | ARCHITECTURE | tui/app.py:266 | provider_factory создаётся в __init__. | Использовать lazy initialization |
| ISS-156 | MEDIUM | ARCHITECTURE | tui/app.py:268-271 | _client и _controller создаются позже. | Рассмотреть использование Optional |
| ISS-157 | MEDIUM | ARCHITECTURE | models/ollama_client.py:328 | _RequestValidator.validate_host вызывается в __init__. | Рассмотреть lazy validation |
| ISS-158 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:42-55 | Фабрика создаёт замыкание. | Рассмотреть использование классов |
| ISS-159 | MEDIUM | ARCHITECTURE | models/provider.py:12-40 | ProviderError имеет slots но использует __init__ базового. | Добавить __init__ с slots |
| ISS-160 | MEDIUM | ARCHITECTURE | tui/constants.py:90-92 | Экземпляры dataclass создаются на уровне модуля. | Рассмотреть использование ENUM |

### ПАКЕТ-9: Чистка и оптимизация (ISS-161 - ISS-180)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-161 | MEDIUM | STYLE | models/conversation.py:19 | __all__ содержит ModelId который импортируется. | Удалить из __all__ |
| ISS-162 | MEDIUM | STYLE | factories/__init__.py:3-7 | Импорт из provider_factory. | Добавить type hints |
| ISS-163 | MEDIUM | STYLE | services/__init__.py:1 | Docstring слишком короткий. | Расширить docstring |
| ISS-164 | MEDIUM | STYLE | models/ollama_client.py:1-4 | Docstring модуля слишком короткий. | Расширить описание |
| ISS-165 | MEDIUM | STYLE | tui/app.py:1-4 | Docstring модуля слишком короткий. | Расширить описание |
| ISS-166 | MEDIUM | STYLE | models/provider.py:1-5 | Docstring модуля можно расширить. | Добавить примеры использования |
| ISS-167 | MEDIUM | STYLE | controllers/dialogue_controller.py:1-4 | Docstring модуля можно расширить. | Добавить описание |
| ISS-168 | MEDIUM | STYLE | services/dialogue_runner.py:1-4 | Docstring модуля можно расширить. | Добавить описание |
| ISS-169 | MEDIUM | STYLE | services/dialogue_service.py:1-4 | Docstring модуля можно расширить. | Добавить описание |
| ISS-170 | MEDIUM | STYLE | tui/sanitizer.py:1-5 | Docstring можно расширить. | Добавить security notes |
| ISS-171 | MEDIUM | STYLE | tui/styles.py:1-4 | Docstring можно расширить. | Добавить описание CSS генерации |
| ISS-172 | MEDIUM | STYLE | models/config.py:1-5 | Docstring можно расширить. | Добавить примеры |
| ISS-173 | MEDIUM | STYLE | main.py:1-2 | Shebang присутствует. | Рассмотреть использование __main__ |
| ISS-174 | MEDIUM | STYLE | main.py:20-29 | logging.basicConfig вызывается дважды. | Удалить дубликат |
| ISS-175 | MEDIUM | STYLE | main.py:33-36 | Docstring main() можно расширить. | Добавить описание |
| ISS-176 | MEDIUM | STYLE | tui/app.py:55-62 | Комментарий в модуле о call_from_thread. | Переместить в docstring |
| ISS-177 | LOW | STYLE | models/conversation.py | Пустые строки между методами. | Добавить консистентность |
| ISS-178 | LOW | STYLE | services/dialogue_runner.py | Пустые строки между методами. | Добавить консистентность |
| ISS-179 | LOW | STYLE | services/dialogue_service.py | Пустые строки между методами. | Добавить консистентность |
| ISS-180 | LOW | STYLE | tui/app.py | Пустые строки между методами. | Добавить консистентность |

### ПАКЕТ-10: Финальные улучшения (ISS-181 - ISS-200)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-181 | MEDIUM | ARCHITECTURE | tui/app.py:235-240 | DialogueApp имеет много ответственностей. | Рассмотреть split на Screen и App |
| ISS-182 | MEDIUM | ARCHITECTURE | models/ollama_client.py:307-345 | OllamaClient - слишком большой класс. | Разделить на HttpClient и ApiClient |
| ISS-183 | MEDIUM | ARCHITECTURE | tui/app.py:70-176 | ModelSelectionScreen и TopicInputScreen - похожие паттерны. | Создать общий базовый класс |
| ISS-184 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:24-28 | DialogueRunner имеет docstring но неполный. | Расширить описание |
| ISS-185 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:39-45 | DialogueService docstring можно расширить. | Добавить usage examples |
| ISS-186 | MEDIUM | ARCHITECTURE | models/conversation.py:36-44 | Conversation dataclass без __post_init__ описания. | Расширить docstring |
| ISS-187 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:37-47 | DialogueController docstring можно расширить. | Добавить usage examples |
| ISS-188 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:17-25 | ProviderFactory Protocol недокументирован. | Добавить docstring |
| ISS-189 | MEDIUM | ARCHITECTURE | models/ollama_client.py:307-310 | OllamaClient docstring можно расширить. | Добавить usage examples |
| ISS-190 | MEDIUM | ARCHITECTURE | tui/app.py:236-239 | DialogueApp docstring можно расширить. | Добавить описание |
| ISS-191 | LOW | STYLE | tests/ | Тесты не используют pytest fixtures. | Рассмотреть рефакторинг |
| ISS-192 | LOW | STYLE | tests/ | Тесты имеют дублирование setup. | Вынести в conftest.py |
| ISS-193 | LOW | STYLE | tests/ | Тесты используют MagicMock вместо AsyncMock. | Исправить на AsyncMock |
| ISS-194 | LOW | STYLE | tests/ | Тесты не используют parametrize. | Рассмотреть использование |
| ISS-195 | LOW | STYLE | tests/ | Некоторые тесты слишком длинные. | Разделить на меньшие |
| ISS-196 | LOW | ARCHITECTURE | tests/test_*.py | Именование тестов можно улучшить. | Использовать snake_case |
| ISS-197 | LOW | ARCHITECTURE | tests/ | Тесты проверяют private methods. | Тестировать только public API |
| ISS-198 | LOW | ARCHITECTURE | tests/ | Тесты используют patch() вместо monkeypatch. | Рассмотреть переход |
| ISS-199 | LOW | ARCHITECTURE | tests/ | Нет integration tests. | Добавить интеграционные тесты |
| ISS-200 | LOW | ARCHITECTURE | tests/ | Нет performance tests. | Добавить benchmark tests |

## Распределение по пакетам

- **Пакет-1**: ISS-001 - ISS-020 (Критические и важные)
- **Пакет-2**: ISS-021 - ISS-040 (Стиль строк)
- **Пакет-3**: ISS-041 - ISS-060 (Архитектура)
- **Пакет-4**: ISS-061 - ISS-080 (Неиспользуемый код)
- **Пакет-5**: ISS-081 - ISS-100 (Типизация)
- **Пакет-6**: ISS-101 - ISS-120 (Безопасность/Deprecated)
- **Пакет-7**: ISS-121 - ISS-140 (Производительность)
- **Пакет-8**: ISS-141 - ISS-160 (Рефакторинг)
- **Пакет-9**: ISS-161 - ISS-180 (Чистка)
- **Пакет-10**: ISS-181 - ISS-200 (Финальные улучшения)
