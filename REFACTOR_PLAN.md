# Autonomous Refactoring Issue Registry
# Generated: 2026-04-21
# Total Issues: 200

## Summary Statistics

| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
|----------|----------|------|--------|-----|-------|
| STYLE | 0 | 0 | 45 | 80 | 125 |
| TYPE_SAFETY | 0 | 0 | 25 | 15 | 40 |
| ARCHITECTURE | 0 | 5 | 10 | 0 | 15 |
| DEPRECATED | 0 | 0 | 5 | 0 | 5 |
| UNUSED | 0 | 0 | 10 | 5 | 15 |
| **Total** | **0** | **5** | **95** | **100** | **200** |

---

## Issue Registry

### ПАКЕТ-1: Критические архитектурные проблемы (ISS-001 - ISS-020)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-001 | HIGH | ARCHITECTURE | models/conversation.py:26 | Conversation class uses @dataclass(slots=True) but defines __init__ which conflicts with slots | Remove custom __init__ or switch to regular dataclass without slots |
| ISS-002 | HIGH | ARCHITECTURE | models/conversation.py:73-88 | __post_init__ called from __init__ creates dual initialization path | Move __post_init__ logic into __init__ or remove __post_init__ override |
| ISS-003 | HIGH | ARCHITECTURE | models/conversation.py:304 | Bare except: catches all exceptions including SystemExit and KeyboardInterrupt | Change to `except Exception` to avoid catching system exits |
| ISS-004 | HIGH | ARCHITECTURE | models/ollama_client.py:419-499 | generate() method has too many responsibilities | Extract request building and response parsing into separate methods |
| ISS-005 | HIGH | ARCHITECTURE | models/ollama_client.py:46-163 | Helper classes (_RequestValidator, _ResponseHandler) are not properly encapsulated | Consider moving to separate module |
| ISS-006 | HIGH | ARCHITECTURE | tui/app.py:290-292 | reactive() call should use proper type annotation | Use `reactive[str]` instead of type: ignore |
| ISS-007 | HIGH | ARCHITECTURE | tui/app.py:331-348 | _on_ui_state_changed has too many exception handlers | Consolidate error handling or split into smaller methods |
| ISS-008 | HIGH | ARCHITECTURE | services/dialogue_service.py:22-37 | DialogueTurnResult dataclass duplicates Conversation.process_turn return type | Consider using typing.NamedTuple or remove duplication |
| ISS-009 | HIGH | ARCHITECTURE | tui/app.py:398-517 | _setup_conversation creates many nested callbacks | Consider using async/await pattern instead of callbacks |
| ISS-010 | HIGH | ARCHITECTURE | tui/app.py:570-616 | _run_dialogue async method is too long | Split into smaller focused methods |
| ISS-011 | MEDIUM | TYPE_SAFETY | models/conversation.py:50 | Line too long (111 chars) - violates E501 | Break line into multiple lines for readability |
| ISS-012 | MEDIUM | TYPE_SAFETY | models/conversation.py:59 | Line too long (82 chars) | Break line into multiple lines |
| ISS-013 | MEDIUM | TYPE_SAFETY | models/conversation.py:107 | Line too long (88 chars) | Break line into multiple lines |
| ISS-014 | MEDIUM | TYPE_SAFETY | models/conversation.py:113 | Line too long (91 chars) | Break line into multiple lines |
| ISS-015 | MEDIUM | ARCHITECTURE | models/conversation.py:155-174 | _add_message_to_context has complex conditional logic | Simplify context management with helper method |
| ISS-016 | MEDIUM | ARCHITECTURE | models/conversation.py:246-268 | generate_response creates tuple then immediately unpacks | Return directly without intermediate tuple |
| ISS-017 | MEDIUM | ARCHITECTURE | models/ollama_client.py:317-355 | OllamaClient.__init__ does validation but doesn't handle all edge cases | Add validation for None host after config resolution |
| ISS-018 | MEDIUM | ARCHITECTURE | models/ollama_client.py:483-495 | Exception handling in generate() is redundant | Use single try-except for all error types |
| ISS-019 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:65-80 | state property creates new UIState copy every call | Consider caching or using @cached_property |
| ISS-020 | MEDIUM | ARCHITECTURE | tui/app.py:681-712 | on_unmount cleanup has nested try-except blocks | Refactor to use context manager or simplify logic |

