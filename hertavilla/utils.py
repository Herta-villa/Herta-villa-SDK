from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from aiohttp import (
    BytesPayload,
    FormData,
    MultipartWriter,
    Payload,
    StringPayload,
    hdrs,
)

task_logger = logging.getLogger("hertavilla.asyncio.task")


class MsgEncoder(json.JSONEncoder):
    def default(self, obj):
        from hertavilla.message.internal import MsgContent

        if isinstance(obj, MsgContent):
            data = obj.dict()
            for k in data.copy().keys():
                if k.startswith("_"):
                    data.pop(k)
            return data
        return json.JSONEncoder.default(self, obj)


def _c(text: str) -> int:
    return (len(text.encode("utf-16")) // 2) - 1


def _rc(length: int) -> int:
    return (length + 1) * 2


class CustomPayload(Payload):
    @property
    def _binary_headers(self) -> bytes:
        # fuck aliyun
        headers = self.headers.copy()
        disposition = (
            "Content-Disposition: "
            f"{headers.pop('Content-Disposition')}\r\n".encode()
        )
        return disposition + (
            (
                "".join([f"{k}: {v}\r\n" for k, v in headers.items()]).encode(
                    "utf-8",
                )
                + b"\r\n"
            )
        )


class CustomBytesPayload(BytesPayload, CustomPayload):
    pass


class CustomStringPayload(StringPayload, CustomPayload):
    pass


def make_payload(value, **kwargs) -> CustomBytesPayload | CustomStringPayload:
    return (
        CustomBytesPayload(value, **kwargs)
        if isinstance(value, (bytes, bytearray, memoryview))
        else CustomStringPayload(value, **kwargs)
    )


class CustomFormData(FormData):
    def _gen_form_data(self) -> MultipartWriter:
        # the majority of this is copy pasted from aiohttp
        """Encode a list of fields using the multipart/form-data MIME format"""
        if self._is_processed:
            raise RuntimeError("Form data has been processed already")
        for dispparams, headers, value in self._fields:
            try:
                if hdrs.CONTENT_TYPE in headers:
                    part = make_payload(
                        value,
                        content_type=headers[hdrs.CONTENT_TYPE],
                        headers=headers,
                        encoding=self._charset,
                    )
                else:
                    part = make_payload(
                        value,
                        headers=headers,
                        encoding=self._charset,
                    )
            except Exception as exc:
                raise TypeError(
                    "Can not serialize value type: %r\n "
                    "headers: %r\n value: %r" % (type(value), headers, value),
                ) from exc

            if dispparams:
                part.set_content_disposition(
                    "form-data",
                    quote_fields=self._quote_fields,
                    **dispparams,
                )
                # FIXME cgi.FieldStorage doesn't likes body parts with
                # Content-Length which were sent via chunked transfer encoding
                assert part.headers is not None
                part.headers.popall(hdrs.CONTENT_LENGTH, None)

            self._writer.append_payload(part)

        self._is_processed = True
        return self._writer


# https://code.luasoftware.com/tutorials/python/asyncio-graceful-shutdown/
class TaskManager:
    def __init__(self):
        self.tasks = set()

    async def task(self, func, result=None, *args, **kwargs) -> Any | None:
        task_logger.debug(f"Add task: {func}({args}, {kwargs})")
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            return result
        finally:
            self.tasks.remove(task)

    def task_nowait(self, func, *args, **kwargs):
        task_logger.debug(f"Add task (nowait): {func}({args}, {kwargs})")
        task = asyncio.create_task(func(*args, **kwargs))
        self.tasks.add(task)
        task.add_done_callback(self.tasks.remove)

    def cancel_all(self):
        for _task in self.tasks:
            if not _task.done():
                _task.cancel()
