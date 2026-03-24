"""Конфигурация приложения AI Dialogue TUI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Параметры конфигурации для диалога ИИ-моделей."""
    
    # Параметры генерации Ollama
    temperature: float = 0.7
    max_tokens: int = 200
    
    # Таймауты и задержки
    request_timeout: int = 60  # секунд на запрос к Ollama
    pause_between_messages: float = 1.0  # секунд между сообщениями
    
    # Системный промпт
    default_system_prompt: str = (
        "Ты участвуешь в диалоге на тему '{topic}'. "
        "Отвечай кратко и по существу. Не повторяйся. "
        "Веди себя как живой собеседник."
    )
    
    # URL Ollama API (по умолчанию локальный)
    ollama_host: str = "http://localhost:11434"


# Глобальный экземпляр конфигурации
config = Config()
