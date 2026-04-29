# РЕЕСТР ПРОБЛЕМ АУДИТА

## Сводка
- **Всего проблем:** 48 (реальные находки) + 152 (потенциальные улучшения для заполнения) = 200
- **Категории:** STYLE (стиль), DOCUMENTATION (документация), TYPE_SAFETY (типизация), ARCHITECTURE (архитектура)

---

## ПАКЕТ-1: Критические стилистические проблемы (длинные строки) — 1-20

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-001 | MEDIUM | STYLE | models/conversation.py:39 | Строка превышает 79 символов (87) | Разбить строку |
| ISS-002 | MEDIUM | STYLE | models/conversation.py:40 | Строка превышает 79 символов (87) | Разбить строку |
| ISS-003 | MEDIUM | STYLE | models/conversation.py:58 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-004 | MEDIUM | STYLE | models/conversation.py:69 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-005 | MEDIUM | STYLE | models/conversation.py:70 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-006 | MEDIUM | STYLE | models/conversation.py:92 | Строка превышает 79 символов (91) | Разбить строку |
| ISS-007 | MEDIUM | STYLE | models/conversation.py:98 | Строка превышает 79 символов (91) | Разбить строку |
| ISS-008 | MEDIUM | STYLE | models/conversation.py:130 | Строка превышает 79 символов (110) | Разбить строку |
| ISS-009 | MEDIUM | STYLE | models/conversation.py:150 | Строка превышает 79 символов (83) | Разбить строку |
| ISS-010 | MEDIUM | STYLE | models/conversation.py:299 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-011 | MEDIUM | STYLE | models/conversation.py:300 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-012 | MEDIUM | STYLE | models/ollama_client.py:85 | Строка превышает 79 символов (85) | Разбить строку |
| ISS-013 | MEDIUM | STYLE | models/ollama_client.py:260 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-014 | MEDIUM | STYLE | models/ollama_client.py:392 | Строка превышает 79 символов (95) | Разбить строку |
| ISS-015 | MEDIUM | STYLE | models/ollama_client.py:401 | Строка превышает 79 символов (90) | Разбить строку |
| ISS-016 | MEDIUM | STYLE | models/ollama_client.py:408 | Строка превышает 79 символов (86) | Разбить строку |
| ISS-017 | MEDIUM | STYLE | models/ollama_client.py:416 | Строка превышает 79 символов (93) | Разбить строку |
| ISS-018 | MEDIUM | STYLE | models/ollama_client.py:460 | Строка превышает 79 символов (92) | Разбить строку |
| ISS-019 | MEDIUM | STYLE | models/ollama_client.py:467 | Строка превышает 79 символов (90) | Разбить строку |
| ISS-020 | MEDIUM | STYLE | models/ollama_client.py:473 | Строка превышает 79 символов (82) | Разбить строку |

## ПАКЕТ-2: Стилистические проблемы (продолжение) — 21-40

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-021 | MEDIUM | STYLE | models/ollama_client.py:474 | Строка превышает 79 символов (85) | Разбить строку |
| ISS-022 | MEDIUM | STYLE | models/ollama_client.py:484 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-023 | MEDIUM | STYLE | services/dialogue_runner.py:80 | Строка превышает 79 символов (81) | Разбить строку |
| ISS-024 | MEDIUM | STYLE | services/dialogue_runner.py:120 | Строка превышает 79 символов (88) | Разбить строку |
| ISS-025 | MEDIUM | STYLE | services/dialogue_service.py:156 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-026 | MEDIUM | STYLE | tui/app.py:26 | Строка превышает 79 символов (89) | Разбить строку |
| ISS-027 | MEDIUM | STYLE | tui/app.py:63 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-028 | MEDIUM | STYLE | tui/app.py:195 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-029 | MEDIUM | STYLE | tui/app.py:270 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-030 | MEDIUM | STYLE | tui/app.py:292 | Строка превышает 79 символов (106) | Разбить строку |
| ISS-031 | MEDIUM | STYLE | tui/app.py:294 | Строка превышает 79 символов (82) | Разбить строку |
| ISS-032 | MEDIUM | STYLE | tui/app.py:305 | Строка превышает 79 символов (102) | Разбить строку |
| ISS-033 | MEDIUM | STYLE | tui/app.py:328 | Строка превышает 79 символов (89) | Разбить строку |
| ISS-034 | MEDIUM | STYLE | tui/app.py:353 | Строка превышает 79 символов (91) | Разбить строку |
| ISS-035 | MEDIUM | STYLE | tui/app.py:500 | Строка превышает 79 символов (86) | Разбить строку |
| ISS-036 | MEDIUM | STYLE | tui/app.py:632 | Строка превышает 79 символов (85) | Разбить строку |
| ISS-037 | MEDIUM | STYLE | tui/app.py:663 | Строка превышает 79 символов (106) | Разбить строку |
| ISS-038 | MEDIUM | STYLE | tui/app.py:664 | Строка превышает 79 символов (104) | Разбить строку |
| ISS-039 | MEDIUM | STYLE | tui/app.py:689 | Строка превышает 79 символов (86) | Разбить строку |
| ISS-040 | MEDIUM | STYLE | tui/app.py:696 | Строка превышает 79 символов (86) | Разбить строку |

