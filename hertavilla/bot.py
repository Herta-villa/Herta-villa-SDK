from __future__ import annotations

from typing import Any, Literal

from hertavilla.exception import raise_exception
from hertavilla.model import BotMemberAccessInfo, Villa

from aiohttp import ClientSession

BASE_API = "https://bbs-api.miyoushe.com/vila/api/bot/platform"


class VillaBot:
    def __init__(self, bot_id: str, secret: str) -> None:
        self.bot_id = bot_id
        self.secret = secret
        self._session = ClientSession()

    def _make_header(self, villa_id: int) -> dict[str, str]:
        return {
            "x-rpc-bot_id": self.bot_id,
            "x-rpc-bot_secret": self.secret,
            "x-rpc-bot_villa_id": str(villa_id),
        }

    def __repr__(self) -> str:
        return f"<VillaBot id={self.bot_id!r}>"

    def __eq__(self, __value: str | VillaBot) -> bool:
        if isinstance(__value, VillaBot):
            return (
                self.bot_id == __value.bot_id and self.secret == __value.secret
            )
        return self.bot_id == __value

    def __hash__(self) -> int:
        return hash(self.bot_id)

    async def base_request(  # noqa: PLR0913
        self,
        api: str,
        method: Literal["POST"] | Literal["GET"],
        /,
        villa_id: int | None = None,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ):
        async with self._session.request(
            method,
            f"{BASE_API}{api}",
            json=data,
            params=params,
            headers=self._make_header(villa_id) if villa_id else None,
        ) as resp:
            payload = await resp.json()
            raise_exception(payload)
            return payload["data"]

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
                data={"token": self.secret},
            ),
        )

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

    async def close(self) -> None:
        await self._session.close()


if __name__ == "__main__":
    import asyncio

    async def main():
        bot = VillaBot("", "")
        print(await bot.get_villa(1785))  # noqa: T201
        await bot.close()

    asyncio.run(main())
