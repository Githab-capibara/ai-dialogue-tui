"""Сервис для маппинга моделей на стили отображения.

Этот модуль содержит логику преобразования состояния модели в UI стили.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from models.conversation import ModelId


class StyleInfo(NamedTuple):
    """Информация о стиле для модели."""

    model_name: str
    style_id: str


class ModelStyleMapper:
    """Сервис для маппинга состояния модели на стиль отображения."""

    def __init__(self) -> None:
        """Инициализация маппера стилей."""
        self._style_map: dict[ModelId, str] = {
            "A": "model_a",
            "B": "model_b",
        }

    def get_style_info(self, model_id: ModelId, model_name: str) -> StyleInfo:
        """Получить информацию о стиле для модели.

        Args:
            model_id: Идентификатор модели (A или B).
            model_name: Название модели.

        Returns:
            Кортеж (model_name, style_id).

        """
        style_id = self._style_map[model_id]
        return StyleInfo(model_name=model_name, style_id=style_id)

    def get_style_id(self, model_id: ModelId) -> str:
        """Получить идентификатор стиля для модели.

        Args:
            model_id: Идентификатор модели (A или B).

        Returns:
            Идентификатор стиля (model_a или model_b).

        """
        return self._style_map[model_id]