### ПАКЕТ-2: Проблемы типизации (ISS-021 - ISS-040)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-021 | MEDIUM | TYPE_SAFETY | tui/app.py:290 | pyright: reportAttributeAccessIssue for reactive assignment | Add type: ignore with specific error code |
| ISS-022 | MEDIUM | TYPE_SAFETY | tui/app.py:339-342 | Type annotation issue with Label query result | Use cast() or proper type narrowing |
| ISS-023 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:70-90 | validate_messages accepts Sequence but expects list | Use proper type hint Sequence[Mapping[str, Any]] |
| ISS-024 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:227-245 | get_session async method missing return type annotation | Add explicit return type: aiohttp.ClientSession |
| ISS-025 | MEDIUM | TYPE_SAFETY | models/conversation.py:40 | _config field has union type but could be more specific | Use ConfigType instead of None for clarity |
| ISS-026 | MEDIUM | TYPE_SAFETY | models/conversation.py:200 | Return type is tuple[MessageDict, ...] but context is list | Ensure consistent return type throughout |
| ISS-027 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:56-70 | start() async method doesn't return awaitable properly | Ensure consistent async pattern |
| ISS-028 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:134-137 | _is_task_cancelled uses deprecated asyncio.current_task() | Use asyncio.get_running_loop().get_name() pattern |
| ISS-029 | MEDIUM | TYPE_SAFETY | controllers/dialogue_controller.py:52 | on_state_changed callback has weak type hint | Use more specific Callable type |
| ISS-030 | MEDIUM | TYPE_SAFETY | tui/sanitizer.py:12 | MAX_RESPONSE_PREVIEW_LENGTH is int but should be Final[int] | Add typing.Final annotation |
| ISS-031 | MEDIUM | TYPE_SAFETY | tui/app.py:276-303 | __init__ has many optional parameters | Use dataclass or typeddict for initialization |
| ISS-032 | MEDIUM | TYPE_SAFETY | tui/app.py:623-641 | _process_dialogue_turn has inconsistent return type | Return type should be consistent (DialogueTurnResult or None) |
| ISS-033 | MEDIUM | TYPE_SAFETY | models/provider.py:9 | Literal import but not used directly | Remove unused Literal import or use it |
| ISS-034 | MEDIUM | TYPE_SAFETY | models/config.py:232-250 | __post_init__ modifies object state after frozen=True | This violates immutability of frozen dataclass |
| ISS-035 | MEDIUM | TYPE_SAFETY | models/config.py:252-279 | _apply_env_overrides uses object.__setattr__ | Document why this is needed or refactor |
| ISS-036 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:133-160 | run_dialogue_cycle has complex control flow | Simplify with early returns or extract logic |
| ISS-037 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:48-67 | __init__ parameters are not validated | Add parameter validation |
| ISS-038 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:32-45 | Factory function creates new provider each time | Document lifecycle management |
| ISS-039 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:19-29 | create_ollama_provider ignores config's full potential | Use more config parameters |
| ISS-040 | MEDIUM | TYPE_SAFETY | models/config.py:78-106 | _validate_numeric_range is generic but has confusing name | Rename to validate_range or make more generic |

