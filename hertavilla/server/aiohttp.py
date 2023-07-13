from __future__ import annotations

import functools
from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.internal import BaseBackend

from aiohttp import web


class AIOHTTPBackend(BaseBackend):
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, **kwargs: Any):
        super().__init__(host, port, **kwargs)
        self._app = web.Application()

    @property
    def app(self) -> web.Application:
        return self._app

    @property
    def name(self) -> str:
        return "AIOHTTP"

    def _start_log(self):
        self.logger.info(
            f"Webhook Server is running on http://{self.host}:{self.port}",
        )
        self.logger.info("Press CTRL + C to stop")

    def run(self, *bots_: VillaBot, host: str = "0.0.0.0", port: int = 8080):
        async def http_handle(request: web.Request):
            resp = await self._run_handles(await request.json())
            return web.json_response(
                {"retcode": resp.retcode, "message": resp.message},
                status=resp.status_code,
            )

        self._register_bots(
            bots_,
            functools.partial(
                self.app.router.add_post,
                handler=http_handle,
            ),  # type: ignore
        )
        self._start_log()
        web.run_app(self.app, host=host, port=port, print=None)  # type: ignore
