# import random
# import os
# import datetime
# import json
# import re
# import asyncio

# from io import BytesIO
# from pathlib import Path

# from nonebot import on_fullmatch , on_regex, on_command
# from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
# from nonebot.adapters.onebot.v11 import Message, MessageSegment
# from util.gen_status_img import gen_status
# from util.Logger import logger

# test = on_command('test')

# @test.handle()
# async def _(bot:Bot, event:GroupMessageEvent):
#     text = str(event.get_message())
#     urls = re.findall(r"url=([^&\]]+)", text)
#     url = urls[0]
#     pass