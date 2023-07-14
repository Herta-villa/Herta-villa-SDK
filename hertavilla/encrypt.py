from __future__ import annotations

import base64
import hashlib
import urllib.parse

from hertavilla.bot import VillaBot

import rsa


def verify(
    bot: VillaBot,
    pub_key: str | rsa.PublicKey,
    sign: str,
    body: str,
) -> bool:
    sign_ = base64.b64decode(sign)
    sign_msg = urllib.parse.urlencode({"body": body, "secret": bot.secret})
    hashed_origin = hashlib.sha256(sign_msg.encode()).digest()
    if isinstance(pub_key, str):
        pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key.encode())
    try:
        rsa.verify(hashed_origin, sign_, pub_key)
    except rsa.VerificationError:
        return False
    else:
        return True
