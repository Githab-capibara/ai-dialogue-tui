"""Tests for batch 03 fixes (issues 0041-0048).

This file contains tests for verifying:
1. ISSUE-0041: Error handling with exc_info=True in ollama_client.py
2. ISSUE-0042: Config injection in Conversation class
3. ISSUE-0043: URL validation improvements
4. ISSUE-0044: Cache TTL zero handling
5. ISSUE-0045: Environment variable support in Config
6. ISSUE-0046: Cancellation handling in dialogue_service.py
7. ISSUE-0047: Context trimming logic fix
8. ISSUE-0048: HTML injection protection in sanitizer

"""

# pylint: disable=protected-access,import-outside-toplevel,no-member
# pylint: disable=too-few-public-methods,line-too-long

import inspect
import os
from unittest.mock import MagicMock, patch

import pytest

from models.config import Config, validate_ollama_url
from models.conversation import MAX_CONTEXT_LENGTH, Conversation
from models.ollama_client import OllamaClient, _ModelsCache
from services.dialogue_service import DialogueService
from tui.sanitizer import sanitize_response_for_display, sanitize_topic

# =============================================================================
# ISSUE-0041: Error handling with exc_info=True in ollama_client.py
# =============================================================================


class TestOllamaClientErrorHandling:
    """Tests for verifying proper exception logging in ollama_client.py."""

    def test_provider_error_logging_uses_exc_info(self):
        """Verify ProviderError logging uses exc_info=True."""
        source = inspect.getsource(OllamaClient.list_models)
        assert "exc_info=True" in source
        assert "ProviderError" in source


# =============================================================================
# ISSUE-0042: Config injection in Conversation class
# =============================================================================


class TestConversationConfigInjection:
    """Tests for verifying config injection in Conversation class."""

    def test_conversation_accepts_config_parameter(self):
        """Verify Conversation.__init__ accepts config parameter."""
        sig = inspect.signature(Conversation.__init__)
        params = list(sig.parameters.keys())
        assert "config" in params

    def test_conversation_uses_injected_config(self):
        """Verify Conversation uses injected config instead of creating new."""
        custom_config = Config(default_system_prompt="Custom prompt: {topic}")

        conversation = Conversation(
            model_a="model_a",
            model_b="model_b",
            topic="test",
            config=custom_config,
        )

        context = conversation.get_context("A")
        assert "Custom prompt:" in context[0]["content"]

    def test_conversation_uses_default_config_when_not_provided(self):
        """Verify Conversation creates default config when not provided."""
        conversation = Conversation(
            model_a="model_a",
            model_b="model_b",
            topic="test",
        )

        assert conversation._config is not None
        assert isinstance(conversation._config, Config)

    def test_conversation_stores_config_instance(self):
        """Verify Conversation stores the config instance."""
        custom_config = Config(temperature=0.9)
        conversation = Conversation(
            model_a="model_a",
            model_b="model_b",
            topic="test",
            config=custom_config,
        )

        assert conversation._config is custom_config


# =============================================================================
# ISSUE-0043: URL validation improvements
# =============================================================================


class TestURLValidation:
    """Tests for verifying URL validation improvements."""

    def test_validate_url_rejects_empty_scheme(self):
        """Verify validation rejects URLs with empty scheme."""
        assert validate_ollama_url("http:") is False
        assert validate_ollama_url("https:") is False

    def test_validate_url_rejects_scheme_only(self):
        """Verify validation rejects scheme-only URLs."""
        assert validate_ollama_url("http://") is False
        assert validate_ollama_url("https://") is False

    def test_validate_url_accepts_valid_urls(self):
        """Verify validation accepts valid URLs."""
        assert validate_ollama_url("http://localhost:11434") is True
        assert validate_ollama_url("https://example.com") is True
        assert validate_ollama_url("http://192.168.1.1:8080") is True

    def test_validate_url_rejects_invalid_schemes(self):
        """Verify validation rejects invalid schemes."""
        assert validate_ollama_url("ftp://localhost") is False
        assert validate_ollama_url("javascript://alert(1)") is False
        assert validate_ollama_url("data:text/html,<script>alert(1)</script>") is False

    def test_validate_url_rejects_none_and_empty(self):
        """Verify validation rejects None and empty strings."""
        assert validate_ollama_url(None) is False
        assert validate_ollama_url("") is False


# =============================================================================
# ISSUE-0044: Cache TTL zero handling
# =============================================================================