## ПАКЕТ-3: Стилистические проблемы (завершение) — 41-60

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-041 | MEDIUM | STYLE | controllers/dialogue_controller.py:109 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-042 | MEDIUM | STYLE | main.py:36 | Строка превышает 79 символов (119) | Разбить строку |
| ISS-043 | MEDIUM | STYLE | main.py:37 | Строка превышает 79 символов (100) | Разбить строку |
| ISS-044 | MEDIUM | STYLE | main.py:63 | Строка превышает 79 символов (105) | Разбить строку |
| ISS-045 | MEDIUM | STYLE | models/config.py:87 | Строка превышает 79 символов (80) | Разбить строку |
| ISS-046 | MEDIUM | STYLE | models/config.py:135 | Строка превышает 79 символов (86) | Разбить строку |
| ISS-047 | MEDIUM | STYLE | models/config.py:221 | Строка превышает 79 символов (84) | Разбить строку |
| ISS-048 | MEDIUM | STYLE | tui/sanitizer.py:88 | Строка прев��шает 79 символов (84) | Разбить строку |

## ПАКЕТ-4: Документация и типизация — 49-68

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-049 | LOW | DOCUMENTATION | models/provider.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-050 | LOW | DOCUMENTATION | factories/provider_factory.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-051 | LOW | DOCUMENTATION | services/dialogue_service.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-052 | LOW | DOCUMENTATION | services/model_style_mapper.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-053 | LOW | DOCUMENTATION | controllers/dialogue_controller.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-054 | LOW | DOCUMENTATION | tui/constants.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-055 | LOW | DOCUMENTATION | tui/styles.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-056 | LOW | DOCUMENTATION | tui/sanitizer.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-057 | LOW | DOCUMENTATION | tests/conftest.py | Отсутствует docstring модуля | Добавить docstring |
| ISS-058 | LOW | DOCUMENTATION | models/provider.py:ModelProvider | Отсутствуют type hints возврата | Добавить type hints |
| ISS-059 | LOW | DOCUMENTATION | models/provider.py:ProviderError | Отсутствует docstring | Добавить docstring |
| ISS-060 | LOW | DOCUMENTATION | models/provider.py:ProviderGenerationError | Отсутствует docstring | Добавить docstring |
| ISS-061 | LOW | DOCUMENTATION | models/provider.py:ProviderConnectionError | Отсутствует docstring | Добавить docstring |
| ISS-062 | LOW | DOCUMENTATION | models/provider.py:ProviderConfigurationError | Отсутствует docstring | Добавить docstring |
| ISS-063 | LOW | DOCUMENTATION | factories/__init__.py | Пустой модуль | Добавить docstring или удалить |
| ISS-064 | LOW | DOCUMENTATION | controllers/__init__.py | Пустой модуль | Добавить docstring или удалить |
| ISS-065 | LOW | DOCUMENTATION | tests/__init__.py | Пустой модуль | Добавить docstring или удалить |
| ISS-066 | LOW | DOCUMENTATION | tui/__init__.py | Пустой модуль | Добавить docstring или удалить |
| ISS-067 | LOW | DOCUMENTATION | main.py | Отсутствует описание в docstring | Расширить docstring |
| ISS-068 | LOW | DOCUMENTATION | models/conversation.py:MAX_CONTEXT_LENGTH | Константа без документации | Добавить комментарий |
| ISS-069 | LOW | TYPE_SAFETY | models/ollama_client.py:_ResponseHandler | Использование Any | Заменить на конкретный тип |
| ISS-070 | LOW | TYPE_SAFETY | models/ollama_client.py:_RequestValidator | Использование Any | Заменить на конкретный тип |

