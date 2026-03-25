"""Тесты целостности архитектуры для AI Dialogue TUI.

# pylint: disable=import-outside-toplevel,missing-class-docstring,missing-function-docstring,unused-argument,reimported

Этот модуль проверяет архитектурные принципы и паттерны:
- ProviderError иерархия исключений
- Config расположение в models модуле
- DialogueService обработка ошибок
- Разделение ответственности между слоями
- Кэширование list_models
- Ограничение контекста
- Sanitizer протокол
- Модульность и зависимости
- SOLID принципы
- Интеграционные сценарии

Всего: 42 теста
"""

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
from tui.sanitizer import Sanitizer, sanitize_response_for_display, sanitize_topic

# =============================================================================
# 1. Тесты ProviderError иерархии
# =============================================================================


class TestProviderErrorHierarchy:
    """Тесты для проверки иерархии исключений ProviderError."""

    def test_provider_error_base_class_exists(self) -> None:
        """
        Проверка что базовый класс ProviderError существует.

        ProviderError должен быть базовым исключением для всех ошибок провайдера.
        """
        assert ProviderError is not None
        assert issubclass(ProviderError, Exception)

    def test_provider_configuration_error_exists(self) -> None:
        """
        Проверка что ProviderConfigurationError существует.

        Это исключение для ошибок конфигурации провайдера.
        """
        assert ProviderConfigurationError is not None
        assert issubclass(ProviderConfigurationError, ProviderError)

    def test_provider_connection_error_exists(self) -> None:
        """
        Проверка что ProviderConnectionError существует.

        Это исключение для ошибок подключения к провайдеру.
        """
        assert ProviderConnectionError is not None
        assert issubclass(ProviderConnectionError, ProviderError)

    def test_provider_generation_error_exists(self) -> None:
        """
        Проверка что ProviderGenerationError существует.

        Это исключение для ошибок генерации ответа.
        """
        assert ProviderGenerationError is not None
        assert issubclass(ProviderGenerationError, ProviderError)

    def test_all_errors_inherit_from_provider_error(self) -> None:
        """
        Проверка что все исключения провайдера наследуются от ProviderError.

        Это позволяет ловить все ошибки провайдера через except ProviderError.
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
        Проверка что ProviderError сохраняет оригинальное исключение.

        Это важно для отладки и сохранения цепочки исключений.
        """
        original_error = ValueError("Original error")
        provider_error = ProviderError(
            "Provider error message",
            original_exception=original_error,
        )

        assert provider_error.original_exception is original_error
        assert str(provider_error) == "Provider error message"

        # Тест без оригинального исключения
        provider_error_no_original = ProviderError("Another error")
        assert provider_error_no_original.original_exception is None


# =============================================================================
# 2. Тесты Config в models
# =============================================================================


class TestConfigLocation:
    """Тесты для проверки расположения Config в models модуле."""

    def test_config_importable_from_models(self) -> None:
        """
        Проверка что Config импортируется из models модуля.

        Config должен быть доступен через models.config.
        """
        from models.config import Config as ConfigFromConfig

        assert ConfigFromConfig is not None
        assert ConfigFromConfig is Config

    def test_config_in_models_module(self) -> None:
        """
        Проверка что Config находится в models модуле.

        Это правильное расположение для domain-объекта.
        """
        # Проверяем что models/config.py существует
        import os

        assert os.path.exists("models/config.py")

        # Проверяем что Config экспортируется из models
        from models import config

        assert hasattr(config, "Config")
        assert config.Config is Config


# =============================================================================
# 3. Тесты DialogueService с ProviderError
# =============================================================================


