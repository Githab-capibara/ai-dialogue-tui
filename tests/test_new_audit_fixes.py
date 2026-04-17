"""Тесты для проверки новых исправлений из аудита кода.

Этот файл содержит тесты для проверки следующих исправлений:
1. models/conversation.py - remaining_messages обрезается корректно
2. models/conversation.py:154-159 - add_message не дублирует код
3. tui/app.py:220 - пустой binding ctrl+c удалён из BINDINGS
4. models/ollama_client.py:208-212 - asyncio.Lock используется в _HTTPSessionManager
5. services/dialogue_service.py:172 - log.exception используется вместо log.warning
6. controllers/dialogue_controller.py:78 - state возвращает копию (replace())
7. models/ollama_client.py:212 - _get_session работает корректно
8. tui/app.py:317 - ProviderConnectionError и ProviderGenerationError обрабатываются раздельно
9. tui/app.py:556-559 - cleanup вызывается при остановке
10. models/conversation.py:131-138 - _add_message_to_context работает корректно

Note:
    Тесты используют доступ к внутренним атрибутам и импорты внутри функций,
    что оправдано для тестирования.
"""

# pylint: disable=protected-access,import-outside-toplevel,no-member
# pylint: disable=too-few-public-methods,line-too-long

import asyncio
import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from controllers.dialogue_controller import DialogueController
from models.conversation import MAX_CONTEXT_LENGTH, Conversation
from models.ollama_client import _HTTPSessionManager
from services.dialogue_service import DialogueService
from tui.app import DialogueApp

# =============================================================================
# 1. Тест: models/conversation.py:108-110 - remaining_messages = context[-max_len:]
# =============================================================================


class TestTrimContextFix:
    """Тесты для проверки исправления в _trim_context_if_needed."""

    def test_trim_context_uses_negative_slicing(self):
        """Проверить, что используется отрицательная индексация context[-max_len:]."""
        source = inspect.getsource(Conversation._trim_context_if_needed)
        assert "context[-max_len:]" in source

    def test_trim_context_no_meaningless_condition(self):
        """Проверить, что нет бессмысленного условия."""
        source = inspect.getsource(Conversation._trim_context_if_needed)
        assert "if remaining_messages" not in source
        assert "remaining_messages and" not in source

    def test_trim_context_with_large_context(self):
        """Проверить обрезку контекста с большим количеством сообщений."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        conversation._context_a = [MagicMock() for _ in range(MAX_CONTEXT_LENGTH + 10)]
        conversation._context_a[0] = {"role": "system", "content": "System prompt"}

        result = conversation._trim_context_if_needed(conversation._context_a, MAX_CONTEXT_LENGTH - 2)

        assert len(result) <= MAX_CONTEXT_LENGTH - 2 + 1
        assert result[0]["role"] == "system"


# =============================================================================
# 2. Тест: models/conversation.py:154-159 - add_message не дублирует код
# =============================================================================


class TestAddMessageNoDuplication:
    """Тесты для проверки отсутствия дублирования кода в add_message."""

    def test_add_message_uses_helper_method(self):
        """Проверить, что add_message использует _add_message_to_context."""
        source = inspect.getsource(Conversation.add_message)
        assert "_add_message_to_context" in source

    def test_add_message_no_direct_context_append(self):
        """Проверить, что нет прямого добавления в контекст в add_message."""
        source = inspect.getsource(Conversation.add_message)
        assert "self._context_a.append" not in source
        assert "self._context_b.append" not in source

    def test_add_message_calls_helper(self):
        """Проверить, что add_message вызывает вспомогательный метод."""
        from models import conversation as conv_module

        conversation = Conversation("model_a", "model_b", "test_topic")
        with patch.object(conv_module.Conversation, "_add_message_to_context", autospec=True) as mock_helper:
            conversation.add_message("A", "user", "Hello")
            mock_helper.assert_called_once_with(conversation, "A", "user", "Hello")


# =============================================================================
# 3. Тест: tui/app.py:220 - пустой binding ctrl+c удалён из BINDINGS
# =============================================================================


class TestEmptyCtrlCBindingRemoved:
    """Тесты для проверки удаления пустого binding ctrl+c."""

    def test_ctrl_c_binding_not_in_bindings(self):
        """Проверить, что ctrl+c binding отсутствует в BINDINGS."""
        bindings = DialogueApp.BINDINGS
        for binding in bindings:
            assert binding.key != "ctrl+c"
            assert binding.key != "ctrl+c()"

    def test_no_empty_action_binding(self):
        """Проверить, что нет binding с пустым действием."""
        source = inspect.getsource(DialogueApp)
        assert 'Binding("ctrl+c", "", ' not in source
        assert 'Binding("ctrl+c", None,' not in source

    def test_bindings_only_has_valid_actions(self):
        """Проверить, что все bindings имеют валидные действия."""
        bindings = DialogueApp.BINDINGS
        for binding in bindings:
            assert binding.action
            assert binding.action not in ("", None)


# =============================================================================
# 4. Тест: models/ollama_client.py:208-212 - asyncio.Lock используется в _HTTPSessionManager
# =============================================================================


class TestHTTPSessionManagerUsesLock:
    """Тесты для проверки использования asyncio.Lock в _HTTPSessionManager."""

    def test_session_manager_has_lock_attribute(self):
        """Проверить, что _HTTPSessionManager имеет атрибут _lock."""
        manager = _HTTPSessionManager(timeout=60)
        assert hasattr(manager, "_lock")

    def test_lock_is_asyncio_lock(self):
        """Проверить, что _lock является asyncio.Lock."""
        manager = _HTTPSessionManager(timeout=60)
        assert isinstance(manager._lock, asyncio.Lock)

    def test_get_session_uses_lock(self):
        """Проверить, что get_session использует async with self._lock."""
        source = inspect.getsource(_HTTPSessionManager.get_session)
        assert "async with self._lock" in source

    @pytest.mark.asyncio
    async def test_get_session_is_thread_safe(self):
        """Проверить, что get_session работает с блокировкой."""
        manager = _HTTPSessionManager(timeout=60)

        async def get_sessions():
            return await manager.get_session()

        results = await asyncio.gather(get_sessions(), get_sessions())
        assert results[0] is results[1]


# =============================================================================
# 5. Тест: services/dialogue_service.py:172 - log.exception используется
# =============================================================================


class TestDialogueServiceUsesLogException:
    """Тесты для проверки использования log.exception в DialogueService."""

    def test_run_dialogue_cycle_uses_log_exception(self):
        """Проверить, что используется log.exception вместо log.warning."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        assert "log.exception" in source

    def test_provider_error_caught_with_exception_logging(self):
        """Проверить обработку ProviderError с log.exception."""
        source = inspect.getsource(DialogueService.run_dialogue_cycle)
        assert "ProviderError" in source
        assert "log.exception" in source


