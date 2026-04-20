# Реестр проблем автономного рефакторинга

## Сводная статистика аудита

| Инструмент | Проблем | Критичность |
|------------|---------|-------------|
| Ruff | 0 | - |
| Flake8 | 17 | MEDIUM |
| Mypy | 0 | - |
| Pyright | 23 | MEDIUM |
| Bandit | 0 | - |
| Pyflakes | 0 | - |
| Pylint | 12 | MEDIUM/LOW |
| Vulture | 0 (src/ не существует) | - |

---

## Полный реестр проблем (200 записей)

### ПАКЕТ-1: Критические проблемы безопасности и типизации (ISS-001..ISS-020)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-001 | HIGH | TYPE_SAFETY | models/provider.py:12 | Базовый класс ProviderError не использует slots | Добавить slots=True к dataclass |
| ISS-002 | HIGH | TYPE_SAFETY | models/provider.py:41 | ProviderConfigurationError не использует slots | Добавить slots=True к dataclass |
| ISS-003 | HIGH | TYPE_SAFETY | models/provider.py:51 | ProviderConnectionError не использует slots | Добавить slots=True к dataclass |
| ISS-004 | HIGH | TYPE_SAFETY | models/provider.py:61 | ProviderGenerationError не использует slots | Добавить slots=True к dataclass |
| ISS-005 | HIGH | ARCHITECTURE | tui/app.py:235 | DialogueApp наследует от App[None] но использует generic без параметров | Изменить на App[None] или использовать более специфичный generic |
| ISS-006 | HIGH | ARCHITECTURE | tui/app.py:477 | Дублирование: TopicInputScreen.push_screen вызывается дважды | Удалить дублирующий вызов |
| ISS-007 | HIGH | STYLE | tui/app.py:294 | Строка 294 превышает 120 символов (82) | Разбить на несколько строк |
| ISS-008 | HIGH | STYLE | tui/app.py:308 | Строка 308 превышает 120 символов (100) | Разбить на несколько строк |
| ISS-009 | HIGH | STYLE | tui/app.py:329 | Строка 329 превышает 120 символов (111) | Разбить на несколько строк |
| ISS-010 | HIGH | STYLE | tui/app.py:355 | Строка 355 превышает 120 символов (82) | Разбить на несколько строк |
| ISS-011 | HIGH | STYLE | tui/app.py:433 | Строка 433 превышает 120 символов (92) | Разбить на несколько строк |
| ISS-012 | HIGH | STYLE | tui/app.py:457 | Строка 457 превышает 120 символов (83) | Разбить на несколько строк |
| ISS-013 | HIGH | STYLE | tui/app.py:458 | Строка 458 превышает 120 символов (103) | Разбить на несколько строк |
| ISS-014 | HIGH | STYLE | tui/app.py:462 | Строка 462 превышает 120 символов (92) | Разбить на несколько строк |
| ISS-015 | HIGH | STYLE | tui/app.py:508 | Строка 508 превышает 120 символов (80) | Разбить на несколько строк |
| ISS-016 | HIGH | STYLE | tui/app.py:512 | Строка 512 превышает 120 символов (80) | Разбить на несколько строк |
| ISS-017 | HIGH | STYLE | tui/app.py:546 | Строка 546 превышает 120 символов (92) | Разбить на несколько строк |
| ISS-018 | HIGH | STYLE | tui/app.py:549 | Строка 549 превышает 120 символов (106) | Разбить на несколько строк |
| ISS-019 | HIGH | STYLE | tui/app.py:586 | Строка 586 превышает 120 символов (108) | Разбить на несколько строк |
| ISS-020 | HIGH | STYLE | tui/app.py:594 | Строка 594 превышает 120 символов (84) | Разбить на несколько строк |

