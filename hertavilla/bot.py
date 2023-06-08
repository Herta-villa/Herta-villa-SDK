from __future__ import annotations

import asyncio
import json
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Literal,
    TypeVar,
)

from hertavilla.exception import raise_exception
from hertavilla.model import BotMemberAccessInfo, Member, Room, Villa
from hertavilla.utils import MsgEncoder

if TYPE_CHECKING:
    from hertavilla.event import Event
    from hertavilla.message import MessageChain, MsgContentInfo


from aiohttp import ClientSession

BASE_API = "https://bbs-api.miyoushe.com/vila/api/bot/platform"

TE = TypeVar("TE", bound="Event")

logger = logging.getLogger("hertavilla.bot")


class VillaBot:
    def __init__(
        self,
        bot_id: str,
        secret: str,
        callback_endpoint: str,
        name: str | None = None,
    ) -> None:
        self.bot_id = bot_id
        self.secret = secret
        self._name = name
        self.callback_endpoint = callback_endpoint
        self.handlers = {}

    @property
    def name(self) -> str | None:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self.name = value

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
        logger.info(f"Calling API {api}.")
        async with ClientSession() as session:
            async with session.request(
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

    async def send_message(
        self,
        villa_id: int,
        room_id: int,
        msg_content_info: "MsgContentInfo",
        object_name: str = "MHY:Text",
    ) -> str:
        """发送消息

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id
            msg_content_info (MsgContentInfo): 消息信息
            object_name (str, optional): 消息类型，目前支持: MHY:Text 文本类型. Defaults to "MHY:Text".

        Returns:
            str: bot_msg_id 机器人所发送消息的唯一标识符
        """  # noqa: E501
        return (
            await self.base_request(
                "/sendMessage",
                "POST",
                villa_id,
                data={
                    "room_id": room_id,
                    "object_name": object_name,
                    "msg_content": json.dumps(
                        msg_content_info,
                        ensure_ascii=False,
                        cls=MsgEncoder,
                    ),
                },
            )
        )["bot_msg_id"]

    async def send(
        self,
        villa_id: int,
        room_id: int,
        chain: "MessageChain",
    ) -> str:
        """通用发送消息方法

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id
            chain (MessageChain): 消息链

        Returns:
            str: bot_msg_id 机器人所发送消息的唯一标识符
        """
        return await self.send_message(
            villa_id,
            room_id,
            await chain.to_content_json(self),
        )

    # event handle
    def listen(
        self,
        event: type[TE],
    ) -> Callable[
        [Callable[[TE, VillaBot], Coroutine[Any, Any, None]]],
        Callable[[TE, VillaBot], Coroutine[Any, Any, None]],
    ]:
        def wrapper(
            func: Callable[[TE, VillaBot], Coroutine[Any, Any, None]],
        ) -> Callable[[TE, VillaBot], Coroutine[Any, Any, None]]:
            self.handlers.setdefault(event.__name__, []).append(func)
            logger.info(f"Registered the handler {func} for {event.__name__}")
            return func

        return wrapper

    async def handle_event(self, event: Event) -> None:
        handlers = self.handlers.get(event.__class__.__name__, [])
        logger.info(f"Handling event for {len(handlers)} handler(s)")
        await asyncio.gather(*[handler(event, self) for handler in handlers])