### ПАКЕТ-3: Проблемы стиля кода (ISS-041 - ISS-060)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-041 | LOW | STYLE | models/conversation.py:50 | Line exceeds 120 chars (ruff config) | Break into multiple lines |
| ISS-042 | LOW | STYLE | models/conversation.py:59 | Line exceeds 120 chars | Break into multiple lines |
| ISS-043 | LOW | STYLE | models/conversation.py:107 | Line exceeds 120 chars | Break into multiple lines |
| ISS-044 | LOW | STYLE | models/conversation.py:113 | Line exceeds 120 chars | Break into multiple lines |
| ISS-045 | LOW | STYLE | models/ollama_client.py:323-324 | __init__ parameters span multiple lines without consistent style | Align or use hanging indent |
| ISS-046 | LOW | STYLE | models/ollama_client.py:381-383 | Status validation call spans multiple lines | Consolidate or use intermediate variable |
| ISS-047 | LOW | STYLE | models/ollama_client.py:467-468 | Status validation call spans multiple lines | Consolidate or use intermediate variable |
| ISS-048 | LOW | STYLE | tui/app.py:290-292 | reactive assignment spans multiple lines | Use single line or different pattern |
| ISS-049 | LOW | STYLE | tui/app.py:509-511 | F-string spans multiple lines | Break into concatenation |
| ISS-050 | LOW | STYLE | tui/app.py:634-637 | Turn message formatting spans multiple lines | Use variable for intermediate formatting |
| ISS-051 | LOW | STYLE | controllers/dialogue_controller.py:74-80 | UIState construction spans many lines | Use single-line construction |
| ISS-052 | LOW | STYLE | models/conversation.py:81-84 | MessageDict construction spans multiple lines | Use single line |
| ISS-053 | LOW | STYLE | models/conversation.py:85-88 | MessageDict construction spans multiple lines | Use single line |
| ISS-054 | LOW | STYLE | models/conversation.py:321-328 | clear_contexts has inconsistent message construction | Standardize to single-line MessageDict |
| ISS-055 | LOW | STYLE | services/dialogue_runner.py:69-70 | create_task call spans multiple lines | Use single line |
| ISS-056 | LOW | STYLE | tui/sanitizer.py:81-87 | str.maketrans call spans many lines | Use dictionary literal |
| ISS-057 | LOW | STYLE | models/provider.py:12-40 | Exception classes have inconsistent docstring style | Standardize docstring format |
| ISS-058 | LOW | STYLE | models/provider.py:94-117 | Protocol class has bare ... for methods | Add docstrings to protocol methods |
| ISS-059 | LOW | STYLE | models/config.py:223-227 | Long string literal for default_system_prompt | Use implicit string concatenation |
| ISS-060 | LOW | STYLE | tui/constants.py:14-28 | Dataclass has inconsistent default formatting | Align all defaults to same style |

