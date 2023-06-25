from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from hertavilla.typing import TypedDict

from pydantic import BaseModel

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot


class _Segment(abc.ABC):
    ...

    @abc.abstractmethod
    async def get_text(self, bot: "VillaBot") -> str:
        raise NotImplementedError


class MsgContentInfo(TypedDict):
    ...


class MsgContent(BaseModel):
    ...