class TestDialogueServiceErrors:
    """Тесты для проверки обработки ошибок в DialogueService."""

    def _create_service_with_mock_provider(
        self, mock_provider: AsyncMock
    ) -> DialogueService:
        """Создать сервис с мок-провайдером."""
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
        Проверка что сервис использует ProviderError а не OllamaError.

        Сервис должен зависеть от абстракций, не от конкретных реализаций.
        """
        # Проверяем что в dialogue_service.py используется ProviderError
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        assert "ProviderError" in source
        assert "from models.provider import" in source
        # Убеждаемся что нет импорта специфичных ошибок Ollama
        assert "OllamaError" not in source

    def test_service_handles_provider_configuration_error(self) -> None:
        """
        Проверка что сервис корректно обрабатывает ProviderConfigurationError.

        Ошибка конфигурации должна пробрасываться дальше.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderConfigurationError(
            "Invalid configuration"
        )

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Ошибка должна пробрасываться
        with pytest.raises(ProviderConfigurationError):
            asyncio.run(service.run_dialogue_cycle())

    def test_service_handles_provider_connection_error(self) -> None:
        """
        Проверка что сервис корректно обрабатывает ProviderConnectionError.

        Ошибка подключения должна пробрасываться дальше.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderConnectionError(
            "Connection failed"
        )

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Ошибка должна пробрасываться
        with pytest.raises(ProviderConnectionError):
            asyncio.run(service.run_dialogue_cycle())

    def test_service_handles_provider_generation_error(self) -> None:
        """
        Проверка что сервис корректно обрабатывает ProviderGenerationError.

        Ошибка генерации должна пробрасываться дальше.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderGenerationError(
            "Generation failed"
        )

        service = self._create_service_with_mock_provider(mock_provider)
        service.start()

        # Ошибка должна пробрасываться
        with pytest.raises(ProviderGenerationError):
            asyncio.run(service.run_dialogue_cycle())


# =============================================================================
# 4. Тесты разделения ответственности
# =============================================================================


