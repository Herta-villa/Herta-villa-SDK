from __future__ import annotations

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import Member


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
