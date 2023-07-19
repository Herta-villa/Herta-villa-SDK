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
    **kwargs: Any,
):
    backend = get_backend()
    backend.run(*bots_, host=host, port=port, **kwargs)


def init_backend(
    backend_class: type[BaseBackend] = DEFAULT_BACKEND,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    global _backend  # noqa: PLW0603
    if _backend is not None:
        raise RuntimeError(
            "Backend has already been initialized",
        )
    _backend = backend_class(host, port)


def get_backend() -> BaseBackend:
    if _backend is None:
        raise RuntimeError("Backend isn't initialized")
    return _backend