### ПАКЕТ-2: Проблемы стиля и форматирования (ISS-021..ISS-040)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-021 | MEDIUM | STYLE | tui/app.py:602 | Строка 602 превышает 120 символов (88) | Разбить на несколько строк |
| ISS-022 | MEDIUM | STYLE | tui/app.py:606 | Строка 606 превышает 120 символов (82) | Разбить на несколько строк |
| ISS-023 | MEDIUM | STYLE | tui/sanitizer.py:65 | Строка 65 превышает 120 символов (80) | Разбить на несколько строк |
| ISS-024 | MEDIUM | ARCHITECTURE | models/ollama_client.py:16 | Использование noqa comment для bandit | Убрать nosec, проверить реальную необходимость |
| ISS-025 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:10 | Import Optional вместо Optional из typing | Использовать from typing import Optional |
| ISS-026 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:10 | Import Optional вместо Optional из typing | Использовать from typing import Optional |
| ISS-027 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:309-331 | Параметр config в __init__ не используется после сохранения | Убрать неиспользуемый параметр или использовать |
| ISS-028 | MEDIUM | TYPE_SAFETY | tui/app.py:581 | Параметры model_name и style не используются | Добавить префикс _ или использовать |
| ISS-029 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:168 | ProviderError логируется но не передаётся с контекстом | Добавить context к исключению |
| ISS-030 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:100 | Callback может быть None - добавить проверку типов | Использовать Protocol для callback |
| ISS-031 | MEDIUM | STYLE | main.py:38 | Docstring Note не соответствует стилю | Переписать docstring |
| ISS-032 | MEDIUM | STYLE | controllers/dialogue_controller.py:51 | Docstring Example содержит >>> который может устареть | Убрать интерактивный пример |
| ISS-033 | MEDIUM | ARCHITECTURE | models/conversation.py:11 | Literal импортируется но используется только для type hints | Использовать TYPE_CHECKING |
| ISS-034 | MEDIUM | ARCHITECTURE | tui/constants.py:68 | pylint disable comment в production коде | Убрать или исправить код |
| ISS-035 | MEDIUM | ARCHITECTURE | models/conversation.py:56 | pylint disable comment в dataclass | Убрать или исправить код |
| ISS-036 | MEDIUM | ARCHITECTURE | tui/app.py:235 | pylint disable comment в классе | Убрать или исправить код |
| ISS-037 | LOW | UNUSED | services/dialogue_runner.py:1 | Модуль dialogue_runner не используется напрямую | Удалить или добавить использование |
| ISS-038 | LOW | ARCHITECTURE | models/conversation.py:22 | MAX_CONTEXT_LENGTH константа не используется вне модуля | Убрать из __all__ |
| ISS-039 | LOW | STYLE | factories/provider_factory.py:56 | Пустая строка перед return | Убрать пустую строку |
| ISS-040 | LOW | STYLE | models/ollama_client.py:488 | Пустая строка в конце файла перед EOF | Добавить пустую строку |

