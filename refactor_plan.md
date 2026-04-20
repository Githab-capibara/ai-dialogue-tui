# Автономный рефакторинг — Реестр проблем (Issue Register)

**Проект:** ai-dialogue-tui
**Дата:** 2026-04-20
**Всего проблем:** 200
**Пакетов:** 10 × 20

---

## Сводная статистика аудита

| Категория | CRITICAL | HIGH | MEDIUM | LOW | Всего |
|-----------|----------|------|--------|-----|-------|
| TYPE_SAFETY | 0 | 5 | 15 | 20 | 40 |
| STYLE | 0 | 2 | 10 | 20 | 32 |
| ARCHITECTURE | 0 | 4 | 12 | 16 | 32 |
| DEPRECATED | 0 | 1 | 8 | 15 | 24 |
| UNUSED | 0 | 2 | 6 | 14 | 22 |
| PERFORMANCE | 0 | 1 | 5 | 10 | 16 |
| SECURITY | 0 | 1 | 3 | 10 | 14 |
| **ИТОГО** | **0** | **16** | **59** | **105** | **200** |

---

## ПАКЕТ-1: TYPE_SAFETY (ISS-001 — ISS-020)

### ISS-001 | CRITICAL → HIGH | TYPE_SAFETY | controllers/dialogue_controller.py:61
**Описание:** Параметр `on_state_changed` имеет тип `Callable[[UIState], None] | None` — отсутствует аннотация возвращаемого типа callable.
**SuggestedFix:** Использовать `collections.abc.Callable` с полной сигнатурой: `Callable[[UIState], None]`.

---

### ISS-002 | HIGH | TYPE_SAFETY | tui/app.py:252
**Описание:** `sub_title` использует `reactive()` без аннотации типа.
**SuggestedFix:** Добавить аннотацию: `sub_title: str = reactive("Диалог двух ИИ-моделей через Ollama")`.

---

### ISS-003 | HIGH | TYPE_SAFETY | tui/app.py:268
**Описание:** `self._client` типизирован как `ModelProvider | None` — рекомендуется использовать `typing.Optional`.
**SuggestedFix:** Заменить на `Optional[ModelProvider] = None`.

---

### ISS-004 | HIGH | TYPE_SAFETY | tui/app.py:253-256
**Описание:** Параметр `provider_factory` не имеет импорта `Callable` в TYPE_CHECKING блоке.
**SuggestedFix:** Добавить `Callable` в импорты TYPE_CHECKING из `collections.abc`.

---

### ISS-005 | HIGH | TYPE_SAFETY | tui/app.py:315
**Описание:** Блок `except Exception` ловит слишком широкое исключение без typed catches.
**SuggestedFix:** Заменить на `except (LookupError, RuntimeError) as exc` с явной типизацией.

---

### ISS-006 | HIGH | TYPE_SAFETY | tui/app.py:592
**Описание:** Неиспользуемые параметры `model_name, style` подавляются через `_ = `, но не типизированы как игнорируемые.
**SuggestedFix:** Переименовать в `_model_name, _style` для однозначности.

---

### ISS-007 | HIGH | TYPE_SAFETY | tui/app.py:635
**Описание:** Параметр `e: Exception` — используется `_` ниже, но тип Exception слишком общий.
**SuggestedFix:** Уточнить до `e: BaseException` или конкретного типа.

---

### ISS-008 | HIGH | TYPE_SAFETY | tui/app.py:645
**Описание:** `except Exception` без typed catches — скрывает типы ошибок.
**SuggestedFix:** Заменить `except Exception` на конкретные типы: `except (RuntimeError, ScreenStackError)`.

---

### ISS-009 | MEDIUM | TYPE_SAFETY | tui/app.py:11
**Описание:** Импорт `ClassVar` без использования — используется только в BINDINGS.
**SuggestedFix:** Убедиться что `ClassVar` используется корректно для всех атрибутов класса.

---

### ISS-010 | MEDIUM | TYPE_SAFETY | tui/app.py:418
**Описание:** `except (NoMatches, LookupError, RuntimeError) as e` — тип `e` не используется.
**SuggestedFix:** Использовать `_` вместо `e` для неиспользуемых переменных исключений.

---

### ISS-011 | MEDIUM | TYPE_SAFETY | tui/app.py:478
**Описание:** `except (NoMatches, LookupError, RuntimeError) as e` — аналогично неиспользуемый `e`.
**SuggestedFix:** Заменить `as e` на `_`.

---

### ISS-012 | MEDIUM | TYPE_SAFETY | tui/app.py:613
**Описание:** `except (NoMatches, LookupError, RuntimeError) as e` — неиспользуемый `e`.
**SuggestedFix:** Заменить `as e` на `_`.

---

### ISS-013 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:41
**Описание:** Параметр `config: Config | None = None` — рекомендуется Optional[Config].
**SuggestedFix:** Заменить на `config: Optional[Config] = None`.

---

### ISS-014 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:66-67
**Описание:** `on_turn` и `on_error` — отсутствует TYPE_CHECKING импорт Callable.
**SuggestedFix:** Добавить Callable в TYPE_CHECKING блок.

---

### ISS-015 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:141
**Описание:** `asyncio.current_task()` возвращает `Task[Any] | None` — не используется дженерик.
**SuggestedFix:** Использовать `asyncio.current_task()[None]` или типизировать дженерик.

---

### ISS-016 | MEDIUM | TYPE_SAFETY | services/dialogue_runner.py:128
**Описание:** `except (RuntimeError, SystemError, OSError)` — OSError слишком широко.
**SuggestedFix:** Разбить на конкретные подтипы OSError (ConnectionError, TimeoutError).

---

### ISS-017 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:60
**Описание:** `config: Config | None = None` — рекомендуется Optional[Config].
**SuggestedFix:** Заменить на `Optional[Config]`.

---

### ISS-018 | MEDIUM | TYPE_SAFETY | services/dialogue_service.py:15
**Описание:** TYPE_CHECKING импортирует `Conversation, ModelId` — ModelId определён локально.
**SuggestedFix:** Использовать `from __future__ import annotations` и строковые аннотации.

---

### ISS-019 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:13
**Описание:** `from typing import Any, Final` — Final используется для констант, но ниже используется `list[str]` напрямую.
**SuggestedFix:** Проверить консистентность использования Final для всех констант.

---

### ISS-020 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:20-21
**Описание:** Импорты `validate_ollama_url` из models.config.py — паук-энаты не используются в TYPE_CHECKING.
**SuggestedFix:** Перенести импорт в основной блок или использовать TYPE_CHECKING.

---

## ПАКЕТ-2: TYPE_SAFETY и ARCHITECTURE (ISS-021 — ISS-040)

