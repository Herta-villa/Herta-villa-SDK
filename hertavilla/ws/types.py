from __future__ import annotations

from enum import IntEnum


class BizType(IntEnum):
    UNKNOWN = 0
    EXCHANGE_KEY = 1
    HEARTBEAT = 2
    LOGIN = 3
    LOGOUT = 4
    P_EXCHANGE_KEY = 5
    P_HEARTBEAT = 6
    P_LOGIN = 7
    P_LOGOUT = 8
    KICK_OFF = 51
    SHUTDOWN = 52
    P_KICK_OFF = 53
    ROOM_ENTER = 60
    ROOM_LEAVE = 61
    ROOM_CLOSE = 62
    ROOM_MSG = 63
    EVENT = 30001


class FlagType(IntEnum):
    REQUEST = 1
    RESPONSE = 2
