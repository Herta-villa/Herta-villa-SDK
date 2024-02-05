from __future__ import annotations

from hertavilla import Event, SendMessageEvent, VillaBot, run
from hertavilla.match import MatchResult, Regex
from hertavilla.server import init_backend

bot = VillaBot(
    "bot_id",
    "bot_secret",
    "/",
    "pub_key",
)


# bot.listen 装饰器用来监听指定类型的事件
@bot.listen(Event)
async def _(event: Event, bot: VillaBot): ...


# 手动注册（不建议）
async def handler(event: Event, bot: VillaBot): ...


bot.register_handler(Event, handler)


# @bot.regex("a|b|c")  # 正则匹配 -- RegexResult
# @bot.startswith("/")  # 前缀匹配 -- StartswithResult
# @bot.endswith(".")  # 后缀匹配 -- EndswithResult
# @bot.keyword("a", "b")  # 关键词匹配 -- KeywordsResult


# bot.match 会要求填入一个 Match 进行匹配
# 上面的四个方法分别是 Regex、Startswith、Endswith、Keywords 的语法糖
@bot.match(Regex("a|b|c"))  # 等价于 @bot.regex("a|b|c")
async def _(event: SendMessageEvent, bot: VillaBot, match_result: MatchResult):
    # match_result 参数用于获取从匹配器获得的匹配信息
    ...


init_backend()
run(bot)