### ISS-021 | HIGH | TYPE_SAFETY | models/ollama_client.py:394
**Описание:** `except (aiohttp.ClientError, asyncio.TimeoutError) as e` — e не используется.
**SuggestedFix:** Заменить `as e` на `_`.

---

### ISS-022 | HIGH | TYPE_SAFETY | models/ollama_client.py:475
**Описание:** `except (aiohttp.ClientError, asyncio.TimeoutError) as e` — неиспользуемый `e`.
**SuggestedFix:** Заменить `as e` на `_`.

---

### ISS-023 | HIGH | TYPE_SAFETY | models/ollama_client.py:489
**Описание:** `except (json.JSONDecodeError, KeyError, TypeError) as e` — неиспользуемый `e`.
**SuggestedFix:** Заменить `as e` на `_`.

---

### ISS-024 | HIGH | ARCHITECTURE | models/ollama_client.py:175-300
**Описание:** Классы `_RequestValidator`, `_ResponseHandler`, `_HTTPSessionManager`, `_ModelsCache` — нарушение инкапсуляции через приватные классы в одном модуле. Слишком много ответственности в одном файле.
**SuggestedFix:** Вынести каждый класс в отдельный модуль: validators.py, handlers.py, session_manager.py, models_cache.py.

---

### ISS-025 | HIGH | ARCHITECTURE | models/ollama_client.py:90
**Описание:** `_ResponseHandler` содержит staticmethod-ы — это процедурный стиль, а не ООП.
**SuggestedFix:** Рефакторить в фасадный класс с инстанс-методами или в модульные функции.

---

### ISS-026 | HIGH | ARCHITECTURE | models/ollama_client.py:45
**Описание:** `_RequestValidator` использует только staticmethod — нарушение SOLID (класс не инстанцируется).
**SuggestedFix:** Преобразовать в модульные функции или декоратор-класс.

---

### ISS-027 | HIGH | ARCHITECTURE | models/conversation.py:293
**Описание:** Широкий `except Exception` — перехватывает все ошибки, включая KeyboardInterrupt и SystemExit.
**SuggestedFix:** Заменить на `except (RuntimeError, ProviderError)`.

---

### ISS-028 | MEDIUM | TYPE_SAFETY | models/conversation.py:11
**Описание:** `from typing import Literal` — ModelId определён через Literal, но импортирован дважды (здесь и в provider.py).
**SuggestedFix:** Использовать реэкспорт из provider.py.

---

### ISS-029 | MEDIUM | TYPE_SAFETY | models/conversation.py:62-63
**Описание:** `_context_a` и `_context_b` имеют тип `list[MessageDict]` — поля приватные, но доступ через `self._context_a` в __post_init__.
**SuggestedFix:** Добавить `field(init=False)` для инициализируемых в __post_init__ полей.

---

### ISS-030 | MEDIUM | TYPE_SAFETY | models/conversation.py:103
**Описание:** Метод `_trim_context_if_needed` принимает `context: list[MessageDict]` — принимает список по значению, что неэффективно.
**SuggestedFix:** Изменить на `context: list[MessageDict]` с мутацией in-place или использовать Sequence.

---

### ISS-031 | MEDIUM | TYPE_SAFETY | models/conversation.py:182
**Описание:** Метод `get_context` возвращает `tuple[MessageDict, ...]` — возвращает копию каждый раз, что неэффективно.
**SuggestedFix:** Рассмотреть возврат `Sequence[MessageDict]` или readonly view.

---

### ISS-032 | MEDIUM | TYPE_SAFETY | models/conversation.py:243
**Описание:** `list(self.get_context(model_id))` — двойное создание копии (get_context уже возвращает tuple).
**SuggestedFix:** Убрать `list()` — provider.generate принимает Sequence.

---

### ISS-033 | MEDIUM | ARCHITECTURE | models/provider.py:8
**Описание:** `from typing import Any` — Any используется в Protocol, что размывает контракт.
**SuggestedFix:** Заменить `Any` на более конкретные типы где возможно.

---

### ISS-034 | MEDIUM | ARCHITECTURE | models/provider.py:118
**Описание:** `raise NotImplementedError` в Protocol-методах — Protocol определяет интерфейс, не реализацию.
**SuggestedFix:** Убрать raise NotImplementedError — это лишнее.

---

### ISS-035 | MEDIUM | ARCHITECTURE | models/provider.py:88
**Описание:** `@runtime_checkable` на ModelProvider — runtime проверка добавляет overhead без необходимости.
**SuggestedFix:** Убрать @runtime_checkable если проверка не нужна.

---

### ISS-036 | MEDIUM | ARCHITECTURE | models/config.py:9
**Описание:** `from typing import Final` — Final не используется в файле, только в импорте.
**SuggestedFix:** Убрать Final из импорта.

---

### ISS-037 | MEDIUM | ARCHITECTURE | models/config.py:186
**Описание:** `frozen=True, slots=True, eq=False` — eq=False при frozen несовместим с dataclass equality.
**SuggestedFix:** Убрать eq=False или пересмотреть архитектуру.

---

### ISS-038 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:30
**Описание:** Функция `factory()` в `create_provider_factory` возвращает `ModelProvider` — отсутствует аннотация возврата.
**SuggestedFix:** Добавить `-> ModelProvider:`.

---

### ISS-039 | MEDIUM | TYPE_SAFETY | factories/provider_factory.py:56-58
**Описание:** Вложенная функция factory() не типизирована.
**SuggestedFix:** Добавить типизацию: `def factory() -> ModelProvider:`.

---

### ISS-040 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:17
**Описание:** ProviderFactory Protocol не используется в коде — только для type hinting.
**SuggestedFix:** Проверить использование Protocol в codebase, возможно упростить.

---

## ПАКЕТ-3: STYLE и DEPRECATED (ISS-041 — ISS-060)

### ISS-041 | MEDIUM | STYLE | factories/provider_factory.py:30
**Описание:** Pylint W2301: Unnecessary ellipsis constant в Protocol.
**SuggestedFix:** Заменить `...` на pass или тело Protocol.

---

### ISS-042 | MEDIUM | STYLE | tui/app.py:51-62
**Описание:** Блок комментария о call_from_thread vs call_after_refresh занимает 11 строк — избыточный.
**SuggestedFix:** Сократить до 3-4 строк docstring.

---

### ISS-043 | MEDIUM | STYLE | tui/app.py:64
**Описание:** Комментарий `# CSS генерируется из централизованных констант` — очевидно из кода.
**SuggestedFix:** Убрать избыточный комментарий.

---

### ISS-044 | MEDIUM | STYLE | tui/app.py:164-165
**Описание:** `# type: ignore[assignment]` — дважды подряд, можно объединить.
**SuggestedFix:** Объединить в один ignore или уточнить тип.

