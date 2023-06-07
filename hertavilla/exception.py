from __future__ import annotations

from typing import Any


class _ExceptionWithRetcode(Exception):
    def __init__(self, /, retcode: int, message: str) -> None:
        self.retcode = retcode
        self.message = message

    def to_dict(self):
        return {"retcode": self.retcode, "message": self.message}


class CallingApiException(_ExceptionWithRetcode):
    def __repr__(self) -> str:
        return (
            "<CallingApiException "
            f"retcode={self.retcode}, message={self.message!r}>"
        )

    def __str__(self) -> str:
        return repr(self)


def raise_exception(payload: dict[str, Any]):
    if payload["retcode"] != 0:
        raise CallingApiException(payload["retcode"], payload["message"])
