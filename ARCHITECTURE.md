# Архитектура AI Dialogue TUI

## Общая схема проекта

```
ai-dialogue-tui/
├── main.py                    # Точка входа
├── config.py                  # Конфигурация (Config dataclass)
├── models/                    # Доменный слой
│   ├── __init__.py
│   ├── provider.py            # Протокол ModelProvider (абстракция)
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
│   └── styles.py              # Централизованные стили и UI IDs
└── tests/                     # Модульные тесты
    ├── __init__.py
    ├── test_critical.py       # Тесты критических функций
    └── test_architecture.py   # Тесты архитектуры
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

**Преимущества:**
- Возможность замены провайдера (Ollama → OpenAI → Anthropic) без изменения доменной логики
- Тестируемость через mock-реализации протокола

#### `models/conversation.py`
Класс `Conversation` управляет диалогом между двумя моделями:
- Хранит независимые контексты для каждой модели
- Реализует атомарные операции для предотвращения рассинхронизации
- Зависит только от протокола `ModelProvider`, не от конкретных реализаций

#### `models/ollama_client.py`
Класс `OllamaClient` реализует протокол `ModelProvider` для Ollama API:
- Асинхронный HTTP-клиент на базе aiohttp
- Валидация ответов API
- Обработка ошибок с сохранением цепочки исключений

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

#### `tui/styles.py`
Централизованные стили и идентификаторы:
- `MESSAGE_STYLES` — стили для сообщений
- `UI_IDS` — идентификаторы UI элементов (устраняет magic strings)
- `CSS_CLASSES` — CSS-классы
- `generate_main_css()` — генерация CSS из констант

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

### 3. Service Layer
Бизнес-логика вынесена в отдельный сервисный слой:
- `DialogueService` — бизнес-логика диалога
- `DialogueController` — логика управления UI

### 4. Data Class
Конфигурация и структуры данных:
- `Config` — параметры приложения
- `MessageDict` — TypedDict для сообщений
- `DialogueTurnResult` — результат хода диалога

## Тестируемость

### Модульные тесты
- `tests/test_critical.py` — 33 теста критических функций
- `tests/test_architecture.py` — 20 тестов архитектуры

### Архитектурные тесты проверяют:
- Отсутствие зависимостей Domain Layer от Infrastructure
- Реализацию протокола `ModelProvider` в `OllamaClient`
- Внедрение зависимостей через конструкторы
- Возможность замены провайдера без изменения домена

### Запуск тестов:
```bash
pytest tests/ -v
```

## Конфигурация

### `config.py`
Класс `Config` (dataclass) с параметрами:
- `temperature`, `max_tokens`, `request_timeout`, `pause_between_messages`
- `default_system_prompt`, `ollama_host`
- Валидация URL через `validate_ollama_url()`

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
- **Тесты:** 60 passed
- **Дублирование кода:** 0%
- **Циклические зависимости:** отсутствуют

---

*Документ обновлён: 24 марта 2026 г.*
