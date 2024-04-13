import re
import os
import json
import aiohttp

from pathlib import Path

from nonebot import on_regex, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment

from .GenB50 import generateb50, get_player_data

best50 = on_fullmatch('dlx50')
all_plate = on_regex(r'^(plate|看牌子)$')
all_frame = on_regex(r'^(frame|看底板)$')

set_plate = on_regex(r'(setplate|设置牌子) ?(\d{6})$')
set_frame = on_regex(r'(setframe|设置底板) ?(\d{6})$')

ratj_on = on_fullmatch('开启分数推荐')
ratj_off = on_fullmatch('关闭分数推荐')

@best50.handle()
async def _(event:GroupMessageEvent):
    qq = event.get_user_id()
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
                try:
                    data = await resp.json()
                    await best50.send(MessageSegment.text('迪拉熊绘制中，稍等一下mai~'))
                    b35 = data['charts']['sd']
                    b15 = data['charts']['dx']
                    nickname = data['nickname']
                    rating = data['rating']
                    img = await generateb50(b35=b35, b15=b15, nickname=nickname, rating=rating, qq=qq)
                    msg = (MessageSegment.at(qq), MessageSegment.image(img))
                    await best50.send(msg)
                except Exception as e:
                    msg = (MessageSegment.at(qq), MessageSegment.text(f'\n生成b50时发生错误：\n{str(e)}'))
                    await best50.send(msg)


@all_frame.handle()
async def _():
    path = './src/maimai/allFrame.png'
    await all_frame.finish(MessageSegment.image(Path(path)))

@all_plate.handle()
async def _():
    path = './src/maimai/allPlate.png'
    await all_plate.finish(MessageSegment.image(Path(path)))

@set_plate.handle()
async def _(event:GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.get_message())
    id = re.search(r'\d+', msg).group(0)
    dir_path = f"./src/maimai/Plate/"
    file_name = f"UI_Plate_{id}.png"
    file_path = Path(dir_path) / file_name
    if os.path.exists(file_path):
        with open('./data/maimai/b50_config.json', 'r') as f:
            config = json.load(f)

        if qq not in config:
            config.setdefault(qq, {'frame': '200502', 'plate': '000101', 'rating_tj': True})
        config[qq]['plate'] = id

        with open('./data/maimai/b50_config.json', 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊帮你换好啦~'))
        await set_plate.send(msg)
    else:
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊没换成功，再试试吧~(输入id有误)'))
        await set_plate.send(msg)

@set_frame.handle()
async def _(event:GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.get_message())
    id = re.search(r'\d+', msg).group(0)
    dir_path = f"./src/maimai/Frame/"
    file_name = f"UI_Frame_{id}.png"
    file_path = Path(dir_path) / file_name
    if os.path.exists(file_path):
        with open('./data/maimai/b50_config.json', 'r') as f:
            config = json.load(f)

        if qq not in config:
            config.setdefault(qq, {'frame': '200502', 'plate': '000101', 'rating_tj': True})
        config[qq]['frame'] = id

        with open('./data/maimai/b50_config.json', 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊帮你换好啦~'))
        await set_plate.send(msg)
    else:
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊没换成功，再试试吧~(输入id有误)'))
        await set_plate.send(msg)

@ratj_on.handle()
async def _(event:GroupMessageEvent):
    qq = event.get_user_id()
    with open('./data/maimai/b50_config.json', 'r') as f:
            config = json.load(f)

    if qq not in config:
        config.setdefault(qq, {'frame': '200502', 'plate': '000101', 'rating_tj': True})
    config[qq]['rating_tj'] = True

    with open('./data/maimai/b50_config.json', 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    msg = (MessageSegment.at(qq), MessageSegment.text(' 已为你开启分数推荐'))
    await ratj_on.finish(msg)

@ratj_off.handle()
async def _(event:GroupMessageEvent):
    qq = event.get_user_id()
    with open('./data/maimai/b50_config.json', 'r') as f:
            config = json.load(f)

    if qq not in config:
        config.setdefault(qq, {'frame': '200502', 'plate': '000101', 'rating_tj': True})
    config[qq]['rating_tj'] = False

    with open('./data/maimai/b50_config.json', 'w') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

    msg = (MessageSegment.at(qq), MessageSegment.text(' 已为你关闭分数推荐'))
    await ratj_off.finish(msg)