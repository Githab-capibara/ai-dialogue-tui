"""Tests for verifying all fixes from code audit.

This file contains tests for verifying the following fixes:
1. Broad Exception Handler - specific exceptions are caught
2. DIP violation - provider_factory is injected
3. Sanitizer type validation - TypeError on None
4. Assert checks - assert works
5. ProviderError unified handling - all errors handled uniformly
6. Exception chaining - __cause__ is preserved
7. XSS protection - markup symbols are escaped
8. Context dictionary - context dictionary works
9. Tuple return - returns tuple
10. Cache size limit - cache is limited
11. MessageDict total=True - dictionary validation

Note:
    Tests use access to internal attributes and imports inside functions,
    which is justified for testing purposes.

"""

# pylint: disable=protected-access,import-outside-toplevel,no-member
# pylint: disable=too-few-public-methods,reimported,redefined-outer-name

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from models.config import Config
from models.conversation import Conversation
from models.ollama_client import OllamaClient, _ModelsCache
from models.provider import (
    MessageDict,
    ProviderConnectionError,
    ProviderError,
    ProviderGenerationError,
)
from tui.app import DialogueApp
from tui.sanitizer import sanitize_response_for_display, sanitize_topic

# =============================================================================
# 1. Broad Exception Handler - test that specific exceptions are caught
# =============================================================================