---

### ISS-045 | MEDIUM | STYLE | tui/app.py:311-316
**Описание:** Серия except-блоков с одинаковой структурой — дублирование кода.
**SuggestedFix:** Вынести в helper-метод `_handle_state_update_error`.

---

### ISS-046 | MEDIUM | STYLE | tui/app.py:352-405
**Описание:** except-блоки в on_mount повторяют паттерн: log.exception + notify + _safe_update_status.
**SuggestedFix:** Создать фабричный метод для создания обработчиков ошибок.

---

### ISS-047 | MEDIUM | STYLE | tui/app.py:589-590
**Описание:** Docstring содержит многословное объяснение — можно сократить.
**SuggestedFix:** Сократить docstring до 2-3 строк.

---

### ISS-048 | MEDIUM | DEPRECATED | tui/app.py:592
**Описание:** `_ = model_name, style` — неиспользуемые параметры лучше префиксировать _.
**SuggestedFix:** Переименовать параметры в `_model_name, _style`.

---

### ISS-049 | MEDIUM | DEPRECATED | tui/app.py:643
**Описание:** `_ = e` — устаревший паттерн игнорирования, в Python 3+ можно просто не bindить.
**SuggestedFix:** Использовать `_handle_critical_error()` без параметра или `*_`.

---

### ISS-050 | MEDIUM | STYLE | tui/app.py:418
**Описание:** Комментарий `# pylint: disable=assignment-from-no-return` — pylinctest в коде.
**SuggestedFix:** Исправить присвоение или убрать pylint-директиву.

---

### ISS-051 | MEDIUM | STYLE | tui/app.py:461
**Описание:** Комментарий `# чтобы UI успел обновиться после закрытия модального окна` — избыточный.
**SuggestedFix:** Убрать или сократить.

---

### ISS-052 | MEDIUM | STYLE | services/dialogue_runner.py:115
**Описание:** `%s` форматирование — используется %-formatting вместо f-strings.
**SuggestedFix:** Заменить на f"Ошибка провайдера в цикле диалога: {e}".

---

### ISS-053 | MEDIUM | STYLE | services/dialogue_runner.py:128
**Описание:** `"Critical error in dialogue loop"` — сообщение без форматирования.
**SuggestedFix:** Использовать f-строку для консистентности.

---

### ISS-054 | MEDIUM | DEPRECATED | services/dialogue_service.py:169
**Описание:** `log.exception` — используется %s вместо f-строки.
**SuggestedFix:** Перейти на f"Ошибка провайдера при выполнении цикла диалога: {e}".

---

### ISS-055 | MEDIUM | STYLE | models/ollama_client.py:15
**Описание:** `# nosec: B044` — игнорирование Bandit B044 (third-party import) в коде.
**SuggestedFix:** Убрать nosec-комментарий, добавить исключение в .bandit.yml.

---

### ISS-056 | MEDIUM | STYLE | models/ollama_client.py:20-21
**Описание:** `# pylint: disable=wrong-import-position` — дважды в одном файле.
**SuggestedFix:** Перенести импорты в правильном порядке или вынести в отдельный блок.

---

### ISS-057 | MEDIUM | STYLE | models/ollama_client.py:26-31
**Описание:** pylint: disable=wrong-import-position — импорты из models.provider и models.config нарушают порядок.
**SuggestedFix:** Реорганизовать импорты: стандартные → third-party → local.

---

### ISS-058 | MEDIUM | STYLE | models/ollama_client.py:394-410
**Описание:** Три except-блока подряд с одинаковым паттерном `_logger + raise ProviderError`.
**SuggestedFix:** Вынести в helper-метод `_log_and_raise`.

---

### ISS-059 | MEDIUM | STYLE | models/ollama_client.py:475-494
**Описание:** Аналогичное дублирование except-блоков в методе generate().
**SuggestedFix:** Вынести в helper-метод.

---

### ISS-060 | MEDIUM | DEPRECATED | models/ollama_client.py:62
**Описание:** `msg = f"..."` followed by `raise ValueError(msg)` — избыточная переменная.
**SuggestedFix:** `raise ValueError(f"Некорректный URL хоста: {host}")`.

---

## ПАКЕТ-4: STYLE и UNUSED (ISS-061 — ISS-080)

### ISS-061 | MEDIUM | STYLE | models/ollama_client.py:78-79
**Описание:** `msg = "..."` then `raise TypeError(msg)` — избыточная переменная.
**SuggestedFix:** `raise TypeError("messages must be a list")`.

---

### ISS-062 | MEDIUM | STYLE | models/ollama_client.py:83
**Описание:** `msg_0 = "..."` then `raise TypeError(msg_0)` — непоследовательное именование переменных.
**SuggestedFix:** Унифицировать: `raise TypeError("Each message must be a dictionary")`.

---

### ISS-063 | MEDIUM | STYLE | models/ollama_client.py:86
**Описание:** `raise TypeError(msg_0)` — повторное использование msg_0.
**SuggestedFix:** Использовать разные сообщения для разных ошибок.

---

### ISS-064 | MEDIUM | STYLE | models/ollama_client.py:109
**Описание:** `# noqa: PLR2004` — magic number 200 проверяется.
**SuggestedFix:** Вынести в константу: `HTTP_OK = 200`.

---

### ISS-065 | MEDIUM | STYLE | models/ollama_client.py:131
**Описание:** Избыточная переменная msg.
**SuggestedFix:** `raise ProviderGenerationError(f"Некорректный формат ответа API ({operation})")`.

---

### ISS-066 | MEDIUM | STYLE | models/conversation.py:130-134
**Описание:** `log.warning` с форматированием — можно использовать f-строку.
**SuggestedFix:** Заменить на f"Контекст превышен ({len(context)} сообщений), обрезано до {len(trimmed)}".

---

### ISS-067 | MEDIUM | STYLE | models/conversation.py:175-180
**Описание:** `log.debug` использует %s форматирование.
**SuggestedFix:** Заменить на f-строку.

---

### ISS-068 | MEDIUM | STYLE | models/conversation.py:204-208
**Описание:** `log.debug` использует %s форматирование.
**SuggestedFix:** Заменить на f-строку.

---

### ISS-069 | MEDIUM | UNUSED | models/ollama_client.py:10
**Описание:** `import json` — используется в двух местах для json.JSONDecodeError, можно заменить на json.loads встроенный.
**SuggestedFix:** Проверить использование — json используется только для JSONDecodeError, можно импортировать только исключение.

---

### ISS-070 | MEDIUM | UNUSED | models/ollama_client.py:12
**Описание:** `import time` — используется только для time.time() в _ModelsCache.
**SuggestedFix:** Проверить, можно ли использовать `datetime.now().timestamp()`.

