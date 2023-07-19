from __future__ import annotations

import functools
from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.internal import BaseBackend

from ._lifespan import L_FUNC, LifespanManager

from aiohttp import web


class AIOHTTPBackend(BaseBackend):
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, **kwargs: Any):
        super().__init__(host, port, **kwargs)
        self._app = web.Application()
        self._lifespan_manager = LifespanManager()

    @property
    def app(self) -> web.Application:
        return self._app

    @property
    def name(self) -> str:
        return "AIOHTTP"

    async def _run_startup(self, _: web.Application):
        await self._lifespan_manager.startup()

    async def _run_shutdown(self, _: web.Application):
        await self._lifespan_manager.shutdown()

    def run(
        self,
        *bots_: VillaBot,
        host: str | None = None,
        port: int | None = None,
    ):
        async def http_handle(request: web.Request):
            resp = await self._run_handles(
                request.headers.get("x-rpc-bot_sign"),
                (await request.text()).strip(),
            )
            return web.json_response(
                {"retcode": resp.retcode, "message": resp.message},
                status=resp.status_code,
            )

        self._register_bots(
            bots_,
            functools.partial(
                self.app.router.add_post,
                handler=http_handle,
            ),
        )
        self.app.on_startup.append(self._run_startup)
        self.app.on_cleanup.append(self._run_shutdown)
        web.run_app(
            self.app,
            host=host or self.host,
            port=port or self.port,
            print=self.logger.info,
        )

    def on_startup(self, func: L_FUNC):
        self._lifespan_manager.on_startup(func)

    def on_shutdown(self, func: L_FUNC):
        self._lifespan_manager.on_shutdown(func)
