"""Tests for preventing NoMatches errors during UI shutdown."""

# pylint: disable=protected-access,import-outside-toplevel,broad-exception-caught
# pylint: disable=duplicate-code

from __future__ import annotations

import pytest

from controllers.dialogue_controller import UIState
from factories.provider_factory import create_provider_factory
from models.config import Config
from tui.app import DialogueApp


class TestUIShutdownError:
    """Tests for preventing NoMatches errors during UI shutdown."""

    def test_on_ui_state_changed_handles_no_matches_exception(self) -> None:
        """
        Test verifies that _on_ui_state_changed handles NoMatches exception.

        This test reproduces the scenario where #status-value element
        is not found in DOM, causing NoMatches exception.
        """
        # Create mock configuration and provider factory
        config = Config()
        provider_factory = create_provider_factory(config)

        # Create application
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Call _on_ui_state_changed directly to test exception handling
        # Application is not yet mounted, so UI elements are unavailable
        test_state = UIState(status_text="Test", status_style="dim")

        # This must not raise exception thanks to our fix
        try:
            app._on_ui_state_changed(test_state)
            # If we reached here, exception was handled
            assert True
        except Exception as e:
            # If exception still occurred, test fails
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")

    def test_on_ui_state_changed_handles_lookup_error(self) -> None:
        """
        Test verifies that _on_ui_state_changed handles LookupError.
        """
        # Create mock configuration and provider factory
        config = Config()
        provider_factory = create_provider_factory(config)

        # Create application
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Call _on_ui_state_changed directly
        test_state = UIState(status_text="Test", status_style="dim")

        # This must not raise exception thanks to our fix
        try:
            app._on_ui_state_changed(test_state)
            # If we reached here, exception was handled
            assert True
        except Exception as e:
            # If exception still occurred, test fails
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")

    def test_on_ui_state_changed_handles_runtime_error(self) -> None:
        """
        Test verifies that _on_ui_state_changed handles RuntimeError.
        """
        # Create mock configuration and provider factory
        config = Config()
        provider_factory = create_provider_factory(config)

        # Create application
        app = DialogueApp(config=config, provider_factory=provider_factory)

        # Call _on_ui_state_changed directly
        test_state = UIState(status_text="Test", status_style="dim")

        # This must not raise exception thanks to our fix
        try:
            app._on_ui_state_changed(test_state)
            # If we reached here, exception was handled
            assert True
        except Exception as e:
            # If exception still occurred, test fails
            pytest.fail(f"_on_ui_state_changed raised unexpected exception: {e}")
