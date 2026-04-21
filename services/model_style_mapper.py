"""Service for mapping models to display styles.

This module contains logic for converting model state to UI styles.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, NamedTuple

if TYPE_CHECKING:
    from models.conversation import ModelId

__all__ = ["ModelStyleMapper", "StyleInfo"]


class StyleInfo(NamedTuple):
    """Style information for a model."""

    model_name: str
    style_id: str


class ModelStyleMapper:
    """Service for mapping model state to display style."""

    _STYLE_MAP: ClassVar[dict[str, str]] = {
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
        style_id = self._STYLE_MAP[model_id]
        return StyleInfo(model_name=model_name, style_id=style_id)
