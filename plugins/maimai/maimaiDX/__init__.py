import json
import os
import random
import re
import traceback
from pathlib import Path

import aiohttp
import requests
from arclet.alconna import Alconna, Args
from nonebot import on_regex, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_alconna import on_alconna, Match, AlconnaMatch

from util.Config import config
from .GenB50 import generateb50, get_player_data, generate_wcb
from .MusicInfo import music_info, play_info

best50 = on_regex(r'^(dlx50)')
ap50 = on_regex(r'^(dlxap)')

songinfo = on_regex(r'^(id) ?(\d+)$')
playinfo = on_regex(r'^(info) ?(.*)$')
randomsong = on_regex(r'^随(个|歌) ?(绿|黄|红|紫|白)?(\d+)(\.\d|\+)?')
maiwhat = on_regex(r'^(mai什么)')

wcb = on_regex(r'^(完成表)')

whatSong = on_regex(r'/?(search|查歌)\s*(.*)|(.*?)是什么歌')
aliasSearch = on_regex(r'^(查看别名) ?(\d+)$|(\d+)(有什么别名)$')

aliasAdd_alc = Alconna(
    '添加别名',
    Args["songId", int],
    Args['alias', str]
)
aliasAdd = on_alconna(aliasAdd_alc, auto_send_output=True)

aliasDel_alc = Alconna(
    '删除别名',
    Args["songId", int],
    Args['alias', str]
)
aliasDel = on_alconna(aliasDel_alc, auto_send_output=True)

all_plate = on_regex(r'^(plate|看牌子)$')
all_frame = on_regex(r'^(frame|看底板)$')

set_plate = on_regex(r'(setplate|设置牌子) ?(\d{6})$')
set_frame = on_regex(r'(setframe|设置底板) ?(\d{6})$')

ratj_on = on_fullmatch('开启分数推荐')
ratj_off = on_fullmatch('关闭分数推荐')

songList = requests.get('https://www.diving-fish.com/api/maimaidxprober/music_data').json()


