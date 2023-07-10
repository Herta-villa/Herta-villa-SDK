from __future__ import annotations

from typing import List

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Emoticon

from pydantic import parse_obj_as


class EmoticonAPIMixin(_BaseAPIMixin):
    async def get_all_emoticon(self) -> list[Emoticon]:
        """获取全量表情

        Returns:
            list[Emoticon]: 表情列表
        """
        return parse_obj_as(
            List[Emoticon],
            (await self.base_request("/getAllEmoticons", "GET"))["list"],
        )
