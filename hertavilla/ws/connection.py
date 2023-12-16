from __future__ import annotations

import asyncio
import logging
import time
from typing import NoReturn

from hertavilla.bot import VillaBot
from hertavilla.event import Event, parse_event
from hertavilla.model import WebSocketInfo
from hertavilla.utils import TaskManager
from hertavilla.ws.package import (
    BIZ_TO_PACK,
    HeartBeat,
    KickOff,
    Login,
    LoginReply,
    Logout,
    LogoutReply,
    Package,
)
from hertavilla.ws.payload import Payload
from hertavilla.ws.pb.model_pb2 import RobotEvent
from hertavilla.ws.types import BizType, FlagType

from aiohttp import ClientError, ClientSession, ClientWebSocketResponse
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("hertavilla.ws.connection")
background_tasks = set()


class StopConnecting(Exception):
    ...


class Reconnect(Exception):
    ...


class WSConn:
    def __init__(
        self,
        bot: VillaBot,
        ws: ClientWebSocketResponse,
        ws_info: WebSocketInfo,
    ):
        self.bot = bot
        self.ws_info = ws_info
        self.ws = ws
        self._id = 0

    async def send(self, pack: Package) -> None:
        logger.debug(f"[{self.bot.bot_id} SEND] {pack!r}")
        data = pack.to_proto()
        payload = Payload.new(
            pack.biz_type,
            self._id,
            self.ws_info['app_id'],
            FlagType.REQUEST,
            data,
        )
        await self.ws.send_bytes(payload.to_bytes())
        self._id += 1

    async def recv(self) -> Package | Event:
        data = await self.ws.receive_bytes()
        payload = Payload.from_bytes(data)

        if payload.biz_type == BizType.EVENT.value:
            # 事件包
            event = parse_event(
                MessageToDict(
                    RobotEvent().FromString(payload.body),
                    preserving_proto_field_name=True,
                    use_integers_for_enums=True,
                ),
            )
            logger.info(
                (
                    f"[RECV] {event.__class__.__name__} "
                    f"on bot {event.robot.template.name}"
                    f"({event.robot.template.id}) "
                    f"in villa {event.robot.villa_id}"
                ),
            )
            return event

        if payload.biz_type in (BizType.SHUTDOWN.value,):
            # 下线进行重连
            raise Reconnect

        pack_cls = BIZ_TO_PACK[payload.biz_type]
        logger.debug(f"[{self.bot.bot_id} RECV RAW] {payload!r}")
        pack = pack_cls.from_proto(payload.body)
        logger.debug(f"[{self.bot.bot_id} RECV] {pack!r}")
        if isinstance(pack, KickOff):
            # 客户端收到 Kickoff 协议表示当前设备已经被踢下线
            # 需要断开连接并且不再重连
            logger.warning(
                f"[{self.bot.bot_id}] Kicked off by server. "
                f"Code: {pack.code}, Reason: {pack.reason}",
            )
            raise StopConnecting
        if isinstance(pack, LogoutReply):
            if pack.code == 0:
                logger.info(f"[{self.bot.bot_id}] Logged out. ")
                raise StopConnecting
            logger.warning(
                f"[{self.bot.bot_id}] Logout failed. ",
                f"Code: {pack.code}, Reason: {pack.msg}",
            )
        return pack


ws_conns: list[WSConn] = []


