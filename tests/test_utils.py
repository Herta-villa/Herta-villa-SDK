# ruff: noqa: PLR2004
from __future__ import annotations


def test_utf16_cal():
    from hertavilla.utils import _c, _rc

    assert _c("你好") == 2
    assert _c("😊") == 2

    assert _rc(2) == 6


def test_msg_encoder():
    import json

    from hertavilla.message.types import MsgContent
    from hertavilla.utils import MsgEncoder

    class TestMsgContent(MsgContent):
        def __init__(self) -> None:
            self.test = 1
            self._private = 0

    assert json.loads(json.dumps(TestMsgContent(), cls=MsgEncoder)) == {
        "test": 1,
    }
