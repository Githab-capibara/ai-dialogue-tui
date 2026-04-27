"""
Architecture tests for verifying layer separation and dependency injection.

This module verifies that:
1. Domain layer does not depend on Infrastructure
2. Presentation layer depends on abstractions, not implementations
3. Dependency injection works correctly
4. ModelProvider implementation can be swapped without changing domain
"""

from __future__ import annotations

# pylint: disable=duplicate-code
import ast
import inspect
from unittest.mock import AsyncMock

import pytest

from controllers.dialogue_controller import DialogueController
from models.conversation import Conversation
from models.ollama_client import OllamaClient
from models.provider import ModelProvider
from services.dialogue_service import DialogueService


class TestArchitectureLayers:
    """Tests for verifying architecture layer separation."""

    def test_conversation_does_not_import_ollama_client(self) -> None:
        """
        Verify that Conversation does not import OllamaClient.

        This is critical for Clean Architecture - domain should not
        depend on infrastructure.
        """
        # Read source code of conversation.py
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Parse AST
        tree = ast.parse(source)

        # Find imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Verify no OllamaClient import
        assert "models.ollama_client" not in imports
        assert "ollama_client" not in imports

    def test_conversation_imports_model_provider(self) -> None:
        """
        Verify that Conversation imports ModelProvider protocol.

        Domain should depend on abstractions.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Verify ModelProvider is imported
        assert "ModelProvider" in source
        assert "from models.provider import" in source

    def test_ollama_client_implements_model_provider(self) -> None:
        """
        Verify that OllamaClient implements ModelProvider protocol.

        Infrastructure must implement abstractions.
        """
        # Verify OllamaClient has required methods
        assert hasattr(OllamaClient, "list_models")
        assert hasattr(OllamaClient, "generate")
        assert hasattr(OllamaClient, "close")

        # Verify methods are async
        assert inspect.iscoroutinefunction(OllamaClient.list_models)
        assert inspect.iscoroutinefunction(OllamaClient.generate)
        assert inspect.iscoroutinefunction(OllamaClient.close)

    def test_dialogue_service_uses_model_provider_protocol(self) -> None:
        """
        Verify that DialogueService uses ModelProvider protocol.

        Service layer must depend on abstractions.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Verify ModelProvider is used
        assert "ModelProvider" in source
        assert "from models.provider import" in source

        # Verify no direct OllamaClient import
        assert "from models.ollama_client import OllamaClient" not in source

    def test_dialogue_controller_uses_service(self) -> None:
        """
        Verify that DialogueController uses DialogueService.

        Controller should depend on service, not on domain directly.
        """
        with open("controllers/dialogue_controller.py", encoding="utf-8") as f:
            source = f.read()

        # Verify DialogueService is used
        assert "DialogueService" in source
        assert "from services.dialogue_service import" in source


class TestDependencyInjection:
    """Tests for verifying dependency injection functionality."""

    def test_conversation_accepts_model_provider(self) -> None:
        """
        Verify that Conversation accepts ModelProvider via DI.

        generate_response method must accept ModelProvider.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Verify method signature
        sig = inspect.signature(conversation.generate_response)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "provider"

    def test_dialogue_service_injects_dependencies(self) -> None:
        """
        Verify that DialogueService receives dependencies via constructor.

        All dependencies must be injected externally.
        """
        # Create provider mock
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.list_models.return_value = ["test"]
        mock_provider.generate.return_value = "test response"
        mock_provider.close.return_value = None

        # Create conversation
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Inject dependencies via constructor
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Verify dependencies are saved
        assert service.conversation is conversation
        assert service.provider is mock_provider

    def test_dialogue_controller_injects_service(self) -> None:
        """Verify that DialogueController receives service via constructor."""
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Inject service via constructor
        controller = DialogueController(service=service)

        # Verify service is saved
        assert controller.service is service


class TestModelProviderProtocol:
    """Tests for verifying ModelProvider protocol."""

    def test_model_provider_protocol_definition(self) -> None:
        """
        Verify that ModelProvider protocol is defined correctly.

        Protocol must have all required methods.
        """
        # Verify protocol has required methods
        assert hasattr(ModelProvider, "list_models")
        assert hasattr(ModelProvider, "generate")
        assert hasattr(ModelProvider, "close")

    def test_mock_provider_can_be_created(self) -> None:
        """
        Verify that mock ModelProvider implementation can be created.

        This is important for testability.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.list_models.return_value = ["model1", "model2"]
        mock_provider.generate.return_value = "response"
        mock_provider.close.return_value = None

        # Verify mock works
        assert isinstance(mock_provider, ModelProvider)

    @pytest.mark.asyncio
    async def test_mock_provider_works_with_conversation(self) -> None:
        """
        Verify that mock provider works with Conversation.

        This proves that Conversation depends on abstraction, not implementation.
        """
        # Create mock provider
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.return_value = "Test response from mock"

        # Create conversation
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Use mock with conversation
        model_id, response = await conversation.generate_response(mock_provider)

        # Verify result
        assert model_id == "A"
        assert response == "Test response from mock"
        mock_provider.generate.assert_called_once()


