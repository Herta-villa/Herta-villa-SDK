# Herta-villa-SDK

[![license](https://img.shields.io/github/license/MingxuanGame/Herta-villa-SDK)](https://github.com/MingxuanGame/Herta-villa-SDK/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/herta-villa-sdk)](https://pypi.python.org/pypi/herta-villa-sdk)
![python version](https://img.shields.io/badge/Python-3.8+-green)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

大别野「黑塔」Python SDK

## 特性

- `aiohttp` 客户端+服务端，完整异步支持
- 完整类型注解支持
- ...

## 安装

```shell
pip install herta-villa-sdk
```

## 快速开始

你需要拥有一个[大别野](https://dby.miyoushe.com/chat)机器人。可前往大别野[「机器人开发者社区」](https://dby.miyoushe.com/chat/463/20020)（`OpenVilla`）申请。

```python
from hertavilla import MessageChain, SendMessageEvent, VillaBot, run

bot = VillaBot(
    "bot_id",  # 这里填写 bot_id
    "bot_secret",  # 这里填写 secret
    "/",  # bot 回调 endpoint
)


@bot.startswith("/")  # 注册一个消息匹配器，匹配前缀为 / 的消息
async def _(event: SendMessageEvent, bot: VillaBot):
    message = event.message
    if str(message[1]) == "/hello":
        chain = MessageChain()
        chain.append("world")
        await bot.send(event.villa_id, event.room_id, chain)


run(bot)  # 运行 bot
```

可以向你的 bot 发送 `@Bot /hello`，bot 会回复 `world`。

## 示例

详见 [examples](./examples/) 文件夹

## Bug 反馈及建议

大别野 Bot 和 Herta SDK 均处于开发状态中，如遇到问题或有相关建议可通过 [Issue](https://github.com/MingxuanGame/Herta-villa-SDK/issues/new) 提出，感谢支持！

## 相关项目

- [CMHopeSunshine/villa-py](https://github.com/CMHopeSunshine/villa-py) 米游社大别野 Bot Python SDK（非官方）

## 交流

- 前往大别野[「斩尽芜杂」](https://dby.miyoushe.com/chat/1785/25317)（`aaUeZqd`）
