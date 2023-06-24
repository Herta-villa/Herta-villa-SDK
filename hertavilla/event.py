# ruff: noqa: A003
from __future__ import annotations

import json
import sys
from typing import Any, List, Literal, Optional, Type

from hertavilla.message import (
    MessageChain,
)
from hertavilla.message.text import (
    EntityDict,
    MentionedInfo,
    QuoteInfo,
    Text,
    entity_types,
)
from hertavilla.utils import _rc

from pydantic import BaseModel, Field, create_model_from_typeddict, validator

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
    commands: List[Command]


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
    created_at: int
    """事件创建时间"""
    id: str
    """事件 id"""
    send_at: int
    """事件回调时间"""

    @property
    def villa_id(self) -> int:
        return self.robot.villa_id

    def __init_subclass__(cls: Type[Self]) -> None:
        super().__init_subclass__()
        literal = cls.__annotations__["type"]
        type_: int = (
            eval(cls.__annotations__["type"])
            if isinstance(literal, str)
            else literal
        ).__args__[
            0
        ]  # 获取类型
        name = cls.__name__.replace("Event", "")  # 获取名称
        events[type_] = cls, name


# JoinVilla


class JoinVillaEvent(Event):
    type: Literal[1]

    join_uid: int
    """用户 id"""
    join_user_nickname: str
    """用户昵称"""
    join_at: int
    """用户加入时间"""


# SendMessage

# why ignore type: https://github.com/pydantic/pydantic/issues/5953
MentionedInfoModel = create_model_from_typeddict(MentionedInfo)  # type: ignore
QuoteInfoModel = create_model_from_typeddict(QuoteInfo)  # type: ignore


class User(BaseModel):
    portrait_uri: str = Field(alias="portraitUri")
    extra: dict
    name: str
    alias: str
    id: str
    portrait: str

    @validator("extra", pre=True)
    def extra_str_to_dict(cls, v: Any):
        return json.loads(v) if isinstance(v, str) else v


class Trace(BaseModel):
    visual_room_version: str
    app_version: str
    action_type: int
    bot_msg_id: str
    client: str
    rong_sdk_version: str


class MessageContent(BaseModel):
    content: MessageChain
    mentioned_info: Optional[MentionedInfoModel] = Field(  # type: ignore
        None,
        alias="mentionedInfo",
    )
    quote: Optional[QuoteInfoModel] = None  # type: ignore
    user: Optional[User] = None
    trace: Optional[Trace] = None

    @validator("content", pre=True)
    def parse_content(cls, v: Any):
        chain = MessageChain()
        text = v["text"].encode("utf-16")
        entities = v["entities"]
        last_offset = 0
        last_length = 0
        end_offset = 0
        for entity in entities:
            entity: EntityDict
            offset = entity["offset"]
            body = entity["entity"]
            type_ = body.pop("type")
            if offset != end_offset:
                # 两个 Entity 偏移相差为文字
                chain.append(
                    Text(text[_rc(end_offset) : _rc(offset)].decode("utf-16")),
                )
            else:
                chain.append(entity_types[type_](**body))
            last_offset = offset
            last_length = entity["length"]
            end_offset = last_offset + last_length
        if _rc(end_offset) != len(text):
            # 最后一个 Entity 之后是文字
            chain.append(
                Text(text[_rc(end_offset) :].decode("utf-16")),
            )
        return chain


class SendMessageEvent(Event):
    type: Literal[2]

    content: MessageContent
    """消息内容"""
    from_user_id: int
    """发送者 id"""
    send_at: int
    """发送时间的时间戳"""
    room_id: int
    """房间 id"""
    object_name: int
    """目前只支持文本类型消息"""
    nickname: str
    """用户昵称"""
    msg_uid: str
    """消息 id"""
    bot_msg_id: Optional[str]
    """如果被回复的消息从属于机器人，则该字段不为空字符串"""

    @validator("content", pre=True)
    def str_to_json(cls, v: Any):
        return json.loads(v)

    @property
    def message(self) -> MessageChain:
        return self.content.content


def parse_event(payload: dict[str, Any]) -> Event:
    type_: int = payload["type"]
    cls_, name = events[type_]
    data = payload["extend_data"]["EventData"][name]
    payload.pop("extend_data")
    payload |= data
    return cls_.parse_obj(payload)