# 根据乐曲别名查询乐曲id列表
async def find_songid_by_alias(name):
    # 读取别名文件
    with open('./src/maimai/aliasList.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 芝士id列表
    matched_ids = []

    # 芝士查找
    for id, info in data.items():
        if name in info['Alias'] or name in info['Name'] or str(name).lower() == str(info['Name']).lower():
            matched_ids.append(id)

    # 芝士排序
    sorted_matched_ids = sorted(matched_ids, key=int)

    # 芝士输出
    return sorted_matched_ids


# id查歌
async def find_song_by_id(song_id):
    with open('./src/maimai/songList.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for song in data:
        if song['id'] == song_id:
            return song

    # 如果没有找到对应 id 的歌曲，返回 None
    return None


async def records_to_ap50(records: list):
    ap_records = []
    for record in records:
        if record['fc'] in ['ap', 'app']:
            ap_records.append(record)

    apsd = []
    apdx = []
    for record in ap_records:
        song_id = record['song_id']
        is_new = [d["basic_info"]["is_new"] for d in songList if d["id"] == str(song_id)]
        if is_new[0]:
            apdx.append(record)
        else:
            apsd.append(record)
    ap35 = (sorted(apsd, key=lambda d: d["ra"], reverse=True))[:35]
    ap15 = (sorted(apdx, key=lambda d: d["ra"], reverse=True))[:15]
    return ap35, ap15


@best50.handle()
async def _(event: GroupMessageEvent):
    qq = event.get_user_id()
    msg_text = str(event.raw_message)
    pattern = r"\[CQ:at,qq=(\d+)\]"
    match = re.search(pattern, msg_text)
    if match:
        target_qq = match.group(1)
    else:
        target_qq = event.get_user_id()
    payload = {"qq": target_qq, 'b50': True}
    async with aiohttp.ClientSession() as session:
        async with session.post("https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
            if resp.status == 400:
                msg = '未找到用户信息，可能是没有绑定查分器\n查分器网址：https://www.diving-fish.com/maimaidx/prober/'
                await best50.finish(msg)
            elif resp.status == 403:
                msg = '该用户禁止了其他人获取数据'
                await best50.finish(msg)
            elif resp.status == 200:
                data = await resp.json()
                # print(data)
                await best50.send(MessageSegment.text('迪拉熊绘制中，稍等一下mai~'))
                b35 = data['charts']['sd']
                b15 = data['charts']['dx']
                nickname = data['nickname']
                # rating = data['rating']
                dani = data['additional_rating']
                try:
                    img = await generateb50(b35=b35, b15=b15, nickname=nickname, qq=target_qq, dani=dani, type='b50')
                    msg = (MessageSegment.at(qq), MessageSegment.image(img))
                    await best50.send(msg)
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    print(f'生成b50时发生错误：\n{traceback_info}')
                    msg = (MessageSegment.at(qq), MessageSegment.text(f'\n生成b50时发生错误：\n{str(e)}'))
                    await best50.send(msg)


@ap50.handle()
async def _(event: GroupMessageEvent):
    qq = event.get_user_id()
    msg_text = str(event.raw_message)
    pattern = r"\[CQ:at,qq=(\d+)\]"
    match = re.search(pattern, msg_text)
    if match:
        target_qq = match.group(1)
    else:
        target_qq = event.get_user_id()
    # payload = {"qq": target_qq, 'b50': True}
    url = 'https://www.diving-fish.com/api/maimaidxprober/dev/player/records'
    headers = {'Developer-Token': config.dev_token}
    payload = {"qq": target_qq}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=payload) as resp:
            if resp.status == 400:
                msg = '未找到用户信息，可能是没有绑定查分器\n查分器网址：https://www.diving-fish.com/maimaidx/prober/'
                await ap50.finish(msg)
            elif resp.status == 200:
                data = await resp.json()
                await ap50.send(MessageSegment.text('迪拉熊绘制中，稍等一下mai~'))
                records = data['records']
                ap35, ap15 = await records_to_ap50(records)
                if len(ap35) == 0 and len(ap15) == 0:
                    msg = (MessageSegment.at(qq), MessageSegment.text('你还没有ap任何一个谱面呢~'))
                    await ap50.finish(msg)
                nickname = data['nickname']
                dani = data['additional_rating']
                try:
                    img = await generateb50(b35=ap35, b15=ap15, nickname=nickname, qq=target_qq, dani=dani, type='ap50')
                    msg = (MessageSegment.at(qq), MessageSegment.image(img))
                    await ap50.send(msg)
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    print(f'生成ap50时发生错误：\n{traceback_info}')
                    msg = (MessageSegment.at(qq), MessageSegment.text(f'\n生成b50时发生错误：\n{str(e)}'))
                    await ap50.send(msg)
            else:
                data = await resp.json()
                await ap50.finish(data)


@wcb.handle()
async def _(event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.message)
    pattern = r'^(完成表) ?((\d+)(\.\d|\+)?)( ([0-9]+))?'
    match = re.match(pattern, msg)
    level = match.group(2)
    if match.group(5) is not None:
        page = int(match.group(5).strip())
        if page <= 0:
            page = 1
    else:
        page = 1
    await wcb.send(MessageSegment.text('迪拉熊绘制中，稍等一下mai~'))
    img = await generate_wcb(qq=qq, level=level, page=page)
    if type(img) is str:
        msg = (MessageSegment.at(qq), MessageSegment.text(img))
        await wcb.finish(msg)
    msg = (MessageSegment.at(qq), MessageSegment.image(img))
    await wcb.finish(msg)


@songinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.get_message())
    song_id = re.search(r'\d+', msg).group(0)
    song_info = await find_song_by_id(song_id)
    if not song_info:
        await songinfo.finish(f"没找到 {song_id} 对应的乐曲")
    else:
        img = await music_info(song_id=song_id, qq=qq)
        msg = (MessageSegment.at(qq), MessageSegment.image(img))
        await songinfo.finish(msg)


@playinfo.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.get_message())
    song = msg.replace('info', '').strip()
    if not song:
        await playinfo.finish(f"请准确输入乐曲的id或别名")
    rep_ids = await find_songid_by_alias(song)
    song_info = await find_song_by_id(song)
    if rep_ids:
        song_id = str(rep_ids[0])
        img = await play_info(song_id=str(song_id), qq=qq)
        if type(img) is str:
            msg = (MessageSegment.at(qq), MessageSegment.text(f'\n{img}'))
            await playinfo.finish(msg)
        else:
            msg = (MessageSegment.at(qq), MessageSegment.image(img))
            await playinfo.finish(msg)
    elif song_info:
        song_id = song
        img = await play_info(song_id=str(song_id), qq=qq)
        if type(img) is str:
            msg = (MessageSegment.at(qq), MessageSegment.text(f'\n{img}'))
            await playinfo.finish(msg)
        msg = (MessageSegment.at(qq), MessageSegment.image(img))
        await playinfo.finish(msg)
    else:
        await playinfo.finish(f"没找到 {song} 对应的乐曲\n请准确输入乐曲的id或别名")


