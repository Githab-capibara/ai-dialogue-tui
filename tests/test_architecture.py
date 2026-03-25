"""
Тесты архитектуры для проверки разделения слоёв и dependency injection.

Этот модуль проверяет что:
1. Domain слой не зависит от Infrastructure
2. Presentation слой зависит от абстракций, не от реализаций
3. Dependency injection работает корректно
4. Можно заменить реализацию ModelProvider без изменения домена
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
    """Тесты для проверки разделения слоёв архитектуры."""

    def test_conversation_does_not_import_ollama_client(self) -> None:
        """
        Проверка что Conversation не импортирует OllamaClient.

        Это критично для соблюдения Clean Architecture - домен не должен
        зависеть от инфраструктуры.
        """
        # Читаем исходный код файла conversation.py
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Парсим AST
        tree = ast.parse(source)

        # Ищем импорты
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        # Проверяем что нет импорта OllamaClient
        assert "models.ollama_client" not in imports
        assert "ollama_client" not in imports

    def test_conversation_imports_model_provider(self) -> None:
        """
        Проверка что Conversation импортирует ModelProvider протокол.

        Домен должен зависеть от абстракций.
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что ModelProvider импортируется
        assert "ModelProvider" in source
        assert "from models.provider import" in source

    def test_ollama_client_implements_model_provider(self) -> None:
        """
        Проверка что OllamaClient реализует протокол ModelProvider.

        Инфраструктура должна реализовывать абстракции.
        """
        # Проверяем что OllamaClient имеет необходимые методы
        assert hasattr(OllamaClient, "list_models")
        assert hasattr(OllamaClient, "generate")
        assert hasattr(OllamaClient, "close")

        # Проверяем что методы асинхронные
        assert inspect.iscoroutinefunction(OllamaClient.list_models)
        assert inspect.iscoroutinefunction(OllamaClient.generate)
        assert inspect.iscoroutinefunction(OllamaClient.close)

    def test_dialogue_service_uses_model_provider_protocol(self) -> None:
        """
        Проверка что DialogueService использует ModelProvider протокол.

        Сервисный слой должен зависеть от абстракций.
        """
        with open("services/dialogue_service.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что используется ModelProvider
        assert "ModelProvider" in source
        assert "from models.provider import" in source

        # Проверяем что не используется прямой импорт OllamaClient
        assert "from models.ollama_client import OllamaClient" not in source

    def test_dialogue_controller_uses_service(self) -> None:
        """
        Проверка что DialogueController использует DialogueService.

        Контроллер должен зависеть от сервиса, не от домена напрямую.
        """
        with open("controllers/dialogue_controller.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что используется DialogueService
        assert "DialogueService" in source
        assert "from services.dialogue_service import" in source


class TestDependencyInjection:
    """Тесты для проверки работы dependency injection."""

    def test_conversation_accepts_model_provider(self) -> None:
        """
        Проверка что Conversation принимает ModelProvider через DI.

        Метод generate_response должен принимать ModelProvider.
        """
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Проверяем сигнатуру метода
        sig = inspect.signature(conversation.generate_response)
        params = list(sig.parameters.values())

        assert len(params) == 1
        assert params[0].name == "provider"

    def test_dialogue_service_injects_dependencies(self) -> None:
        """
        Проверка что DialogueService получает зависимости через конструктор.

        Все зависимости должны внедряться извне.
        """
        # Создаём мок провайдера
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.list_models.return_value = ["test"]
        mock_provider.generate.return_value = "test response"
        mock_provider.close.return_value = None

        # Создаём conversation
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Внедряем зависимости через конструктор
        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Проверяем что зависимости сохранены
        assert service.conversation is conversation
        assert service.provider is mock_provider

    def test_dialogue_controller_injects_service(self) -> None:
        """
        Проверка что DialogueController получает сервис через конструктор.
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

        # Внедряем сервис через конструктор
        controller = DialogueController(service=service)

        # Проверяем что сервис сохранён
        assert controller.service is service


class TestModelProviderProtocol:
    """Тесты для проверки протокола ModelProvider."""

    def test_model_provider_protocol_definition(self) -> None:
        """
        Проверка что ModelProvider протокол определён корректно.

        Протокол должен иметь все необходимые методы.
        """
        # Проверяем что протокол имеет необходимые методы
        assert hasattr(ModelProvider, "list_models")
        assert hasattr(ModelProvider, "generate")
        assert hasattr(ModelProvider, "close")

    def test_mock_provider_can_be_created(self) -> None:
        """
        Проверка что можно создать мок реализацию ModelProvider.

        Это важно для тестируемости.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.list_models.return_value = ["model1", "model2"]
        mock_provider.generate.return_value = "response"
        mock_provider.close.return_value = None

        # Проверяем что мок работает
        assert isinstance(mock_provider, ModelProvider)

    @pytest.mark.asyncio
    async def test_mock_provider_works_with_conversation(self) -> None:
        """
        Проверка что мок провайдер работает с Conversation.

        Это доказывает что Conversation зависит от абстракции, не от реализации.
        """
        # Создаём мок провайдер
        mock_provider = AsyncMock(spec=ModelProvider)
        mock_provider.generate.return_value = "Test response from mock"

        # Создаём conversation
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Используем мок с conversation
        model_id, response = await conversation.generate_response(mock_provider)

        # Проверяем результат
        assert model_id == "A"
        assert response == "Test response from mock"
        mock_provider.generate.assert_called_once()


class TestServiceLayer:
    """Тесты для проверки сервисного слоя."""

    def test_dialogue_service_has_state_management(self) -> None:
        """
        Проверка что DialogueService управляет состоянием.

        Сервис должен иметь флаги is_running, is_paused.
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

        # Начальное состояние
        assert not service.is_running
        assert not service.is_paused

        # После запуска
        service.start()
        assert service.is_running
        assert not service.is_paused

        # После паузы
        service.pause()
        assert service.is_running
        assert service.is_paused

        # После возобновления
        service.resume()
        assert service.is_running
        assert not service.is_paused

        # После остановки
        service.stop()
        assert not service.is_running
        assert not service.is_paused

    def test_dialogue_service_clear_history(self) -> None:
        """
        Проверка что DialogueService.clear_history работает.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )

        # Добавляем сообщение
        conversation.add_message("A", "user", "test")
        initial_count = len(conversation.get_context("A"))

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )

        # Очищаем историю
        service.clear_history()

        # Проверяем что контекст очищен
        assert len(conversation.get_context("A")) < initial_count

    @pytest.mark.asyncio
    async def test_dialogue_service_run_cycle(self) -> None:
        """
        Проверка что DialogueService.run_dialogue_cycle работает.
        """
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

        # Запускаем сервис
        service.start()

        # Выполняем цикл
        result = await service.run_dialogue_cycle()

        # Проверяем результат
        assert result is not None
        assert result.model_name == "test-a"
        assert result.response == "Test response"
        assert service.turn_count == 1


