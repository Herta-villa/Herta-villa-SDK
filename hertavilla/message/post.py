from __future__ import annotations

from typing import TYPE_CHECKING

from hertavilla.message.types import (
    MsgContent,
    MsgContentInfo,
    _Segment,
)

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot


# MsgContentInfo for post
class ImageMsgContentInfo(MsgContentInfo):
    content: PostMsgContent


# Segment for post


class Post(_Segment):
    def __init__(self, post_id: str) -> None:
        self.post_id = post_id

    async def get_text(self, _: VillaBot) -> str:
        # TODO: 帖子名
        # 米游社的 API 可以获取到，但是需要 DS
        # 感觉加到这里有点臃肿了
        #
        # https://bbs-api.miyoushe.com/post/wapi/semPosts?gids=6&post_id={}
        return "[帖子]"


# MsgContent for post
class PostMsgContent(MsgContent):
    def __init__(self, post_id: str) -> None:
        self.post_id = post_id


def post_to_content(post: Post) -> ImageMsgContentInfo:
    return {"content": PostMsgContent(post.post_id)}
