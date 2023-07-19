from __future__ import annotations

from typing import Any, Awaitable, Callable

L_FUNC = Callable[[], Awaitable[Any]]


class LifespanManager:
    def __init__(self) -> None:
        self._startup_funcs: list[L_FUNC] = []
        self._shutdown_funcs: list[L_FUNC] = []

    def on_startup(self, func: L_FUNC) -> L_FUNC:
        self._startup_funcs.append(func)
        return func

    def on_shutdown(self, func: L_FUNC) -> L_FUNC:
        self._shutdown_funcs.append(func)
        return func

    async def startup(self) -> None:
        if self._startup_funcs:
            for func in self._startup_funcs:
                await func()

    async def shutdown(self) -> None:
        if self._shutdown_funcs:
            for func in self._shutdown_funcs:
                await func()