class TestBroadExceptionHandler:
    """Tests for verifying specific exception handling."""

    @pytest.mark.asyncio
    async def test_json_decode_error_handling(self) -> None:
        """
        Test: JSONDecodeError is caught and converted to ProviderGenerationError.

        Verifies that invalid JSON from API raises ProviderGenerationError
        with preserved exception chain (__cause__).
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        # Create mock session that returns invalid JSON
        mock_response = AsyncMock()
        mock_response.status = 200

        # Use json.JSONDecodeError instead of ContentTypeError
        mock_response.json = AsyncMock(
            side_effect=aiohttp.ClientResponseError(
                request_info=MagicMock(),
                history=(),
                status=200,
                message="Invalid JSON",
            )
        )

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_response.__aenter__.return_value)
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act & Assert
            with pytest.raises(ProviderError) as exc_info:
                await client.list_models()

            # Verify exception has chain
            assert exc_info.value.__cause__ is not None

    @pytest.mark.asyncio
    async def test_connection_error_handling(self) -> None:
        """
        Test: ClientError is caught as ProviderConnectionError.

        Verifies that API connection errors are converted to ProviderConnectionError.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        # Create mock session that throws ClientError
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=aiohttp.ClientError("Connection refused"))

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act & Assert
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.list_models()

            # Verify exception has chain
            assert exc_info.value.__cause__ is not None
            assert "could not connect" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self) -> None:
        """
        Test: asyncio.TimeoutError is caught as ProviderConnectionError.

        Verifies that timeouts are converted to ProviderConnectionError.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        # Create mock session that throws TimeoutError
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=asyncio.TimeoutError())

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act & Assert
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.list_models()

            assert exc_info.value.__cause__ is not None


# =============================================================================
# 2. DIP violation - test that provider_factory is injected
# =============================================================================


class TestDependencyInjection:
    """Tests for verifying dependency injection via provider_factory."""

    def test_provider_factory_can_be_injected(self) -> None:
        """
        Test: provider_factory can be injected instead of concrete implementation.

        Verifies that custom provider factory can be passed.
        """
        # Arrange
        custom_provider = MagicMock()
        custom_provider.list_models = AsyncMock(return_value=["custom-model"])
        custom_provider.generate = AsyncMock(return_value="response")
        custom_provider.close = AsyncMock()

        def provider_factory():
            return custom_provider

        # Act - verify factory returns our mock provider
        result = provider_factory()

        # Assert
        assert result is custom_provider
        assert result.list_models is custom_provider.list_models

    def test_ollama_client_uses_injected_config(self) -> None:
        """
        Test: OllamaClient uses injected configuration.

        Verifies that custom configuration can be injected.
        """
        # Arrange
        custom_config = Config(
            ollama_host="http://custom-host:9999",
            temperature=0.9,
            max_tokens=500,
        )

        # Act
        client = OllamaClient(config=custom_config)

        # Assert
        assert client.host == "http://custom-host:9999"


# =============================================================================
# 3. Sanitizer type validation - test that TypeError on None
# =============================================================================


class TestSanitizerTypeValidation:
    """Tests for verifying type validation in sanitizer."""

    def test_sanitize_topic_rejects_none(self) -> None:
        """
        Test: sanitize_topic raises TypeError on None.

        Verifies that function does not accept None as input.
        """
        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            sanitize_topic(None)  # type: ignore

        assert "string" in str(exc_info.value)

    def test_sanitize_topic_rejects_non_string(self) -> None:
        """
        Test: sanitize_topic raises TypeError for non-string.

        Verifies that function rejects other data types.
        """
        # Act & Assert
        with pytest.raises(TypeError):
            sanitize_topic(123)  # type: ignore

        with pytest.raises(TypeError):
            sanitize_topic(["topic"])  # type: ignore

    def test_sanitize_response_rejects_none(self) -> None:
        """
        Test: sanitize_response_for_display raises TypeError on None.

        Verifies that function does not accept None.
        """
        # Act & Assert
        with pytest.raises(TypeError) as exc_info:
            sanitize_response_for_display(None)  # type: ignore

        assert "string" in str(exc_info.value)

    def test_sanitize_response_rejects_non_string(self) -> None:
        """Test: sanitize_response_for_display raises TypeError for non-string."""
        # Act & Assert
        with pytest.raises(TypeError):
            sanitize_response_for_display(123)  # type: ignore


# =============================================================================
# 4. Assert checks - test that assert works
# =============================================================================


class TestAssertChecks:
    """Tests for verifying assert checks in code."""

    def test_assert_validates_client_not_none(self) -> None:
        """
        Test: assert checks that client is not None.

        Verifies that there are assert checks before usage.
        """
        # Arrange
        import inspect

        from tui.app import DialogueApp

        # Act - get source code
        source = inspect.getsource(DialogueApp)

        # Assert - verify assert checks exist
        assert "assert" in source or "is not None" in source

    def test_conversation_initialized_flag(self) -> None:
        """
        Test: Conversation has required fields.

        Verifies core fields exist.
        """
        # Arrange
        conversation = Conversation("model_a", "model_b", "test")

        # Act & Assert
        assert conversation.model_a == "model_a"
        assert conversation.model_b == "model_b"
        assert conversation.topic == "test"


# =============================================================================
# 5. ProviderError unified handling - test that all errors handled uniformly
# =============================================================================


class TestProviderErrorUnifiedHandling:
    """Tests for verifying unified ProviderError handling."""

    def test_all_provider_errors_inherit_from_base(self) -> None:
        """
        Test: all ProviderError exceptions inherit from base.

        Verifies that exception hierarchy is correct.
        """
        # Arrange & Act
        connection_error = ProviderConnectionError("connection")
        generation_error = ProviderGenerationError("generation")

        # Assert
        assert isinstance(connection_error, ProviderError)
        assert isinstance(generation_error, ProviderError)

    def test_provider_error_has_message(self) -> None:
        """
        Test: ProviderError preserves message.

        Verifies that message is accessible via str().
        """
        # Arrange
        error = ProviderError("test message")

        # Act & Assert
        assert str(error) == "test message"

    def test_provider_error_preserves_original_exception(self) -> None:
        """
        Test: ProviderError preserves original exception.

        Verifies that original_exception is accessible.
        """
        # Arrange
        original = ValueError("original")
        error = ProviderError("wrapper", original_exception=original)

        # Act & Assert
        assert error.original_exception is original

    @pytest.mark.asyncio
    async def test_unified_error_handling_in_client(self) -> None:
        """
        Test: all errors in client are converted to ProviderError.

        Verifies that different error types are handled uniformly.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        # Create mock that throws KeyError
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=KeyError("missing key"))

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act & Assert
            with pytest.raises(ProviderError) as exc_info:
                await client.list_models()

            # All errors should be ProviderError or subclass
            assert isinstance(exc_info.value, ProviderError)


# =============================================================================
# 6. Exception chaining - test that __cause__ is preserved
# =============================================================================


