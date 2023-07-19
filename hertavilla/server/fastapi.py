from __future__ import annotations

from contextlib import asynccontextmanager
import functools
from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.internal import BaseBackend

from ._lifespan import L_FUNC, LifespanManager

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError as e:
    raise ImportError(
        "FastAPI Backend isn't installed. Please install extra `fastapi`",
    ) from e


class FastAPIBackend(BaseBackend):
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, **kwargs: Any):
        super().__init__(host, port, **kwargs)
        self._lifespan_manager = LifespanManager()
        self._app = FastAPI(
            lifespan=self.lifespan,
            openapi_url=None,
            docs_url=None,
            include_in_schema=False,
            redoc_url=None,
        )

    @property
    def app(self) -> FastAPI:
        return self._app

    @property
    def name(self) -> str:
        return "FastAPI"

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        await self._lifespan_manager.startup()
        try:
            yield
        finally:
            await self._lifespan_manager.shutdown()

    def run(
        self,
        *bots_: VillaBot,
        host: str | None = None,
        port: int | None = None,
    ):
        async def http_handle(request: Request) -> JSONResponse:
            resp = await self._run_handles(
                request.headers.get("x-rpc-bot_sign"),
                (await request.body()).decode().strip(),
            )
            return JSONResponse(
                {"retcode": resp.retcode, "message": resp.message},
                status_code=resp.status_code,
            )

        self._register_bots(
            bots_,
            functools.partial(
                self.app.add_api_route,
                endpoint=http_handle,
                methods=["POST"],
            ),
        )
        uvicorn.run(
            self.app,
            host=host or self.host,
            port=port or self.port,
            log_config=None,
        )

    def on_startup(self, func: L_FUNC):
        self._lifespan_manager.on_startup(func)

    def on_shutdown(self, func: L_FUNC):
        self._lifespan_manager.on_shutdown(func)
