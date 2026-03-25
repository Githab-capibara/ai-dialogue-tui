# Архитектура AI Dialogue TUI

## Общая схема проекта

```
ai-dialogue-tui/
├── main.py                    # Точка входа
├── models/                    # Доменный слой
│   ├── __init__.py
│   ├── config.py              # Конфигурация (Config dataclass)
│   ├── provider.py            # Протокол ModelProvider + иерархия ProviderError
│   ├── ollama_client.py       # Реализация ModelProvider для Ollama
│   └── conversation.py        # Доменная логика диалога
├── services/                  # Сервисный слой
│   ├── __init__.py
│   └── dialogue_service.py    # Бизнес-логика диалога
├── controllers/               # Слой контроллеров
│   ├── __init__.py
│   └── dialogue_controller.py # Управление состоянием UI
├── tui/                       # Презентационный слой (Textual TUI)
│   ├── __init__.py
│   ├── app.py                 # Основное TUI приложение
│   ├── styles.py              # Централизованные стили и UI IDs
│   └── sanitizer.py           # Sanitizer Protocol + функции санитизации
└── tests/                     # Модульные тесты
    ├── __init__.py
    ├── test_critical.py       # Тесты критических функций
    ├── test_architecture.py   # Тесты архитектуры
    ├── test_fixes.py          # Тесты исправлений
    └── test_arch_fixes.py     # Тесты архитектурных изменений
```

## Архитектурные слои

Проект следует принципам **Clean Architecture** с разделением на слои:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │   tui/app.py    │  │ controllers/dialogue_       │   │
│  │   (Textual UI)  │  │ controller.py               │   │
│  └─────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ depends on
┌─────────────────────────────────────────────────────────┐
│                     Service Layer                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │ services/dialogue_service.py                    │    │
│  │ (бизнес-логика диалога, управление состоянием)  │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓ depends on
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                        │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ models/         │  │ models/ollama_client.py     │   │
│  │ conversation.py │  │ (реализация ModelProvider)  │   │
│  └─────────────────┘  └─────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐    │
│  │ models/provider.py                              │    │
│  │ (протокол ModelProvider - абстракция)           │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Направление зависимостей

Зависимости направлены **снизу вверх**:
- **Domain Layer** не зависит от других слоёв (чистая доменная логика)
- **Service Layer** зависит от Domain Layer
- **Presentation Layer** зависит от Service Layer и Domain Layer (через абстракции)

## Основные модули

### Domain Layer

#### `models/provider.py`
Протокол `ModelProvider` определяет абстракцию для работы с LLM-провайдерами:
```python
class ModelProvider(Protocol):
    async def list_models() -> list[str]: ...
    async def generate(model: str, messages: list[MessageDict]) -> str: ...
    async def close() -> None: ...
```

**Иерархия исключений ProviderError:**
- `ProviderError` — базовое исключение для всех ошибок провайдера
- `ProviderConfigurationError` — ошибки конфигурации (некорректный URL, параметры)
- `ProviderConnectionError` — ошибки подключения (недоступность хоста, таймауты)
- `ProviderGenerationError` — ошибки генерации (ошибки API, валидации ответа)

**Преимущества:**
- Возможность замены провайдера (Ollama → OpenAI → Anthropic) без изменения доменной логики
- Тестируемость через mock-реализации протокола
- Типизированная обработка ошибок через иерархию исключений

#### `models/conversation.py`
Класс `Conversation` управляет диалогом между двумя моделями:
- Хранит независимые контексты для каждой модели
- Реализует атомарные операции для предотвращения рассинхронизации
- Зависит только от протокола `ModelProvider`, не от конкретных реализаций

**Оптимизации:**
- `__slots__` в dataclass для уменьшения потребления памяти
- Early returns в `__post_init__` для предотвращения повторной инициализации
- `.copy()` при возврате контекста для безопасности (защита от внешних изменений)
- Присваивание новых списков в `clear_contexts()` для простоты и читаемости

#### `models/ollama_client.py`
Класс `OllamaClient` реализует протокол `ModelProvider` для Ollama API:
- Асинхронный HTTP-клиент на базе aiohttp
- Валидация ответов API
- Обработка ошибок с сохранением цепочки исключений

**Внутренние компоненты:**
- `_RequestValidator` — валидация входных параметров запросов
- `_ResponseHandler` — обработка и валидация ответов API
- `_HTTPSessionManager` — управление HTTP-сессиями и пулинг соединений
- `_ModelsCache` — TTL-кэширование списка моделей (TTL 300 секунд)

