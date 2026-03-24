"""TUI приложение для диалога двух ИИ-моделей."""

from __future__ import annotations

import asyncio
from typing import Final

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
from textual.worker import Worker, WorkerState

from config import config
from models.conversation import Conversation
from models.ollama_client import OllamaClient, OllamaError


# Стили для разных типов сообщений
STYLE_MODEL_A: Final = "bold green"
STYLE_MODEL_B: Final = "bold blue"
STYLE_SYSTEM: Final = "dim italic yellow"
STYLE_ERROR: Final = "bold red"


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
    
    def compose(self) -> ComposeResult:
        with Container(id="model-selection-container"):
            yield Static("Выберите две модели для диалога", id="selection-title")
            
            with Horizontal(id="models-row"):
                with Vertical(id="model-a-container"):
                    yield Label("Модель A:", id="model-a-label")
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id="model-a-select",
                        value=self._available_models[0] if self._available_models else None,
                    )
                
                with Vertical(id="model-b-container"):
                    yield Label("Модель B:", id="model-b-label")
                    yield Select(
                        [(m, m) for m in self._available_models],
                        id="model-b-select",
                        value=self._available_models[1] if len(self._available_models) > 1 else (
                            self._available_models[0] if self._available_models else None
                        ),
                    )
            
            with Horizontal(id="selection-buttons"):
                yield Button("Начать диалог", id="start-btn", variant="primary")
                yield Button("Отмена", id="cancel-btn", variant="error")
    
    def action_cancel(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#start-btn")
    def on_start_pressed(self) -> None:
        model_a = self.query_one("#model-a-select", Select).value
        model_b = self.query_one("#model-b-select", Select).value
        
        if model_a == model_b:
            self.notify(
                "Выберите две разные модели!",
                title="Ошибка",
                severity="error",
            )
            return
        
        if model_a is Select.BLANK or model_b is Select.BLANK:
            self.notify(
                "Выберите обе модели!",
                title="Ошибка",
                severity="error",
            )
            return
        
        self.dismiss((model_a, model_b))
    
    @on(Button.Pressed, "#cancel-btn")
    def on_cancel_pressed(self) -> None:
        self.dismiss(None)


class TopicInputScreen(ModalScreen):
    """Модальное окно для ввода темы диалога."""
    
    BINDINGS = [
        Binding("escape", "cancel", "Отмена"),
        Binding("enter", "submit", "OK"),
    ]
    
    def compose(self) -> ComposeResult:
        with Container(id="topic-input-container"):
            yield Static("Введите тему диалога:", id="topic-label")
            yield Input(
                placeholder="Например: Спор о преимуществах Python перед Go",
                id="topic-input",
            )
            with Horizontal(id="topic-buttons"):
                yield Button("Начать", id="topic-start-btn", variant="primary")
                yield Button("Отмена", id="topic-cancel-btn", variant="error")
    
    def action_submit(self) -> None:
        self._submit_topic()
    
    def action_cancel(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#topic-start-btn")
    def on_start_pressed(self) -> None:
        self._submit_topic()
    
    @on(Button.Pressed, "#topic-cancel-btn")
    def on_cancel_pressed(self) -> None:
        self.dismiss(None)
    
    def _submit_topic(self) -> None:
        topic_input = self.query_one("#topic-input", Input)
        topic = topic_input.value.strip()
        
        if not topic:
            self.notify(
                "Введите тему диалога!",
                title="Ошибка",
                severity="error",
            )
            return
        
        self.dismiss(topic)


class DialogueApp(App):
    """Основное TUI приложение для диалога ИИ-моделей."""
    
    CSS = """
    #model-selection-container {
        align: center middle;
        height: 100%;
        background: $surface;
    }
    
    #selection-title {
        text-align: center;
        text-style: bold;
        padding: 1 2;
        margin-bottom: 2;
    }
    
    #models-row {
        height: auto;
        align: center middle;
    }
    
    #model-a-container, #model-b-container {
        width: 30;
        margin: 0 2;
        border: solid $primary;
        padding: 1 2;
    }
    
    #model-a-label, #model-b-label {
        margin-bottom: 1;
        text-align: center;
    }
    
    #selection-buttons {
        height: auto;
        align: center middle;
        margin-top: 2;
    }
    
    #selection-buttons Button {
        margin: 0 1;
    }
    
    #topic-input-container {
        align: center middle;
        height: 100%;
        background: $surface;
    }
    
    #topic-label {
        text-align: center;
        text-style: bold;
        padding: 1 2;
        margin-bottom: 1;
    }
    
    #topic-input {
        width: 60;
        margin-bottom: 2;
    }
    
    #topic-buttons {
        height: auto;
        align: center middle;
    }
    
    #topic-buttons Button {
        margin: 0 1;
    }
    
    #main-container {
        height: 100%;
    }
    
    #status-bar {
        height: 3;
        background: $surface;
        border: solid $primary;
        margin: 1;
        padding: 0 2;
    }
    
    #status-row {
        height: 100%;
        align: left middle;
    }
    
    #status-label {
        width: auto;
        padding: 0 1;
    }
    
    #dialogue-log {
        height: 1fr;
        margin: 0 1;
        border: solid $secondary;
    }
    
    #controls-bar {
        height: 4;
        background: $surface;
        border: solid $primary;
        margin: 1;
        padding: 0 2;
    }
    
    #controls-row {
        height: 100%;
        align: center middle;
    }
    
    #controls-row Button {
        margin: 0 1;
        width: 16;
    }
    
    .model-a-message {
        color: $success;
        text-style: bold;
    }
    
    .model-b-message {
        color: $accent;
        text-style: bold;
    }
    
    .system-message {
        color: $warning;
        text-style: italic;
    }
    
    .error-message {
        color: $error;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Выход", priority=True),
        Binding("ctrl+p", "toggle_pause", "Пауза/Старт"),
        Binding("ctrl+r", "clear_log", "Очистить"),
        Binding("ctrl+c", "", ""),  # Отключаем стандартное поведение
    ]
    
    TITLE = "AI Dialogue TUI"
    SUB_TITLE = "Диалог двух ИИ-моделей через Ollama"
    
    def __init__(self) -> None:
        super().__init__()
        self._client: OllamaClient | None = None
        self._conversation: Conversation | None = None
        self._dialogue_task: asyncio.Task | None = None
        self._is_paused = False
        self._models: list[str] = []
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="main-container"):
            # Статус бар
            with Container(id="status-bar"):
                with Horizontal(id="status-row"):
                    yield Label("Статус: ", id="status-label")
                    yield Label("Ожидание...", id="status-value")
            
            # Лог диалога
            yield RichLog(id="dialogue-log", highlight=True, markup=True)
            
            # Панель управления
            with Container(id="controls-bar"):
                with Horizontal(id="controls-row"):
                    yield Button("▶ Старт", id="start-btn", variant="success")
                    yield Button("⏸ Пауза", id="pause-btn", variant="warning")
                    yield Button("🗑 Очистить", id="clear-btn", variant="default")
                    yield Button("✕ Выход", id="exit-btn", variant="error")
        
        yield Footer()
    
    async def on_mount(self) -> None:
        """Инициализация при запуске приложения."""
        self._client = OllamaClient()
        
        try:
            # Получаем список моделей
            self._models = await self._client.list_models()
            
            if not self._models:
                self.notify(
                    "Не найдено установленных моделей Ollama!\n"
                    "Установите модель командой: ollama pull llama3",
                    title="Ошибка",
                    severity="error",
                    timeout=10,
                )
                self.query_one("#status-value", Label).update(
                    "[red]Нет моделей[/red]"
                )
                return
            
            # Показываем окно выбора моделей
            def on_models_selected(result: tuple[str, str] | None) -> None:
                if result is None:
                    self.exit(1)
                    return
                
                model_a, model_b = result
                self._setup_conversation(model_a, model_b)
            
            # Показываем модальное окно выбора моделей
            self.push_screen(
                ModelSelectionScreen(self._models),
                callback=on_models_selected,
            )
            
        except OllamaError as e:
            self.notify(
                str(e),
                title="Ошибка подключения к Ollama",
                severity="error",
                timeout=10,
            )
            self.query_one("#status-value", Label).update(
                f"[red]Ошибка: {e}[/red]"
            )
        except Exception as e:
            self.notify(
                f"Неожиданная ошибка: {e}",
                title="Ошибка",
                severity="error",
            )
            self.query_one("#status-value", Label).update(
                f"[red]Ошибка: {e}[/red]"
            )
    
    def _setup_conversation(self, model_a: str, model_b: str) -> None:
        """Настроить диалог после выбора моделей."""
        def on_topic_entered(topic: str | None) -> None:
            if topic is None:
                self.exit(1)
                return
            
            self._conversation = Conversation(
                model_a=model_a,
                model_b=model_b,
                topic=topic,
            )
            
            # Обновляем заголовок и статус
            self.SUB_TITLE = f"{model_a} ↔ {model_b} | Тема: {topic}"
            self.query_one("#status-value", Label).update(
                f"[green]Готов к запуску[/green]"
            )
            
            # Логируем начало
            log = self.query_one("#dialogue-log", RichLog)
            log.write(
                f"[bold]=== Диалог начат ===[/bold]\n"
                f"[bold]Модель A:[/bold] [{STYLE_MODEL_A}]{model_a}[/{STYLE_MODEL_A}]\n"
                f"[bold]Модель B:[/bold] [{STYLE_MODEL_B}]{model_b}[/{STYLE_MODEL_B}]\n"
                f"[bold]Тема:[/bold] {topic}\n"
                f"[dim]Нажмите 'Старт' для начала диалога[/dim]"
            )
        
        # Показываем окно ввода темы
        self.push_screen(TopicInputScreen(), callback=on_topic_entered)
    
    @on(Button.Pressed, "#start-btn")
    def on_start_pressed(self) -> None:
        """Запуск диалога."""
        if self._conversation is None:
            self.notify(
                "Сначала выберите модели и тему!",
                title="Ошибка",
                severity="error",
            )
            return
        
        if self._dialogue_task and not self._dialogue_task.done():
            self.notify("Диалог уже запущен!", title="Инфо", severity="information")
            return
        
        self._is_paused = False
        self._dialogue_task = asyncio.create_task(self._run_dialogue())
        self.query_one("#status-value", Label).update(
            f"[green]Диалог идёт...[/green]"
        )
        self.notify("Диалог запущен!", title="Старт", severity="information")
    
    @on(Button.Pressed, "#pause-btn")
    def on_pause_pressed(self) -> None:
        """Пауза/продолжение диалога."""
        self.action_toggle_pause()
    
    @on(Button.Pressed, "#clear-btn")
    def on_clear_pressed(self) -> None:
        """Очистка лога и контекстов."""
        if self._conversation:
            self._conversation.clear_contexts()
        
        log = self.query_one("#dialogue-log", RichLog)
        log.clear()
        log.write("[dim]История очищена[/dim]")
        
        self.notify("История очищена!", title="Очистка", severity="information")
    
    @on(Button.Pressed, "#exit-btn")
    def on_exit_pressed(self) -> None:
        """Выход из приложения."""
        self.exit()
    
    def action_toggle_pause(self) -> None:
        """Переключить паузу."""
        if self._conversation is None:
            return
        
        self._is_paused = not self._is_paused
        
        status_label = self.query_one("#status-value", Label)
        if self._is_paused:
            status_label.update("[yellow]На паузе[/yellow]")
            self.notify("Диалог приостановлен", title="Пауза", severity="warning")
        else:
            status_label.update("[green]Диалог идёт...[/green]")
            self.notify("Диалог продолжен", title="Старт", severity="information")
    
    def action_clear_log(self) -> None:
        """Очистить лог (горячая клавиша)."""
        self.on_clear_pressed()
    
    async def _run_dialogue(self) -> None:
        """Основной цикл диалога."""
        if not self._client or not self._conversation:
            return
        
        log = self.query_one("#dialogue-log", RichLog)
        turn_count = 0
        
        try:
            while not self._is_paused:
                turn_count += 1
                
                # Получаем текущую модель
                model_name = self._conversation.get_current_model_name()
                model_id = self._conversation.current_turn
                style = STYLE_MODEL_A if model_id == "A" else STYLE_MODEL_B
                
                # Обновляем статус
                self.call_from_thread(
                    self.query_one("#status-value", Label).update,
                    f"[bold {style}]Ход: {model_name}[/bold {style}]",
                )
                
                try:
                    # Генерируем ответ
                    _, _, response = await self._conversation.process_turn(
                        self._client
                    )
                    
                    # Форматируем и выводим сообщение
                    formatted_response = response.replace("\n", " ")
                    if len(formatted_response) > 100:
                        formatted_response = formatted_response[:100] + "..."
                    
                    message = (
                        f"\n[{style}]Ход {turn_count}: {model_name}[/\n"
                        f"  {formatted_response}"
                    )
                    self.call_from_thread(log.write, message)
                    
                except OllamaError as e:
                    error_msg = f"\n[{STYLE_ERROR}]Ошибка ({model_name}): {e}[/]"
                    self.call_from_thread(log.write, error_msg)
                    self.notify(
                        f"Ошибка генерации: {e}",
                        title="Ошибка",
                        severity="error",
                    )
                
                # Пауза между сообщениями
                await asyncio.sleep(config.pause_between_messages)
                
        except asyncio.CancelledError:
            # Нормальное завершение при отмене задачи
            pass
        except Exception as e:
            self.call_from_thread(
                log.write,
                f"\n[{STYLE_ERROR}]Критическая ошибка: {e}[/]",
            )
        finally:
            self.call_from_thread(
                self.query_one("#status-value", Label).update,
                "[dim]Остановлен[/dim]",
            )
    
    async def on_unmount(self) -> None:
        """Очистка при закрытии приложения."""
        # Отменяем задачу диалога
        if self._dialogue_task and not self._dialogue_task.done():
            self._dialogue_task.cancel()
            try:
                await self._dialogue_task
            except asyncio.CancelledError:
                pass
        
        # Закрываем клиент
        if self._client:
            await self._client.close()
