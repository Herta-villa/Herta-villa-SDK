from __future__ import annotations

from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.aiohttp import AIOHTTPBackend
from hertavilla.server.internal import BaseBackend

DEFAULT_BACKEND = AIOHTTPBackend
_backend: BaseBackend | None = None


def run(
    *bots_: VillaBot,
    host: str = "0.0.0.0",
    port: int = 8080,
    backend_class: type[BaseBackend] = DEFAULT_BACKEND,
    **kwargs: Any,
):
    global _backend  # noqa: PLW0603
    if _backend is None:
        _backend = backend_class(host, port, **kwargs)
    _backend.run(*bots_)


def init_backend(backend: BaseBackend) -> None:
    global _backend  # noqa: PLW0603
    if _backend is not None:
        raise RuntimeError(  # noqa: TRY003
            "Backend has already been initialized",
        )
    _backend = backend


def get_backend() -> BaseBackend:
    if _backend is None:
        raise RuntimeError("Backend isn't initialized")  # noqa: TRY003
    return _backend
