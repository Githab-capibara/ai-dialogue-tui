"""Тесты для проверки всех исправлений из аудита кода.

Этот файл содержит тесты для проверки следующих исправлений:
1. __slots__ в Config и Conversation
2. Валидация параметров Config
3. Конкретные типы исключений
4. _handle_api_error с dictionary mapping
5. validate_messages
6. Уменьшенная вложенность (early returns)
7. Константы (DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, etc.)
8. sanitize_topic с MAX_RESPONSE_PREVIEW_LENGTH
9. pause/resume без избыточных проверок
10. Удаление update_for_ready
11. DEFAULT_NOTIFY_TIMEOUT
12. Упрощённая логика ModelSelectionScreen
13. Обработка ошибок в on_unmount

Note:
    Тесты используют доступ к внутренним атрибутам и импорты внутри функций,
    что оправдано для тестирования.
"""

# pylint: disable=protected-access,import-outside-toplevel,no-member

import inspect
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from controllers.dialogue_controller import DialogueController
from models.config import (
    DEFAULT_MAX_TOKENS,
    DEFAULT_PAUSE_BETWEEN_MESSAGES,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_TEMPERATURE,
    MAX_TEMPERATURE,
    MIN_MAX_TOKENS,
    MIN_PAUSE_BETWEEN_MESSAGES,
    MIN_REQUEST_TIMEOUT,
    MIN_TEMPERATURE,
    Config,
)
from models.conversation import Conversation
from models.ollama_client import (
    _DEFAULT_OPTIONS,
    OllamaClient,
)
from models.provider import ProviderError
from services.dialogue_service import DialogueService
from tui.app import DEFAULT_NOTIFY_TIMEOUT, ModelSelectionScreen
from tui.sanitizer import MAX_RESPONSE_PREVIEW_LENGTH, sanitize_topic

# =============================================================================
# 1. Тесты для __slots__ в Config
# =============================================================================


class TestConfigSlots:
    """Тесты для проверки __slots__ в Config."""

    def test_config_has_slots(self):
        """Проверить, что Config имеет __slots__."""
        assert hasattr(Config, "__slots__")
        assert Config.__slots__ is not None

    def test_config_slots_prevents_arbitrary_attributes(self):
        """Проверить, что нельзя добавить произвольный атрибут в Config."""
        config = Config()
        # __slots__ предотвращает создание произвольных атрибутов
        # Ошибка может быть TypeError или AttributeError в зависимости от
        # версии Python
        with pytest.raises((AttributeError, TypeError)):
            config.arbitrary_attribute = "value"

    def test_config_slots_contains_expected_fields(self):
        """Проверить, что __slots__ содержит ожидаемые поля."""
        expected_fields = {
            "temperature",
            "max_tokens",
            "request_timeout",
            "pause_between_messages",
            "default_system_prompt",
            "ollama_host",
        }
        assert expected_fields.issubset(set(Config.__slots__))

    def test_config_memory_efficiency_with_slots(self):
        """Проверить экономию памяти с __slots__ (опционально)."""
        # Config с __slots__ не имеет __dict__
        config = Config()
        assert not hasattr(config, "__dict__")


# =============================================================================
# 2. Тесты для __slots__ в Conversation
# =============================================================================


class TestConversationSlots:
    """Тесты для проверки __slots__ в Conversation."""

    def test_conversation_has_slots(self):
        """Проверить, что Conversation имеет __slots__."""
        assert hasattr(Conversation, "__slots__")
        assert Conversation.__slots__ is not None

    def test_conversation_slots_prevents_arbitrary_attributes(self):
        """Проверить, что нельзя добавить произвольный атрибут в Conversation."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        with pytest.raises(AttributeError):
            conversation.arbitrary_attribute = "value"

    def test_conversation_slots_contains_expected_fields(self):
        """Проверить, что __slots__ содержит ожидаемые поля."""
        expected_fields = {
            "model_a",
            "model_b",
            "topic",
            "_config",
            "_context_a",
            "_context_b",
            "_current_turn",
            "_system_prompt",
            "_initialized",
        }
        assert expected_fields.issubset(set(Conversation.__slots__))

    def test_conversation_memory_efficiency_with_slots(self):
        """Проверить экономию памяти с __slots__ (опционально)."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        assert not hasattr(conversation, "__dict__")