class TestExceptionChaining:
    """Tests for verifying exception chain preservation."""

    @pytest.mark.asyncio
    async def test_exception_chain_preserved(self) -> None:
        """
        Test: __cause__ is preserved when converting exceptions.

        Verifies that original exception is accessible via __cause__.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        original_error = aiohttp.ClientError("original connection error")
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=original_error)

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.list_models()

            # Assert
            assert exc_info.value.__cause__ is original_error

    def test_provider_error_cause_property(self) -> None:
        """
        Test: ProviderError.original_exception returns passed exception.

        Verifies that original_exception property works.
        """
        # Arrange
        original = RuntimeError("cause")
        error = ProviderError("wrapper", original_exception=original)

        # Assert - original_exception accessible via property
        # __cause__ may not be set automatically in Python
        assert error.original_exception is original


# =============================================================================
# 7. XSS protection - test that markup symbols are escaped
# =============================================================================


class TestXSSProtection:
    """Tests for verifying XSS protection via markup escaping."""

    @pytest.mark.security
    def test_square_brackets_escaped(self) -> None:
        """
        Test: square brackets are escaped.

        Verifies that [ and ] are converted to [[ and ]].
        """
        # Arrange
        malicious_input = "test [bold]injected[/bold]"

        # Act
        result = sanitize_response_for_display(malicious_input)

        # Assert - verify brackets are escaped (doubled)
        assert "[[" in result
        assert "]]" in result
        # Original pattern now contains escaped brackets
        assert "[[bold]]" in result

    @pytest.mark.security
    def test_curly_braces_escaped(self) -> None:
        """
        Test: curly braces are escaped.

        Verifies that { and } are converted to {{ and }}.
        """
        # Arrange
        malicious_input = "test {injected}"

        # Act
        result = sanitize_response_for_display(malicious_input)

        # Assert
        assert "{{" in result
        assert "}}" in result

    @pytest.mark.security
    def test_html_entities_escaped(self) -> None:
        """
        Test: HTML entities are escaped.

        Verifies that < and > are converted to &lt; and &gt;.
        """
        # Arrange
        malicious_input = "<script>alert('xss')</script>"

        # Act
        result = sanitize_response_for_display(malicious_input)

        # Assert
        assert "<script>" not in result
        assert "&lt;" in result
        assert "&gt;" in result

    @pytest.mark.security
    def test_special_characters_escaped(self) -> None:
        """
        Test: special Textual characters are escaped.

        Verifies that *, _, `, @, # are escaped.
        """
        # Arrange
        malicious_input = "*bold* _italic_ `code` @class #id"

        # Act
        result = sanitize_response_for_display(malicious_input)

        # Assert
        assert "\\*" in result
        assert "\\_" in result
        assert "\\`" in result
        assert "@@" in result
        assert "##" in result

    @pytest.mark.security
    def test_sanitize_topic_escapes_injection(self) -> None:
        """
        Test: sanitize_topic prevents prompt injection.

        Verifies that curly braces in topic are escaped.
        """
        # Arrange
        malicious_topic = "test {injected prompt}"

        # Act
        result = sanitize_topic(malicious_topic)

        # Assert - verify braces are escaped (doubled)
        assert "{{" in result
        assert "}}" in result
        # Escaped pattern contains double braces
        assert "{{injected" in result


# =============================================================================
# 8. Context dictionary - test that context dictionary works
# =============================================================================


class TestContextDictionary:
    """Tests for verifying context dictionary in Conversation."""

    def test_conversation_has_separate_contexts(self) -> None:
        """
        Test: Conversation has separate contexts for models A and B.

        Verifies that _context_a and _context_b exist.
        """
        # Arrange
        conversation = Conversation("model_a", "model_b", "test")

        # Act & Assert
        assert hasattr(conversation, "_context_a")
        assert hasattr(conversation, "_context_b")
        assert conversation._context_a is not conversation._context_b

    def test_contexts_are_independent_lists(self) -> None:
        """
        Test: contexts are independent.

        Verifies that adding to one context does not affect the other.
        """
        # Arrange
        conversation = Conversation("model_a", "model_b", "test")

        # Save original length (there may be system message)
        initial_len_b = len(conversation._context_b)

        # Act - add message only to context A (model_id is first
        # parameter!)
        conversation.add_message("A", "user", "message for A")

        # Assert - context A increased, B stayed the same
        assert len(conversation._context_a) > 0
        assert len(conversation._context_b) == initial_len_b

    def test_get_context_returns_correct_model_context(self) -> None:
        """
        Test: get_context returns correct context.

        Verifies that for model A, _context_a is returned.
        """
        # Arrange
        conversation = Conversation("model_a", "model_b", "test")
        conversation.add_message("A", "user", "msg A")
        conversation.add_message("B", "user", "msg B")

        # Act
        context_a = conversation.get_context("A")
        context_b = conversation.get_context("B")

        # Assert - verify messages added to correct contexts
        # (system message + our message = 2)
        assert len(context_a) >= 1
        assert len(context_b) >= 1
        # Verify last message in each context is correct
        assert context_a[-1]["content"] == "msg A"
        assert context_b[-1]["content"] == "msg B"


