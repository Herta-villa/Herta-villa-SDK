# ruff: noqa: A003
from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel


class _BotMemberAccess(BaseModel):
    uid: int
    """用户 id"""

    villa_id: int
    """大别野 id"""

    member_access_token: str
    """用户机器人访问凭证"""

    bot_tpl_id: str
    """机器人模板 id"""


class Role(BaseModel):
    id: str
    """身份组 id"""
    name: str
    """身份组名称"""
    color: str
    """身份组颜色"""
    role_type: str
    """身份组类型"""
    villa_id: str
    """大别野 id"""


class MemberBasic(BaseModel):
    uid: int
    """用户 uid"""

    nickname: str
    """昵称"""

    introduce: str
    """个性签名"""

    avatar: str
    """头像"""
    avatar_url: str
    """"""


class Member(BaseModel):
    basic: MemberBasic
    """用户基本信息"""

    role_id_list: List[int]
    """用户加入的身份组 id 列表"""

    joined_at: str
    """用户加入时间 (ISO8601 timestamp)"""
    role_list: List[Role]


class BotMemberAccessInfo(BaseModel):
    access_info: _BotMemberAccess
    """token 解析的用户信息"""
    member: Member
    """用户详细信息"""


class Villa(BaseModel):
    villa_id: int
    """大别野 id"""

    name: str
    """名称"""

    villa_avatar_url: str
    """别野头像链接"""

    owner_uid: int
    """别野主人 id"""

    is_official: bool
    """是否是官方别野"""

    introduce: str
    """介绍"""

    category_id: int
    """"""

    tags: List[str]
    """标签"""


class RoomType(str, Enum):
    CHAT_ROOM = "BOT_PLATFORM_ROOM_TYPE_CHAT_ROOM"
    """聊天房间"""
    POST_ROOM = "BOT_PLATFORM_ROOM_TYPE_POST_ROOM"
    """帖子房间"""
    SCENE_ROOM = "BOT_PLATFORM_ROOM_TYPE_SCENE_ROOM"
    """场景房间"""
    INVALID = "BOT_PLATFORM_ROOM_TYPE_INVALID"
    """无效"""


class SendMsgAuthRange(BaseModel):
    is_all_send_msg: bool
    """是否全局可发送"""

    roles: List[int]
    """可发消息的身份组 id"""


class Room(BaseModel):
    room_id: int
    """房间 id"""

    room_name: str
    """房间名称"""

    room_type: RoomType
    """房间类型"""

    group_id: int
    """分组 id"""

    room_default_notify_type: str
    """房间默认通知类型"""

    send_msg_auth_range: SendMsgAuthRange
    """房间消息发送权限范围设置"""