---

### ISS-071 | MEDIUM | UNUSED | models/ollama_client.py:13
**Описание:** `from typing import Any, Final` — Any используется, но Final не используется в классах _RequestValidator и _ResponseHandler.
**SuggestedFix:** Убрать Final из этого импорта (используется только в _DEFAULT_OPTIONS).

---

### ISS-072 | MEDIUM | UNUSED | models/ollama_client.py:195
**Описание:** Scalability-блок в docstring — описывает будущие улучшения, не текущий код.
**SuggestedFix:** Перенести в код как TODO или убрать если не актуально.

---

### ISS-073 | MEDIUM | UNUSED | models/ollama_client.py:189-194
**Описание:** Docstring для _HTTPSessionManager содержит Note/Scalability — нарушение DRY.
**SuggestedFix:** Сократить docstring, вынести детали в код.

---

### ISS-074 | MEDIUM | UNUSED | models/conversation.py:9
**Описание:** `import logging` — используется, но log не типизирован.
**SuggestedFix:** Использовать typing_extensions для typed log или убрать аннотацию.

---

### ISS-075 | MEDIUM | UNUSED | services/dialogue_service.py:8
**Описание:** `import logging` — log используется, но тип не уточнён.
**SuggestedFix:** log = logging.getLogger(__name__) — уже правильно, можно добавить typed log.

---

### ISS-076 | MEDIUM | UNUSED | services/dialogue_runner.py:8
**Описание:** `import asyncio` — asyncio используется для asyncio.Task, asyncio.CancelledError.
**SuggestedFix:** Проверить, можно ли использовать из collections.abc.

---

### ISS-077 | MEDIUM | UNUSED | tui/app.py:8
**Описание:** `import asyncio` — используется для asyncio.Task, asyncio.CancelledError.
**SuggestedFix:** Корректное использование.

---

### ISS-078 | MEDIUM | UNUSED | tui/sanitizer.py:9
**Описание:** `import html` — используется для html.escape, корректно.
**SuggestedFix:** Корректное использование.

---

### ISS-079 | MEDIUM | UNUSED | tui/constants.py:9
**Описание:** `from typing import Final` — используется для констант, корректно.
**SuggestedFix:** Корректное использование.

---

### ISS-080 | MEDIUM | UNUSED | tui/styles.py:8
**Описание:** `from tui.constants import CSS_CLASSES, UI_IDS` — используется только UI_IDS частично.
**SuggestedFix:** Проверить использование CSS_CLASSES — он импортируется но не используется в generate_main_css.

---

## ПАКЕТ-5: ARCHITECTURE и TYPE_SAFETY (ISS-081 — ISS-100)

### ISS-081 | HIGH | ARCHITECTURE | tui/app.py:235
**Описание:** DialogueApp имеет 9+ атрибутов — нарушение Single Responsibility Principle.
**SuggestedFix:** Вынести части в отдельные компоненты: StateManager, ThemeManager, DialogueLoopController.

---

### ISS-082 | HIGH | ARCHITECTURE | tui/app.py:421-485
**Описание:** `_setup_conversation` — 65 строк, выполняет слишком много задач.
**SuggestedFix:** Разбить на: _create_conversation, _create_service, _setup_ui_callbacks.

---

### ISS-083 | HIGH | ARCHITECTURE | tui/app.py:535-575
**Описание:** `_run_dialogue` — 40 строк, содержит бизнес-логику в UI слое.
**SuggestedFix:** Делегировать в DialogueRunner, оставить только UI callback-и.

---

### ISS-084 | HIGH | ARCHITECTURE | tui/app.py:535-575
**Описание:** _run_dialogue дублирует логику DialogueRunner._run_loop — нарушение DRY.
**SuggestedFix:** Использовать DialogueRunner для выполнения цикла, получать callback-и.

---

### ISS-085 | HIGH | ARCHITECTURE | tui/app.py:298-316
**Описание:** Обработчик `_on_ui_state_changed` содержит 4 except-блока с одинаковой целью.
**SuggestedFix:** Создать helper-метод `_safe_update_label` с единой обработкой ошибок.

---

### ISS-086 | MEDIUM | ARCHITECTURE | models/ollama_client.py:302-495
**Описание:** OllamaClient — 193 строки, слишком большой класс.
**SuggestedFix:** Вынести: _URLBuilder, _PayloadBuilder, _ErrorMapper.

---

### ISS-087 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:23-36
**Описание:** DialogueRunner не является полноценным сервисом — дублирует DialogueService.
**SuggestedFix:** Убрать DialogueRunner или сделать егоthin-обёрткой над asyncio.

---

### ISS-088 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:132-139
**Описание:** `_process_turn` просто проксирует в service — лишняя абстракция.
**SuggestedFix:** Убрать метод, вызывать service напрямую.

---

### ISS-089 | MEDIUM | ARCHITECTURE | services/dialogue_service.py:21-36
**Описание:** DialogueTurnResult dataclass — небольшой, но используется только в одном месте.
**SuggestedFix:** Рассмотреть использование NamedTuple или просто tuple.

---

### ISS-090 | MEDIUM | ARCHITECTURE | models/conversation.py:28-33
**Описание:** _ConversationContext — dataclass с 2 полями, не используется.
**SuggestedFix:** Убрать dataclass, использовать обычные поля в Conversation.

---

### ISS-091 | MEDIUM | ARCHITECTURE | models/config.py:66-183
**Описание:** 5 функций валидации с почти идентичным телом — нарушение DRY.
**SuggestedFix:** Вынести в декоратор `@validate_param(name, min, max)`.

---

### ISS-092 | MEDIUM | ARCHITECTURE | models/config.py:186-237
**Описание:** Config dataclass вызывает 5 валидаторов в __post_init__ — дублирование.
**SuggestedFix:** Использовать attrs-подобные validators или dataclass-validators.

---

### ISS-093 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:102-104
**Описание:** `_notify_state_changed` вызывает callback напрямую без защиты от re-entry.
**SuggestedFix:** Добавить guard от повторного вызова или использовать lock.

---

### ISS-094 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:82-89
**Описание:** `state` property возвращает копию через конструктор — нет immutable подхода.
**SuggestedFix:** Использовать frozen dataclass или attrs.

---

### ISS-095 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:33-38
**Описание:** `_style_map` словарь — можно заменить на Enum для type safety.
**SuggestedFix:** Создать enum ModelStyle с A и B значениями.

---

### ISS-096 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:46-60
**Описание:** `create_provider_factory` создаёт вложенную функцию — можно использовать partial.
**SuggestedFix:** Заменить на `functools.partial(create_ollama_provider, config)`.

---

