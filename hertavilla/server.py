from __future__ import annotations

import asyncio
import json
import logging

from hertavilla.bot import VillaBot
from hertavilla.event import Event, parse_event

from aiohttp import web

background_tasks = set()
bots: dict[str, VillaBot] = {}

logger = logging.getLogger("hertavilla.webhook")


async def _run_handles(event: Event):
    # sourcery skip: raise-from-previous-error
    if bot := bots.get(event.robot.template.id):
        logger.info(
            (
                f"[RECV] {event.__class__.__name__} "
                f"on bot {event.robot.template.name}"
                f"({event.robot.template.id}) "
                f"in villa {event.robot.villa_id}"
            ),
        )
        if bot._bot_info is None:  # noqa: SLF001
            bot.bot_info = event.robot.template
        try:
            task = asyncio.create_task(bot.handle_event(event))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            return web.json_response({"message": "", "retcode": 0})
        except Exception:
            logger.exception("Raised exceptions while handling event.")
            raise web.HTTPInternalServerError(  # noqa: B904, TRY200
                text=json.dumps(
                    {"retcode": -100, "message": "internal error"},
                ),
            )
    logger.warning(
        f"Received event but no bot with id {event.robot.template.id}",
    )
    raise web.HTTPNotFound(
        text=json.dumps(
            {"retcode": 1, "message": "no bot with this id"},
        ),
    )


async def http_handle(request: web.Request):
    if not request.can_read_body:
        raise web.HTTPBadRequest(
            text=json.dumps({"retcode": -2, "message": "body is empty"}),
        )
    try:
        data = await request.json()
        if event_payload := data.get("event", None):
            try:
                event = parse_event(event_payload)
                return await _run_handles(event)
            except ValueError:
                ...
    except json.JSONDecodeError:
        ...
    # 当数据不符合结构时返回 400 Bad Request
    # retcode: -1
    # message: event body is invalid
    logger.warning("Event is invalid")
    raise web.HTTPBadRequest(
        text=json.dumps({"retcode": -1, "message": "event body is invalid"}),
    )


def _start_log(host: str = "0.0.0.0", port: int = 8080):
    logger.info(f"Webhook Server is running on http://{host}:{port}")
    logger.info("Press CTRL + C to stop")


def run(*bots_: VillaBot, host: str = "0.0.0.0", port: int = 8080):
    app = web.Application()
    for bot in bots_:
        bots[bot.bot_id] = bot
        endpoint = bot.callback_endpoint
        app.router.add_post(endpoint, http_handle)
        logger.info(f"Register endpoint {endpoint} for bot {bot.bot_id}")
    _start_log(host, port)
    web.run_app(app, host=host, port=port, print=None)  # type: ignore
