# ruff: noqa: A003
from __future__ import annotations

from enum import Enum
from typing import List, Optional

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


class MemberRoleType(str, Enum):
    ALL_MEMBER = "MEMBER_ROLE_TYPE_ALL_MEMBER"
    """所有人身份组"""

    ADMIN = "MEMBER_ROLE_TYPE_ADMIN"
    """管理员身份组"""

    OWNER = "MEMBER_ROLE_TYPE_OWNER"
    """大别野房主身份组"""

    CUSTOM = "MEMBER_ROLE_TYPE_CUSTOM"
    """其他自定义身份组"""

    UNKNOWN = "MEMBER_ROLE_TYPE_UNKNOWN"
    """未知"""


class RolePermissionDetail(BaseModel):
    key: str
    """权限 key 字符串"""

    name: str
    """权限名称"""

    describe: str
    """权限描述"""


class Role(BaseModel):
    id: str
    """身份组 id"""

    name: str
    """身份组名称"""

    color: str
    """颜色"""

    villa_id: str
    """所属大别野 id"""

    role_type: MemberRoleType
    """身份组类型"""

    member_num: str
    """身份组下成员数量"""

    permissions: Optional[List[RolePermissionDetail]] = None
    """身份组拥有的权限列表"""

    web_color: str
    """在网页端显示的颜色"""
    font_color: str
    """字体颜色（未知）"""
    bg_color: str
    """背景颜色（未知）"""
    is_all_room: bool
    """是否可以管理所有可见房间"""
    room_ids: List[int]
    """可管理房间 id"""
    color_scheme_id: int


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
    LIVE_ROOM = "BOT_PLATFORM_ROOM_TYPE_LIVE_ROOM"
    """直播房间"""


class SendMsgAuthRange(BaseModel):
    is_all_send_msg: bool
    """是否全局可发送"""

    roles: List[int]
    """可发消息的身份组 id"""


class Group(BaseModel):
    group_id: int
    """分组 id"""

    group_name: str
    """分组名称"""


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


class ListRoom(BaseModel):
    room_id: int
    """房间 id"""

    room_name: str
    """房间名称"""

    room_type: RoomType
    """房间类型"""

    group_id: int
    """分组 id"""


class GroupRoom(BaseModel):
    group_id: int
    """分组 id"""

    group_name: str
    """分组名称"""

    room_list: List[ListRoom]
    """房间信息"""


class RoleColor(str, Enum):
    BLUE = "#6173AB"
    PINK = "#F485D8"
    RED = "#F47884"
    ORANGE = "#FFA54B"
    GREEN = "#7BC26F"
    SKY_BLUE = "#59A1EA"
    PURPLE = "#977EE1"
    # 此颜色为所有人身份组颜色，无法作为创建和编辑身份组的颜色
    LIGHT_BLUE = "#8F9BBF"


class RolePermission(str, Enum):
    MENTION_ALL = "mention_all"
    """@全体全员 - 允许成员能够 @全体成员"""

    RECALL_MESSAGE = "recall_message"
    """撤回消息 - 允许成员能够在聊天房间中撤回任何人的消息"""

    PIN_MESSAGE = "pin_message"
    """置顶消息 - 允许成员能够在聊天房间中置顶消息"""

    MANAGE_MEMBER_ROLE = "manage_member_role"
    """身份组管理 - 允许成员添加、删除身份组，管理身份组成员，修改身份组的权限"""  # noqa: E501

    EDIT_VILLA_INFO = "edit_villa_info"
    """编辑大别野详情 - 允许成员编辑大别野的简介、标签、设置大别野加入条件等"""

    MANAGE_GROUP_AND_ROOM = "manage_group_and_room"
    """房间及分组管理 - 允许成员新建房间，新建/删除房间分组，调整房间及房间分组的排序"""  # noqa: E501

    VILLA_SILENCE = "villa_silence"
    """禁言 - 允许成员能够在房间里禁言其他人"""

    BLACK_OUT = "black_out"
    """拉黑 - 允许成员能够拉黑和将其他人移出大别野"""

    HANDLE_APPLY = "handle_apply"
    """加入审核 - 允许成员审核大别野的加入申请"""

    MANAGE_CHAT_ROOM = "manage_chat_room"
    """聊天房间管理 - 允许成员编辑房间信息及设置可见、发言权限"""

    VIEW_DATA_BOARD = "view_data_board"
    """查看大别野数据 - 允许成员查看大别野数据看板"""

    MANAGE_CUSTOM_EVENT = "manage_custom_event"
    """组织活动 - 允许成员创建活动，编辑活动信息"""

    LIVE_ROOM_ORDER = "live_room_order"
    """点播房间节目 - 允许成员在直播房间中点播节目及控制节目播放"""

    MANAGE_SPOTLIGHT_COLLECTION = "manage_spotlight_collection"
    """设置精选消息 - 允许成员设置、移除精选消息"""


class Emoticon(BaseModel):
    emoticon_id: int
    """表情 id"""

    describe_text: str
    """描述文本"""

    icon: str
    """表情图片链接"""
