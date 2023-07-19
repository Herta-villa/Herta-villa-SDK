# Herta-villa-SDK

[![license](https://img.shields.io/github/license/Herta-villa/Herta-villa-SDK)](https://github.com/Herta-villa/Herta-villa-SDK/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/herta-villa-sdk)](https://pypi.python.org/pypi/herta-villa-sdk)
![python version](https://img.shields.io/badge/Python-3.8+-green)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

大别野「黑塔」Python SDK

## 特性

- 多种服务器后端（内置 `aiohttp` 和 `fastapi` 后端），完整异步支持
- 完整类型注解支持
- ...

## 安装

```shell
pip install herta-villa-sdk
```

FastAPI 后端支持:

```shell
pip install herta-villa-sdk[fastapi]
```

## 快速开始

你需要拥有一个[大别野](https://dby.miyoushe.com/chat)机器人。可前往大别野[「机器人开发者社区」](https://dby.miyoushe.com/chat/463/20020)（`OpenVilla`）申请。

```python
from hertavilla import MessageChain, SendMessageEvent, VillaBot, run
from hertavilla.server import init_backend


PUB_KEY = """-----BEGIN PUBLIC KEY-----
aaa
bbb
ccc
-----END PUBLIC KEY-----
"""  # 开放平台 pub_key
# 需要注意 `-----BEGIN PUBLIC KEY-----` 前没有换行符
#  `-----END PUBLIC KEY-----` 后有一个换行符
# 目前从网页端复制下来的时候会为一串 pub_key，需要将空格转为换行

bot = VillaBot(
    "bot_id",  # 这里填写 bot_id
    "bot_secret",  # 这里填写 secret
    "/",  # bot 回调 endpoint
    PUB_KEY,  # 开放平台提供的 pub_key
)


@bot.startswith("/")  # 注册一个消息匹配器，匹配前缀为 / 的消息
async def _(event: SendMessageEvent, bot: VillaBot):
    message = event.message
    if str(message[1]) == "/hello":
        chain = MessageChain()
        chain.append("world")
        await bot.send(event.villa_id, event.room_id, chain)


init_backend()  # 初始化后端
run(bot)  # 运行 bot
```

可以向你的 bot 发送 `@Bot /hello`，bot 会回复 `world`。

## 示例

详见 [examples](./examples/) 文件夹

## 支持的 API

- [x] 鉴权
  - [x] 校验用户机器人访问凭证 `/checkMemberBotAccessToken`
- [x] 大别野
  - [x] 获取大别野信息 `/getVilla`
- [x] 用户
  - [x] 获取用户信息 `/getMember`
  - [x] 获取大别野成员列表 `/getVillaMembers`
  - [x] 踢出大别野用户 `/deleteVillaMember`
- [x] 消息
  - [x] 置顶消息 `/pinMessage`
  - [x] 撤回消息 `/recallMessage`
  - [x] 发送消息 `/sendMessage`
- [x] 房间
  - [x] 创建分组 `/createGroup`
  - [x] 编辑分组 `/editGroup`
  - [x] 删除分组 `/deleteGroup`
  - [x] 获取分组列表 `/getGroupList`
  - [x] 编辑房间 `/editRoom`
  - [x] 删除房间 `/deleteRoom`
  - [x] 获取房间信息 `/getRoom`
  - [x] 获取房间列表信息 `/getVillaGroupRoomList`
- [x] 身份组
  - [x] 向身份组操作用户 `/operateMemberToRole`
  - [x] 创建身份组 `/createMemberRole`
  - [x] 编辑身份组 `/editMemberRole`
  - [x] 删除身份组 `/deleteMemberRole`
  - [x] 获取身份组 `/getMemberRoleInfo`
  - [x] 获取大别野下所有身份组 `/getVillaMemberRoles`
- [x] 表态表情
  - [x] 获取全量表情 `/getAllEmoticons`
- [ ] 审核 `/audit`

## 支持的事件

- [x] [JoinVilla](https://webstatic.mihoyo.com/vila/bot/doc/callback.html###JoinVilla) 有新用户加入大别野
- [x] [SendMessage](https://webstatic.mihoyo.com/vila/bot/doc/callback.html###SendMessage) 用户@机器人发送消息
- [x] [CreateRobot](https://webstatic.mihoyo.com/vila/bot/doc/callback.html###CreateRobot) 大别野添加机器人实例
- [x] [DeleteRobot](https://webstatic.mihoyo.com/vila/bot/doc/callback.html###DeleteRobot) 大别野删除机器人实例
- [x] [AddQuickEmoticon](https://webstatic.mihoyo.com/vila/bot/doc/callback.html#AddQuickEmoticon) 用户使用表情回复消息表态
- [ ] [AuditCallback](https://webstatic.mihoyo.com/vila/bot/doc/callback.html#AuditCallback) 审核结果回调

## Bug 反馈及建议

大别野 Bot 和 Herta SDK 均处于开发状态中，如遇到问题或有相关建议可通过 [Issue](https://github.com/Herta-villa/Herta-villa-SDK/issues/new) 提出，感谢支持！

## 相关项目

- [CMHopeSunshine/villa-py](https://github.com/CMHopeSunshine/villa-py) 米游社大别野 Bot Python SDK（非官方）

## 交流

- 前往大别野[「斩尽芜杂」](https://dby.miyoushe.com/chat/1785/25317)（`aaUeZqd`）