### ПАКЕТ-3: Проблемы типизации и аннотаций (ISS-041..ISS-060)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-041 | HIGH | TYPE_SAFETY | models/provider.py:24 | ProviderError.__init__ не использует slots | Добавить slots=True |
| ISS-042 | MEDIUM | TYPE_SAFETY | models/conversation.py:182 | get_context возвращает tuple но документация неполная | Улучшить docstring |
| ISS-043 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:409-414 | generate метод использует **kwargs без type hints | Добавить TypedDict для kwargs |
| ISS-044 | MEDIUM | TYPE_SAFETY | tui/app.py:252-256 | Callable[[], ModelProvider] не использует runtime checkable | Использовать Protocol |
| ISS-045 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:60 | Callable[[UIState], None] не является runtime_checkable | Добавить Protocol |
| ISS-046 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:66-67 | on_turn и on_error callbacks без строгой типизации | Создать Protocols для callbacks |
| ISS-047 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:260-271 | _is_cache_valid использует time.time() без явного импорта | Добавить time в импорты |
| ISS-048 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:10 | Optional импортирован но не используется с Final | Использовать from typing import Optional |
| ISS-049 | MEDIUM | ARCHITECTURE | models/ollama_client.py:43-47 | _RequestValidator не использует slots | Добавить slots=True |
| ISS-050 | MEDIUM | ARCHITECTURE | models/ollama_client.py:88-171 | _ResponseHandler не использует slots | Добавить slots=True |
| ISS-051 | MEDIUM | ARCHITECTURE | models/ollama_client.py:173-240 | _HTTPSessionManager использует slots частично | Убедиться что все атрибуты в slots |
| ISS-052 | MEDIUM | ARCHITECTURE | models/ollama_client.py:243-297 | _ModelsCache использует slots частично | Убедиться что все атрибуты в slots |
| ISS-053 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:148-151 | extract_models_list может вернуть пустой список при ошибке | Добавить логирование |
| ISS-054 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:165-170 | extract_generation_response возвращает пустую строку на ошибке | Добавить логирование или исключение |
| ISS-055 | MEDIUM | TYPE_SAFETY | models/config.py:66-93 | _validate_numeric_range использует string formatting | Использовать f-string |
| ISS-056 | MEDIUM | ARCHITECTURE | tui/sanitizer.py:22-45 | sanitize_topic использует regex для каждого вызова | Скомпилировать regex заранее |
| ISS-057 | MEDIUM | PERFORMANCE | tui/sanitizer.py:74-87 | sanitize_response_for_display делает много replace операций | Использовать str.translate или compiled regex |
| ISS-058 | MEDIUM | ARCHITECTURE | tui/constants.py:13-28 | MessageStyles dataclass не использует slots | Добавить slots=True |
| ISS-059 | MEDIUM | ARCHITECTURE | tui/constants.py:32-104 | UIElementIDs dataclass не использует slots | Добавить slots=True |
| ISS-060 | MEDIUM | ARCHITECTURE | tui/constants.py:107-122 | CSSClasses dataclass не использует slots | Добавить slots=True |

### ПАКЕТ-4: Архитектурные антипаттерны (ISS-061..ISS-080)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-061 | HIGH | ARCHITECTURE | tui/app.py:318-405 | Все exception handlers в одном методе | Разбить на отдельные методы |
| ISS-062 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:77-100 | Слишком много properties подряд | Сгруппировать логически |
| ISS-063 | MEDIUM | ARCHITECTURE | models/conversation.py:103-136 | _trim_context_if_needed создаёт новые списки | Оптимизировать для больших контекстов |
| ISS-064 | MEDIUM | ARCHITECTURE | models/ollama_client.py:347-407 | list_models содержит дублирование валидации | Вынести валидацию в отдельный метод |
| ISS-065 | MEDIUM | ARCHITECTURE | models/ollama_client.py:409-491 | generate метод длинный и сложный | Разбить на меньшие методы |
| ISS-066 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:36-206 | DialogueController обрабатывает слишком много состояний | Разбить на отдельные методы |
| ISS-067 | MEDIUM | ARCHITECTURE | tui/app.py:528-567 | _run_dialogue слишком длинный | Разбить на меньшие методы |
| ISS-068 | MEDIUM | ARCHITECTURE | tui/app.py:574-589 | _process_dialogue_turn混合логика | Разбить на подготовку и выполнение |
| ISS-069 | MEDIUM | ARCHITECTURE | models/config.py:186-237 | Config dataclass содержит слишком много атрибутов | Использовать composition |
| ISS-070 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:33-38 | _style_map инициализируется в __init__ | Использовать __slots__ |
| ISS-071 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:17-30 | ProviderFactory Protocol не используется | Либо удалить, либо использовать |
| ISS-072 | MEDIUM | ARCHITECTURE | models/conversation.py:274-298 | process_turn использует snapshot для rollback | Использовать contextlib |
| ISS-073 | MEDIUM | ARCHITECTURE | tui/app.py:252-256 | provider_factory параметр без валидации | Добавить проверку callable |
| ISS-074 | MEDIUM | ARCHITECTURE | models/ollama_client.py:323-324 | Валидация host происходит дважды | Убрать дублирование |
| ISS-075 | MEDIUM | ARCHITECTURE | models/config.py:220-236 | __post_init__ слишком длинный | Разбить на отдельные валидаторы |
| ISS-076 | MEDIUM | ARCHITECTURE | tui/app.py:406-413 | _safe_update_status ловит слишком широкий Exception | Ловить конкретные исключения |
| ISS-077 | MEDIUM | ARCHITECTURE | tui/app.py:310-316 | _on_ui_state_changed ловит слишком широкий Exception | Ловить конкретные исключения |
| ISS-078 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:141-170 | run_dialogue_cycle возвращает None на паузе | Использовать Optional[T] |
| ISS-079 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:73-88 | state property возвращает копию | Документировать что возвращается копия |
| ISS-080 | MEDIUM | ARCHITECTURE | tui/app.py:630-661 | on_unmount содержит смешанную логику | Разбить на cleanup и cancel |

