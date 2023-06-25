from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

from hertavilla.message.image import (
    Image,
    ImageMsgContentInfo,
    image_to_content,
)
from hertavilla.message.post import Post, post_to_content
from hertavilla.message.text import Text, text_to_content
from hertavilla.message.types import MsgContentInfo, _Segment

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot

logger = logging.getLogger("hertavilla.message")


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
        image = []
        posts = []

        for segment in self:
            if isinstance(segment, Image):
                image.append(image_to_content(segment))
            elif isinstance(segment, Post):
                posts.append(post_to_content(segment))
            else:
                text_entities.append(segment)

        if not text_entities:
            if image:
                if posts:
                    logger.warn(
                        "Both Image and Post in the message is not allowed, "
                        "Image has been selected",
                    )
                if len(image) <= 1:
                    return ImageMsgContentInfo(content=image[0]), "MHY:Image"
                logger.warn(
                    "Multiple images will be sent using MHY:Text, "
                    "which will cause the "
                    "images to not be displayed on the web side",
                )
                logger.warn(
                    "Recommend to send the images using multiple times",
                )
                return (
                    await text_to_content([Text("\u200B")], bot, image),
                    "MHY:Text",
                )
            if posts:
                if len(posts) > 1:
                    logger.warn(
                        "Only support one post in one message, "
                        "so use the last one",
                    )
                return posts[-1], "MHY:Post"
            raise ValueError("Message is empty")  # noqa: TRY003
        if image:
            logger.warn(
                "When the image and text exist at the same time, "
                "the message will be sent as MHY:Text, "
                "and the image will not be displayed on the web side",
            )
        if posts:
            logger.warn(
                "When post and text are present at the same time, "
                "the post will not be displayed",
            )
        return await text_to_content(text_entities, bot, image), "MHY:Text"

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
        texts: list[str] = []
        for i, x in enumerate(self):
            space = "" if i == len(self) - 1 else " "
            text = await x.get_text(bot)
            if not isinstance(x, (Text, Image, Post)):
                text += space
            texts.append(text)
        return "".join(texts)

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
