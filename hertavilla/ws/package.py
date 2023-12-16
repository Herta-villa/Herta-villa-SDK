from __future__ import annotations

from dataclasses import asdict, dataclass
import sys
from typing import ClassVar

from hertavilla.ws.pb.command_pb2 import (
    PHeartBeat,
    PHeartBeatReply,
    PKickOff,
    PLogin,
    PLoginReply,
    PLogout,
    PLogoutReply,
)
from hertavilla.ws.types import BizType, FlagType

from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.message import Message

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


BIZ_TO_PACK: dict[int, type[Package]] = {}
BIZ_TO_PROTO_REQUEST: dict[int, type[Message]] = {}
BIZ_TO_PROTO_RESPONSE: dict[int, type[Message]] = {}


@dataclass(repr=True)
class Package:
    def __init_subclass__(
        cls,
        pb_stub: type[Message] | None = None,
        flag: FlagType = FlagType.REQUEST,
    ) -> None:
        biz_type = cls.biz_type
        if pb_stub is not None:
            if flag == FlagType.REQUEST:
                BIZ_TO_PROTO_REQUEST[biz_type.value] = pb_stub
            else:
                BIZ_TO_PROTO_RESPONSE[biz_type.value] = pb_stub
        BIZ_TO_PACK[biz_type.value] = cls

    @classmethod
    def from_proto(
        cls,
        data: bytes,
        stub: type[Message] | None = None,
    ) -> Self:
        stub = BIZ_TO_PROTO_RESPONSE.get(cls.biz_type) or stub
        if stub is None:
            raise TypeError("Protobuf stub is not provided")
        return cls(
            **MessageToDict(
                stub().FromString(data),
                preserving_proto_field_name=True,
                use_integers_for_enums=True,
            ),
        )

    biz_type: ClassVar[BizType] = BizType.UNKNOWN

    def to_proto(self, stub: type[Message] | None = None) -> bytes:
        stub = BIZ_TO_PROTO_REQUEST.get(self.biz_type) or stub
        if stub is None:
            raise TypeError("Protobuf stub is not provided")
        return ParseDict(asdict(self), stub()).SerializeToString()


@dataclass(repr=True)
class Login(Package, pb_stub=PLogin):
    uid: int
    """长连接唯一id。使用接口下发参数。"""

    token: str
    """机器人 Websocket 鉴权 token，格式为 {villa_id}.{secret}.{bot_id}。
    机器人未上线时，villa_id 使用测试别野，上线后可传 0"""

    platform: int
    """操作平台枚举。使用接口下发参数。"""

    app_id: int
    """应用标识。使用接口下发参数。"""

    device_id: str
    """唯一标识。使用接口下发参数。"""

    biz_type: ClassVar[BizType] = BizType.P_LOGIN


@dataclass(repr=True)
class LoginReply(Package, pb_stub=PLoginReply, flag=FlagType.RESPONSE):
    server_timestamp: int
    """服务端时间戳，精确到ms"""

    conn_id: int
    """唯一连接ID"""

    code: int = 0
    """非0表示失败，错误码见附录 网关错误码"""

    msg: str = ""
    """错误提示"""

    biz_type: ClassVar[BizType] = BizType.P_LOGIN


@dataclass(repr=True)
class Logout(Package, pb_stub=PLogout):
    uid: int
    """长连接唯一id。使用接口下发参数。"""

    platform: int
    """操作平台枚举。使用接口下发参数。"""

    app_id: int
    """应用标识。使用接口下发参数。"""

    device_id: str
    """唯一标识。使用接口下发参数。"""

    biz_type: ClassVar[BizType] = BizType.P_LOGOUT


@dataclass(repr=True)
class LogoutReply(Package, pb_stub=PLogoutReply, flag=FlagType.RESPONSE):
    conn_id: int
    """唯一连接ID"""

    code: int = 0
    """非0表示失败，错误码见附录 网关错误码"""

    msg: str = ""
    """错误提示"""

    biz_type: ClassVar[BizType] = BizType.P_LOGOUT


@dataclass(repr=True)
class HeartBeat(Package, pb_stub=PHeartBeat):
    client_timestamp: str
    """客户端时间戳，精确到ms"""

    biz_type: ClassVar[BizType] = BizType.P_HEARTBEAT


@dataclass(repr=True)
class HeartBeatReply(Package, pb_stub=PHeartBeatReply, flag=FlagType.RESPONSE):
    server_timestamp: str
    """服务端时间戳，精确到ms"""

    code: int = 0
    """非0表示失败，此时连接是无法感知正常的业务数据包上下行的，遇到失败错误码时应该兜底。"""

    biz_type: ClassVar[BizType] = BizType.P_HEARTBEAT


@dataclass(repr=True)
class KickOff(Package, pb_stub=PKickOff, flag=FlagType.RESPONSE):
    code: int = 0
    """踢出原因状态码"""

    reason: str = ""
    """状态码对应的文案"""

    biz_type: ClassVar[BizType] = BizType.P_KICK_OFF
