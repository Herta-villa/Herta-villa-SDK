from __future__ import annotations

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Villa


class VillaAPIMixin(_BaseAPIMixin):
    async def get_villa(self, villa_id: int) -> Villa:
        """获取大别野信息

        Args:
            villa_id (int): 大别野 id

        Returns:
            Villa: 大别野信息
        """
        return Villa.parse_obj(
            (
                await self.base_request(
                    "/getVilla",
                    "GET",
                    villa_id,
                    params={"villa_id": villa_id},
                )
            )["villa"],
        )