### ПАКЕТ-4: Неиспользуемый код (ISS-061 - ISS-080)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-061 | MEDIUM | UNUSED | models/provider.py:9 | Literal imported but used via MessageDict | Remove explicit Literal import |
| ISS-062 | MEDIUM | UNUSED | tui/app.py:13 | aiohttp imported but only used for ClientError | Import specific exception |
| ISS-063 | MEDIUM | UNUSED | models/conversation.py:9 | logging imported at module level but log used | Keep but document usage pattern |
| ISS-064 | MEDIUM | UNUSED | models/conversation.py:41-42 | _context_a and _context_b are duplicated in __init__ | Remove field defaults since __init__ redefines |
| ISS-065 | MEDIUM | UNUSED | models/conversation.py:47 | _initialized flag is set but only partially used | Review initialization logic |
| ISS-066 | MEDIUM | UNUSED | models/ollama_client.py:12 | time imported but used for cache timestamp | Document why time module is needed |
| ISS-067 | MEDIUM | UNUSED | models/ollama_client.py:36-40 | _DEFAULT_OPTIONS defined but not used in generate() | Remove or use consistently |
| ISS-068 | MEDIUM | UNUSED | models/ollama_client.py:141-163 | extract_models_list could be simplified | Consider using list comprehension |
| ISS-069 | MEDIUM | UNUSED | models/ollama_client.py:165-181 | extract_generation_response has redundant checks | Simplify logic |
| ISS-070 | MEDIUM | UNUSED | controllers/dialogue_controller.py:11-12 | TYPE_CHECKING imports not fully utilized | Review and remove unused imports |
| ISS-071 | MEDIUM | UNUSED | services/dialogue_service.py:10 | dataclass imported but DialogueTurnResult is simple | Consider using NamedTuple |
| ISS-072 | MEDIUM | UNUSED | services/dialogue_runner.py:13 | ProviderError imported but used indirectly | Remove unused import |
| ISS-073 | MEDIUM | UNUSED | services/dialogue_runner.py:99 | _is_task_cancelled check may be unnecessary | Consider removing for simplicity |
| ISS-074 | MEDIUM | UNUSED | factories/provider_factory.py:8 | Callable imported but type hints sufficient | Remove import if not needed |
| ISS-075 | MEDIUM | UNUSED | tui/app.py:31 | Select imported but query_one used instead | Remove if not needed |
| ISS-076 | MEDIUM | UNUSED | tui/app.py:38 | ProviderGenerationError imported but caught as ProviderError | Review exception handling |
| ISS-077 | MEDIUM | UNUSED | tui/app.py:51-62 | Comment block about call_from_thread vs call_after_refresh | Convert to proper docstring or remove |
| ISS-078 | MEDIUM | UNUSED | tui/styles.py:7 | from __future__ import annotations unused | Remove if Python 3.10+ only |
| ISS-079 | MEDIUM | UNUSED | tui/constants.py:10 | Final imported but not consistently used | Use consistently |
| ISS-080 | MEDIUM | UNUSED | tui/sanitizer.py:9 | html imported but html.escape used only twice | Consider inline or remove |

### ПАКЕТ-5: Устаревшие конструкции (ISS-081 - ISS-100)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-081 | MEDIUM | DEPRECATED | models/ollama_client.py:52-53 | __slots__ = () on static classes is redundant | Remove __slots__ or make it consistent |
| ISS-082 | MEDIUM | DEPRECATED | models/ollama_client.py:99-100 | __slots__ = () on static classes is redundant | Remove __slots__ or make it consistent |
| ISS-083 | MEDIUM | DEPRECATED | models/provider.py:51,63,75 | __slots__ = () on exception classes is redundant | Remove __slots__ from exceptions |
| ISS-084 | MEDIUM | DEPRECATED | models/conversation.py:26 | slots=True conflicts with custom __init__ | Remove slots=True and define __slots__ manually |
| ISS-085 | MEDIUM | DEPRECATED | models/config.py:198 | frozen=True conflicts with __post_init__ modifications | Remove frozen=True or refactor |
| ISS-086 | MEDIUM | DEPRECATED | models/config.py:278 | object.__setattr__ usage indicates design issue | Consider dataclass without frozen |
| ISS-087 | MEDIUM | DEPRECATED | services/dialogue_runner.py:136 | asyncio.current_task() deprecated pattern | Use asyncio.get_running_loop() |
| ISS-088 | MEDIUM | DEPRECATED | tui/app.py:618-621 | asyncio.current_task() deprecated pattern | Use asyncio.get_running_loop() |
| ISS-089 | MEDIUM | DEPRECATED | tui/app.py:294-296 | Lambda in __init__ creates closure capture | Use method reference or partial |
| ISS-090 | MEDIUM | DEPRECATED | services/dialogue_runner.py:115 | asyncio.sleep in loop may cause issues | Consider using asyncio.wait_for |
| ISS-091 | MEDIUM | ARCHITECTURE | models/ollama_client.py:184-255 | _HTTPSessionManager could use context manager protocol | Implement __aenter__/__aexit__ |
| ISS-092 | MEDIUM | ARCHITECTURE | models/ollama_client.py:257-314 | _ModelsCache could implement cache protocol | Consider adding clear method |
| ISS-093 | MEDIUM | ARCHITECTURE | models/config.py:232-279 | Config.__post_init__ does too much | Split into validators |
| ISS-094 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:17-34 | UIState dataclass should use slots=True | Add slots=True to UIState |
| ISS-095 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:22-37 | DialogueTurnResult should use slots=True | Add slots=True to DialogueTurnResult |
| ISS-096 | MEDIUM | ARCHITECTURE | tui/constants.py:13-28 | MessageStyles should use slots=True | Add slots=True |
| ISS-097 | MEDIUM | ARCHITECTURE | tui/constants.py:32-70 | UIElementIDs should use slots=True | Already has slots=True |
| ISS-098 | MEDIUM | ARCHITECTURE | tui/constants.py:73-88 | CSSClasses should use slots=True | Add slots=True |
| ISS-099 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:8 | TYPE_CHECKING import not used | Remove or add typing imports |
| ISS-100 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:11 | TYPE_CHECKING import only used for type hint | Keep for lazy imports |