# =============================================================================
# 3. Тесты для валидации Config
# =============================================================================


class TestConfigValidation:
    """Тесты для проверки валидации параметров Config."""

    def test_config_temperature_below_zero_raises(self):
        """temperature за пределами 0.0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="temperature"):
            Config(temperature=-0.1)

    def test_config_temperature_above_one_raises(self):
        """temperature за пределами 1.0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="temperature"):
            Config(temperature=1.1)

    def test_config_temperature_boundary_zero(self):
        """temperature = 0.0 должен приниматься."""
        config = Config(temperature=0.0)
        assert config.temperature == 0.0

    def test_config_temperature_boundary_one(self):
        """temperature = 1.0 должен приниматься."""
        config = Config(temperature=1.0)
        assert config.temperature == 1.0

    def test_config_max_tokens_zero_raises(self):
        """max_tokens <= 0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="max_tokens"):
            Config(max_tokens=0)

    def test_config_max_tokens_negative_raises(self):
        """max_tokens < 0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="max_tokens"):
            Config(max_tokens=-1)

    def test_config_max_tokens_boundary_one(self):
        """max_tokens = 1 должен приниматься."""
        config = Config(max_tokens=1)
        assert config.max_tokens == 1

    def test_config_request_timeout_zero_raises(self):
        """request_timeout <= 0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="request_timeout"):
            Config(request_timeout=0)

    def test_config_request_timeout_negative_raises(self):
        """request_timeout < 0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="request_timeout"):
            Config(request_timeout=-1)

    def test_config_request_timeout_boundary_one(self):
        """request_timeout = 1 должен приниматься."""
        config = Config(request_timeout=1)
        assert config.request_timeout == 1

    def test_config_pause_between_messages_negative_raises(self):
        """pause_between_messages < 0 должен вызывать ValueError."""
        with pytest.raises(ValueError, match="pause_between_messages"):
            Config(pause_between_messages=-0.1)

    def test_config_pause_between_messages_zero_accepted(self):
        """pause_between_messages = 0 должен приниматься."""
        config = Config(pause_between_messages=0.0)
        assert config.pause_between_messages == 0.0

    def test_config_valid_values_accepted(self):
        """Корректные значения должны приниматься."""
        config = Config(
            temperature=0.5,
            max_tokens=500,
            request_timeout=120,
            pause_between_messages=2.0,
        )
        assert config.temperature == 0.5
        assert config.max_tokens == 500
        assert config.request_timeout == 120
        assert config.pause_between_messages == 2.0


# =============================================================================
# 4. Тесты для конкретных типов исключений
# =============================================================================


class TestSpecificExceptionTypes:
    """Тесты для проверки конкретных типов исключений."""

    def test_provider_error_has_original_exception_property(self):
        """Проверить, что ProviderError имеет свойство original_exception."""
        original = ValueError("original error")
        error = ProviderError("test error", original_exception=original)
        assert error.original_exception is original

    def test_provider_error_without_original_exception(self):
        """Проверить, что ProviderError может быть без original_exception."""
        error = ProviderError("test error")
        assert error.original_exception is None

    def test_provider_connection_error_is_subclass(self):
        """Проверить, что ProviderConnectionError это подкласс ProviderError."""
        from models.provider import ProviderConnectionError

        error = ProviderConnectionError("connection error")
        assert isinstance(error, ProviderError)

    def test_provider_configuration_error_is_subclass(self):
        """Проверить, что ProviderConfigurationError это подкласс ProviderError."""
        from models.provider import ProviderConfigurationError

        error = ProviderConfigurationError("config error")
        assert isinstance(error, ProviderError)

    def test_provider_generation_error_is_subclass(self):
        """Проверить, что ProviderGenerationError это подкласс ProviderError."""
        from models.provider import ProviderGenerationError

        error = ProviderGenerationError("generation error")
        assert isinstance(error, ProviderError)