### ПАКЕТ-5: Проблемы безопасности и обработки ошибок (ISS-081..ISS-100)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-081 | HIGH | SECURITY | tui/sanitizer.py:44-45 | sanitize_topic экранирует { и } но не все special chars | Расширить экранирование |
| ISS-082 | HIGH | SECURITY | tui/sanitizer.py:75-87 | sanitize_response_for_display не экранирует все markup | Использовать более полное экранирование |
| ISS-083 | HIGH | SECURITY | models/ollama_client.py:367 | URL формируется конкатенацией | Использовать urllib.parse.urljoin |
| ISS-084 | HIGH | SECURITY | models/ollama_client.py:434 | URL формируется конкатенацией | Использовать urllib.parse.urljoin |
| ISS-085 | HIGH | SECURITY | tui/app.py:374 | f-string в notify может содержать пользовательский ввод | Экранировать ввод |
| ISS-086 | MEDIUM | ARCHITECTURE | models/ollama_client.py:392-407 | Обработка исключений слишком широкая | Конкретизировать исключения |
| ISS-087 | MEDIUM | ARCHITECTURE | models/ollama_client.py:472-491 | Обработка исключений в generate слишком широкая | Конкретизировать исключения |
| ISS-088 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:157-170 | ProviderError ловится и перевыбрасывается | Добавить больше контекста |
| ISS-089 | MEDIUM | ARCHITECTURE | tui/app.py:560-563 | Exception ловится слишком широко | Конкретизировать исключения |
| ISS-090 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:121-135 | handle_start не проверяет is_paused корректно | Исправить логику проверки |
| ISS-091 | MEDIUM | ARCHITECTURE | models/ollama_client.py:391 | except as err используется но err не всегда используется | Убрать переменную если не нужна |
| ISS-092 | MEDIUM | ARCHITECTURE | models/ollama_client.py:401-403 | except as err используется но err не всегда используется | Убрать переменную если не нужна |
| ISS-093 | MEDIUM | ARCHITECTURE | models/ollama_client.py:485-487 | except as err используется но err не всегда используется | Убрать переменную если не нужна |
| ISS-094 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:168-170 | ProviderError перевыбрасывается без добавления context | Добавить context к исключению |
| ISS-095 | MEDIUM | ARCHITECTURE | tui/app.py:352-405 | Все исключения обрабатываются одинаково | Создать иерархию обработчиков |
| ISS-096 | MEDIUM | ARCHITECTURE | tui/app.py:352-368 | ProviderConnectionError и ProviderGenerationError обрабатываются одинаково | Объединить в один handler |
| ISS-097 | MEDIUM | ARCHITECTURE | tui/app.py:369-378 | ValueError обрабатывается как config error | Переименовать в ProviderConfigurationError |
| ISS-098 | MEDIUM | ARCHITECTURE | tui/app.py:379-387 | aiohttp.ClientError обрабатывается отдельно | Использовать более общий handler |
| ISS-099 | MEDIUM | ARCHITECTURE | tui/app.py:388-396 | asyncio.TimeoutError обрабатывается отдельно | Объединить с network errors |
| ISS-100 | MEDIUM | ARCHITECTURE | tui/app.py:397-405 | RuntimeError и SystemError обрабатываются вместе | Использовать конкретные исключения |

