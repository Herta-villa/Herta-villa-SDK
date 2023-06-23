from __future__ import annotations

from typing import TYPE_CHECKING, Optional, TypedDict, cast

from hertavilla.message.types import (
    MsgContent,
    MsgContentInfo,
    _Segment,
)

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot


# MsgContentInfo for image
class ImageMsgContentInfo(MsgContentInfo):
    content: ImageMsgContent


# Segment for image
class Size(TypedDict):
    width: int
    height: int


class Image(_Segment):
    def __init__(
        self,
        url: str,
        width: int | None = None,
        height: int | None = None,
        file_size: int | None = None,
    ) -> None:
        if width is None and height is None:
            self.size = None
        elif width and height:
            self.size = {"width": width, "height": height}
        else:
            raise ValueError(  # noqa: TRY003
                "Parameter width and height are not both None or int",
            )
        self.url = url
        self.file_size = file_size

    async def get_text(self, _: VillaBot) -> str:
        return "[图片]"


# MsgContent for image
class ImageMsgContent(MsgContent):
    def __init__(
        self,
        url: str,
        size: Size | None = None,
        file_size: int | None = None,
    ) -> None:
        self.url = url
        if size:
            self.size = size
        if file_size:
            self.file_size = file_size


def image_to_content(image: Image) -> ImageMsgContentInfo:
    return {
        "content": ImageMsgContent(
            image.url,
            cast(Optional[Size], image.size),
            image.file_size,
        ),
    }