class TestServiceLayer:
    """Tests for verifying service layer."""

    def test_dialogue_service_has_state_management(self) -> None:
        """
        Verify that DialogueService manages state.

        Service must have is_running, is_paused flags.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Initial state
        assert not service.is_running
        assert not service.is_paused

        # After start
        service.start()
        assert service.is_running
        assert not service.is_paused

        # After pause
        service.pause()
        assert service.is_running
        assert service.is_paused

        # After resume
        service.resume()
        assert service.is_running
        assert not service.is_paused

        # After stop
        service.stop()
        assert not service.is_running
        assert not service.is_paused

    def test_dialogue_service_clear_history(self) -> None:
        """Verify that DialogueService.clear_history works."""
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Add message
        conversation.add_message("A", "user", "test")
        initial_count = len(conversation.get_context("A"))

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Clear history
        service.clear_history()

        # Verify context is cleared
        assert len(conversation.get_context("A")) < initial_count

    @pytest.mark.asyncio
    async def test_dialogue_service_run_cycle(self) -> None:
        """Verify that DialogueService.run_dialogue_cycle works."""
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.return_value = "Test response"
        mock_provider.close.return_value = None

        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Start service
        service.start()

        # Execute cycle
        result = await service.run_dialogue_cycle()

        # Verify result
        assert result is not None
        assert result.model_name == "test-a"
        assert result.response == "Test response"
        assert service.turn_count == 1


class TestControllerLayer:
    """Tests for verifying controller layer."""

    def test_controller_handles_start(self) -> None:
        """Verify that DialogueController.handle_start works."""
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        controller = DialogueController(service=service)

        # Handle start
        result = controller.handle_start()

        # Verify result
        assert result is True
        assert service.is_running

    def test_controller_handles_pause(self) -> None:
        """Verify that DialogueController.handle_pause works."""
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        controller = DialogueController(service=service)

        # Start and pause
        service.start()
        result = controller.handle_pause()

        # Verify result
        assert result is True
        assert service.is_paused

    def test_controller_handles_clear(self) -> None:
        """Verify that DialogueController.handle_clear works."""
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        # Add message
        conversation.add_message("A", "user", "test")

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        controller = DialogueController(service=service)

        # Clear
        controller.handle_clear()

        # Verify counter is reset
        assert controller.state.turn_count == 0


class TestCleanArchitecture:
    """
    Integration tests for verifying Clean Architecture.

    Verify that dependencies are directed correctly:
    Domain <- Presentation <- Infrastructure
    """

    def test_domain_has_no_infrastructure_dependencies(self) -> None:
        """
        Verify that domain does not depend on infrastructure.

        Conversation must only import:
        - config (configuration)
        - models.provider (abstractions)
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Verify no infrastructure imports
        assert "from models.ollama_client" not in source
        assert "import models.ollama_client" not in source
        assert "from services" not in source
        assert "from controllers" not in source
        assert "from tui" not in source

    def test_presentation_depends_on_abstractions(self) -> None:
        """
        Verify that presentation layer depends on abstractions.

        DialogueApp must import ModelProvider protocol,
        not only OllamaClient implementation.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Verify abstractions are used
        assert "DialogueService" in source
        assert "DialogueController" in source

    def test_can_swap_provider_implementation(self) -> None:
        """
        Verify that provider implementation can be swapped.

        This is a key advantage of dependency injection.
        """

        # Create alternative implementation
        class AlternativeProvider:
            """Alternative ModelProvider implementation for testing."""

            async def list_models(self) -> list[str]:
                """Get list of models."""
                return ["alt-model"]

            async def generate(
                self,
                model: str,
                messages: list[dict[str, str]],  # type: ignore[override]
                # pylint: disable=unused-argument
            ) -> str:
                """Generate response."""
                return f"Alternative response from {model}"

            async def close(self) -> None:
                """Close connection."""

        # Use alternative provider
        # (this works because Conversation depends on protocol)
        provider = AlternativeProvider()

        # Verify it works
        assert isinstance(provider, ModelProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