### ПАКЕТ-6: Проблемы производительности и оптимизации (ISS-101..ISS-120)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-101 | MEDIUM | PERFORMANCE | models/conversation.py:148-154 | _add_message_to_context делает много проверок | Оптимизировать проверки |
| ISS-102 | MEDIUM | PERFORMANCE | tui/app.py:273 | ModelStyleMapper создаётся каждый раз | Сделать singleton |
| ISS-103 | MEDIUM | PERFORMANCE | models/ollama_client.py:257 | _ModelsCache использует time.time() каждый раз | Кэшировать время проверки |
| ISS-104 | MEDIUM | PERFORMANCE | models/conversation.py:192-194 | get_context создаёт tuple каждый раз | Возвращать список или кэшировать |
| ISS-105 | MEDIUM | PERFORMANCE | tui/sanitizer.py:45 | re.sub вызывается без компиляции | Скомпилировать regex |
| ISS-106 | MEDIUM | PERFORMANCE | tui/app.py:539-554 | Цикл while проверяет is_running и is_paused | Добавить early exit |
| ISS-107 | MEDIUM | PERFORMANCE | models/ollama_client.py:226-234 | get_session создаёт новую сессию каждый раз | Проверить существующую сессию |
| ISS-108 | MEDIUM | PERFORMANCE | models/ollama_client.py:363-364 | Проверка кэша происходит синхронно | Возможно использовать async кэширование |
| ISS-109 | MEDIUM | ARCHITECTURE | models/conversation.py:241-250 | generate_response не использует контекст эффективно | Передавать копию контекста |
| ISS-110 | MEDIUM | PERFORMANCE | tui/app.py:463-471 | f-string формируется при каждом ходе | Кэшировать форматирование |
| ISS-111 | MEDIUM | PERFORMANCE | models/ollama_client.py:438-445 | options dict создаётся каждый раз | Использовать frozen dataclass |
| ISS-112 | MEDIUM | PERFORMANCE | services/dialogue_service.py:77-80 | conversation property может возвращать None | Проверить на None |
| ISS-113 | MEDIUM | PERFORMANCE | services/dialogue_service.py:83-85 | provider property может возвращать None | Проверить на None |
| ISS-114 | MEDIUM | PERFORMANCE | controllers/dialogue_controller.py:81-88 | UIState копируется при каждом обращении | Добавить кэширование |
| ISS-115 | MEDIUM | PERFORMANCE | models/ollama_client.py:148-151 | List comprehension создаёт новый список | Использовать generator |
| ISS-116 | MEDIUM | PERFORMANCE | tui/app.py:588 | call_after_refresh используется для каждого сообщения | Баталировать сообщения |
| ISS-117 | MEDIUM | ARCHITECTURE | models/ollama_client.py:50-62 | validate_host использует validate_ollama_url | Упростить интерфейс |
| ISS-118 | MEDIUM | ARCHITECTURE | models/config.py:29-63 | validate_ollama_url использует urlparse | Использовать pydantic для валидации |
| ISS-119 | MEDIUM | ARCHITECTURE | tui/app.py:252-256 | Callable без проверки типа | Использовать Protocol |
| ISS-120 | MEDIUM | PERFORMANCE | tui/app.py:455 | call_after_refresh вызывается для простого обновления | Использовать более эффективный метод |