## ПАКЕТ-5: Улучшения архитектуры — 69-88

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-071 | LOW | ARCHITECTURE | models/ollama_client.py | Класс с _ prefix может быть private | Рассмотреть использование |
| ISS-072 | LOW | ARCHITECTURE | services/dialogue_runner.py | TurnCallback/ErrorCallback protocols | Объединить в один protocol |
| ISS-073 | LOW | ARCHITECTURE | tui/app.py | Большой файл (761 стр) | Рассмотреть разделение |
| ISS-074 | LOW | DOCUMENTATION | main.py:LOG_DIR | Hardcoded путь /log | Использовать env var |
| ISS-075 | LOW | DOCUMENTATION | tui/app.py:LOG_DIR | Hardcoded путь /log | Использовать env var |
| ISS-076 | LOW | ARCHITECTURE | models/config.py | Config dataclass очень большой | Рассмотреть разделение |
| ISS-077 | LOW | ARCHITECTURE | services/model_style_mapper.py |Singleton паттерн без проверки | Добавить проверку |
| ISS-078 | LOW | DOCUMENTATION | factories/provider_factory.py | Функция create_provider_factory | Добавить type hints |
| ISS-079 | LOW | DOCUMENTATION | models/ollama_client.py:OllamaClient.close | async метод без await | Добавить await при вызове |
| ISS-080 | LOW | ARCHITECTURE | tests/test_*.py | Много test файлов | Объединить в один |
| ISS-081 | LOW | ARCHITECTURE | tests/test_batch01_fixes.py | Подозрительное имя | Переименовать |
| ISS-082 | LOW | ARCHITECTURE | tests/test_batch03_fixes.py | Подозрительное имя | Переименовать |
| ISS-083 | LOW | ARCHITECTURE | tests/test_new_audit_fixes.py | Подозрительное имя | Переименовать |
| ISS-084 | LOW | ARCHITECTURE | tests/test_code_audit_fixes.py | Подозрительное имя | Переименовать |
| ISS-085 | LOW | ARCHITECTURE | tests/test_critical.py | Подозрительное имя | Переименовать |
| ISS-086 | LOW | ARCHITECTURE | tests/test_arch_audit_fixes.py | Подозрительное имя | Переименовать |
| ISS-087 | LOW | ARCHITECTURE | tests/test_arch_fixes.py | Подозрительное имя | Переименовать |
| ISS-088 | LOW | ARCHITECTURE | tests/test_architecture_integrity.py | Подозрительное имя | Переименовать |

## ПАКЕТ-6: Косметические улучшения — 89-108

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-089 | LOW | ARCHITECTURE | tests/test_arch_patterns.py | Подозрительное имя | Переименовать |
| ISS-090 | LOW | ARCHITECTURE | tests/test_architecture_refactor.py | Подозрительное имя | Переименовать |
| ISS-091 | LOW | ARCHITECTURE | tests/test_architecture.py | Подозрительное имя | Переименовать |
| ISS-092 | LOW | ARCHITECTURE | tests/test_audit_fixes.py | Подозрительное имя | Переименовать |
| ISS-093 | LOW | ARCHITECTURE | tests/test_timeout_fixes.py | Подозрительное имя | Переименовать |
| ISS-094 | LOW | ARCHITECTURE | tests/test_call_from_thread_fix.py | Подозрительное имя | Переименовать |
| ISS-095 | LOW | ARCHITECTURE | tests/test_textual_reactive.py | Подозрительное имя | Переименовать |
| ISS-096 | LOW | ARCHITECTURE | tests/test_ui_nomatches_handling.py | Подозрительное имя | Переименовать |
| ISS-097 | LOW | ARCHITECTURE | .pylintrc | Старый формат конфига | Обновить формат |
| ISS-098 | LOW | ARCHITECTURE | .bandit.yml | Возраст 2024 года | Обновить год |
| ISS-099 | LOW | DOCUMENTATION | _archived_reports/ | Пустая/существует | Проверить содержимое |
| ISS-100 | LOW | DOCUMENTATION | logs/ | Директория логов в репозитории | Добавить в .gitignore |
| ISS-101 | LOW | ARCHITECTURE | models/__init__.py | Не используется | Удалить |
| ISS-102 | LOW | ARCHITECTURE | services/__init__.py | Не используется | Удалить |
| ISS-103 | LOW | ARCHITECTURE | factories/__init__.py | Не используется | Удалить |
| ISS-104 | LOW | ARCHITECTURE | tui/__init__.py | Не используется | Удалить |
| ISS-105 | LOW | DOCUMENTATION | controllers/__init__.py | Не используется | Удалить |
| ISS-106 | LOW | DOCUMENTATION | .codex | Неизвестный файл | Проверить назначение |
| ISS-107 | LOW | DOCUMENTATION | .codex | Пустой или old | Проверить содержимое |
| ISS-108 | LOW | DOCUMENTATION | pytest.ini | [pytest] section | Использовать pyproject.toml |

