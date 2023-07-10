from __future__ import annotations

from typing import List

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Group, GroupRoom, Room

from pydantic import parse_obj_as


class RoomAPIMixin(_BaseAPIMixin):
    async def create_group(self, villa_id: int, group_name: str) -> int:
        """创建分组

        Args:
            villa_id (int): 大别野 id
            group_name (str): 分组名称

        Returns:
            int: 分组 id
        """
        return int(
            (
                await self.base_request(
                    "/createGroup",
                    "POST",
                    villa_id,
                    data={
                        "group_name": group_name,
                    },
                )
            )["group_id"],
        )

    async def edit_group(
        self,
        villa_id: int,
        group_id: int,
        group_name: str,
    ) -> None:
        """编辑分组，只允许编辑分组的名称

        Args:
            villa_id (int): 大别野 id
            group_id (int): 分组 id
            group_name (str): 分组名称
        """
        await self.base_request(
            "/editGroup",
            "POST",
            villa_id,
            data={"group_id": group_id, "group_name": group_name},
        )

    async def delete_group(self, villa_id: int, group_id: int) -> None:
        """删除分组

        Args:
            villa_id (int): 大别野 id
            group_id (int): 分组 id
        """
        await self.base_request(
            "/deleteGroup",
            "POST",
            villa_id,
            data={"group_id": group_id},
        )

    async def get_group_list(self, villa_id: int) -> list[Group]:
        """获取大别野下的所有分组的列表，只返回分组的基本信息，不包含分组内的房间信息。

        Args:
            villa_id (int): 大别野 id

        Returns:
            list[Group]: 分组列表
        """
        return parse_obj_as(
            List[Group],
            (
                await self.base_request(
                    "/getGroupList",
                    "GET",
                    villa_id,
                )
            )["list"],
        )

    async def edit_room(
        self,
        villa_id: int,
        room_id: int,
        room_name: str,
    ) -> None:
        """编辑房间，只允许编辑房间的名称

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id
            room_name (str): 房间名称
        """
        await self.base_request(
            "/editRoom",
            "POST",
            villa_id,
            data={"room_id": room_id, "room_name": room_name},
        )

    async def delete_room(self, villa_id: int, room_id: int) -> None:
        """删除房间

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id
        """
        await self.base_request(
            "/deleteRoom",
            "POST",
            villa_id,
            data={"room_id": room_id},
        )

    async def get_room(self, villa_id: int, room_id: int) -> Room:
        """获取房间信息

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

    async def get_villa_group_room_list(
        self,
        villa_id: int,
    ) -> list[GroupRoom]:
        """获取大别野下的所有分组和房间的列表

        Args:
            villa_id (int): 大别野 id

        Returns:
            list[GroupRoom]: 房间列表
        """
        return parse_obj_as(
            List[GroupRoom],
            (
                await self.base_request(
                    "/getVillaGroupRoomList",
                    "GET",
                    villa_id,
                )
            )["list"],
        )