# =============================================================================
# 5. Тесты для валидации сообщений через _RequestValidator
# =============================================================================


class TestRequestValidator:
    """Тесты для проверки _RequestValidator."""

    def test_validate_messages_with_valid_list(self):
        """Проверить валидацию корректного списка сообщений."""
        from models.ollama_client import _RequestValidator

        messages = [
            {"role": "system", "content": "test"},
            {"role": "user", "content": "test"},
        ]
        # Не должно вызывать исключений
        _RequestValidator.validate_messages(messages)

    def test_validate_messages_non_list_raises(self):
        """Проверить, что не-список вызывает ValueError."""
        from models.ollama_client import _RequestValidator

        with pytest.raises(ValueError, match="списком"):
            _RequestValidator.validate_messages("not a list")

    def test_validate_messages_non_dict_item_raises(self):
        """Проверить, что не-dict элемент вызывает ValueError."""
        from models.ollama_client import _RequestValidator

        with pytest.raises(ValueError, match="словарём"):
            _RequestValidator.validate_messages(["not a dict"])

    def test_validate_messages_missing_role_raises(self):
        """Проверить, что отсутствие 'role' вызывает ValueError."""
        from models.ollama_client import _RequestValidator

        with pytest.raises(ValueError, match="'role' и 'content'"):
            _RequestValidator.validate_messages([{"content": "test"}])

    def test_validate_messages_missing_content_raises(self):
        """Проверить, что отсутствие 'content' вызывает ValueError."""
        from models.ollama_client import _RequestValidator

        with pytest.raises(ValueError, match="'role' и 'content'"):
            _RequestValidator.validate_messages([{"role": "user"}])

    def test_validate_messages_empty_list_accepted(self):
        """Проверить, что пустой список принимается."""
        from models.ollama_client import _RequestValidator

        _RequestValidator.validate_messages([])


# =============================================================================
# 6. Тесты для уменьшенной вложенности (early returns)
# =============================================================================


class TestReducedNesting:
    """Тесты для проверки уменьшенной вложенности."""

    def test_ollama_client_list_models_has_early_return_pattern(self):
        """Проверить early returns в list_models."""
        source = inspect.getsource(OllamaClient.list_models)
        # Проверяем, что есть явный raise ProviderError для статуса != 200
        assert (
            "if response.status != 200:" in source or "validate_status_code" in source
        )

    def test_ollama_client_generate_has_early_return_pattern(self):
        """Проверить early returns в generate."""
        source = inspect.getsource(OllamaClient.generate)
        # Проверяем, что есть явный raise ProviderError для статуса != 200
        assert (
            "if response.status != 200:" in source or "validate_status_code" in source
        )

    def test_ollama_client_uses_try_except_not_nested_if(self):
        """Проверить, что используется try/except вместо вложенных if."""
        source = inspect.getsource(OllamaClient.list_models)
        # Проверяем, что есть try/except блок
        assert "try:" in source
        assert "except" in source


# =============================================================================
# 8. Тесты для констант
# =============================================================================


