from __future__ import annotations

from typing import List

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Member

from pydantic import parse_obj_as


class MemberAPIMixin(_BaseAPIMixin):
    async def get_member(self, villa_id: int, uid: int) -> Member:
        """获取用户信息

        Args:
            villa_id (int): 大别野 id
            uid (int): 用户 id

        Returns:
            Member: 用户详情
        """
        return Member.parse_obj(
            (
                await self.base_request(
                    "/getMember",
                    "GET",
                    villa_id,
                    params={"uid": uid},
                )
            )["member"],
        )

    async def get_villa_members(
        self,
        villa_id: int,
        offset_str: str = "0",
        size: int = 10,
    ) -> tuple[list[Member], str]:
        """获取大别野成员列表。
        当 offset_str 为空时，返回第一页的成员列表信息；
        当使用本次请求返回值中的`下一页的偏移量起始位置`作为下次请求中的 offset_str 时，会返回下一页的成员列表。

        Args:
            villa_id (int): 大别野 id
            offset_str (str, optional): 起始位置偏移量. Defaults to "0".
            size (int, optional): 分页大小. Defaults to 10.

        Returns:
            tuple[list[Member], str]: 用户信息列表与下一页的偏移量起始位置
        """  # noqa: E501
        data = await self.base_request(
            "/getVillaMembers",
            "GET",
            villa_id,
            params={"offset_str": offset_str, "size": size},
        )
        return (
            parse_obj_as(List[Member], data["list"]),
            data["next_offset_str"],
        )

    async def delete_villa_member(self, villa_id: int, uid: int) -> None:
        """踢出大别野用户

        Args:
            villa_id (int): 大别野 id
            uid (int): 用户 id
        """
        await self.base_request(
            "/deleteVillaMember",
            "POST",
            villa_id,
            data={"uid": uid},
        )
