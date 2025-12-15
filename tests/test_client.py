import asyncio
import ssl
import unittest
from unittest.mock import AsyncMock, MagicMock, Mock, patch, call

import aiohttp
import pytest

from pyshowdown.client import Client
from pyshowdown.message import (
    ChatMessage,
    ChallstrMessage,
    InitMessage,
    PMMessage,
    Message,
)
from pyshowdown.plugins.plugin import BasePlugin
from pyshowdown.user import User


class MockPlugin(BasePlugin):
    def __init__(self, client, should_match=True, response_text="response"):
        super().__init__(client)
        self.should_match = should_match
        self.response_text = response_text
        self.match_called = False
        self.response_called = False

    async def match(self, message: Message) -> bool:
        self.match_called = True
        return self.should_match

    async def response(self, message: Message) -> str:
        self.response_called = True
        return self.response_text


class ClientTest(unittest.TestCase):
    def test_init_basic(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        self.assertEqual(client.username, "username")
        self.assertEqual(client.password, "password")
        self.assertEqual(client.login_type, "password")
        self.assertFalse(client.connected)
        self.assertIsNone(client.cookies)
        self.assertEqual(client.plugins, [])
        self.assertEqual(client.rooms, {})
        self.assertFalse(client.logging_in)
        self.assertEqual(client.backoff, 1)

    def test_init_with_oauth(self):
        with patch.object(Client, "load_plugin"):
            client = Client(
                "username", "password", "wss://example.com", login_type="oauth"
            )

        self.assertEqual(client.login_type, "oauth")

    def test_init_with_ssl_context(self):
        ssl_context = ssl.create_default_context()
        with patch.object(Client, "load_plugin"):
            client = Client(
                "username", "password", "wss://example.com", ssl_context=ssl_context
            )

        self.assertEqual(client.conn.ssl_context, ssl_context)

    def test_init_loads_system_plugins(self):
        with patch.object(Client, "load_plugin") as mock_load:
            client = Client("username", "password", "wss://example.com")

        # Should load the 5 system plugins
        self.assertEqual(mock_load.call_count, 5)
        expected_plugins = ["challstr", "init", "deinit", "title", "users"]
        for plugin_name in expected_plugins:
            mock_load.assert_any_call(plugin_name)

    def test_load_plugin_success(self):
        with patch.object(Client, "_load_system_plugins"):
            client = Client("username", "password", "wss://example.com")

        mock_plugin = MagicMock(spec=BasePlugin)
        mock_module = MagicMock()
        mock_module.setup = MagicMock(return_value=[mock_plugin])

        with patch("importlib.import_module", return_value=mock_module):
            result = client.load_plugin("test_plugin")

        self.assertTrue(result)
        self.assertIn(mock_plugin, client.plugins)

    def test_load_plugin_failure(self):
        with patch.object(Client, "_load_system_plugins"):
            client = Client("username", "password", "wss://example.com")

        with patch("importlib.import_module", side_effect=ImportError("Not found")):
            result = client.load_plugin("nonexistent_plugin")

        self.assertFalse(result)

    def test_str(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        self.assertEqual(str(client), "Client(wss://example.com)")

    def test_repr(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        self.assertEqual(repr(client), "Client(wss://example.com)")

    def test_print(self):
        with patch("builtins.print") as mock_print:
            Client.print("test message")

        mock_print.assert_called_once_with("test message")


class ClientAsyncTest(unittest.IsolatedAsyncioTestCase):
    async def test_connect(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.conn.connect = AsyncMock()

        with patch.object(client, "print"):
            await client.connect()

        client.conn.connect.assert_called_once()

    async def test_send(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.queue = asyncio.Queue()

        await client.send("lobby", "Hello!")

        message = await client.queue.get()
        self.assertEqual(message, "lobby|Hello!")

    async def test_send_creates_queue_if_not_exists(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        await client.send("lobby", "Hello!")

        self.assertIsNotNone(client.queue)
        message = await client.queue.get()
        self.assertEqual(message, "lobby|Hello!")

    async def test_send_pm(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.queue = asyncio.Queue()

        await client.send_pm("user", "Hello!")

        message = await client.queue.get()
        self.assertEqual(message, "|/w user, Hello!")

    async def test_receive(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_message = MagicMock()
        client.conn.receive = AsyncMock(return_value=mock_message)

        result = await client.receive()

        self.assertEqual(result, mock_message)

    async def test_join(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.queue = asyncio.Queue()

        await client.join("lobby")

        message = await client.queue.get()
        self.assertEqual(message, "|/join lobby")

    async def test_leave(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.queue = asyncio.Queue()

        await client.leave("lobby")

        message = await client.queue.get()
        self.assertEqual(message, "lobby|/leave")

    async def test_close(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        # Create a mock task
        mock_task = MagicMock()
        mock_task.done = MagicMock(return_value=False)
        mock_task.cancel = MagicMock()
        client._message_queue_task = mock_task

        client.conn.close = AsyncMock()

        with patch("asyncio.gather", new_callable=AsyncMock):
            await client.close()

        mock_task.cancel.assert_called_once()
        client.conn.close.assert_called_once()

    async def test_close_without_queue_task(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.conn.close = AsyncMock()

        await client.close()

        client.conn.close.assert_called_once()

    async def test_close_with_completed_task(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_task = MagicMock()
        mock_task.done = MagicMock(return_value=True)
        client._message_queue_task = mock_task

        client.conn.close = AsyncMock()

        await client.close()

        # Should not cancel already completed task
        mock_task.cancel.assert_not_called()
        client.conn.close.assert_called_once()

    async def test_start_message_queue(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.conn.send = AsyncMock()

        # Start the queue task
        queue_task = asyncio.create_task(client.start_message_queue())

        # Wait a bit for the queue to be created
        await asyncio.sleep(0.01)

        # Send a message
        await client.queue.put("test|message")

        # Wait for processing
        await asyncio.sleep(0.01)

        # Cancel the task
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass

        # Check that send was called
        client.conn.send.assert_called()

    async def test_handle_message_routes_to_plugin(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_plugin = MockPlugin(client, should_match=True, response_text="reply")
        client.plugins = [mock_plugin]
        client.queue = asyncio.Queue()

        with patch.object(client, "print"):
            await client.handle_message("lobby", "|c|@user|hello")

        self.assertTrue(mock_plugin.match_called)
        self.assertTrue(mock_plugin.response_called)

        # Check that response was queued
        queued_message = await client.queue.get()
        self.assertEqual(queued_message, "lobby|reply")

    async def test_handle_message_no_match(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_plugin = MockPlugin(client, should_match=False)
        client.plugins = [mock_plugin]
        client.queue = asyncio.Queue()

        with patch.object(client, "print"):
            await client.handle_message("lobby", "|c|@user|hello")

        self.assertTrue(mock_plugin.match_called)
        self.assertFalse(mock_plugin.response_called)

        # Queue should be empty
        self.assertTrue(client.queue.empty())

    async def test_handle_message_plugin_error(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_plugin = MockPlugin(client, should_match=True)
        mock_plugin.response = AsyncMock(side_effect=Exception("Plugin error"))
        client.plugins = [mock_plugin]

        with patch.object(client, "print"):
            # Should not raise an error
            await client.handle_message("lobby", "|c|@user|hello")

    async def test_handle_message_pm_response(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        mock_plugin = MockPlugin(client, should_match=True, response_text="pm reply")
        client.plugins = [mock_plugin]
        client.queue = asyncio.Queue()

        with patch.object(client, "print"):
            await client.handle_message("", "|pm|@sender|@receiver|hello")

        # Should send PM response
        queued_message = await client.queue.get()
        self.assertEqual(queued_message, "|/w sender, pm reply")

    async def test_handle_message_old_message_no_scrollback(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        # Create a mock room with join_time
        from pyshowdown.room import Room

        room = Room("lobby")
        room.join_time = 2000000000  # Future timestamp
        client.rooms["lobby"] = room

        mock_plugin = MockPlugin(client, should_match=True)
        mock_plugin.scrollback_access = False
        client.plugins = [mock_plugin]

        # Create a message with an old timestamp
        with patch.object(client, "print"):
            await client.handle_message("lobby", "|c:|1000000000|@user|old message")

        # Plugin should not have been called due to old message
        self.assertFalse(mock_plugin.match_called)

    async def test_handle_message_old_message_with_scrollback(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        from pyshowdown.room import Room

        room = Room("lobby")
        room.join_time = 2000000000  # Future timestamp
        client.rooms["lobby"] = room

        mock_plugin = MockPlugin(client, should_match=True)
        mock_plugin.scrollback_access = True  # Plugin has scrollback access
        client.plugins = [mock_plugin]
        client.queue = asyncio.Queue()

        with patch.object(client, "print"):
            await client.handle_message("lobby", "|c:|1000000000|@user|old message")

        # Plugin should have been called despite old message
        self.assertTrue(mock_plugin.match_called)

    async def test_receive_forever_processes_messages(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        # Create mock websocket messages
        mock_msg1 = MagicMock()
        mock_msg1.type = aiohttp.WSMsgType.TEXT
        mock_msg1.data = ">lobby\n|c|@user|hello"

        mock_msg2 = MagicMock()
        mock_msg2.type = aiohttp.WSMsgType.CLOSED
        mock_msg2.data = ""

        mock_ws = MagicMock()
        mock_ws.__aiter__.return_value = [mock_msg1, mock_msg2]

        client.conn.ws = mock_ws
        client.conn.close = AsyncMock()
        client.handle_message = AsyncMock()

        await client.receive_forever()

        # Should handle the message
        client.handle_message.assert_called()
        client.conn.close.assert_called_once()
        self.assertFalse(client.connected)

    async def test_receive_forever_not_connected(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        with self.assertRaises(ConnectionError):
            await client.receive_forever()

    async def test_receive_forever_splits_multiple_messages(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        # Multiple messages in one websocket message
        mock_msg1 = MagicMock()
        mock_msg1.type = aiohttp.WSMsgType.TEXT
        mock_msg1.data = ">lobby\n|c|@user|hello\n|c|@user2|world"

        mock_msg2 = MagicMock()
        mock_msg2.type = aiohttp.WSMsgType.CLOSED
        mock_msg2.data = ""

        mock_ws = MagicMock()
        mock_ws.__aiter__.return_value = [mock_msg1, mock_msg2]

        client.conn.ws = mock_ws
        client.conn.close = AsyncMock()
        client.handle_message = AsyncMock()

        await client.receive_forever()

        # Should handle both messages
        self.assertEqual(client.handle_message.call_count, 2)

    async def test_receive_forever_global_room(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        # Message without room prefix
        mock_msg1 = MagicMock()
        mock_msg1.type = aiohttp.WSMsgType.TEXT
        mock_msg1.data = "|challstr|test"

        mock_msg2 = MagicMock()
        mock_msg2.type = aiohttp.WSMsgType.CLOSED
        mock_msg2.data = ""

        mock_ws = MagicMock()
        mock_ws.__aiter__.return_value = [mock_msg1, mock_msg2]

        client.conn.ws = mock_ws
        client.conn.close = AsyncMock()
        client.handle_message = AsyncMock()

        await client.receive_forever()

        # Should handle message with empty room
        client.handle_message.assert_called_with("", "|challstr|test")

    async def test_keep_connected_connects_and_receives(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.connect = AsyncMock()
        client.start_message_queue = AsyncMock()

        # Make receive_forever raise an exception to break the loop
        call_count = 0

        async def mock_receive_forever():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call succeeds but throws to break loop
                raise asyncio.CancelledError()

        client.receive_forever = AsyncMock(side_effect=mock_receive_forever)

        # Mock asyncio.sleep to speed up test
        original_sleep = asyncio.sleep

        async def mock_sleep(delay):
            await original_sleep(0.001)  # Sleep very briefly instead of full backoff

        # Run keep_connected with mocked sleep
        with patch("asyncio.sleep", side_effect=mock_sleep):
            task = asyncio.create_task(client.keep_connected())
            # Wait using the original sleep, not the mocked one
            await original_sleep(0.1)  # Give it time to run
            task.cancel()

            try:
                await task
            except asyncio.CancelledError:
                pass

        # Should have tried to connect
        self.assertGreaterEqual(client.connect.call_count, 1)
        client.start_message_queue.assert_called_once()

    async def test_keep_connected_retries_on_failure(self):
        with patch.object(Client, "load_plugin"):
            client = Client("username", "password", "wss://example.com")

        client.connect = AsyncMock(side_effect=Exception("Connection failed"))
        client.start_message_queue = AsyncMock()
        client.print = MagicMock()  # Mock print to avoid output

        # Mock asyncio.sleep to speed up test
        original_sleep = asyncio.sleep
        sleep_call_count = 0

        async def mock_sleep(delay):
            nonlocal sleep_call_count
            sleep_call_count += 1
            # Only actually sleep for the first few calls
            if sleep_call_count < 3:
                await original_sleep(0.001)
            else:
                # After 2 retries, raise to exit the test
                raise asyncio.CancelledError()

        # Run keep_connected with mocked sleep
        with patch("asyncio.sleep", side_effect=mock_sleep):
            task = asyncio.create_task(client.keep_connected())

            try:
                await task
            except asyncio.CancelledError:
                pass

        # Should have tried multiple times
        self.assertGreaterEqual(client.connect.call_count, 2)
        # Backoff should have increased
        self.assertGreaterEqual(client.backoff, 2)
