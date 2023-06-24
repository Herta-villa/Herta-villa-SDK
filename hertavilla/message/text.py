from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, List, Literal, Optional, cast

# Pydantic:
#   TypeError: You should use `typing_extensions.TypedDict`
#   instead of `typing.TypedDict` with Python < 3.9.2.
#   Without it, there is no way to differentiate
#   required and optional fields when subclassed.
if sys.version_info >= (3, 9, 2):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from hertavilla.message.types import MsgContent, MsgContentInfo, _Segment
from hertavilla.utils import _c

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot

entity_types: dict[str, type["_TextEntity"]] = {}

# MsgContentInfo for text


class TextMsgContentInfo(MsgContentInfo):
    content: TextMsgContent
    mentionedInfo: Optional[MentionedInfo]
    quote: Optional[QuoteInfo]


class QuoteInfo(TypedDict):
    quoted_message_id: str
    """引用消息 id"""

    quoted_message_send_time: str
    """引用消息发送时间戳"""

    original_message_id: str
    """引用树初始消息 id，和 quoted_message_id 保持一致即可"""

    original_message_send_time: str
    """引用树初始消息发送时间戳，和 quoted_message_send_time 保持一致即可"""


class MentionedInfo(TypedDict):
    type: Literal[1, 2]  # noqa: A003
    """提及类型:
    值为1: @全员
    值为2: @部分成员"""

    userIdList: List[str]
    """如果不是提及全员，应该填写被提及的用户 id 列表"""


class EntityDict(TypedDict):
    entity: Any
    length: int
    offset: int


# Segment for text


class _TextEntity(_Segment):
    type_: str

    def __init__(self, **kwargs) -> None:
        ...

    def get_mention(self) -> tuple[Literal[1, 2], str] | None:
        return None

    def __init_subclass__(cls) -> None:
        if cls.__name__ not in {"Text", "Quote"}:
            entity_types[cls.type_] = cls
        return super().__init_subclass__()


class Text(_TextEntity):
    def __init__(self, text: str) -> None:
        self.text = text

    async def get_text(self, _: VillaBot) -> str:
        return self.text

    def __str__(self) -> str:
        return self.text


class VillaRoomLink(_TextEntity):
    type_ = "villa_room_link"

    def __init__(self, villa_id: int, room_id: int) -> None:
        self.villa_id = str(villa_id)
        self.room_id = str(room_id)

    async def get_text(self, bot: VillaBot) -> str:
        room = await bot.get_room(self.villa_id, self.room_id)  # type: ignore
        return f"#{room.room_name}"


class Link(_TextEntity):
    type_ = "link"

    def __init__(self, url: str) -> None:
        self.url = url

    async def get_text(self, _: VillaBot) -> str:
        return self.url


class MentionedRobot(_TextEntity):
    type_ = "mentioned_robot"

    def __init__(self, bot_id: str) -> None:
        self.bot_id = bot_id

    async def get_text(self, bot: VillaBot) -> str:
        # 目前只能 @ 机器人自身，故直接从 bot 处获取名称
        return f"@{bot.name}"

    def get_mention(self) -> tuple[Literal[1, 2], str] | None:
        return 2, self.bot_id


class MentionedUser(_TextEntity):
    type_ = "mentioned_user"

    def __init__(
        self,
        user_id: str,
        _villa_id: int = 0,
    ) -> None:
        self.user_id = user_id
        self._villa_id = _villa_id

    async def get_text(self, bot: VillaBot) -> str:
        member = await bot.get_member(self._villa_id, int(self.user_id))
        return f"@{member.basic.nickname}"

    def get_mention(self) -> tuple[Literal[1, 2], str] | None:
        return 2, self.user_id


class MentionedAll(_TextEntity):
    type_ = "mentioned_all"

    async def get_text(self, _: VillaBot) -> str:
        return "@全体成员"

    def get_mention(self) -> tuple[Literal[1, 2], str] | None:
        return 1, ""


class Quote(_TextEntity):
    def __init__(self, message_id: str, time: int) -> None:
        self.message_id = message_id
        self.time = time

    async def get_text(self, bot: VillaBot) -> str:
        raise NotImplementedError


# MsgContent for text


class TextMsgContent(MsgContent):
    def __init__(self, text: str, entities: list[EntityDict]) -> None:
        self.text = text
        self.entities = entities


async def text_to_content(
    text_entities: list[_TextEntity],
    bot: VillaBot,
) -> TextMsgContentInfo:
    texts: list[str] = []
    entities: list[EntityDict] = []
    mentioned_info: MentionedInfo | None = None
    quote: QuoteInfo | None = None
    offset = 0
    for i, entity in enumerate(text_entities):
        if isinstance(entity, Quote):
            # 存在 Quote Entity 转换成 quote
            message_id = entity.message_id
            time = entity.time
            quote = cast(
                QuoteInfo,
                {
                    "original_message_id": message_id,
                    "original_message_send_time": time,
                    "quoted_message_id": message_id,
                    "quoted_message_send_time": time,
                },
            )
            continue
        # 非文字 entity 尾随空格，最末除外
        space = "" if i == len(text_entities) - 1 else " "
        if isinstance(entity, Text):
            text = str(entity)
            length = len(text)
        else:
            text = f"{await entity.get_text(bot)}{space}"
            length = _c(text)
            entities.append(
                {
                    "entity": {"type": entity.type_, **entity.__dict__},
                    "length": length,
                    "offset": offset,
                },
            )
            if mention := entity.get_mention():
                type_, id_ = mention
                if mentioned_info is None:
                    user_id_list = []
                    mentioned_info = cast(
                        MentionedInfo,
                        {"type": type_, "userIdList": user_id_list},
                    )
                else:
                    if mentioned_info["type"] != 1:
                        mentioned_info["type"] = type_
                    user_id_list = mentioned_info["userIdList"]
                if type_ != 1:
                    user_id_list.append(id_)
        offset += len(text)
        texts.append(text)
    return {
        "content": TextMsgContent("".join(texts), entities),
        "quote": quote,
        "mentionedInfo": mentioned_info,
    }
