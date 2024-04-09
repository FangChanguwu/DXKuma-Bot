import aiohttp
from nonebot import on_regex, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment

from .GenB50 import generateb50, get_player_data

best50 = on_fullmatch('dlx50')

@best50.handle()
async def _(event:GroupMessageEvent):
    qq = event.user_id
    payload = {"qq": qq, 'b50': True}
    async with aiohttp.ClientSession() as session:
        async with session.post("https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
            if resp.status == 400:
                msg = '未找到用户信息，可能是没有绑定查分器\n查分器网址：https://www.diving-fish.com/maimaidx/prober/'
                await best50.finish(msg)
            elif resp.status == 403:
                msg = '该用户禁止了其他人获取数据.'
                await best50.finish(msg)
            elif resp.status == 200:
                data = await resp.json()
                await best50.send(MessageSegment.text('迪拉熊绘制中，稍等一下mai~'))
                b35 = data['charts']['sd']
                b15 = data['charts']['dx']
                nickname = data['nickname']
                rating = data['rating']
                img = await generateb50(b35=b35, b15=b15, nickname=nickname, rating=rating, qq=qq)
                await best50.send(MessageSegment.image(img))