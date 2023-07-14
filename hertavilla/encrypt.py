from __future__ import annotations

import base64
import urllib.parse

from hertavilla.bot import VillaBot

import rsa


def verify(
    bot: VillaBot,
    sign: str,
    body: str,
) -> bool:
    sign_ = base64.b64decode(sign)
    sign_msg = urllib.parse.urlencode({"body": body, "secret": bot.secret})
    pub_key = bot.rsa_pub_key
    if isinstance(pub_key, str):
        pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key.encode())
    try:
        rsa.verify(sign_msg.encode(), sign_, pub_key)
    except rsa.VerificationError:
        return False
    else:
        return True