### ПАКЕТ-6: Тестовые файлы - Проблемы стиля (ISS-101 - ISS-120)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-101 | LOW | STYLE | tests/test_batch01_fixes.py:13-14 | Unused imports F401 | Remove unused imports |
| ISS-102 | LOW | STYLE | tests/test_batch03_fixes.py:18,21 | Unused imports F401 | Remove unused imports |
| ISS-103 | LOW | STYLE | tests/test_batch03_fixes.py:127 | Line exceeds 79 chars | Break line |
| ISS-104 | LOW | STYLE | tests/test_batch03_fixes.py:235 | Line exceeds 79 chars | Break line |
| ISS-105 | LOW | STYLE | tests/test_batch03_fixes.py:272 | Line exceeds 79 chars | Break line |
| ISS-106 | LOW | STYLE | tests/test_batch03_fixes.py:280 | Line exceeds 79 chars | Break line |
| ISS-107 | LOW | STYLE | tests/test_batch03_fixes.py:284 | Line exceeds 79 chars | Break line |
| ISS-108 | LOW | STYLE | tests/test_batch03_fixes.py:289 | Line exceeds 79 chars | Break line |
| ISS-109 | LOW | STYLE | tests/test_batch03_fixes.py:296 | Line exceeds 79 chars | Break line |
| ISS-110 | LOW | STYLE | tests/test_batch03_fixes.py:298 | Line exceeds 79 chars | Break line |
| ISS-111 | LOW | STYLE | tests/test_batch03_fixes.py:308 | Line exceeds 79 chars | Break line |
| ISS-112 | LOW | STYLE | tests/test_call_from_thread_fix.py:5-7 | Lines exceed 79 chars | Break lines |
| ISS-113 | LOW | STYLE | tests/test_call_from_thread_fix.py:13 | Line exceeds 79 chars | Break line |
| ISS-114 | LOW | STYLE | tests/test_call_from_thread_fix.py:48 | Line exceeds 79 chars | Break line |
| ISS-115 | LOW | STYLE | tests/test_call_from_thread_fix.py:104-176 | Multiple lines exceed 79 chars | Break lines |
| ISS-116 | LOW | STYLE | tests/test_code_audit_fixes.py:46-65 | Lines exceed 79 chars | Break lines |
| ISS-117 | LOW | STYLE | tests/test_code_audit_fixes.py:65 | Whitespace before colon E203 | Remove whitespace |
| ISS-118 | LOW | STYLE | tests/test_code_audit_fixes.py:77-116 | Lines exceed 79 chars | Break lines |
| ISS-119 | LOW | STYLE | tests/test_audit_fixes.py:53-101 | Lines exceed 79 chars | Break lines |
| ISS-120 | LOW | STYLE | tests/test_audit_fixes.py:684 | Line exceeds 79 chars | Break line |

