from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import logging
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    Literal,
    NamedTuple,
    TypeVar,
)

from hertavilla.exception import raise_exception
from hertavilla.match import Endswith, Keywords, Match, Regex, Startswith
from hertavilla.model import BotMemberAccessInfo, Member, Room, Villa
from hertavilla.utils import MsgEncoder

if TYPE_CHECKING:
    from hertavilla.event import Command, Event, SendMessageEvent, Template
    from hertavilla.message import MessageChain
    from hertavilla.message.types import MsgContentInfo


from aiohttp import ClientSession

BASE_API = "https://bbs-api.miyoushe.com/vila/api/bot/platform"

TE = TypeVar("TE", bound="Event")

MessageHandlerFunc = Callable[
    ["SendMessageEvent", "VillaBot"],
    Coroutine[Any, Any, None],
]

logger = logging.getLogger("hertavilla.bot")


@dataclass
class Handler(Generic[TE]):
    event: type[TE]
    func: Callable[[TE, VillaBot], Coroutine[Any, Any, None]]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def __eq__(self, __value: Event) -> bool:
        return isinstance(__value, self.event)


class MessageHandler(NamedTuple):
    match: Match
    func: Callable[["SendMessageEvent", VillaBot], Coroutine[Any, Any, None]]

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def check(self, chain: MessageChain) -> bool:
        return self.match.check(chain)


class VillaBot:
    def __init__(
        self,
        bot_id: str,
        secret: str,
        callback_endpoint: str,
        bot_info: "Template" | None = None,
    ) -> None:
        from hertavilla.event import SendMessageEvent

        self.bot_id = bot_id
        self.secret = secret
        self._bot_info = bot_info
        self.callback_endpoint = callback_endpoint
        self.handlers: list[Handler] = []
        self.message_handlers: list[MessageHandler] = []
        self.register_handler(SendMessageEvent, self.message_handler)

    @property
    def bot_info(self) -> "Template":
        assert (
            self._bot_info is not None
        ), f"No bot info, maybe bot {self.bot_id} not connected"
        return self._bot_info

    @bot_info.setter
    def bot_info(self, value: "Template") -> None:
        self._bot_info = value

    @property
    def name(self) -> str:
        """Bot 昵称"""
        return self.bot_info.name

    @property
    def avatar(self) -> str:
        """Bot 头像地址"""
        return self.bot_info.icon

    @property
    def commands(self) -> list["Command"]:
        """Bot 预设命令列表"""
        return self.bot_info.commands

    @property
    def description(self) -> str:
        """Bot 介绍"""
        return self.bot_info.desc

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
            *(await chain.to_content_json(self)),
        )

    # event handle

    def register_handler(
        self,
        event: type[TE],
        func: Callable[[TE, VillaBot], Coroutine[Any, Any, None]],
    ):
        self.handlers.append(Handler[TE](event, func))
        logger.info(f"Registered the handler {func} for {event.__name__}")
        return func

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
            self.register_handler(event, func)
            return func

        return wrapper

    async def handle_event(self, event: Event) -> None:
        handlers = filter(lambda x: x == event, self.handlers)
        logger.info(f"Handling event {event.__class__.__name__}")
        await asyncio.gather(*[handler(event, self) for handler in handlers])

    # message handle
    @staticmethod
    async def message_handler(event: "SendMessageEvent", bot: "VillaBot"):
        handlers = filter(
            lambda x: x.check(event.message),
            bot.message_handlers,
        )
        await asyncio.gather(*[handler(event, bot) for handler in handlers])

    def register_msg_handler(self, match: Match, func: MessageHandlerFunc):
        self.message_handlers.append(MessageHandler(match, func))
        logger.info(f"Registered the handler {func} with {match}")
        return func

    def match(
        self,
        match: Match,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(match, func)
            return func

        return wrapper

    def regex(
        self,
        pattern: str | re.Pattern,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Regex(pattern), func)
            return func

        return wrapper

    def startswith(
        self,
        prefix: str,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Startswith(prefix), func)
            return func

        return wrapper

    def endswith(
        self,
        suffix: str,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Endswith(suffix), func)
            return func

        return wrapper

    def keyword(
        self,
        *keywords: str,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Keywords(*keywords), func)
            return func

        return wrapper
