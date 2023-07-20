from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass
import logging
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Generic,
    NamedTuple,
    TypeVar,
)
import urllib.parse

from hertavilla.apis.auth import AuthAPIMixin
from hertavilla.apis.img import ImgAPIMixin
from hertavilla.apis.member import MemberAPIMixin
from hertavilla.apis.message import MessageAPIMixin
from hertavilla.apis.role import RoleAPIMixin
from hertavilla.apis.room import RoomAPIMixin
from hertavilla.apis.villa import VillaAPIMixin
from hertavilla.match import Endswith, Keywords, Match, Regex, Startswith

import rsa

if TYPE_CHECKING:
    from hertavilla.event import Command, Event, SendMessageEvent, Template
    from hertavilla.message import MessageChain


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
    temp: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def __eq__(self, __value: Event) -> bool:
        return isinstance(__value, self.event)


class MessageHandler(NamedTuple):
    match: Match
    func: Callable[["SendMessageEvent", VillaBot], Coroutine[Any, Any, None]]
    temp: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def check(self, chain: MessageChain) -> bool:
        return self.match.check(chain)


class VillaBot(
    AuthAPIMixin,
    MemberAPIMixin,
    MessageAPIMixin,
    RoomAPIMixin,
    VillaAPIMixin,
    RoleAPIMixin,
    ImgAPIMixin,
):
    def __init__(
        self,
        bot_id: str,
        secret: str,
        callback_endpoint: str,
        pub_key: str,
        bot_info: "Template" | None = None,
    ) -> None:
        from hertavilla.event import SendMessageEvent

        super().__init__(bot_id, secret, pub_key)
        self.rsa_pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(
            pub_key.encode(),
        )
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

    def verify(
        self,
        sign: str,
        body: str,
    ) -> bool:
        sign_ = base64.b64decode(sign)
        sign_msg = urllib.parse.urlencode(
            {"body": body, "secret": self.secret},
        ).encode()
        try:
            rsa.verify(sign_msg, sign_, self.rsa_pub_key)
        except rsa.VerificationError:
            return False
        else:
            return True

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
        temp: bool = False,
    ):
        self.handlers.append(Handler[TE](event, func, temp))
        logger.info(
            f"Registered the handler {func} "
            f"for {event.__name__} (temp: {temp})",
        )
        return func

    def listen(
        self,
        event: type[TE],
        temp: bool = False,
    ) -> Callable[
        [Callable[[TE, VillaBot], Coroutine[Any, Any, None]]],
        Callable[[TE, VillaBot], Coroutine[Any, Any, None]],
    ]:
        def wrapper(
            func: Callable[[TE, VillaBot], Coroutine[Any, Any, None]],
        ) -> Callable[[TE, VillaBot], Coroutine[Any, Any, None]]:
            self.register_handler(event, func, temp)
            return func

        return wrapper

    async def handle_event(self, event: Event) -> None:
        handlers = list(filter(lambda x: x == event, self.handlers))
        logger.info(f"Handling event {event.__class__.__name__}")
        need_remove_handlers = filter(lambda x: x.temp, handlers)
        try:
            await asyncio.gather(
                *[handler(event, self) for handler in handlers],
            )
        except Exception:
            logger.exception("Raised exceptions while handling event.")
        for handler in need_remove_handlers:
            self.handlers.remove(handler)
            logger.debug(f"Removed handler for {event.__class__.__name__}")

    # message handle
    @staticmethod
    async def message_handler(event: "SendMessageEvent", bot: "VillaBot"):
        handlers = list(
            filter(
                lambda x: x.check(event.message),
                bot.message_handlers,
            ),
        )
        need_remove_handlers = filter(lambda x: x.temp, handlers)
        await asyncio.gather(*[handler(event, bot) for handler in handlers])
        for handler in need_remove_handlers:
            bot.message_handlers.remove(handler)
            logger.debug(f"Removed message handler with {handler.match}")

    def register_msg_handler(
        self,
        match: Match,
        func: MessageHandlerFunc,
        temp: bool = False,
    ):
        self.message_handlers.append(MessageHandler(match, func, temp))
        logger.info(
            f"Registered the handler {func} with {match} (temp: {temp})",
        )
        return func

    def match(
        self,
        match: Match,
        temp: bool = False,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(match, func, temp)
            return func

        return wrapper

    def regex(
        self,
        pattern: str | re.Pattern,
        temp: bool = False,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Regex(pattern), func, temp)
            return func

        return wrapper

    def startswith(
        self,
        prefix: str,
        temp: bool = False,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Startswith(prefix), func, temp)
            return func

        return wrapper

    def endswith(
        self,
        suffix: str,
        temp: bool = False,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Endswith(suffix), func, temp)
            return func

        return wrapper

    def keyword(
        self,
        *keywords: str,
        temp: bool = False,
    ) -> Callable[[MessageHandlerFunc], MessageHandlerFunc]:
        def wrapper(
            func: MessageHandlerFunc,
        ) -> MessageHandlerFunc:
            self.register_msg_handler(Keywords(*keywords), func, temp)
            return func

        return wrapper