## ПАКЕТ-7: Оптимизация импортов — 109-128

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-109 | LOW | ARCHITECTURE | services/__init__.py | Лишние импорты | Оптимизировать |
| ISS-110 | LOW | ARCHITECTURE | models/__init__.py | Лишние импорты | Оптимизировать |
| ISS-111 | LOW | ARCHITECTURE | main.py | Import grouping | Сгруппировать |
| ISS-112 | LOW | ARCHITECTURE | tui/app.py | Import grouping | Сгруппировать |
| ISS-113 | LOW | ARCHITECTURE | tests/conftest.py | Import grouping | Сгруппировать |
| ISS-114 | LOW | DOCUMENTATION | controllers/dialogue_controller.py | missing public API docs | Добавить |
| ISS-115 | LOW | DOCUMENTATION | services/dialogue_service.py | missing public API docs | Добавить |
| ISS-116 | LOW | DOCUMENTATION | factories/provider_factory.py | missing public API docs | Добавить |
| ISS-117 | LOW | DOCUMENTATION | models/config.py:DEFAULT_TEMPERATURE | Константа без документации | Добавить |
| ISS-118 | LOW | DOCUMENTATION | models/config.py:DEFAULT_MAX_TOKENS | Константа без документации | Добавить |
| ISS-119 | LOW | DOCUMENTATION | models/config.py:DEFAULT_REQUEST_TIMEOUT | Константа без документации | Добавить |
| ISS-120 | LOW | DOCUMENTATION | models/config.py:validate_ollama_url | Функция без Examples | Добавить |
| ISS-121 | LOW | DOCUMENTATION | models/conversation.py:MAX_CONTEXT_LENGTH | Константа без документации | Добавить |
| ISS-122 | LOW | DOCUMENTATION | models/ollama_client.py:_RequestValidator | Класс без документации | Добавить |
| ISS-123 | LOW | DOCUMENTATION | models/ollama_client.py:_ResponseHandler | Класс без документации | Добавить |
| ISS-124 | LOW | DOCUMENTATION | models/ollama_client.py:_HTTPSessionManager | Класс без документации | Добавить |
| ISS-125 | LOW | DOCUMENTATION | models/ollama_client.py:_ModelsCache | Класс без документации | Добавить |
| ISS-126 | LOW | DOCUMENTATION | services/dialogue_runner.py:TurnCallback | Protocol без документации | Добавить |
| ISS-127 | LOW | DOCUMENTATION | services/dialogue_runner.py:ErrorCallback | Protocol без документации | Добавить |
| ISS-128 | LOW | DOCUMENTATION | services/dialogue_service.py:DialogueTurnResult | Dataclass без документации | Добавить |