**Кэширование:**
- `list_models()` использует кэш с TTL 300 секунд для производительности
- Автоматическая инвалидация кэша при закрытии клиента

**Ограничение контекста:**
- `MAX_CONTEXT_LENGTH = 50` — максимальное количество сообщений в контексте
- Предотвращает переполнение памяти при длительных диалогах

**Обработка исключений:**
- Используется иерархия `ProviderError` для типизированной обработки ошибок
- Конкретные типы исключений вместо broad `Exception`:
  - `ProviderConnectionError` — ошибки подключения
  - `ProviderGenerationError` — ошибки генерации и валидации
- Сохранение цепочки исключений через `raise ... from`

**Валидация:**
- `_RequestValidator.validate_messages()` — валидация структуры сообщений
- `_ResponseHandler.validate_status_code()` — валидация HTTP статуса
- `validate_ollama_url()` — валидация URL хоста

**Оптимизации:**
- Кэшированные дефолтные опции (`_DEFAULT_OPTIONS`)
- `_HTTPSessionManager` для пулинга соединений
- List comprehension для эффективной обработки
- Early returns в функциях валидации

### Service Layer

#### `services/dialogue_service.py`
Класс `DialogueService` содержит бизнес-логику диалога:
- Методы: `run_dialogue_cycle()`, `start()`, `pause()`, `resume()`, `stop()`, `clear_history()`
- Управление состоянием: `_is_running`, `_is_paused`, `_turn_count`
- Зависимости внедряются через конструктор (`ModelProvider`, `Conversation`)

**Протокол `DialogueUICallback`:**
```python
class DialogueUICallback(Protocol):
    async def on_turn_complete(self, result: DialogueTurnResult) -> None: ...
    async def on_error(self, error: Exception) -> None: ...
    async def on_status_change(self, status: str) -> None: ...
```

### Presentation Layer

#### `controllers/dialogue_controller.py`
Класс `DialogueController` управляет состоянием UI:
- Обработчики команд: `handle_start()`, `handle_pause()`, `handle_clear()`, `handle_stop()`
- Зависит от `DialogueService`
- Использует протокол `UIState` для обновления UI

#### `tui/app.py`
Класс `DialogueApp` (Textual App) содержит только UI-логику:
- Композиция виджетов
- Обработчики событий UI
- Делегирует бизнес-логику в `DialogueController` и `DialogueService`
- Фабрика `create_ollama_client()` для создания клиента

#### `tui/styles.py`
Централизованные стили и идентификаторы:
- `MESSAGE_STYLES` — стили для сообщений
- `UI_IDS` — идентификаторы UI элементов (устраняет magic strings)
- `StatusStyle` — Enum для статусных сообщений
- `CSS_CLASSES` — CSS-классы
- `generate_main_css()` — генерация CSS из констант

#### `tui/sanitizer.py`
Функции санитизации для безопасного отображения:
- `sanitize_topic()` — экранирование специальных символов в теме
- `sanitize_response_for_display()` — экранирование markup и HTML

**Sanitizer Protocol:**
```python
@runtime_checkable
class Sanitizer(Protocol):
    def sanitize_topic(self, topic: str) -> str: ...
    def sanitize_response_for_display(self, response: str) -> str: ...
```
- Позволяет использовать dependency injection для тестируемости
- Определяет интерфейс для компонентов санитизации

## Паттерны проектирования

### 1. Dependency Injection
Все зависимости внедряются через конструкторы:
```python
class DialogueService:
    def __init__(
        self,
        provider: ModelProvider,
        conversation: Conversation,
    ) -> None: ...
```

### 2. Protocol (Interface)
Протоколы для абстракций:
- `ModelProvider` — абстракция провайдера моделей
- `DialogueUICallback` — абстракция UI-коллбеков
- `UIState` — абстракция состояния UI
- `Sanitizer` — абстракция санитизации данных

### 3. Service Layer
Бизнес-логика вынесена в отдельный сервисный слой:
- `DialogueService` — бизнес-логика диалога
- `DialogueController` — логика управления UI

### 4. Data Class
Конфигурация и структуры данных:
- `Config` — параметры приложения
- `MessageDict` — TypedDict для сообщений
- `DialogueTurnResult` — результат хода диалога
- `UIState` — состояние UI

### 5. Logging
Логирование для отладки и мониторинга:
- Модульный логгер в `models/conversation.py`

## SOLID принципы

Проект следует принципам SOLID:

