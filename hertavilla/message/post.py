from __future__ import annotations

from hertavilla.message.types import (
    MsgContent,
    MsgContentInfo,
    _Segment,
)


# MsgContentInfo for post
class ImageMsgContentInfo(MsgContentInfo):
    content: PostMsgContent


# Segment for post


class Post(_Segment):
    def __init__(self, post_id: str) -> None:
        self.post_id = post_id


# MsgContent for post
class PostMsgContent(MsgContent):
    def __init__(self, post_id: str) -> None:
        self.post_id = post_id


def post_to_content(post: Post) -> ImageMsgContentInfo:
    return {"content": PostMsgContent(post.post_id)}
