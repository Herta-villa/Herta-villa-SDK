from __future__ import annotations

import json

from hertavilla.apis.internal import _BaseAPIMixin
from hertavilla.message.component import Panel
from hertavilla.message.internal import MsgContentInfo
from hertavilla.utils import MsgEncoder


class MessageAPIMixin(_BaseAPIMixin):
    async def send_message(
        self,
        villa_id: int,
        room_id: int,
        msg_content_info: MsgContentInfo,
        object_name: str = "MHY:Text",
    ) -> str:
        """发送消息

        Args:
            villa_id (int): 大别野 id
            room_id (int): 房间 id
            msg_content_info (MsgContentInfo): 消息信息
            object_name (str, optional): 消息类型，目前支持: MHY:Text 文本类型. Defaults to "MHY:Text".

        Returns:
            str: bot_msg_id 机器人所发送消息的唯一标识符
        """  # noqa: E501
        return (
            await self.base_request(
                "/sendMessage",
                "POST",
                villa_id,
                data={
                    "room_id": room_id,
                    "object_name": object_name,
                    "msg_content": json.dumps(
                        msg_content_info,
                        ensure_ascii=False,
                        cls=MsgEncoder,
                    ),
                },
            )
        )["bot_msg_id"]

    async def pin_message(
        self,
        villa_id: int,
        msg_uid: str,
        room_id: int,
        send_at: int,
        is_cancel: bool = False,
    ) -> None:
        """置顶消息

        Args:
            villa_id (int): 大别野 id
            msg_uid (str): 消息 id
            room_id (int): 房间 id
            send_at (int): 发送时间
            is_cancel (bool, optional): 是否取消置顶. Defaults to False.
        """
        await self.base_request(
            "/pinMessage",
            "POST",
            villa_id,
            data={
                "msg_uid": msg_uid,
                "room_id": room_id,
                "send_at": send_at,
                "is_cancel": is_cancel,
            },
        )

    async def recall_message(
        self,
        villa_id: int,
        msg_uid: str,
        room_id: int,
        msg_time: int,
    ) -> None:
        """撤回消息

        Args:
            villa_id (int): 大别野 id
            msg_uid (str): 消息 id
            room_id (int): 房间 id
            msg_time (int): 发送时间
        """
        await self.base_request(
            "/recallMessage",
            "POST",
            villa_id,
            data={
                "msg_uid": msg_uid,
                "room_id": room_id,
                "msg_time": msg_time,
            },
        )

    async def create_component_template(
        self,
        villa_id: int,
        panel: Panel,
    ) -> int:
        """创建消息组件模板，创建成功后会返回 template_id，
        发送消息时，可以使用 template_id 填充 component_board

        Args:
            villa_id (int): 大别野 id
            panel (Panel): 消息组件面板

        Returns:
            int: 组件模板id
        """
        if template_id := (panel_dict := panel.to_dict()).get("template_id"):
            return template_id
        return int(
            (
                await self.base_request(
                    "/createComponentTemplate",
                    "POST",
                    villa_id,
                    data={
                        "panel": json.dumps(panel_dict),
                    },
                )
            )["template_id"],
        )
