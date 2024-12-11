import asyncio
import unittest
from unittest.mock import MagicMock

from hippolyzer.lib.base.events import Event


class TestEvents(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.event = Event()

    async def test_trigger_sync(self):
        mock = MagicMock(return_value=False)
        self.event.subscribe(mock)
        self.event.notify("foo")
        mock.assert_called_with("foo")
        self.assertIn(mock, [x[0] for x in self.event.subscribers])

    async def test_trigger_sync_unsub(self):
        mock = MagicMock(return_value=True)
        self.event.subscribe(mock)
        self.event.notify("foo")
        mock.assert_called_with("foo")
        self.assertNotIn(mock, [x[0] for x in self.event.subscribers])

    async def test_trigger_async(self):
        called = asyncio.Event()
        mock = MagicMock()

        async def _mock_wrapper(*args, **kwargs):
            called.set()
            mock(*args, **kwargs)
        self.event.subscribe(_mock_wrapper)
        self.event.notify("foo")
        await called.wait()
        mock.assert_called_with("foo")
        self.assertIn(_mock_wrapper, [x[0] for x in self.event.subscribers])

    async def test_trigger_async_unsub(self):
        called = asyncio.Event()
        mock = MagicMock()

        async def _mock_wrapper(*args, **kwargs):
            called.set()
            mock(*args, **kwargs)
            return True
        self.event.subscribe(_mock_wrapper)
        self.event.notify("foo")
        await called.wait()
        mock.assert_called_with("foo")
        self.assertNotIn(_mock_wrapper, [x[0] for x in self.event.subscribers])

    async def test_multiple_subscribers(self):
        called = asyncio.Event()
        called2 = asyncio.Event()

        self.event.subscribe(lambda *args: called.set())
        self.event.subscribe(lambda *args: called2.set())

        self.event.notify(None)

        self.assertTrue(called.is_set())
        self.assertTrue(called2.is_set())
