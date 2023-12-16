from __future__ import annotations

from dataclasses import dataclass
import struct
import sys

from hertavilla.ws.types import BizType, FlagType

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

MAGIC = 0xBABEFACE
HEADER_LEN_V2 = 24
HEADER_LEN_V1 = 20
FIX_HEADER_LEN = 8


@dataclass
class Payload:
    header_len: int
    """消息头长度"""
    id: int  # noqa: A003
    """消息的序号，请求包的ID单调递增，回应包的ID与请求包的ID一致"""
    flag: FlagType
    """消息的方向"""
    biz_type: int
    """消息命令字"""
    app_id: int
    """消息发出方所属的AppId"""

    body: bytes
    """消息的内容"""

    @classmethod
    def new(
        cls,
        biz_type: BizType,
        id_: int,
        app_id: int,
        flag: FlagType,
        data: bytes,
    ) -> Self:
        return cls(
            header_len=HEADER_LEN_V1 if app_id == 0 else HEADER_LEN_V2,
            id=id_,
            flag=flag,
            biz_type=biz_type.value,
            app_id=app_id,
            body=data,
        )

    def to_bytes(self) -> bytes:
        if self.header_len == HEADER_LEN_V2:
            headers = struct.pack(
                "<IQIIi",
                self.header_len,
                self.id,
                self.flag.value,
                self.biz_type,
                self.app_id,
            )
        else:
            headers = struct.pack(
                "<IQII",
                self.header_len,
                self.id,
                self.flag.value,
                self.biz_type,
            )
        changeable = headers + self.body
        return (
            struct.pack(
                "<II",
                MAGIC,
                len(changeable),  # 消息体长度
            )
            + changeable
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        # 解析定长头
        magic, body_len = struct.unpack("<II", data[:8])
        if magic != MAGIC:
            raise ValueError("invalid magic")
        payload_len = FIX_HEADER_LEN + body_len
        if payload_len != len(data):
            raise ValueError(
                "Invalid body length. "
                f"expected length: {payload_len}, actual length: {len(data)}",
            )

        # 解析变长头
        header_start = FIX_HEADER_LEN + 4  # 12
        header_len = struct.unpack(
            "<I",
            data[FIX_HEADER_LEN:header_start],
        )[0]
        if header_len not in (HEADER_LEN_V1, HEADER_LEN_V2):
            raise ValueError("invalid header length")
        body_start = FIX_HEADER_LEN + header_len  # V1: 28, V2: 32
        if header_len == HEADER_LEN_V2:
            id_, flag, biz_type, app_id = struct.unpack(
                "<QIIi",
                data[header_start:body_start],
            )
        else:
            id_, flag, biz_type = struct.unpack(
                "<QII",
                data[header_start:body_start],
            )
            app_id = 0

        body_data = data[body_start:payload_len]

        return cls(
            header_len=header_len,
            id=id_,
            flag=flag,
            biz_type=biz_type,
            app_id=app_id,
            body=body_data,
        )