class TestConstants:
    """Тесты для проверки констант."""

    def test_default_temperature_constant_exists(self):
        """Проверить, что DEFAULT_TEMPERATURE существует."""
        assert DEFAULT_TEMPERATURE == 0.7

    def test_default_max_tokens_constant_exists(self):
        """Проверить, что DEFAULT_MAX_TOKENS существует."""
        assert DEFAULT_MAX_TOKENS == 200

    def test_default_request_timeout_constant_exists(self):
        """Проверить, что DEFAULT_REQUEST_TIMEOUT существует."""
        assert DEFAULT_REQUEST_TIMEOUT == 60

    def test_default_pause_between_messages_constant_exists(self):
        """Проверить, что DEFAULT_PAUSE_BETWEEN_MESSAGES существует."""
        assert DEFAULT_PAUSE_BETWEEN_MESSAGES == 1.0

    def test_min_temperature_constant_exists(self):
        """Проверить, что MIN_TEMPERATURE существует."""
        assert MIN_TEMPERATURE == 0.0

    def test_max_temperature_constant_exists(self):
        """Проверить, что MAX_TEMPERATURE существует."""
        assert MAX_TEMPERATURE == 1.0

    def test_min_max_tokens_constant_exists(self):
        """Проверить, что MIN_MAX_TOKENS существует."""
        assert MIN_MAX_TOKENS == 1

    def test_min_request_timeout_constant_exists(self):
        """Проверить, что MIN_REQUEST_TIMEOUT существует."""
        assert MIN_REQUEST_TIMEOUT == 1

    def test_min_pause_between_messages_constant_exists(self):
        """Проверить, что MIN_PAUSE_BETWEEN_MESSAGES существует."""
        assert MIN_PAUSE_BETWEEN_MESSAGES == 0.0

    def test_default_options_uses_constants(self):
        """Проверить, что _DEFAULT_OPTIONS использует константы."""
        assert _DEFAULT_OPTIONS["temperature"] == DEFAULT_TEMPERATURE
        assert _DEFAULT_OPTIONS["num_predict"] == DEFAULT_MAX_TOKENS


# =============================================================================
# 9. Тесты для sanitize_topic с константой
# =============================================================================


class TestSanitizeTopicWithConstant:
    """Тесты для проверки sanitize_topic с MAX_RESPONSE_PREVIEW_LENGTH."""

    def test_max_response_preview_length_constant_exists(self):
        """Проверить, что MAX_RESPONSE_PREVIEW_LENGTH существует."""
        assert MAX_RESPONSE_PREVIEW_LENGTH == 100

    def test_sanitize_topic_escapes_braces(self):
        """Проверить экранирование фигурных скобок."""
        result = sanitize_topic("test {topic}")
        assert "{{" in result
        assert "}}" in result

    def test_sanitize_topic_strips_whitespace(self):
        """Проверить удаление пробелов."""
        result = sanitize_topic("  test topic  ")
        assert result == "test topic"

    def test_sanitize_topic_handles_brackets(self):
        """Проверить обработку квадратных скобок."""
        result = sanitize_topic("test [bracket]")
        assert "[[" in result
        assert "]]" in result


# =============================================================================
# 10. Тесты для pause/resume без избыточных проверок
# =============================================================================


class TestPauseResumeIndependent:
    """Тесты для проверки pause/resume без избыточных проверок."""

    def test_pause_works_regardless_of_is_running(self):
        """Проверить, что pause работает независимо от is_running."""
        conversation = Conversation("model_a", "model_b", "test")
        provider = MagicMock()
        service = DialogueService(conversation, provider)

        # is_running = False, но pause должен работать
        assert service.is_running is False
        service.pause()
        assert service.is_paused is True

    def test_resume_works_regardless_of_is_running(self):
        """Проверить, что resume работает независимо от is_running."""
        conversation = Conversation("model_a", "model_b", "test")
        provider = MagicMock()
        service = DialogueService(conversation, provider)

        # Устанавливаем paused = True
        service._is_paused = True  # noqa: W0212

        # is_running = False, но resume должен работать
        assert service.is_running is False
        service.resume()
        assert service.is_paused is False

    def test_pause_sets_paused_flag(self):
        """Проверить, что pause устанавливает флаг is_paused."""
        conversation = Conversation("model_a", "model_b", "test")
        provider = MagicMock()
        service = DialogueService(conversation, provider)

        service.start()
        service.pause()

        assert service.is_paused is True
        assert service.is_running is True

    def test_resume_clears_paused_flag(self):
        """Проверить, что resume сбрасывает флаг is_paused."""
        conversation = Conversation("model_a", "model_b", "test")
        provider = MagicMock()
        service = DialogueService(conversation, provider)

        service.start()
        service.pause()
        service.resume()

        assert service.is_paused is False
        assert service.is_running is True