### ПАКЕТ-7: Тестовые файлы - Продолжение (ISS-121 - ISS-140)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-121 | LOW | STYLE | tests/test_audit_fixes_verification.py:118-195 | Lines exceed 79 chars | Break lines |
| ISS-122 | LOW | STYLE | tests/test_architecture.py:223-237 | Lines exceed 79 chars | Break lines |
| ISS-123 | LOW | STYLE | tests/test_architecture_integrity.py:168-819 | Many lines exceed 79 chars | Break lines |
| ISS-124 | LOW | STYLE | tests/test_architecture_patterns.py:46-197 | Many lines exceed 79 chars | Break lines |
| ISS-125 | LOW | STYLE | tests/test_architecture_refactor.py:34-168 | Lines exceed 79 chars | Break lines |
| ISS-126 | LOW | STYLE | tests/test_arch_audit_fixes.py:38-141 | Lines exceed 79 chars | Break lines |
| ISS-127 | LOW | STYLE | tests/test_arch_fixes.py | Review for style issues | Check and fix |
| ISS-128 | LOW | STYLE | tests/test_critical.py:15-642 | Many lines exceed 79 chars | Break lines |
| ISS-129 | LOW | STYLE | tests/test_dialogue_runner_error_handling.py:60-143 | Lines exceed 79 chars | Break lines |
| ISS-130 | LOW | STYLE | tests/test_fixes.py:4-225 | Lines exceed 79 chars | Break lines |
| ISS-131 | LOW | STYLE | tests/test_new_audit_fixes.py:11-352 | Lines exceed 79 chars | Break lines |
| ISS-132 | LOW | STYLE | tests/test_textual_reactive.py:32-35 | Lines exceed 79 chars | Break lines |
| ISS-133 | LOW | STYLE | tests/test_timeout_fixes.py:46-177 | Lines exceed 79 chars | Break lines |
| ISS-134 | LOW | STYLE | tests/test_ui_nomatches_handling.py:17 | Line exceeds 79 chars | Break line |
| ISS-135 | LOW | STYLE | tests/test_ui_shutdown_error.py:3-90 | Lines exceed 79 chars | Break lines |
| ISS-136 | LOW | STYLE | tests/test_ui_state_changed.py:7-183 | Lines exceed 79 chars | Break lines |
| ISS-137 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:131 | None passed to str parameter | Add type validation |
| ISS-138 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:274-310 | Type mismatch in context | Use proper MessageDict type |
| ISS-139 | MEDIUM | TYPE_SAFETY | tests/test_batch03_fixes.py:385-390 | Literal[123] passed to str parameter | Use proper string type |
| ISS-140 | MEDIUM | TYPE_SAFETY | tests/test_call_from_thread_fix.py:60 | Literal type mismatch | Use proper ModelId type |