class WSConnection:
    def __init__(self, bot: VillaBot, owner: set[WSConnection]):
        self.bot = bot
        self.task_manager = TaskManager()
        self.ws_conn: WSConn | None = None
        self.ws_info: WebSocketInfo | None = None
        self.owner = owner
        self.bot.ws = self

    async def connect(self) -> None:
        async with ClientSession() as session:
            self.ws_info = ws_info = await self.bot.get_websocket_info(
                self.bot.test_villa_id,
            )

            while True:
                try:
                    async with session.ws_connect(
                        ws_info["websocket_url"],
                        timeout=30,
                    ) as resp:
                        logging.info(
                            f"[{ws_info['device_id']}] "
                            f"Connected to {ws_info['websocket_url']}",
                        )
                        try:
                            self.ws_conn = ws_conn = WSConn(
                                self.bot,
                                resp,
                                ws_info,
                            )
                            ws_conns.append(ws_conn)
                            is_login = await self._login(ws_conn, ws_info)
                            if not is_login:
                                continue

                            logger.info(
                                f"[{ws_info['device_id']}] Logged in. ",
                            )
                            await self._start_heartbeat()
                            await self.listen_ws(ws_conn)
                        except Reconnect:
                            continue
                except (ClientError, ConnectionError) as e:
                    if self.ws_conn:
                        ws_conns.remove(self.ws_conn)
                        self.ws_conn = None
                    logger.warning(
                        f"Connecting to {ws_info['websocket_url']} "
                        f"failed: {e}, Reconnect in 5 seconds",
                    )
                    await asyncio.sleep(
                        5,
                    )
                except StopConnecting:
                    break
                except Exception:
                    logger.exception(
                        "Unexpected error when connecting to websocket server",
                    )
                finally:
                    if self.ws_conn:
                        ws_conns.remove(self.ws_conn)
                        self.ws_conn = None
                    await self._stop_heartbeat()
        logger.info(f"[{self.bot.bot_id}] Connection is closed.")
        self.bot.ws = None
        self.owner.discard(self)

    async def logout(self) -> None:
        logger.debug(f"[{self.bot.bot_id}] Trying to logout")
        if self.ws_conn and self.ws_info:
            await self.ws_conn.send(
                Logout(
                    int(self.ws_info['uid']),
                    self.ws_info['platform'],
                    self.ws_info['app_id'],
                    self.ws_info['device_id'],
                ),
            )

    async def listen_ws(self, ws: WSConn) -> NoReturn:
        while True:
            pack = await ws.recv()
            if isinstance(pack, Event):
                if self.bot._bot_info is None:  # noqa: SLF001
                    self.bot.bot_info = pack.robot.template
                task = asyncio.create_task(self.bot.handle_event(pack))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)

    async def _heartbeat(self) -> None:
        while self._heartbeat_run:
            try:
                if not self.ws_conn:
                    continue
                await self.ws_conn.send(
                    HeartBeat(client_timestamp=str(int(time.time() * 1000))),
                )
                await asyncio.sleep(20)
            except Exception:
                logger.exception("Unexpected error when sending heartbeat")

    async def _start_heartbeat(self) -> None:
        self._heartbeat_run = True
        logger.debug(f"[{self.bot.bot_id}] Start heartbeat")
        self.task_manager.task_nowait(self._heartbeat)

    async def _stop_heartbeat(self) -> None:
        logger.debug(f"[{self.bot.bot_id}] Stop heartbeat")
        self._heartbeat_run = False
        self.task_manager.cancel_all()

    async def _login(
        self,
        ws: WSConn,
        ws_info: WebSocketInfo,
    ) -> bool:
        logging.debug(f"[{self.bot.bot_id}] Trying to login")
        login = Login(
            uid=int(ws_info['uid']),
            token=f"{self.bot.test_villa_id}.{self.bot.secret_encrypted}.{self.bot.bot_id}",
            platform=ws_info['platform'],
            app_id=ws_info['app_id'],
            device_id=ws_info['device_id'],
        )
        await ws.send(login)
        pack = await ws.recv()
        if not isinstance(pack, LoginReply):
            logger.warning(
                f"[{self.bot.bot_id}] Login failed. "
                "Package type is not LoginReply",
            )
            return False
        if pack.code != 0:
            logger.warning(
                f"[{self.bot.bot_id}] Login failed. "
                f"Code: {pack.code}, Message: {pack.msg}",
            )
            return False
        return True
