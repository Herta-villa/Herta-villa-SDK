from __future__ import annotations

from typing import TYPE_CHECKING, List

from hertavilla.message.image import Image, image_to_content
from hertavilla.message.post import Post, post_to_content
from hertavilla.message.text import Text, text_to_content
from hertavilla.message.types import MsgContentInfo, _Segment

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot


class MessageChain(List[_Segment]):
    def append(self, __object: _Segment | str) -> None:
        if isinstance(__object, str):
            __object = Text(__object)
        super().append(__object)

    async def to_content_json(
        self,
        bot: VillaBot,
    ) -> tuple[MsgContentInfo, str]:
        text_entities = []

        for segment in self:
            if isinstance(segment, Image):
                return image_to_content(segment), "MHY:Image"
            if isinstance(segment, Post):
                return post_to_content(segment), "MHY:Post"
            text_entities.append(segment)
        return await text_to_content(text_entities, bot), "MHY:Text"

    async def get_text(
        self,
        bot: "VillaBot",
    ) -> str:
        """获取文本（每段消息的文本形式）。
        需要注意此函数与 plaintext 不同。

        Args:
            bot (VillaBot): 大别野 Bot

        Returns:
            str: 文本内容
        """
        return "".join([await x.get_text(bot) for x in self])

    @property
    def plaintext(self) -> str:
        """获取纯文本。
        需要注意此属性与 get_text() 不同。

        Returns:
            str: 纯文本内容
        """
        return "".join(map(str, filter(lambda x: isinstance(x, Text), self)))

    def __str__(self) -> str:
        return self.plaintext
