from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment

from util.gen_status_img import gen_status

status = on_command('status')


@status.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    img = await gen_status()
    await status.finish(MessageSegment.image(img))