### ПАКЕТ-7: Дублирование и DRY нарушения (ISS-121..ISS-140)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-121 | MEDIUM | ARCHITECTURE | tui/app.py:477-478 | Дублирование: TopicInputScreen.push_screen вызывается дважды | Удалить дублирующий вызов |
| ISS-122 | MEDIUM | ARCHITECTURE | models/ollama_client.py:372-374 | validate_status_code вызывается но результат игнорируется | Использовать возвращаемое значение |
| ISS-123 | MEDIUM | ARCHITECTURE | models/ollama_client.py:456-457 | validate_status_code вызывается но результат игнорируется | Использовать возвращаемое значение |
| ISS-124 | MEDIUM | ARCHITECTURE | models/ollama_client.py:376-379 | JSON decode error обрабатывается дважды | Убрать дублирование |
| ISS-125 | MEDIUM | ARCHITECTURE | models/ollama_client.py:460-464 | JSON decode error обрабатывается дважды | Убрать дублирование |
| ISS-126 | MEDIUM | ARCHITECTURE | tui/app.py:410-412 | query_one вызывается несколько раз с одним id | Кэшировать результат |
| ISS-127 | MEDIUM | ARCHITECTURE | tui/app.py:462-463 | query_one вызывается несколько раз | Кэшировать результат |
| ISS-128 | MEDIUM | ARCHITECTURE | tui/app.py:594-596 | query_one вызывается несколько раз | Кэшировать результат |
| ISS-129 | MEDIUM | ARCHITECTURE | models/conversation.py:96-99 | Форматирование промпта повторяется | Вынести в отдельный метод |
| ISS-130 | MEDIUM | ARCHITECTURE | models/conversation.py:306-309 | Форматирование промпта повторяется | Вынести в отдельный метод |
| ISS-131 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:151-152 | Проверка is_running и is_paused повторяется | Создать helper метод |
| ISS-132 | MEDIUM | ARCHITECTURE | tui/app.py:540-541 | Проверка is_running и is_paused повторяется | Создать helper метод |
| ISS-133 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:106 | Проверка is_running и is_paused повторяется | Создать helper метод |
| ISS-134 | MEDIUM | ARCHITECTURE | tui/app.py:315-316 | Exception логируется но не добавляется context | Добавить context |
| ISS-135 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:81-88 | UIState копируется вручную | Использовать copy.deepcopy или dataclasses.replace |
| ISS-136 | MEDIUM | ARCHITECTURE | models/config.py:186-237 | Config использует frozen=True но имеет eq=False | Исправить eq=True или убрать frozen |
| ISS-137 | MEDIUM | ARCHITECTURE | tui/sanitizer.py:71-87 | sanitize_response_for_display содержит повторяющиеся операции | Использовать loop или translate |
| ISS-138 | MEDIUM | ARCHITECTURE | models/ollama_client.py:16 | nosec comment нарушает безопасность | Убрать nosec или проверить |
| ISS-139 | MEDIUM | ARCHITECTURE | tui/app.py:457-458 | f-string с f"{model_a} ↔ {model_b}" | Использовать str.format |
| ISS-140 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:158 | process_turn получает _ но использует не все значения | Переименовать в _ |

### ПАКЕТ-8: Проблемы тестируемости и документации (ISS-141..ISS-160)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-141 | MEDIUM | ARCHITECTURE | tui/app.py:235 | DialogueApp имеет слишком много обязанностей | Разбить на миксины |
| ISS-142 | MEDIUM | ARCHITECTURE | models/ollama_client.py:300 | OllamaClient имеет слишком много обязанностей | Выделить менеджер сессий |
| ISS-143 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:39 | DialogueService имеет слишком много обязанностей | Использовать composition |
| ISS-144 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:36 | DialogueController имеет слишком много обязанностей | Разбить на controller и state manager |
| ISS-145 | MEDIUM | DOCUMENTATION | models/provider.py:94-105 | Docstring Example содержит код который не запускается | Обновить или убрать |
| ISS-146 | MEDIUM | DOCUMENTATION | models/provider.py:115-117 | Docstring raises не соответствует реализации | Исправить docstring |
| ISS-147 | MEDIUM | DOCUMENTATION | models/provider.py:137-139 | Docstring raises не соответствует реализации | Исправить docstring |
| ISS-148 | MEDIUM | DOCUMENTATION | controllers/dialogue_controller.py:51-53 | Docstring Example устарел | Обновить или убрать |
| ISS-149 | MEDIUM | DOCUMENTATION | services/dialogue_service.py:40-53 | Docstring Note не соответствует стилю | Переписать docstring |
| ISS-150 | MEDIUM | DOCUMENTATION | services/dialogue_runner.py:23-35 | Docstring Note не соответствует стилю | Переписать docstring |
| ISS-151 | MEDIUM | DOCUMENTATION | models/ollama_client.py:187-193 | Scalability section не соответствует формату | Переписать в стандартном формате |
| ISS-152 | MEDIUM | DOCUMENTATION | models/ollama_client.py:300-307 | Docstring неполный | Добавить Attributes section |
| ISS-153 | MEDIUM | DOCUMENTATION | models/conversation.py:50-53 | Docstring Note дублирует pylint comment | Убрать один из них |
| ISS-154 | MEDIUM | DOCUMENTATION | tui/app.py:55-62 | Комментарий о call_from_thread vs call_after_refresh | Перенести в документацию |
| ISS-155 | MEDIUM | DOCUMENTATION | tui/app.py:599-607 | Комментарий о call_from_thread vs call_after_refresh | Перенести в документацию |
| ISS-156 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:76 | asyncio.get_running_loop() может вызвать ошибку | Кэшировать loop |
| ISS-157 | MEDIUM | ARCHITECTURE | models/ollama_client.py:215 | asyncio.Lock используется для сессии | Использовать более эффективный механизм |
| ISS-158 | MEDIUM | ARCHITECTURE | tui/app.py:571 | asyncio.current_task() возвращает None возможно | Добавить проверку |
| ISS-159 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:143 | asyncio.current_task() возвращает None возможно | Добавить проверку |
| ISS-160 | MEDIUM | ARCHITECTURE | tui/app.py:637-647 | Отмена задачи делается неправильно | Использовать asyncio.gather |