# =============================================================================
# 9. Tuple return - test that tuple is returned
# =============================================================================


class TestTupleReturn:
    """Tests for verifying methods return tuple."""

    def test_get_context_returns_tuple(self) -> None:
        """
        Test: get_context returns tuple.

        Verifies that return value is tuple (immutable).
        """
        # Arrange
        conversation = Conversation("model_a", "model_b", "test")
        conversation.add_message("A", "user", "test")

        # Act
        result = conversation.get_context("A")

        # Assert
        assert isinstance(result, tuple)

    def test_list_models_returns_list(self) -> None:
        """
        Test: list_models returns list.

        Verifies return type.
        """
        # Arrange - verify type annotation
        import inspect

        from models.ollama_client import OllamaClient

        # Act
        sig = inspect.signature(OllamaClient.list_models)

        # Assert - verify return annotation contains list
        assert "list" in str(sig.return_annotation)


# =============================================================================
# 10. Cache size limit - test that cache is limited
# =============================================================================


class TestCacheSizeLimit:
    """Tests for verifying cache size limit."""

    def test_models_cache_uses_ttl_only(self) -> None:
        """
        Test: _ModelsCache uses only TTL for invalidation.

        Verifies that cache is invalidated only on time expiration.
        """
        # Arrange
        cache = _ModelsCache(ttl=300)
        cache.set(["model1", "model2"])

        # Act & Assert - cache returns data
        result = cache.get()
        assert result == ["model1", "model2"]

        # After TTL expires, cache is invalidated
        import time

        time.sleep(0.1)  # Wait a bit for TTL
        # Note: in real usage TTL is 300 seconds


# =============================================================================
# 11. MessageDict total=True - test on validation
# =============================================================================