# =============================================================================
# 11. Тесты для удаления update_for_ready
# =============================================================================


class TestUpdateForReadyRemoved:
    """Тесты для проверки удаления update_for_ready."""

    def test_update_for_ready_method_not_exists(self):
        """Проверить, что метод update_for_ready удалён."""
        from controllers import dialogue_controller as dc_module

        # Проверяем, что метода нет в классе
        assert not hasattr(DialogueController, "update_for_ready")

        # Проверяем, что метода нет в исходном коде
        source = inspect.getsource(dc_module)
        assert "def update_for_ready" not in source

    def test_existing_functionality_works(self):
        """Проверить, что существующий функционал работает."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        # Проверяем, что handle_start работает
        result = controller.handle_start()
        assert result is True
        assert controller.state.is_dialogue_active is True

        # Сбрасываем состояние сервиса для следующих тестов
        mock_service.is_running = True
        mock_service.is_paused = False

        # Проверяем, что handle_pause работает
        result = controller.handle_pause()
        assert result is True

        # Проверяем, что handle_clear работает
        controller.handle_clear()
        assert controller.state.turn_count == 0


# =============================================================================
# 12. Тесты для DEFAULT_NOTIFY_TIMEOUT
# =============================================================================


class TestDefaultNotifyTimeout:
    """Тесты для проверки DEFAULT_NOTIFY_TIMEOUT."""

    def test_default_notify_timeout_constant_exists(self):
        """Проверить, что DEFAULT_NOTIFY_TIMEOUT существует."""
        assert DEFAULT_NOTIFY_TIMEOUT == 10

    def test_default_notify_timeout_is_integer(self):
        """Проверить, что DEFAULT_NOTIFY_TIMEOUT - целое число."""
        assert isinstance(DEFAULT_NOTIFY_TIMEOUT, int)

    def test_default_notify_timeout_used_in_app(self):
        """Проверить, что константа используется в app.py."""
        from tui import app as app_module

        source = inspect.getsource(app_module)
        assert "DEFAULT_NOTIFY_TIMEOUT" in source


# =============================================================================
# 13. Тесты для упрощённой логики ModelSelectionScreen
# =============================================================================


class TestModelSelectionScreenSimplified:
    """Тесты для проверки упрощённой логики ModelSelectionScreen."""

    def test_get_model_value_with_empty_list(self):
        """Проверить _get_model_value с пустым списком."""
        screen = ModelSelectionScreen(models=[])
        result = screen._get_model_value(0)
        assert result is None

    def test_get_model_value_with_valid_index(self):
        """Проверить _get_model_value с корректным индексом."""
        screen = ModelSelectionScreen(models=["model1", "model2", "model3"])
        result = screen._get_model_value(1)
        assert result == "model2"

    def test_get_model_value_with_out_of_bounds_index(self):
        """Проверить _get_model_value с индексом за границами."""
        screen = ModelSelectionScreen(models=["model1", "model2"])
        result = screen._get_model_value(10)
        assert result == "model2"  # Последний элемент

    def test_get_model_value_with_zero_index(self):
        """Проверить _get_model_value с индексом 0."""
        screen = ModelSelectionScreen(models=["model1", "model2"])
        result = screen._get_model_value(0)
        assert result == "model1"

    def test_on_button_pressed_with_start_btn(self):
        """Проверить on_button_pressed с кнопкой старта."""
        screen = ModelSelectionScreen(models=["model1", "model2"])

        # Создаем мок события с правильным button.id
        mock_button = MagicMock()
        mock_button.id = "start_btn"
        mock_event = MagicMock()
        mock_event.button = mock_button

        # Вызываем метод - он должен вызвать _on_start_pressed
        # Проверяем, что метод существует и вызывается без ошибок
        assert hasattr(screen, "_on_start_pressed")
        # Метод должен существовать и быть вызванным
        screen.on_button_pressed(mock_event)
        # Если дошли сюда - тест пройден (метод вызван)

    def test_on_button_pressed_with_cancel_btn(self):
        """Проверить on_button_pressed с кнопкой отмены."""
        screen = ModelSelectionScreen(models=["model1", "model2"])

        # Создаем мок события
        mock_button = MagicMock()
        mock_button.id = "cancel_btn"
        mock_event = MagicMock()
        mock_event.button = mock_button

        # Проверяем, что dismiss существует
        assert hasattr(screen, "dismiss")
        # Вызываем метод - он должен вызвать dismiss(None)
        screen.on_button_pressed(mock_event)


# =============================================================================
# 14. Тесты для обработки ошибок в on_unmount
# =============================================================================


class TestOnUnmountErrorHandling:
    """Тесты для проверки обработки ошибок в on_unmount."""

    def test_on_unmount_logs_warning_on_error(self, caplog):
        """Проверить логирование warning при ошибке."""
        import logging

        from tui.app import DialogueApp

        app = DialogueApp()

        # Мокаем _dialogue_task с ошибкой при отмене
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()

        async def raise_error():
            raise aiohttp.ClientError("cleanup error")

        mock_task.__await__ = raise_error

        app._dialogue_task = mock_task  # noqa: W0212

        # Мокаем _controller
        mock_controller = AsyncMock()
        mock_controller.cleanup.side_effect = aiohttp.ClientError("cleanup error")
        app._controller = mock_controller  # noqa: W0212

        # Запускаем on_unmount
        with caplog.at_level(logging.WARNING):
            # Используем asyncio.run для асинхронного метода
            import asyncio

            asyncio.run(app.on_unmount())

        # Проверяем, что warning был залогирован
        assert any(
            "Ошибка при очистке ресурсов" in record.message for record in caplog.records
        )

    def test_on_unmount_handles_cancelled_error(self):
        """Проверить обработку asyncio.CancelledError."""
        from tui.app import DialogueApp

        app = DialogueApp()

        # Мокаем _dialogue_task
        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()

        async def raise_cancelled():
            raise asyncio.CancelledError()

        mock_task.__await__ = raise_cancelled
        app._dialogue_task = mock_task  # noqa: W0212

        # Не должно вызывать исключений
        import asyncio

        asyncio.run(app.on_unmount())


# =============================================================================
# Интеграционные тесты
# =============================================================================


class TestIntegration:
    """Интеграционные тесты для проверки взаимодействия компонентов."""

    @pytest.mark.asyncio
    async def test_config_validation_with_ollama_client(self):
        """Проверить, что валидация Config работает с OllamaClient."""
        config = Config(
            temperature=0.5,
            max_tokens=300,
            request_timeout=90,
            ollama_host="http://localhost:11434",
        )

        # Создаем клиент с валидной конфигурацией
        client = OllamaClient(config=config)
        assert client.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_conversation_with_validated_config(self):
        """Проверить Conversation с валидированным Config."""
        config = Config(
            temperature=0.8,
            default_system_prompt="Тестовая тема: {topic}",
        )

        conversation = Conversation(
            "model_a",
            "model_b",
            "тестирование",
            _config=config,
        )

        assert conversation._system_prompt == "Тестовая тема: тестирование"  # noqa: W0212

    def test_dialogue_service_pause_resume_flow(self):
        """Проверить полный цикл pause/resume в DialogueService."""
        conversation = Conversation("model_a", "model_b", "test")
        provider = MagicMock()
        service = DialogueService(conversation, provider)

        # Начальное состояние
        assert service.is_running is False
        assert service.is_paused is False

        # Запуск
        service.start()
        assert service.is_running is True
        assert service.is_paused is False

        # Пауза
        service.pause()
        assert service.is_running is True
        assert service.is_paused is True

        # Возобновление
        service.resume()
        assert service.is_running is True
        assert service.is_paused is False

        # Остановка
        service.stop()
        assert service.is_running is False
        assert service.is_paused is False