@randomsong.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.message)
    pattern = r'^随(个|歌) ?(绿|黄|红|紫|白)?(\d+)(\.\d|\+)?'
    match = re.match(pattern, msg)
    level_label = match.group(2)
    if level_label:
        level_index = level_label.replace('绿', '0').replace('黄', '1').replace('红', '2').replace('紫', '3').replace(
            '白', '4')
        level_index = int(level_index)
    else:
        level_index = None
    level = match.group(3)
    if match.group(4) is not None:
        level += match.group(4)
    s_type = 'level'
    if '.' in level:
        s_type = 'ds'
    s_songs = []
    with open('./src/maimai/songList.json', 'r', encoding='utf-8') as f:
        song_list = json.load(f)

    for song in song_list:
        song_id = song['id']
        s_list = song[s_type]
        if s_type == 'ds':
            level = float(level)
        if level_index is not None:
            if len(s_list) > level_index:
                if level == s_list[level_index]:
                    s_songs.append(song_id)
        elif level in s_list:
            s_songs.append(song_id)
    if len(s_songs) == 0:
        msg = (MessageSegment.at(qq), MessageSegment.text(f' 没有符合条件的乐曲'))
        await randomsong.finish(msg)
    song_id = random.choice(s_songs)
    img = await music_info(song_id=song_id, qq=qq)
    msg = (MessageSegment.at(qq), MessageSegment.image(img))
    await randomsong.finish(msg)


@maiwhat.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    with open('./src/maimai/songList.json', 'r', encoding='utf-8') as f:
        song_list = json.load(f)
    song = random.choice(song_list)
    song_id = song['id']
    img = await music_info(song_id=song_id, qq=qq)
    msg = (MessageSegment.at(qq), MessageSegment.image(img))
    await randomsong.finish(msg)


@whatSong.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.message)
    match = re.match(r'/?(search|查歌)\s*(.*)|(.*?)是什么歌', msg, re.IGNORECASE)
    if match:
        if match.group(2):
            name = match.group(2)
        elif match.group(3):
            name = match.group(3)
        else:
            await whatSong.finish("什么都没找到……")
            return

        rep_ids = await find_songid_by_alias(name)
        if not rep_ids:
            await whatSong.finish("什么都没找到……")
        elif len(rep_ids) == 1:
            img = await music_info(rep_ids[0], qq=qq)
            msg = (MessageSegment.at(qq), MessageSegment.image(img))
            await whatSong.finish(msg)
        else:
            output_lst = f'{name} 的搜索结果如下：'
            for song_id in rep_ids:
                song_info = await find_song_by_id(song_id)
                if song_info:
                    song_title = song_info["title"]
                    output_lst += f"\n{song_id} - {song_title}"
            await whatSong.finish(output_lst)


