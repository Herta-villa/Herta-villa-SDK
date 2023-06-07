from __future__ import annotations

import json

from hertasdk.models import parse_event

from aiohttp import web


async def hello(request: web.Request):
    if not request.can_read_body:
        raise web.HTTPBadRequest(
            text=json.dumps({"retcode": -2, "message": "body is empty"}),
        )
    try:
        data = await request.json()
        if event_payload := data.get("event", None):
            try:
                event = parse_event(event_payload)  # noqa: F841
                ...
                return web.json_response({"message": "", "retcode": 0})

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


app = web.Application()
app.add_routes([web.post("/", hello)])
web.run_app(app)
