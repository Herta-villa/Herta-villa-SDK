from __future__ import annotations

from hertavilla import (
    Image,
    Link,
    MentionedAll,
    MentionedRobot,
    MentionedUser,
    MessageChain,
    Post,
    SendMessageEvent,
    VillaBot,
    VillaRoomLink,
    run,
)
from hertavilla.message.text import Text

bot = VillaBot(
    "bot_id",
    "bot_secret",
    "/",
    "pub_key",
)


@bot.listen(SendMessageEvent)  # 注册一个消息匹配器
async def _(event: SendMessageEvent, bot: VillaBot):
    # 消息链
    # 需要通过对这个链拼接构成消息
    chain = MessageChain()

    # Text: 文字类型
    # https://webstatic.mihoyo.com/vila/bot/doc/message_api/msg_define/text_msg_content.html#textentity
    # 可以直接添加 str，SDK 会自动转成 Text
    # 以下两行代码等价
    chain.append("hello")
    chain.append(Text("hello"))

    # Mention*: 提及类型

    # @指定成员
    # 注意需要填写大别野 ID
    chain.append(MentionedUser(str(event.from_user_id), event.villa_id))
    # @全体成员
    chain.append(MentionedAll())
    # @机器人（目前只能@自身）
    chain.append(MentionedRobot(bot.bot_id))

    # VillaRoomLink: 链接房间（#房间）
    chain.append(VillaRoomLink(event.villa_id, event.room_id))

    # Link: 链接
    chain.append(Link("https://www.miyoushe.com/"))

    # Image: 图片
    # https://webstatic.mihoyo.com/vila/bot/doc/message_api/msg_define/img_msg_content.html
    chain.append(Image(url=""))

    # Post: 帖子转发
    # https://webstatic.mihoyo.com/vila/bot/doc/message_api/msg_define/post_msg_content.html
    chain.append(
        Post("40569017"),
    )  # https://www.miyoushe.com/sr/article/40569017

    # 请注意
    # Post:
    #   如果存在多个 Post，SDK 会选择最后一个 Post 发送
    #   如果存在 Text，SDK 不会发送 Post
    # Image:
    #   如果存在 Text，则将使用 MHY:Text 发送，Web 端无法查看图片（不受支持）
    #   如果存在多张图片，则将使用 MHY:Text 发送，Web 端无法查看（不受支持）


run(bot)
