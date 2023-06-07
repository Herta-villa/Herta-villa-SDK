# ruff: noqa: A003
from __future__ import annotations

from datetime import datetime
import sys
from typing import Any, Literal, Type

from pydantic import BaseModel

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

events: dict[int, tuple[Type["Event"], str]] = {}


class Command(BaseModel):
    name: str
    desc: str


class Template(BaseModel):
    id: str
    name: str
    desc: str
    icon: str
    commands: list[Command]


class Robot(BaseModel):
    """机器人相关信息"""

    template: Template
    """机器人模板信息"""
    villa_id: int
    """事件所属的大别野 id"""


class Event(BaseModel):
    robot: Robot
    """用户机器人访问凭证"""
    type: int
    """事件类型"""
    created_at: datetime
    """事件创建时间"""
    id: str
    """事件 id"""
    send_at: datetime
    """事件回调时间"""

    def __init_subclass__(cls: Type[Self]) -> None:
        super().__init_subclass__()
        type_: int = eval(cls.__annotations__["type"]).__args__[0]  # 获取类型
        name = cls.__name__.replace("Event", "")  # 获取名称
        events[type_] = cls, name


# JoinVilla


class JoinVillaEvent(Event):
    type: Literal[1]

    join_uid: int
    """用户 id"""
    join_user_nickname: str
    """用户昵称"""
    join_at: datetime
    """用户加入时间"""


# SendMessage
class SendMessageEvent(Event):
    type: Literal[2]

    content: str
    """消息内容"""
    from_user_id: int
    """发送者 id"""
    send_at: datetime
    """发送时间的时间戳"""
    room_id: int
    """房间 id"""
    object_name: int
    """目前只支持文本类型消息"""
    nickname: str
    """用户昵称"""
    msg_uid: str
    """消息 id"""
    bot_msg_id: str | None
    """如果被回复的消息从属于机器人，则该字段不为空字符串"""


def parse_event(payload: dict[str, Any]) -> Event:
    type_: int = payload["type"]
    cls_, name = events[type_]
    data = payload["extend_data"]["EventData"][name]
    payload.pop("extend_data")
    payload |= data
    return cls_.parse_obj(payload)


if __name__ == "__main__":
    event = parse_event(
        {
            "event": {
                "robot": {
                    "template": {
                        "id": "bot_ea9d3xxxxxx9",
                        "name": "测试",
                        "desc": "测试机器人",
                        "icon": "",
                        "commands": [{"name": "/重置", "desc": "重置会话"}],
                    },
                    "villa_id": 100001,
                },
                "type": 2,
                "extend_data": {
                    "EventData": {
                        "SendMessage": {
                            "content": "",
                            "from_user_id": 3300034,
                            "send_at": 1683275781450,
                            "object_name": 1,
                            "room_id": 95333,
                            "nickname": "kdodjcoclss",
                            "msg_uid": "C7TC-71AI-KDN8-MS0I",
                        },
                    },
                },
                "created_at": 1683275781450,
                "id": "8ee4c10d-8354-18d7-84df-7e02f034cfd1",
                "send_at": 1683275782,
            },
        }["event"],
    )
    print(event.dict())  # noqa: T201
