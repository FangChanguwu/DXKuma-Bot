import random
import os
import datetime
import json

from io import BytesIO
from pathlib import Path

from nonebot import on_fullmatch , on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from util.gen_status_img import gen_status
from util.Logger import logger

kuma_pic = on_regex(r'^((随机)(迪拉|滴蜡)熊|dlx)(涩图|色图|瑟图|st|)$')
rank = on_regex(r'^(迪拉熊排行榜|dlxlist)$')

KUMAPIC = './src/kuma-pic/正经图'
KUMAPIC_R18 = './src/kuma-pic/涩图'
DATA_PATH = './data/random_pic/count.json'


def get_time():
    today = datetime.date.today()

    # 获取当前年份
    year = today.year

    # 获取当前日期所在的周数
    week_number = today.isocalendar()[1]

    # 将年份和周数拼接成字符串
    result = str(year) + str(week_number)
    return result

async def update_count(qq:str, type:str):
    with open(DATA_PATH, 'r') as f:
        count_data = json.load(f)

    time = get_time()
    
    if qq not in count_data:
        count_data.setdefault(qq, {})
        count_data[qq].setdefault(time, {"kuma": 0, "kuma_r18": 0})
       
    
    count_data[qq][time][type] += 1

    with open(DATA_PATH, 'w') as f:
        json.dump(count_data, f, ensure_ascii=False, indent=4)

async def gen_rank(data, time):
    leaderboard = []

    for qq, qq_data in data.items():
        if time in qq_data:
            total_count = qq_data[time]["kuma"] + qq_data[time]["kuma_r18"]
            leaderboard.append((qq, total_count))

    leaderboard.sort(key=lambda x: x[1], reverse=True)

    return leaderboard[:5]

@kuma_pic.handle()
async def _(event: GroupMessageEvent):
    qq = event.get_user_id()
    msg = str(event.get_message())
    type = 'kuma'
    path = KUMAPIC
    if '涩图' in msg or '色图' in msg or '瑟图' in msg or 'st' in msg:
        type = 'kuma_r18'
        path = KUMAPIC_R18
    files = os.listdir(path)
    file = random.choice(files)
    pic_path = os.path.join(path, file)
    await update_count(qq=qq, type=type)
    await kuma_pic.finish(MessageSegment.image(Path(pic_path)))

@rank.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    qq = event.get_user_id()
    with open(DATA_PATH, 'r') as f:
        count_data = json.load(f)

    time = get_time()
    leaderboard_output = []
    leaderboard = await gen_rank(count_data, time)
    for i, (qq, total_count) in enumerate(leaderboard, start=1):
        user_name = (await bot.get_stranger_info(user_id=int(qq), no_cache=False))['nickname']
        rank_str = f"{i}. {user_name} - {total_count}"
        leaderboard_output.append(rank_str)
    
    msg = '\n'.join(leaderboard_output)
    msg = f'本周迪拉熊厨力最高的人是…\n{msg}\n迪拉熊给上面五个宝宝一个大大的拥抱~\n（积分每周一重算）'
    await rank.finish(msg)