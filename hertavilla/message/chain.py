from __future__ import annotations

from typing import List

from hertavilla.bot import VillaBot
from hertavilla.message.image import Image, image_to_content
from hertavilla.message.post import Post, post_to_content
from hertavilla.message.text import Text, text_to_content
from hertavilla.message.types import MsgContentInfo, _Segment


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
            elif isinstance(segment, Post):  # noqa: RET505
                return post_to_content(segment), "MHY:Post"
            else:
                text_entities.append(segment)
        return await text_to_content(text_entities, bot), "MHY:Text"