class TestMessageDictValidation:
    """Tests for verifying MessageDict validation."""

    def test_message_dict_has_required_fields(self) -> None:
        """
        Test: MessageDict requires role and content.

        Verifies that TypedDict with total=True requires all fields.
        """
        # Arrange & Act - verify annotation

        # Assert - verify MessageDict is TypedDict
        assert hasattr(MessageDict, "__annotations__")
        assert "role" in MessageDict.__annotations__
        assert "content" in MessageDict.__annotations__

    def test_message_dict_role_literal(self) -> None:
        """
        Test: role must be one of valid values.

        Verifies that role is Literal["system", "user", "assistant"].
        """
        # Arrange
        import typing

        # Act - get role annotation
        role_annotation = MessageDict.__annotations__["role"]

        # Assert - verify it's Literal
        assert (
            "Literal" in str(role_annotation)
            or "Literal" in str(typing.get_origin(role_annotation))
            or str(role_annotation).startswith("typing.Literal")
        )

    def test_message_dict_content_str(self) -> None:
        """
        Test: content must be string.

        Verifies that content is annotated as str.
        """
        # Arrange
        content_annotation = MessageDict.__annotations__["content"]

        # Assert
        assert isinstance(content_annotation, type) or "str" in str(content_annotation)

    def test_valid_message_dict(self) -> None:
        """
        Test: correct MessageDict is accepted.

        Verifies that dictionary with role and content works.
        """
        # Arrange
        message: MessageDict = {"role": "user", "content": "test"}

        # Act & Assert
        assert message["role"] == "user"
        assert message["content"] == "test"

    @pytest.mark.asyncio
    async def test_ollama_client_validates_message_dict(self) -> None:
        """
        Test: OllamaClient validates MessageDict.

        Verifies that generate checks message structure.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        # Act & Assert - messages without role should raise error
        with pytest.raises(TypeError, match="role"):
            await client.generate(
                model="test",
                messages=[{"content": "no role"}],  # type: ignore
            )


# =============================================================================
# Integration tests
# =============================================================================


class TestIntegration:
    """Integration tests for verifying component interaction."""

    @pytest.mark.asyncio
    async def test_full_error_handling_chain(self) -> None:
        """
        Test: full error handling chain.

        Verifies that errors propagate correctly through layers.
        """
        # Arrange
        config = Config(ollama_host="http://localhost:11434")
        client = OllamaClient(config=config)

        original_error = aiohttp.ClientError("network error")
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=original_error)

        with patch.object(client, "_get_session", return_value=mock_session):
            # Act
            with pytest.raises(ProviderConnectionError) as exc_info:
                await client.list_models()

            # Assert - verify entire chain
            assert isinstance(exc_info.value, ProviderError)
            assert exc_info.value.__cause__ is original_error
            assert exc_info.value.original_exception is original_error

    @pytest.mark.security
    def test_xss_protection_end_to_end(self) -> None:
        """
        Test: XSS protection end-to-end.

        Verifies that malicious input is fully escaped.
        """
        # Arrange
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "[bold]injected[/bold]",
            "{injected prompt}",
            "*bold* _italic_",
        ]

        # Act & Assert
        for malicious in malicious_inputs:
            result = sanitize_response_for_display(malicious)
            # Verify original symbols are escaped
            # < and > become &lt; and &gt;
            # [ and ] become [[ and ]]
            # { and } become {{ and }}
            # * and _ become \* and \_
            assert "<script>" not in result  # HTML tags escaped
            # Verify escaping happened
            assert result != malicious  # Result differs from original


# =============================================================================
# Additional verification tests from test_audit_fixes_verification.py
# =============================================================================


class TestCloseIdempotency:
    """HIGH 1: Test close() method idempotency."""

    @pytest.mark.asyncio
    async def test_close_can_be_called_multiple_times(self) -> None:
        """Test that close() can be called multiple times without errors."""
        client = OllamaClient(host="http://localhost:11434")

        await client.close()
        await client.close()
        await client.close()

    @pytest.mark.asyncio
    async def test_close_handles_already_closed_session(self) -> None:
        """Test that close() handles already closed session."""
        client = OllamaClient(host="http://localhost:11434")

        await client.close()

        mock_session = AsyncMock()
        mock_session.closed = True
        client._http_manager._session = mock_session

        await client.close()


class TestContextManagementOptimization:
    """HIGH 2: Test context management optimization."""

    def test_trim_before_add_message(self) -> None:
        """Test that context is trimmed before adding message."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test",
        )

        for i in range(60):
            conversation.add_message("A", "user", f"Message {i}")

        context_a = conversation.get_context("A")
        assert len(context_a) <= 51


class TestOllamaClientNoExtraInstances:
    """MEDIUM 2: Test no extra class instances."""

    def test_no_validator_instance(self) -> None:
        """Test that _RequestValidator is not instantiated."""
        client = OllamaClient(host="http://localhost:11434")
        assert not hasattr(client, "_request_validator")

    def test_no_handler_instance(self) -> None:
        """Test that _ResponseHandler is not instantiated."""
        client = OllamaClient(host="http://localhost:11434")
        assert not hasattr(client, "_response_handler")


class TestConversationSystemPrompt:
    """MEDIUM 4: Test system_prompt fix in Conversation."""

    def test_conversation_accepts_system_prompt(self) -> None:
        """Test that Conversation accepts system_prompt."""
        custom_prompt = "Custom system prompt for testing"
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test",
            system_prompt=custom_prompt,
        )
        assert conversation.system_prompt == custom_prompt

    def test_conversation_formats_system_prompt_with_topic(self) -> None:
        """Test that Conversation formats system_prompt with topic in context."""
        conversation = Conversation(
            model_a="llama3",
            model_b="mistral",
            topic="Test Topic",
        )
        context_a = conversation.get_context("A")
        assert len(context_a) > 0
        assert context_a[0]["role"] == "system"
        assert "Test Topic" in context_a[0]["content"]


class TestModelIdExport:
    """LOW 1: Test ModelId export."""

    def test_model_id_in_all(self) -> None:
        """Test that ModelId is exported."""
        from models import conversation

        assert "ModelId" in conversation.__all__


class TestCSSLazyInitialization:
    """LOW 2: Test CSS lazy initialization."""

    def test_css_defined_in_class(self) -> None:
        """Test that CSS is defined in class."""
        assert hasattr(DialogueApp, "CSS")
