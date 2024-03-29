"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import builtins
import collections.abc
import google.protobuf.descriptor
import google.protobuf.internal.containers
import google.protobuf.internal.enum_type_wrapper
import google.protobuf.message
import sys
import typing

if sys.version_info >= (3, 10):
    import typing as typing_extensions
else:
    import typing_extensions

DESCRIPTOR: google.protobuf.descriptor.FileDescriptor

class _Command:
    ValueType = typing.NewType("ValueType", builtins.int)
    V: typing_extensions.TypeAlias = ValueType

class _CommandEnumTypeWrapper(google.protobuf.internal.enum_type_wrapper._EnumTypeWrapper[_Command.ValueType], builtins.type):
    DESCRIPTOR: google.protobuf.descriptor.EnumDescriptor
    UNKNOWN: _Command.ValueType  # 0
    EXCHANGE_KEY: _Command.ValueType  # 1
    HEARTBEAT: _Command.ValueType  # 2
    LOGIN: _Command.ValueType  # 3
    LOGOUT: _Command.ValueType  # 4
    P_EXCHANGE_KEY: _Command.ValueType  # 5
    P_HEARTBEAT: _Command.ValueType  # 6
    P_LOGIN: _Command.ValueType  # 7
    P_LOGOUT: _Command.ValueType  # 8
    KICK_OFF: _Command.ValueType  # 51
    SHUTDOWN: _Command.ValueType  # 52
    P_KICK_OFF: _Command.ValueType  # 53
    ROOM_ENTER: _Command.ValueType  # 60
    ROOM_LEAVE: _Command.ValueType  # 61
    ROOM_CLOSE: _Command.ValueType  # 62
    ROOM_MSG: _Command.ValueType  # 63

class Command(_Command, metaclass=_CommandEnumTypeWrapper): ...

UNKNOWN: Command.ValueType  # 0
EXCHANGE_KEY: Command.ValueType  # 1
HEARTBEAT: Command.ValueType  # 2
LOGIN: Command.ValueType  # 3
LOGOUT: Command.ValueType  # 4
P_EXCHANGE_KEY: Command.ValueType  # 5
P_HEARTBEAT: Command.ValueType  # 6
P_LOGIN: Command.ValueType  # 7
P_LOGOUT: Command.ValueType  # 8
KICK_OFF: Command.ValueType  # 51
SHUTDOWN: Command.ValueType  # 52
P_KICK_OFF: Command.ValueType  # 53
ROOM_ENTER: Command.ValueType  # 60
ROOM_LEAVE: Command.ValueType  # 61
ROOM_CLOSE: Command.ValueType  # 62
ROOM_MSG: Command.ValueType  # 63
global___Command = Command

@typing_extensions.final
class PHeartBeat(google.protobuf.message.Message):
    """心跳请求命令字"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CLIENT_TIMESTAMP_FIELD_NUMBER: builtins.int
    client_timestamp: builtins.str
    """客户端时间戳，精确到ms"""
    def __init__(
        self,
        *,
        client_timestamp: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["client_timestamp", b"client_timestamp"]) -> None: ...

global___PHeartBeat = PHeartBeat

@typing_extensions.final
class PHeartBeatReply(google.protobuf.message.Message):
    """心跳返回"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CODE_FIELD_NUMBER: builtins.int
    SERVER_TIMESTAMP_FIELD_NUMBER: builtins.int
    code: builtins.int
    """错误码 非0表示失败"""
    server_timestamp: builtins.int
    """服务端时间戳，精确到ms"""
    def __init__(
        self,
        *,
        code: builtins.int = ...,
        server_timestamp: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["code", b"code", "server_timestamp", b"server_timestamp"]) -> None: ...

global___PHeartBeatReply = PHeartBeatReply