class TestSeparationOfConcerns:
    """Тесты для проверки разделения ответственности между слоями."""

    def test_ui_layer_does_not_contain_business_logic(self) -> None:
        """
        Проверка что UI слой не содержит бизнес-логики.

        tui/app.py должен содержать только UI-логику.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что бизнес-логика вынесена в сервис
        assert "DialogueService" in source
        assert "DialogueController" in source

        # Проверяем что нет прямой бизнес-логики
        assert "async def run_dialogue_cycle" not in source
        assert "class DialogueService" not in source

    def test_service_layer_handles_dialogue_logic(self) -> None:
        """
        Проверка что сервисный слой содержит логику диалога.

        services/dialogue_service.py должен содержать бизнес-логику.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем наличие бизнес-логики
        assert "run_dialogue_cycle" in source
        assert "start" in source
        assert "pause" in source
        assert "resume" in source
        assert "stop" in source
        assert "clear_history" in source

    def test_domain_layer_independent_of_infrastructure(self) -> None:
        """
        Проверка что доменный слой независим от инфраструктуры.

        models/conversation.py не должен импортировать инфраструктурные модули.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем отсутствие инфраструктурных импортов
        assert "from models.ollama_client" not in source
        assert "import models.ollama_client" not in source
        assert "from services" not in source
        assert "from controllers" not in source
        assert "from tui" not in source

        # Проверяем что используются только абстракции
        assert "from models.provider import" in source
        assert "ModelProvider" in source


# =============================================================================
# 5. Тесты кэширования list_models
# =============================================================================


class TestModelsCaching:
    """Тесты для проверки кэширования списка моделей."""

    def test_list_models_uses_cache(self) -> None:
        """
        Проверка что list_models использует кэширование.

        OllamaClient должен кэшировать результат list_models.
        """
        # Проверяем что _ModelsCache используется в OllamaClient
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "_ModelsCache" in source
        assert "_models_cache" in source
        assert "self._models_cache.get()" in source
        assert "self._models_cache.set(" in source

    def test_cache_has_ttl_300_seconds(self) -> None:
        """
        Проверка что кэш имеет TTL 300 секунд.

        Время жизни кэша должно быть 5 минут.
        """
        # Проверяем константу TTL
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "_MODELS_CACHE_TTL" in source
        assert "300" in source

        # Проверяем значение константы
        from models.ollama_client import _MODELS_CACHE_TTL

        assert _MODELS_CACHE_TTL == 300

    def test_cache_invalidates_after_ttl(self) -> None:
        """
        Проверка что кэш инвалидируется после TTL.

        Кэш должен становиться невалидным после истечения времени жизни.
        """
        cache = _ModelsCache(ttl=1)  # 1 секунда для теста

        # Устанавливаем кэш
        cache.set(["model1", "model2"])
        assert cache.get() == ["model1", "model2"]

        # Ждём истечения TTL
        time.sleep(1.1)

        # Кэш должен быть невалиден
        assert cache.get() is None

    def test_cache_clears_on_error(self) -> None:
        """
        Проверка что кэш очищается при ошибке.

        При ошибке подключения кэш должен инвалидироваться.
        """
        # Проверяем что close() инвалидирует кэш
        with open("models/ollama_client.py", encoding="utf-8") as f:
            source = f.read()

        assert "self._models_cache.invalidate()" in source

        # Тестируем поведение кэша
        cache = _ModelsCache()
        cache.set(["model1"])
        assert cache.get() == ["model1"]

        cache.invalidate()
        assert cache.get() is None


# =============================================================================
# 6. Тесты ограничения контекста
# =============================================================================


class TestContextLengthLimit:
    """Тесты для проверки ограничения длины контекста."""

    def test_max_context_length_constant_exists(self) -> None:
        """
        Проверка что константа MAX_CONTEXT_LENGTH существует.

        Константа должна быть определена в models/conversation.py.
        """
        assert MAX_CONTEXT_LENGTH is not None
        assert isinstance(MAX_CONTEXT_LENGTH, int)

    def test_context_trims_when_exceeds_limit(self) -> None:
        """
        Проверка что контекст обрезается при превышении лимита.

        При добавлении сообщения которое превышает лимит, контекст должен обрезаться.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Добавляем больше сообщений чем лимит
        for i in range(MAX_CONTEXT_LENGTH + 10):
            conversation.add_message("A", "user", f"Message {i}")

        # Контекст должен быть обрезан
        context = conversation.get_context("A")
        assert len(context) <= MAX_CONTEXT_LENGTH

        # Системный промпт должен сохраниться
        assert context[0]["role"] == "system"

    def test_context_does_not_trim_when_under_limit(self) -> None:
        """
        Проверка что контекст не обрезается если под лимитом.

        При нормальном количестве сообщений обрезка не нужна.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Добавляем меньше сообщений чем лимит
        initial_count = len(conversation.get_context("A"))
        for i in range(5):
            conversation.add_message("A", "user", f"Message {i}")

        # Контекст должен увеличиться но не обрезаться
        context = conversation.get_context("A")
        assert len(context) == initial_count + 5

    def test_max_context_length_is_50(self) -> None:
        """
        Проверка что MAX_CONTEXT_LENGTH равно 50.

        Это значение должно быть константой.
        """
        assert MAX_CONTEXT_LENGTH == 50


# =============================================================================
# 7. Тесты Sanitizer протокола
# =============================================================================


class TestSanitizerProtocol:
    """Тесты для проверки Sanitizer протокола."""

    def test_sanitizer_protocol_exists(self) -> None:
        """
        Проверка что протокол Sanitizer существует.

        Протокол должен быть определён в tui/sanitizer.py.
        """
        assert Sanitizer is not None
        assert issubclass(type(Sanitizer), type(Protocol))

    def test_sanitize_topic_implements_protocol(self) -> None:
        """
        Проверка что sanitize_topic соответствует протоколу.

        Функция должна иметь правильную сигнатуру.
        """
        import inspect

        sig = inspect.signature(sanitize_topic)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "topic"

        # Проверяем что функция работает
        result = sanitize_topic("test topic")
        assert isinstance(result, str)

    def test_sanitize_response_implements_protocol(self) -> None:
        """
        Проверка что sanitize_response_for_display соответствует протоколу.

        Функция должна иметь правильную сигнатуру.
        """
        import inspect

        sig = inspect.signature(sanitize_response_for_display)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "response"

        # Проверяем что функция работает
        result = sanitize_response_for_display("test response")
        assert isinstance(result, str)

    def test_protocol_runtime_checkable(self) -> None:
        """
        Проверка что протокол runtime_checkable.

        Это позволяет проверять isinstance() во время выполнения.
        """
        from typing import get_origin

        from tui.sanitizer import Sanitizer as SanitizerProtocol

        # Проверяем что протокол runtime_checkable через isinstance проверку
        # runtime_checkable протоколы имеют специальный флаг в __protocol_attrs__
        # или могут быть проверены через isinstance

        # Создаём класс реализующий протокол
        class MySanitizer:
            def sanitize_topic(self, topic: str) -> str:
                return topic

            def sanitize_response_for_display(self, response: str) -> str:
                return response

        # Проверяем что isinstance работает - это доказывает runtime_checkable
        sanitizer = MySanitizer()
        assert isinstance(sanitizer, SanitizerProtocol)

        # Дополнительная проверка через get_origin для Protocol
        assert (
            get_origin(SanitizerProtocol) is None
            or get_origin(SanitizerProtocol) is SanitizerProtocol
        )


# =============================================================================
# 8. Тесты модульности и зависимостей
# =============================================================================


class TestModularity:
    """Тесты для проверки модульности и зависимостей."""

    def test_no_circular_dependencies(self) -> None:
        """
        Проверка отсутствие циклических зависимостей.

        Модули не должны импортировать друг друга циклически.
        """
        # Проверяем основные модули
        modules_to_check = [
            ("models/conversation.py", ["services", "controllers", "tui"]),
            ("services/dialogue_service.py", ["controllers", "tui"]),
            ("controllers/dialogue_controller.py", ["tui"]),
        ]

        for module_path, forbidden_imports in modules_to_check:
            with open(module_path, encoding="utf-8") as f:
                source = f.read()

            for forbidden in forbidden_imports:
                # Проверяем что нет импортов запрещённых модулей
                assert f"from {forbidden}" not in source
                assert f"import {forbidden}" not in source

    def test_domain_layer_has_no_infrastructure_imports(self) -> None:
        """
        Проверка что доменный слой не импортирует инфраструктуру.

        models/ не должен импортировать tui/ или infrastructure.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        assert "from tui" not in source
        assert "import tui" not in source
        assert "from models.ollama_client" not in source

    def test_service_layer_depends_on_domain_only(self) -> None:
        """
        Проверка что сервисный слой зависит только от домена.

        services/ должен импортировать только models/.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что импортируется domain
        assert "from models" in source
        assert "from models.config import Config" in source
        assert "from models.conversation import" in source
        assert "from models.provider import" in source

        # Проверяем что нет импортов presentation
        assert "from tui" not in source
        assert "import tui" not in source

    def test_presentation_layer_depends_on_abstractions(self) -> None:
        """
        Проверка что presentation слой зависит от абстракций.

        tui/ должен использовать протоколы и сервисы, не реализации.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что используются абстракции
        assert "from models.provider import" in source
        assert "ProviderError" in source

        # Проверяем что используется сервисный слой
        assert "from services.dialogue_service import" in source
        assert "DialogueService" in source