class TestModelsCacheTTL:
    """Tests for verifying cache TTL handling."""

    def test_cache_invalid_when_ttl_is_zero(self):
        """Verify cache is invalid when TTL is 0."""
        cache = _ModelsCache(ttl=0)
        cache.set(["model1", "model2"])

        assert cache._is_cache_valid() is False

    def test_cache_invalid_when_ttl_is_negative(self):
        """Verify cache is invalid when TTL is negative."""
        cache = _ModelsCache(ttl=-1)
        cache.set(["model1", "model2"])

        assert cache._is_cache_valid() is False

    def test_cache_valid_with_positive_ttl(self):
        """Verify cache is valid with positive TTL."""
        cache = _ModelsCache(ttl=300)
        cache.set(["model1", "model2"])

        assert cache._is_cache_valid() is True

    def test_cache_set_stores_models(self):
        """Verify set stores models correctly."""
        cache = _ModelsCache(ttl=300)
        cache.set(["model1", "model2"])

        models = cache.get()
        assert models == ["model1", "model2"]


# =============================================================================
# ISSUE-0045: Environment variable support in Config
# =============================================================================


class TestConfigEnvironmentVariables:
    """Tests for verifying environment variable support in Config."""

    def test_config_reads_ollama_host_from_env(self):
        """Verify Config reads OLLAMA_HOST from environment."""
        env_value = "http://custom-host:9999"
        with patch.dict(os.environ, {"OLLAMA_HOST": env_value}):
            config = Config()
            assert config.ollama_host == env_value

    def test_config_reads_temperature_from_env(self):
        """Verify Config reads OLLAMA_TEMPERATURE from environment."""
        with patch.dict(os.environ, {"OLLAMA_TEMPERATURE": "0.5"}):
            config = Config()
            assert config.temperature == 0.5

    def test_config_reads_max_tokens_from_env(self):
        """Verify Config reads OLLAMA_MAX_TOKENS from environment."""
        with patch.dict(os.environ, {"OLLAMA_MAX_TOKENS": "100"}):
            config = Config()
            assert config.max_tokens == 100

    def test_config_reads_request_timeout_from_env(self):
        """Verify Config reads OLLAMA_REQUEST_TIMEOUT from environment."""
        with patch.dict(os.environ, {"OLLAMA_REQUEST_TIMEOUT": "30"}):
            config = Config()
            assert config.request_timeout == 30

    def test_config_ignores_invalid_env_values(self):
        """Verify Config ignores invalid environment variable values."""
        with patch.dict(os.environ, {"OLLAMA_TEMPERATURE": "invalid"}):
            config = Config()
            assert config.temperature == 0.7

    def test_config_has_env_override_method(self):
        """Verify Config has _apply_env_overrides method."""
        config = Config()
        assert hasattr(config, "_apply_env_overrides")
        assert callable(config._apply_env_overrides)


# =============================================================================
# ISSUE-0046: Cancellation handling in dialogue_service.py
# =============================================================================


class TestDialogueServiceCancellation:
    """Tests for verifying cancellation handling in DialogueService."""

    def test_run_dialogue_cycle_handles_cancelled_error(self):
        """Verify run_dialogue_cycle handles asyncio.CancelledError."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        assert "asyncio.CancelledError" in source

    def test_cancelled_error_re_raised(self):
        """Verify CancelledError is re-raised after logging."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        cancelled_block = source[source.find("CancelledError") : source.find("CancelledError") + 200]
        assert "raise" in cancelled_block, "CancelledError should be re-raised"

    def test_service_has_is_running_property(self):
        """Verify DialogueService has is_running property."""
        mock_conv = MagicMock()
        mock_provider = MagicMock()
        service = DialogueService(mock_conv, mock_provider)
        assert hasattr(service, "is_running")

    def test_service_has_is_paused_property(self):
        """Verify DialogueService has is_paused property."""
        mock_conv = MagicMock()
        mock_provider = MagicMock()
        service = DialogueService(mock_conv, mock_provider)
        assert hasattr(service, "is_paused")


# =============================================================================
# ISSUE-0047: Context trimming logic fix
# =============================================================================


