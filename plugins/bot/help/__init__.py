import json

from pathlib import Path

from nonebot import on_command, on_fullmatch, on_regex
from nonebot.params import Arg, ArgStr, CommandArg, Depends, ArgPlainText
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from util.md_support.button import *
from util.md_support.md import send_markdown

all_help = on_regex(r'(dlxhelp|迪拉熊指令|迪拉熊帮助)')
b50cfg_help = on_fullmatch('dlxhelp2')

eatbreak = on_fullmatch('我的绝赞给你吃~')

# @help.handle()
# async def _(bot: Bot, event: GroupMessageEvent):
#     group_id = event.group_id
#     res = "# 需要迪拉熊做什么呢~"
#     action = [
#         {
#             "type": "node",
#             "data": {
#                 "name": "迪拉熊",
#                 "uin": "2689340931",
#                 "content": [
#                     {
#                         "type": "markdown",
#                         "data": {"content": res},
#                     }
#                 ],
#             },
#         }
#     ]
#     help_list = Button(
#         render_data=RenderData(label="指令大全", visited_label="指令大全",style=1),
#         action=Action(type=2, data="指令大全", permission=Permission(),enter=True),
#     )
#     b50 = Button(
#         render_data=RenderData(label="B50", visited_label="B50",style=1),
#         action=Action(type=2, data="dlx50", permission=Permission(),enter=True),
#     )
#     ap50 = Button(
#         render_data=RenderData(label="AP50", visited_label="AP50",style=1),
#         action=Action(type=2, data="dlxap", permission=Permission(),enter=True),
#     )
#     b50cfg = Button(
#         render_data=RenderData(label="B50设置", visited_label="B50设置",style=1),
#         action=Action(type=2, data="dlxhelp2", permission=Permission(),enter=True),
#     )
#     dlxpic = Button(
#         render_data=RenderData(label="迪拉熊图片", visited_label="迪拉熊图片",style=1),
#         action=Action(type=2, data="dlx", permission=Permission(),enter=True),
#     )
#     dlxpicst = Button(
#         render_data=RenderData(label="迪拉熊色图", visited_label="迪拉熊色图",style=1),
#         action=Action(type=2, data="dlxst", permission=Permission(),enter=True),
#     )
#     dlxlist = Button(
#         render_data=RenderData(label="厨力排行榜", visited_label="厨力排行榜",style=1),
#         action=Action(type=2, data="dlxlist", permission=Permission(),enter=True),
#     )
#     poke = Button(
#         render_data=RenderData(label="戳迪拉熊屁屁", visited_label="戳迪拉熊屁屁",style=1),
#         action=Action(type=2, data="戳屁屁", permission=Permission(),enter=True),
#     )
#     dontpress = Button(
#         render_data=RenderData(label="别按这个", visited_label="别按这个"),
#         action=Action(type=2, data="我的绝赞给你吃~", permission=Permission(),enter=True),
#     )
#     help_bnt = Buttons().add(help_list)
#     b50_bnt = Buttons().add(b50).add(ap50).add(b50cfg)
#     if group_id == 967611986:
#         pic_bnt = Buttons().add(dlxpic).add(dlxpicst).add(dlxlist)
#     else:  
#         pic_bnt = Buttons().add(dlxpic).add(dlxlist)
#     poke_bnt = Buttons().add(poke)
#     dont_bnt = Buttons().add(dontpress)
#     keyboard = KeyBoard().add(help_bnt).add(b50_bnt).add(pic_bnt).add(poke_bnt).add(dont_bnt)
#     await send_markdown(bot=bot,group_id=event.group_id,markdown=res,keyboard=keyboard)

# @b50cfg_help.handle()
# async def _(bot: Bot, event: GroupMessageEvent):
#     qq = event.get_user_id()
#     with open('./data/maimai/b50_config.json', 'r') as f:
#             b50config = json.load(f)
#     if qq not in b50config:
#         b50config = {'frame': '200502', 'plate': '000101', 'rating_tj': True}
#     else:
#         b50config = b50config[qq]
#     ratj = '✅' if b50config['rating_tj'] else '❌'
#     ratj_switch = '关闭分数推荐' if b50config['rating_tj'] else '开启分数推荐'
#     group_id = event.group_id
#     res = "# 设置你的b50"
#     action = [
#         {
#             "type": "node",
#             "data": {
#                 "name": "迪拉熊",
#                 "uin": "2689340931",
#                 "content": [
#                     {
#                         "type": "markdown",
#                         "data": {"content": res},
#                     }
#                 ],
#             },
#         }
#     ]
#     all_plate = Button(
#         render_data=RenderData(label="查看牌子", visited_label="查看牌子", style=1),
#         action=Action(type=2, data="plate", permission=Permission(),enter=True),
#     )
#     all_frame = Button(
#         render_data=RenderData(label="查看底板", visited_label="查看底板", style=1),
#         action=Action(type=2, data="frame", permission=Permission(),enter=True),
#     )

#     set_plate = Button(
#         render_data=RenderData(label="设置牌子", visited_label="设置牌子", style=1),
#         action=Action(type=2, data="设置牌子 000000(将000000替换为你要设置的物品六位id并删掉该括号内容)", permission=Permission(),enter=False),
#     )
#     set_frame = Button(
#         render_data=RenderData(label="设置底板", visited_label="设置底板", style=1),
#         action=Action(type=2, data="设置底板 000000(将000000替换为你要设置的物品六位id并删掉该括号内容)", permission=Permission(),enter=False),
#     )

#     rating_tj = Button(
#         render_data=RenderData(label=f"开/关分数推荐:{ratj}", visited_label=f"开/关分数推荐:{'❌' if ratj == '✅' else '✅'}", style=1),
#         action=Action(type=2, data=ratj_switch, permission=Permission(),enter=False),
#     )
#     all_bnt = Buttons().add(all_plate).add(all_frame)
#     set_bnt = Buttons().add(set_plate).add(set_frame)
#     ratj_switch_bnt = Buttons().add(rating_tj)
#     keyboard = KeyBoard().add(all_bnt).add(set_bnt).add(ratj_switch_bnt)
#     await send_markdown(bot=bot,group_id=event.group_id,markdown=res,keyboard=keyboard)

@all_help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
     text = '迪拉熊bot指令使用指南（临时）\n' \
            '-dlx50-生成迪拉熊主体的b50\n' \
            '-dlx-随机生成迪拉熊绘图作品\n' \
            '*生成作品不要随意传播\n' \
            '-dlxlist-迪拉熊图片查询次数排名\n' \
            '-戳屁屁-字面意思\n' \
            '-frame/看底板-查看底板序号\n' \
            '-plate/看牌子-查看牌子序号\n' \
            '-setframe/设置底板+对应数字\n' \
            '-setplate/设置牌子+对应数字\n' \
            '-开启分数推荐-开启b50分数推荐\n' \
            '-关闭分数推荐-关闭b50分数推荐'
     msg = (MessageSegment.text(text), MessageSegment.image(Path('./src/请稍后.jpg')))
     await all_help.finish(msg)

@eatbreak.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.user_id
    msg = (MessageSegment.text('谢谢~'), MessageSegment.image(Path('./src/eatbreak.png')))
    await eatbreak.finish(msg)
    