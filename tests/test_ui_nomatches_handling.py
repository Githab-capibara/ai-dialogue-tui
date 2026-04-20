"""Tests for handling UI element unavailability with active modal dialogs."""

# pylint: disable=protected-access,import-outside-toplevel

from __future__ import annotations

import pytest
from textual.css.query import NoMatches
from textual.widgets import Label

from controllers.dialogue_controller import UIState
from models.config import Config
from tui.app import DialogueApp


class TestUINoMatchesHandling:
    """Tests for preventing NoMatches errors when working with modal dialogs."""

    def test_on_ui_state_changed_no_matches_logged_as_debug(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test verifies that NoMatches exception is logged at DEBUG level.

        Scenario: #status-value element unavailable (modal dialog active),
        error should be handled without ERROR logging.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Test", status_style="green")

        # Call method when UI is not yet mounted
        with caplog.at_level("DEBUG"):
            app._on_ui_state_changed(test_state)

        # Verify DEBUG message was recorded
        assert "Element #status-value unavailable for update" in caplog.text
        # Verify ERROR was not logged
        assert "Error updating UI state" not in caplog.text

    def test_on_ui_state_changed_runtime_error_logged_as_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test verifies that RuntimeError is logged at ERROR level.

        Scenario: unexpected error during UI update should be
        logged as ERROR with full traceback.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Test", status_style="green")

        # Mock query_one to raise RuntimeError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise RuntimeError("Test runtime error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("ERROR"):
            app._on_ui_state_changed(test_state)

        # Verify ERROR was recorded
        assert "RuntimeError updating UI state" in caplog.text

    def test_on_ui_state_changed_lookup_error_logged_as_error(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test verifies that LookupError is logged at ERROR level.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Test", status_style="green")

        # Mock query_one to raise LookupError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise LookupError("Test lookup error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("ERROR"):
            app._on_ui_state_changed(test_state)

        # Verify ERROR was recorded
        assert "LookupError updating UI state" in caplog.text

    def test_on_ui_state_changed_screen_stack_error_logged_as_debug(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test verifies that ScreenStackError is logged at DEBUG level.
        """
        from textual.app import ScreenStackError

        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Test", status_style="green")

        # Mock query_one to raise ScreenStackError
        def mock_query_one(selector: str, widget_type: type) -> Label:
            if selector == "#status-value" and widget_type == Label:
                raise ScreenStackError("Test screen stack error")
            raise NoMatches(f"No nodes match {selector!r}")

        app.query_one = mock_query_one  # type: ignore[method-assign]

        with caplog.at_level("DEBUG"):
            app._on_ui_state_changed(test_state)

        # Verify DEBUG was recorded
        assert "Element #status-value unavailable for update" in caplog.text

    def test_on_ui_state_changed_no_matches_does_not_reraise(self) -> None:
        """
        Test verifies that NoMatches does not cause re-raise.

        Method should handle exception and continue without errors.
        """
        config = Config()
        app = DialogueApp(config=config)
        test_state = UIState(status_text="Test", status_style="green")

        # This should not raise exception
        app._on_ui_state_changed(test_state)

        # If code reached here - test passed
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
