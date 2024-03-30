from nonebot import on_command, on_notice
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.adapters.onebot.v11.event import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent

def is_groupIncrease(event: GroupIncreaseNoticeEvent):
    return True

def is_groupDecrease(event: GroupDecreaseNoticeEvent):
    return True

groupIncrease = on_notice(rule=is_groupIncrease)
groupDecrease = on_notice(rule=is_groupDecrease)

@groupIncrease.handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    qq = event.get_user_id()
    user_name = (await bot.get_stranger_info(user_id=int(qq), no_cache=False))['nickname']
    msg = (MessageSegment.text(f'恭喜{user_name}（{qq}）发现了迪拉熊宝藏地带，发送dlx试一下吧~'))
    await groupIncrease.finish(msg)

@groupDecrease.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    qq = event.get_user_id()
    user_name = (await bot.get_stranger_info(user_id=int(qq), no_cache=False))['nickname']
    msg = (MessageSegment.text(f'很遗憾，{user_name}（{qq}）离开了迪拉熊的小窝QAQ'))
    await groupDecrease.finish(msg)