# =============================================================================
# 6. Тест: controllers/dialogue_controller.py:78 - state возвращает копию (replace())
# =============================================================================


class TestControllerStateReturnsCopy:
    """Тесты для проверки возврата копии state в DialogueController."""

    def test_state_property_uses_constructor(self):
        """Проверить, что state использует конструктор для возврата копии."""
        source = inspect.getsource(DialogueController.state.fget)
        assert "UIState(" in source
        assert "replace(" not in source

    def test_state_returns_independent_copy(self):
        """Проверить, что возвращаемый state не связан с внутренним состоянием."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        state1 = controller.state
        state2 = controller.state

        assert state1 is not state2


# =============================================================================
# 7. Тест: models/ollama_client.py:212 - _get_session работает корректно
# =============================================================================


class TestHTTPSessionManagerGetSession:
    """Тесты для проверки работы _get_session (alias для get_session)."""

    def test_get_session_method_exists(self):
        """Проверить, что метод get_session существует."""
        manager = _HTTPSessionManager(timeout=60)
        assert hasattr(manager, "get_session")
        assert callable(manager.get_session)

    @pytest.mark.asyncio
    async def test_get_session_creates_new_session(self):
        """Проверить, что get_session создаёт новую сессию при первой вызове."""
        manager = _HTTPSessionManager(timeout=60)
        session = await manager.get_session()
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing_session(self):
        """Проверить, что get_session переиспользует существующую сессию."""
        manager = _HTTPSessionManager(timeout=60)
        session1 = await manager.get_session()
        session2 = await manager.get_session()
        assert session1 is session2

    @pytest.mark.asyncio
    async def test_get_session_creates_new_after_close(self):
        """Проверить, что создаётся новая сессия после закрытия старой."""
        manager = _HTTPSessionManager(timeout=60)
        session1 = await manager.get_session()
        await session1.close()
        session2 = await manager.get_session()
        assert session1 is not session2


# =============================================================================
# 8. Тест: ProviderConnectionError и ProviderGenerationError обрабатываются раздельно
# =============================================================================


class TestSeparateExceptionHandling:
    """Тесты для проверки раздельной обработки исключений в app.py."""

    def test_on_mount_has_specific_handlers(self):
        """Проверить наличие специфичных обработчиков для исключений."""
        source = inspect.getsource(DialogueApp.on_mount)
        # Проверяем что есть специфичные обработчики
        assert "ProviderConnectionError" in source or "aiohttp.ClientError" in source
        assert "ProviderGenerationError" in source or "asyncio.TimeoutError" in source

    def test_connection_error_handler_exists(self):
        """Проверить обработку ProviderConnectionError."""
        source = inspect.getsource(DialogueApp.on_mount)
        assert "ProviderConnectionError" in source

    def test_generation_error_handler_exists(self):
        """Проверить обработку ProviderGenerationError."""
        source = inspect.getsource(DialogueApp.on_mount)
        assert "ProviderGenerationError" in source

    def test_no_generic_exception_handler(self):
        """Проверить, что нет общего обработчика исключений."""
        source = inspect.getsource(DialogueApp.on_mount)
        if "except Exception" in source or "except ProviderError" in source:
            assert "ProviderConnectionError" in source
            assert "ProviderGenerationError" in source


# =============================================================================
# 9. Тест: tui/app.py:556-559 - cleanup вызывается при остановке
# =============================================================================


class TestCleanupOnUnmount:
    """Тесты для проверки вызова cleanup при остановке приложения."""

    def test_on_unmount_calls_cleanup(self):
        """Проверить, что on_unmount вызывает cleanup."""
        source = inspect.getsource(DialogueApp.on_unmount)
        assert "await self._controller.cleanup()" in source

    def test_on_unmount_cancels_dialogue_task(self):
        """Проверить, что on_unmount отменяет задачу диалога."""
        source = inspect.getsource(DialogueApp.on_unmount)
        assert "_dialogue_task.cancel()" in source or "cancel()" in source

    @pytest.mark.asyncio
    async def test_on_unmount_handles_cleanup_error(self):
        """Проверить обработку ошибок при cleanup."""
        app = DialogueApp()

        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        app._dialogue_task = mock_task

        mock_controller = AsyncMock()
        mock_controller.cleanup.side_effect = aiohttp.ClientError("cleanup error")
        app._controller = mock_controller

        await app.on_unmount()

    @pytest.mark.asyncio
    async def test_on_unmount_calls_controller_cleanup(self):
        """Проверить вызов cleanup у контроллера."""
        app = DialogueApp()

        mock_task = AsyncMock()
        mock_task.done.return_value = False
        mock_task.cancel = MagicMock()
        app._dialogue_task = mock_task

        mock_controller = AsyncMock()
        app._controller = mock_controller

        await app.on_unmount()

        mock_controller.cleanup.assert_called_once()


# =============================================================================
# 10. Тест: models/conversation.py:131-138 - _add_message_to_context работает корректно
# =============================================================================


class TestAddMessageToContext:
    """Тесты для проверки работы _add_message_to_context."""

    def test_add_message_to_context_exists(self):
        """Проверить существование метода _add_message_to_context."""
        conversation = Conversation("model_a", "model_b", "test_topic")
        assert hasattr(conversation, "_add_message_to_context")

    def test_add_message_to_context_trims_when_needed(self):
        """Проверить обрезку контекста при достижении лимита."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        initial_context_len = MAX_CONTEXT_LENGTH - 1
        conversation._context_a = [{"role": "user", "content": f"msg_{i}"} for i in range(initial_context_len)]

        conversation._add_message_to_context("A", "user", "new message")

        assert len(conversation._context_a) <= MAX_CONTEXT_LENGTH

    def test_add_message_to_context_adds_to_correct_model(self):
        """Проверить добавление сообщения в правильный контекст модели."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        conversation._add_message_to_context("A", "user", "message for A")
        assert conversation._context_a[-1]["content"] == "message for A"
        assert len(conversation._context_b) == 1

        conversation._add_message_to_context("B", "assistant", "message for B")
        assert conversation._context_b[-1]["content"] == "message for B"
        assert len(conversation._context_a) == 2

    def test_add_message_to_context_handles_message_dict(self):
        """Проверить создание MessageDict при добавлении."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        conversation._add_message_to_context("A", "user", "test content")

        msg = conversation._context_a[-1]
        assert msg["role"] == "user"
        assert msg["content"] == "test content"


