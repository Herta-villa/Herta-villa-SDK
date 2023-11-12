from __future__ import annotations

from hashlib import md5
from io import BytesIO
from pathlib import Path
from typing import Literal

from hertavilla.apis.internal import _BaseAPIMixin
from hertavilla.exception import HTTPStatusError
from hertavilla.model import UploadParams
from hertavilla.utils import CustomFormData

from aiohttp import ClientSession


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

    async def get_upload_image_params(
        self,
        villa_id: int,
        md5: str,
        ext: Literal["jpg", "png", "jpeg", "bmp", "gif"],
    ) -> UploadParams:
        """获取米游社阿里云 OSS 上传参数

        Args:
            villa_id (int): 大别野 id
            md5 (str): 图片的 md5，最后会被用于文件名
            ext (Literal[&quot;jpg&quot;, &quot;png&quot;, &quot;jpeg&quot;, &quot;bmp&quot;, &quot;gif&quot;]): 图片扩展名 (支持 jpg,jpeg,png,gif,bmp)

        Returns:
            UploadParams: 上传参数
        """  # noqa: E501
        return await self.base_request(
            "/getUploadImageParams",
            "GET",
            villa_id,
            params={"md5": md5, "ext": ext},
        )

    async def upload_to_aliyun_oss(
        self,
        image: bytes,
        params: UploadParams,
    ) -> str:
        """上传图片到阿里云 OSS

        Args:
            image (bytes): 图片二进制
            params (UploadParams): 上传参数

        Returns:
            str: 图片 URL
        """
        form = CustomFormData(
            {
                "x:extra": params["params"]["callback_var"]["x:extra"],
                "OSSAccessKeyId": params["params"]["accessid"],
                "signature": params["params"]["signature"],
                "success_action_status": params["params"][
                    "success_action_status"
                ],
                "name": params["params"]["name"],
                "callback": params["params"]["callback"],
                "x-oss-content-type": params["params"]["x_oss_content_type"],
                "key": params["params"]["key"],
                "policy": params["params"]["policy"],
            },
        )
        form.add_field("file", image)
        async with ClientSession() as session:
            async with session.post(
                params["params"]["host"],
                data=form,
            ) as resp:
                if not resp.ok:
                    raise HTTPStatusError(resp.status)
                return (await resp.json())["data"]["url"]

    async def upload_image(
        self,
        villa_id: int,
        image: bytes | BytesIO | Path,
        ext: Literal["jpg", "png", "jpeg", "bmp", "gif"],
    ) -> str:
        """上传图片（快捷方法）

        Args:
            villa_id (int): 大别野 id
            image (bytes): 图片
            ext (Literal[&quot;jpg&quot;, &quot;png&quot;, &quot;jpeg&quot;, &quot;bmp&quot;, &quot;gif&quot;]): 图片扩展名

        Returns:
            str: 图片 URL
        """  # noqa: E501
        if isinstance(image, BytesIO):
            image = image.getvalue()
        elif isinstance(image, Path):
            image = image.read_bytes()
        params = await self.get_upload_image_params(
            villa_id,
            md5(image).hexdigest(),
            ext,
        )
        return await self.upload_to_aliyun_oss(image, params)