@typing_extensions.final
class PLogin(google.protobuf.message.Message):
    """登录命令"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    @typing_extensions.final
    class MetaEntry(google.protobuf.message.Message):
        DESCRIPTOR: google.protobuf.descriptor.Descriptor

        KEY_FIELD_NUMBER: builtins.int
        VALUE_FIELD_NUMBER: builtins.int
        key: builtins.str
        value: builtins.str
        def __init__(
            self,
            *,
            key: builtins.str = ...,
            value: builtins.str = ...,
        ) -> None: ...
        def ClearField(self, field_name: typing_extensions.Literal["key", b"key", "value", b"value"]) -> None: ...

    UID_FIELD_NUMBER: builtins.int
    TOKEN_FIELD_NUMBER: builtins.int
    PLATFORM_FIELD_NUMBER: builtins.int
    APP_ID_FIELD_NUMBER: builtins.int
    DEVICE_ID_FIELD_NUMBER: builtins.int
    REGION_FIELD_NUMBER: builtins.int
    META_FIELD_NUMBER: builtins.int
    uid: builtins.int
    """长连接侧唯一id，uint64格式"""
    token: builtins.str
    """用于业务后端验证的token"""
    platform: builtins.int
    """客户端操作平台枚举"""
    app_id: builtins.int
    """业务所在客户端应用标识，用于在同一个客户端隔离不同业务的长连接通道。"""
    device_id: builtins.str
    region: builtins.str
    """区域划分字段，通过uid+app_id+platform+region四个字段唯一确定一条长连接"""
    @property
    def meta(self) -> google.protobuf.internal.containers.ScalarMap[builtins.str, builtins.str]:
        """长连内部的扩展字段，是个map"""
    def __init__(
        self,
        *,
        uid: builtins.int = ...,
        token: builtins.str = ...,
        platform: builtins.int = ...,
        app_id: builtins.int = ...,
        device_id: builtins.str = ...,
        region: builtins.str = ...,
        meta: collections.abc.Mapping[builtins.str, builtins.str] | None = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["app_id", b"app_id", "device_id", b"device_id", "meta", b"meta", "platform", b"platform", "region", b"region", "token", b"token", "uid", b"uid"]) -> None: ...

global___PLogin = PLogin

@typing_extensions.final
class PLoginReply(google.protobuf.message.Message):
    """登录命令返回"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CODE_FIELD_NUMBER: builtins.int
    MSG_FIELD_NUMBER: builtins.int
    SERVER_TIMESTAMP_FIELD_NUMBER: builtins.int
    CONN_ID_FIELD_NUMBER: builtins.int
    code: builtins.int
    """错误码 非0表示失败"""
    msg: builtins.str
    """错误信息"""
    server_timestamp: builtins.int
    """服务端时间戳，精确到ms"""
    conn_id: builtins.int
    """唯一连接ID"""
    def __init__(
        self,
        *,
        code: builtins.int = ...,
        msg: builtins.str = ...,
        server_timestamp: builtins.int = ...,
        conn_id: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["code", b"code", "conn_id", b"conn_id", "msg", b"msg", "server_timestamp", b"server_timestamp"]) -> None: ...

global___PLoginReply = PLoginReply

@typing_extensions.final
class PLogout(google.protobuf.message.Message):
    """登出命令字"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    UID_FIELD_NUMBER: builtins.int
    PLATFORM_FIELD_NUMBER: builtins.int
    APP_ID_FIELD_NUMBER: builtins.int
    DEVICE_ID_FIELD_NUMBER: builtins.int
    REGION_FIELD_NUMBER: builtins.int
    uid: builtins.int
    """长连接侧唯一id，uint64格式"""
    platform: builtins.int
    """客户端操作平台枚举"""
    app_id: builtins.int
    """业务所在客户端应用标识，用于在同一个客户端隔离不同业务的长连接通道。"""
    device_id: builtins.str
    """客户端设备唯一标识"""
    region: builtins.str
    """区域划分字段，通过uid+app_id+platform+region四个字段唯一确定一条长连接"""
    def __init__(
        self,
        *,
        uid: builtins.int = ...,
        platform: builtins.int = ...,
        app_id: builtins.int = ...,
        device_id: builtins.str = ...,
        region: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["app_id", b"app_id", "device_id", b"device_id", "platform", b"platform", "region", b"region", "uid", b"uid"]) -> None: ...

global___PLogout = PLogout

@typing_extensions.final
class PLogoutReply(google.protobuf.message.Message):
    """登出命令返回"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CODE_FIELD_NUMBER: builtins.int
    MSG_FIELD_NUMBER: builtins.int
    CONN_ID_FIELD_NUMBER: builtins.int
    code: builtins.int
    """错误码 非0表示失败"""
    msg: builtins.str
    """错误信息"""
    conn_id: builtins.int
    """连接id"""
    def __init__(
        self,
        *,
        code: builtins.int = ...,
        msg: builtins.str = ...,
        conn_id: builtins.int = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["code", b"code", "conn_id", b"conn_id", "msg", b"msg"]) -> None: ...

global___PLogoutReply = PLogoutReply

@typing_extensions.final
class CommonReply(google.protobuf.message.Message):
    """通用返回"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CODE_FIELD_NUMBER: builtins.int
    MSG_FIELD_NUMBER: builtins.int
    code: builtins.int
    """错误码 非0表示失败"""
    msg: builtins.str
    """错误信息"""
    def __init__(
        self,
        *,
        code: builtins.int = ...,
        msg: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["code", b"code", "msg", b"msg"]) -> None: ...

global___CommonReply = CommonReply

@typing_extensions.final
class PKickOff(google.protobuf.message.Message):
    """踢出连接协议"""

    DESCRIPTOR: google.protobuf.descriptor.Descriptor

    CODE_FIELD_NUMBER: builtins.int
    REASON_FIELD_NUMBER: builtins.int
    code: builtins.int
    """踢出原因状态码"""
    reason: builtins.str
    """状态码对应的文案"""
    def __init__(
        self,
        *,
        code: builtins.int = ...,
        reason: builtins.str = ...,
    ) -> None: ...
    def ClearField(self, field_name: typing_extensions.Literal["code", b"code", "reason", b"reason"]) -> None: ...

global___PKickOff = PKickOff