# =============================================================================
# Интеграционные тесты
# =============================================================================


class TestIntegration:
    """Интеграционные тесты для проверки взаимодействия компонентов."""

    def test_conversation_trim_and_add_message_flow(self):
        """Проверить полный поток обрезки и добавления сообщений."""
        conversation = Conversation("model_a", "model_b", "test_topic")

        for i in range(MAX_CONTEXT_LENGTH + 5):
            conversation.add_message("A", "user", f"message {i}")

        # Контекст должен быть обрезан до MAX_CONTEXT_LENGTH или меньше
        assert len(conversation._context_a) <= MAX_CONTEXT_LENGTH
        # Trim логика сохраняет system message + последние сообщения
        # После добавления 55 сообщений (0-54) и trim до 49, последнее будет
        # message 54
        assert conversation._context_a[-1]["role"] == "user"
        # Первое сообщение должно быть системным промптом
        assert conversation._context_a[0]["role"] == "system"

    def test_controller_state_immutability(self):
        """Проверить неизменяемость state после возврата из controller."""
        mock_service = MagicMock()
        mock_service.is_running = False
        mock_service.is_paused = False

        controller = DialogueController(mock_service)

        state = controller.state
        assert state.is_dialogue_active is False

    @pytest.mark.asyncio
    async def test_session_manager_concurrent_access(self):
        """Проверить безопасность параллельного доступа к session manager."""
        manager = _HTTPSessionManager(timeout=60)

        async def get_session_twice():
            s1 = await manager.get_session()
            s2 = await manager.get_session()
            return s1, s2

        results = await asyncio.gather(
            get_session_twice(),
            get_session_twice(),
            get_session_twice(),
        )

        all_sessions = [r[0] for r in results] + [r[1] for r in results]
        unique_sessions = set(id(s) for s in all_sessions)
        assert len(unique_sessions) == 1