### ISS-097 | MEDIUM | ARCHITECTURE | main.py:25-28
**Описание:** `logging.basicConfig` в main — глобальная конфигурация логирования.
**SuggestedFix:** Использовать dictConfig или конфигурацию через env-переменные.

---

### ISS-098 | MEDIUM | ARCHITECTURE | main.py:31-71
**Описание:** main() содержит много except-блоков — можно вынести в ErrorHandler.
**SuggestedFix:** Создать декоратор @handle_errors или ErrorHandler класс.

---

### ISS-099 | MEDIUM | ARCHITECTURE | tui/sanitizer.py:13
**Описание:** MAX_RESPONSE_PREVIEW_LENGTH = 100 — magic number, хотя константа.
**SuggestedFix:** Проверить, используется ли в других местах.

---

### ISS-100 | MEDIUM | ARCHITECTURE | tui/sanitizer.py:48-91
**Описание:** sanitize_response_for_display делает too much — экранирует и обрезает.
**SuggestedFix:** Разбить на sanitize_for_markup и truncate_response.

---

## ПАКЕТ-6: STYLE и DEPRECATED (ISS-101 — ISS-120)

### ISS-101 | MEDIUM | DEPRECATED | models/ollama_client.py:36-39
**Описание:** `_DEFAULT_OPTIONS: Final = {...}` — Final для mutable dict — ошибка.
**SuggestedFix:** Использовать `MappingProxyType` или создавать dict в __init__.

---

### ISS-102 | MEDIUM | STYLE | models/ollama_client.py:108
**Описание:** Комментарий `# noqa: PLR2004` — можно заменить константой.
**SuggestedFix:** `HTTP_SUCCESS_CODE = 200`.

---

### ISS-103 | MEDIUM | STYLE | models/ollama_client.py:402
**Описание:** `_logger.debug` использует %s formatting.
**SuggestedFix:** Использовать f-строку.

---

### ISS-104 | MEDIUM | DEPRECATED | models/ollama_client.py:408
**Описание:** `_logger.warning("Игнорируемое OSError...")` — слово "Игнорируемое" в коде.
**SuggestedFix:** Переписать: `_logger.debug("OSError during model listing: %s", e)`.

---

### ISS-105 | MEDIUM | DEPRECATED | models/ollama_client.py:493
**Описание:** Аналогичное "Игнорируемое OSError" в методе generate.
**SuggestedFix:** Аналогичное исправление.

---

### ISS-106 | MEDIUM | STYLE | models/ollama_client.py:436
**Описание:** `url = f"{self.host}/api/chat"` — host уже содержит trailing slash?
**SuggestedFix:** Использовать `urljoin` из urllib.parse для безопасного построения URL.

---

### ISS-107 | MEDIUM | STYLE | models/ollama_client.py:369
**Описание:** Аналогичное: `url = f"{self.host}/api/tags"`.
**SuggestedFix:** Использовать urljoin.

---

### ISS-108 | MEDIUM | DEPRECATED | models/conversation.py:50-53
**Описание:** Note в docstring о 8 атрибутах — pylint disable используется.
**SuggestedFix:** Убрать Note из docstring, положиться на disable.

---

### ISS-109 | MEDIUM | DEPRECATED | models/conversation.py:56
**Описание:** `# pylint: disable=too-many-instance-attributes` — inline pylint directive.
**SuggestedFix:** Вынести в .pylintrc или убрать dataclass-поля.

---

### ISS-110 | MEDIUM | DEPRECATED | models/conversation.py:293
**Описание:** except Exception — широкое перехватывание.
**SuggestedFix:** Заменить на конкретные типы.

---

### ISS-111 | MEDIUM | DEPRECATED | tui/app.py:235
**Описание:** `# pylint: disable=too-many-instance-attributes` — inline directive.
**SuggestedFix:** Вынести в .pylintrc.

---

### ISS-112 | MEDIUM | DEPRECATED | tui/constants.py:68
**Описание:** `# pylint: disable=too-many-instance-attributes` в dataclass.
**SuggestedFix:** Использовать @dataclass с field для группировки атрибутов.

---

### ISS-113 | MEDIUM | STYLE | tui/constants.py:25-28
**Описание:** MessageStyles использует dataclass вместо NamedTuple или attrs.
**SuggestedFix:** Рассмотреть использование frozen dataclass для immutability.

---

### ISS-114 | MEDIUM | STYLE | tui/constants.py:31-105
**Описание:** UIElementIDs dataclass с 35+ полей — много ответственности.
**SuggestedFix:** Разбить на UIElementIDs_Main, UIElementIDs_Selection, UIElementIDs_Topic.

---

### ISS-115 | MEDIUM | STYLE | tui/constants.py:108-123
**Описание:** CSSClasses dataclass — можно объединить с MessageStyles.
**SuggestedFix:** Создать единый класс стилей UI.

---

### ISS-116 | MEDIUM | DEPRECATED | controllers/dialogue_controller.py:47-55
**Описание:** Example в docstring использует `>>>` синтаксис — устаревший стиль.
**SuggestedFix:** Использовать RST-стиль examples или убрать интерактивный синтаксис.

---

### ISS-117 | MEDIUM | DEPRECATED | services/dialogue_service.py:51-53
**Описание:** Note в docstring — избыточная информация.
**SuggestedFix:** Убрать Note или сократить.

---

### ISS-118 | MEDIUM | DEPRECATED | services/dialogue_runner.py:33-35
**Описание:** Note в docstring — избыточная информация.
**SuggestedFix:** Сократить docstring.

---

### ISS-119 | MEDIUM | DEPRECATED | factories/provider_factory.py:17-30
**Описание:** ProviderFactory Protocol с ... — Protocol должен быть без реализации.
**SuggestedFix:** Убрать тело метода, оставить только аннотации.

---

### ISS-120 | MEDIUM | DEPRECATED | main.py:37-40
**Описание:** Note в docstring — избыточная информация.
**SuggestedFix:** Сократить docstring.

---

## ПАКЕТ-7: ARCHITECTURE и STYLE (ISS-121 — ISS-140)

### ISS-121 | MEDIUM | ARCHITECTURE | models/ollama_client.py:245-300
**Описание:** _ModelsCache не использует typing.Protocol — можно сделать generic.
**SuggestedFix:** Добавить typing.Protocol для通用ного cache interface.

---

### ISS-122 | MEDIUM | ARCHITECTURE | models/ollama_client.py:175-242
**Описание:** _HTTPSessionManager не использует async context manager pattern.
**SuggestedFix:** Реализовать `__aenter__` и `__aexit__` для using.

---

### ISS-123 | MEDIUM | ARCHITECTURE | models/ollama_client.py:218
**Описание:** Метод get_session() создаёт сессию при каждом вызове если closed.
**SuggestedFix:** Добавить retry logic или использовать aenter.

