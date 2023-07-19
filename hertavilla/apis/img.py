from __future__ import annotations

from hertavilla.apis.base import _BaseAPIMixin


class ImgAPIMixin(_BaseAPIMixin):
    async def transfer_image(
        self,
        villa_id: int,
        url: str,
    ) -> str:
        """将非米游社的三方图床图片转存到米游社官方图床

        Args:
            villa_id (int): 大别野 id
            url (str): 三方图床的图片链接

        Returns:
            str: 新的米游社官方图床的图片链接
        """
        return (
            await self.base_request(
                "/transferImage",
                "POST",
                villa_id,
                data={"url": url},
            )
        )["new_url"]
