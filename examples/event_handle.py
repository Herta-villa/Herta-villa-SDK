from __future__ import annotations

from hertavilla import Event, SendMessageEvent, VillaBot, run
from hertavilla.match import Regex

bot = VillaBot(
    "bot_id",
    "bot_secret",
    "/",
    "pub_key",
)


# bot.listen 装饰器用来监听指定类型的事件
@bot.listen(Event)
async def _(event: Event, bot: VillaBot):
    ...


# 手动注册（不建议）
async def handler(event: Event, bot: VillaBot):
    ...


bot.register_handler(Event, handler)


@bot.regex("a|b|c")  # 正则匹配
@bot.startswith("/")  # 前缀匹配
@bot.endswith(".")  # 后缀匹配
@bot.keyword("a", "b")  # 关键词匹配

# bot.match 会要求填入一个 Match 进行匹配
# 上面的四个方法分别是 Regex、Startswith、Endswith、Keywords 的语法糖
@bot.match(Regex("a|b|c"))  # 等价于 @bot.regex("a|b|c")
async def _(event: SendMessageEvent, bot: VillaBot):
    ...


run(bot)