### ПАКЕТ-9: Дополнительные улучшения (ISS-161..ISS-180)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-161 | LOW | STYLE | main.py:1 | shebang может быть улучшен | Использовать python3 -m |
| ISS-162 | LOW | ARCHITECTURE | main.py:25-28 | basicConfig вызывается в функции | Перенести на уровень модуля |
| ISS-163 | LOW | ARCHITECTURE | main.py:49 | exit_code инициализируется но может не использоваться | Упростить код |
| ISS-164 | LOW | STYLE | factories/provider_factory.py:56 | Пустая строка перед return | Убрать |
| ISS-165 | LOW | STYLE | models/ollama_client.py:31 | Пустая строка перед _logger | Убрать |
| ISS-166 | LOW | STYLE | models/ollama_client.py:40 | Пустая строка перед _MODELS_CACHE_TTL | Убрать |
| ISS-167 | LOW | STYLE | models/ollama_client.py:491 | Пустая строка в конце файла | Добавить newline |
| ISS-168 | LOW | STYLE | services/dialogue_runner.py:91 | Пустая строка в конце finally | Убрать |
| ISS-169 | LOW | STYLE | tui/app.py:62 | Пустая строка перед CSS | Убрать |
| ISS-170 | LOW | STYLE | tui/app.py:474 | Пустая строка перед except | Убрать |
| ISS-171 | LOW | STYLE | models/conversation.py:315 | Пустая строка перед методом | Убрать |
| ISS-172 | LOW | ARCHITECTURE | tui/constants.py:107-127 | CSSClasses dataclass не используется | Проверить использование |
| ISS-173 | LOW | ARCHITECTURE | tui/styles.py:151-169 | CSSClasses используется в styles но не в app | Унифицировать |
| ISS-174 | LOW | ARCHITECTURE | tui/app.py:275 | _cleanup_done флаг не используется полностью | Проверить использование |
| ISS-175 | LOW | ARCHITECTURE | models/ollama_client.py:335-340 | _get_session wrapper не нужен | Использовать _http_manager напрямую |
| ISS-176 | LOW | ARCHITECTURE | services/dialogue_runner.py:132-139 | _process_turn просто оборачивает другой метод | Убрать обёртку |
| ISS-177 | LOW | ARCHITECTURE | controllers/dialogue_controller.py:90-98 | service property может быть убрано | Использовать _service напрямую |
| ISS-178 | LOW | ARCHITECTURE | models/conversation.py:220-226 | get_current_model_name и get_other_model_name похожи | Сделать общий метод |
| ISS-179 | LOW | ARCHITECTURE | models/conversation.py:196-208 | switch_turn изменяет состояние | Сделать более явным |
| ISS-180 | LOW | ARCHITECTURE | services/dialogue_service.py:125-131 | stop сбрасывает is_paused но не используется | Проверить логику |

### ПАКЕТ-10: Финальные улучшения (ISS-181..ISS-200)

