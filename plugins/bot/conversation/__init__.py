from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from util.Config import config

xc = on_regex(r'(香草|想草)(迪拉熊|滴蜡熊|dlx)')

@xc.handle()
async def _():
    await xc.finish('变态！！！')