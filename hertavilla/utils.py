from __future__ import annotations

import json


class MsgEncoder(json.JSONEncoder):
    def default(self, obj):
        from hertavilla.message.types import MsgContent

        if isinstance(obj, MsgContent):
            data = obj.__dict__
            for k in data.copy().keys():
                if k.startswith("_"):
                    data.pop(k)
            return data
        return json.JSONEncoder.default(self, obj)


def _c(text: str) -> int:
    return (len(text.encode("utf-16")) // 2) - 1


def _rc(length: int) -> int:
    return (length + 1) * 2
