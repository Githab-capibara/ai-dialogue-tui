"""CSS generation for TUI application.

This module contains functions for generating CSS from constants
and defining display styles and visual themes for the AI Dialogue TUI.
"""

from __future__ import annotations

from tui.constants import CSS_CLASSES, UI_IDS


def generate_main_css() -> str:
    """Generate main CSS from centralized constants.

    Returns:
        CSS string for application.

    """
    return f"""
#{UI_IDS.model_selection_container} {{
    align: center top;
    padding: 3 1;
    background: $surface;
}}

#{UI_IDS.selection_title} {{
    text-align: center;
    text-style: bold;
    padding: 1 2;
    margin-bottom: 2;
}}

#{UI_IDS.selection_buttons} {{
    height: auto;
    align: center middle;
    margin-top: 2;
}}

#{UI_IDS.models_row} {{
    height: auto;
    width: 100%;
    align: center top;
}}

#{UI_IDS.model_a_container}, #{UI_IDS.model_b_container} {{
    width: 100%;
    height: 3;
    margin: 1 0;
    align: left middle;
}}

#{UI_IDS.model_a_label}, #{UI_IDS.model_b_label} {{
    width: 15;
    margin: 0 1;
}}

#{UI_IDS.model_a_select}, #{UI_IDS.model_b_select} {{
    width: 1fr;
}}

#{UI_IDS.selection_buttons} Button {{
    margin: 0 1;
}}

#{UI_IDS.topic_input_container} {{
    align: center middle;
    width: 100%;
    height: 100%;
    background: $surface;
}}

#{UI_IDS.topic_input_content} {{
    align: center middle;
    width: 80%;
    height: auto;
    min-height: 10;
}}

#{UI_IDS.topic_label} {{
    text-align: center;
    text-style: bold;
    padding: 1 2;
    margin-bottom: 1;
}}

#{UI_IDS.topic_input} {{
    width: 60;
    margin-bottom: 2;
}}

#{UI_IDS.topic_buttons} {{
    height: auto;
    align: center middle;
}}

#{UI_IDS.topic_buttons} Button {{
    margin: 0 1;
}}

#{UI_IDS.main_container} {{
    height: 100%;
}}

#{UI_IDS.status_bar} {{
    height: 3;
    background: $surface;
    border: solid $primary;
    margin: 1;
    padding: 0 2;
}}

#{UI_IDS.status_row} {{
    height: 100%;
    align: left middle;
}}

#{UI_IDS.status_label} {{
    width: auto;
    padding: 0 1;
}}

#{UI_IDS.dialogue_log} {{
    height: 1fr;
    margin: 0 1;
    border: solid $secondary;
}}

#{UI_IDS.controls_bar} {{
    height: 4;
    background: $surface;
    border: solid $primary;
    margin: 1;
    padding: 0 2;
}}

#{UI_IDS.controls_row} {{
    height: 100%;
    align: center middle;
}}

#{UI_IDS.controls_row} Button {{
    margin: 0 1;
    width: 16;
}}

.{CSS_CLASSES.model_a_message} {{
    color: $success;
    text-style: bold;
}}

.{CSS_CLASSES.model_b_message} {{
    color: $accent;
    text-style: bold;
}}

.{CSS_CLASSES.system_message} {{
    color: $warning;
    text-style: italic;
}}

.{CSS_CLASSES.error_message} {{
    color: $error;
    text-style: bold;
}}
"""


__all__ = [
    "generate_main_css",
]