### ПАКЕТ-8: Тестовые файлы - Окончание (ISS-141 - ISS-160)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-141 | MEDIUM | TYPE_SAFETY | tests/test_call_from_thread_fix.py:91-98 | Generator return type issues | Fix return type annotations |
| ISS-142 | MEDIUM | TYPE_SAFETY | tests/test_critical.py:276 | dict[str, str] not compatible with MessageDict | Use proper type |
| ISS-143 | MEDIUM | TYPE_SAFETY | tests/test_fixes.py:200-207 | Invalid type passed to validate_ollama_url | Use proper string type |
| ISS-144 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:109-123 | Tuple access issues - attribute not found | Fix tuple indexing |
| ISS-145 | MEDIUM | TYPE_SAFETY | tests/test_new_audit_fixes.py:191 | getsource None type issue | Handle None case |
| ISS-146 | MEDIUM | TYPE_SAFETY | tests/test_textual_reactive.py:54 | Tuple attribute access issue | Fix tuple handling |
| ISS-147 | MEDIUM | TYPE_SAFETY | tests/test_architecture_integrity.py:882 | tuple append - type error | Fix type handling |
| ISS-148 | MEDIUM | TYPE_SAFETY | tests/test_audit_fixes_verification.py:118 | UIState type incompatibility | Import proper type |
| ISS-149 | MEDIUM | TYPE_SAFETY | tests/test_arch_audit_fixes.py:46-48 | ast attribute access issues | Fix ast node handling |
| ISS-150 | LOW | STYLE | tests/test_arch_audit_fixes.py:46-89 | Lines exceed 79 chars | Break lines |
| ISS-151 | LOW | STYLE | tests/test_architecture_integrity.py:710-832 | Lines exceed 79 chars | Break lines |
| ISS-152 | LOW | STYLE | tests/test_architecture_patterns.py:46-197 | Lines exceed 79 chars | Break lines |
| ISS-153 | LOW | STYLE | tests/test_architecture_refactor.py | Lines exceed 79 chars | Break lines |
| ISS-154 | LOW | STYLE | tests/test_critical.py | Lines exceed 79 chars | Break lines |
| ISS-155 | LOW | STYLE | tests/test_dialogue_runner_error_handling.py | Lines exceed 79 chars | Break lines |
| ISS-156 | LOW | STYLE | tests/test_fixes.py | Lines exceed 79 chars | Break lines |
| ISS-157 | LOW | STYLE | tests/test_new_audit_fixes.py | Lines exceed 79 chars | Break lines |
| ISS-158 | LOW | STYLE | tests/test_timeout_fixes.py | Lines exceed 79 chars | Break lines |
| ISS-159 | LOW | STYLE | tests/test_ui_state_changed.py | Lines exceed 79 chars | Break lines |
| ISS-160 | LOW | STYLE | tests/test_ui_shutdown_error.py | Lines exceed 79 chars | Break lines |

### ПАКЕТ-9: Рефакторинг конфигурации и документации (ISS-161 - ISS-180)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-161 | LOW | STYLE | models/config.py | Multiple long lines need formatting | Format according to ruff config |
| ISS-162 | LOW | STYLE | models/conversation.py | Multiple long lines need formatting | Format according to ruff config |
| ISS-163 | LOW | STYLE | models/ollama_client.py | Multiple long lines need formatting | Format according to ruff config |
| ISS-164 | LOW | STYLE | tui/app.py:290 | Line exceeds 79 chars (tui/app.py:290) | Break line |
| ISS-165 | LOW | STYLE | tui/sanitizer.py | Multiple long lines need formatting | Format according to ruff config |
| ISS-166 | LOW | STYLE | services/dialogue_runner.py | Multiple long lines need formatting | Format according to ruff config |
| ISS-167 | LOW | DOCUMENTATION | models/conversation.py | Missing module docstring improvements | Add more examples |
| ISS-168 | LOW | DOCUMENTATION | models/ollama_client.py | Missing module docstring improvements | Add usage examples |
| ISS-169 | LOW | DOCUMENTATION | models/config.py | Missing docstring for validate_ollama_url examples | Add more examples |
| ISS-170 | LOW | DOCUMENTATION | services/dialogue_service.py | Missing docstring improvements | Add more details |
| ISS-171 | LOW | DOCUMENTATION | services/dialogue_runner.py | Missing docstring improvements | Add more details |
| ISS-172 | LOW | DOCUMENTATION | controllers/dialogue_controller.py | Missing docstring improvements | Add more details |
| ISS-173 | LOW | DOCUMENTATION | tui/app.py | Missing docstring improvements | Add more details |
| ISS-174 | LOW | DOCUMENTATION | tui/sanitizer.py | Missing docstring improvements | Add more details |
| ISS-175 | LOW | DOCUMENTATION | tui/constants.py | Missing docstring improvements | Add more details |
| ISS-176 | LOW | DOCUMENTATION | factories/provider_factory.py | Missing docstring improvements | Add more details |
| ISS-177 | LOW | DOCUMENTATION | services/model_style_mapper.py | Missing docstring improvements | Add more details |
| ISS-178 | LOW | ARCHITECTURE | main.py | main() function could use logging config | Improve logging setup |
| ISS-179 | LOW | ARCHITECTURE | main.py | Missing type annotation for main() return | Add proper return type |
| ISS-180 | LOW | ARCHITECTURE | main.py | Exception handling could be consolidated | Use exception hierarchy |