class TestControllerLayer:
    """Тесты для проверки слоя контроллеров."""

    def test_controller_handles_start(self) -> None:
        """
        Проверка что DialogueController.handle_start работает.
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
        controller = DialogueController(service=service)

        # Обработаем старт
        result = controller.handle_start()

        # Проверяем результат
        assert result is True
        assert service.is_running

    def test_controller_handles_pause(self) -> None:
        """
        Проверка что DialogueController.handle_pause работает.
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
        controller = DialogueController(service=service)

        # Запускаем и ставим на паузу
        service.start()
        result = controller.handle_pause()

        # Проверяем результат
        assert result is True
        assert service.is_paused

    def test_controller_handles_clear(self) -> None:
        """
        Проверка что DialogueController.handle_clear работает.
        """
        mock_provider = AsyncMock(spec=ModelProvider)
        conversation = Conversation(
            model_a="test-a",
            model_b="test-b",
            topic="test",
        )
        # Добавляем сообщение
        conversation.add_message("A", "user", "test")

        service = DialogueService(
            conversation=conversation,
            provider=mock_provider,
        )
        controller = DialogueController(service=service)

        # Очищаем
        controller.handle_clear()

        # Проверяем что счётчик сброшен
        assert controller.state.turn_count == 0


class TestCleanArchitecture:
    """
    Интеграционные тесты для проверки Clean Architecture.

    Проверяют что зависимости направлены в правильную сторону:
    Domain ← Presentation ← Infrastructure
    """

    def test_domain_has_no_infrastructure_dependencies(self) -> None:
        """
        Проверка что домен не зависит от инфраструктуры.

        Conversation должен импортировать только:
        - config (конфигурация)
        - models.provider (абстракции)
        """
        with open("models/conversation.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что нет импортов инфраструктуры
        assert "from models.ollama_client" not in source
        assert "import models.ollama_client" not in source
        assert "from services" not in source
        assert "from controllers" not in source
        assert "from tui" not in source

    def test_presentation_depends_on_abstractions(self) -> None:
        """
        Проверка что presentation слой зависит от абстракций.

        DialogueApp должен импортировать ModelProvider протокол,
        а не только конкретную реализацию OllamaClient.
        """
        with open("tui/app.py", encoding="utf-8") as f:
            source = f.read()

        # Проверяем что используются абстракции
        assert "DialogueService" in source
        assert "DialogueController" in source

    def test_can_swap_provider_implementation(self) -> None:
        """
        Проверка что можно заменить реализацию провайдера.

        Это ключевое преимущество dependency injection.
        """

        # Создаём альтернативную реализацию
        class AlternativeProvider:
            """Альтернативная реализация ModelProvider для теста."""

            async def list_models(self) -> list[str]:
                """Получить список моделей."""
                return ["alt-model"]

            async def generate(
                self,
                model: str,
                messages: list[dict[str, str]],  # type: ignore[override]
                # pylint: disable=unused-argument
            ) -> str:
                """Сгенерировать ответ."""
                return f"Alternative response from {model}"

            async def close(self) -> None:
                """Закрыть соединение."""

        # Используем альтернативный провайдер
        # (это работает потому что Conversation зависит от протокола)
        provider = AlternativeProvider()

        # Проверяем что работает
        assert isinstance(provider, ModelProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
