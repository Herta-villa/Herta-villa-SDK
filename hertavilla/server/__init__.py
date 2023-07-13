from __future__ import annotations

from typing import Any

from hertavilla.bot import VillaBot
from hertavilla.server.aiohttp import AIOHTTPBackend
from hertavilla.server.internal import BaseBackend

DEFAULT_BACKEND = AIOHTTPBackend


def run(
    *bots_: VillaBot,
    host: str = "0.0.0.0",
    port: int = 8080,
    backend_class: type[BaseBackend] = DEFAULT_BACKEND,
    **kwargs: Any,
):
    backend = backend_class(host, port, **kwargs)
    backend.run(*bots_)