# 查看别名
@aliasSearch.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    msg = str(event.get_message())
    song_id = re.search(r'\d+', msg).group(0)
    with open('./src/maimai/aliasList.json', 'r') as f:
        alias_list = json.load(f)
    alias = alias_list.get(song_id, None)
    if not alias:
        await aliasSearch.finish(f"没找到 {song_id} 对应的乐曲\n请准确输入乐曲的id")
    else:
        song_name = alias['Name']
        song_alias = '\n'.join(alias['Alias'])
        msg = f'{song_id}.{song_name} 的别名有：\n{song_alias}'
        await aliasSearch.finish(msg)


@aliasAdd.handle()
async def _(bot: Bot,
            event: GroupMessageEvent,
            song_id: Match[int] = AlconnaMatch("songId"),
            alias: Match[str] = AlconnaMatch("alias")):
    song_id = str(song_id.result)
    alias_name = alias.result
    with open('./src/maimai/aliasList.json', 'r') as f:
        alias_list = json.load(f)
    song_alias = alias_list.get(song_id, None)
    if not song_alias:
        await aliasAdd.finish(f"没找到 {song_id} 对应的乐曲\n请准确输入乐曲的id")
    elif alias_name in alias_list[str(song_id)]['Alias']:
        await aliasAdd.finish(f"{song_id}.{song_alias['Name']} 已有该别名：{alias_name}")
    else:
        alias_list[str(song_id)]['Alias'].append(alias_name)
        with open('./src/maimai/aliasList.json', 'w', encoding='utf-8') as f:
            json.dump(alias_list, f, ensure_ascii=False, indent=4)
        await aliasAdd.finish(f"已将 {alias_name} 添加到 {song_id}.{song_alias['Name']} 的别名")


@aliasDel.handle()
async def _(song_id: Match[int] = AlconnaMatch("songId"), alias: Match[str] = AlconnaMatch("alias")):
    song_id = str(song_id.result)
    alias_name = alias.result
    with open('./src/maimai/aliasList.json', 'r') as f:
        alias_list = json.load(f)
    song_alias = alias_list.get(song_id, None)
    if not song_alias:
        await aliasDel.finish(f"没找到 {song_id} 对应的乐曲\n请准确输入乐曲的id")
    elif alias_name not in alias_list[str(song_id)]['Alias']:
        await aliasDel.finish(f"{song_id}.{song_alias['Name']} 没有该别名：{alias_name}")
    else:
        alias_list[str(song_id)]['Alias'].remove(alias_name)
        with open('./src/maimai/aliasList.json', 'w', encoding='utf-8') as f:
            json.dump(alias_list, f, ensure_ascii=False, indent=4)
        await aliasDel.finish(f"已从 {song_id}.{song_alias['Name']} 的别名中移除 {alias_name}")


@all_frame.handle()
async def _():
    path = './src/maimai/allFrame.png'
    await all_frame.finish(MessageSegment.image(Path(path)))


@all_plate.handle()
async def _():
    path = './src/maimai/allPlate.png'
    await all_plate.finish(MessageSegment.image(Path(path)))


@set_plate.handle()
async def _(event: GroupMessageEvent):
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
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊没换成功，再试试吧~（输入id有误）'))
        await set_plate.send(msg)


@set_frame.handle()
async def _(event: GroupMessageEvent):
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
        msg = (MessageSegment.at(qq), MessageSegment.text(' 迪拉熊没换成功，再试试吧~（输入id有误）'))
        await set_plate.send(msg)


@ratj_on.handle()
async def _(event: GroupMessageEvent):
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
async def _(event: GroupMessageEvent):
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
