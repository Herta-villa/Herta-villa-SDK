from __future__ import annotations

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Room


class RoomAPIMixin(_BaseAPIMixin):
    async def get_room(self, villa_id: int, room_id: int) -> Room:
        """获取房间

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id

        Returns:
            Room: 房间信息
        """
        return Room.parse_obj(
            (
                await self.base_request(
                    "/getRoom",
                    "GET",
                    villa_id,
                    params={"room_id": room_id},
                )
            )["room"],
        )