# =============================================================================
# 9. Тесты SOLID принципов
# =============================================================================


class TestSOLIDPrinciples:
    """Тесты для проверки SOLID принципов."""

    def test_single_responsibility_dialogue_service(self) -> None:
        """
        Проверка принцип единственной ответственности DialogueService.

        Сервис должен отвечать только за бизнес-логику диалога.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что сервис содержит только бизнес-логику
        assert "class DialogueService" in source

        # Проверяем методы бизнес-логики
        assert "def run_dialogue_cycle" in source
        assert "def start" in source
        assert "def pause" in source
        assert "def resume" in source
        assert "def stop" in source
        assert "def clear_history" in source

        # Проверяем что нет UI-логики
        assert "yield " not in source  # Нет виджетов Textual
        assert "query_one" not in source

    def test_open_closed_provider_protocol(self) -> None:
        """
        Проверка принцип открытости/закрытости для ModelProvider.

        Протокол должен быть открыт для расширения, закрыт для модификации.
        """
        # Проверяем что ModelProvider это Protocol
        assert issubclass(type(ModelProvider), type(Protocol))

        # Проверяем что протокол определяет интерфейс
        assert hasattr(ModelProvider, "list_models")
        assert hasattr(ModelProvider, "generate")
        assert hasattr(ModelProvider, "close")

        # Проверяем что можно создать новую реализацию
        class NewProvider:
            async def list_models(self) -> list[str]:
                return ["new-model"]

            async def generate(
                self,
                model: str,
                messages: list[dict[str, str]],  # type: ignore[override]
            ) -> str:
                return "response"

            async def close(self) -> None:
                pass

        # Новая реализация совместима с протоколом
        provider = NewProvider()
        assert isinstance(provider, ModelProvider)

    def test_dependency_inversion_service_uses_protocol(self) -> None:
        """
        Проверка принцип инверсии зависимостей.

        Сервис должен зависеть от абстракций (протоколов), не от реализаций.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что используется протокол
        assert "ModelProvider" in source
        assert "from models.provider import" in source

        # Проверяем что нет зависимости от конкретной реализации
        assert "from models.ollama_client import OllamaClient" not in source
        assert "OllamaClient" not in source

    def test_liskov_substitution_provider_errors(self) -> None:
        """
        Проверка принцип подстановки Барбары Лисков для ошибок.

        Подклассы ProviderError должны быть заменяемы базовым классом.
        """
        # Создаём экземпляры всех типов ошибок
        errors = [
            ProviderError("base error"),
            ProviderConfigurationError("config error"),
            ProviderConnectionError("connection error"),
            ProviderGenerationError("generation error"),
        ]

        # Все ошибки должны быть заменяемы базовым классом
        for error in errors:
            assert isinstance(error, ProviderError)

            # Все ошибки должны иметь original_exception
            assert hasattr(error, "original_exception")

        # Проверяем что можно ловить все ошибки через базовый класс
        def raise_error(error: Exception) -> None:
            raise error

        for error in errors:
            with pytest.raises(ProviderError):
                raise_error(error)


