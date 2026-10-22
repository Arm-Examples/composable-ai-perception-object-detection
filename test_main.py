import asyncio
import importlib
import os
import signal
import unittest
from collections.abc import Awaitable, Callable
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import main


class WorkflowLifetimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_until_sigterm_and_cleans_up(self) -> None:
        await self.assert_runs_until_signal(signal.SIGTERM)

    async def test_runs_until_sigint_and_cleans_up(self) -> None:
        await self.assert_runs_until_signal(signal.SIGINT)

    async def assert_runs_until_signal(self, shutdown_signal: signal.Signals) -> None:
        with patch.dict(os.environ, {"WORKFLOW_DURATION_SECONDS": "0"}):
            importlib.reload(main)

        subscribed = asyncio.Event()
        configuration = object()
        subscription = object()
        camera = SimpleNamespace(
            get_stream_configurations=AsyncMock(return_value=[configuration])
        )
        session = SimpleNamespace(
            topics=SimpleNamespace(results="results"), stop=AsyncMock()
        )
        service = SimpleNamespace(deploy=AsyncMock(return_value=session))
        notifications = AsyncMock()

        async def subscribe(
            topic: str, callback: Callable[[main.Notification], Awaitable[None]]
        ) -> object:
            subscribed.set()
            return subscription

        notifications.subscribe.side_effect = subscribe
        with (
            patch.object(main, "CameraService") as cameras,
            patch.object(main, "PerceptionWorkflow"),
            patch.object(main, "PerceptionService") as perception,
            patch.object(main, "NotificationService") as messaging,
        ):
            cameras.return_value.list_cameras.return_value = [camera]
            perception.connect = AsyncMock(return_value=service)
            messaging.return_value.__aenter__ = AsyncMock(return_value=notifications)
            messaging.return_value.__aexit__ = AsyncMock(return_value=False)
            task = asyncio.create_task(main.main())
            try:
                await asyncio.wait_for(subscribed.wait(), timeout=1)
                await asyncio.sleep(0)
                self.assertFalse(task.done(), "workflow stopped without a signal")
                session.stop.assert_not_awaited()
                os.kill(os.getpid(), shutdown_signal)
                await asyncio.wait_for(task, timeout=1)
                notifications.unsubscribe.assert_awaited_once_with(subscription)
                session.stop.assert_awaited_once_with()
            finally:
                if not task.done():
                    task.cancel()
                    with self.assertRaises(asyncio.CancelledError):
                        await task


if __name__ == "__main__":
    unittest.main()
