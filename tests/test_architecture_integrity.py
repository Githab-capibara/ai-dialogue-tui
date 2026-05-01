"""Architecture integrity tests for AI Dialogue TUI.

This module verifies architectural principles and patterns:
- ProviderError exception hierarchy
- Config location in models module
- DialogueService error handling
- Separation of responsibilities between layers
- list_models caching
- Context limit
- Sanitizer protocol
- Modularity and dependencies
- SOLID principles
- Integration scenarios

Total: 42 tests
"""

# pylint: disable=import-outside-toplevel,reimported,duplicate-code
# pylint: disable=line-too-long,too-few-public-methods,missing-class-docstring
# pylint: disable=missing-function-docstring,unused-argument

from __future__ import annotations

import asyncio
import time
from typing import Protocol
from unittest.mock import AsyncMock

import pytest

from models.config import Config
from models.conversation import MAX_CONTEXT_LENGTH, Conversation
from models.ollama_client import _ModelsCache
from models.provider import (
    ModelProvider,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from services.dialogue_service import DialogueService
from tui.sanitizer import sanitize_response_for_display, sanitize_topic

# =============================================================================
# 1. ProviderError hierarchy tests
# =============================================================================


class TestProviderErrorHierarchy:
    """Tests for verifying ProviderError exception hierarchy."""

    def test_provider_error_base_class_exists(self) -> None:
        """
        Verify that base class ProviderError exists.

        ProviderError must be the base exception for all provider errors.
        """
        assert ProviderError is not None
        assert issubclass(ProviderError, Exception)

    def test_provider_configuration_error_exists(self) -> None:
        """
        Verify that ProviderConfigurationError exists.

        This exception is for provider configuration errors.
        """
        assert ProviderConfigurationError is not None
        assert issubclass(ProviderConfigurationError, ProviderError)

    def test_provider_connection_error_exists(self) -> None:
        """
        Verify that ProviderConnectionError exists.

        This exception is for provider connection errors.
        """
        assert ProviderConnectionError is not None
        assert issubclass(ProviderConnectionError, ProviderError)

    def test_provider_generation_error_exists(self) -> None:
        """
        Verify that ProviderGenerationError exists.

        This exception is for response generation errors.
        """
        assert ProviderGenerationError is not None
        assert issubclass(ProviderGenerationError, ProviderError)

    def test_all_errors_inherit_from_provider_error(self) -> None:
        """
        Verify that all provider exceptions inherit from ProviderError.

        This allows catching all provider errors via except ProviderError.
        """
        errors = [
            ProviderConfigurationError,
            ProviderConnectionError,
            ProviderGenerationError,
        ]

        for error_class in errors:
            assert issubclass(error_class, ProviderError)

    def test_provider_error_has_original_exception_property(self) -> None:
        """
        Verify that ProviderError preserves original exception.

        This is important for debugging and exception chain preservation.
        """
        original_error = ValueError("Original error")
        provider_error = ProviderError(
            "Provider error message",
            original_exception=original_error,
        )

        assert provider_error.original_exception is original_error
        assert str(provider_error) == "Provider error message"

        # Test without original exception
        provider_error_no_original = ProviderError("Another error")
        assert provider_error_no_original.original_exception is None


# =============================================================================
# 2. Config in models tests
# =============================================================================


class TestConfigLocation:
    """Tests for verifying Config location in models module."""

    def test_config_importable_from_models(self) -> None:
        """
        Verify that Config is importable from models module.

        Config must be accessible via models.config.
        """
        from models.config import Config as ConfigFromConfig

        assert ConfigFromConfig is not None
        assert ConfigFromConfig is Config

    def test_config_in_models_module(self) -> None:
        """
        Verify that Config is in models module.

        This is the correct location for a domain object.
        """
        # Check that models/config.py exists
        import os

        assert os.path.exists("models/config.py")

        # Check that Config is exported from models
        from models import config

        assert hasattr(config, "Config")
        assert config.Config is Config


# =============================================================================
# 3. DialogueService with ProviderError tests
# =============================================================================


class TestDialogueServiceErrors:
    """Tests for verifying error handling in DialogueService."""

    def _create_service_with_mock_provider(self, mock_provider: AsyncMock) -> DialogueService:
        """Create service with mock provider."""
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        return DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

    def test_service_uses_provider_error_not_ollama_error(self) -> None:
        """
        Verify that service uses ProviderError not OllamaError.

        Service must depend on abstractions, not concrete implementations.
        """
        # Check that dialogue_service.py uses ProviderError
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        assert "ProviderError" in source
        assert "from models.provider import" in source
        # Ensure no Ollama-specific error imports
        assert "OllamaError" not in source

    def test_service_handles_provider_configuration_error(self) -> None:
        """
        Verify that service correctly handles ProviderConfigurationError.

        Configuration error should propagate further.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderConfigurationError("Invalid configuration")

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Error should propagate
        with pytest.raises(ProviderConfigurationError):
            asyncio.run(service.run_dialogue_cycle())

    def test_service_handles_provider_connection_error(self) -> None:
        """
        Verify that service correctly handles ProviderConnectionError.

        Connection error should propagate further.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderConnectionError("Connection failed")

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Error should propagate
        with pytest.raises(ProviderConnectionError):
            asyncio.run(service.run_dialogue_cycle())

    def test_service_handles_provider_generation_error(self) -> None:
        """
        Verify that service correctly handles ProviderGenerationError.

        Generation error should propagate further.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderGenerationError("Generation failed")

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Error should propagate
        with pytest.raises(ProviderGenerationError):
            asyncio.run(service.run_dialogue_cycle())


# =============================================================================
# 4. Separation of concerns tests
# =============================================================================


class TestSeparationOfConcerns:
    """Tests for verifying separation of responsibilities between layers."""

    def test_ui_layer_does_not_contain_business_logic(self) -> None:
        """
        Verify that UI layer does not contain business logic.

        tui/app.py must contain only UI logic.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Check that business logic is extracted to service
        assert "DialogueService" in source
        assert "DialogueController" in source

        # Check that there is no direct business logic
        assert "async def run_dialogue_cycle" not in source
        assert "class DialogueService" not in source

    def test_service_layer_handles_dialogue_logic(self) -> None:
        """
        Verify that service layer contains dialogue logic.

        services/dialogue_service.py must contain business logic.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Check for business logic presence
        assert "run_dialogue_cycle" in source
        assert "start" in source
        assert "pause" in source
        assert "resume" in source
        assert "stop" in source
        assert "clear_history" in source

    def test_domain_layer_independent_of_infrastructure(self) -> None:
        """
        Verify that domain layer is independent of infrastructure.

        models/conversation.py must not import infrastructure modules.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Check for absence of infrastructure imports
        assert "from models.ollama_client" not in source
        assert "import models.ollama_client" not in source
        assert "from services" not in source
        assert "from controllers" not in source
        assert "from tui" not in source

        # Check that only abstractions are used
        assert "from models.provider import" in source
        assert "ModelProvider" in source


# =============================================================================
# 5. list_models caching tests
# =============================================================================


class TestModelsCaching:
    """Tests for verifying models list caching."""

    def test_list_models_uses_cache(self) -> None:
        """
        Verify that list_models uses caching.

        OllamaClient must cache list_models result.
        """
        # Check that _ModelsCache is used in OllamaClient
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "_ModelsCache" in source
        assert "_models_cache" in source
        assert "self._models_cache.get()" in source
        assert "self._models_cache.set(" in source

    def test_cache_has_ttl_300_seconds(self) -> None:
        """
        Verify that cache has TTL of 300 seconds.

        Cache lifetime must be 5 minutes.
        """
        # Check TTL constant
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "_MODELS_CACHE_TTL" in source
        assert "300" in source

        # Check constant value
        from models.ollama_client import _MODELS_CACHE_TTL

        assert _MODELS_CACHE_TTL == 300

    def test_cache_invalidates_after_ttl(self) -> None:
        """
        Verify that cache invalidates after TTL.

        Cache must become invalid after lifetime expiration.
        """
        cache = _ModelsCache(ttl=1)  # 1 second for test

        # Set cache
        cache.set(["model1", "model2"])
        assert cache.get() == ["model1", "model2"]

        # Wait for TTL expiration
        time.sleep(1.1)

        # Cache must be invalid
        assert cache.get() is None

    def test_cache_clears_on_error(self) -> None:
        """
        Verify that cache is cleared on error.

        On connection error, cache must be invalidated.
        """
        # Check that close() invalidates cache
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "self._models_cache.invalidate()" in source

        # Test cache behavior
        cache = _ModelsCache()
        cache.set(["model1"])
        assert cache.get() == ["model1"]

        cache.invalidate()
        assert cache.get() is None


# =============================================================================
# 6. Context limit tests
# =============================================================================


class TestContextLengthLimit:
    """Tests for verifying context length limit."""

    def test_max_context_length_constant_exists(self) -> None:
        """
        Verify that MAX_CONTEXT_LENGTH constant exists.

        Constant must be defined in models/conversation.py.
        """
        assert MAX_CONTEXT_LENGTH is not None
        assert isinstance(MAX_CONTEXT_LENGTH, int)

    def test_context_trims_when_exceeds_limit(self) -> None:
        """
        Verify that context is trimmed when limit is exceeded.

        When adding a message that exceeds the limit, context must be trimmed.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Add more messages than the limit
        for i in range(MAX_CONTEXT_LENGTH + 10):
            conversation.add_message("A", "user", f"Message {i}")

        # Context must be trimmed
        context = conversation.get_context("A")
        assert len(context) <= MAX_CONTEXT_LENGTH

        # System prompt must be preserved
        assert context[0]["role"] == "system"

    def test_context_does_not_trim_when_under_limit(self) -> None:
        """
        Verify that context is not trimmed when under limit.

        With normal message count, trimming is not needed.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Add fewer messages than the limit
        initial_count = len(conversation.get_context("A"))
        for i in range(5):
            conversation.add_message("A", "user", f"Message {i}")

        # Context must grow but not be trimmed
        context = conversation.get_context("A")
        assert len(context) == initial_count + 5

    def test_max_context_length_is_128(self) -> None:
        """
        Verify that MAX_CONTEXT_LENGTH equals 128.

        This value was increased from 50 to 128 for longer dialogues.
        """
        assert MAX_CONTEXT_LENGTH == 128


# =============================================================================
# 7. Sanitizer protocol tests
# =============================================================================


class TestSanitizerProtocol:
    """Tests for verifying sanitization functions."""

    def test_sanitize_topic_implements_protocol(self) -> None:
        """Verify that sanitize_topic has correct signature."""
        import inspect

        sig = inspect.signature(sanitize_topic)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "topic"

        # Check that function works
        result = sanitize_topic("test topic")
        assert isinstance(result, str)

    def test_sanitize_response_implements_protocol(self) -> None:
        """Verify that sanitize_response_for_display has correct signature."""
        import inspect

        sig = inspect.signature(sanitize_response_for_display)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "response"

        # Check that function works
        result = sanitize_response_for_display("test response")
        assert isinstance(result, str)


# =============================================================================
# 8. Modularity and dependencies tests
# =============================================================================


class TestModularity:
    """Tests for verifying modularity and dependencies."""

    def test_no_circular_dependencies(self) -> None:
        """
        Verify absence of circular dependencies.

        Modules must not import each other cyclically.
        """
        # Check main modules
        modules_to_check = [
            ("models/conversation.py", ["services", "controllers", "tui"]),
            ("services/dialogue_service.py", ["controllers", "tui"]),
            ("controllers/dialogue_controller.py", ["tui"]),
        ]

        for module_path, forbidden_imports in modules_to_check:
            with open(module_path, encoding="utf-8") as f:
                source = f.read()

            for forbidden in forbidden_imports:
                # Check that there are no imports of forbidden modules
                assert f"from {forbidden}" not in source
                assert f"import {forbidden}" not in source

    def test_domain_layer_has_no_infrastructure_imports(self) -> None:
        """
        Verify that domain layer does not import infrastructure.

        models/ must not import tui/ or infrastructure.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source
        assert "from models.ollama_client" not in source

    def test_service_layer_depends_on_domain_only(self) -> None:
        """
        Verify that service layer depends only on domain.

        services/ must import only models/.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Check that domain is imported
        assert "from models" in source
        assert "from models.config import Config" in source
        assert "from models.conversation import" in source
        assert "from models.provider import" in source

        # Check that there are no presentation imports
        assert "from tui" not in source
        assert "import tui" not in source

    def test_presentation_layer_depends_on_abstractions(self) -> None:
        """
        Verify that presentation layer depends on abstractions.

        tui/ must use protocols and services, not implementations.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Check that abstractions are used
        assert "from models.provider import" in source
        assert "ProviderError" in source

        # Check that service layer is used
        assert "from services.dialogue_service import" in source
        assert "DialogueService" in source


# =============================================================================
# 9. SOLID principles tests
# =============================================================================


class TestSOLIDPrinciples:
    """Tests for verifying SOLID principles."""

    def test_single_responsibility_dialogue_service(self) -> None:
        """
        Verify Single Responsibility Principle for DialogueService.

        Service must be responsible only for dialogue business logic.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Check that service contains only business logic
        assert "class DialogueService" in source

        # Check business logic methods
        assert "def run_dialogue_cycle" in source
        assert "def start" in source
        assert "def pause" in source
        assert "def resume" in source
        assert "def stop" in source
        assert "def clear_history" in source

        # Check that there is no UI logic
        assert "yield " not in source  # No Textual widgets
        assert "query_one" not in source

    def test_open_closed_provider_protocol(self) -> None:
        """
        Verify Open/Closed Principle for ModelProvider.

        Protocol must be open for extension, closed for modification.
        """
        # Check that ModelProvider is a Protocol
        assert issubclass(type(ModelProvider), type(Protocol))

        # Check that protocol defines interface
        assert hasattr(ModelProvider, "list_models")
        assert hasattr(ModelProvider, "generate")
        assert hasattr(ModelProvider, "close")

        # Check that new implementation can be created
        class NewProvider:  # pylint: disable=missing-class-docstring
            """New provider implementation for testing."""

            async def list_models(self) -> list[str]:
                """List of models."""
                return ["new-model"]

            async def generate(  # pylint: disable=unused-argument
                self,
                model: str,
                messages: list[dict[str, str]],  # type: ignore[override]
            ) -> str:
                """Generate response."""
                return "response"

            async def close(self) -> None:
                """Close provider."""

        # New implementation is compatible with protocol
        provider = NewProvider()
        assert isinstance(provider, ModelProvider)

    def test_dependency_inversion_service_uses_protocol(self) -> None:
        """
        Verify Dependency Inversion Principle.

        Service must depend on abstractions (protocols), not implementations.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Check that protocol is used
        assert "ModelProvider" in source
        assert "from models.provider import" in source

        # Check that there is no concrete implementation dependency
        assert "from models.ollama_client import OllamaClient" not in source
        assert "OllamaClient" not in source

    def test_liskov_substitution_provider_errors(self) -> None:
        """
        Verify Liskov Substitution Principle for errors.

        ProviderError subclasses must be replaceable with base class.
        """
        # Create instances of all error types
        errors = [
            ProviderError("base error"),
            ProviderConfigurationError("config error"),
            ProviderConnectionError("connection error"),
            ProviderGenerationError("generation error"),
        ]

        # All errors must be replaceable with base class
        for error in errors:
            assert isinstance(error, ProviderError)

            # All errors must have original_exception
            assert hasattr(error, "original_exception")

        # Check that all errors can be caught via base class
        def raise_error(error: Exception) -> None:
            raise error

        for error in errors:
            with pytest.raises(ProviderError):
                raise_error(error)


# =============================================================================
# 10. Integration tests
# =============================================================================


class TestArchitectureIntegration:
    """Integration tests for verifying architecture integrity."""

    def test_full_dialogue_flow_with_new_errors(self) -> None:
        """
        Integration test of full dialogue flow with new errors.

        Verifies that ProviderError correctly propagates through all layers.
        """
        # Create mock provider with error
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderGenerationError("Test generation error")
        mock_provider.list_models.return_value = ["test-model"]
        mock_provider.close.return_value = None

        # Create conversation and service
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        service.start()

        # Error must propagate through service
        with pytest.raises(ProviderGenerationError) as exc_info:
            asyncio.run(service.run_dialogue_cycle())

        # Check that error is of correct type
        assert exc_info.value is mock_provider.generate.side_effect

    def test_config_validation_in_domain_layer(self) -> None:
        """
        Integration test of configuration validation in domain layer.

        Verifies that Config is validated on creation.
        """
        # Check that Config in models has validation
        from models.config import Config as ModelsConfig

        # Valid configuration
        config = ModelsConfig()
        assert config.temperature == 0.7
        assert config.max_tokens == -1  # Unlimited

        # Invalid temperature
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(temperature=1.5)
        assert "temperature" in str(exc_info.value).lower()

        # Invalid max_tokens
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(max_tokens=-2)
        assert "max_tokens" in str(exc_info.value).lower()

        # Invalid URL
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(ollama_host="invalid-url")
        assert "url" in str(exc_info.value).lower() or "ollama" in str(exc_info.value).lower()

    def test_provider_error_propagation_to_ui(self) -> None:
        """
        Integration test of provider error propagation to UI.

        Verifies that ProviderError is correctly handled in UI layer.
        """
        # Check that tui/app.py handles ProviderError
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Check that ProviderError is imported
        assert "ProviderError" in source
        assert "from models.provider import" in source

        # Check that error is handled (with or without "as e")
        assert "ProviderError" in source and "except" in source

        # Check that error handling exists in on_mount
        assert "ProviderError" in source

        # Check that error handling with log.exception exists in _run_dialogue
        # Ищем комбинацию ProviderError и log.exception в одном контексте
        lines = source.split("\n")
        in_run_dialogue = False
        found_exception_logging = False

        for i, line in enumerate(lines):
            if "async def _run_dialogue" in line:
                in_run_dialogue = True
            # Ищем except ProviderError с log.exception рядом
            if in_run_dialogue:
                if "except ProviderError" in line:
                    # Проверяем строки после except (расширили диапазон для service None check)
                    for j in range(i, min(i + 10, len(lines))):
                        if "log.exception" in lines[j] and "ProviderError" not in lines[j]:
                            found_exception_logging = True
                            break
                    if found_exception_logging:
                        break

        assert found_exception_logging


# =============================================================================
# Additional tests for complete coverage
# =============================================================================


class TestProviderErrorDetails:
    """Additional tests for ProviderError."""

    def test_provider_error_message_preserved(self) -> None:
        """Verify that error message is preserved."""
        error = ProviderError("Test message")
        assert str(error) == "Test message"

    def test_provider_error_chain_preserved(self) -> None:
        """Verify that exception chain is preserved."""
        original = ValueError("Original")
        error = ProviderError("Wrapper", original_exception=original)

        assert error.__cause__ is original or error.original_exception is original

    def test_provider_error_subclasses_have_specific_names(self) -> None:
        """Verify that subclasses have specific names."""
        assert ProviderConfigurationError.__name__ == "ProviderConfigurationError"
        assert ProviderConnectionError.__name__ == "ProviderConnectionError"
        assert ProviderGenerationError.__name__ == "ProviderGenerationError"


class TestConfigImmutability:
    """Tests for verifying Config immutability."""

    def test_config_is_mutable(self) -> None:
        """Verify that Config is mutable (not frozen)."""
        config = Config()

        # Config should be mutable for runtime reconfiguration
        config.temperature = 0.9
        assert config.temperature == 0.9

    def test_config_has_slots(self) -> None:
        """Verify that Config uses slots."""
        # Check that __slots__ is defined
        assert hasattr(Config, "__slots__")


class TestConversationContextIsolation:
    """Tests for verifying context isolation."""

    def test_contexts_are_independent(self) -> None:
        """Verify that model contexts are independent."""
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Add message only to context A
        conversation.add_message("A", "user", "Message for A")

        # Get contexts
        context_a = conversation.get_context("A")
        context_b = conversation.get_context("B")

        # Context A must contain message
        assert any(msg["content"] == "Message for A" for msg in context_a)

        # Context B must not contain this message
        assert not any(msg["content"] == "Message for A" for msg in context_b)

    def test_get_context_returns_copy(self) -> None:
        """Verify that get_context returns a copy."""
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        context = conversation.get_context("A")
        original_len = len(context)

        # Check that tuple (immutable) is returned
        assert isinstance(context, tuple)

        # Try to modify returned context - must raise error
        try:
            # type: ignore[attr-defined] - tuple не имеет append, это ожидаемо
            context.append({"role": "user", "content": "Injected"})  # type: ignore[attr-defined]
            assert False, "AttributeError expected for tuple"
        except AttributeError:
            pass  # Expected behavior

        # Original context must not be modified
        assert len(conversation.get_context("A")) == original_len


class TestSanitizerSecurity:
    """Security tests for Sanitizer."""

    def test_sanitize_topic_prevents_injection(self) -> None:
        """Verify that sanitize_topic prevents injections."""
        # Attempt injection via curly braces
        malicious = "{__import__('os').system('rm -rf /')}"
        result = sanitize_topic(malicious)

        assert "{{" in result
        assert "__import__" not in result or "{{" in result

    def test_sanitize_response_prevents_xss(self) -> None:
        """Verify that sanitize_response prevents XSS."""
        malicious = "<script>alert('XSS')</script>"
        result = sanitize_response_for_display(malicious)

        assert "<script>" not in result
        assert "&lt;" in result


class TestModelsCacheEdgeCases:
    """Edge case tests for models cache."""

    def test_cache_with_empty_list(self) -> None:
        """Verify caching of empty list."""
        cache = _ModelsCache()
        cache.set([])

        result = cache.get()
        assert result == []

    def test_cache_with_none_value(self) -> None:
        """Verify that None is not cached as valid value."""
        cache = _ModelsCache()
        # Don't set value

        result = cache.get()
        assert result is None

    def test_cache_ttl_zero(self) -> None:
        """Verify cache with TTL=0."""
        cache = _ModelsCache(ttl=0)
        cache.set(["model1"])

        # Cache must be immediately invalid
        result = cache.get()
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
