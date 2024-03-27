import math
import io

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from nonebot.params import Arg, ArgStr, Depends, CommandArg, ArgPlainText
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from util.gen_status_img import gen_status
from util.Logger import logger

status = on_command(' status')


@status.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    img = await gen_status()
    await status.finish(MessageSegment.image(img))
