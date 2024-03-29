from nonebot_plugin_alconna import on_alconna, funcommand, Command, Arparma, Match, AlconnaMatch
from arclet.alconna import Alconna, Subcommand, Args
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from util.Config import config
from util.PermissonManager import pm

perm = on_alconna(Alconna(
    [config.comm_prefix],
    "perm",
    Subcommand(
        "update"
    ),
    Subcommand(
        "addUser",
        Args["pg", str]["uid", int]
    ),
    Subcommand(
        "addGroup",
        Args["pg", str]["uid", int]
    )
))


@perm.handle()
async def _(event: GroupMessageEvent, result: Arparma):
    if result.find('update'):
        if pm.is_op(event.user_id):
            pm.read_perms()
            await perm.finish(MessageSegment.text("权限成功更新！"))
        else:
            await perm.finish(MessageSegment.text("你没有进行此操作的权限！"))


@perm.handle()
async def _(event: GroupMessageEvent, result: Arparma):
    if result.find('addUser'):
        if pm.is_admin(event.user_id):
            if result.find('pg') and result.find('uid'):
                pg = result.query[str]("addUser.pg")
                uid = result.query[int]("addUser.uid")
                result = pm.add_user(pg, uid)
                if result == 0:
                    await perm.finish(MessageSegment.text("已成功添加{}到{}权限组中".format(uid, pg)))
                elif result == 1:
                    await perm.finish(MessageSegment.text("user权限组无需添加"))
                elif result == 2:
                    await perm.finish(MessageSegment.text("{}权限组不存在！".format(pg)))
                else:
                    await perm.finish(MessageSegment.text("{}已经在{}权限组了！".format(uid, pg)))
        else:
            await perm.finish(MessageSegment.text("你没有进行此操作的权限！"))


@perm.handle()
async def _(event: GroupMessageEvent, result: Arparma):
    if result.find('addGroup'):
        if pm.is_admin(event.user_id):
            if result.find('pg') and result.find('uid'):
                pg = result.query[str]("addGroup.pg")
                uid = result.query[int]("addGroup.uid")
                result = pm.add_group(pg, uid)
                if result == 0:
                    await perm.finish(MessageSegment.text("已成功添加群组{}到{}权限组中".format(uid, pg)))
                elif result == 1:
                    await perm.finish(MessageSegment.text("default权限组无需添加"))
                elif result == 2:
                    await perm.finish(MessageSegment.text("{}权限组不存在！".format(pg)))
                else:
                    await perm.finish(MessageSegment.text("{}已经在{}权限组了！".format(uid, pg)))
        else:
            await perm.finish(MessageSegment.text("你没有进行此操作的权限！"))


@perm.handle()
async def _(bot: Bot, event: GroupMessageEvent, result: Arparma):
    # 获取权限组信息
    user_perm = pm.get_user_perm(event.user_id)
    group_perm = pm.get_group_perm(event.group_id)
    # 构建返回信息
    rt_text = "你现在所在的权限组为{}\n当前所在群的权限组为{}".format(str(user_perm), str(group_perm))
    await perm.finish(MessageSegment.at(event.user_id) + MessageSegment.text('\n' + rt_text))
