from __future__ import annotations

import asyncio
import json

from hertavilla.bot import bots
from hertavilla.event import Event, parse_event

from aiohttp import web

background_tasks = set()


async def _run_handles(event: Event):
    # sourcery skip: raise-from-previous-error
    try:
        if bot := bots.get(event.robot.template.id, None):
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


def run_http():
    app = web.Application()
    app.add_routes([web.post("/", http_handle)])
    web.run_app(app)
