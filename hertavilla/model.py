# ruff: noqa: A003
from __future__ import annotations

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


class Basic(BaseModel):
    uid: str
    """用户 id"""
    nickname: str
    """用户昵称"""
    introduce: str
    """用户简介"""
    avatar: str
    """头像 id"""
    avatar_url: str
    """"""


class Member(BaseModel):
    basic: Basic
    """"""
    role_id_list: list[str]
    """"""
    joined_at: str
    """用户加入大别野时间戳"""
    role_list: list[Role]
    """"""


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

    tags: list[str]
    """标签"""
