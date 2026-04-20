"""Service for mapping models to display styles.

This module contains logic for converting model state to UI styles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from models.conversation import ModelId


class StyleInfo(NamedTuple):
    """Style information for a model."""

    model_name: str
    style_id: str


class ModelStyleMapper:
    """Service for mapping model state to display style."""

    def __init__(self) -> None:
        """Initialize style mapper."""
        self._style_map: dict[ModelId, str] = {
            "A": "model_a",
            "B": "model_b",
        }

    def get_style_info(self, model_id: ModelId, model_name: str) -> StyleInfo:
        """Get style information for model.

        Args:
            model_id: Model identifier (A or B).
            model_name: Model name.

        Returns:
            Tuple (model_name, style_id).

        """
        style_id = self._style_map[model_id]
        return StyleInfo(model_name=model_name, style_id=style_id)

    def get_style_id(self, model_id: ModelId) -> str:
        """Get style identifier for model.

        Args:
            model_id: Model identifier (A or B).

        Returns:
            Style identifier (model_a or model_b).

        """
        return self._style_map[model_id]