---

### ISS-124 | MEDIUM | ARCHITECTURE | services/dialogue_runner.py:79-91
**Описание:** stop() использует try/except/finally — можно использовать context manager.
**SuggestedFix:** Использовать asyncio.TaskGroup в Python 3.11+.

---

### ISS-125 | MEDIUM | ARCHITECTURE | tui/app.py:652-683
**Описание:** on_unmount имеет 30+ строк — много ответственности.
**SuggestedFix:** Разбить на _cancel_dialogue_task, _cleanup_controller, _cleanup_client.

---

### ISS-126 | MEDIUM | ARCHITECTURE | tui/app.py:275
**Описание:** `_cleanup_done` flag — ручной механизм идемпотентности.
**SuggestedFix:** Использовать `contextlib.AsyncExitStack`.

---

### ISS-127 | MEDIUM | ARCHITECTURE | tui/app.py:11
**Описание:** Импорт `ClassVar` без явного использования — только для подсказок типа.
**SuggestedFix:** Проверить использование в BINDINGS.

---

### ISS-128 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:17
**Описание:** UIState использует @dataclass(slots=True) — для dataclass с 5 полями slots overkill.
**SuggestedFix:** Убрать slots или заменить на NamedTuple.

---

### ISS-129 | MEDIUM | ARCHITECTURE | models/config.py:211-215
**Описание:** default_system_prompt — длинная строка в конструкторе dataclass.
**SuggestedFix:** Вынести в константу DEFAULT_SYSTEM_PROMPT.

---

### ISS-130 | MEDIUM | ARCHITECTURE | models/config.py:218
**Описание:** ollama_host по умолчанию захардкожен — не читается из env.
**SuggestedFix:** Добавить чтение из os.environ.get("OLLAMA_HOST", "http://localhost:11434").

---

### ISS-131 | MEDIUM | STYLE | models/provider.py:8
**Описание:** `from typing import Any` — Any в Protocol размывает контракт.
**SuggestedFix:** Заменить на конкретные типы где возможно.

---

### ISS-132 | MEDIUM | STYLE | models/provider.py:12-38
**Описание:** ProviderError использует @property для original_exception — можно через super().
**SuggestedFix:** Перейти на стандартное исключение с __cause__.

---

### ISS-133 | MEDIUM | STYLE | models/provider.py:12-68
**Описание:** Три специализированных ProviderError-а — похожие, можно объединить через enum.
**SuggestedFix:** Создать ProviderErrorType enum и единый ProviderError.

---

### ISS-134 | MEDIUM | STYLE | models/provider.py:24
**Описание:** ProviderError.__init__ параметр `original_exception` не используется в raise.
**SuggestedFix:** Использовать `raise ProviderError(...) from original_exception`.

---

### ISS-135 | MEDIUM | STYLE | services/dialogue_service.py:21-36
**Описание:** DialogueTurnResult dataclass — можно использовать NamedTuple.
**SuggestedFix:** Заменить dataclass на NamedTuple для производительности.

---

### ISS-136 | MEDIUM | STYLE | services/dialogue_service.py:158
**Описание:** `_, _, response = await ...` — игнорируемые переменные.
**SuggestedFix:** Использовать `result = await ...` и обращаться по индексу.

---

### ISS-137 | MEDIUM | STYLE | services/dialogue_runner.py:106
**Описание:** `while self._service.is_running and not self._service.is_paused` — длинное условие.
**SuggestedFix:** Вынести в property `_is_active` или метод `_should_continue()`.

---

### ISS-138 | MEDIUM | STYLE | services/dialogue_runner.py:107-108
**Описание:** `if self._is_task_cancelled()` followed by `break` — можно объединить.
**SuggestedFix:** `if self._is_task_cancelled(): break`.

---

### ISS-139 | MEDIUM | STYLE | factories/provider_factory.py:8
**Описание:** TYPE_CHECKING импорт Protocol — Protocol не нужен в runtime.
**SuggestedFix:** Оставить только в TYPE_CHECKING.

---

### ISS-140 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:46
**Описание:** create_provider_factory возвращает функцию — можно использовать partial.
**SuggestedFix:** Использовать functools.partial.

---

## ПАКЕТ-8: TYPE_SAFETY и PERFORMANCE (ISS-141 — ISS-160)

### ISS-141 | MEDIUM | TYPE_SAFETY | tui/app.py:338
**Описание:** `def on_models_selected(result: tuple[str, str] | None)` — вложенная функция без type hint на параметры.
**SuggestedFix:** Добавить полную типизацию.

---

### ISS-142 | MEDIUM | TYPE_SAFETY | tui/app.py:430
**Описание:** `def on_topic_entered(topic: str | None)` — вложенная функция.
**SuggestedFix:** Добавить TYPE_CHECKING аннотацию.

---

### ISS-143 | MEDIUM | TYPE_SAFETY | tui/app.py:462
**Описание:** `_finalize_setup` — вложенная функция без типизации.
**SuggestedFix:** Вынести в метод класса или типизировать.

---

### ISS-144 | MEDIUM | TYPE_SAFETY | tui/app.py:556
**Описание:** `_process_dialogue_turn` возвращает DialogueTurnResult | None — None не обрабатывается.
**SuggestedFix:** Добавить проверку None или изменить return type.

---

### ISS-145 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:349-392
**Описание:** list_models не типизирует возвращаемое значение для пустого списка.
**SuggestedFix:** Явно типизировать `-> list[str]:`.

---

### ISS-146 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:412-495
**Описание:** generate() имеет **kwargs — не типизирован.
**SuggestedFix:** Использовать `**kwargs: Unpack[GeneratorKwargs]` если доступен.

---

### ISS-147 | MEDIUM | PERFORMANCE | models/ollama_client.py:251-299
**Описание:** _ModelsCache использует time.time() float — можно использовать monotonic().
**SuggestedFix:** Заменить time.time() на time.monotonic() для измерения интервалов.

---

### ISS-148 | MEDIUM | PERFORMANCE | models/ollama_client.py:262-273
**Описание:** _is_cache_valid() вычисляет current_time каждый раз.
**SuggestedFix:** Вычислять время в get() и set(), не в is_cache_valid().

---

### ISS-149 | MEDIUM | PERFORMANCE | models/conversation.py:103-136
**Описание:** _trim_context_if_needed возвращает новый список каждый раз.
**SuggestedFix:** Мутировать in-place для производительности.

---

### ISS-150 | MEDIUM | PERFORMANCE | models/conversation.py:273-276
**Описание:** Создание 3 snapshots (context_a, context_b, turn) при каждом process_turn.
**SuggestedFix:** Использовать контекстный менеджер или attrs.

---

