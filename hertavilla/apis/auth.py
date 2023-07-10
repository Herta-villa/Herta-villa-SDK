from __future__ import annotations

from hertavilla.apis.base import _BaseAPIMixin
from hertavilla.model import BotMemberAccessInfo


class AuthAPIMixin(_BaseAPIMixin):
    async def check_member_bot_access_token(
        self,
        token: str,
    ) -> BotMemberAccessInfo:
        """校验用户机器人访问凭证，并返回用户信息

        Args:
            token (str): 用户机器人访问凭证

        Returns:
            BotMemberAccessInfo: 返回数据，包含 token 解析的用户信息 和 用户详细信息
        """  # noqa: E501
        return BotMemberAccessInfo.parse_obj(
            await self.base_request(
                "/checkMemberBotAccessToken",
                "POST",
                data={"token": token},
            ),
        )
