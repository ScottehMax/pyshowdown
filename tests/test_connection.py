import ssl
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from pyshowdown.connection import Connection


class ConnectionTest(unittest.TestCase):
    def test_init(self):
        conn = Connection("wss://sim3.psim.us/showdown/websocket")
        self.assertEqual(conn.url, "wss://sim3.psim.us/showdown/websocket")
        self.assertIsNone(conn.ws)
        self.assertIsNone(conn.ssl_context)
        self.assertIsNone(conn.session)

    def test_init_with_ssl_context(self):
        ssl_context = ssl.create_default_context()
        conn = Connection("wss://example.com", ssl_context=ssl_context)
        self.assertEqual(conn.url, "wss://example.com")
        self.assertIsNone(conn.ws)
        self.assertEqual(conn.ssl_context, ssl_context)
        self.assertIsNone(conn.session)

    def test_str(self):
        conn = Connection("wss://example.com")
        self.assertEqual(str(conn), "Connection: wss://example.com")

    def test_repr(self):
        conn = Connection("wss://example.com")
        self.assertEqual(repr(conn), "Connection: wss://example.com")


class ConnectionAsyncTest(unittest.IsolatedAsyncioTestCase):
    async def test_connect_without_ssl(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await conn.connect()

        self.assertIsNotNone(conn.session)
        self.assertEqual(conn.ws, mock_ws)
        mock_session.ws_connect.assert_called_once_with("wss://example.com")

    async def test_connect_with_ssl(self):
        ssl_context = ssl.create_default_context()
        conn = Connection("wss://example.com", ssl_context=ssl_context)
        mock_ws = AsyncMock()
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.ws_connect = AsyncMock(return_value=mock_ws)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await conn.connect()

        self.assertIsNotNone(conn.session)
        self.assertEqual(conn.ws, mock_ws)
        mock_session.ws_connect.assert_called_once_with(
            "wss://example.com", ssl=ssl_context
        )

    async def test_connect_failure_closes_session(self):
        conn = Connection("wss://example.com")
        mock_session = MagicMock(spec=aiohttp.ClientSession)
        mock_session.ws_connect = AsyncMock(
            side_effect=aiohttp.ClientError("Connection failed")
        )
        mock_session.close = AsyncMock()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with self.assertRaises(aiohttp.ClientError):
                await conn.connect()

        # Session should be closed and set to None on failure
        mock_session.close.assert_called_once()
        self.assertIsNone(conn.session)

    async def test_send_success(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        conn.ws = mock_ws

        await conn.send("test message")

        mock_ws.send_str.assert_called_once_with("test message")

    async def test_send_not_connected(self):
        conn = Connection("wss://example.com")

        with self.assertRaises(ConnectionError) as context:
            await conn.send("test message")

        self.assertEqual(str(context.exception), "Not connected to server.")

    async def test_receive_success(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        mock_message = MagicMock()
        mock_ws.receive = AsyncMock(return_value=mock_message)
        conn.ws = mock_ws

        result = await conn.receive()

        self.assertEqual(result, mock_message)
        mock_ws.receive.assert_called_once()

    async def test_receive_not_connected(self):
        conn = Connection("wss://example.com")

        with self.assertRaises(ConnectionError) as context:
            await conn.receive()

        self.assertEqual(str(context.exception), "Not connected to server.")

    async def test_close_with_websocket_and_session(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        mock_session = AsyncMock()
        conn.ws = mock_ws
        conn.session = mock_session

        await conn.close()

        mock_ws.close.assert_called_once()
        mock_session.close.assert_called_once()
        self.assertIsNone(conn.ws)
        self.assertIsNone(conn.session)

    async def test_close_with_only_websocket(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        conn.ws = mock_ws

        await conn.close()

        mock_ws.close.assert_called_once()
        self.assertIsNone(conn.ws)

    async def test_close_with_only_session(self):
        conn = Connection("wss://example.com")
        mock_session = AsyncMock()
        conn.session = mock_session

        await conn.close()

        mock_session.close.assert_called_once()
        self.assertIsNone(conn.session)

    async def test_close_when_not_connected(self):
        conn = Connection("wss://example.com")

        # Should not raise an error
        await conn.close()

        self.assertIsNone(conn.ws)
        self.assertIsNone(conn.session)

    async def test_close_handles_websocket_error(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        mock_ws.close = AsyncMock(side_effect=Exception("Close failed"))
        mock_session = AsyncMock()
        conn.ws = mock_ws
        conn.session = mock_session

        # Should not raise an error
        await conn.close()

        # Both should still be set to None despite the error
        self.assertIsNone(conn.ws)
        self.assertIsNone(conn.session)
        mock_session.close.assert_called_once()

    async def test_close_handles_session_error(self):
        conn = Connection("wss://example.com")
        mock_ws = AsyncMock()
        mock_session = AsyncMock()
        mock_session.close = AsyncMock(side_effect=Exception("Close failed"))
        conn.ws = mock_ws
        conn.session = mock_session

        # Should not raise an error
        await conn.close()

        # Both should still be set to None despite the error
        self.assertIsNone(conn.ws)
        self.assertIsNone(conn.session)
        mock_ws.close.assert_called_once()