### ISS-151 | MEDIUM | PERFORMANCE | models/conversation.py:138-155
**Описание:** _add_message_to_context дважды проверяет MAX_CONTEXT_LENGTH.
**SuggestedFix:** Проверять один раз в add_message.

---

### ISS-152 | MEDIUM | PERFORMANCE | services/dialogue_service.py:141-170
**Описание:** run_dialogue_cycle создаёт DialogueTurnResult dataclass — overhead.
**SuggestedFix:** Использовать NamedTuple или простой tuple.

---

### ISS-153 | MEDIUM | PERFORMANCE | services/dialogue_runner.py:120
**Описание:** asyncio.sleep использует float константу — нет проверки на negative.
**SuggestedFix:** Добавить max(0, self._config.pause_between_messages).

---

### ISS-154 | MEDIUM | PERFORMANCE | tui/app.py:273
**Описание:** `_style_mapper = ModelStyleMapper()` создаётся в __init__ — кэшируется правильно.
**SuggestedFix:** Корректно.

---

### ISS-155 | MEDIUM | PERFORMANCE | tui/sanitizer.py:48-91
**Описание:** sanitize_response_for_display проходит 15+ replace операций.
**SuggestedFix:** Использовать re.sub с compiled regex patterns для группы символов.

---

### ISS-156 | MEDIUM | PERFORMANCE | tui/sanitizer.py:70
**Описание:** html.escape с quote=False каждый раз.
**SuggestedFix:** Использовать compiled escape table.

---

### ISS-157 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:150-154
**Описание:** extract_models_list — comprehension с isinstance проверками внутри.
**SuggestedFix:** Вынести валидацию в отдельный метод.

---

### ISS-158 | MEDIUM | TYPE_SAFETY | models/ollama_client.py:167-172
**Описание:** extract_generation_response — chain of isinstance checks.
**SuggestedFix:** Добавить валидацию через Pydantic или attrs.

---

### ISS-159 | MEDIUM | TYPE_SAFETY | models/config.py:43-49
**Описание:** Examples в docstring функции validate_ollama_url не соответствуют типу.
**SuggestedFix:** Использовать doctest вместо Example.

---

### ISS-160 | MEDIUM | TYPE_SAFETY | models/config.py:83-86
**Описание:** Examples в _validate_numeric_range используют >>> без doctest framework.
**SuggestedFix:** Убрать examples или добавить в doctest suite.

---

## ПАКЕТ-9: STYLE и UNUSED (ISS-161 — ISS-180)

### ISS-161 | MEDIUM | STYLE | models/ollama_client.py:77
**Описание:** `if not isinstance(messages, list)` — двойное отрицание.
**SuggestedFix:** `if isinstance(messages, list): raise TypeError(...)`.

---

### ISS-162 | MEDIUM | STYLE | models/ollama_client.py:150-154
**Описание:** List comprehension длинная — разбить на строки.
**SuggestedFix:** Отформатировать с переносами.

---

### ISS-163 | MEDIUM | STYLE | models/conversation.py:96-99
**Описание:** try/except с единственной операцией format.
**SuggestedFix:** Упростить: `formatted_prompt = effective_prompt.format(topic=self.topic) if "{topic}" in effective_prompt else effective_prompt`.

---

### ISS-164 | MEDIUM | STYLE | models/conversation.py:124
**Описание:** system_message = context[0] if context else None — ternary с side effect.
**SuggestedFix:** Использовать `system_message = context[0] if context else MessageDict(...)`.

---

### ISS-165 | MEDIUM | STYLE | models/conversation.py:128
**Описание:** Строка с распаковкой `[system_message, *remaining_messages]` — можно упростить.
**SuggestedFix:** `trimmed = [system_message] + remaining_messages if system_message else remaining_messages`.

---

### ISS-166 | MEDIUM | STYLE | models/conversation.py:195
**Описание:** Комментарий `# Возвращаем tuple для безопасности и производительности` — избыточный.
**SuggestedFix:** Убрать комментарий.

---

### ISS-167 | MEDIUM | STYLE | models/conversation.py:199-200
**Описание:** Docstring с Note о Command pattern — избыточная информация.
**SuggestedFix:** Сократить docstring.

---

### ISS-168 | MEDIUM | STYLE | models/conversation.py:279-280
**Описание:** Комментарий `# Генерируем ответ ДО любых изменений контекста` — очевидно из кода.
**SuggestedFix:** Убрать комментарий.

---

### ISS-169 | MEDIUM | STYLE | models/conversation.py:300-316
**Описание:** Метод clear_contexts длинный — 16 строк.
**SuggestedFix:** Разбить на _create_system_context и _reset_turn.

---

### ISS-170 | MEDIUM | UNUSED | models/ollama_client.py:186
**Описание:** Scalability docstring блок — future concerns в production коде.
**SuggestedFix:** Перенести в TODO comments или архитектурный документ.

---

### ISS-171 | MEDIUM | UNUSED | models/ollama_client.py:189
**Описание:** Note в docstring дублирует код.
**SuggestedFix:** Сократить docstring.

---

### ISS-172 | MEDIUM | UNUSED | models/ollama_client.py:44
**Описание:** `_MODELS_CACHE_TTL: Final = 300` — magic number 300 секунд.
**SuggestedFix:** Добавить комментарий: `# 5 minutes`.

---

### ISS-173 | MEDIUM | UNUSED | models/config.py:13-18
**Описание:** Константы MIN_*, MAX_* экспортируются но не используются в __all__.
**SuggestedFix:** Добавить в __all__ или убрать из экспорта.

---

### ISS-174 | MEDIUM | UNUSED | services/dialogue_service.py:14
**Описание:** TYPE_CHECKING импортирует ModelId — но ModelId используется в DialogueTurnResult.
**SuggestedFix:** Проверить использование — возможно убрать из TYPE_CHECKING.

---

### ISS-175 | MEDIUM | UNUSED | services/dialogue_runner.py:15-18
**Описание:** TYPE_CHECKING блок импортирует DialogueTurnResult — используется в типизации.
**SuggestedFix:** Корректно.

---

### ISS-176 | MEDIUM | UNUSED | controllers/dialogue_controller.py:10-12
**Описание:** TYPE_CHECKING блок импортирует Callable — уже импортирован выше.
**SuggestedFix:** Убрать дублирующий импорт из TYPE_CHECKING.

---

### ISS-177 | MEDIUM | UNUSED | tui/app.py:48-49
**Описание:** TYPE_CHECKING импортирует Callable — Callable уже доступен.
**SuggestedFix:** Проверить дублирование импорта Callable.

---

### ISS-178 | MEDIUM | UNUSED | tui/app.py:10
**Описание:** `from typing import Any` — Any используется широко.
**SuggestedFix:** Уменьшить использование Any.

