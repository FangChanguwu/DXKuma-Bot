import io

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from nonebot.params import Arg, ArgStr, Depends, CommandArg, ArgPlainText
from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from util.gen_status_img import gen_status
from util.Logger import logger
from util.Permission import permisson

get_pem = on_command(' perm')
grant_op = on_command(' grantOp')
grant_group_enabled = on_command(' addGroup')
grant_group_unlimited = on_command(' grantGroupUnlimited')


@get_pem.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    print(event.group_id, event.user_id)
    print(permisson.is_group_enabled(event.group_id))
    if permisson.is_group_enabled(event.group_id):
        user_pem = False
        group_pem = False
        if permisson.is_op(event.user_id):
            user_pem = True
        if permisson.is_group_unlimited(event.group_id):
            group_pem = True

        # 构建返回文本
        rt = (f"你的身份为：{'用户' if not user_pem else '管理员'}\n"
              f"当前所在群的权限组为：{'Limited' if not group_pem else 'Unlimited'}")

        await get_pem.finish(MessageSegment.text(rt))


@grant_op.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检测是否为op
    if permisson.is_op(event.user_id):
        arg = args.extract_plain_text()
        try:
            arg = int(arg)
        except ValueError as e:
            grant_op.finish(MessageSegment.text("传入的信息不合法！"))
            return

        # 检测数据合法性后尝试添加数据
        if permisson.add_op(arg):
            await grant_op.finish(MessageSegment.text("添加管理员成功"))
        else:
            await grant_op.finish(MessageSegment.text("该管理员已经存在"))


@grant_group_enabled.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检测是否为op
    if permisson.is_op(event.user_id):
        arg = args.extract_plain_text()
        try:
            if arg == "this":
                arg = event.group_id
            arg = int(arg)
        except ValueError as e:
            grant_group_enabled.finish(MessageSegment.text("传入的信息不合法！"))
            return

        # 检测数据合法性后尝试添加数据
        if permisson.add_group_enabled(arg):
            await grant_group_enabled.finish(MessageSegment.text("添加群组成功"))
        else:
            await grant_group_enabled.finish(MessageSegment.text("该群组已经存在"))


@grant_group_unlimited.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    # 检测是否为op
    if permisson.is_op(event.user_id):
        arg = args.extract_plain_text()
        try:
            if arg == "this":
                arg = event.group_id
            arg = int(arg)
        except ValueError as e:
            grant_group_unlimited.finish(MessageSegment.text("传入的信息不合法！"))
            return

        # 检测数据合法性后尝试添加数据
        if permisson.add_group_unlimited(arg):
            await grant_group_unlimited.finish(MessageSegment.text("提升群组权限成功"))
        else:
            await grant_group_unlimited.finish(MessageSegment.text("该群组已经存在"))