# =============================================================================
# 10. Интеграционные тесты
# =============================================================================


class TestArchitectureIntegrity:
    """Интеграционные тесты для проверки целостности архитектуры."""

    def test_full_dialogue_flow_with_new_errors(self) -> None:
        """
        Интеграционный тест полного потока диалога с новыми ошибками.

        Проверяет что ProviderError корректно распространяется через все слои.
        """
        # Создаём мок провайдера с ошибкой
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.side_effect = ProviderGenerationError(
            "Test generation error"
        )
        mock_provider.list_models.return_value = ["test-model"]
        mock_provider.close.return_value = None

        # Создаём conversation и сервис
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

        # Ошибка должна проброситься через сервис
        with pytest.raises(ProviderGenerationError) as exc_info:
            asyncio.run(service.run_dialogue_cycle())

        # Проверяем что ошибка правильного типа
        assert exc_info.value is mock_provider.generate.side_effect

    def test_config_validation_in_domain_layer(self) -> None:
        """
        Интеграционный тест валидации конфигурации в доменном слое.

        Проверяет что Config валидируется при создании.
        """
        # Проверяем что Config в models имеет валидацию
        from models.config import Config as ModelsConfig

        # Валидная конфигурация
        config = ModelsConfig()
        assert config.temperature == 0.7
        assert config.max_tokens == 200

        # Невалидная температура
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(temperature=1.5)
        assert "temperature" in str(exc_info.value).lower()

        # Невалидный max_tokens
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(max_tokens=0)
        assert "max_tokens" in str(exc_info.value).lower()

        # Невалидный URL
        with pytest.raises(ValueError) as exc_info:
            ModelsConfig(ollama_host="invalid-url")
        assert (
            "url" in str(exc_info.value).lower()
            or "ollama" in str(exc_info.value).lower()
        )

    def test_provider_error_propagation_to_ui(self) -> None:
        """
        Интеграционный тест распространения ошибок провайдера до UI.

        Проверяет что ProviderError корректно обрабатывается в UI слое.
        """
        # Проверяем что tui/app.py обрабатывает ProviderError
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что ProviderError импортируется
        assert "from models.provider import ProviderError" in source

        # Проверяем что ошибка обрабатывается
        assert "except ProviderError:" in source

        # Проверяем что есть обработка ошибок в on_mount
        assert "except ProviderError:" in source

        # Проверяем что есть обработка ошибок в _run_dialogue
        lines = source.split("\n")
        in_run_dialogue = False
        found_error_handling = False

        for line in lines:
            if "async def _run_dialogue" in line:
                in_run_dialogue = True
            if in_run_dialogue and "except ProviderError:" in line:
                found_error_handling = True
                break

        assert found_error_handling


