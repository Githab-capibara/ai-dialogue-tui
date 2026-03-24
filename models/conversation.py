"""Логика диалога и хранение контекстов для двух моделей."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from config import config
from models.ollama_client import OllamaClient


ModelId = Literal["A", "B"]


@dataclass
class Conversation:
    """
    Управление диалогом между двумя моделями.
    
    Каждая модель имеет свой независимый контекст (историю сообщений).
    Ответ одной модели добавляется в контекст другой как сообщение от пользователя.
    """
    
    model_a: str  # Название модели A
    model_b: str  # Название модели B
    topic: str  # Тема диалога
    
    # Контексты для каждой модели (списки сообщений в формате Ollama)
    _context_a: list[dict[str, str]] = field(default_factory=list)
    _context_b: list[dict[str, str]] = field(default_factory=list)
    
    # Чей сейчас ход
    _current_turn: ModelId = "A"
    
    # Системный промпт
    _system_prompt: str = field(init=False)
    
    def __post_init__(self) -> None:
        """Инициализация системного промпта после создания объекта."""
        self._system_prompt = config.default_system_prompt.format(
            topic=self.topic
        )
        # Добавляем системный промпт в оба контекста
        self._context_a.append({
            "role": "system",
            "content": self._system_prompt
        })
        self._context_b.append({
            "role": "system",
            "content": self._system_prompt
        })
    
    def add_message(
        self,
        model_id: ModelId,
        role: str,
        content: str,
    ) -> None:
        """
        Добавить сообщение в контекст указанной модели.
        
        Args:
            model_id: Идентификатор модели (A или B).
            role: Роль сообщения ("user", "assistant", "system").
            content: Текст сообщения.
        """
        context = self._context_a if model_id == "A" else self._context_b
        context.append({"role": role, "content": content})
    
    def get_context(self, model_id: ModelId) -> list[dict[str, str]]:
        """
        Получить историю сообщений для указанной модели.
        
        Args:
            model_id: Идентификатор модели (A или B).
            
        Returns:
            Список сообщений в формате Ollama.
        """
        context = self._context_a if model_id == "A" else self._context_b
        return context.copy()
    
    def switch_turn(self) -> ModelId:
        """
        Переключить ход на другую модель.
        
        Returns:
            Идентификатор модели, которой сейчас ходить.
        """
        self._current_turn = "B" if self._current_turn == "A" else "A"
        return self._current_turn
    
    @property
    def current_turn(self) -> ModelId:
        """Получить модель, которой сейчас ходить."""
        return self._current_turn
    
    def get_current_model_name(self) -> str:
        """Получить название текущей модели."""
        return self.model_a if self._current_turn == "A" else self.model_b
    
    def get_other_model_name(self) -> str:
        """Получить название другой модели."""
        return self.model_b if self._current_turn == "A" else self.model_a
    
    async def generate_response(
        self,
        client: OllamaClient,
    ) -> tuple[ModelId, str]:
        """
        Сгенерировать ответ для текущей модели.
        
        Args:
            client: Клиент Ollama для генерации.
            
        Returns:
            Кортеж (идентификатор модели, сгенерированный ответ).
        """
        model_id = self._current_turn
        model_name = self.get_current_model_name()
        context = self.get_context(model_id)
        
        response = await client.generate(
            model=model_name,
            messages=context,
        )
        
        return model_id, response
    
    async def process_turn(
        self,
        client: OllamaClient,
    ) -> tuple[str, str, str]:
        """
        Обработать один ход диалога.
        
        Генерирует ответ текущей модели, добавляет его в оба контекста
        (как assistant для текущей модели и как user для другой),
        затем переключает ход.
        
        Args:
            client: Клиент Ollama для генерации.
            
        Returns:
            Кортеж (название модели, роль "assistant", текст ответа).
        """
        model_id = self._current_turn
        model_name = self.get_current_model_name()
        
        # Генерируем ответ
        _, response = await self.generate_response(client)
        
        # Добавляем ответ в контекст текущей модели как assistant
        self.add_message(model_id, "assistant", response)
        
        # Добавляем ответ в контекст другой модели как user
        other_id: ModelId = "B" if model_id == "A" else "A"
        self.add_message(other_id, "user", response)
        
        # Переключаем ход
        self.switch_turn()
        
        return model_name, "assistant", response
    
    def clear_contexts(self) -> None:
        """
        Очистить оба контекста, сохранив только системный промпт и тему.
        """
        self._context_a = [{
            "role": "system",
            "content": self._system_prompt
        }]
        self._context_b = [{
            "role": "system",
            "content": self._system_prompt
        }]
        self._current_turn = "A"
    
    def get_context_stats(self) -> dict[str, int]:
        """
        Получить статистику контекстов.
        
        Returns:
            Словарь с количеством сообщений в каждом контексте.
        """
        return {
            "model_a_messages": len(self._context_a),
            "model_b_messages": len(self._context_b),
        }
