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
    try:
        if bot := bots.get(event.robot.template.id):
            task = asyncio.create_task(bot.handle_event(event))
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            return web.json_response({"message": "", "retcode": 0})
    except Exception:
        raise web.HTTPInternalServerError(  # noqa: B904, TRY200
            text=json.dumps(
                {"retcode": -100, "message": "internal server error"},
            ),
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
    raise web.HTTPBadRequest(
        text=json.dumps({"retcode": -1, "message": "event body is invalid"}),
    )


def run(*bots_: VillaBot, host: str = "0.0.0.0", port: int = 8080):
    app = web.Application()
    for bot in bots_:
        bots[bot.bot_id] = bot
        app.router.add_post(bot.callback_endpoint, http_handle)
    web.run_app(app, host=host, port=port, print=None)  # type: ignore
