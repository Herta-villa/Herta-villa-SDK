from __future__ import annotations

import abc
import asyncio
from dataclasses import dataclass
import json
import logging
from typing import Any, Callable, Sequence

from hertavilla.bot import VillaBot
from hertavilla.event import parse_event

from ._lifespan import L_FUNC

background_tasks = set()


@dataclass
class ResponseData:
    status_code: int = 200
    retcode: int = 0
    message: str = ""


INVALID_EVENT = ResponseData(400, -1, "event body is invalid")
VERIFY_FAILED = ResponseData(401, -2, "verify failed")
NO_BOT = ResponseData(404, 1, "no bot with this id")


class BaseBackend(abc.ABC):
    def __init__(self, host: str = "0.0.0.0", port: int = 8080, **kwargs: Any):
        self.host = host
        self.port = port
        self.backend_extra_config = kwargs
        self.bots: dict[str, VillaBot] = {}
        self.logger = logging.getLogger(
            f"hertavilla.backend.{self.name.lower()}",
        )

    @abc.abstractproperty
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractproperty
    def app(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def run(
        self,
        *bots_: VillaBot,
        host: str | None = None,
        port: int | None = None,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def on_startup(self, func: L_FUNC):
        raise NotImplementedError

    @abc.abstractmethod
    def on_shutdown(self, func: L_FUNC):
        raise NotImplementedError

    def _register_bots(
        self,
        bots: Sequence[VillaBot],
        add_router_callback: Callable[[str], Any],
    ) -> None:
        for bot in bots:
            self.bots[bot.bot_id] = bot
            endpoint = bot.callback_endpoint
            add_router_callback(endpoint)
            self.logger.info(
                f"Register endpoint {endpoint} for bot {bot.bot_id}",
            )

    async def _run_handles(
        self,
        sign: str | None,
        body: str,
    ) -> ResponseData:
        payload = json.loads(body)
        if not (event_payload := payload.get("event")):
            self.logger.warning("Event is invalid")
            return INVALID_EVENT
        try:
            event = parse_event(event_payload)
        except ValueError:
            self.logger.warning("Event is invalid")
            return INVALID_EVENT

        if bot := self.bots.get(event.robot.template.id):
            if sign is None or not bot.verify(sign, body):
                logging.warn("Event verify check is failed. Reject handling.")
                return VERIFY_FAILED

            self.logger.info(
                (
                    f"[RECV] {event.__class__.__name__} "
                    f"on bot {event.robot.template.name}"
                    f"({event.robot.template.id}) "
                    f"in villa {event.robot.villa_id}"
                ),
            )
            if bot._bot_info is None:  # noqa: SLF001
                bot.bot_info = event.robot.template
            task = asyncio.create_task(bot.handle_event(event))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            return ResponseData()
        self.logger.warning(
            f"Received event but no bot with id {event.robot.template.id}",
        )
        return NO_BOT