### ПАКЕТ-10: Финальные улучшения (ISS-181 - ISS-200)

| ID | Severity | Category | Location | Description | SuggestedFix |
|----|----------|----------|----------|-------------|--------------|
| ISS-181 | LOW | STYLE | All source files | Final formatting pass with ruff | Run ruff format on all files |
| ISS-182 | LOW | STYLE | All source files | Final linting pass with ruff | Run ruff check --fix |
| ISS-183 | LOW | TYPE_SAFETY | All source files | Final type checking pass with mypy | Run mypy and fix issues |
| ISS-184 | LOW | TYPE_SAFETY | All source files | Final type checking with pyright | Run pyright and fix issues |
| ISS-185 | LOW | ARCHITECTURE | All modules | Remove redundant __all__ exports | Review and clean exports |
| ISS-186 | LOW | ARCHITECTURE | All modules | Verify consistent import ordering | Run isort or manual fix |
| ISS-187 | LOW | ARCHITECTURE | All modules | Check for circular imports | Review import graph |
| ISS-188 | LOW | ARCHITECTURE | All modules | Verify all public APIs have docstrings | Add missing docstrings |
| ISS-189 | LOW | ARCHITECTURE | All modules | Check for consistent error handling | Standardize error patterns |
| ISS-190 | LOW | ARCHITECTURE | All modules | Verify all constants use Final | Add Final where missing |
| ISS-191 | LOW | ARCHITECTURE | All modules | Add __slots__ where beneficial | Review and add |
| ISS-192 | LOW | ARCHITECTURE | All modules | Check for property overuse | Consider method alternatives |
| ISS-193 | LOW | ARCHITECTURE | All modules | Review callback patterns | Use Protocol for callbacks |
| ISS-194 | LOW | ARCHITECTURE | All modules | Check for consistency in dataclasses | Standardize dataclass usage |
| ISS-195 | LOW | ARCHITECTURE | All modules | Review async patterns | Ensure consistent async usage |
| ISS-196 | LOW | ARCHITECTURE | All modules | Check for magic numbers | Extract to constants |
| ISS-197 | LOW | ARCHITECTURE | All modules | Review logging usage | Ensure consistent pattern |
| ISS-198 | LOW | ARCHITECTURE | All modules | Check for overly long functions | Split if needed |
| ISS-199 | LOW | ARCHITECTURE | All modules | Verify test coverage | Run coverage and review |
| ISS-200 | LOW | ARCHITECTURE | All modules | Final review of SOLID principles | Ensure compliance |

---

## Processing Order

1. **Пакет-1** (ISS-001 - ISS-020): Критические архитектурные проблемы
2. **Пакет-2** (ISS-021 - ISS-040): Проблемы типизации
3. **Пакет-3** (ISS-041 - ISS-060): Проблемы стиля кода
4. **Пакет-4** (ISS-061 - ISS-080): Неиспользуемый код
5. **Пакет-5** (ISS-081 - ISS-100): Устаревшие конструкции
6. **Пакет-6** (ISS-101 - ISS-120): Тестовые файлы - Проблемы стиля
7. **Пакет-7** (ISS-121 - ISS-140): Тестовые файлы - Продолжение
8. **Пакет-8** (ISS-141 - ISS-160): Тестовые файлы - Окончание
9. **Пакет-9** (ISS-161 - ISS-180): Рефакторинг конфигурации и документации
10. **Пакет-10** (ISS-181 - ISS-200): Финальные улучшения