**S — Single Responsibility Principle (Принцип единственной ответственности):**
- Каждый класс имеет одну ответственность:
  - `OllamaClient` — взаимодействие с Ollama API
  - `Conversation` — управление контекстом диалога
  - `DialogueService` — бизнес-логика диалога
  - `DialogueController` — управление состоянием UI
  - `_RequestValidator`, `_ResponseHandler`, `_HTTPSessionManager` — отдельные компоненты для валидации, обработки ответов и управления сессиями

**O — Open/Closed Principle (Принцип открытости/закрытости):**
- Протокол `ModelProvider` позволяет добавлять новых провайдеров без изменения существующего кода
- `DialogueService` открыт для расширения через новые реализации `ModelProvider`

**L — Liskov Substitution Principle (Принцип подстановки Барбары Лисков):**
- Любая реализация `ModelProvider` может быть подставлена вместо базового типа
- Иерархия `ProviderError` позволяет заменять базовые исключения на специфичные

**I — Interface Segregation Principle (Принцип разделения интерфейса):**
- Протоколы узкоспециализированы:
  - `ModelProvider` — только методы для работы с моделями
  - `DialogueUICallback` — только коллбеки для UI
  - `Sanitizer` — только методы санитизации

**D — Dependency Inversion Principle (Принцип инверсии зависимостей):**
- Модули верхнего уровня не зависят от модулей нижнего уровня
- Все зависимости определяются через абстракции (протоколы)
- Domain Layer не зависит от Infrastructure Layer

## Тестируемость

### Модульные тесты
- `tests/test_critical.py` — тесты критических функций
- `tests/test_architecture.py` — тесты архитектуры
- `tests/test_fixes.py` — тесты исправлений
- `tests/test_arch_fixes.py` — тесты архитектурных изменений
- `tests/test_audit_fixes.py` — тесты аудита кода

**Всего: 208 тестов**

### Архитектурные тесты проверяют:
- Отсутствие зависимостей Domain Layer от Infrastructure
- Реализацию протокола `ModelProvider` в `OllamaClient`
- Внедрение зависимостей через конструкторы
- Возможность замены провайдера без изменения домена
- Отсутствие циклических зависимостей
- Разделение модулей

### Запуск тестов:
```bash
pytest tests/ -v
```

## Конфигурация

### `models/config.py`
Класс `Config` (dataclass) с параметрами:
- `temperature`, `max_tokens`, `request_timeout`, `pause_between_messages`
- `default_system_prompt`, `ollama_host`
- Валидация URL через `validate_ollama_url()`

### Константы по умолчанию

Модуль определяет константы для параметров конфигурации:
- `DEFAULT_TEMPERATURE = 0.7` — температура генерации
- `DEFAULT_MAX_TOKENS = 200` — максимальное количество токенов
- `DEFAULT_REQUEST_TIMEOUT = 60` — таймаут запроса (сек)
- `DEFAULT_PAUSE_BETWEEN_MESSAGES = 1.0` — пауза между сообщениями (сек)

### Валидация конфигурации

Класс `Config` использует `__post_init__` для автоматической валидации:
- `_validate_temperature()` — проверка диапазона [0.0, 1.0]
- `_validate_max_tokens()` — проверка минимального значения >= 1
- `_validate_request_timeout()` — проверка минимального значения >= 1
- `_validate_pause_between_messages()` — проверка минимального значения >= 0.0
- `validate_ollama_url()` — валидация HTTP/HTTPS URL через `urllib.parse`

При некорректных значениях выбрасывается `ValueError` с подробным сообщением.

### Оптимизации

- **`__slots__`**: Класс `Config` использует `slots=True` для уменьшения потребления памяти
- **`frozen=True`**: Dataclass заморожен для неизменяемости экземпляров
- **Early returns**: Функции валидации используют ранние возвраты для эффективности

## Расширяемость

### Добавление нового провайдера (например, OpenAI):
1. Создать класс `OpenAIProvider` реализующий `ModelProvider`
2. Внедрить через конструктор в `DialogueService`
3. Никаких изменений в доменной логике не требуется

### Добавление нового UI (например, веб-интерфейс):
1. Создать контроллер реализующий `UIState`
2. Использовать существующий `DialogueService`
3. Никаких изменений в бизнес-логике не требуется

## Инструменты качества кода

```bash
# Проверка и форматирование
ruff check .
ruff format .

# Статический анализ
pylint . --reports=yes

# Проверка зависимостей
deptry .
pip check
```

## Метрики качества

- **Pylint:** 10.00/10
- **Ruff:** All checks passed
- **Тесты:** 208 passed
- **Дублирование кода:** 0%
- **Циклические зависимости:** отсутствуют

---

*Документ обновлён: 25 марта 2026 г.*