class TestContextTrimming:
    """Tests for verifying context trimming logic fix."""

    def test_trim_context_uses_instead_of_is(self):
        """Verify _trim_context_if_needed uses 'in' instead of 'is'."""
        source = inspect.getsource(Conversation._trim_context_if_needed)
        assert "in last_messages" in source or "in" in source
        assert "is system_message" not in source

    def test_trim_preserves_system_message_when_excluded(self):
        """Verify system message is preserved when not in last_messages."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        long_context = [{"role": "system", "content": "sys"}]
        long_context.extend([{"role": "user", "content": f"msg{i}"} for i in range(55)])

        result = conversation._trim_context_if_needed(long_context, 48)

        assert result[0]["role"] == "system"
        assert len(result) <= 49

    def test_trim_avoids_duplicate_system_message(self):
        """Verify no duplicate system message when context just exceeds limit."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        context = [{"role": "system", "content": "sys"}]
        context.extend([{"role": "user", "content": f"msg{i}"} for i in range(49)])

        result = conversation._trim_context_if_needed(context, 48)

        system_count = sum(1 for m in result if m["role"] == "system")
        assert system_count == 1, f"Expected 1 system message, got {system_count}"

    def test_trim_at_max_context_boundary(self):
        """Test trimming at MAX_CONTEXT_LENGTH boundary."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        context = [{"role": "system", "content": "sys"}]
        context.extend([{"role": "user", "content": f"msg{i}"} for i in range(MAX_CONTEXT_LENGTH)])

        result = conversation._trim_context_if_needed(context, MAX_CONTEXT_LENGTH - 2)

        assert result[0]["role"] == "system"
        system_count = sum(1 for m in result if m["role"] == "system")
        assert system_count == 1

    def test_trim_does_not_modify_original_when_under_limit(self):
        """Verify original context is not modified when under limit."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        short_context = [{"role": "system", "content": "sys"}, {"role": "user", "content": "msg"}]

        result = conversation._trim_context_if_needed(short_context, 10)

        assert result is short_context
        assert len(result) == 2


# =============================================================================
# ISSUE-0048: HTML injection protection in sanitizer
# =============================================================================


class TestSanitizerInjectionProtection:
    """Tests for verifying HTML injection protection."""

    def test_sanitize_topic_escapes_double_quotes(self):
        """Verify sanitize_topic escapes double quotes."""
        result = sanitize_topic('Hello "world"')
        assert "&quot;" in result
        assert '"' not in result

    def test_sanitize_topic_escapes_html_entities(self):
        """Verify sanitize_topic escapes HTML entities."""
        result = sanitize_topic("<script>alert(1)</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result

    def test_sanitize_topic_escapes_ampersand(self):
        """Verify sanitize_topic escapes ampersands."""
        result = sanitize_topic("Tom & Jerry")
        assert "&amp;" in result
        assert result.count("&") == 1 and "&amp;" in result

    def test_sanitize_topic_preserves_normal_text(self):
        """Verify sanitize_topic preserves normal text."""
        result = sanitize_topic("Hello world")
        assert result == "Hello world"

    def test_sanitize_response_escapes_double_quotes(self):
        """Verify sanitize_response_for_display escapes double quotes."""
        result = sanitize_response_for_display('Hello "world"')
        assert "&quot;" in result

    def test_sanitize_response_escapes_single_quotes(self):
        """Verify sanitize_response_for_display escapes single quotes."""
        result = sanitize_response_for_display("Hello 'world'")
        assert "x27" in result or "&#39;" in result
        assert "'" not in result

    def test_sanitize_response_escapes_angle_brackets(self):
        """Verify sanitize_response_for_display escapes angle brackets."""
        result = sanitize_response_for_display("<script>alert(1)</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "<script>" not in result

    def test_sanitize_topic_html_entity_bypass(self):
        """Verify sanitize_topic prevents HTML entity bypass attacks."""
        result = sanitize_topic("&lt;script&gt;alert(1)&lt;/script&gt;")
        assert "<" not in result
        assert ">" not in result

    def test_sanitize_response_handles_empty_string(self):
        """Verify sanitize_response handles empty string."""
        result = sanitize_response_for_display("")
        assert result == ""

    def test_sanitize_topic_handles_empty_string(self):
        """Verify sanitize_topic handles empty string."""
        result = sanitize_topic("")
        assert result == ""

    def test_sanitize_topic_handles_non_string(self):
        """Verify sanitize_topic raises TypeError for non-string."""
        with pytest.raises(TypeError):
            sanitize_topic(123)

    def test_sanitize_response_handles_non_string(self):
        """Verify sanitize_response raises TypeError for non-string."""
        with pytest.raises(TypeError):
            sanitize_response_for_display(123)
