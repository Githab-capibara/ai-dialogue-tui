# AI Dialogue TUI

TUI-приложение для организации диалога между двумя ИИ-моделями через Ollama.

---

## Возможности

- **Диалог двух моделей** — запустите одновременный обмен сообщениями между двумя моделями Ollama
- **TUI-интерфейс** — удобный текстовый интерфейс на базе Textual
- **Гибкая настройка** — настройте модели, параметры генерации и поведение через конфигурацию
- **Обработка ошибок** — корректная обработка ошибок подключения и генерации

---

## Требования

- Python 3.10+
- Ollama (локально или удалённо)

---

## Установка

### Клонирование репозитория

```bash
git clone https://github.com/Githab-capibara/ai-dialogue-tui.git
cd ai-dialogue-tui
```

### Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows
```

### Установка зависимостей

```bash
pip install -r requirements.txt
```

---

## Настройка

Создайте файл `.env` в корне проекта (необязательно):

```env
# Ollama хост (по умолчанию: http://localhost:11434)
OLLAMA_HOST=http://localhost:11434
```

### Конфигурация

Параметры модели и приложения настраиваются через `Config` в `models/config.py`:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `host` | URL Ollama | `http://localhost:11434` |
| `model_a` | Модель A | — |
| `model_b` | Модель B | — |
| `temperature` | Температура генерации | 0.7 |
| `max_tokens` | Максимум токенов | 500 |
| `timeout` | Таймаут запроса (сек) | 120 |

---

## Запуск

```bash
python3 main.py
```

### Управление

- **Enter** — отправить сообщение
- **Ctrl+C** — выход
- Выбор моделей через меню

---

## Архитектура

```
ai-dialogue-tui/
├── main.py                 # Точка входа
├── models/                 # Модели данных
│   ├── config.py          # Конфигурация
│   ├── conversation.py    # Модель диалога
│   ├── ollama_client.py   # Ollama API клиент
│   └── provider.py        # Абстракции провайдера
├── services/              # Бизнес-логика
│   ├── dialogue_service.py
│   ├── dialogue_runner.py
│   └── model_style_mapper.py
├── controllers/           # Контроллеры
│   └── dialogue_controller.py
├── tui/                   # UI-компоненты
│   ├── app.py            # Главное приложение
│   ├── constants.py      # Константы UI
│   ├── sanitizer.py      # Очистка вывода
│   └── styles.py         # Стили
├── factories/            # Фабрики
│   └── provider_factory.py
└── tests/                # Тесты
```

---

## Тестирование

```bash
python3 -m pytest
```

---

## Лицензия

MIT License — подробности в файле LICENSE.

---

## Автор

[Githab-capibara](https://github.com/Githab-capibara)