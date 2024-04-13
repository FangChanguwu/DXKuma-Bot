import json

from nonebot import on_command, on_fullmatch
from nonebot.params import Arg, ArgStr, CommandArg, Depends, ArgPlainText
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from util.md_support.button import *
from util.md_support.md import send_markdown

help = on_fullmatch('dlxhelp')

eatbreak = on_fullmatch('我的绝赞给你吃~')

@help.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    res = "# 需要迪拉熊做什么呢~"
    action = [
        {
            "type": "node",
            "data": {
                "name": "迪拉熊",
                "uin": "2689340931",
                "content": [
                    {
                        "type": "markdown",
                        "data": {"content": res},
                    }
                ],
            },
        }
    ]
    b50 = Button(
        render_data=RenderData(label="b50", visited_label="b50",style=1),
        action=Action(type=2, data="dlx50", permission=Permission(),enter=True),
    )
    dlxpic = Button(
        render_data=RenderData(label="迪拉熊图片", visited_label="迪拉熊图片",style=1),
        action=Action(type=2, data="dlx", permission=Permission(),enter=True),
    )
    dlxpicst = Button(
        render_data=RenderData(label="迪拉熊色图", visited_label="迪拉熊色图",style=1),
        action=Action(type=2, data="dlxst", permission=Permission(),enter=True),
    )
    dlxlist = Button(
        render_data=RenderData(label="厨力排行榜", visited_label="厨力排行榜",style=1),
        action=Action(type=2, data="dlxlist", permission=Permission(),enter=True),
    )
    poke = Button(
        render_data=RenderData(label="戳迪拉熊屁屁", visited_label="戳迪拉熊屁屁",style=1),
        action=Action(type=2, data="戳屁屁", permission=Permission(),enter=True),
    )
    dontpress = Button(
        render_data=RenderData(label="别按这个", visited_label="别按这个"),
        action=Action(type=2, data="我的绝赞给你吃~", permission=Permission(),enter=True),
    )
    b50_bnt = Buttons().add(b50)
    if group_id == 967611986:
        pic_bnt = Buttons().add(dlxpic).add(dlxpicst).add(dlxlist)
    else:  
        pic_bnt = Buttons().add(dlxpic).add(dlxlist)
    poke_bnt = Buttons().add(poke)
    dont_bnt = Buttons().add(dontpress)
    keyboard = KeyBoard().add(b50_bnt).add(pic_bnt).add(poke_bnt).add(dont_bnt)
    await send_markdown(bot=bot,group_id=event.group_id,markdown=res,keyboard=keyboard)


@eatbreak.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    qq = event.user_id
    with open('./src/eatbreak.png', 'rb') as file:
        img = file.read()
    msg = (MessageSegment.text('谢谢~'), MessageSegment.image(img))
    await eatbreak.finish(msg)
    