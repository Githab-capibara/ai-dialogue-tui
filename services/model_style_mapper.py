"""Сервис для маппинга моделей на стили отображения.

Этот модуль содержит логику преобразования состояния модели в UI стили.
"""

from __future__ import annotations

from dataclasses import dataclass

from models.conversation import ModelId


@dataclass
class ModelStyleInfo:
    """
    Информация о стиле модели.

    Attributes:
        model_name: Название модели.
        style_id: Идентификатор стиля (model_a или model_b).
        model_id: Идентификатор модели (A или B).
    """

    model_name: str
    style_id: str
    model_id: ModelId


class ModelStyleMapper:
    """
    Сервис для маппинга состояния модели на стиль отображения.

    Инкапсулирует логику преобразования ModelId в CSS стиль.

    Example:
        >>> mapper = ModelStyleMapper()
        >>> info = mapper.get_style_info("A", "llama3")
        >>> info.style_id  # "model_a"
    """

    def __init__(self) -> None:
        """Инициализация маппера стилей."""
        self._style_map: dict[ModelId, str] = {
            "A": "model_a",
            "B": "model_b",
        }

    def get_style_info(self, model_id: ModelId, model_name: str) -> ModelStyleInfo:
        """
        Получить информацию о стиле для модели.

        Args:
            model_id: Идентификатор модели (A или B).
            model_name: Название модели.

        Returns:
            ModelStyleInfo с информацией о стиле.
        """
        style_id = self._style_map[model_id]
        return ModelStyleInfo(
            model_name=model_name,
            style_id=style_id,
            model_id=model_id,
        )

    def get_style_id(self, model_id: ModelId) -> str:
        """
        Получить идентификатор стиля для модели.

        Args:
            model_id: Идентификатор модели (A или B).

        Returns:
            Идентификатор стиля (model_a или model_b).
        """
        return self._style_map[model_id]
