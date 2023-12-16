from __future__ import annotations

from hertavilla.apis.internal import _BaseAPIMixin
from hertavilla.model import AuditContentType


class AuditAPIMixin(_BaseAPIMixin):
    async def audit(
        self,
        villa_id: int,
        audit_content: str,
        uid: int,
        room_id: int | None = None,
        pass_through: str | None = None,
        content_type: AuditContentType = AuditContentType.TEXT,
    ) -> str:
        """审核用户配置内容是否合规，调用成功后会返回审核事件id(audit_id)。审核结果会通过回调接口异步通知 (`AuditCallback`)。
        如果机器人存在大别野用户自定义内容，就要调用审核接口，判断内容是否合规。

        Args:
            villa_id (int): 大别野 id
            audit_content (str): 待审核内容
            uid (int): 用户 id
            room_id (int | None, optional): 房间 id，选填. Defaults to None.
            pass_through (str | None, optional): 透传信息，该字段会在审核结果回调时携带给开发者，选填. Defaults to None.
            content_type (AuditContentType, optional): 审核内容的类型. Defaults to AuditContentType.TEXT.

        Returns:
            str: 审核事件 id
        """  # noqa: E501
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
                    "content_type": content_type.value,
                },
            )
        )["audit_id"]
