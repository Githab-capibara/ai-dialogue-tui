# AI Dialogue TUI

TUI-приложение для диалога двух локальных ИИ-моделей через Ollama.

## Особенности

- 🎨 Современный TUI-интерфейс на базе **Textual**
- 🤖 Автоматическое обнаружение установленных моделей Ollama
- 💬 Независимые контексты для каждой модели
- ⏸️ Управление диалогом: старт, пауза, очистка истории
- ⌨️ Горячие клавиши для быстрого управления
- 🔄 Асинхронная архитектура без блокировки интерфейса

## Требования

- Python 3.10+
- Установленный и запущенный **Ollama** (https://ollama.ai)
- Как минимум одна установленная модель Ollama

## Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/Githab-capibara/ai-dialogue-tui.git
cd ai-dialogue-tui

# Создайте виртуальное окружение (рекомендуется)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt
```

## Быстрый старт

1. Убедитесь, что Ollama запущен:
   ```bash
   ollama serve
   ```

2. Установите модели (если ещё не установлены):
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```

3. Запустите приложение:
   ```bash
   python main.py
   ```

## Использование

1. **Выбор моделей**: При запуске выберите две разные модели из списка доступных.

2. **Ввод темы**: Введите тему диалога (например, "Спор о преимуществах Python перед Go").

3. **Запуск диалога**: Нажмите кнопку "Старт" или `Ctrl+P` для начала диалога.

4. **Управление**:
   - `Ctrl+P` — Пауза/Продолжить диалог
   - `Ctrl+R` — Очистить историю
   - `Ctrl+Q` — Выход
   - Кнопки внизу экрана — альтернативное управление мышью

## Архитектура

Проект следует принципам **Clean Architecture** с разделением на слои:

```
ai_dialogue_tui/
├── main.py                    # Точка входа
├── models/                    # Domain Layer
│   ├── __init__.py
│   ├── config.py              # Конфигурация (Config dataclass)
│   ├── provider.py            # Протокол ModelProvider + иерархия ProviderError
│   ├── ollama_client.py       # Реализация ModelProvider для Ollama
│   └── conversation.py        # Доменная логика диалога
├── services/                  # Service Layer
│   ├── __init__.py
│   └── dialogue_service.py    # Бизнес-логика диалога
├── controllers/               # Controller Layer
│   ├── __init__.py
│   └── dialogue_controller.py # Управление состоянием UI
├── tui/                       # Presentation Layer
│   ├── __init__.py
│   ├── app.py                 # Textual TUI приложение
│   ├── styles.py              # Централизованные стили и UI IDs
│   └── sanitizer.py           # Sanitizer Protocol + функции санитизации
├── tests/                     # Модульные тесты
│   ├── __init__.py
│   ├── test_critical.py       # Тесты критических функций
│   ├── test_architecture.py   # Тесты архитектуры
│   ├── test_fixes.py          # Тесты исправлений
│   ├── test_arch_fixes.py     # Тесты архитектурных изменений
│   ├── test_audit_fixes.py    # Тесты аудита кода
│   ├── test_arch_audit_fixes.py # Тесты архитектурных исправлений аудита
│   ├── test_audit_fixes_verification.py # Тесты верификации исправлений аудита
│   ├── test_architecture_integrity.py # Тесты целостности архитектуры
│   └── test_code_audit_fixes.py # Тесты исправлений по результатам аудита
└── pytest.ini                 # Конфигурация pytest
```

### Ключевые компоненты

- **ModelProvider** (протокол): Абстракция для работы с LLM-провайдерами
- **ProviderError иерархия**: Типизированные исключения для обработки ошибок
  - `ProviderError` — базовое исключение
  - `ProviderConfigurationError` — ошибки конфигурации
  - `ProviderConnectionError` — ошибки подключения
  - `ProviderGenerationError` — ошибки генерации
- **OllamaClient**: Реализация ModelProvider для Ollama API
- **Conversation**: Доменная логика диалога между двумя моделями
- **DialogueService**: Бизнес-логика диалога (сервисный слой)
- **DialogueController**: Управление состоянием UI (контроллер)
- **DialogueApp**: TUI-приложение на базе Textual

Подробное описание архитектуры см. в [ARCHITECTURE.md](ARCHITECTURE.md).

## Конфигурация

Параметры можно изменить в `models/config.py`:

```python
# Константы по умолчанию
DEFAULT_TEMPERATURE: float = 0.7           # Температура генерации (0.0-1.0)
DEFAULT_MAX_TOKENS: int = 200              # Максимальная длина ответа
DEFAULT_REQUEST_TIMEOUT: int = 60          # Таймаут запроса (сек)
DEFAULT_PAUSE_BETWEEN_MESSAGES: float = 1.0  # Пауза между сообщениями (сек)

# Класс Config использует __slots__ для оптимизации памяти
@dataclass(frozen=True, slots=True)
class Config:
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    request_timeout: int = DEFAULT_REQUEST_TIMEOUT
    pause_between_messages: float = DEFAULT_PAUSE_BETWEEN_MESSAGES
    default_system_prompt: str = "..."
    ollama_host: str = "http://localhost:11434"
```

### Валидация конфигурации

Класс `Config` включает автоматическую валидацию в `__post_init__`:
- **temperature**: диапазон [0.0, 1.0]
- **max_tokens**: >= 1
- **request_timeout**: >= 1
- **pause_between_messages**: >= 0.0
- **ollama_host**: валидный HTTP/HTTPS URL

При некорректных значениях выбрасывается `ValueError`.

## Тестирование

Проект использует pytest для модульного тестирования:

```bash
# Запустить все тесты
pytest tests/ -v

# Запустить тесты с покрытием
pytest tests/ -v --cov=. --cov-report=term-missing
```

Включено **248 тестов**:
- **test_critical.py** — тесты критических функций (валидация, атомарность, санитизация)
- **test_architecture.py** — тесты архитектуры (слои, зависимости, протоколы)
- **test_fixes.py** — тесты исправлений и оптимизаций
- **test_arch_fixes.py** — тесты архитектурных улучшений
- **test_audit_fixes.py** — тесты аудита кода
- **test_architecture_integrity.py** — тесты целостности архитектуры
- **test_audit_fixes_verification.py** — тесты верификации исправлений аудита
- **test_code_audit_fixes.py** — тесты исправлений по результатам аудита кода
- **test_architecture_refactor.py** — тесты архитектурного рефакторинга

## Инструменты качества кода

Проект использует следующие инструменты для поддержания качества кода:

```bash
# Проверка и форматирование кода
ruff check .
ruff format .

# Статический анализ
pylint . --reports=yes

# Проверка зависимостей
deptry .
pip check
```

### Метрики качества

- **Pylint:** 10.00/10
- **Ruff:** All checks passed
- **Тесты:** 248 passed
- **Дублирование кода:** 0%

## Как это работает

1. Каждая модель имеет свой независимый контекст (историю сообщений)
2. При ходе модели её ответ добавляется:
   - В её собственный контекст как `assistant`
   - В контекст другой модели как `user`
3. Это позволяет моделям "понимать" друг друга, сохраняя независимые роли
4. Системный промпт с темой добавляется в оба контекста при старте

## Пример диалога

```
Тема: Спор о преимуществах Python перед Go

Ход 1: llama3
  Python превосходит Go благодаря своей экосистеме библиотек для ML и Data Science...

Ход 2: mistral
  Но Go обеспечивает лучшую производительность и простоту развёртывания...

Ход 3: llama3
  Согласен, однако для прототипирования Python остаётся незаменимым...
```

## Лицензия

MIT