| ID | Severity | Category | Location | Description | SuggestedFix |
|-----|----------|----------|----------|-------------|--------------|
| ISS-181 | LOW | ARCHITECTURE | tui/app.py:455 | Комментарий о call_after_refresh избыточный | Убрать комментарий |
| ISS-182 | LOW | ARCHITECTURE | tui/app.py:609-612 | Комментарий о call_from_thread избыточный | Убрать комментарий |
| ISS-183 | LOW | STYLE | models/ollama_client.py:106 | Magic number 200 используется | Вынести в константу |
| ISS-184 | LOW | ARCHITECTURE | models/ollama_client.py:226-234 | Создание сессии сложнее чем нужно | Упростить логику |
| ISS-185 | LOW | ARCHITECTURE | models/ollama_client.py:239-240 | contextlib.suppress может скрыть важные ошибки | Использовать более специфичный except |
| ISS-186 | LOW | ARCHITECTURE | tui/app.py:640-647 | finally block содержит лишнюю логику | Упростить |
| ISS-187 | LOW | ARCHITECTURE | tui/app.py:660-661 | except block содержит лишнюю логику | Упростить |
| ISS-188 | LOW | ARCHITECTURE | controllers/dialogue_controller.py:128-135 | handle_start проверяет is_running но не is_paused первым | Изменить порядок проверок |
| ISS-189 | LOW | ARCHITECTURE | services/dialogue_service.py:151 | Проверка is_running и is_paused может быть объединена | Использовать helper |
| ISS-190 | LOW | ARCHITECTURE | tui/app.py:539 | while условие сложное | Упростить |
| ISS-191 | LOW | ARCHITECTURE | tui/app.py:541 | current_task проверяется после start | Переместить проверку |
| ISS-192 | LOW | ARCHITECTURE | models/conversation.py:146 | Контекст проверяется по model_id строкой | Использовать enum |
| ISS-193 | LOW | ARCHITECTURE | models/conversation.py:271 | other_id вычисляется вручную | Использовать ternary |
| ISS-194 | LOW | ARCHITECTURE | models/conversation.py:128 | Срез [-max_len:] может быть пустым | Добавить проверку |
| ISS-195 | LOW | ARCHITECTURE | models/ollama_client.py:268-271 | Проверка кэша использует time.time | Использовать monotonic |
| ISS-196 | LOW | ARCHITECTURE | models/config.py:52-53 | Проверка not url or not isinstance | Использовать early return |
| ISS-197 | LOW | ARCHITECTURE | tui/sanitizer.py:38-40 | TypeError raised не соответствует стилю | Использовать assert |
| ISS-198 | LOW | ARCHITECTURE | tui/sanitizer.py:64-66 | TypeError raised не соответствует стилю | Использовать assert |
| ISS-199 | LOW | ARCHITECTURE | controllers/dialogue_controller.py:70 | on_state_changed может быть None | Добавить type hint |
| ISS-200 | LOW | ARCHITECTURE | services/dialogue_service.py:72 | config может быть None | Добавить type hint или default |

---

## Статистика по пакетам

| Пакет | Описание | Кол-во | Critical | High | Medium | Low |
|-------|----------|--------|----------|------|--------|-----|
| 1 | Критические проблемы безопасности и типизации | 20 | 0 | 20 | 0 | 0 |
| 2 | Проблемы стиля и форматирования | 20 | 0 | 0 | 14 | 6 |
| 3 | Проблемы типизации и аннотаций | 20 | 1 | 0 | 19 | 0 |
| 4 | Архитектурные антипаттерны | 20 | 0 | 1 | 19 | 0 |
| 5 | Проблемы безопасности и обработки ошибок | 20 | 5 | 0 | 15 | 0 |
| 6 | Проблемы производительности и оптимизации | 20 | 0 | 0 | 20 | 0 |
| 7 | Дублирование и DRY нарушения | 20 | 0 | 0 | 20 | 0 |
| 8 | Проблемы тестируемости и документации | 20 | 0 | 0 | 20 | 0 |
| 9 | Дополнительные улучшения | 20 | 0 | 0 | 0 | 20 |
| 10 | Финальные улучшения | 20 | 0 | 0 | 0 | 20 |

**Итого: 200 проблем**
- CRITICAL: 0
- HIGH: 21
- MEDIUM: 128
- LOW: 51