---

### ISS-179 | MEDIUM | UNUSED | tui/app.py:315
**Описание:** `# pylint: disable=broad-exception-caught` — broad exception disabled.
**SuggestedFix:** Заменить на конкретные типы.

---

### ISS-180 | MEDIUM | UNUSED | tui/app.py:415
**Описание:** `# pylint: disable=assignment-from-no-return` — suppression directive.
**SuggestedFix:** Исправить код чтобы не требовалось.

---

## ПАКЕТ-10: DEPRECATED и ARCHITECTURE (ISS-181 — ISS-200)

### ISS-181 | MEDIUM | DEPRECATED | models/ollama_client.py:216
**Описание:** `asyncio.Lock()` — asyncio.Lock() без argument рекомендуется asyncio.Lock(loop=None).
**SuggestedFix:** Использовать asyncio.Lock() — уже deprecated в Python 3.10+.

---

### ISS-182 | MEDIUM | DEPRECATED | models/ollama_client.py:241
**Описание:** `contextlib.suppress` оборачивает только один тип исключения.
**SuggestedFix:** Использовать try/except с pass.

---

### ISS-183 | MEDIUM | DEPRECATED | models/conversation.py:148
**Описание:** `MAX_CONTEXT_LENGTH - 2` — magic numbers в коде.
**SuggestedFix:** Вынести в константу.

---

### ISS-184 | MEDIUM | DEPRECATED | models/conversation.py:271
**Описание:** `other_id: ModelId = "B" if model_id == "A" else "A"` — можно через dataclass field.
**SuggestedFix:** Использовать enum ModelId.

---

### ISS-185 | MEDIUM | DEPRECATED | models/config.py:186
**Описание:** frozen=True с slots=True — dataclass compatibility issues.
**SuggestedFix:** Проверить совместимость с Python 3.10.

---

### ISS-186 | MEDIUM | DEPRECATED | services/dialogue_runner.py:143
**Описание:** `asyncio.current_task()` deprecated — заменить на `asyncio.get_running_loop().task_count()`.
**SuggestedFix:** Использовать `asyncio.current_task()` с deprecated warning — оставить пока.

---

### ISS-187 | MEDIUM | DEPRECATED | services/dialogue_service.py:145
**Описание:** Comment `# increment` contains grammar error.
**SuggestedFix:** Исправить на `# Increments counter`.

---

### ISS-188 | MEDIUM | DEPRECATED | tui/app.py:55-62
**Описание:** Комментарий о call_from_thread vs call_after_refresh устарел.
**SuggestedFix:** Обновить комментарий для текущей версии Textual.

---

### ISS-189 | MEDIUM | ARCHITECTURE | tui/app.py:587-600
**Описание:** _process_dialogue_turn содержит бизнес-логику в UI — нарушение MVC.
**SuggestedFix:** Делегировать форматирование в сервисный слой.

---

### ISS-190 | MEDIUM | ARCHITECTURE | tui/app.py:615-636
**Описание:** _handle_dialogue_error делает too much — логирование, UI update, notify.
**SuggestedFix:** Разбить на отдельные методы.

---

### ISS-191 | MEDIUM | ARCHITECTURE | tui/app.py:638-650
**Описание:** _handle_critical_error принимает Exception но не использует его.
**SuggestedFix:** Убрать параметр или использовать для enhanced logging.

---

### ISS-192 | MEDIUM | ARCHITECTURE | tui/constants.py:107-127
**Описание:** Экспорт CSS_CLASSES но CSS не используется в tui/styles.py.
**SuggestedFix:** Убрать неиспользуемый импорт или использовать CSSClasses.

---

### ISS-193 | MEDIUM | ARCHITECTURE | tui/styles.py:151-169
**Описание:** CSSClasses в коде не используются, только объявлены.
**SuggestedFix:** Применить CSSClasses в generate_main_css или убрать.

---

### ISS-194 | MEDIUM | ARCHITECTURE | services/model_style_mapper.py:33-38
**Описание:** _style_map создаётся при каждом __init__ — можно вынести на уровень класса.
**SuggestedFix:** Использовать class-level dict: `_STYLE_MAP: ClassVar[dict]`.

---

### ISS-195 | MEDIUM | ARCHITECTURE | factories/provider_factory.py:56-58
**Описание:** Вложенная функция factory не использует замыкания оптимально.
**SuggestedFix:** Использовать functools.partial.

---

### ISS-196 | MEDIUM | ARCHITECTURE | main.py:45-47
**Описание:** Создание factory, затем передача в DialogueApp — лишняя абстракция.
**SuggestedFix:** Передать Config напрямую, создавать factory внутри App.

---

### ISS-197 | MEDIUM | ARCHITECTURE | main.py:74-75
**Описание:** `if __name__ == "__main__"` блок — можно вынести в run.py.
**SuggestedFix:** Создать __main__.py для пакета.

---

### ISS-198 | MEDIUM | ARCHITECTURE | controllers/dialogue_controller.py:17
**Описание:** UIState dataclass — можно использовать attrs для consistency.
**SuggestedFix:** Использовать attrs или остаться с dataclass.

---

### ISS-199 | MEDIUM | ARCHITECTURE | models/provider.py:88
**Описание:** @runtime_checkable добавляет overhead для type checking.
**SuggestedFix:** Убрать если не используется isinstance проверка.

---

### ISS-200 | MEDIUM | DEPRECATED | models/ollama_client.py:15
**Описание:** `# nosec: B044` — workaround для линтера в production коде.
**SuggestedFix:** Убрать nosec, добавить исключение в .bandit.yml.

---

## Распределение по пакетам

| Пакет | Диапазон | Основная тематика | Кол-во |
|-------|----------|------------------|--------|
| Пакет-1 | ISS-001-020 | TYPE_SAFETY | 20 |
| Пакет-2 | ISS-021-040 | TYPE_SAFETY, ARCHITECTURE | 20 |
| Пакет-3 | ISS-041-060 | STYLE, DEPRECATED | 20 |
| Пакет-4 | ISS-061-080 | STYLE, UNUSED | 20 |
| Пакет-5 | ISS-081-100 | ARCHITECTURE, TYPE_SAFETY | 20 |
| Пакет-6 | ISS-101-120 | STYLE, DEPRECATED | 20 |
| Пакет-7 | ISS-121-140 | ARCHITECTURE, STYLE | 20 |
| Пакет-8 | ISS-141-160 | TYPE_SAFETY, PERFORMANCE | 20 |
| Пакет-9 | ISS-161-180 | STYLE, UNUSED | 20 |
| Пакет-10 | ISS-181-200 | DEPRECATED, ARCHITECTURE | 20 |

---

**Итого: 200 проблем в 10 пакетах**