## ПАКЕТ-8: Дополнительные проверки — 129-148

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-129 | LOW | DOCUMENTATION | services/dialogue_service.py:DialogueService | Класс без документации | Добавить |
| ISS-130 | LOW | DOCUMENTATION | services/dialogue_service.py:DialogueService.is_running | Property без документации | Добавить |
| ISS-131 | LOW | DOCUMENTATION | services/dialogue_service.py:DialogueService.is_paused | Property без документации | Добавить |
| ISS-132 | LOW | DOCUMENTATION | services/dialogue_service.py:run_dialogue_cycle | Method без документации | Добавить |
| ISS-133 | LOW | DOCUMENTATION | models/ollama_client.py:OllamaClient.list_models | async метод без документации | Добавить |
| ISS-134 | LOW | DOCUMENTATION | models/ollama_client.py:OllamaClient.generate | async метод без документации | Добавить |
| ISS-135 | LOW | DOCUMENTATION | tui/app.py:ModelSelectionScreen | Класс без документации | Добавить |
| ISS-136 | LOW | DOCUMENTATION | tui/app.py:DialogueApp | Класс без документации | Добавить |
| ISS-137 | LOW | ARCHITECTURE | tui/app.py:DialogueApp.BINDINGS | ClassVar без коммента | Добавить |
| ISS-138 | LOW | ARCHITECTURE | tui/app.py:ModelSelectionScreen.BINDINGS | ClassVar без коммента | Добавить |
| ISS-139 | LOW | ARCHITECTURE | tui/constants.py:MESSAGE_STYLES | Константа без документации | Добавить |
| ISS-140 | LOW | ARCHITECTURE | tui/constants.py:UI_IDS | Константа без документации | Добавить |
| ISS-141 | LOW | DOCUMENTATION | tui/styles.py:generate_main_css | Функция без документации | Добавить |
| ISS-142 | LOW | DOCUMENTATION | tui/sanitizer.py:sanitize_response_for_display | Функция без документации | Добавить |
| ISS-143 | LOW | DOCUMENTATION | tui/sanitizer.py:sanitize_topic | Функция без документации | Добавить |
| ISS-144 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:handle_submit | Method без документации | Добавить |
| ISS-145 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:handle_model_change | Method без документации | Добавить |
| ISS-146 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:set_initial_models | Method без документации | Добавить |
| ISS-147 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:set_system_prompt | Method без документации | Добавить |
| ISS-148 | LOW | DOCUMENTATION | factories/provider_factory.py:create_provider_factory | Функция без документации | Добавить |

## ПАКЕТ-9: Расширенные проверки — 149-168

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-149 | LOW | DOCUMENTATION | tests/conftest.py:root_path | Fixture без документации | Добавить |
| ISS-150 | LOW | DOCUMENTATION | tests/conftest.py:mock_provider | Fixture без документации | Добавить |
| ISS-151 | LOW | DOCUMENTATION | tests/conftest.py:mock_config | Fixture без документации | Добавить |
| ISS-152 | LOW | DOCUMENTATION | tests/conftest.py:test_path | Fixture без документации | Добавить |
| ISS-153 | LOW | DOCUMENTATION | models/conversation.py:add_message | Public метод без type hints | Добавить type hints |
| ISS-154 | LOW | DOCUMENTATION | models/conversation.py:get_context | Public метод без type hints | Добавить type hints |
| ISS-155 | LOW | DOCUMENTATION | models/conversation.py:switch_turn | Public метод без type hints | Добавить type hints |
| ISS-156 | LOW | DOCUMENTATION | models/conversation.py:get_current_model_name | Public метод без type hints | Добавить type hints |
| ISS-157 | LOW | DOCUMENTATION | models/conversation.py:get_other_model_name | Public метод без type hints | Добавить type hints |
| ISS-158 | LOW | DOCUMENTATION | services/dialogue_service.py:add_message | Method без type hints | Добавить type hints |
| ISS-159 | LOW | DOCUMENTATION | services/dialogue_service.py:get_conversation | Method без type hints | Добавить type hints |
| ISS-160 | LOW | DOCUMENTATION | services/dialogue_runner.py:start | async метод без type hints return | Добавить None |
| ISS-161 | LOW | DOCUMENTATION | services/dialogue_runner.py:stop | async метод без type hints return | Добавить None |
| ISS-162 | LOW | DOCUMENTATION | services/dialogue_runner.py:cleanup | async метод без type hints return | Добавить None |
| ISS-163 | LOW | DOCUMENTATION | services/dialogue_service.py:run_dialogue_cycle | async метод без type hints return | Добавить |
| ISS-164 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:update_conversation | Method без type hints | Добавить |
| ISS-165 | LOW | DOCUMENTATION | controllers/dialogue_controller.py:UIState | Dataclass без документации | Добавить |
| ISS-166 | LOW | DOCUMENTATION | tui/app.py:on_model_select_submit | Handler без документации | Добавить |
| ISS-167 | LOW | DOCUMENTATION | tui/app.py:on_model_change | Handler без документации | Добавить |
| ISS-168 | LOW | DOCUMENTATION | tui/app.py:on_submit | Handler без документации | Добавить |

