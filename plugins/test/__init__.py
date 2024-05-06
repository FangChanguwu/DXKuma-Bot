from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

test = on_regex(r'^(test)')


@test.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    target = str(event.raw_message)
    print(target)
