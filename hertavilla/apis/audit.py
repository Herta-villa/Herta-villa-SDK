from __future__ import annotations

from hertavilla.apis.internal import _BaseAPIMixin


class AuditAPIMixin(_BaseAPIMixin):
    async def audit(
        self,
        villa_id: int,
        audit_content: str,
        room_id: int,
        uid: int,
        pass_through: str | None = None,
    ) -> str:
        """审核用户配置内容是否合规，调用成功后会返回审核事件id(audit_id)。审核结果会通过回调接口异步通知 (`AuditCallback`)。
        如果机器人存在大别野用户自定义内容，就要调用审核接口，判断内容是否合规。

        Args:
            villa_id (int): 大别野 id
            audit_content (str): 待审核内容
            room_id (int): 房间 id
            uid (int): 用户 id
            pass_through (str | None, optional): 透传信息，该字段会在审核结果回调时携带给开发者，选填. Defaults to None.

        Returns:
            str: 审核事件 id
        """  # noqa: E501
        # FIXME: 文档所说 room_id 和 uid 为选填
        # 但是不填会 -1，所以这里设置成了必填
        return (
            await self.base_request(
                "/audit",
                "POST",
                villa_id,
                data={
                    "audit_content": audit_content,
                    "room_id": room_id,
                    "uid": uid,
                    "pass_through": pass_through,
                },
            )
        )["audit_id"]