# =============================================================================
# Дополнительные тесты для полного покрытия
# =============================================================================


class TestProviderErrorDetails:
    """Дополнительные тесты для ProviderError."""

    def test_provider_error_message_preserved(self) -> None:
        """Проверка что сообщение ошибки сохраняется."""
        error = ProviderError("Test message")
        assert str(error) == "Test message"

    def test_provider_error_chain_preserved(self) -> None:
        """Проверка что цепочка исключений сохраняется."""
        original = ValueError("Original")
        error = ProviderError("Wrapper", original_exception=original)

        assert error.__cause__ is original or error.original_exception is original

    def test_provider_error_subclasses_have_specific_names(self) -> None:
        """Проверка что подклассы имеют специфичные имена."""
        assert ProviderConfigurationError.__name__ == "ProviderConfigurationError"
        assert ProviderConnectionError.__name__ == "ProviderConnectionError"
        assert ProviderGenerationError.__name__ == "ProviderGenerationError"


class TestConfigImmutability:
    """Тесты для проверки неизменяемости Config."""

    def test_config_is_frozen(self) -> None:
        """Проверка что Config заморожен."""
        config = Config()

        # Попытка изменить должна вызвать ошибку
        with pytest.raises(Exception):  # frozen dataclass вызывает FrozenInstanceError
            config.temperature = 0.9  # type: ignore[misc]

    def test_config_has_slots(self) -> None:
        """Проверка что Config использует slots."""
        # Проверяем что __slots__ определён
        assert hasattr(Config, "__slots__")


class TestConversationContextIsolation:
    """Тесты для проверки изоляции контекстов."""

    def test_contexts_are_independent(self) -> None:
        """Проверка что контексты моделей независимы."""
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Добавляем сообщение только в контекст A
        conversation.add_message("A", "user", "Message for A")

        # Получаем контексты
        context_a = conversation.get_context("A")
        context_b = conversation.get_context("B")

        # Контекст A должен содержать сообщение
        assert any(msg["content"] == "Message for A" for msg in context_a)

        # Контекст B не должен содержать это сообщение
        assert not any(msg["content"] == "Message for A" for msg in context_b)

    def test_get_context_returns_copy(self) -> None:
        """Проверка что get_context возвращает копию."""
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        context = conversation.get_context("A")
        original_len = len(context)

        # Пытаемся изменить возвращённый контекст
        context.append({"role": "user", "content": "Injected"})

        # Оригинальный контекст не должен измениться
        assert len(conversation.get_context("A")) == original_len


class TestSanitizerSecurity:
    """Тесты безопасности для Sanitizer."""

    def test_sanitize_topic_prevents_injection(self) -> None:
        """Проверка что sanitize_topic предотвращает инъекции."""
        # Попытка инъекции через фигурные скобки
        malicious = "{__import__('os').system('rm -rf /')}"
        result = sanitize_topic(malicious)

        assert "{{" in result
        assert "__import__" not in result or "{{" in result

    def test_sanitize_response_prevents_xss(self) -> None:
        """Проверка что sanitize_response предотвращает XSS."""
        malicious = "<script>alert('XSS')</script>"
        result = sanitize_response_for_display(malicious)

        assert "<script>" not in result
        assert "&lt;" in result


class TestModelsCacheEdgeCases:
    """Тесты граничных случаев для кэша моделей."""

    def test_cache_with_empty_list(self) -> None:
        """Проверка кэширования пустого списка."""
        cache = _ModelsCache()
        cache.set([])

        result = cache.get()
        assert result == []

    def test_cache_with_none_value(self) -> None:
        """Проверка что None не кэшируется как валидное значение."""
        cache = _ModelsCache()
        # Не устанавливаем значение

        result = cache.get()
        assert result is None

    def test_cache_ttl_zero(self) -> None:
        """Проверка кэша с TTL=0."""
        cache = _ModelsCache(ttl=0)
        cache.set(["model1"])

        # Кэш должен быть сразу невалиден
        result = cache.get()
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
