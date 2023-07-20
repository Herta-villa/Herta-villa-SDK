from __future__ import annotations

from typing import Any

call_api_exceptions: dict[int, type[_ExceptionWithRetcode]] = {}


class PubkeyNoneWarning(Warning):
    ...


class SDKException(Exception):
    ...


class HTTPStatusError(SDKException):
    def __init__(
        self,
        /,
        status: int,
    ) -> None:
        self.status = status

    def __repr__(self) -> str:
        return "<HTTPStatusError status={self.status}"


class _ExceptionWithRetcode(SDKException):
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

    def __init_subclass__(cls, retcode: int) -> None:
        call_api_exceptions[retcode] = cls
        return super().__init_subclass__()

    def __str__(self) -> str:
        return repr(self)


class UnknownServerError(CallingApiException, retcode=-502):
    ...


class InvalidRequest(CallingApiException, retcode=-1):
    ...


class InsufficientPermission(CallingApiException, retcode=10318001):
    ...


class BotNotAdded(CallingApiException, retcode=10322002):
    ...


class PermissionDenied(CallingApiException, retcode=10322003):
    ...


class InvalidMemberBotAccessToken(CallingApiException, retcode=10322004):
    ...


class InvalidBotAuthInfo(CallingApiException, retcode=10322005):
    ...


class UnsupportedMsgType(CallingApiException, retcode=10322006):
    ...


def raise_exception(payload: dict[str, Any]):
    if payload["retcode"] != 0:
        retcode = payload["retcode"]
        raise call_api_exceptions.get(retcode, CallingApiException)(
            retcode,
            payload["message"],
        )
