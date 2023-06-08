from __future__ import annotations

import json


class MsgEncoder(json.JSONEncoder):
    def default(self, obj):
        from hertavilla.message import MsgContent

        if isinstance(obj, MsgContent):
            data = obj.__dict__
            for k in data.keys():
                if k.startswith("_"):
                    data.pop(k)
            return data
        return json.JSONEncoder.default(self, obj)