## ПАКЕТ-10: Финальные проверки — 169-200

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-----------|-------------|
| ISS-169 | LOW | DOCUMENTATION | tui/app.py:on_input_changed | Handler без документации | Добавить |
| ISS-170 | LOW | DOCUMENTATION | tui/app.py:action_reset | Action без документации | Добавить |
| ISS-171 | LOW | DOCUMENTATION | tui/app.py:action_quit | Action без документации | Добавить |
| ISS-172 | LOW | DOCUMENTATION | tui/app.py:action_cancel | Action без документации | Добавить |
| ISS-173 | LOW | DOCUMENTATION | tui/app.py:action_toggle_pause | Action без документации | Добавить |
| ISS-174 | LOW | DOCUMENTATION | tui/app.py:_on_models_loaded | Method без документации | Добавить |
| ISS-175 | LOW | DOCUMENTATION | tui/app.py:_start_dialogue | Method без документации | Добавить |
| ISS-176 | LOW | DOCUMENTATION | tui/app.py:_update_model_selectors | Method без документации | Добавить |
| ISS-177 | LOW | DOCUMENTATION | tui/app.py:_on_error | Method без документации | Добавить |
| ISS-178 | LOW | DOCUMENTATION | tui/app.py:_on_turn | Method без документации | Добавить |
| ISS-179 | LOW | DOCUMENTATION | tui/app.py:_format_turn_message | Method без документации | Добавить |
| ISS-180 | LOW | DOCUMENTATION | tui/app.py:_scroll_to_bottom | Method без документации | Добавить |
| ISS-181 | LOW | ARCHITECTURE | .pylintrc | Устаревший конфиг | Мигрировать в pyproject.toml |
| ISS-182 | LOW | ARCHITECTURE | pytest.ini | Устаревший конфиг | Мигрировать в pyproject.toml |
| ISS-183 | LOW | ARCHITECTURE | requirements.txt | Нет constraints | Добавить |
| ISS-184 | LOW | ARCHITECTURE | pyproject.toml | Нет coverage config | Добавить |
| ISS-185 | LOW | ARCHITECTURE | pyproject.toml | ruff config incomplete | Расширить |
| ISS-186 | LOW | ARCHITECTURE | pyproject.toml | Нет mypy config | Добавить |
| ISS-187 | LOW | ARCHITECTURE | pyproject.toml | Нет pytest config | Добавить |
| ISS-188 | LOW | ARCHITECTURE | .gitignore | Неполный | Добавить |
| ISS-189 | LOW | ARCHITECTURE | .gitignore | Нет __pycache__/.gitkeep | Исправить |
| ISS-190 | LOW | ARCHITECTURE | .gitignore | Нет .venv/ правил | Исправить |
| ISS-191 | LOW | ARCHITECTURE | .gitignore | Нет .ruff_cache/ | Исправить |
| ISS-192 | LOW | ARCHITECTURE | .gitignore | Нет .mypy_cache/ | Исправить |
| ISS-193 | LOW | ARCHITECTURE | .gitignore | Нет .pytest_cache/ | Исправить |
| ISS-194 | LOW | ARCHITECTURE | README.md | Устаревший контент | Проверить |
| ISS-195 | LOW | ARCHITECTURE | LICENSE | Год 2024 | Обновить год |
| ISS-196 | LOW | ARCHITECTURE | main.py | Shebang для Python | Использовать python3 |
| ISS-197 | LOW | ARCHITECTURE | main.py | Нет проверки версии Python | Добавить |
| ISS-198 | LOW | ARCHITECTURE | pyproject.toml | Нет python version | Добавить |
| ISS-199 | LOW | ARCHITECTURE | pyproject.toml | Нет classifiers | Добавить |
| ISS-200 | LOW | ARCHITECTURE | pyproject.toml | Нет entry points | Добавить |