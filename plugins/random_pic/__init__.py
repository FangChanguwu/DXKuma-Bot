import random
import os

from io import BytesIO
from pathlib import Path

from nonebot import on_fullmatch , on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from util.gen_status_img import gen_status
from util.Logger import logger

kuma_pic = on_regex(r'^((随机)(迪拉|滴蜡)熊|dlx)(涩图|色图|瑟图|st|)$')

KUMAPIC = './src/kuma-pic/正经图'
KUMAPIC_R18 = './src/kuma-pic/涩图'

@kuma_pic.handle()
async def _(event: GroupMessageEvent):
    msg = str(event.get_message())
    path = KUMAPIC
    if '涩图' in msg or '色图' in msg or '瑟图' in msg or 'st' in msg:
        path = KUMAPIC_R18
    files = os.listdir(path)
    file = random.choice(files)
    pic_path = os.path.join(path, file)
    await kuma_pic.finish(MessageSegment.image(Path(pic_path)))