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

test = on_fullmatch('test')

@test.handle()
async def _(bot:Bot, event:GroupMessageEvent):
    print(str(event.get_message()))
