from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any, List, Literal

from hertavilla.message.internal import _Segment

from pydantic import BaseModel, validator

if TYPE_CHECKING:
    from hertavilla.bot import VillaBot


SMALL_MAX = 4
MID_MAX = 2
BIG_MAX = 1


class Component(BaseModel):
    id: str  # noqa: A003
    """组件id，由机器人自定义，不能为空字符串。面板内的id需要唯一"""

    text: str
    """组件展示文本, 不能为空"""

    type: int  # noqa: A003
    """组件类型，目前支持 type=1 按钮组件，未来会扩展更多组件类型"""

    need_callback: bool = True
    """是否订阅该组件的回调事件"""

    extra: str = ""
    """组件回调透传信息，由机器人自定义"""


Comp = Component


class ComponentGroup(BaseModel):
    __root__: List[Component]

    def __init__(self, *components: Component):
        super().__init__(__root__=components)


CGroup = ComponentGroup


class ComponentGroupList(BaseModel):
    __root__: List[CGroup]

    def __init__(self, *groups):
        super().__init__(__root__=groups)


CGroupList = ComponentGroupList


class SGroup(CGroup):
    def __init__(self, *components: Component):
        super().__init__(*components)

    @validator("__root__")
    def check(cls, v: List[Component]) -> List[Component]:
        if len(v) > SMALL_MAX:
            raise ValueError(
                f"small component group max length is {SMALL_MAX}",
            )
        return v


class MGroup(CGroup):
    def __init__(self, *components: Component):
        super().__init__(*components)

    @validator("__root__")
    def check(cls, v: List[Component]) -> List[Component]:
        if len(v) > MID_MAX:
            raise ValueError(f"mid component group max length is {MID_MAX}")
        return v


class BGroup(CGroup):
    def __init__(self, *components: Component):
        super().__init__(*components)

    @validator("__root__")
    def check(cls, v: List[Component]) -> List[Component]:
        if len(v) > BIG_MAX:
            raise ValueError(f"big component group max length is {BIG_MAX}")
        return v


LGroup = BGroup


class Panel(_Segment):
    def __init__(
        self,
        template_id: int | None = None,
        small: CGroupList | None = None,
        mid: CGroupList | None = None,
        big: CGroupList | None = None,
    ) -> None:
        if not template_id and not (small or mid or big):
            raise ValueError(
                "At least one of template_id, component group must be set",
            )
        self.small = CGroupList() if small is None else small
        self.mid = CGroupList() if mid is None else mid
        self.big = CGroupList() if big is None else big

        self.template_id = template_id

    async def get_text(self, _: "VillaBot") -> str:
        return "[Panel]"

    def to_dict(
        self,
    ) -> dict[str, Any]:
        if (template_id := self.template_id) is not None:
            return {"template_id": template_id}
        return {
            "small_component_group_list": self.small.dict()["__root__"],
            "mid_component_group_list": self.mid.dict()["__root__"],
            "big_component_group_list": self.big.dict()["__root__"],
        }

    # def insert(self, target: Literal["small", "mid", "big"], index: tuple[int, int], component: Component) -> None:  # noqa: E501


class ButtonType(IntEnum):
    """组件交互类型"""

    CALLBACK = 1
    """回传型"""
    INPUT = 2
    """输入型"""
    LINK = 3
    """跳转型"""


class Button(Component):
    type: Literal[1] = 1  # noqa: A003

    c_type: ButtonType
    """组件交互类型"""

    input: str = ""  # noqa: A003
    """如果交互类型为输入型，则需要在该字段填充输入内容，不能为空"""

    link: str = ""
    """如果交互类型为跳转型，需要在该字段填充跳转链接，不能为空"""

    need_token: bool = False
    """对于跳转链接来说，如果希望携带用户信息token，则need_token设置为true"""

    @validator("input")
    def check_input(cls, v, values):
        if values["c_type"] == ButtonType.INPUT and not v:
            raise ValueError("input is required")
        return v

    @validator("link")
    def check_link(cls, v, values):
        if values["c_type"] == ButtonType.LINK and not v:
            raise ValueError("link is required")
        return v
