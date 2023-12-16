from __future__ import annotations

import asyncio
import signal
from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server._lifespan import L_FUNC, LifespanManager
from hertavilla.server.internal import BaseBackend

HANDLED_SIGNALS = {
    signal.SIGINT,  # Unix kill -2(CTRL + C)
    signal.SIGTERM,  # Unix kill -15
}


class LoopBackend(BaseBackend):
    def __init__(
        self,
        auto_shutdown: bool = True,
        watch_interval: int = 10,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.should_exit = asyncio.Event()
        self.auto_shutdown = auto_shutdown
        self.watch_interval = watch_interval
        self._lifespan_manager = LifespanManager()

    @property
    def name(self) -> str:
        return "loop"

    @property
    def app(self) -> None:
        return None

    @property
    def lifespan_manager(self) -> LifespanManager:
        return self._lifespan_manager

    async def _loop(self):
        await self.should_exit.wait()

    def _handle_exit(self, sig, frame):
        self.should_exit.set()

    async def _shutdown(self):
        await self.lifespan_manager.shutdown()
        self.task_manager.cancel_all()

    def on_startup(self, func: L_FUNC):
        self.lifespan_manager.on_startup(func)

    def on_shutdown(self, func: L_FUNC):
        self.lifespan_manager.on_shutdown(func)

    async def _run(self, bots_: tuple[VillaBot, ...]):
        await self.lifespan_manager.startup()
        await self._start_ws(bots_)
        if self.auto_shutdown:
            self.task_manager.task_nowait(self._watch_conns)
        await self._loop()
        await self._shutdown()

    async def _watch_conns(self):
        while True:
            if len(self.ws_connections) == 0:
                self.logger.info(
                    "There is no WebSocket connection. Shutdown application.",
                )
                self.should_exit.set()
                break
            await asyncio.sleep(self.watch_interval)

    def run(
        self,
        *bots_: VillaBot,
    ):
        for sig in HANDLED_SIGNALS:
            self.logger.debug(f"Register {sig} handler")
            signal.signal(sig, self._handle_exit)
        asyncio.run(self._run(bots_))
