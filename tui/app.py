"""TUI приложение для диалога двух ИИ-моделей.

Этот модуль содержит только UI-компоненты и обработчики событий.
Бизнес-логика вынесена в сервисный слой (services/dialogue_service.py).
"""

from __future__ import annotations

import asyncio
import logging

import aiohttp
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    RichLog,
    Select,
    Static,
)

from config import Config, validate_ollama_url
from controllers.dialogue_controller import DialogueController, UIState
from models.conversation import Conversation
from models.ollama_client import OllamaClient, OllamaError
from services.dialogue_service import DialogueService, DialogueTurnResult
from tui.sanitizer import sanitize_response_for_display, sanitize_topic
from tui.styles import (
    MESSAGE_STYLES,
    StatusStyle,
    UI_IDS,
    generate_main_css,
)


def _get_status_style_string(style: StatusStyle | str) -> str:
    """
    Конвертировать StatusStyle в строку для отображения в UI.

    Args:
        style: StatusStyle enum или строка.

    Returns:
        Строковое представление стиля.
    """
    if isinstance(style, StatusStyle):
        mapping = {
            StatusStyle.INFO: "dim",
            StatusStyle.SUCCESS: "green",
            StatusStyle.WARNING: "yellow",
            StatusStyle.ERROR: "red",
        }
        return mapping.get(style, "dim")
    return style


MAIN_CSS = generate_main_css()

log = logging.getLogger(__name__)


def create_ollama_client(host: str) -> OllamaClient:
    """
    Фабрика для создания OllamaClient.

    Этот метод инкапсулирует создание клиента и позволяет
    легко заменять реализацию в будущем.

    Args:
        host: URL хоста Ollama.

    Returns:
        Настроенный экземпляр OllamaClient.
    """
    return OllamaClient(host=host)


class ModelSelectionScreen(ModalScreen):
    """Модальное окно для выбора двух моделей."""

    BINDINGS = [
        Binding("escape", "cancel", "Отмена"),
    ]

    def __init__(
        self,
        models: list[str],
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._available_models = models