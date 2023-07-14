from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Literal
import warnings

from hertavilla.exception import (
    HTTPStatusError,
    PubkeyNoneWarning,
    raise_exception,
)

from aiohttp import ClientSession

logger = logging.getLogger("hertavilla.api")
BASE_API = "https://bbs-api.miyoushe.com/vila/api/bot/platform"


class _BaseAPIMixin:
    def __init__(
        self,
        bot_id: str,
        secret: str,
        pub_key: str | None = None,
    ):
        self.bot_id = bot_id
        self.secret = secret
        self.pub_key = pub_key
        if pub_key is None:
            warnings.warn(
                "Pubkey is None. You're using unencrypted secret. "
                "Unencrypted secret will be deprecated after August 8, 2023",
                stacklevel=3,
                category=PubkeyNoneWarning,
            )

    def _make_header(self, villa_id: int) -> dict[str, str]:
        if self.pub_key is not None:
            secret = hmac.new(
                self.pub_key.encode(),
                self.secret.encode(),
                hashlib.sha256,
            ).hexdigest()
        else:
            secret = self.secret
        return {
            "x-rpc-bot_id": self.bot_id,
            "x-rpc-bot_secret": secret,
            "x-rpc-bot_villa_id": str(villa_id),
        }

    async def base_request(
        self,
        api: str,
        method: Literal["POST"] | Literal["GET"],
        /,
        villa_id: int | None = None,
        *,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ):
        logger.info(f"Calling API {api}.")
        async with ClientSession() as session:
            async with session.request(
                method,
                f"{BASE_API}{api}",
                json=data,
                params=params,
                headers=self._make_header(villa_id) if villa_id else None,
            ) as resp:
                if not resp.ok:
                    raise HTTPStatusError(resp.status)
                payload = await resp.json()
                raise_exception(payload)
                return payload["data"]
