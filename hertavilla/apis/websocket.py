from __future__ import annotations

from hertavilla.apis.internal import _BaseAPIMixin
from hertavilla.model import WebSocketInfo


class WebSocketAPIMixin(_BaseAPIMixin):
    async def get_websocket_info(self, villa_id: int) -> WebSocketInfo:
        """获取 WebSocket 接入信息

        Args:
            villa_id (int): 大别野 id

        Returns:
            WebSocketInfo: WebSocket 接入信息
        """
        return await self.base_request("/getWebsocketInfo", "GET", villa_id)
