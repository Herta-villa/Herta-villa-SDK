from __future__ import annotations

from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.aiohttp import AIOHTTPBackend
from hertavilla.server.internal import BaseBackend

DEFAULT_BACKEND = AIOHTTPBackend
_backend: BaseBackend | None = None


def run(
    *bots_: VillaBot,
    **kwargs: Any,
):
    backend = get_backend()
    backend.run(*bots_, **kwargs)


def init_backend(
    backend_class: type[BaseBackend] = DEFAULT_BACKEND,
    **kwargs: Any,
) -> None:
    global _backend  # noqa: PLW0603
    if _backend is not None:
        raise RuntimeError(
            "Backend has already been initialized",
        )
    _backend = backend_class(**kwargs)


def get_backend() -> BaseBackend:
    if _backend is None:
        raise RuntimeError("Backend isn't initialized")
    return _backend
